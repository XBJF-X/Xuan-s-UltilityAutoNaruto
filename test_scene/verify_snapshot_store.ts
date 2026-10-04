/**
 * 验证前端快照唯一写入口的核心逻辑（frontend/src/stores/snapshot.ts）
 *
 * 背景（阶段 5）：改前有 5 处直接写 `appStore.schedulerSnapshots[configId]`——
 * Layout/Dashboard/PresetEditor 语义各不相同（WS 整体替换、轮询只合并 tasks、重置写空快照），
 * 且都没有 seq 保护：一次慢的旧 WS 帧或旧轮询响应会把新状态盖回去（切配置时尤其明显）。
 * 现在统一经 `applySnapshot` → `computeSnapshotWrite`，本脚本钉住它的规则。
 *
 * 运行：node --experimental-strip-types test_scene/verify_snapshot_store.ts
 */
import { computeSnapshotWrite } from '../frontend/src/stores/app/snapshot.ts'

let failures = 0
function check(cond: boolean, msg: string) {
  if (cond) {
    console.log(`  ok   ${msg}`)
  } else {
    failures += 1
    console.error(`  FAIL ${msg}`)
  }
}

function main() {
  // ---------- 1. 整体替换（WS 推送） ----------
  let r = computeSnapshotWrite({ running: false, tasks: [{ name: 'A' }] },
    { running: true, mode: 'persistent', tasks: [{ name: 'B' }] }, -1)
  check(r.changed, '1: 首次写入生效')
  check(r.snapshot.running === true, '1: running 被替换为新值')
  check(r.snapshot.tasks.length === 1 && r.snapshot.tasks[0].name === 'B', '1: tasks 整体替换（不残留旧项）')

  // ---------- 2. mergeTasks（轮询兜底只覆盖 tasks） ----------
  r = computeSnapshotWrite({ running: true, mode: 'once', tasks: [{ name: 'A' }] },
    { tasks: [{ name: 'B' }, { name: 'C' }] }, -1, { mergeTasks: true, source: 'poll' })
  check(r.snapshot.running === true && r.snapshot.mode === 'once',
    '2: mergeTasks 保留 WS 推送的 running/mode')
  check(r.snapshot.tasks.length === 2, '2: tasks 被轮询结果覆盖')

  // ---------- 3. mergeTasks 但快照未带 tasks（防御：保留旧列表） ----------
  r = computeSnapshotWrite({ running: true, tasks: [{ name: 'A' }] }, { running: false }, -1,
    { mergeTasks: true })
  check(r.snapshot.tasks.length === 1 && r.snapshot.tasks[0].name === 'A',
    '3: mergeTasks 且未给 tasks 时保留旧列表，不写 undefined')

  // ---------- 4. seq 去旧帧 ----------
  let seq = -1
  r = computeSnapshotWrite(undefined, { running: true, tasks: [] }, seq, { seq: 5 })
  check(r.changed && r.appliedSeq === 5, '4: seq=5 首次应用')
  seq = r.appliedSeq
  r = computeSnapshotWrite(r.snapshot, { running: false, tasks: [] }, seq, { seq: 4 })
  check(!r.changed, '4: 过期帧 seq=4 < 5 被丢弃')
  check(r.snapshot.running === true, '4: 丢弃过期帧后快照保持新状态')
  r = computeSnapshotWrite(r.snapshot, { running: false, tasks: [] }, seq, { seq: 5 })
  check(!r.changed, '4: 同 seq 重复帧被丢弃（幂等）')
  r = computeSnapshotWrite(r.snapshot, { running: false, tasks: [] }, seq, { seq: 6 })
  check(r.changed && r.appliedSeq === 6 && r.snapshot.running === false, '4: seq=6 正常应用')

  // ---------- 5. 无 seq（旧后端 / 轮询 / 重置）不受序号约束 ----------
  r = computeSnapshotWrite({ running: true, tasks: [] },
    { running: false, mode: 'once', tasks: [] }, 99, { source: 'reset' })
  check(r.changed && r.appliedSeq === 99, '5: 无 seq 写入不被丢弃，appliedSeq 不变')
  check(r.snapshot.running === false, '5: 重置写入生效')

  // ---------- 6. 非数字/NaN seq 视为未提供 ----------
  r = computeSnapshotWrite({ running: true }, { running: false }, 7, { seq: NaN })
  check(r.changed && r.appliedSeq === 7, '6: seq=NaN 不参与比较（按未提供处理）')
  r = computeSnapshotWrite({ running: true }, { running: false }, 7, { seq: undefined })
  check(r.changed, '6: seq=undefined 正常写入')

  // ---------- 7. 首次写入（prev 为空） ----------
  r = computeSnapshotWrite(undefined, { running: true, tasks: [] }, -1)
  check(r.snapshot.running === true && Array.isArray(r.snapshot.tasks), '7: prev 为空时也能写入')

  // ---------- 8. 不修改传入对象（纯函数） ----------
  const prev = { running: true, tasks: [{ name: 'A' }] }
  const incoming = { tasks: [{ name: 'B' }] }
  const snapshotBefore = JSON.stringify(prev)
  computeSnapshotWrite(prev, incoming, -1, { mergeTasks: true })
  check(JSON.stringify(prev) === snapshotBefore, '8: 不修改传入的 prev 对象')
  check(incoming.tasks.length === 1 && incoming.tasks[0].name === 'B', '8: 不修改传入的 snapshot 对象')

  console.log(failures === 0 ? '\n全部通过' : `\n${failures} 项失败`)
  process.exit(failures === 0 ? 0 : 1)
}

main()
