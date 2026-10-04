/**
 * WebSocket 连接管理器（支持批量消息 + UI 更新节流 + 按 config_id 隔离日志）
 *
 * 日志按 config_id 分别存储，前端 LogPanel 通过 props 选择要显示的日志流。
 * 后端 WebSocketLogHandler 从 logger name 中提取 config_id 并附加到每条日志消息。
 *
 * 协议（阶段 2）：连接成功后发送 `{type:'subscribe', protocol:1}` 协商 v1 统一信封；
 * 帧解析一律走 `wsProtocol.parseFrame`，因此**新旧帧都支持**（旧后端仍发
 * `["log", batch]` 数组帧与顶层字段对象帧，行为不变）。
 */

import { ref } from 'vue'
// 注意：显式带 .ts 扩展名——`tsconfig.json` 已开 allowImportingTsExtensions，
// vite 与 tsc 都能解析；这样 test_scene 下用 `node --experimental-strip-types`
// 直跑本模块的测试时不会被 Node 的 ESM 解析器拒绝。
import {
  buildSubscribeFrame,
  parseFrame,
  type LogEntry,
  type WSMessage,
} from './wsProtocol.ts'

// 向后兼容的再导出（LogPanel 等仍从 '@/api/ws' 取类型）
export type { LogEntry, WSMessage } from './wsProtocol.ts'

type MessageHandler = (msg: WSMessage) => void

const _handlers = new Set<MessageHandler>()
/** 按 type 注册的处理器（新代码用；与 onMessage 并存，渐进迁移） */
const _typedHandlers = new Map<string, Set<MessageHandler>>()
const connected = ref(false)
/** 已协商的协议版本（1 = v1 信封；0 = legacy，仅用于状态展示） */
const protocolVersion = ref(0)
/** 服务端能力（hello 帧携带） */
const serverCaps = ref<Record<string, unknown> | null>(null)

/** 尚未识别的服务端消息类型（每个类型只提示一次，避免刷屏） */
const _unknownTypes = new Set<string>()

/** 所有日志按 config_id 分组存储，key="" 表示无归属的全局日志 */
const logMap = ref<Record<string, LogEntry[]>>({})

/** 单个配置的日志缓存上限，超出丢弃最旧日志，避免长时间运行内存无限增长 */
const MAX_LOG_PER_CONFIG = 3000

/** 追加日志到指定 config，超过上限时丢弃最旧日志 */
function appendLog(cid: string, entry: LogEntry) {
  if (!logMap.value[cid]) logMap.value[cid] = []
  const arr = logMap.value[cid]
  arr.push(entry)
  if (arr.length > MAX_LOG_PER_CONFIG) {
    arr.splice(0, arr.length - MAX_LOG_PER_CONFIG)
  }
}

/** 便捷获取全局日志（兼容旧版调用） */
const logMessages = ref<LogEntry[]>([])

// 同步 logMessages 到全局日志（默认显示所有日志）
function syncGlobalLogs() {
  const all: LogEntry[] = []
  for (const entries of Object.values(logMap.value)) {
    all.push(...entries)
  }
  // 按时间排序
  all.sort((a, b) => a.ts - b.ts)
  logMessages.value = all
}

let _ws: WebSocket | null = null
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null
let _pingTimer: ReturnType<typeof setInterval> | null = null
let _batchTimer: ReturnType<typeof setTimeout> | null = null
let _pendingLogs: LogEntry[] = []

function getWsUrl(): string {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${location.host}/ws/logs`
}

/** 节流刷新日志到响应式存储（最多每 50ms 刷新一次） */
function flushLogs() {
  if (_batchTimer) return
  _batchTimer = setTimeout(() => {
    _batchTimer = null
    if (_pendingLogs.length === 0) return
    for (const entry of _pendingLogs) {
      appendLog(entry.config_id || '', entry)
    }
    _pendingLogs = []
    syncGlobalLogs()
  }, 200)
}

/** 统一分发：广播给全部订阅者 + 类型订阅者（取快照，避免回调里增删订阅者导致漏发） */
function dispatch(msg: WSMessage) {
  for (const handler of Array.from(_handlers)) {
    try {
      handler(msg)
    } catch (e) {
      console.error('[ws] 消息处理器异常:', msg.type, e)
    }
  }
  const typed = _typedHandlers.get(msg.type)
  if (!typed) return
  for (const handler of Array.from(typed)) {
    try {
      handler(msg)
    } catch (e) {
      console.error('[ws] 类型处理器异常:', msg.type, e)
    }
  }
}

function pushLog(level: string, message: string, config_id?: string, logger_name?: string, ts?: number) {
  _pendingLogs.push({
    level,
    message,
    ts: typeof ts === 'number' && ts > 0 ? ts : Date.now(),
    config_id,
    logger_name,
  })
  flushLogs()
}

/** 获取指定 config_id 的日志（响应式） */
export function getLogsByConfig(configId: string | null): LogEntry[] {
  return logMap.value[configId || ''] || []
}

/** 清空指定 config_id 的日志；不传则清空全部 */
export function clearLogsByConfig(configId?: string) {
  if (configId) {
    logMap.value[configId] = []
  } else {
    logMap.value = {}
  }
  syncGlobalLogs()
}

/**
 * 合并历史日志到指定 config（刷新/重连后恢复展示用）。
 *
 * 历史日志来自日志文件（时间戳精确到秒），实时日志来自 WebSocket（服务端毫秒）。
 * 两者时间戳精度不同，若直接用 `ts + message` 去重会全部判为“新日志”，
 * 导致刚看过的日志在历史补齐后再重复展示一遍（现象：日志面板每条重复两次）。
 * 因此统一按「秒级时间戳 + 级别 + logger + 消息」比对，并用多重集计数消费：
 * 同一秒内完全相同的重复日志（如失败重试循环）仍按已有条数保留，只补齐缺失条目。
 */
export function mergeHistory(configId: string, entries: LogEntry[]) {
  if (!entries || entries.length === 0) return
  const cid = configId || ''
  const existing = logMap.value[cid] || []
  const available = new Map<string, number>()
  for (const e of existing) {
    const key = historyKey(e)
    available.set(key, (available.get(key) || 0) + 1)
  }
  const added: LogEntry[] = []
  for (const e of entries) {
    const key = historyKey(e)
    const remain = available.get(key) || 0
    if (remain > 0) {
      available.set(key, remain - 1)
      continue
    }
    added.push(e)
  }
  if (added.length === 0) return
  const merged = [...existing, ...added]
  merged.sort((a, b) => a.ts - b.ts)
  logMap.value[cid] = merged
  syncGlobalLogs()
}

/** 历史/实时日志统一比对键（秒级时间戳，与日志文件时间精度一致） */
function historyKey(e: LogEntry): string {
  return `${Math.floor((e.ts || 0) / 1000)}:${e.level}:${e.logger_name || ''}:${e.message}`
}

export function useWebSocket() {
  function connect() {
    if (_ws && (_ws.readyState === WebSocket.OPEN || _ws.readyState === WebSocket.CONNECTING)) return

    const url = getWsUrl()
    _ws = new WebSocket(url)

    _ws.onopen = () => {
      connected.value = true
      if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null }
      // 协商 v1 统一信封（后端在收到 subscribe 前只发 legacy 帧，保证旧 dist 兼容）
      try {
        _ws?.send(buildSubscribeFrame())
      } catch (e) {
        console.warn('[ws] 协议协商帧发送失败，继续使用 legacy 帧:', e)
      }
      _pingTimer = setInterval(() => {
        if (_ws?.readyState === WebSocket.OPEN) _ws.send('ping')
      }, 30000)
      // 通知各订阅者连接（含重连）成功，便于重新拉取历史日志补齐缺口
      dispatch({ type: 'reconnected' })
    }

    _ws.onmessage = (event) => {
      let raw: unknown
      try {
        raw = JSON.parse(event.data)
      } catch (e) {
        // 服务端可能发文本帧（pong）：解析失败只留痕，不影响实时流
        console.debug('[ws] 非 JSON 帧（忽略）:', event.data, e)
        return
      }
      for (const frame of parseFrame(raw)) {
        if (frame.kind === 'logs') {
          for (const entry of frame.entries) {
            pushLog(entry.level, entry.message, entry.config_id,
              entry.logger_name, entry.ts)
            // 保持既有契约：每条日志也作为 type='log' 的消息派发
            dispatch({ type: 'log', ...entry })
          }
          if (frame.dropped > 0) {
            console.warn(`[ws] 服务端丢弃了 ${frame.dropped} 条日志（单帧上限）`)
            dispatch({ type: 'log.truncated', dropped: frame.dropped })
          }
          continue
        }
        if (frame.kind === 'message') {
          if (frame.message.type === 'hello') {
            protocolVersion.value = frame.message.protocol || 0
            serverCaps.value = (frame.message.caps as Record<string, unknown>) || null
          }
          dispatch(frame.message)
          continue
        }
        // 未知 type：必须忽略（前向兼容），每个类型只提示一次
        if (!_unknownTypes.has(frame.type)) {
          _unknownTypes.add(frame.type)
          console.debug('[ws] 忽略未知服务端消息类型:', frame.type)
        }
      }
    }

    _ws.onclose = () => {
      connected.value = false
      if (_pingTimer) { clearInterval(_pingTimer); _pingTimer = null }
      if (_pendingLogs.length > 0) {
        for (const entry of _pendingLogs) {
          appendLog(entry.config_id || '', entry)
        }
        _pendingLogs = []
        syncGlobalLogs()
      }
      _reconnectTimer = setTimeout(connect, 3000)
    }

    _ws.onerror = () => { /* onclose handles */ }
  }

  function disconnect() {
    if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null }
    if (_pingTimer) { clearInterval(_pingTimer); _pingTimer = null }
    if (_batchTimer) { clearTimeout(_batchTimer); _batchTimer = null }
    if (_pendingLogs.length > 0) {
      for (const entry of _pendingLogs) {
        appendLog(entry.config_id || '', entry)
      }
      _pendingLogs = []
      syncGlobalLogs()
    }
    _ws?.close()
    _ws = null
    connected.value = false
  }

  function onMessage(handler: MessageHandler) {
    _handlers.add(handler)
    return () => _handlers.delete(handler)
  }

  /** 按消息类型订阅（新代码用；内部与 onMessage 同一分发路径） */
  function on(type: WSMessage['type'], handler: MessageHandler) {
    if (!_typedHandlers.has(type)) _typedHandlers.set(type, new Set())
    const set = _typedHandlers.get(type)!
    set.add(handler)
    return () => set.delete(handler)
  }

  function clearLogs() {
    logMap.value = {}
    syncGlobalLogs()
  }

  connect()

  return {
    connected,
    protocolVersion,
    serverCaps,
    logMessages,
    logMap,
    connect,
    disconnect,
    onMessage,
    on,
    clearLogs,
    clearLogsByConfig,
  }
}
