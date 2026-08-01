<template>
  <div class="app-layout">
    <!-- 顶部栏 -->
    <div class="topbar">
      <div class="topbar-left">
        <n-gradient-text
          type="info" :size="18" style="font-weight: bold; cursor: pointer;"
          @click="switchToGlobalLog"
        >
          ☯ Xuan
        </n-gradient-text>
        <n-tag :type="appStore.backendConnected ? 'success' : 'error'" size="small" style="margin-left: 10px">
          {{ appStore.backendConnected ? '已连接' : '未连接' }}
        </n-tag>
      </div>
      <div class="topbar-right">
        <n-button text size="small" @click="appStore.checkBackendHealth()">
          <template #icon><n-icon><RefreshOutlined /></n-icon></template>
          刷新
        </n-button>
        <n-dropdown trigger="click" :options="menuOptions" @select="handleMenuSelect">
          <n-button text size="small">
            <template #icon><n-icon size="22"><MenuOutlined /></n-icon></template>
          </n-button>
        </n-dropdown>
      </div>
    </div>

    <!-- 主体三栏 -->
    <div class="main-body">
      <!-- 左侧：配置切换列表 -->
      <div class="col-configs">
        <div class="config-list-title">配置</div>
        <div
          v-for="cfg in appStore.configs"
          :key="cfg.id"
          class="config-btn"
          :class="{ active: cfg.id === appStore.activeConfigId }"
          @click="selectConfig(cfg.id)"
          @contextmenu.prevent="showConfigContextMenu($event, cfg.id, cfg.username)"
        >
          <div class="config-btn-name">{{ cfg.username || cfg.id }}</div>
          <div class="config-btn-id">{{ cfg.id }}</div>
        </div>
        <div class="config-btn config-btn-add" @click="showCreateDialog = true">
          <div class="config-btn-name">+ 新建</div>
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
            class="tree-node"
            :class="{ active: currentView === 'assistant' }"
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
        <template v-else-if="currentView === 'assistant'">
          <AssistantSettingsPanel v-if="appStore.activeConfigId" :config-id="appStore.activeConfigId" />
          <n-empty v-else description="请先选择配置" style="margin-top: 80px" />
        </template>
        <template v-else>
          <router-view />
        </template>
      </div>
    </div>

    <!-- 新建配置对话框 -->
    <n-modal v-model:show="showCreateDialog" title="新建配置" preset="card" style="width: 400px">
      <n-space vertical>
        <n-input v-model:value="newUsername" placeholder="输入用户名" />
        <n-button type="primary" block @click="handleCreateConfig" :loading="creating">创建</n-button>
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, h } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon, useMessage } from 'naive-ui'
import {
  RefreshOutlined, MenuOutlined, SettingsOutlined,
  AccountTreeOutlined, TaskOutlined
} from '@vicons/material'
import { useAppStore } from '@/stores/app'
import { configApi, schedulerApi } from '@/api/client'
import TaskConfigPanel from '@/components/TaskConfigPanel.vue'
import LogPanel from '@/components/LogPanel.vue'
import AssistantSettingsPanel from '@/components/AssistantSettingsPanel.vue'

const router = useRouter()
const appStore = useAppStore()
const message = useMessage()

const showCreateDialog = ref(false)
const newUsername = ref('')
const creating = ref(false)
const schedulerRunning = ref(false)
const schedulerStarting = ref(false)

const currentView = ref<'overview' | 'task' | 'globallog' | 'assistant'>('overview')
const currentTaskName = ref<string | null>(null)

// 任务数据
const rawTasks = ref<Record<string, any>>({})
const taskSchema = ref<Record<string, any>>({})

// 是否显示已禁用的任务
const showDisabledTasks = ref(false)

// 配置右键菜单
const configContextMenu = ref({ show: false, x: 0, y: 0, configId: '', configName: '' })
const configContextOptions = computed(() => [
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
  if (key === 'rename') {
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
  currentView.value = 'assistant'
  currentTaskName.value = null
}

// ---- 右上角菜单 ----
const menuOptions = [
  { label: '场景管理', key: 'Scenes', icon: () => h(NIcon, null, { default: () => h(AccountTreeOutlined) }) },
  { label: '任务优先级', key: 'TaskPriority', icon: () => h(NIcon, null, { default: () => h(TaskOutlined) }) },
  { type: 'divider' as const },
  { label: '设置', key: 'Settings', icon: () => h(NIcon, null, { default: () => h(SettingsOutlined) }) },
]

function handleMenuSelect(key: string) {
  router.push({ name: key })
}

// 独立页面路由（总览/设置/场景管理等）时，切回 overview 让 router-view 接管内容区
// 否则 currentView 停留在 task/assistant/globallog 时，内容区会被对应组件独占，设置页无法显示
const STANDALONE_ROUTES = ['Dashboard', 'Settings', 'Scenes', 'SceneEditor', 'TaskPriority', 'ConfigDetail']
watch(
  () => router.currentRoute.value.name,
  (name) => {
    if (name && (STANDALONE_ROUTES as string[]).includes(name as string)) {
      currentView.value = 'overview'
      currentTaskName.value = null
    }
  }
)

// ---- 配置选择 ----
async function selectConfig(id: string) {
  appStore.setActiveConfig(id)
  loadTaskData()
  switchToOverview()
  // 查询该配置的调度器状态，确保按钮同步
  try {
    const res = await schedulerApi.status(id)
    schedulerRunning.value = res.data?.running ?? false
  } catch {
    schedulerRunning.value = false
  }
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

// ---- 新建配置 ----
async function handleCreateConfig() {
  if (!newUsername.value) return
  creating.value = true
  try {
    await configApi.create(newUsername.value)
    await appStore.loadConfigs()
    showCreateDialog.value = false
    newUsername.value = ''
  } catch { /* ignore */ }
  finally { creating.value = false }
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

onMounted(() => {
  appStore.checkBackendHealth()
  appStore.loadConfigs()
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
  height: 44px;
  padding: 0 12px;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
  background: #fff;
}
.topbar-left { display: flex; align-items: center; }
.topbar-right { display: flex; align-items: center; gap: 4px; }
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
</style>