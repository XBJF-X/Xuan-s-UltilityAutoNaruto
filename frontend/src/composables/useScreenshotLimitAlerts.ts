/**
 * 截图超限提醒 composable（每日截图上限，R3/R4）
 *
 * 后端在「本次运行截图数超过每日上限」时广播一次 v1 事件 `screenshot.limit`
 * （每个配置、每次运行各自一次，见 `backend/services/scheduler/screenshot_guard.py`）。
 * 这里负责订阅、入队与消费；展示交给 `ScreenshotLimitDialog.vue`
 * （弹窗不可自动消失，只由用户点按钮关闭）。
 *
 * 与其它 composable 同一约定：WS 订阅与退订都在本文件内完成，Layout.vue 只做编排
 * （`verify_layout_composables.py` 会断言 Layout 内不再出现 `useWebSocket(`）。
 */
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useWebSocket } from '@/api/ws'

/** 后端 `screenshot.limit` 事件载荷（`config_id` 由后端补在顶层与 payload 内） */
export interface ScreenshotLimitAlert {
  config_id: string
  username?: string
  limit: number
  run_count: number
  today_count: number
}

export function useScreenshotLimitAlerts() {
  const { on: onWsMessage } = useWebSocket()

  /** 待展示的提醒队列（多配置超限时依次展示，队首为当前弹窗） */
  const screenshotAlerts = ref<ScreenshotLimitAlert[]>([])
  let stopListener: (() => void) | null = null

  /** 用户确认某配置的提醒 → 出队（队列还有则继续展示下一条） */
  function consumeScreenshotAlert(configId: string) {
    screenshotAlerts.value = screenshotAlerts.value.filter((a) => a.config_id !== configId)
  }

  /** `screenshot.limit` 事件处理：同一配置已待展示时不重复入队 */
  function onScreenshotLimit(msg: any) {
    const data = msg?.data || {}
    const configId = String(msg?.config_id || data.config_id || '')
    if (!configId) return
    if (screenshotAlerts.value.some((a) => a.config_id === configId)) return
    screenshotAlerts.value = [...screenshotAlerts.value, {
      config_id: configId,
      username: data.username || '',
      limit: Number(data.limit) || 0,
      run_count: Number(data.run_count) || 0,
      today_count: Number(data.today_count) || 0,
    }]
  }

  onMounted(() => {
    stopListener = onWsMessage('screenshot_limit', onScreenshotLimit)
  })

  onBeforeUnmount(() => {
    stopListener?.()
    stopListener = null
  })

  return {
    screenshotAlerts,
    consumeScreenshotAlert,
    onScreenshotLimit,
  }
}
