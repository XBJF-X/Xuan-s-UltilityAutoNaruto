/**
 * 快照写入的纯逻辑（阶段 5：唯一写入口 `applySnapshot` 的核心）
 *
 * 抽成无依赖纯模块的原因：
 * 1. store 里的合并/去旧帧规则需要被单测覆盖，而 `stores/app.ts` 依赖 pinia 与 `@/` 别名，
 *    无法用 `node --experimental-strip-types` 直接跑；纯函数则可以（见 verify_snapshot_store.ts）；
 * 2. "同一份规则只写一次"——改前 5 处直接写 `schedulerSnapshots[configId]`，语义各不相同：
 *    WS 整体替换、轮询只合并 tasks、重置写空快照，且都没有 seq 保护。
 */

export interface SnapshotWriteOptions {
  /** WS 帧序号：提供时按"每配置单调递增"丢弃过期帧（旧后端帧无 seq，按不校验处理） */
  seq?: number
  /** 写入来源，仅用于调试留痕 */
  source?: 'ws' | 'poll' | 'reset' | 'test'
  /** true=只覆盖快照里的 tasks 字段（轮询兜底用法）；false/缺省=整体替换 */
  mergeTasks?: boolean
}

export interface SnapshotWriteResult {
  /** 是否真正写入（过期帧/空 configId → false） */
  changed: boolean
  snapshot: Record<string, any>
  /** 该配置已应用的最大 seq（未变化时原样返回） */
  appliedSeq: number
}

/**
 * 计算写入某配置后的快照与 seq。
 *
 * @param prev        该配置当前快照（不存在传 undefined）
 * @param snapshot    新快照内容
 * @param appliedSeq  该配置已应用的最大 seq（未应用过传 -1）
 */
export function computeSnapshotWrite(
  prev: Record<string, any> | undefined,
  snapshot: Record<string, any>,
  appliedSeq: number,
  options: SnapshotWriteOptions = {},
): SnapshotWriteResult {
  const { seq, mergeTasks = false } = options
  if (typeof seq === 'number' && Number.isFinite(seq)) {
    if (seq <= appliedSeq) {
      // 过期帧：丢弃，避免"慢的旧帧把新状态盖回去"
      return { changed: false, snapshot: prev || {}, appliedSeq }
    }
    appliedSeq = seq
  }
  const base = prev || {}
  const next = mergeTasks
    ? { ...base, ...snapshot, tasks: snapshot.tasks ?? base.tasks ?? [] }
    : { ...snapshot }
  return { changed: true, snapshot: next, appliedSeq }
}
