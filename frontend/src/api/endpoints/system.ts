/**
 * 设备 / 全局设置 / 工具 / 健康检查 API
 *
 * 阶段 5：从 `api/client.ts` 拆出；`client.ts` 作为 barrel 再导出，既有 import 不变。
 */
import client from '../http'

// ===== 全局设置 API =====
export const settingsApi = {
  getAll: () => client.get('/settings'),
  get: (section: string, key: string) => client.get(`/settings/${section}/${key}`),
  set: (section: string, key: string, value: string) =>
    client.put('/settings', { section, key, value }),
}

// ===== 设备 API =====
export const deviceApi = {
  // 检测模拟器运行环境（路径文件/实例/分辨率16:9/后台保活）
  checkEnvironment: (configId: string) =>
    client.post(`/device/${configId}/check-environment`),
  // 获取模拟器截图（用于键位配置），返回 { image: 'data:image/png;base64,...' }
  screenshot: (configId: string) => client.get(`/device/${configId}/screenshot`),
  // 截图并保存到 log/<用户名>/<日期>/screenshot/，返回 { ok, path }
  saveScreenshot: (configId: string) => client.post(`/device/${configId}/save-screenshot`),
  // 获取 ADB 设备串口列表，返回 { serials: string[] }
  serialList: (configId: string) => client.get(`/device/${configId}/serial-list`),
  // 重启 ADB 服务并重新枚举设备，返回 { ok: boolean, serials: string[] }
  restartAdb: (configId: string) => client.post(`/device/${configId}/adb-restart`),
  // 清理设备端残留触点（连点中途被杀进程导致 evdev slot 卡在按下态），
  // 返回 { ok, serial, had_stale, before, after }，无需重启模拟器
  cleanStaleContacts: (configId: string) =>
    client.post(`/device/${configId}/clean-stale-contacts`),
}

// ===== 工具 API =====
export const utilsApi = {
  // 读取历史日志文件，供刷新/重连后恢复展示（config_id 为空或 '__global__' 表示程序全局日志）
  logHistory: (configId: string, limit = 500) =>
    client.get('/utils/log-history', { params: { config_id: configId, limit } }),
  // 在系统文件管理器中打开本地日志目录，返回 { ok, path }（config_id 为空或 __global__ 打开 log/ 根目录）
  openLogDir: (configId: string) =>
    client.get('/utils/open-log-dir', { params: { config_id: configId } }),
  // 本地客户端版本：读取根目录 _version.py（不访问外部更新源）
  localVersion: () => client.get('/utils/version'),
  // 检查更新：对比本地 version.json 与 GitHub v17 分支，返回提交历史
  checkUpdate: () => client.get('/utils/check-update'),
  // 依赖健康检查：版本是否满足 MIN_RELEASE_TAG + 关键模块是否缺失
  checkDependency: () => client.get('/utils/dependency-check'),
  // 应用更新（后台执行，进度通过 updateStatus 轮询）
  // sha 可选：指定后拉取该提交（当前已是最新也允许），不传则更新到分支最新提交
  applyUpdate: (sha?: string) => client.post('/utils/apply-update', sha ? { sha } : {}),
  // 应用大更新：下载最新 GitHub Release 安装包并自动重启安装（进度通过 updateStatus 轮询）
  applyReleaseUpdate: () => client.post('/utils/apply-release-update'),
  // 查询更新任务进度
  updateStatus: () => client.get('/utils/update-status'),
  // 反馈打包：根据当前配置日志目录生成选择项（日期、任务）
  // 传入 date 时可进一步返回该日期下的任务列表
  feedbackOptions: (configId: string, date?: string) =>
    client.get('/utils/feedback/options', { params: { config_id: configId, date: date || '' } }),
  // 启动反馈打包（后台执行）
  feedbackPackage: (data: { config_id: string; date: string; task_names: string[]; save_path: string }) =>
    client.post('/utils/feedback/package', data),
  // 查询反馈打包进度
  feedbackStatus: () => client.get('/utils/feedback/package-status'),
  // 弹出 Windows 文件夹选择对话框，返回 { ok: boolean, path?: string }
  browseFolder: (title: string) => client.post('/utils/browse-folder', { title }),
  // 校验模拟器安装路径下关键文件存在性（仅存在性，不做实例/分辨率检测）
  // mode: 'mumu' | 'ld'；返回 { ok, dll_ok, manager_ok, missing: string[] }
  validateInstallPath: (mode: 'mumu' | 'ld', path: string) =>
    client.post('/utils/install-path', { mode, path }),
}

// ===== 健康检查 =====
export const healthApi = {
  check: () => client.get('/health'),
}
