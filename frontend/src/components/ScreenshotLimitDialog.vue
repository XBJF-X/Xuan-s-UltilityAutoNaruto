<template>
  <n-modal
    :show="current !== null"
    preset="card"
    title="截图数量已达上限"
    style="width: min(560px, calc(100vw - 48px))"
    :mask-closable="false"
    :closable="false"
    :close-on-esc="false"
  >
    <div v-if="current" class="limit-body">
      <n-alert type="warning" :bordered="false" style="margin-bottom: 12px">
        本次运行已自动保存 <b>{{ current.run_count }}</b> 张截图，已达到「每日截图上限」（<b>{{ current.limit }}</b> 张）。
      </n-alert>
      <div class="limit-lines">
        <div class="limit-line">
          <span class="limit-label">配置</span>
          <span class="limit-value">{{ configLabel }}</span>
        </div>
        <div class="limit-line">
          <span class="limit-label">今日自动截图</span>
          <span class="limit-value">{{ current.today_count }} / {{ current.limit }} 张</span>
        </div>
      </div>
      <n-text depth="3" style="font-size: 12px; line-height: 1.7">
        继续运行会持续写入截图并删除更早的截图，占用不必要的磁盘读写。
        请点击主界面<b>日志面板右上角</b>的「<b>截图</b>」开关将其关闭
        （关闭后仍需记录异常时，错误/超时/卡死会自动截图，不受该开关影响）。
      </n-text>
    </div>

    <template #footer>
      <div class="limit-footer">
        <n-text v-if="queue.length > 0" depth="3" style="font-size: 12px">
          另有 {{ queue.length }} 条配置超限提醒待查看
        </n-text>
        <n-space align="center">
          <n-button :disabled="!canDisable" :loading="disabling" @click="disableScreenshot">
            {{ canDisable ? '一键关闭该配置的截图开关' : '该配置截图开关已关闭' }}
          </n-button>
          <n-button type="primary" @click="dismiss">我知道了</n-button>
        </n-space>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
/**
 * 截图超限提醒弹窗（每日截图上限，R3/R4）
 *
 * - **只能由用户手动关闭**：不设右上角关闭叉、遮罩不可点、Esc 不生效、无倒计时，
 *   唯一出口是底部按钮（`我知道了` 或 `一键关闭该配置的截图开关`）。
 * - 每个配置每次运行各弹一次：多条提醒依次展示（队首一条 + “另有 N 条待查看”）。
 * - 一键关闭走既有配置接口 `保存截图 = 0`；由于 `SchedulerService` 与 `ConfigService`
 *   共用同一个 `Config` 实例，关闭后运行中的调度器会立刻停止后续自动截图。
 */
import { computed, ref, watch } from 'vue'
import { NAlert, NButton, NModal, NSpace, NText, useMessage } from 'naive-ui'
import { configApi } from '@/api/client'
// 载荷类型与订阅逻辑同源（见 composables/useScreenshotLimitAlerts.ts）
import type { ScreenshotLimitAlert } from '@/composables/useScreenshotLimitAlerts'

export type { ScreenshotLimitAlert }

const props = withDefaults(defineProps<{
  /** 待展示的提醒队列（多配置超限时依次展示） */
  alerts?: ScreenshotLimitAlert[]
}>(), {
  alerts: () => [],
})

const emit = defineEmits<{
  /** 消费掉队首提醒（由父组件从队列移除） */
  consume: [configId: string]
}>()

const message = useMessage()

/** 当前正在展示的提醒（队首） */
const current = computed<ScreenshotLimitAlert | null>(() => {
  const queue = props.alerts || []
  return queue.length > 0 ? queue[0] : null
})
/** 剩余待展示条数（不含当前） */
const queue = computed(() => (props.alerts || []).slice(1))

const configLabel = computed(() => {
  const c = current.value
  if (!c) return ''
  return c.username ? `${c.config_id}（${c.username}）` : c.config_id
})

// 该配置当前「保存截图」开关状态；null = 未知（按可关闭处理）
const saveEnabled = ref<boolean | null>(null)
const disabling = ref(false)
const canDisable = computed(() => saveEnabled.value !== false)

/** 切换提醒时重新读取该配置的截图开关状态（避免显示过期的“已关闭/未关闭”） */
async function loadSaveEnabled() {
  const c = current.value
  saveEnabled.value = null
  if (!c) return
  try {
    const res = await configApi.get(c.config_id)
    const v = res.data?.setting_dics?.['保存截图']
    saveEnabled.value = !(v === 0 || v === false)
  } catch {
    // 读取失败按“未关闭”处理：允许用户点一键关闭（比禁用按钮更有帮助）
    saveEnabled.value = null
  }
}

watch(() => current.value?.config_id, () => { loadSaveEnabled() }, { immediate: true })

/**
 * 一键关闭该配置的截图开关（`保存截图 = 0`）。
 * 失败只提示，不阻断弹窗关闭（用户仍可点「我知道了」）。
 */
async function disableScreenshot() {
  const c = current.value
  if (!c || !canDisable.value) return
  disabling.value = true
  try {
    await configApi.updateSetting(c.config_id, '保存截图', 0)
    saveEnabled.value = false
    message.success('已关闭该配置的截图开关（错误/超时截图不受影响）')
  } catch (e: any) {
    message.error(`关闭截图开关失败：${e?.response?.data?.detail || e?.message || e}`)
  } finally {
    disabling.value = false
  }
}

/** 用户确认：消费队首提醒（队列还有则继续展示下一条） */
function dismiss() {
  const c = current.value
  if (!c) return
  emit('consume', c.config_id)
}
</script>

<style scoped>
.limit-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.limit-lines {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}
.limit-line {
  display: flex;
  gap: 10px;
}
.limit-label {
  color: #8a8a8a;
  min-width: 84px;
}
.limit-value {
  color: #333;
  font-weight: 600;
}
.limit-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
</style>
