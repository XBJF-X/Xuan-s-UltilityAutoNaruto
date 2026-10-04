/**
 * 配置管理 API（`/api/configs/*`）
 *
 * 阶段 5：端点对象从 `api/client.ts` 拆到 `api/endpoints/`，`client.ts` 继续以 barrel
 * 形式再导出这些名字，因此所有既有 `import { configApi } from '@/api/client'` 无需改动。
 */
import client from '../http'

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
  // 说明：原「批量更新任务优先级」接口已删除——前端方法 / 后端路由 / ConfigService
  // 方法三层均无调用方，实际优先级由每个任务的「基础优先级」决定
  // （ConfigDetail.vue 保存时逐个写入）。
  updateTaskOrder: (id: string, orderedTaskNames: string[]) =>
    client.put(`/configs/${id}/task-order`, { tasks: orderedTaskNames }),
  duplicate: (id: string) => client.post(`/configs/${id}/duplicate`),
  getDefaultTasks: () => client.get('/configs/default-tasks'),
  delete: (id: string) => client.delete(`/configs/${id}`),
  rename: (id: string, newUsername: string) =>
    client.put(`/configs/${id}/rename`, { key: '用户名', value: newUsername }),
}

/** 任务管理 API（`/api/tasks/*`） */
export const tasksApi = {
  getSchema: () => client.get('/tasks/schema'),
}
