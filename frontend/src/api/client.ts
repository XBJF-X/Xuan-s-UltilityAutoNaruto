import axios from 'axios'
import type { AxiosInstance } from 'axios'

const API_BASE = '/api'

const client: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  },
)

export default client

// ===== 配置管理 API =====
export const configApi = {
  list: () => client.get('/configs'),
  get: (id: string) => client.get(`/configs/${id}`),
  create: (username: string, configType = '持久') =>
    client.post('/configs', { username, config_type: configType }),
  updateSetting: (id: string, key: string, value: any) =>
    client.put(`/configs/${id}/setting`, { key, value }),
  updateTask: (id: string, taskName: string, key: string, value: any) =>
    client.put(`/configs/${id}/task/${taskName}`, { key, value }),
  updateTaskParam: (id: string, taskName: string, paramName: string, value: any) =>
    client.put(`/configs/${id}/task/${taskName}/param/${paramName}`, { key: paramName, value }),
  updateTaskPriorities: (id: string, orderedTaskNames: string[]) =>
    client.put(`/configs/${id}/task-priorities`, { tasks: orderedTaskNames }),
  updateTaskOrder: (id: string, orderedTaskNames: string[]) =>
    client.put(`/configs/${id}/task-order`, { tasks: orderedTaskNames }),
  duplicate: (id: string) => client.post(`/configs/${id}/duplicate`),
  getDefaultTasks: () => client.get('/configs/default-tasks'),
  delete: (id: string) => client.delete(`/configs/${id}`),
  rename: (id: string, newUsername: string) =>
    client.put(`/configs/${id}/rename`, { key: '用户名', value: newUsername }),
}

// ===== 任务管理 API =====
export const tasksApi = {
  getSchema: () => client.get('/tasks/schema'),
}

// ===== 调度器 API =====
export const schedulerApi = {
  start: (configId: string) => client.post(`/scheduler/start/${configId}`),
  stop: (configId: string) => client.post(`/scheduler/stop/${configId}`),
  status: (configId: string) => client.get(`/scheduler/status/${configId}`),
  getTasks: (configId: string) => client.get(`/scheduler/tasks/${configId}`),
  // 启动前快速预检（串口/截图路径），返回 { ok, errors: string[], warnings: string[] }
  precheck: (configId: string) => client.post(`/scheduler/precheck/${configId}`),
  executeTask: (configId: string, taskName: string) =>
    client.post(`/scheduler/tasks/${configId}/${taskName}/execute`),
  toggleActivation: (configId: string, taskName: string, state: boolean) =>
    client.put(`/scheduler/tasks/${configId}/${taskName}/activation?state=${state}`),
}

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
}

// ===== 工具 API =====
export const utilsApi = {
  // 读取历史日志文件，供刷新/重连后恢复展示（config_id 为空或 '__global__' 表示程序全局日志）
  logHistory: (configId: string, limit = 500) =>
    client.get('/utils/log-history', { params: { config_id: configId, limit } }),
  // 在系统文件管理器中打开本地日志目录，返回 { ok, path }（config_id 为空或 __global__ 打开 log/ 根目录）
  openLogDir: (configId: string) =>
    client.get('/utils/open-log-dir', { params: { config_id: configId } }),
  // 检查更新：对比本地 version.json 与 GitHub v17 分支，返回提交历史
  checkUpdate: () => client.get('/utils/check-update'),
  // 依赖健康检查：版本是否满足 MIN_RELEASE_TAG + 关键模块是否缺失
  checkDependency: () => client.get('/utils/dependency-check'),
  // 应用更新（后台执行，进度通过 updateStatus 轮询）
  applyUpdate: () => client.post('/utils/apply-update'),
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
