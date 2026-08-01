<template>
  <div class="priority-panel">
    <!-- 排序方式 -->
    <n-space align="center" style="margin-bottom: 12px">
      <n-text depth="3">排序方式：</n-text>
      <n-radio-group v-model:value="localSortMode" @update:value="emit('update:sortMode', $event)">
        <n-radio-button value="name">按任务名</n-radio-button>
        <n-radio-button value="priority">按优先级</n-radio-button>
      </n-radio-group>
    </n-space>

    <n-grid :cols="2" :x-gap="12">
      <n-grid-item>
        <n-card title="编辑" size="small" :bordered="true">
          <template #header-extra>
            <n-tag size="small" type="warning">值越小越先执行</n-tag>
          </template>
          <div class="edit-list">
            <n-scrollbar style="max-height: 500px">
              <n-list bordered>
                <n-list-item v-for="task in sortedTasks" :key="task.name">
                  <n-thing>
                    <template #header>
                      <n-space align="center" justify="space-between">
                        <n-text>{{ task.name }}</n-text>
                        <n-tag size="tiny" :type="getRankType(getTaskRank(task.name))">
                          第 {{ getTaskRank(task.name) }} 顺位
                        </n-tag>
                      </n-space>
                    </template>
                    <template #description>
                      <n-input-number
                        v-model:value="taskValues[task.name]"
                        :min="-999"
                        :max="999"
                        :step="1"
                        size="small"
                        style="width: 120px"
                        @update:value="onPriorityChanged"
                      />
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-scrollbar>
          </div>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card title="执行顺序预览" size="small" :bordered="true">
          <n-scrollbar style="max-height: 500px">
            <n-list bordered>
              <n-list-item v-for="(task, idx) in orderedPreview" :key="task.name">
                <n-thing>
                  <template #header>
                    <n-space align="center">
                      <n-badge :value="task.rank" color="#18a058" />
                      <n-text>{{ task.name }}</n-text>
                    </n-space>
                  </template>
                  <template #description>
                    <n-text depth="3">优先级: {{ taskValues[task.name] }}</n-text>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-scrollbar>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  tasks: Record<string, any>
  sortMode: 'name' | 'priority'
  keyName: string
}>()

const emit = defineEmits<{
  'update:sortMode': [value: 'name' | 'priority']
  'update:taskValues': [values: Record<string, number>]
}>()

const localSortMode = ref(props.sortMode)

// 从 tasks 中提取优先级值到本地响应式对象
const taskValues = ref<Record<string, number>>({})

watch(() => props.tasks, (val) => {
  const vals: Record<string, number> = {}
  for (const [name, info] of Object.entries(val || {})) {
    vals[name] = info[props.keyName] ?? 0
  }
  taskValues.value = vals
}, { immediate: true, deep: true })

// 排序后的任务列表
const sortedTasks = computed(() => {
  const entries = Object.entries(props.tasks || {})
  if (localSortMode.value === 'priority') {
    entries.sort(([, a], [, b]) => {
      const pa = taskValues.value[a.name!] ?? 0
      const pb = taskValues.value[b.name!] ?? 0
      return pa - pb || a.name!.localeCompare(b.name!)
    })
  } else {
    entries.sort(([a], [b]) => a.localeCompare(b))
  }
  return entries.map(([name]) => ({ name, ...(props.tasks?.[name] || {}) }))
})

// 执行顺序预览（按优先级升序排列+顺位编号）
const orderedPreview = computed(() => {
  const entries = Object.entries(props.tasks || {}).map(([name]) => ({
    name,
    priority: taskValues.value[name] ?? 0,
  }))
  entries.sort((a, b) => a.priority - b.priority || a.name.localeCompare(b.name))

  let rank = 0
  let prevPriority: number | null = null
  return entries.map((entry) => {
    if (entry.priority !== prevPriority) {
      rank++
      prevPriority = entry.priority
    }
    return { ...entry, rank }
  })
})

function getTaskRank(taskName: string): number {
  const p = taskValues.value[taskName] ?? 0
  // 去重计 rank: 读取 orderedPreview
  const found = orderedPreview.value.find(t => t.name === taskName)
  return found?.rank ?? 0
}

function getRankType(rank: number): 'success' | 'warning' | 'error' | 'info' {
  if (rank <= 3) return 'success'
  if (rank <= 10) return 'info'
  if (rank <= 20) return 'warning'
  return 'error'
}

function onPriorityChanged() {
  emit('update:taskValues', { ...taskValues.value })
}
</script>

<style scoped>
.priority-panel {
  width: 100%;
}
.edit-list {
  width: 100%;
}
</style>