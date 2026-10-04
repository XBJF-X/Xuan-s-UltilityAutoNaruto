import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { healthApi, configApi } from '@/api/client'
import { abortAllInFlight } from '@/api/http'
import { computeSnapshotWrite, type SnapshotWriteOptions } from './snapshot'

export type { SnapshotWriteOptions }

export const useAppStore = defineStore('app', () => {
  const backendConnected = ref(false)
  const backendVersion = ref('')
  const activeConfigId = ref<string | null>(null)
  const schedulerRunning = ref(false)
  const configs = ref<any[]>([])
  // 切换配置中：右侧面板需等待从后端获取完调度器/任务状态等请求结束后才允许点击，
  // 避免上一个配置的慢响应与当前配置请求产生竞态
  const configSwitching = ref(false)
  // 各配置的调度器完整状态快照（由 WS scheduler_snapshot 推送维护，前端据此零轮询）
  const schedulerSnapshots = ref<Record<string, any>>({})
  // 每配置已应用的快照 seq（阶段 5：快照唯一写入口 applySnapshot 用它丢弃过期帧）
  const snapshotSeq = ref<Record<string, number>>({})

  const activeConfig = computed(() =>
    configs.value.find(c => c.id === activeConfigId.value) || null
  )

  async function checkBackendHealth() {
    try {
      const res = await healthApi.check()
      backendConnected.value = true
      backendVersion.value = res.data.version
    } catch {
      backendConnected.value = false
    }
  }

  async function loadConfigs() {
    try {
      const res = await configApi.list()
      configs.value = res.data
    } catch {
      configs.value = []
    }
  }

  /**
   * 快照唯一写入口（阶段 5）。
   *
   * 改前有 5 处直接写 `schedulerSnapshots[configId]`（Layout/Dashboard/PresetEditor），
   * 语义各不相同（WS 整体替换、轮询只合并 tasks、重置写空快照），且都没有 seq 保护：
   * 一次慢的旧帧/旧轮询响应会把新状态盖回去。现在统一从这里写。
   *
   * @returns 是否真正写入（过期帧/空 configId 返回 false）
   */
  function applySnapshot(
    configId: string | null | undefined,
    snapshot: Record<string, any>,
    options: SnapshotWriteOptions = {},
  ): boolean {
    if (!configId) return false
    const prev = schedulerSnapshots.value[configId]
    const appliedSeq = snapshotSeq.value[configId] ?? -1
    const result = computeSnapshotWrite(prev, snapshot, appliedSeq, options)
    if (!result.changed) return false
    schedulerSnapshots.value = {
      ...schedulerSnapshots.value,
      [configId]: result.snapshot,
    }
    if (result.appliedSeq !== appliedSeq) {
      snapshotSeq.value = { ...snapshotSeq.value, [configId]: result.appliedSeq }
    }
    return true
  }

  /** 清空某配置的快照与 seq（配置被删除时调用，避免内存与序号残留） */
  function dropSnapshot(configId: string) {
    const next = { ...schedulerSnapshots.value }
    delete next[configId]
    schedulerSnapshots.value = next
    const nextSeq = { ...snapshotSeq.value }
    delete nextSeq[configId]
    snapshotSeq.value = nextSeq
  }

  /**
   * 切换当前配置（阶段 5）。
   *
   * 切换时取消所有在途请求：否则上一个配置的慢响应（GET /scheduler/tasks、
   * /configs/{id} 等）会在切换后返回并写入新配置的界面状态，表现为"切了配置却显示
   * 上个配置的数据"。取消后由新配置的请求与 WS 快照填充，配合 `configSwitching`
   * 禁用右侧面板交互。
   */
  function setActiveConfig(id: string | null) {
    if (id === activeConfigId.value) return
    abortAllInFlight('config-switch')
    activeConfigId.value = id
  }

  return {
    backendConnected,
    backendVersion,
    activeConfigId,
    activeConfig,
    configs,
    schedulerRunning,
    configSwitching,
    schedulerSnapshots,
    snapshotSeq,
    checkBackendHealth,
    loadConfigs,
    setActiveConfig,
    applySnapshot,
    dropSnapshot,
  }
})
