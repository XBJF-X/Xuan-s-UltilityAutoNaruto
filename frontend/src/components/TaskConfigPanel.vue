<template>
  <div class="task-config-panel">
    <template v-if="!loadedConfig">
      <n-empty description="请先选择配置">
        <template #extra>
          <n-button @click="$router.push({ name: 'Dashboard' })">前往总览</n-button>
        </template>
      </n-empty>
    </template>
    <template v-else-if="!currentTaskName">
      <n-empty description="请在左侧选择一个任务" />
    </template>
    <template v-else-if="currentTask">
      <div class="config-scroll">
        <!-- 基础设置卡片 -->
        <div class="config-card">
          <div class="card-title">{{ currentTaskName }} | 任务设置</div>
          <div class="card-divider"></div>
          <div v-if="currentTask.描述" class="card-desc">{{ currentTask.描述 }}</div>
          <div class="param-grid">
            <div class="param-row">
              <div class="param-label">
                <div class="param-label-main">启用任务</div>
                <div class="param-label-desc">将这个任务加入调度器</div>
              </div>
              <div class="param-control">
                <n-switch
                  :value="currentTask.是否启用"
                  @update:value="(v: boolean) => updateTaskField('是否启用', v)"
                />
              </div>
            </div>
            <div class="param-row">
              <div class="param-label">
                <div class="param-label-main">下次执行时间</div>
                <div class="param-label-desc">自动计算得出，无须修改</div>
              </div>
              <div class="param-control">
                <n-input
                  :value="formattedNextTime"
                  disabled
                  style="min-width: 240px; text-align: center; font-size: 16px;"
                />
              </div>
            </div>
            <div class="param-row">
              <div class="param-label">
                <div class="param-label-main">可执行窗口</div>
                <div class="param-label-desc">任务的声明式排期（窗口 + 周期）</div>
              </div>
              <div class="param-control">
                <n-input
                  :value="taskSchedule"
                  disabled
                  style="min-width: 240px; text-align: center;"
                />
              </div>
            </div>

          </div>
        </div>

        <!-- 执行参数卡片 -->
        <div v-if="execParams && Object.keys(execParams).length > 0" class="config-card">
          <div class="card-title">{{ currentTaskName }}</div>
          <div class="card-divider"></div>
          <div class="param-grid">
            <div v-for="(paramDetail, paramName) in execParams" :key="paramName" class="param-row">
              <div class="param-label">
                <div class="param-label-main">{{ paramName }}</div>
                <div v-if="paramDetail.描述" class="param-label-desc">{{ paramDetail.描述 }}</div>
              </div>
              <div class="param-control">
                <!-- INT 类型 -->
                <n-input-number
                  v-if="paramDetail.类型 === 'INT'"
                  :value="paramDetail.当前值"
                  @update:value="(v: number | null) => onParamChange(paramName as string, v ?? 0)"
                  :min="paramDetail.最小值 ?? 0"
                  :max="paramDetail.最大值 ?? 100"
                  style="width: 100px"
                />
                <!-- COMBOX 类型 -->
                <n-select
                  v-else-if="paramDetail.类型 === 'COMBOX'"
                  :value="paramDetail.当前值"
                  @update:value="(v: number | string) => onParamChange(paramName as string, v as number)"
                  :options="comboOptions(paramDetail)"
                  :style="{ width: comboWidth(paramDetail) + 'px' }"
                />
                <!-- BOOL 类型 -->
                <n-switch
                  v-else-if="paramDetail.类型 === 'BOOL'"
                  :value="paramDetail.当前值"
                  @update:value="(v: boolean) => onParamChange(paramName as string, v)"
                />
                <n-text v-else depth="3" style="font-size: 12px">
                  不支持的参数类型: {{ paramDetail.类型 }}
                </n-text>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <n-empty description="未找到任务数据" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { configApi, schedulerApi } from '@/api/client'

const props = defineProps<{
  taskName: string | null
}>()

const emit = defineEmits<{
  (e: 'task-enabled-changed', taskName: string, enabled: boolean): void
}>()

const appStore = useAppStore()
const loadedConfig = ref<any>(null)
const rawTasks = ref<Record<string, any>>({})

const currentTaskName = computed(() => props.taskName)

const currentTask = computed(() => {
  if (!currentTaskName.value || !rawTasks.value[currentTaskName.value]) return null
  return rawTasks.value[currentTaskName.value]
})

const execParams = computed(() => {
  return currentTask.value?.['执行参数'] ?? {}
})

const formattedNextTime = computed(() => {
  const t = currentTask.value?.['下次执行时间']
  if (!t || t === 0) return '-'
  // 如果是时间戳数字，转换为日期字符串
  if (typeof t === 'number') {
    const d = new Date(t * 1000)
    const pad = (n: number) => n.toString().padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  }
  // 已经是字符串则直接返回
  return t
})

/** 任务排期描述（窗口 + 周期）：取自调度器状态快照；调度器未启动时显示 — */
const taskSchedule = computed(() => {
  const snap = appStore.schedulerSnapshots[appStore.activeConfigId as string]
  const entry = (snap?.tasks || []).find((t: any) => t.name === currentTaskName.value)
  return entry?.schedule || '—'
})

function comboOptions(detail: any) {
  return (detail.枚举列表 || []).map((label: string, idx: number) => ({
    label,
    value: idx,
  }))
}

/** 根据枚举列表最长文本估算下拉框宽度 */
function comboWidth(detail: any): number {
  const list: string[] = detail.枚举列表 || []
  if (list.length === 0) return 200
  const maxLen = Math.max(...list.map((s: string) => s.length))
  // 每个中文字符约 16px，加上 padding 和箭头空间
  return Math.max(180, Math.min(maxLen * 16 + 40, 400))
}

function updateTaskField(field: string, value: boolean | number) {
  if (!currentTaskName.value || !rawTasks.value[currentTaskName.value]) return
  rawTasks.value[currentTaskName.value][field] = value
  // 保存到后端配置文件
  configApi.updateTask(appStore.activeConfigId!, currentTaskName.value, field, value).catch(() => {})
  // 通知父组件任务启用状态变化，以便刷新树节点指示灯
  if (field === '是否启用') {
    emit('task-enabled-changed', currentTaskName.value, value as boolean)
    // 同时也通知调度器（发送 WebSocket 消息触发 Dashboard 刷新）
    schedulerApi.toggleActivation(appStore.activeConfigId!, currentTaskName.value, value as boolean).catch(() => {})
  }
}

function updateExecParam(paramName: string, value: boolean | number | string) {
  if (!currentTaskName.value || !rawTasks.value[currentTaskName.value]) return
  const param = rawTasks.value[currentTaskName.value]['执行参数']?.[paramName]
  if (param) {
    param.当前值 = value
  }
  configApi.updateTaskParam(appStore.activeConfigId!, currentTaskName.value, paramName, value).catch(() => {})
}

function onParamChange(paramName: string, value: boolean | number | string) {
  updateExecParam(paramName, value)
}

async function loadConfigTasks() {
  if (!appStore.activeConfigId) {
    loadedConfig.value = null
    rawTasks.value = {}
    return
  }
  try {
    const res = await configApi.get(appStore.activeConfigId)
    loadedConfig.value = res.data
    rawTasks.value = JSON.parse(JSON.stringify(res.data.tasks || {}))
  } catch {
    loadedConfig.value = null
    rawTasks.value = {}
  }
}

watch(() => appStore.activeConfigId, () => {
  loadConfigTasks()
})

onMounted(() => {
  loadConfigTasks()
})
</script>

<style scoped>
.task-config-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
}
.config-scroll {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.config-card {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 12px 0;
}
.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #222;
  margin: 0 14px 6px;
}
.card-divider {
  height: 1px;
  background: #d0d0d0;
  margin: 0 14px 10px;
}
.card-desc {
  font-size: 15px;
  color: rgba(255, 0, 0, 0.5);
  margin: 0 14px 10px 22px;
  line-height: 1.5;
}
.param-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 14px 0 24px;
}
.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 40px;
}
.param-label {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
}
.param-label-main {
  font-size: 17px;
  font-weight: 600;
  color: #222;
}
.param-label-desc {
  font-size: 14px;
  color: #959595;
  margin-left: 18px;
  line-height: 1.4;
}
.param-control {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  min-width: 80px;
}
</style>
