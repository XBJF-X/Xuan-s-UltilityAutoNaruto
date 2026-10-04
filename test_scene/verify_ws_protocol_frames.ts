/**
 * 验证前端 WS 帧解析（frontend/src/api/wsProtocol.ts）—— v1 统一信封 + legacy 兼容。
 *
 * 背景：改前解析逻辑散落在 ws.ts 的 if/else 里（`Array.isArray(data) && data[0]==='log'`
 * 特判 + 把 `data.config_id` 拍到顶层的 hack）。现在三种帧形态统一走 parseFrame：
 *   A. legacy 数组帧 `["log", [entries]]`
 *   B. legacy 对象帧 `{type:'log'|'status'|...}`（含单条日志形态）
 *   C. v1 信封 `{v:1,type,seq,ts,config_id,payload}`
 * 且 v1 的 `task.state` / `scheduler.snapshot` 必须映射回既有 legacy type，使
 * Dashboard / Layout / PresetEditor / LogPanel 无需改动。
 *
 * 运行：node --experimental-strip-types test_scene/verify_ws_protocol_frames.ts
 */
import { buildSubscribeFrame, parseFrame } from '../frontend/src/api/wsProtocol.ts'

let failures = 0
function check(cond: boolean, msg: string) {
  if (cond) {
    console.log(`  ok   ${msg}`)
  } else {
    failures += 1
    console.error(`  FAIL ${msg}`)
  }
}

const CID = 'Config_1'
const TS = 1757568000123

function kinds(frames: ReturnType<typeof parseFrame>) {
  return frames.map(f => f.kind)
}

function main() {
  // ---------- A. legacy 数组帧 ----------
  let frames = parseFrame(['log', [
    { type: 'log', level: 'INFO', message: '第一条', config_id: CID, logger_name: 'L', ts: TS },
    { type: 'log', level: 'ERROR', message: '第二条', config_id: CID, logger_name: 'L', ts: TS + 10 },
  ]])
  const logsFrame = frames[0]
  check(logsFrame.kind === 'logs', 'A: 数组帧解析为 logs')
  check(logsFrame.kind === 'logs' && logsFrame.entries.length === 2, 'A: 两条日志')
  check(logsFrame.kind === 'logs' && logsFrame.entries[0].ts === TS, 'A: 保留服务端 ts')
  check(frames.filter(f => f.kind === 'message').length === 2,
    'A: 同时把每条日志作为 message 派发（旧行为保留）')

  // 单条日志的旧形态（后端 batch==1 时发对象帧）
  frames = parseFrame({ type: 'log', level: 'INFO', message: '单条', config_id: CID, ts: TS })
  check(kinds(frames).includes('logs'), 'B: 单条 log 对象帧仍进日志缓存（回归修复）')
  check(frames.some(f => f.kind === 'message' && f.message.type === 'log'),
    'B: 单条 log 同时派发为 message')

  // ---------- B. legacy 状态帧 ----------
  frames = parseFrame({ type: 'status', data: { running: true, config_id: CID } })
  check(frames.length === 1 && frames[0].kind === 'message', 'B: status 解析为 message')
  check(frames[0].kind === 'message' && frames[0].message.config_id === CID,
    'B: config_id 从 data 提升到顶层（旧 hack 归档到解析器）')
  check(frames[0].kind === 'message' && frames[0].message.data?.running === true,
    'B: data 原样保留')

  // ---------- C. v1 信封 ----------
  frames = parseFrame({ v: 1, type: 'log.batch', seq: 5, ts: TS, config_id: CID,
    payload: { entries: [
      { level: 'INFO', message: 'v1 日志', config_id: CID, logger_name: 'L', ts: TS },
    ], dropped: 0 } })
  check(frames[0].kind === 'logs' && frames[0].entries[0].message === 'v1 日志',
    'C: log.batch 解析为 logs')
  check(frames[0].kind === 'logs' && frames[0].dropped === 0, 'C: dropped=0')

  frames = parseFrame({ v: 1, type: 'log.batch', seq: 6, config_id: CID,
    payload: { entries: [], dropped: 37 } })
  check(frames[0].kind === 'logs' && frames[0].dropped === 37, 'C: 透传 dropped 计数')

  const mapping: Array<[string, string]> = [
    ['status', 'status'],
    ['task.state', 'task_state'],
    ['scheduler.snapshot', 'scheduler_snapshot'],
  ]
  for (const [v1Type, legacyType] of mapping) {
    const out = parseFrame({ v: 1, type: v1Type, seq: 7, ts: TS, config_id: CID,
      payload: { running: true, config_id: CID } })
    const msg = out[0]
    check(msg.kind === 'message' && msg.message.type === legacyType,
      `C: ${v1Type} → legacy type ${legacyType}（消费端零改动）`)
    check(msg.kind === 'message' && msg.message.config_id === CID,
      `C: ${v1Type} 的 config_id 在顶层`)
    check(msg.kind === 'message' && msg.message.seq === 7, `C: ${v1Type} 带 seq`)
  }

  frames = parseFrame({ v: 1, type: 'hello', seq: 1, ts: TS, config_id: '',
    payload: { server_version: '0.17.61', protocol: 1, caps: { subscribe: true } } })
  check(frames[0].kind === 'message' && frames[0].message.type === 'hello',
    'C: hello 解析为 message')
  check(frames[0].kind === 'message' && frames[0].message.protocol === 1,
    'C: hello 携带协议版本')
  check(frames[0].kind === 'message' && frames[0].message.caps?.subscribe === true,
    'C: hello 携带能力')

  frames = parseFrame({ v: 1, type: 'log.truncated', seq: 9, payload: { dropped: 3 } })
  check(frames[0].kind === 'message' && frames[0].message.dropped === 3,
    'C: log.truncated 解析为 message')

  frames = parseFrame({ v: 1, type: 'brand.new.type', seq: 10, payload: {} })
  check(frames[0].kind === 'unknown' && frames[0].type === 'brand.new.type',
    'C: 未知 v1 type → unknown（必须被忽略，保证前向兼容）')

  // ---------- 边界 ----------
  check(parseFrame('pong')[0].kind === 'unknown', '文本帧（pong）→ unknown，不影响实时流')
  check(parseFrame(null)[0].kind === 'unknown', 'null → unknown')
  check(parseFrame(['weird', 1])[0].kind === 'unknown', '异常数组帧 → unknown')

  const subscribe = JSON.parse(buildSubscribeFrame())
  check(subscribe.type === 'subscribe' && subscribe.protocol === 1,
    '订阅帧格式正确（协商 v1）')
  check(!('config_ids' in subscribe), '未指定配置时不带 config_ids（订阅全部）')
  check(JSON.parse(buildSubscribeFrame(['Config_2'])).config_ids[0] === 'Config_2',
    '可指定 config_ids 做连接级订阅')

  if (failures > 0) {
    console.error(`\n${failures} 项失败`)
    ;(globalThis as any).process.exit(1)
  }
  console.log('\n全部通过')
}

main()
