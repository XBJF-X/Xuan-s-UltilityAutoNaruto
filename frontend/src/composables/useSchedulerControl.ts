/**
 * 调度器控制 composable（阶段 5：从 Layout.vue 抽出）
 *
 * 负责顶栏"启动/停止调度器"按钮与运行状态同步：
 * - `schedulerRunning` / `schedulerStarting` 状态
 * - `toggleScheduler()` / `startScheduler()` / `stopScheduler()`
 * - WS 订阅：`status`（旧后端）与 `scheduler_snapshot`（新协议）两条路径都会同步按钮状态；
 *   快照统一写入 `appStore.applySnapshot`（带 seq 去旧帧，阶段 5 唯一写入口）
 * - `onBeforeUnmount` 自动退订（composable 在 setup 中被调用，注册有效）
 */
import { ref, onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { schedulerApi } from '@/api/client'
import { useWebSocket } from '@/api/ws'

export function useSchedulerControl() {
  const appStore = useAppStore()
  const message = useMessage()

  const schedulerRunning = ref(false)
  const schedulerStarting = ref(false)

  async function toggleScheduler() {
    if (!appStore.activeConfigId) return
    if (schedulerRunning.value) {
      await stopScheduler()
    } else {
      await startScheduler()
    }
  }

  async function startScheduler() {
    if (!appStore.activeConfigId) return
    schedulerStarting.value = true
    try {
      // 启动前快速预检：串口（已配置/格式/占用/在线）与 MuMu/LD 截图路径环境，
      // 避免参数错误时进入耗时的设备连接导致界面长时间无响应
      const pre = await schedulerApi.precheck(appStore.activeConfigId)
      if (pre.data?.errors?.length) {
        message.error(`启动前检查未通过：\n${pre.data.errors.join('\n')}`)
        return
      }
      if (pre.data?.warnings?.length) {
        message.warning(pre.data.warnings.join('\n'))
      }
      await schedulerApi.start(appStore.activeConfigId)
      schedulerRunning.value = true
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '启动失败')
    } finally {
      schedulerStarting.value = false
    }
  }

  async function stopScheduler() {
    if (!appStore.activeConfigId) return
    try {
      await schedulerApi.stop(appStore.activeConfigId)
      schedulerRunning.value = false
    } catch (e: any) {
      // 刻意不上抛/不弹窗（保持抽取前行为）：停止是幂等操作，调度器已停止或预设已跑完
      // 自动停止时后端会返回错误，此时"停止失败"提示反而是噪音。仅在控制台留痕。
      console.warn('[scheduler] 停止请求未成功（可能已停止）:', e?.detail ?? e?.message ?? e)
    }
  }

  // 监听调度器运行状态（含预设任务跑完自动停止），同步启停按钮
  const { onMessage } = useWebSocket()
  const unsubSchedulerStatus = onMessage((msg) => {
    if (msg.type === 'status' && msg.data?.config_id === appStore.activeConfigId) {
      schedulerRunning.value = !!msg.data?.running
    }
    // 调度器完整状态快照：按 config_id 存到 AppStore（Dashboard/PresetEditor 据此零轮询）
    if (msg.type === 'scheduler_snapshot' && msg.config_id) {
      appStore.applySnapshot(msg.config_id, msg.data, { seq: msg.seq, source: 'ws' })
      if (msg.config_id === appStore.activeConfigId) {
        schedulerRunning.value = !!msg.data?.running
      }
    }
  })

  onBeforeUnmount(() => {
    unsubSchedulerStatus()
  })

  return {
    schedulerRunning,
    schedulerStarting,
    toggleScheduler,
    startScheduler,
    stopScheduler,
  }
}
