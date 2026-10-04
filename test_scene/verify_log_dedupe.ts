/**
 * 验证前端日志去重逻辑（frontend/src/api/ws.ts）—— 修复“日志面板同一行出现两次”。
 *
 * 背景：LogPanel 挂载/切换配置/WebSocket 重连时会拉取历史日志并 mergeHistory 合并。
 * 历史日志来自日志文件（时间戳精确到秒），实时日志来自 WebSocket（服务端毫秒）；
 * 若实时日志用浏览器接收时刻作时间戳，去重键不匹配 → 已展示的日志被再插一遍。
 *
 * 运行：node --experimental-strip-types test_scene/verify_log_dedupe.ts
 */
type LogEntry = {
  level: string
  message: string
  ts: number
  config_id?: string
  logger_name?: string
}

// ---- 桩：ws.ts 模块加载时会立即 connect()，需要 location / WebSocket ----
class FakeWebSocket {
  static last: FakeWebSocket | null = null
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3
  readyState = 1
  url: string
  sent: string[] = []
  onopen: (() => void) | null = null
  onmessage: ((event: { data: string }) => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null
  constructor(url: string) {
    this.url = url
    FakeWebSocket.last = this
  }
  send(data: string) { this.sent.push(data) }
  close() { this.readyState = 3; this.onclose?.() }
}

const proc = (globalThis as any).process
;(globalThis as any).location = { protocol: 'http:', host: 'localhost:4199' }
;(globalThis as any).WebSocket = FakeWebSocket

let failures = 0
function check(cond: boolean, msg: string) {
  if (cond) {
    console.log(`  ok   ${msg}`)
  } else {
    failures += 1
    console.error(`  FAIL ${msg}`)
  }
}
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

async function main() {
  const ws = await import('../frontend/src/api/ws/index.ts')
  const { logMap } = ws.useWebSocket()
  const mergeHistory = ws.mergeHistory

  const CID = 'Config_1'
  const SERVER_TS = 1757568000123                    // 服务端毫秒时间戳（任意值）
  const SECOND = SERVER_TS - (SERVER_TS % 1000)      // 日志文件精度：截断到秒
  const LOGGER_TASK = 'SchedulerService_Config_1.秘境探险'
  const LOGGER_OP = 'SchedulerService_Config_1.Operationer'

  const send = (items: any[]) =>
    FakeWebSocket.last!.onmessage!({ data: JSON.stringify(['log', items]) })
  const live = (level: string, message: string, logger_name: string, ts?: number) =>
    ({ type: 'log', level, message, config_id: CID, logger_name, ...(ts ? { ts } : {}) })
  const history = (level: string, message: string, logger_name: string,
                   ts: number = SECOND): LogEntry =>
    ({ level, message, ts, config_id: CID, logger_name })

  // 1) 实时日志：采用后端 payload 携带的服务端时间戳（而非接收时刻）
  send([
    live('INFO', '识别到场景: 秘境探险-首页', LOGGER_TASK, SERVER_TS),
    live('INFO', '[Click] [创建房间]', LOGGER_OP, SERVER_TS + 400),
  ])
  await sleep(300)   // 等待 flushLogs 的 200ms 防抖
  check(logMap.value[CID].length === 2, '实时日志两条已写入缓存')
  check(logMap.value[CID][0].ts === SERVER_TS,
    '实时日志 ts 采用服务端时间戳（不是浏览器接收时刻）')

  // 2) 历史日志是同一批日志（秒级时间戳）→ 不应重复展示
  mergeHistory(CID, [
    history('INFO', '识别到场景: 秘境探险-首页', LOGGER_TASK),
    history('INFO', '[Click] [创建房间]', LOGGER_OP),
  ])
  check(logMap.value[CID].length === 2, '历史补齐同一批日志后不产生重复条目')

  // 3) 真正的缺口仍要补齐（历史里有实时流没收到过的日志）
  mergeHistory(CID, [
    history('INFO', '识别到场景: 秘境探险-首页', LOGGER_TASK),
    history('INFO', '[Click] [创建房间]', LOGGER_OP),
    history('WARNING', '搜索超时：1.4s', LOGGER_OP),
  ])
  check(logMap.value[CID].length === 3, '实时流缺失的历史条目被补齐')
  check(logMap.value[CID].some(e => e.message === '搜索超时：1.4s'),
    '补齐条目内容正确')

  // 4) 同一秒内合法的重复日志（如失败重试循环）不能被去重吞掉
  const repeatTs = SERVER_TS + 60000
  send([
    live('INFO', '开始扫荡', LOGGER_TASK, repeatTs),
    live('INFO', '开始扫荡', LOGGER_TASK, repeatTs + 120),
    live('INFO', '开始扫荡', LOGGER_TASK, repeatTs + 240),
  ])
  await sleep(300)
  const afterRepeats = logMap.value[CID].length
  const repeatSecond = repeatTs - (repeatTs % 1000)
  check(afterRepeats === 6, '同一秒内 3 条相同日志全部保留')
  mergeHistory(CID, [
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
  ])
  check(logMap.value[CID].length === afterRepeats,
    '相同条数的历史重复日志被完全对齐（不重复展示）')
  mergeHistory(CID, [
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
    history('INFO', '开始扫荡', LOGGER_TASK, repeatSecond),
  ])
  check(logMap.value[CID].length === afterRepeats + 1,
    '历史比实时多出 1 条重复日志时只补 1 条')

  // 5) 兼容旧后端：payload 没有 ts 时回退到接收时刻（仍然可用）
  logMap.value[CID] = []
  send([live('INFO', '无时间戳的日志', LOGGER_TASK, 0)])
  await sleep(300)
  const fallback = logMap.value[CID].find(e => e.message === '无时间戳的日志')
  check(!!fallback && Math.abs((fallback as LogEntry).ts - Date.now()) < 10000,
    '缺少 ts 的旧后端 payload 回退为接收时刻')
}

main().then(() => {
  if (failures > 0) {
    console.error(`\n${failures} 项检查失败`)
    proc.exit(1)
  }
  console.log('\nALL PASS')
  proc.exit(0)
}).catch((err: unknown) => {
  console.error(err)
  proc.exit(1)
})
