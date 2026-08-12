<template>
  <div class="preset-editor">
    <!-- 顶部：标题 + 启动/停止 -->
    <div class="pe-header">
      <div class="pe-title">
        <span class="pe-name">{{ presetName || props.configId }}</span>
        <n-tag size="small" type="warning">临时预设 · 只执行一遍</n-tag>
        <n-tag v-if="schedulerRunning" size="small" type="error">运行中</n-tag>
      </div>

    </div>

    <!-- 设备与二级密码设置 -->
    <n-card size="small" title="控制模式 / 截图模式 / 二级密码" class="pe-card">
      <AssistantSettingsPanel :config-id="props.configId" />
    </n-card>

    <!-- 任务流程：勾选 + 拖拽排序 + 执行参数 -->
    <n-card size="small" title="任务流程（勾选即执行，拖拽调整顺序）" class="pe-card">
      <div class="pe-order-hint">
        拖动任务左侧手柄可调整执行顺序（实时保存）；运行时按顺序逐个执行，失败/超时的任务会被跳过并标记。
      </div>
      <div class="pe-task-list">
        <template v-for="(name, idx) in orderedTaskNames" :key="name">
          <div
            class="pe-task-row"
            :class="{ dragging: dragIndex === idx, failed: !!failedTasks[name] }"
            draggable="true"
            @dragstart="onDragStart(idx, $event)"
            @dragover.prevent
            @drop="onDrop(idx)"
          >
            <span class="pe-drag-handle" title="拖拽调整顺序">⠿</span>
            <span class="pe-task-idx">{{ idx + 1 }}</span>
            <n-switch
              size="small"
              :value="!!(tasks[name]?.是否启用)"
              @update:value="(v: boolean) => toggleTask(name, v)"
            />
            <span class="pe-task-name" :class="{ disabled: !(tasks[name]?.是否启用) }">{{ name }}</span>
            <n-button
              v-if="Object.keys(tasks[name]?.执行参数 || {}).length > 0"
              text
              size="tiny"
              class="pe-param-toggle"
              @click="toggleExpand(name)"
            >
              {{ expandedTask === name ? '收起参数 ▲' : '参数 ▼' }}
            </n-button>
            <span v-if="failedTasks[name]" class="pe-failed-tag" :title="failedTasks[name]">失败</span>
          </div>
          <!-- 执行参数展开：出现在当前任务卡片下方 -->
          <n-collapse-transition :show="expandedTask === name">
            <div v-if="expandedTask === name" class="pe-params-inline">
              <div
                v-for="(paramDetail, paramName) in (tasks[name]?.['执行参数'] || {})"
                :key="paramName"
                class="pe-param-row"
              >
                <div class="pe-param-label">
                  <div class="pe-param-main">{{ paramName }}</div>
                  <div v-if="paramDetail.描述" class="pe-param-desc">{{ paramDetail.描述 }}</div>
                </div>
                <div class="pe-param-control">
                  <n-input-number
                    v-if="paramDetail.类型 === 'INT'"
                    :value="paramDetail.当前值"
                    @update:value="(v: number | null) => onParamChange(name, paramName, v ?? 0)"
                    :min="paramDetail.最小值 ?? 0"
                    :max="paramDetail.最大值 ?? 100"
                    style="width: 110px"
                  />
                  <n-select
                    v-else-if="paramDetail.类型 === 'COMBOX'"
                    :value="paramDetail.当前值"
                    @update:value="(v: any) => onParamChange(name, paramName, v)"
                    :options="(paramDetail.枚举列表 || []).map((s: string) => ({ label: String(s), value: s }))"
                    style="width: 200px"
                  />
                  <n-switch
                    v-else-if="paramDetail.类型 === 'BOOL'"
                    :value="!!paramDetail.当前值"
                    @update:value="(v: boolean) => onParamChange(name, paramName, v)"
                  />
                  <n-text v-else depth="3" style="font-size: 12px">{{ paramDetail.当前值 }}</n-text>
                </div>
              </div>
              <n-empty
                v-if="Object.keys(tasks[name]?.['执行参数'] || {}).length === 0"
                description="该任务没有可配置的执行参数"
                style="padding: 8px 0"
              />
            </div>
          </n-collapse-transition>
        </template>
        <n-empty v-if="orderedTaskNames.length === 0" description="暂无任务数据" />
      </div>
    </n-card>

    <!-- 运行进度 -->
    <n-card v-if="schedulerRunning" size="small" title="执行进度" class="pe-card">
      <div class="pe-progress">
        <span class="pe-progress-text">{{ progressText }}</span>
        <n-progress :percentage="progressPercent" :show-indicator="false" height="8" />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'
import { configApi, schedulerApi } from '@/api/client'
import { useWebSocket } from '@/api/ws'
import AssistantSettingsPanel from '@/components/AssistantSettingsPanel.vue'

const props = defineProps<{ configId: string }>()
const message = useMessage()

const presetName = ref('')
const tasks = ref<Record<string, any>>({})
const taskOrder = ref<string[]>([])
const expandedTask = ref<string | null>(null)
const failedTasks = ref<Record<string, string>>({})

const schedulerRunning = ref(false)
const schedulerStarting = ref(false)
const runningTasks = ref<any[]>([])
/** 任务列表顺序：以保存的"任务执行顺序"为主，未收录的任务补到末尾 */
const orderedTaskNames = computed(() => {
  const names = [...taskOrder.value]
  for (const name of Object.keys(tasks.value)) {
    if (!names.includes(name)) names.push(name)
  }
  return names
})

/** 勾选且按顺序排列的任务（与调度器 once 模式实际执行顺序一致） */
const checkedOrdered = computed(() =>
  orderedTaskNames.value.filter((n) => tasks.value[n]?.是否启用),
)
const currentRunning = computed(() =>
  runningTasks.value.find((t) => t.status === 0) || null,
)
const currentIndex = computed(() => {
  if (!currentRunning.value) return -1
  return checkedOrdered.value.findIndex((n) => n === currentRunning.value.name)
})
const progressText = computed(() => {
  if (currentRunning.value && currentIndex.value >= 0) {
    return `正在执行第 ${currentIndex.value + 1}/${checkedOrdered.value.length} 个任务：${currentRunning.value.name}`
  }
  return `全部任务已执行完毕（共 ${checkedOrdered.value.length} 个）`
})
const progressPercent = computed(() => {
  if (checkedOrdered.value.length === 0) return 0
  if (currentIndex.value >= 0) return Math.round((currentIndex.value / checkedOrdered.value.length) * 100)
  return 100
})

async function loadPreset() {
  try {
    const res = await configApi.get(props.configId)
    presetName.value = res.data?.username || props.configId
    tasks.value = res.data?.tasks || {}
    const order = res.data?.setting_dics?.['任务执行顺序']
    taskOrder.value = Array.isArray(order) ? order : []
  } catch {
    tasks.value = {}
    taskOrder.value = []
  }
}

async function refreshStatus() {
  try {
    const s = await schedulerApi.status(props.configId)
    schedulerRunning.value = s.data?.running ?? false
  } catch {
    schedulerRunning.value = false
  }
  if (schedulerRunning.value) {
    try {
      const t = await schedulerApi.getTasks(props.configId)
      runningTasks.value = t.data || []
    } catch {
      runningTasks.value = []
    }
  } else {
    runningTasks.value = []
  }
}

// ---- 拖拽排序（原生 HTML5 DnD） ----
const dragIndex = ref<number | null>(null)
function onDragStart(idx: number, e: DragEvent) {
  dragIndex.value = idx
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}
function onDrop(idx: number) {
  if (dragIndex.value === null || dragIndex.value === idx) {
    dragIndex.value = null
    return
  }
  const arr = [...orderedTaskNames.value]
  const [item] = arr.splice(dragIndex.value, 1)
  arr.splice(idx, 0, item)
  taskOrder.value = arr
  dragIndex.value = null
  persistOrder()
}
function persistOrder() {
  configApi.updateTaskOrder(props.configId, taskOrder.value).catch(() => {
    message.warning('执行顺序保存失败')
  })
}

// ---- 任务勾选 ----
function toggleTask(name: string, enabled: boolean) {
  if (tasks.value[name]) tasks.value[name]['是否启用'] = enabled
  configApi.updateTask(props.configId, name, '是否启用', enabled).catch(() => {})
}

function toggleExpand(name: string) {
  expandedTask.value = expandedTask.value === name ? null : name
}

// ---- 执行参数编辑 ----
function onParamChange(taskName: string, paramName: string, value: any) {
  if (tasks.value[taskName]?.['执行参数']?.[paramName]) {
    tasks.value[taskName]['执行参数'][paramName]['当前值'] = value
  }
  configApi.updateTaskParam(props.configId, taskName, paramName, value).catch(() => {})
}

// ---- 调度器启动/停止 ----
async function toggleScheduler() {
  schedulerStarting.value = true
  try {
    if (schedulerRunning.value) {
      await schedulerApi.stop(props.configId)
      schedulerRunning.value = false
      runningTasks.value = []
    } else {
      await schedulerApi.start(props.configId)
      schedulerRunning.value = true
    }
    await refreshStatus()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '操作失败')
  } finally {
    schedulerStarting.value = false
  }
}

// ---- WebSocket：任务完成（失败标记）与运行状态 ----
const { onMessage } = useWebSocket()
const unsub = onMessage((msg) => {
  if (msg.type === 'task_state' && msg.config_id === props.configId) {
    if (msg.action === 'complete' && msg.name) {
      if (msg.error) {
        failedTasks.value[msg.name] = msg.error
      } else {
        delete failedTasks.value[msg.name]
      }
    }
    refreshStatus()
  } else if (msg.type === 'status' && msg.config_id === props.configId) {
    schedulerRunning.value = !!msg.data?.running
    refreshStatus()
  }
})

watch(
  () => props.configId,
  () => {
    failedTasks.value = {}
    expandedTask.value = null
    loadPreset()
    refreshStatus()
  },
)

onMounted(() => {
  loadPreset()
  refreshStatus()
})
onBeforeUnmount(() => unsub())
</script>

<style scoped>
.preset-editor {
  height: 100%;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.pe-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.pe-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pe-name {
  font-size: 18px;
  font-weight: 700;
  color: #222;
}
.pe-card {
  flex-shrink: 0;
}
.pe-order-hint {
  font-size: 12px;
  color: #888;
  margin-bottom: 10px;
}
.pe-task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.pe-task-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f8f9fa;
  border: 1px solid #e8e8e8;
  border-left: 3px solid #bbb;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.15s;
}
.pe-task-row:hover {
  background: #f0f1f3;
  border-color: #ccc;
}
.pe-task-row.dragging {
  opacity: 0.5;
  border-color: #1677ff;
}
.pe-task-row.failed {
  border-left-color: #e53935;
  background: #fff1f0;
}
.pe-drag-handle {
  color: #aaa;
  font-size: 14px;
  cursor: grab;
  user-select: none;
}
.pe-task-idx {
  font-size: 12px;
  font-weight: 700;
  color: #999;
  min-width: 1.5em;
  text-align: center;
  font-family: Consolas, monospace;
}
.pe-task-name {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pe-task-name.disabled {
  color: #bbb;
  font-weight: 400;
}
.pe-param-toggle {
  flex-shrink: 0;
}
.pe-failed-tag {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: #e53935;
  padding: 1px 6px;
  border-radius: 8px;
  cursor: help;
}
.pe-params-inline {
  margin: 2px 0 8px 30px;
  padding: 10px 12px;
  background: #fff;
  border: 1px dashed #d8d8d8;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.pe-param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.pe-param-label {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
}
.pe-param-main {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.pe-param-desc {
  font-size: 12px;
  color: #999;
  line-height: 1.4;
}
.pe-param-control {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
}
.pe-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.pe-progress-text {
  font-size: 13px;
  color: #555;
}
</style>
