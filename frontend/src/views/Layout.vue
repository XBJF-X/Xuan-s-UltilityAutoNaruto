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

    <!-- 切换配置加载遮罩：除左侧配置切换面板（col-configs）外，其余部分全部拦截点击，避免竞态 -->
    <div v-if="appStore.configSwitching" class="config-switching-mask">
      <n-spin size="small" />
      <span class="config-switching-mask-text">正在加载配置...</span>
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
    <FeedbackDialog
      v-model:show="showFeedbackDialog"
      :config-id="appStore.activeConfigId"
      @open-update="showUpdateDialog = true"
    />

    <!-- 启动引导提示：程序启动时弹出，10s 内不可关闭，勾选「不再提示」后不再弹出 -->
    <StartupNoticeDialog v-model:show="showStartupNotice" @go-feedback="handleStartupGoFeedback" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  RefreshOutlined, SettingsOutlined, SystemUpdateOutlined,
  FolderOpenOutlined, HelpOutlineOutlined, CameraOutlined, HubOutlined,
} from '@vicons/material'
import githubIcon from '@/assets/GithubIcon.png'
import asdsIcon from '@/assets/ASDS.ico'
import { useAppStore } from '@/stores/app'
import TaskConfigPanel from '@/components/TaskConfigPanel.vue'
import LogPanel from '@/components/LogPanel.vue'
import AssistantSettingsPanel from '@/components/AssistantSettingsPanel.vue'
import UpdateDialog from '@/components/UpdateDialog.vue'
import FeedbackDialog from '@/components/FeedbackDialog.vue'
import StartupNoticeDialog from '@/components/StartupNoticeDialog.vue'
import PresetEditor from '@/views/PresetEditor.vue'
// 阶段 5：把任务树 / 调度器控制 / 启动检查 / 配置列表与切换四块职责抽成 composable
// （Layout 只做编排与模板）
import { useTaskTree } from '@/composables/useTaskTree'
import { useSchedulerControl } from '@/composables/useSchedulerControl'
import { useStartupChecks } from '@/composables/useStartupChecks'
import { useConfigs } from '@/composables/useConfigs'

const router = useRouter()
const appStore = useAppStore()

// ---- 任务树（任务数据 / 分组 / 启用状态同步）----
const {
  rawTasks, showDisabledTasks, taskGroups, enabledTaskNames,
  loadTaskData, onTaskEnabledChanged,
} = useTaskTree()

// ---- 调度器控制（启停 + 状态/快照 WS 订阅）----
const {
  schedulerRunning, schedulerStarting, toggleScheduler, startScheduler, stopScheduler,
} = useSchedulerControl()

// ---- 启动检查（引导/依赖/自动更新）与截图、反馈入口 ----
const {
  showUpdateDialog, showFeedbackDialog, showStartupNotice,
  checkStartupNotice, checkDependencyOnStart, checkUpdateOnStart,
  handleStartupGoFeedback, handleScreenshot, openFeedback,
} = useStartupChecks()

const currentView = ref<'overview' | 'task' | 'globallog' | 'assistant' | 'preset'>('overview')
const currentTaskName = ref<string | null>(null)

// ---- 配置列表与切换（类型页签 / 增删改 / 右键菜单 / 切换编排）----
// 与其它 composable 的耦合以回调注入：视图切换、任务数据加载、调度器运行状态
const {
  configTab, filteredConfigs, createDialogType, createDialogTitle,
  showCreateDialog, newUsername, creating,
  configContextMenu, configContextOptions,
  showConfigContextMenu, handleConfigContextSelect,
  selectConfig, switchConfigTab, openCreateDialog, handleCreateConfig,
  handleDuplicateConfig, handleRenameConfig, handleDeleteConfig,
} = useConfigs({
  switchToOverview: () => switchToOverview(),
  loadTaskData,
  schedulerRunning,
})

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


/** 资源图/资源管理页：hash 路由下新标签页打开需带上当前 hash 前缀 */
function openResourceGraph() {
  const href = router.resolve({ name: 'ResourceGraph' }).href
  window.open(href, '_blank')
}

// 启动流程：健康检查 + 配置列表 + 依赖检查 / 自动更新 / 使用引导
// （三项检查的实现见 composables/useStartupChecks.ts，此处只做编排）
onMounted(() => {
  appStore.checkBackendHealth()
  appStore.loadConfigs()
  checkDependencyOnStart()
  checkUpdateOnStart()
  checkStartupNotice()
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
  z-index: 51;
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
  /* 切换配置期间置于全屏遮罩之上，保持可点击（其余区域全部被遮罩拦截） */
  position: relative;
  z-index: 51;
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
/* 切换配置时的全屏加载遮罩：覆盖顶部栏/中栏/右侧内容区，仅左侧配置切换面板（z-index 51）可点击 */
.config-switching-mask {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(1px);
  cursor: wait;
}
.config-switching-mask-text {
  font-size: 13px;
  color: #666;
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
