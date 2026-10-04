/**
 * 任务树 composable（阶段 5：从 Layout.vue 抽出）
 *
 * 负责"当前配置的任务数据 + 分组视图"这一块：
 * - `rawTasks` / `taskSchema` / `showDisabledTasks` 状态
 * - `loadTaskData()`（按 appStore.activeConfigId 拉取任务与 schema，失败清空避免脏数据）
 * - `taskGroups` / `enabledTaskNames` / `allTasks` 派生数据（模板直接消费）
 * - `onTaskEnabledChanged()`（TaskConfigPanel 勾选后同步本地树节点状态）
 *
 * 抽出的意义：Layout.vue 的 script 原本 503 行、混着配置 CRUD / 调度器启停 / 启动检查 /
 * 任务树四件事；本块与其它三块的耦合只有 `appStore.activeConfigId`，可独立演进与复用。
 */
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { configApi } from '@/api/client'

export function useTaskTree() {
  const appStore = useAppStore()

  // 任务数据
  const rawTasks = ref<Record<string, any>>({})
  const taskSchema = ref<Record<string, any>>({})

  // 是否显示已禁用的任务
  const showDisabledTasks = ref(true)

  // 任务树分组（匹配原版 Servicer 映射：task_type = 1 if 类型==5 else 类型；
  // 「临时」类别已取消——改为每个任务独立的「是否临时」属性，类型 5 不再使用）
  const typeGroupMap: Record<number, string> = {
    0: '每日任务',
    1: '每周任务',
    2: '每周任务',
    3: '活动任务',
    4: '活动任务',
  }

  const taskGroups = computed(() => {
    const groups: Record<string, { label: string; tasks: any[] }> = {}
    for (const [name, info] of Object.entries(rawTasks.value)) {
      // 不显示禁用任务时跳过
      if (!showDisabledTasks.value && !(info as any)['是否启用']) continue
      const type = (info as any)['类型'] ?? 0
      const groupLabel = typeGroupMap[type] || '其他'
      if (!groups[groupLabel]) groups[groupLabel] = { label: groupLabel, tasks: [] }
      groups[groupLabel].tasks.push({ name, ...(info as any) })
    }
    // 按标签排序
    const order = ['每日任务', '每周任务', '每月任务', '周期任务', '活动任务', '其他']
    return order.filter(l => groups[l]).map(l => groups[l])
  })

  /** 所有已启用的任务名列表（用于判断树是否为空） */
  const enabledTaskNames = computed(() => {
    const names: string[] = []
    for (const [name, info] of Object.entries(rawTasks.value)) {
      if ((info as any)['是否启用']) names.push(name)
    }
    return names
  })

  const allTasks = computed(() => Object.keys(rawTasks.value))

  /** 加载当前配置的任务数据（失败时清空，避免显示上一个配置的脏数据） */
  async function loadTaskData() {
    if (!appStore.activeConfigId) {
      rawTasks.value = {}
      return
    }
    // 1. 加载任务数据
    try {
      const res = await configApi.get(appStore.activeConfigId)
      rawTasks.value = res.data.tasks || {}
    } catch (e) {
      // 失败清空 + 留痕（调用方负责提示；此处不打断界面）
      console.error('加载任务数据失败:', e)
      rawTasks.value = {}
    }
    // 2. 加载任务 schema（仅首次；加载失败不影响已加载的任务列表）
    if (Object.keys(taskSchema.value).length === 0) {
      try {
        const schemaRes = await configApi.getDefaultTasks()
        taskSchema.value = schemaRes.data || {}
      } catch (e) {
        console.error('加载任务 schema 失败:', e)
      }
    }
  }

  /** 任务启用状态变更回调（来自 TaskConfigPanel）：同步本地树节点指示灯 */
  function onTaskEnabledChanged(taskName: string, enabled: boolean) {
    if (rawTasks.value[taskName]) {
      rawTasks.value[taskName]['是否启用'] = enabled
    }
  }

  return {
    rawTasks,
    taskSchema,
    showDisabledTasks,
    typeGroupMap,
    taskGroups,
    enabledTaskNames,
    allTasks,
    loadTaskData,
    onTaskEnabledChanged,
  }
}
