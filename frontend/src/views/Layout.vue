<template>
  <div class="app-layout">
    <!-- 顶部栏 -->
    <div class="topbar">
      <div class="topbar-left">
        <div
          class="topbar-brand"
          @click="switchToGlobalLog"
          style="cursor: pointer; display: flex; align-items: center;"
        >
          <img :src="asdsIcon" alt="logo" class="topbar-logo-icon" />
          <n-gradient-text type="info" :size="23" style="font-weight: bold;">
            Xuan-s-UltilityAutoNaruto
          </n-gradient-text>
        </div>
        <n-tag :type="appStore.backendConnected ? 'success' : 'error'" size="medium">
          {{ appStore.backendConnected ? '已连接' : '未连接' }}
        </n-tag>
      </div>
      <div class="topbar-right">
        <!-- 刷新 -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button text size="medium" @click="appStore.checkBackendHealth()">
              <template #icon><n-icon size="32"><RefreshOutlined /></n-icon></template>
            </n-button>
          </template>
          刷新
        </n-tooltip>

        <!-- 截图 -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button text size="medium" :disabled="!appStore.activeConfigId" @click="handleScreenshot">
              <template #icon><n-icon size="30"><CameraOutlined /></n-icon></template>
            </n-button>
          </template>
          截图
        </n-tooltip>

        <!-- 项目主页（GitHub） -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <a
              class="topbar-icon-link"
              href="https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto"
              target="_blank"
              rel="noopener noreferrer"
            >
              <img :src="githubIcon" alt="GitHub" class="github-icon" />
            </a>
          </template>
          项目主页
        </n-tooltip>

        <!-- 反馈 -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button text size="medium" @click="openFeedback">
              <template #icon><n-icon size="30"><FolderOpenOutlined /></n-icon></template>
            </n-button>
          </template>
          反馈
        </n-tooltip>

        <!-- Q&A -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <a
              class="topbar-icon-link"
              href="https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98%E5%92%8C%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9"
              target="_blank"
              rel="noopener noreferrer"
            >
              <n-icon size="30" color="#333"><HelpOutlineOutlined /></n-icon>
            </a>
          </template>
          Q&A
        </n-tooltip>

        <!-- 场景资源（独立页面，新标签页打开） -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button text size="medium" @click="openResourceGraph">
              <template #icon><n-icon size="30"><HubOutlined /></n-icon></template>
            </n-button>
          </template>
          场景资源
        </n-tooltip>

        <!-- 检查更新 -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button text size="medium" @click="showUpdateDialog = true">
              <template #icon><n-icon size="30"><SystemUpdateOutlined /></n-icon></template>
            </n-button>
          </template>
          检查更新
        </n-tooltip>
        <!-- 设置 -->
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button text size="medium" @click="switchToSetting">
              <template #icon><n-icon size="30"><SettingsOutlined /></n-icon></template>
            </n-button>
          </template>
          设置
        </n-tooltip>
      </div>
    </div>

    <!-- 主体三栏 -->
    <div class="main-body">
      <!-- 左侧：配置切换列表（账号配置 / 任务预设） -->
      <div class="col-configs">
        <div class="config-type-tabs">
          <div
            class="config-type-tab"
            :class="{ active: configTab === 'persist' }"
            @click="switchConfigTab('persist')"
          >账号配置</div>
          <div
            class="config-type-tab"
            :class="{ active: configTab === 'preset' }"
            @click="switchConfigTab('preset')"
          >任务预设</div>
        </div>
        <div
          v-for="cfg in filteredConfigs"
          :key="cfg.id"
          class="config-btn"
          :class="{ active: cfg.id === appStore.activeConfigId }"
          @click="selectConfig(cfg.id)"
          @contextmenu.prevent="showConfigContextMenu($event, cfg.id, cfg.username)"
        >
          <div class="config-btn-name">{{ cfg.username || cfg.id }}</div>
          <div class="config-btn-id">{{ cfg.id }}</div>
        </div>
        <div class="config-btn config-btn-add" @click="openCreateDialog">
          <div class="config-btn-name">+ 新建{{ configTab === 'preset' ? '任务预设' : '账号配置' }}</div>
        </div>
      </div>

      <!-- 配置右键菜单 -->
      <n-dropdown
        trigger="manual"
        placement="bottom-start"
        :show="configContextMenu.show"
        :x="configContextMenu.x"
        :y="configContextMenu.y"
        :options="configContextOptions"
        @select="handleConfigContextSelect"
        @clickoutside="configContextMenu.show = false"
      />

      <!-- 中间：任务导航树 -->
      <div class="col-center">
        <!-- 顶栏操作区：总览按钮 + 启停调度（水平排列） -->
        <div class="top-actions">
          <div
            class="overview-btn"
            :class="{ active: currentView === 'overview' }"
            @click="switchToOverview"
          >
            <span class="overview-btn-icon">📊</span>
            <span class="overview-btn-label">总览</span>
          </div>
          <button
            v-if="appStore.activeConfigId"
            class="scheduler-toggle-btn"
            :class="schedulerRunning ? 'running' : 'stopped'"
            @click="toggleScheduler"
            :disabled="schedulerStarting"
          >
            <span class="scheduler-toggle-icon">{{ schedulerRunning ? '⏸' : '▶' }}</span>
            <span class="scheduler-toggle-label">{{ schedulerRunning ? '暂停' : '启动' }}</span>
          </button>
          <n-text v-else depth="3" style="font-size: 11px; padding: 8px;">请先选择配置</n-text>
        </div>

        <!-- 分割线 -->
        <div class="tree-divider"></div>

        <!-- 任务树 -->
        <div class="tree-title-row">
          <span class="tree-title">任务配置</span>
          <n-button text size="tiny" @click="showDisabledTasks = !showDisabledTasks" style="font-size: 11px; color: #888;">
            {{ showDisabledTasks ? '隐藏禁用' : '显示禁用' }}
          </n-button>
        </div>
        <div class="tree-scroll">
          <div v-for="group in taskGroups" :key="group.label" class="tree-group">
            <div class="tree-group-label">{{ group.label }} ({{ group.tasks.length }})</div>
            <div
              v-for="task in group.tasks"
              :key="task.name"
              class="tree-node"
              :class="{ active: currentView === 'task' && currentTaskName === task.name, disabled: !task.是否启用 }"
              @click="switchToTask(task.name)"
            >
              <span class="tree-node-dot" :class="task.是否启用 ? 'enabled' : 'disabled'"></span>
              <span class="tree-node-name">{{ task.name }}</span>
            </div>
          </div>
          
          <div v-if="enabledTaskNames.length === 0 && !showDisabledTasks" class="tree-empty">
            <n-text depth="3" style="font-size: 12px">暂无已启用的任务，点击上方"显示禁用"查看</n-text>
          </div>
          <div v-else-if="Object.keys(rawTasks).length === 0" class="tree-empty">
            <n-text depth="3" style="font-size: 12px">暂无任务数据</n-text>
          </div>
        </div>
        <div
            v-if="appStore.activeConfigId"
            class="tree-node"
            :class="{ active: currentView === 'assistant' || currentView === 'preset' }"
            @click="switchToAssistant"
          >
            <span class="tree-title">助手设置</span>
          </div>
      </div>

      <!-- 右侧：内容区 -->
      <div class="col-content">
        <template v-if="currentView === 'overview'">
          <router-view />
        </template>
        <template v-else-if="currentView === 'globallog'">
          <LogPanel title="全局日志" :config-id="'__global__'" />
        </template>
        <template v-else-if="currentView === 'task' && currentTaskName">
          <TaskConfigPanel
            :task-name="currentTaskName"
            @task-enabled-changed="onTaskEnabledChanged"
          />
        </template>
        <template v-else-if="currentView === 'assistant' && appStore.activeConfigId">
          <AssistantSettingsPanel :config-id="appStore.activeConfigId" />
        </template>
        <template v-else-if="currentView === 'preset' && appStore.activeConfigId">
          <PresetEditor :config-id="appStore.activeConfigId" />
        </template>
        <template v-else>
          <router-view />
        </template>
      </div>
    </div>

    <!-- 新建配置对话框（账号配置/任务预设） -->
    <n-modal v-model:show="showCreateDialog" :title="createDialogTitle" preset="card" style="width: 400px">
      <n-space vertical>
        <n-input
          v-model:value="newUsername"
          :placeholder="`输入${createDialogType === 'preset' ? '预设名称' : '用户名'}`"
        />
        <n-button type="primary" block @click="handleCreateConfig" :loading="creating">创建</n-button>
      </n-space>
    </n-modal>

    <!-- 检查更新 -->
    <UpdateDialog v-model:show="showUpdateDialog" />

    <!-- 反馈 -->
    <FeedbackDialog v-model:show="showFeedbackDialog" :config-id="appStore.activeConfigId" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  RefreshOutlined, SettingsOutlined, SystemUpdateOutlined,
  FolderOpenOutlined, HelpOutlineOutlined, CameraOutlined, HubOutlined,
} from '@vicons/material'
import githubIcon from '@/assets/GithubIcon.png'
import asdsIcon from '@/assets/ASDS.ico'
import { useAppStore } from '@/stores/app'
import { configApi, schedulerApi, utilsApi, deviceApi } from '@/api/client'
import TaskConfigPanel from '@/components/TaskConfigPanel.vue'
import LogPanel from '@/components/LogPanel.vue'
import AssistantSettingsPanel from '@/components/AssistantSettingsPanel.vue'
import UpdateDialog from '@/components/UpdateDialog.vue'
import FeedbackDialog from '@/components/FeedbackDialog.vue'
import PresetEditor from '@/views/PresetEditor.vue'
import { useWebSocket } from '@/api/ws'

const router = useRouter()
const appStore = useAppStore()
const message = useMessage()

const showCreateDialog = ref(false)
const newUsername = ref('')
const creating = ref(false)
const schedulerRunning = ref(false)
const schedulerStarting = ref(false)
const showUpdateDialog = ref(false)
const showFeedbackDialog = ref(false)

const currentView = ref<'overview' | 'task' | 'globallog' | 'assistant' | 'preset'>('overview')
const currentTaskName = ref<string | null>(null)

// 配置列表类型切换：账号配置（持久）/ 任务预设（临时）
const configTab = ref<'persist' | 'preset'>('persist')
const filteredConfigs = computed(() =>
  appStore.configs.filter((c: any) =>
    configTab.value === 'preset'
      ? c.config_type === '临时'
      : c.config_type !== '临时')
)
const createDialogType = ref<'persist' | 'preset'>('persist')
const createDialogTitle = computed(() => createDialogType.value === 'preset' ? '新建任务预设' : '新建账号配置')

// 任务数据
const rawTasks = ref<Record<string, any>>({})
const taskSchema = ref<Record<string, any>>({})

// 是否显示已禁用的任务
const showDisabledTasks = ref(false)

// 配置右键菜单
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
  configContextMenu.value = {
    show: true,
    x: e.clientX,
    y: e.clientY,
    configId,
    configName,
  }
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

// ---- 任务树分组 ----
// 匹配原版 Servicer 映射：task_type = 1 if 类型==5 else 类型
// 即类型 5（活动·APP类）与类型 1 同属“每周任务”组
const typeGroupMap: Record<number, string> = {
  0: '每日任务',
  1: '每周任务',
  2: '每周任务',
  3: '活动任务',
  4: '活动任务',
  5: '每周任务',
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

// ---- 加载任务数据 ----
async function loadTaskData() {
  if (!appStore.activeConfigId) {
    rawTasks.value = {}
    return
  }
  try {
    const res = await configApi.get(appStore.activeConfigId)
    rawTasks.value = res.data.tasks || {}
    // 加载 schema（仅一次）
    if (Object.keys(taskSchema.value).length === 0) {
      const schemaRes = await configApi.getDefaultTasks()
      taskSchema.value = schemaRes.data
    }
  } catch {
    rawTasks.value = {}
  }
}

// ---- 任务启用状态变更回调（来自 TaskConfigPanel） ----
function onTaskEnabledChanged(taskName: string, enabled: boolean) {
  if (rawTasks.value[taskName]) {
    rawTasks.value[taskName]['是否启用'] = enabled
  }
}

// ---- 视图切换 ----
function switchToGlobalLog() {
  currentView.value = 'globallog'
  currentTaskName.value = null
}

function switchToOverview() {
  currentView.value = 'overview'
  currentTaskName.value = null
  router.push({ name: 'Dashboard' })
}

function switchToTask(taskName: string) {
  currentView.value = 'task'
  currentTaskName.value = taskName
}

function switchToAssistant() {
  currentTaskName.value = null
  const cfg = appStore.configs.find((c: any) => c.id === appStore.activeConfigId)
  if (cfg?.config_type === '临时') {
    // 临时预设 → 直接进入 PresetEditor（预设设置 + 任务流程整体界面）
    currentView.value = 'preset'
  } else {
    currentView.value = 'assistant'
  }
}

function switchToSetting() {
  currentView.value = 'overview'
  currentTaskName.value = null
  router.push({ name: 'Settings' })
}

// ---- 配置选择 ----
async function selectConfig(id: string) {
  appStore.setActiveConfig(id)
  loadTaskData()
  // 点击左侧配置统一进入总览；预设的助手设置/任务流程通过中栏「助手设置」入口进入
  switchToOverview()
  // 查询该配置的调度器状态，确保按钮同步
  try {
    const res = await schedulerApi.status(id)
    schedulerRunning.value = res.data?.running ?? false
  } catch {
    schedulerRunning.value = false
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

// ---- 调度器 ----
async function toggleScheduler() {
  if (!appStore.activeConfigId) return
  if (schedulerRunning.value) { await stopScheduler() }
  else { await startScheduler() }
}

async function startScheduler() {
  if (!appStore.activeConfigId) return
  schedulerStarting.value = true
  try {
    await schedulerApi.start(appStore.activeConfigId)
    schedulerRunning.value = true
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '启动失败')
  } finally {
    schedulerStarting.value = false
  }
}

async function stopScheduler() {
  if (!appStore.activeConfigId) return
  try { await schedulerApi.stop(appStore.activeConfigId); schedulerRunning.value = false }
  catch { /* ignore */ }
}

// 监听调度器运行状态（含预设任务跑完自动停止），同步中栏启停按钮
const { onMessage } = useWebSocket()
const unsubSchedulerStatus = onMessage((msg) => {
  if (msg.type === 'status' && msg.data?.config_id === appStore.activeConfigId) {
    schedulerRunning.value = !!msg.data?.running
  }
})

// ---- 新建配置（账号配置/任务预设） ----
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
  } catch { /* ignore */ }
  finally { creating.value = false }
}

// ---- 复制配置 ----
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
  }).catch(() => {
    message.error('复制失败')
  })
}

// ---- 配置右键菜单操作 ----
function handleRenameConfig(configId: string, oldName: string) {
  const newName = prompt('请输入新的名称：', oldName)
  if (!newName || newName === oldName) return
  configApi.rename(configId, newName).then(() => {
    appStore.loadConfigs()
    message.success('重命名成功')
  }).catch(() => {
    message.error('重命名失败')
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
  }).catch(() => {
    message.error('删除失败')
  })
}

// 切换配置时重新加载任务数据并同步调度器状态
watch(() => appStore.activeConfigId, async (id) => {
  loadTaskData()
  if (id) {
    try {
      const res = await schedulerApi.status(id)
      schedulerRunning.value = res.data?.running ?? false
    } catch {
      schedulerRunning.value = false
    }
  } else {
    schedulerRunning.value = false
  }
})
async function handleScreenshot() {
  if (!appStore.activeConfigId) {
    message.warning('请先选择一个配置')
    return
  }
  try {
    const res = await deviceApi.saveScreenshot(appStore.activeConfigId)
    message.success(`截图已保存：${res.data?.path || ''}`)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '截图失败')
  }
}

function openFeedback() {
  if (!appStore.activeConfigId) {
    message.warning('请先选择一个配置')
    return
  }
  showFeedbackDialog.value = true
}

function openResourceGraph() {
  // hash 路由下，新标签页打开需带上当前 hash 前缀
  const href = router.resolve({ name: 'ResourceGraph' }).href
  window.open(href, '_blank')
}

onMounted(() => {
  appStore.checkBackendHealth()
  appStore.loadConfigs()
  checkUpdateOnStart()
})

// 程序启动时自动检查更新：仅在云端最新提交与本地最新提交不一致时弹出更新窗口
async function checkUpdateOnStart() {
  try {
    const res = await utilsApi.checkUpdate()
    if (res.data?.ok && res.data.has_update) {
      showUpdateDialog.value = true
    }
  } catch {
    // 网络异常时静默忽略，用户可随时通过顶部按钮手动检查
  }
}
onBeforeUnmount(() => {
  unsubSchedulerStatus()
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 16px;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
  background: #fff;
}
.topbar-left { display: flex; align-items: center; gap: 10px; }
.topbar-right { display: flex; align-items: center; gap: 20px; }
.topbar-logo-icon {
  width: 44px;
  height: 44px;
  margin-right: 6px;
  vertical-align: middle;
}
.topbar-brand {
  display: flex;
  align-items: center;
}
.github-icon {
  width: 26px;
  height: 26px;
  display: block;
  border-radius: 4px;
}
.main-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.col-configs {
  width: 130px;
  flex-shrink: 0;
  border-right: 1px solid #d5d5d5;
  padding: 8px 4px;
  overflow-y: auto;
  background: #fafafa;
}
.config-list-title {
  font-size: 13px;
  font-weight: 600;
  color: #999;
  text-align: center;
  padding: 4px 0 8px;
  border-bottom: 1px solid #eee;
  margin-bottom: 6px;
}
/* 账号配置 / 任务预设 切换 */
.config-type-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #eee;
}
.config-type-tab {
  flex: 1;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: #888;
  padding: 5px 0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}
.config-type-tab:hover { background: #eef1f4; }
.config-type-tab.active { color: #1677ff; background: #e6f4ff; }
.config-btn {
  padding: 6px 4px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
  text-align: center;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.config-btn:hover { background: #e8e8e8; }
.config-btn.active { background: #e6f4ff; border-color: #1677ff; }
.config-btn-name {
  font-size: 13px; font-weight: 600; color: #333;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.config-btn-id {
  font-size: 11px; color: #999;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.config-btn-add { margin-top: 8px; border: 1px dashed #ccc; }
.config-btn-add:hover { border-color: #1677ff; color: #1677ff; }
.col-center {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e8e8e8;
  background: #fafafa;
  overflow: hidden;
}
.top-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
}
.overview-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 7px 10px;
  cursor: pointer;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #fff;
  transition: all 0.15s;
  flex: 1;
  justify-content: center;
}
.overview-btn:hover { border-color: #1677ff; background: #e6f4ff; }
.overview-btn.active { border-color: #1677ff; background: #e6f4ff; }
.overview-btn-icon { font-size: 16px; }
.overview-btn-label { font-size: 15px; font-weight: 700; color: #000; }

.scheduler-toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.15s;
  flex: 1;
  justify-content: center;
  font-family: inherit;
  font-size: 15px;
  font-weight: 700;
  background: #fff;
}
.scheduler-toggle-btn.running {
  color: #e53935;
  border-color: #e53935;
}
.scheduler-toggle-btn.running:hover {
  background: #ffebee;
}
.scheduler-toggle-btn.stopped {
  color: #43a047;
  border-color: #43a047;
}
.scheduler-toggle-btn.stopped:hover {
  background: #e8f5e9;
}
.scheduler-toggle-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.scheduler-toggle-icon { font-size: 16px; line-height: 1; }

.tree-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 4px 8px;
}
.tree-divider-inline {
  margin: 6px 8px 4px;
}

.tree-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px 4px;
}
.tree-title {
  font-size: 16px;
  font-weight: 800;
  color: #000;
}

.tree-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0 4px 8px;
}

.tree-group {
  margin-bottom: 4px;
}

.tree-group-label {
  font-size: 15px;
  font-weight: 800;
  color: #000;
  padding: 4px 8px 2px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px 5px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.12s;
  margin: 1px 0;
}
.tree-node:hover { background: #e8e8e8; }
.tree-node.active { background: #d6e9ff; }
.tree-node.disabled .tree-node-name { color: #bbb; }

.tree-node-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tree-node-dot.enabled { background: #52c41a; }
.tree-node-dot.disabled { background: #e53935; }

.tree-node-name {
  font-size: 15px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-empty {
  text-align: center;
  padding: 20px 8px;
}

.col-content {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
/* 让 <a> 链接也变成弹性容器，方便居中图标 */
.topbar-icon-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 0;
}

/* 保证 n-icon 垂直居中（避免基线偏移） */
.topbar-right :deep(.n-icon) {
  vertical-align: middle;
}

/* 保证 img 垂直居中（GitHub 图标） */
.topbar-right img {
  vertical-align: middle;
}
</style>