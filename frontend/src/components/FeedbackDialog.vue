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
      <!-- 代码版本检测（打开反馈界面即自动检查）：非最新时提示先更新，更新后仍存在问题再反馈 -->
      <n-alert
        v-if="codeCheckState === 'checking'"
        type="info"
        class="code-check-bar"
        :show-icon="false"
      >
        正在检查当前代码是否为最新...
      </n-alert>
      <n-alert
        v-else-if="codeCheckState === 'outdated'"
        type="warning"
        title="当前代码非最新"
        class="code-check-bar"
      >
        <div class="code-check-msg">{{ codeCheckMessage }}</div>
        <div class="code-check-actions">
          <n-button size="small" type="primary" @click="openUpdate">去更新</n-button>
          <n-text depth="3" style="font-size: 12px">
            若有问题可先尝试更新后看是否解决，未解决再按下方步骤生成反馈包
          </n-text>
        </div>
      </n-alert>
      <n-alert
        v-else-if="codeCheckState === 'unknown'"
        type="default"
        class="code-check-bar"
        :show-icon="false"
      >
        未能检测当前代码是否为最新（{{ codeCheckMessage }}），可忽略此提示直接生成反馈包
      </n-alert>

      <!-- 顶部：打开本地日志目录（打包反馈前核对日志文件） -->
      <div class="log-dir-bar">
        <n-text depth="3" style="font-size: 12px; flex: 1;">打包前如需核对日志文件，可先在系统文件管理器中打开本地日志目录</n-text>
        <n-button size="small" :loading="openingLogDir" :disabled="isPackaging" @click="openLogDir">
          打开日志目录
        </n-button>
      </div>

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
const emit = defineEmits<{
  'update:show': [value: boolean]
  // 代码非最新时点「去更新」→ 由父组件打开检查更新窗口
  'open-update': []
}>()

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
const openingLogDir = ref(false)
const isPackaging = ref(false)
const starting = ref(false)
const progress = ref<{ running: boolean; phase: string; percent: number; message: string; error: string }>({
  running: false, phase: '', percent: 0, message: '', error: '',
})

let pollTimer: ReturnType<typeof setInterval> | null = null

/**
 * 代码版本检测状态：
 * - checking 检测中
 * - latest   已是最新
 * - outdated 本地提交与更新源分支不一致（需先更新）
 * - unknown  更新源不可达/请求异常（不打断反馈流程）
 */
const codeCheckState = ref<'idle' | 'checking' | 'latest' | 'outdated' | 'unknown'>('idle')
const codeCheckMessage = ref('')

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
    } else if (!data?.cancelled) {
      // 用户取消（cancelled=true）静默；真实失败必须提示，避免"点了没反应"
      message.warning(data?.message || '选择文件夹失败')
    }
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '选择文件夹失败')
  } finally {
    browsing.value = false
  }
}

/** 在系统文件管理器中打开当前配置对应的本地日志目录 */
async function openLogDir() {
  if (openingLogDir.value) return
  openingLogDir.value = true
  try {
    const res = await utilsApi.openLogDir(props.configId || '')
    const data = res.data
    if (data?.ok) {
      message.success(`已打开日志目录：${data.path || ''}`)
    } else {
      message.error(data?.message || '打开日志目录失败')
    }
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '打开日志目录失败')
  } finally {
    openingLogDir.value = false
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
  openingLogDir.value = false
  codeCheckState.value = 'idle'
  codeCheckMessage.value = ''
  progress.value = { running: false, phase: '', percent: 0, message: '', error: '' }
}

function close() {
  emit('update:show', false)
}

/** 「去更新」：交给父组件打开检查更新窗口（更新流程由 UpdateDialog 承担） */
function openUpdate() {
  emit('open-update')
}

/**
 * 打开反馈界面时自动检测当前代码是否为最新（后端对比本地 version.json 与更新源分支）。
 * 非最新时提示用户先尝试更新，更新后问题仍未解决再反馈；检测失败只轻提示，不阻塞反馈流程。
 */
async function checkCodeVersion() {
  codeCheckState.value = 'checking'
  codeCheckMessage.value = ''
  try {
    const res = await utilsApi.checkUpdate()
    const data = res.data
    if (!data?.ok) {
      codeCheckState.value = 'unknown'
      codeCheckMessage.value = data?.message || '更新源不可达'
      return
    }
    if (data.update_type && data.update_type !== 'none') {
      codeCheckState.value = 'outdated'
      const local = data.local_version
        || data.current_commit?.short_sha
        || (data.current_sha ? String(data.current_sha).slice(0, 7) : '')
      const remote = data.update_type === 'full'
        ? (data.full?.tag || data.full?.version || '')
        : (data.latest_sha ? String(data.latest_sha).slice(0, 7) : '')
      codeCheckMessage.value =
        `本地版本 ${local || '未知'}，更新源最新 ${remote || '未知'}${data.latest_message ? `（${data.latest_message}）` : ''}`
      return
    }
    codeCheckState.value = 'latest'
  } catch (e: any) {
    // 外部更新源不可控：检测失败降级为「无法检测」，不影响用户生成反馈包
    codeCheckState.value = 'unknown'
    codeCheckMessage.value = e?.response?.data?.detail || '网络请求失败'
  }
}

watch(() => props.show, (v) => {
  if (v) {
    loadOptions()
    // 打开反馈界面即检测代码是否最新（含从启动引导弹窗跳转过来的场景）
    checkCodeVersion()
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
.log-dir-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  padding: 8px 10px;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 6px;
}
.center-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 0;
}
.progress-card { margin-bottom: 12px; }
/* 代码版本检测提示条 */
.code-check-bar { margin-bottom: 12px; }
.code-check-msg {
  font-size: 13px;
  line-height: 1.7;
  word-break: break-all;
}
.code-check-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
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