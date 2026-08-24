/**
 * WebSocket 连接管理器（支持批量消息 + UI 更新节流 + 按 config_id 隔离日志）
 *
 * 日志按 config_id 分别存储，前端 LogPanel 通过 props 选择要显示的日志流。
 * 后端 WebSocketLogHandler 从 logger name 中提取 config_id 并附加到每条日志消息。
 */

import { ref } from 'vue'

export type WSMessage = {
  type: 'log' | 'status' | 'task_state' | 'scheduler_snapshot'
  level?: string
  message?: string
  config_id?: string
  logger_name?: string
  name?: string
  status?: number
  action?: string
  error?: string
  data?: any
}

export type LogEntry = {
  level: string
  message: string
  ts: number
  config_id?: string
  logger_name?: string
}

type MessageHandler = (msg: WSMessage) => void

const _handlers = new Set<MessageHandler>()
const connected = ref(false)

/** 所有日志按 config_id 分组存储，key="" 表示无归属的全局日志 */
const logMap = ref<Record<string, LogEntry[]>>({})

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
      const cid = entry.config_id || ''
      if (!logMap.value[cid]) {
        logMap.value[cid] = []
      }
      logMap.value[cid].push(entry)
    }
    _pendingLogs = []
    syncGlobalLogs()
  }, 200)
}

function pushLog(level: string, message: string, config_id?: string, logger_name?: string) {
  _pendingLogs.push({ level, message, ts: Date.now(), config_id, logger_name })
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
 * 按 (ts + message) 去重，合并后按时间排序，不覆盖已有实时日志。
 */
export function mergeHistory(configId: string, entries: LogEntry[]) {
  if (!entries || entries.length === 0) return
  const cid = configId || ''
  const existing = logMap.value[cid] || []
  const seen = new Set(existing.map(e => `${e.ts}:${e.message}`))
  const added: LogEntry[] = []
  for (const e of entries) {
    const key = `${e.ts}:${e.message}`
    if (!seen.has(key)) {
      seen.add(key)
      added.push(e)
    }
  }
  if (added.length === 0) return
  const merged = [...existing, ...added]
  merged.sort((a, b) => a.ts - b.ts)
  logMap.value[cid] = merged
  syncGlobalLogs()
}

export function useWebSocket() {
  function connect() {
    if (_ws && (_ws.readyState === WebSocket.OPEN || _ws.readyState === WebSocket.CONNECTING)) return

    const url = getWsUrl()
    _ws = new WebSocket(url)

    _ws.onopen = () => {
      connected.value = true
      if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null }
      _pingTimer = setInterval(() => {
        if (_ws?.readyState === WebSocket.OPEN) _ws.send('ping')
      }, 30000)
      // 通知各订阅者连接（含重连）成功，便于重新拉取历史日志补齐缺口
      for (const h of _handlers) h({ type: 'reconnected' })
    }

    _ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (Array.isArray(data) && data[0] === 'log') {
          const batch: any[] = data[1]
          for (const item of batch) {
            if (item.type === 'log') {
              pushLog(item.level || 'INFO', item.message || '', item.config_id, item.logger_name)
            }
            for (const h of _handlers) h(item)
          }
        } else {
          const msg = data as WSMessage
          if (msg.type === 'log') {
            pushLog(msg.level || 'INFO', msg.message || '', msg.config_id, msg.logger_name)
          } else if (msg.type === 'status' || msg.type === 'task_state' || msg.type === 'scheduler_snapshot') {
            // broadcast_status/broadcast_task_state/broadcast_snapshot 把 config_id
            // 包在 data 内，归一化到顶层，各监听者统一用 msg.config_id 过滤
            if (!msg.config_id && msg.data && typeof msg.data === 'object') {
              msg.config_id = msg.data.config_id
            }
          }
          for (const h of _handlers) h(msg)
        }
      } catch { /* ignore */ }
    }

    _ws.onclose = () => {
      connected.value = false
      if (_pingTimer) { clearInterval(_pingTimer); _pingTimer = null }
      if (_pendingLogs.length > 0) {
        for (const entry of _pendingLogs) {
          const cid = entry.config_id || ''
          if (!logMap.value[cid]) logMap.value[cid] = []
          logMap.value[cid].push(entry)
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
        const cid = entry.config_id || ''
        if (!logMap.value[cid]) logMap.value[cid] = []
        logMap.value[cid].push(entry)
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

  function clearLogs() {
    logMap.value = {}
    syncGlobalLogs()
  }

  connect()

  return { connected, logMessages, logMap, connect, disconnect, onMessage, clearLogs, clearLogsByConfig }
}
