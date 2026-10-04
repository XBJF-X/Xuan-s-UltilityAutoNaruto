/**
 * HTTP 客户端与端点集合的**统一入口**（barrel）
 *
 * 阶段 5 结构整理：端点对象按职责拆到 `api/endpoints/`：
 * - `endpoints/configs.ts`   `configApi` / `tasksApi`
 * - `endpoints/scheduler.ts` `schedulerApi`
 * - `endpoints/system.ts`    `settingsApi` / `deviceApi` / `utilsApi` / `healthApi`
 *
 * 本文件继续再导出**全部原有名字**，因此既有 `import { configApi, schedulerApi } from '@/api/client'`
 * 等调用点（含测试里的 `mock.patch("backend.api.utils.requests.get")` 无关，前端 TS 测试不受影响）
 * 无需任何改动；新代码也可以直接从 `@/api/endpoints/<name>` 引入更精确的模块。
 */
import client from './http'

export default client
export { client, ApiError, errorMessage, isApiError, normalizeError, request, requestRaw, abortAllInFlight, inFlightCount } from './http'
export type { ApiErrorKind } from './http'

export { configApi, tasksApi } from './endpoints/configs'
export { schedulerApi } from './endpoints/scheduler'
export { settingsApi, deviceApi, utilsApi, healthApi } from './endpoints/system'
