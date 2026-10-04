/**
 * 启动检查 composable（阶段 5：从 Layout.vue 抽出）
 *
 * 负责程序启动时的三个非阻塞检查与两个入口：
 * - `checkStartupNotice()`：使用引导弹窗（读 [助手设置] 启动提示；与更新弹窗错开 1.2s）
 * - `checkDependencyOnStart()`：依赖库/OCR 加速健康检查（不完整时引导前往 Release）
 * - `checkUpdateOnStart()`：按 [助手设置] 自动更新开关决定是否弹更新窗口
 * - `handleScreenshot()` / `openFeedback()`：顶栏与引导弹窗的入口
 *
 * 三者都是"失败只留痕、不打扰用户"的启动期检查（接口异常时静默），
 * 抽出的意义：Layout.vue 只保留 onMounted 里的一次调用，模板靠返回的 dialog 开关驱动。
 */
import { ref } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { utilsApi, settingsApi, deviceApi } from '@/api/client'

export function useStartupChecks() {
  const appStore = useAppStore()
  const message = useMessage()
  const dialog = useDialog()

  const showUpdateDialog = ref(false)
  const showFeedbackDialog = ref(false)
  const showStartupNotice = ref(false)

  /** 使用引导提示：读取全局设置 [助手设置] 启动提示（默认 True） */
  async function checkStartupNotice() {
    try {
      // 与依赖检查/自动更新弹窗错开 1.2s，避免多个弹窗叠加遮挡
      await new Promise(resolve => setTimeout(resolve, 1200))
      if (showUpdateDialog.value) return
      const res = await settingsApi.getAll()
      const flag = res.data?.['助手设置']?.['启动提示']
      // 仅显式 False 时不再提示；键缺失/为空（旧 setting.ini）时仍弹出，避免引导被静默跳过
      if (String(flag ?? '').trim().toLowerCase() === 'false') return
      showStartupNotice.value = true
    } catch (e) {
      // 全局设置接口异常时不打扰用户（启动引导非关键功能），仅留痕
      console.warn('[startup] 读取启动提示失败，跳过引导:', e)
    }
  }

  /** 引导弹窗「跳转反馈界面」：未选择配置时给出指引（反馈需按配置用户名定位日志目录） */
  function handleStartupGoFeedback() {
    if (!appStore.activeConfigId) {
      message.warning('请先在左侧选择或新建一个配置，再生成反馈包')
      return
    }
    showFeedbackDialog.value = true
  }

  /**
   * 启动时依赖健康检查：版本过低或模块缺失时弹窗引导前往 Release 更新，
   * 让用户在依赖库不完整时也能通过界面操作，而不是只能在群里求助。
   * 另外单独检查 OCR GPU(DirectML) 加速：依赖库不含 DML provider 时 OCR 会静默回退
   * CPU 推理（任务执行时 CPU 占用呈尖峰），同样引导用户覆盖安装最新 Release。
   */
  async function checkDependencyOnStart() {
    try {
      const res = await utilsApi.checkDependency()
      const data = res.data
      if (!data) return
      const releaseUrl = data.release_url
        || 'https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto/releases'
      // 仅在依赖库本身无问题时提示 OCR 加速（否则下面的「依赖库不完整」弹窗已包含同一
      // 修复动作——覆盖安装，避免连弹两次）
      if (data.ok && data.ocr_accel?.needs_notice) {
        const pkg = data.ocr_accel.package || '未知'
        const ver = data.ocr_accel.onnxruntime_version || ''
        dialog.warning({
          title: 'OCR 加速不可用',
          content: `${data.ocr_accel.message}\n\n当前 onnxruntime：${pkg} ${ver}`.trim(),
          positiveText: '前往 Release',
          negativeText: '知道了',
          onPositiveClick: () => { window.open(releaseUrl, '_blank') },
        })
      }
      if (data.ok) return
      const msgs: string[] = []
      if (data.deprecated) {
        msgs.push(`当前版本 ${data.local_version} 低于本版本要求的最低版本 ${data.required_tag}，依赖库不完整`)
      }
      if (data.missing_modules?.length) {
        msgs.push(`检测到以下依赖缺失：${data.missing_modules.join('、')}`)
      }
      dialog.warning({
        title: '依赖库不完整',
        content: `${msgs.join('\n')}\n\n为避免任务出现异常，请前往 GitHub Release 页面下载最新安装包更新。`,
        positiveText: '前往 Release',
        negativeText: '稍后再说',
        onPositiveClick: () => {
          window.open(releaseUrl, '_blank')
        },
      })
    } catch (e) {
      // 依赖检查接口异常时静默忽略（不打扰用户），仅留痕
      console.warn('[startup] 依赖检查失败，跳过引导:', e)
    }
  }

  /** 程序启动时自动检查更新：仅当全局设置"自动更新"开启且云端有新版本时弹出更新窗口 */
  async function checkUpdateOnStart() {
    try {
      // 读取全局设置 [助手设置] 段的"自动更新"开关（默认关闭）
      const settingsRes = await settingsApi.getAll()
      const autoUpdate = settingsRes.data?.['助手设置']?.['自动更新']
      if (String(autoUpdate ?? '').trim().toLowerCase() !== 'true') {
        return
      }
      const res = await utilsApi.checkUpdate()
      // 有大更新（正式版/依赖库）或热更新时均弹出更新窗口（update_type: full/hot/none）
      if (res.data?.ok && res.data.update_type && res.data.update_type !== 'none') {
        showUpdateDialog.value = true
      }
    } catch (e) {
      // 网络异常时静默忽略（用户可随时通过顶部按钮手动检查），仅留痕
      console.warn('[startup] 自动检查更新失败，跳过:', e)
    }
  }

  /** 顶栏截图：保存到日志目录（config_id 必填） */
  async function handleScreenshot() {
    if (!appStore.activeConfigId) {
      message.warning('请先选择一个配置')
      return
    }
    try {
      const res = await deviceApi.saveScreenshot(appStore.activeConfigId)
      message.success(`截图已保存：${res.data?.path || ''}`)
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '截图失败')
    }
  }

  /** 顶栏反馈入口 */
  function openFeedback() {
    if (!appStore.activeConfigId) {
      message.warning('请先选择一个配置')
      return
    }
    showFeedbackDialog.value = true
  }

  return {
    showUpdateDialog,
    showFeedbackDialog,
    showStartupNotice,
    checkStartupNotice,
    checkDependencyOnStart,
    checkUpdateOnStart,
    handleStartupGoFeedback,
    handleScreenshot,
    openFeedback,
  }
}
