/**
 * 统一 HTTP 出口（阶段 2：通信契约与错误处理）
 *
 * 背景：改前 `client.ts` 只挂了一个 `console.error` 拦截器 —— 非 2xx、超时、网络错误、
 * 取消全部以原始 axios 错误向上冒泡，各调用点自行 `e?.response?.data?.detail` 取值，
 * 全仓 0 处 AbortController（切配置时在途请求无法取消）。
 *
 * 现在：
 * - 唯一 axios 实例（baseURL / timeout / 拦截器都在这里）；
 * - 所有失败归一为 `ApiError`（kind: http / timeout / network / canceled / unknown）；
 * - **向后兼容**：ApiError 保留 `response` 与 `message`，既有
 *   `e?.response?.data?.detail`、`e.message` 取值方式继续可用，无需一次性改 50+ 处；
 * - `request<T>()` 供新代码使用：直接拿到解包后的 payload；
 * - 可取消：每个请求自动带 AbortController 并登记，`abortAllInFlight()` 可一次性取消
 *   （切配置/离开页面时调用），`ApiError.isCanceled` 用于区分"用户主动取消"与真失败。
 */
import axios from 'axios'
import type { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios'

const API_BASE = '/api'

/** 失败类别：调用方可据此决定"提示 / 静默 / 重试" */
export type ApiErrorKind = 'http' | 'timeout' | 'network' | 'canceled' | 'unknown'

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number
  /** 后端返回的 detail（字符串或结构体） */
  readonly detail?: unknown
  /** 原始 axios 响应：保留以兼容既有 `e.response?.data?.detail` 写法 */
  readonly response?: AxiosError['response']
  /** 是否是本模块归一化后的错误（用于类型判断） */
  readonly isApiError = true

  constructor(
    kind: ApiErrorKind,
    message: string,
    opts: { status?: number; detail?: unknown; response?: AxiosError['response'] } = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = opts.status
    this.detail = opts.detail
    this.response = opts.response
  }

  get isCanceled(): boolean {
    return this.kind === 'canceled'
  }
}

export function isApiError(e: unknown): e is ApiError {
  return !!e && typeof e === 'object' && (e as ApiError).isApiError === true
}

/** 把任意异常归一为 ApiError（保留 response/message 兼容既有取值方式） */
export function normalizeError(error: unknown): ApiError {
  if (isApiError(error)) return error as ApiError
  const axiosError = error as AxiosError
  const response = axiosError?.response
  const detail = (response?.data as any)?.detail
  const code = (axiosError as any)?.code as string | undefined
  const status = response?.status

  if (axios.isCancel(error) || code === 'ERR_CANCELED') {
    return new ApiError('canceled', '请求已取消', { status, detail, response })
  }
  if (code === 'ECONNABORTED' || code === 'ETIMEDOUT') {
    return new ApiError('timeout', '请求超时，请稍后重试', { status, detail, response })
  }
  if (!response) {
    return new ApiError('network', '无法连接后端服务，请确认程序仍在运行', { detail, response })
  }
  const message = typeof detail === 'string' && detail
    ? detail
    : `请求失败（HTTP ${status}）`
  return new ApiError('http', message, { status, detail, response })
}

/** 面向用户的一行错误文案（取消返回空串，便于调用方静默跳过） */
export function errorMessage(error: unknown, fallback = '请求失败'): string {
  const err = normalizeError(error)
  if (err.kind === 'canceled') return ''
  if (typeof err.detail === 'string' && err.detail) return err.detail
  return err.message || fallback
}

export const client: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ---- 在途请求登记（支持一次性取消） ----
const _inflight = new Set<AbortController>()

export function abortAllInFlight(reason = 'aborted'): void {
  for (const controller of _inflight) {
    try {
      controller.abort(reason)
    } catch (e) {
      console.warn('[api] abort 失败:', e)
    }
  }
  _inflight.clear()
}

export function inFlightCount(): number {
  return _inflight.size
}

client.interceptors.request.use((config) => {
  // 调用方自带 signal 时尊重之，不重复登记
  if (!config.signal) {
    const controller = new AbortController()
    ;(config as any).__ownAbort = controller
    _inflight.add(controller)
    config.signal = controller.signal
  }
  return config
})

function releaseController(config?: AxiosRequestConfig): void {
  const controller = (config as any)?.__ownAbort as AbortController | undefined
  if (controller) _inflight.delete(controller)
}

client.interceptors.response.use(
  (response) => {
    releaseController(response.config)
    return response
  },
  (error) => {
    releaseController(error?.config)
    const normalized = normalizeError(error)
    if (!normalized.isCanceled) {
      // 统一留痕（提示由调用方决定，避免"底层弹一次、上层再弹一次"）
      console.error(`[api] ${normalized.kind} ${normalized.status ?? ''}`.trim(), normalized.detail ?? normalized.message)
    }
    return Promise.reject(normalized)
  },
)

/** 统一请求出口：返回**解包后的 payload**（新代码用；旧 API 对象继续返回 AxiosResponse） */
export async function request<T = any>(config: AxiosRequestConfig): Promise<T> {
  const response = await client.request<T>(config)
  return response.data
}

/** 兼容包装：返回 AxiosResponse（`res.data` 用法不变） */
export function requestRaw<T = any>(config: AxiosRequestConfig) {
  return client.request<T>(config)
}

export default client
