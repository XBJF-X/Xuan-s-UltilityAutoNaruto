<template>
  <div class="task-priority-editor">
    <n-space vertical size="medium">
      <!-- 顶部工具栏 -->
      <n-card size="small">
        <n-space align="center">
          <n-h3 style="margin: 0">任务优先级编辑器</n-h3>
          <n-divider vertical />
          <n-form-item label="选择配置" :show-feedback="false" style="margin-bottom: 0">
            <n-select v-model:value="selectedConfigId" :options="configOptions"
              placeholder="请选择配置" style="width: 220px" @update:value="loadTasks" />
          </n-form-item>
          <n-button @click="loadTasks" :loading="loadingTasks" size="small">
            <template #icon><n-icon><RefreshOutlined /></n-icon></template>
            刷新
          </n-button>
          <n-divider vertical />
          <n-button type="primary" @click="savePriority" :loading="saving" size="small"
            :disabled="!selectedConfigId">
            <template #icon><n-icon><SaveOutlined /></n-icon></template>
            保存优先级
          </n-button>
        </n-space>
      </n-card>

      <!-- 任务列表 -->
      <n-card v-if="selectedConfigId">
        <template #header>
          <n-text>任务列表（共 {{ tasks.length }} 个任务，拖拽调整顺序）</n-text>
        </template>
        <n-spin :show="loadingTasks">
          <div class="task-list">
            <n-empty v-if="tasks.length === 0 && !loadingTasks" description="暂无任务数据" />
            <div v-for="(task, idx) in tasks" :key="task.name" class="task-item"
              draggable="true"
              @dragstart="handleDragStart($event, idx)"
              @dragover.prevent="handleDragOver($event, idx)"
              @dragend="handleDragEnd"
              @drop="handleDrop($event, idx)"
              :class="{ 'drag-over': dragOverIndex === idx, 'dragging': dragIndex === idx }"
            >
              <div class="drag-handle">
                <n-icon size="20"><MenuOutlined /></n-icon>
                <n-tag size="small" type="info" :bordered="false">{{ idx + 1 }}</n-tag>
              </div>
              <div class="task-info">
                <n-space align="center">
                  <n-text strong>{{ task.display_name || task.name }}</n-text>
                  <n-tag v-if="task.task_type" size="tiny" :bordered="false" type="success">
                    {{ task.task_type }}
                  </n-tag>
                </n-space>
                <n-text depth="3" style="font-size: 12px">{{ task.description || task.name }}</n-text>
              </div>
              <div class="task-actions">
                <n-switch v-model:value="task.is_active" @update:value="(val: boolean) => handleToggleActivation(task, val)">
                  <template #checked>激活</template>
                  <template #unchecked>禁用</template>
                </n-switch>
              </div>
            </div>
          </div>
        </n-spin>
      </n-card>

      <n-card v-else>
        <n-empty description="请选择配置文件" />
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { RefreshOutlined, SaveOutlined, MenuOutlined } from '@vicons/material'
import { configApi, schedulerApi } from '@/api/client'

const message = useMessage()

// State
const configs = ref<any[]>([])
const tasks = ref<any[]>([])
const selectedConfigId = ref<string | null>(null)
const loadingTasks = ref(false)
const saving = ref(false)

// Drag state
const dragIndex = ref<number | null>(null)
const dragOverIndex = ref<number | null>(null)

// Config options
const configOptions = computed(() =>
  configs.value.map((c: any) => ({ label: c.id || c.username, value: c.id || c.username }))
)

// API: Load configs
async function loadConfigs() {
  try {
    const res = await configApi.list()
    configs.value = (res.data || []) as any[]
  } catch (e: any) {
    message.error('加载配置列表失败: ' + (e.response?.data?.detail || e.message))
  }
}

// API: Load tasks for selected config
async function loadTasks() {
  if (!selectedConfigId.value) return
  loadingTasks.value = true
  try {
    // 从配置 API 获取任务定义（dict 格式），不依赖调度器是否运行
    const configRes = await configApi.get(selectedConfigId.value)
    const configData = configRes.data as any
    const tasksDict = configData.tasks || {}
    const priorityOrder: string[] = configData.setting_dics?.["任务优先级顺序"] || []

    // 将 dict 转为数组，保留激活状态，按优先级排序
    let rawTasks = Object.keys(tasksDict).map((name: string) => ({
      name,
      display_name: name,
      is_active: tasksDict[name]?.["是否启用"] !== false,
    }))

    // 按存储的优先级顺序排列
    if (priorityOrder.length > 0) {
      const orderMap = new Map(priorityOrder.map((n, i) => [n, i]))
      rawTasks.sort((a: any, b: any) => {
        const ai = orderMap.get(a.name)
        const bi = orderMap.get(b.name)
        if (ai !== undefined && bi !== undefined) return ai - bi
        if (ai !== undefined) return -1
        if (bi !== undefined) return 1
        return 0
      })
    }
    tasks.value = rawTasks
  } catch (e: any) {
    message.error('加载任务失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    loadingTasks.value = false
  }
}

// Drag and Drop
function handleDragStart(e: DragEvent, idx: number) {
  dragIndex.value = idx
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(idx))
  }
}

function handleDragOver(_e: DragEvent, idx: number) {
  dragOverIndex.value = idx
}

function handleDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
}

function handleDrop(e: DragEvent, targetIdx: number) {
  e.preventDefault()
  const sourceIdx = dragIndex.value
  if (sourceIdx === null || sourceIdx === targetIdx) return

  // Reorder tasks
  const items = [...tasks.value]
  const [moved] = items.splice(sourceIdx, 1)
  items.splice(targetIdx, 0, moved)
  tasks.value = items

  dragIndex.value = null
  dragOverIndex.value = null
}

// Toggle activation
async function handleToggleActivation(task: any, state: boolean) {
  if (!selectedConfigId.value) return
  try {
    await schedulerApi.toggleActivation(selectedConfigId.value, task.name, state)
    message.success(`任务 "${task.display_name || task.name}" 已${state ? '激活' : '禁用'}`)
  } catch (e: any) {
    // 恢复状态
    task.is_active = !state
    message.error('切换失败: ' + (e.response?.data?.detail || e.message))
  }
}

// Save priority
async function savePriority() {
  if (!selectedConfigId.value) return
  saving.value = true
  try {
    // 构建任务排序列表，发送到后端批量更新
    const orderedTaskNames = tasks.value.map((t: any) => t.name)
    await configApi.updateTaskPriorities(selectedConfigId.value, orderedTaskNames)
    message.success('优先级保存成功')
  } catch (e: any) {
    message.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.task-priority-editor {
  padding: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid var(--n-border-color);
  border-radius: 4px;
  background: var(--n-color);
  transition: background 0.2s, transform 0.15s;
  cursor: grab;
  user-select: none;
}

.task-item:hover {
  background: var(--n-hover-color);
}

.task-item.dragging {
  opacity: 0.5;
  transform: scale(0.98);
}

.task-item.drag-over {
  border-color: var(--n-primary-color);
  background: rgba(64, 158, 255, 0.08);
  border-style: dashed;
}

.drag-handle {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-right: 12px;
  color: var(--n-text-color-3);
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-actions {
  margin-left: auto;
  flex-shrink: 0;
}
</style>