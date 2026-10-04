/**
 * 调度器 API（`/api/scheduler/*`）
 *
 * 阶段 5：从 `api/client.ts` 拆出；`client.ts` 作为 barrel 再导出 `schedulerApi`，
 * 既有 import 路径不变。
 */
import client from '../http'

export const schedulerApi = {
  start: (configId: string) => client.post(`/scheduler/start/${configId}`),
  stop: (configId: string) => client.post(`/scheduler/stop/${configId}`),
  status: (configId: string) => client.get(`/scheduler/status/${configId}`),
  getTasks: (configId: string) => client.get(`/scheduler/tasks/${configId}`),
  // 启动前快速预检（串口/截图路径），返回 { ok, errors: string[], warnings: string[] }
  precheck: (configId: string) => client.post(`/scheduler/precheck/${configId}`),
  // force=true：用户已在二次确认弹窗中选择「忽略窗口强制执行」（默认受任务排期窗口约束）
  executeTask: (configId: string, taskName: string, force = false) =>
    client.post(
      `/scheduler/tasks/${configId}/${taskName}/execute${force ? "?force=true" : ""}`,
    ),
  // 「是否启用」的单一写端点（后端保证：有调度器实例→同步队列/快照并写配置；
  // 无实例→只写配置，不创建实例）
  toggleActivation: (configId: string, taskName: string, state: boolean) =>
    client.put(`/scheduler/tasks/${configId}/${taskName}/activation?state=${state}`),
}
