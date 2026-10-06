/**
 * WebSocket 帧解析（v1 统一信封 + legacy 帧兼容）
 *
 * 背景：改前服务端有 4 类消息 + 1 种数组帧（`["log", batch]`）+ 2 种字段位置
 * （顶层字段与 `data` 混用），解析逻辑散落在 ws.ts 的 if/else 里，且 `config_id`
 * 需要把 `data.config_id` 手动"拍到顶层"。新增 v1 信封：
 *
 *     {v:1, type:'scheduler.snapshot', seq, ts, config_id, payload:{...}}
 *
 * 本模块只做**纯解析**（无副作用、可被 node 直接跑测试），把三种帧形态归一为：
 * - `{kind:'logs'}`    → 日志条目（legacy 数组帧 / 单条 log / v1 log.batch）
 * - `{kind:'message'}` → 交给既有 `onMessage` 订阅者，**并映射回 legacy 的 type 与
 *   `data` 字段**，使 Dashboard / Layout / PresetEditor / LogPanel 无需改动即可兼容
 *   v1（这正是"后端先兼容、前端后切换"里前端这一步的落地方式）
 * - `{kind:'unknown'}` → 未识别的 type（必须被忽略，保证前向兼容）
 */
export type WSMessage = {
  /** `reconnected` 是**前端本地伪消息**（重连成功时由 ws.ts 自己派发，服务端不发） */
  type:
    | 'log'
    | 'status'
    | 'task_state'
    | 'scheduler_snapshot'
    | 'reconnected'
    | 'hello'
    | 'error'
    | 'log.truncated'
    /** 本次运行截图数超过每日上限（后端 v1 事件 `screenshot.limit`；payload 见 data） */
    | 'screenshot_limit'
  level?: string
  message?: string
  config_id?: string
  logger_name?: string
  /** 服务端日志生成时刻（毫秒，record.created）——仅 log 帧携带 */
  ts?: number
  name?: string
  status?: number
  action?: string
  error?: string
  data?: any
  /** v1 信封字段（legacy 帧无） */
  seq?: number
  protocol?: number
  caps?: Record<string, unknown>
  dropped?: number
}

export type LogEntry = {
  level: string
  message: string
  /** 日志记录生成时刻（毫秒）。实时日志取自后端 record.created（服务端时间），
   *  历史日志取自日志文件解析（精确到秒）——两者同源，便于 mergeHistory 去重。 */
  ts: number
  config_id?: string
  logger_name?: string
}

export type NormalizedFrame =
  | { kind: 'logs'; entries: LogEntry[]; dropped: number }
  | { kind: 'message'; message: WSMessage }
  | { kind: 'unknown'; type: string }

/** v1 type → legacy type（消费端契约保持不变） */
const V1_TO_LEGACY: Record<string, WSMessage['type']> = {
  status: 'status',
  'task.state': 'task_state',
  'scheduler.snapshot': 'scheduler_snapshot',
  // 截图超限提醒（新增事件）：映射到 legacy 风格 `type + data`，
  // 使 Layout 等消费方与 status/snapshot 用同一套 `data` 读取方式
  'screenshot.limit': 'screenshot_limit',
}

function toLogEntry(item: any): LogEntry {
  return {
    level: item?.level || 'INFO',
    message: item?.message || '',
    ts: typeof item?.ts === 'number' && item.ts > 0 ? item.ts : Date.now(),
    config_id: item?.config_id,
    logger_name: item?.logger_name,
  }
}

function isEnvelope(value: any): boolean {
  return !!value && typeof value === 'object' && !Array.isArray(value)
    && 'v' in value && 'type' in value
}

/** 解析一个服务端帧（可能产出 0~n 条归一化结果） */
export function parseFrame(raw: unknown): NormalizedFrame[] {
  // ---- legacy 数组帧：["log", [entries]] ----
  if (Array.isArray(raw)) {
    if (raw[0] === 'log' && Array.isArray(raw[1])) {
      const entries: LogEntry[] = raw[1].map(toLogEntry)
      // 旧行为：逐条 pushLog 之外，还把每条日志作为消息派发给 onMessage 订阅者
      return [
        { kind: 'logs', entries, dropped: 0 },
        ...entries.map((entry) => ({
          kind: 'message' as const,
          message: { type: 'log' as const, ...entry },
        })),
      ]
    }
    return [{ kind: 'unknown', type: String(raw[0] ?? 'array') }]
  }
  if (!raw || typeof raw !== 'object') {
    return [{ kind: 'unknown', type: typeof raw }]
  }

  const value = raw as any

  // ---- v1 统一信封 ----
  if (isEnvelope(value)) {
    const type = String(value.type)
    const payload = value.payload ?? {}
    const configId = value.config_id ?? payload?.config_id
    if (type === 'log.batch') {
      const entries: LogEntry[] = (Array.isArray(payload.entries) ? payload.entries : [])
        .map(toLogEntry)
      return [
        { kind: 'logs', entries, dropped: Number(payload.dropped) || 0 },
        ...entries.map((entry) => ({
          kind: 'message' as const,
          message: { type: 'log' as const, ...entry },
        })),
      ]
    }
    if (type === 'hello') {
      return [{
        kind: 'message',
        message: {
          type: 'hello',
          protocol: Number(payload.protocol) || 0,
          config_id: configId,
          seq: value.seq,
          caps: payload.caps,
          message: payload.server_version,
        },
      }]
    }
    if (type === 'error' || type === 'log.truncated') {
      return [{
        kind: 'message',
        message: {
          type: type as WSMessage['type'],
          config_id: configId,
          seq: value.seq,
          error: payload.code,
          message: payload.message,
          dropped: payload.dropped,
        },
      }]
    }
    const legacyType = V1_TO_LEGACY[type]
    if (legacyType) {
      return [{
        kind: 'message',
        message: { type: legacyType, data: payload, config_id: configId, seq: value.seq },
      }]
    }
    return [{ kind: 'unknown', type }]
  }

  // ---- legacy 对象帧（顶层字段 + 可选 data） ----
  if (typeof value.type === 'string') {
    if (!value.config_id && value.data && typeof value.data === 'object') {
      // 旧行为：config_id 包在 data 内，归一化到顶层供各监听者统一过滤
      value.config_id = value.data.config_id
    }
    const message = value as WSMessage
    // 单条日志帧（后端在 batch 长度为 1 时发的形态）同样要进日志缓存
    if (message.type === 'log') {
      return [
        { kind: 'logs', entries: [toLogEntry(message)], dropped: 0 },
        { kind: 'message', message },
      ]
    }
    return [{ kind: 'message', message }]
  }
  return [{ kind: 'unknown', type: 'object' }]
}

/** 客户端订阅帧（协商 v1 + 可选按配置订阅） */
export function buildSubscribeFrame(configIds?: string[]): string {
  const frame: Record<string, unknown> = { type: 'subscribe', protocol: 1 }
  if (configIds && configIds.length) frame.config_ids = configIds
  return JSON.stringify(frame)
}
