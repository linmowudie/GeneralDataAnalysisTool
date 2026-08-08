import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';

/** 结构化 API 错误 */
export class ApiError extends Error {
  code: number;
  detail?: unknown;

  constructor(message: string, code: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.detail = detail;
  }
}

export interface UploadOptions {
  onProgress?: (percent: number) => void;
  signal?: AbortSignal;
}

export interface RequestOptions {
  signal?: AbortSignal;
}

/**
 * 基础API服务类
 * 封装HTTP请求逻辑，提供统一的请求处理
 */
export class ApiService {
  private axiosInstance: AxiosInstance;
  private sessionId: string | null = null;
  private static readonly MAX_RETRIES = 1;

  constructor(baseURL: string = '') {
    this.axiosInstance = axios.create({
      baseURL: baseURL || import.meta.env?.VITE_API_BASE_URL || '',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器：注入 session_id
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.sessionId) {
          config.headers.set('X-Session-Id', this.sessionId);
        }
        return config;
      },
      (error: AxiosError) => Promise.reject(error),
    );

    // 响应拦截器：按状态码分类处理
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        const status = error.response?.status;
        const detail = (error.response?.data as Record<string, unknown>)?.detail;
        const message = (detail as string) || error.message || '请求失败';

        if (status === 401) {
          console.error('API 401: 未授权，会话可能已过期');
        } else if (status === 403) {
          console.error('API 403: 禁止访问');
        } else if (status === 404) {
          console.error(`API 404: 资源不存在 - ${error.config?.url}`);
        } else if (status && status >= 500) {
          console.error(`API ${status}: 服务器错误`);
        } else if (!status) {
          console.error('API 网络错误:', message);
        }

        return Promise.reject(new ApiError(message, status ?? 0, detail));
      },
    );
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * GET 请求（支持自动重试 1 次 + 请求取消）
   */
  async get<T>(url: string, params?: Record<string, unknown>, options?: RequestOptions): Promise<T> {
    const execute = (attempt: number): Promise<T> =>
      this.axiosInstance
        .get<T>(url, { params, signal: options?.signal })
        .then((res) => res.data)
        .catch((err: AxiosError) => {
          // 仅对网络错误（无响应）重试，HTTP 错误不重试
          if (attempt < ApiService.MAX_RETRIES && !err.response && !options?.signal?.aborted) {
            return execute(attempt + 1);
          }
          throw err;
        });
    return execute(0);
  }

  /**
   * POST 请求（支持请求取消，不自动重试）
   */
  async post<T>(url: string, data?: Record<string, unknown>, options?: RequestOptions): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data, { signal: options?.signal });
    return response.data;
  }

  /**
   * 文件上传请求（支持进度回调 + 请求取消）
   */
  async upload<T>(url: string, formData: FormData, uploadOpts?: UploadOptions): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      signal: uploadOpts?.signal,
      onUploadProgress: (event) => {
        if (uploadOpts?.onProgress && event.total) {
          uploadOpts.onProgress(Math.round((event.loaded * 100) / event.total));
        }
      },
    });
    return response.data;
  }
}

// 创建全局API服务实例
export const apiService = new ApiService();
