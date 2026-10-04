/**
 * 配置列表与切换 composable（阶段 5：Layout.vue 最后一块抽出）
 *
 * 负责左侧配置栏：类型页签、创建/复制/重命名/删除、右键菜单，以及"切换配置"的编排：
 * - `selectConfig(id)`：设置 `activeConfigId` 并进入总览；重复点击同一配置时主动重载
 * - `useConfigs` 内部注册 `watch(activeConfigId)`：配置变化后重新拉任务数据与调度器状态
 * - `_switchSeq` 自增序号丢弃过期响应 + `appStore.configSwitching` 遮罩，避免
 *   "上一个配置的慢响应覆盖当前配置状态"
 *
 * 与其它 composable 的耦合通过**回调注入**（不反向依赖）：
 * - `switchToOverview`：Layout 的视图切换（hash 路由跳转）
 * - `loadTaskData`：`useTaskTree` 的任务数据加载
 * - `schedulerRunning`：`useSchedulerControl` 的运行状态 ref（切换配置时同步）
 */
import { ref, computed, watch, type Ref } from 'vue'
import { useMessage } from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { configApi, schedulerApi } from '@/api/client'

export interface UseConfigsOptions {
  /** 点击配置后统一进入总览（Layout 的视图切换逻辑） */
  switchToOverview: () => void
  /** 加载当前配置的任务数据（`useTaskTree().loadTaskData`） */
  loadTaskData: () => Promise<void>
  /** 调度器运行状态（`useSchedulerControl().schedulerRunning`） */
  schedulerRunning: Ref<boolean>
}

export function useConfigs(options: UseConfigsOptions) {
  const appStore = useAppStore()
  const message = useMessage()
  const { switchToOverview, loadTaskData, schedulerRunning } = options

  // ---- 列表与页签 ----
  const configTab = ref<'persist' | 'preset'>('persist')
  const filteredConfigs = computed(() =>
    appStore.configs.filter((c: any) =>
      configTab.value === 'preset'
        ? c.config_type === '临时'
        : c.config_type !== '临时')
  )
  const createDialogType = ref<'persist' | 'preset'>('persist')
  const createDialogTitle = computed(() =>
    createDialogType.value === 'preset' ? '新建任务预设' : '新建账号配置')
  const showCreateDialog = ref(false)
  const newUsername = ref('')
  const creating = ref(false)

  // ---- 右键菜单 ----
  const configContextMenu = ref({ show: false, x: 0, y: 0, configId: '', configName: '' })
  const configContextOptions = computed(() => [
    {
      label: `复制 "${configContextMenu.value.configName || configContextMenu.value.configId}"`,
      key: 'copy',
    },
    {
      label: `重命名 "${configContextMenu.value.configName || configContextMenu.value.configId}"`,
      key: 'rename',
    },
    { type: 'divider' as const },
    {
      label: `删除 "${configContextMenu.value.configName || configContextMenu.value.configId}"`,
      key: 'delete',
      props: { style: { color: '#e53935' } },
    },
  ])

  function showConfigContextMenu(e: MouseEvent, configId: string, configName: string) {
    e.preventDefault()
    configContextMenu.value = { show: true, x: e.clientX, y: e.clientY, configId, configName }
  }

  function handleConfigContextSelect(key: string) {
    configContextMenu.value.show = false
    if (key === 'copy') {
      handleDuplicateConfig(configContextMenu.value.configId, configContextMenu.value.configName)
    } else if (key === 'rename') {
      handleRenameConfig(configContextMenu.value.configId, configContextMenu.value.configName)
    } else if (key === 'delete') {
      handleDeleteConfig(configContextMenu.value.configId, configContextMenu.value.configName)
    }
  }

  // ---- 切换配置 ----
  // 切换配置时右侧面板需等待从后端获取完调度器状态与任务状态等请求结束后才允许点击，
  // 避免上一个配置的慢响应覆盖当前配置状态（竞态）。自增 seq 用于丢弃过期响应。
  let _switchSeq = 0

  async function _loadConfigAndStatus(id: string | null, seq: number) {
    try {
      if (id) {
        await loadTaskData()
        const res = await schedulerApi.status(id)
        if (seq !== _switchSeq) return
        schedulerRunning.value = res.data?.running ?? false
      } else {
        schedulerRunning.value = false
      }
    } catch (e) {
      // 状态拉取失败按"未运行"处理并留痕（不打断切换流程）
      console.warn('[configs] 拉取调度器状态失败:', e)
      if (seq === _switchSeq) schedulerRunning.value = false
    } finally {
      if (seq === _switchSeq) appStore.configSwitching = false
    }
  }

  async function selectConfig(id: string) {
    const seq = ++_switchSeq
    appStore.configSwitching = true
    if (appStore.activeConfigId === id) {
      // 重复点击同一配置：activeConfigId 不变，watch 不会触发，这里主动重新加载
      switchToOverview()
      await _loadConfigAndStatus(id, seq)
    } else {
      appStore.setActiveConfig(id)
      // 点击左侧配置统一进入总览；预设的助手设置/任务流程通过中栏「助手设置」入口进入
      switchToOverview()
    }
  }

  function switchConfigTab(tab: 'persist' | 'preset') {
    if (configTab.value === tab) return
    configTab.value = tab
    appStore.setActiveConfig(null)
    schedulerRunning.value = false
    switchToOverview()
  }

  function openCreateDialog() {
    createDialogType.value = configTab.value
    newUsername.value = ''
    showCreateDialog.value = true
  }

  // ---- 增删改 ----
  async function handleCreateConfig() {
    if (!newUsername.value) return
    creating.value = true
    try {
      const type = createDialogType.value === 'preset' ? '临时' : '持久'
      const res = await configApi.create(newUsername.value, type)
      await appStore.loadConfigs()
      showCreateDialog.value = false
      newUsername.value = ''
      configTab.value = type === '临时' ? 'preset' : 'persist'
      const newId = res.data?.id
      if (newId) {
        await selectConfig(newId)
      }
    } catch (e) {
      // 保持抽取前行为：不弹窗（创建失败时后端错误已由 http 层统一留痕），仅补 console 留痕
      console.error('[configs] 新建配置失败:', e)
    } finally {
      creating.value = false
    }
  }

  function handleDuplicateConfig(configId: string, configName: string) {
    configApi.duplicate(configId).then(async (res) => {
      await appStore.loadConfigs()
      const newId = res.data?.id
      if (newId) {
        const newCfg = appStore.configs.find((c: any) => c.id === newId)
        configTab.value = newCfg?.config_type === '临时' ? 'preset' : 'persist'
        await selectConfig(newId)
      }
      message.success(`已复制 "${configName}"`)
    }).catch((e) => {
      message.error('复制失败')
      console.error('[configs] 复制配置失败:', e)
    })
  }

  function handleRenameConfig(configId: string, oldName: string) {
    const newName = prompt('请输入新的名称：', oldName)
    if (!newName || newName === oldName) return
    configApi.rename(configId, newName).then(() => {
      appStore.loadConfigs()
      message.success('重命名成功')
    }).catch((e) => {
      message.error('重命名失败')
      console.error('[configs] 重命名失败:', e)
    })
  }

  function handleDeleteConfig(configId: string, configName: string) {
    const ok = confirm(`确定要删除配置 "${configName}" 吗？此操作不可恢复。`)
    if (!ok) return
    configApi.delete(configId).then(() => {
      if (appStore.activeConfigId === configId) {
        appStore.setActiveConfig(null)
      }
      appStore.loadConfigs()
      message.success('删除成功')
    }).catch((e) => {
      message.error('删除失败')
      console.error('[configs] 删除配置失败:', e)
    })
  }

  // 切换配置时重新加载任务数据并同步调度器状态（selectConfig 会触发本 watch）
  watch(() => appStore.activeConfigId, (id) => {
    const seq = ++_switchSeq
    if (id) {
      appStore.configSwitching = true
      _loadConfigAndStatus(id, seq)
    } else {
      schedulerRunning.value = false
      appStore.configSwitching = false
    }
  })

  return {
    configTab,
    filteredConfigs,
    createDialogType,
    createDialogTitle,
    showCreateDialog,
    newUsername,
    creating,
    configContextMenu,
    configContextOptions,
    showConfigContextMenu,
    handleConfigContextSelect,
    selectConfig,
    switchConfigTab,
    openCreateDialog,
    handleCreateConfig,
    handleDuplicateConfig,
    handleRenameConfig,
    handleDeleteConfig,
  }
}
