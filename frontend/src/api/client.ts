import axios from 'axios'
import type { AxiosInstance } from 'axios'

const API_BASE = '/api'

const client: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 响应拦截器
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
  create: (data: any) => client.post('/configs', data),
  update: (id: string, data: any) => client.put(`/configs/${id}`, data),
}

// ===== 场景管理 API =====
export const scenesApi = {
  list: () => client.get('/scenes'),
  get: (id: string) => client.get(`/scenes/${id}`),
  create: (data: any) => client.post('/scenes', data),
  update: (id: string, data: any) => client.put(`/scenes/${id}`, data),
  delete: (id: string) => client.delete(`/scenes/${id}`),
  getImage: (id: string) => client.get(`/scenes/${id}/image`, { responseType: 'blob' }),
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
  list: () => client.get('/tasks'),
  get: (name: string) => client.get(`/tasks/${name}`),
  execute: (name: string) => client.post(`/tasks/${name}/execute`),
  toggleActivation: (name: string, enabled: boolean) =>
    client.put(`/tasks/${name}/activation`, { enabled }),
}

// ===== 调度器 API =====
export const schedulerApi = {
  start: () => client.post('/scheduler/start'),
  stop: () => client.post('/scheduler/stop'),
  status: () => client.get('/scheduler/status'),
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

// ===== 健康检查 =====
export const healthApi = {
  check: () => client.get('/health'),
}