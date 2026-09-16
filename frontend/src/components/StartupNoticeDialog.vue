<template>
  <n-modal
    v-model:show="showModel"
    preset="card"
    title="使用前提示"
    style="width: min(620px, calc(100vw - 48px))"
    :mask-closable="false"
    :closable="canClose"
  >
    <div class="notice-body">
      <n-text>
        如果任务执行出现异常，请第一时间打开日志面板右上角的截图开关，完整记录下异常情况后，
        点击顶部栏右上角的文件夹图标，按照指引检查代码是否为最新，选择日期和对应的任务后生成反馈包，
        将反馈包发送给开发者即可。
      </n-text>
      <div class="notice-steps">
        <div class="step-item">1. 打开日志面板右上角的「截图」开关，完整记录异常过程</div>
        <div class="step-item">2. 点击顶部栏右上角的文件夹图标（反馈）</div>
        <div class="step-item">3. 按指引确认代码是否为最新，选择日期与出现问题的任务</div>
        <div class="step-item">4. 生成反馈包并发送给开发者</div>
      </div>
    </div>

    <template #footer>
      <div class="notice-footer">
        <n-checkbox v-model:checked="dontRemind">不再提示</n-checkbox>
        <n-space align="center">
          <n-text v-if="countdown > 0" depth="3" style="font-size: 12px">
            请阅读提示，{{ countdown }}s 后可操作
          </n-text>
          <n-button :disabled="countdown > 0 || saving" @click="onGoFeedback">跳转反馈界面</n-button>
          <n-button type="primary" :disabled="countdown > 0 || saving" :loading="saving" @click="onKnown">知道了</n-button>
        </n-space>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { NButton, NCheckbox, NModal, NSpace, NText, useMessage } from 'naive-ui'
import { settingsApi } from '@/api/client'

const props = defineProps<{
  show: boolean
}>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  'go-feedback': []
}>()

const showModel = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const message = useMessage()

/** 倒计时秒数：未结束时窗口不可关闭（无关闭叉、遮罩不可点、两个按钮禁用） */
const COUNTDOWN_SECONDS = 10
const countdown = ref(COUNTDOWN_SECONDS)
const dontRemind = ref(false)  // 默认不勾选
const saving = ref(false)

let timer: ReturnType<typeof setInterval> | null = null

const canClose = computed(() => countdown.value <= 0)

function stopCountdown() {
  if (timer) { clearInterval(timer); timer = null }
}

function startCountdown() {
  stopCountdown()
  countdown.value = COUNTDOWN_SECONDS
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) stopCountdown()
  }, 1000)
}

/**
 * 勾选「不再提示」时写入全局设置 [助手设置] 启动提示 = False，
 * 下次启动不再弹出（可在「全局设置 → 助手设置」改回 True 恢复提示）。
 * 写入失败只提示不阻断关闭流程。
 */
async function persistDontRemind() {
  if (!dontRemind.value) return
  saving.value = true
  try {
    await settingsApi.set('助手设置', '启动提示', 'False')
  } catch (e: any) {
    message.error(`保存「不再提示」失败：${e?.response?.data?.detail || e?.message || e}`)
  } finally {
    saving.value = false
  }
}

async function onKnown() {
  if (!canClose.value) return
  await persistDontRemind()
  emit('update:show', false)
}

async function onGoFeedback() {
  if (!canClose.value) return
  await persistDontRemind()
  emit('update:show', false)
  emit('go-feedback')
}

watch(() => props.show, (v) => {
  if (v) {
    dontRemind.value = false
    startCountdown()
  } else {
    stopCountdown()
  }
})

onBeforeUnmount(stopCountdown)
</script>

<style scoped>
.notice-body {
  font-size: 14px;
  line-height: 1.8;
}
.notice-steps {
  margin-top: 12px;
  padding: 10px 12px;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 6px;
}
.step-item {
  font-size: 13px;
  line-height: 1.9;
  color: #555;
}
.notice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
</style>
