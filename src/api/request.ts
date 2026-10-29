export const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export class ApiError extends Error {
  constructor(message: string, public status = 0, public data: unknown = null) {
    super(message);
    this.name = 'ApiError';
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : '操作失败，请稍后重试';
}

interface RequestOptions extends RequestInit { anonymous?: boolean }

export async function request<T = unknown>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { anonymous, ...init } = options;
  const token = anonymous ? null : localStorage.getItem('token');
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (init.signal?.aborted) controller.abort();
  init.signal?.addEventListener('abort', abort, { once: true });
  const timeout = window.setTimeout(abort, 15000);
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...init, headers, signal: controller.signal
    });
    const body = await res.json().catch(() => null) as ApiResponse<T> | null;
    if (!res.ok || !body || typeof body.code !== 'number' || body.code < 200 || body.code >= 300) {
      if (res.status === 401 && token && token === localStorage.getItem('token')) {
        window.dispatchEvent(new Event('session-expired'));
      }
      throw new ApiError(body?.message || '服务暂时不可用，请稍后重试', res.status, body?.data);
    }
    return body;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted) throw new ApiError('请求已超时或取消，请重试');
    throw new ApiError('网络连接失败，请稍后重试');
  } finally {
    clearTimeout(timeout);
    init.signal?.removeEventListener('abort', abort);
  }
}
