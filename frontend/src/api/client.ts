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
  create: (username: string) => client.post('/configs', { username }),
  updateSetting: (id: string, key: string, value: any) =>
    client.put(`/configs/${id}/setting`, { key, value }),
  updateTask: (id: string, taskName: string, key: string, value: any) =>
    client.put(`/configs/${id}/task/${taskName}`, { key, value }),
  updateTaskParam: (id: string, taskName: string, paramName: string, value: any) =>
    client.put(`/configs/${id}/task/${taskName}/param/${paramName}`, { key: paramName, value }),
  updateTaskPriorities: (id: string, orderedTaskNames: string[]) =>
    client.put(`/configs/${id}/task-priorities`, { tasks: orderedTaskNames }),
  getDefaultTasks: () => client.get('/configs/default-tasks'),
  delete: (id: string) => client.delete(`/configs/${id}`),
  rename: (id: string, newUsername: string) =>
    client.put(`/configs/${id}/rename`, { key: '用户名', value: newUsername }),
}

// ===== 场景管理 API =====
export const scenesApi = {
  list: () => client.get('/scenes'),
  get: (id: string) => client.get(`/scenes/${id}`),
  create: (data: any) => client.post('/scenes', data),
  update: (id: string, data: any) => client.put(`/scenes/${id}`, data),
  delete: (id: string) => client.delete(`/scenes/${id}`),
  getImage: (id: string) => client.get(`/scenes/${id}/image`, { responseType: 'blob' }),
  addEdge: (source: string, target: string) => client.post('/scenes/edges', { source, target }),
  deleteEdge: (source: string, target: string) =>
    client.delete('/scenes/edges', { data: { source, target } }),
}

// ===== 元素管理 API =====
export const elementsApi = {
  list: () => client.get('/elements'),
  create: (formData: FormData) => client.post('/elements', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getImage: (id: string, type: 'bgra' | 'gray' | 'mask' = 'bgra') =>
    client.get(`/elements/${id}/image?type=${type}`, { responseType: 'blob' }),
  update: (id: string, data: any) => client.put(`/elements/${id}`, data),
  delete: (id: string) => client.delete(`/elements/${id}`),
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

// ===== 场景识别 API =====
export const recognizeApi = {
  recognize: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ===== 设备 API =====
export const deviceApi = {
  // 获取模拟器截图（用于键位配置），返回 { image: 'data:image/png;base64,...' }
  screenshot: (configId: string) => client.get(`/device/${configId}/screenshot`),
  // 获取 ADB 设备串口列表，返回 { serials: string[] }
  serialList: (configId: string) => client.get(`/device/${configId}/serial-list`),
  // 重启 ADB 服务并重新枚举设备，返回 { ok: boolean, serials: string[] }
  restartAdb: (configId: string) => client.post(`/device/${configId}/adb-restart`),
}

// ===== 健康检查 =====
export const healthApi = {
  check: () => client.get('/health'),
}
