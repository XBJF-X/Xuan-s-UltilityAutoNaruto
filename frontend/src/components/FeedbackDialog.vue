<template>
  <n-modal
    v-model:show="showModel"
    preset="card"
    title="反馈"
    style="width: 560px"
    :mask-closable="!isPackaging"
    :closable="!isPackaging"
    @after-leave="reset"
  >
    <template v-if="loadingOptions">
      <div class="center-box">
        <n-spin size="large" />
        <n-text depth="3">正在读取日志目录...</n-text>
      </div>
    </template>

    <template v-else>
      <!-- 第一步：问题发生日期 -->
      <n-form label-placement="top" :show-feedback="false">
        <n-form-item label="问题发生日期">
          <n-select
            v-model:value="selectedDate"
            :options="dateOptions"
            placeholder="请选择日期"
            clearable
          />
        </n-form-item>

        <!-- 第二步：出现问题的任务（仅当所选日期存在 screenshot 目录时显示） -->
        <n-form-item v-if="showTaskStep" label="出现问题的任务">
          <n-select
            v-model:value="selectedTasks"
            :options="taskOptions"
            multiple
            placeholder="请选择任务（可多选）"
          />
          <template #feedback>
            <n-text depth="3" style="font-size: 12px">留空表示不包含截图，仅打包日志</n-text>
          </template>
        </n-form-item>

        <!-- 保存位置 -->
        <n-form-item label="压缩包保存位置">
          <n-input-group>
            <n-input v-model:value="savePath" placeholder="请选择保存位置" readonly />
            <n-button @click="browse" :loading="browsing">选择...</n-button>
          </n-input-group>
        </n-form-item>
      </n-form>

      <!-- 打包进度 -->
      <template v-if="isPackaging">
        <n-card size="small" class="progress-card">
          <div class="phase-row">
            <n-text :type="progress.error ? 'error' : 'primary'" weight="bold">
              {{ phaseLabel }}
            </n-text>
          </div>
          <n-progress
            type="line"
            :percentage="progress.percent"
            :status="progress.error ? 'error' : undefined"
            :processing="progress.running && !progress.error"
            indicator-placement="inside"
            height="14"
          />
          <n-text depth="3" class="phase-msg">{{ progress.message }}</n-text>
        </n-card>
      </template>

    </template>

    <template #footer>
      <n-space justify="end">
        <n-button @click="close" :disabled="isPackaging">取消</n-button>
        <n-button
          type="primary"
          :disabled="!canSubmit"
          :loading="starting"
          @click="startPackage"
        >
          生成反馈包
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'
import { utilsApi } from '@/api/client'

const props = defineProps<{
  show: boolean
  configId: string | null
}>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const showModel = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const message = useMessage()
const loadingOptions = ref(false)
const dateOptions = ref<{ label: string; value: string }[]>([])
const taskOptions = ref<{ label: string; value: string }[]>([])
const selectedDate = ref<string | null>(null)
const selectedTasks = ref<string[]>([])
const savePath = ref('')
const browsing = ref(false)
const isPackaging = ref(false)
const starting = ref(false)
const progress = ref<{ running: boolean; phase: string; percent: number; message: string; error: string }>({
  running: false, phase: '', percent: 0, message: '', error: '',
})

let pollTimer: ReturnType<typeof setInterval> | null = null

const showTaskStep = computed(() => !!selectedDate.value && taskOptions.value.length > 0)
const canSubmit = computed(() => {
  if (isPackaging.value) return false
  if (!selectedDate.value) return false
  if (!savePath.value) return false
  // 日期有截图但未选任务时，仍允许（不带截图打包）；无截图日期直接允许
  return true
})

const phaseLabel = computed(() => {
  const map: Record<string, string> = {
    zipping: '压缩中',
    done: '打包完成',
    error: '打包失败',
  }
  return map[progress.value.phase] || '准备中'
})

async function loadOptions() {
  loadingOptions.value = true
  try {
    const res = await utilsApi.feedbackOptions(props.configId || '')
    const data = res.data
    if (data?.ok) {
      dateOptions.value = (data.dates || []).map((d: { label?: string; date: string }) => ({
        label: d.label || d.date,
        value: d.date,
      }))
    } else {
      message.warning(data?.message || '读取日志目录失败')
    }
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '读取日志目录失败')
  } finally {
    loadingOptions.value = false
  }
}

async function browse() {
  browsing.value = true
  try {
    const res = await utilsApi.browseFolder('选择压缩包保存位置')
    const data = res.data
    if (data?.ok && data.path) {
      savePath.value = data.path
    }
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '选择文件夹失败')
  } finally {
    browsing.value = false
  }
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

async function startPackage() {
  if (!selectedDate.value || !savePath.value) return
  isPackaging.value = true
  starting.value = true
  try {
    const res = await utilsApi.feedbackPackage({
      config_id: props.configId || '',
      date: selectedDate.value,
      task_names: selectedTasks.value,
      save_path: savePath.value,
    })
    if (!res.data?.ok) {
      message.error(res.data?.message || '启动打包失败')
      isPackaging.value = false
      return
    }
    pollTimer = setInterval(async () => {
      try {
        const stRes = await utilsApi.feedbackStatus()
        const st = stRes.data
        if (!st) return
        progress.value = {
          running: st.running,
          phase: st.phase,
          percent: st.percent ?? 0,
          message: st.message || '',
          error: st.error || '',
        }
        if (st.phase === 'done') {
          stopPolling()
          message.success(st.message || (st.output ? `反馈包已生成：${st.output}` : '打包完成'))
          setTimeout(() => {
            isPackaging.value = false
            close()
          }, 1500)
        } else if (st.phase === 'error') {
          stopPolling()
          message.error(st.message || '打包失败')
          isPackaging.value = false
        }
      } catch { /* 忽略轮询错误 */ }
    }, 800)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '启动打包失败')
    isPackaging.value = false
  } finally {
    starting.value = false
  }
}

function reset() {
  stopPolling()
  loadingOptions.value = false
  dateOptions.value = []
  taskOptions.value = []
  selectedDate.value = null
  selectedTasks.value = []
  savePath.value = ''
  isPackaging.value = false
  starting.value = false
  progress.value = { running: false, phase: '', percent: 0, message: '', error: '' }
}

function close() {
  emit('update:show', false)
}

watch(() => props.show, (v) => {
  if (v) {
    loadOptions()
  } else {
    reset()
  }
})

watch(selectedDate, async (date) => {
  taskOptions.value = []
  if (!date) return
  try {
    const res = await utilsApi.feedbackOptions(props.configId || '', date)
    const data = res.data
    if (data?.ok) {
      const tasks = data.tasks || []
      taskOptions.value = tasks.map((t: string) => ({ label: t, value: t }))
      // 如果只有一个任务目录则默认选中
      if (tasks.length === 1) {
        selectedTasks.value = [tasks[0]]
      }
    } else {
      taskOptions.value = []
    }
  } catch {
    taskOptions.value = []
  }
})

onBeforeUnmount(stopPolling)
</script>

<style scoped>
.center-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 0;
}
.progress-card { margin-bottom: 12px; }
.phase-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.phase-msg {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  word-break: break-all;
}
</style>