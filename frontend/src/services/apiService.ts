import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

/**
 * 基础API服务类
 * 封装HTTP请求逻辑，提供统一的请求处理
 */
export class ApiService {
  private axiosInstance: AxiosInstance;
  private sessionId: string | null = null;

  constructor(baseURL: string = '') {
    this.axiosInstance = axios.create({
      baseURL: baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // 可以在这里添加认证token等
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        // 统一错误处理
        const errorMessage = (error.response?.data as any)?.detail || error.message || '请求失败';
        console.error('API请求错误:', errorMessage);
        throw new Error(errorMessage);
      }
    );
  }

  /**
   * 设置会话ID
   * @param sessionId 会话ID
   */
  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  /**
   * 获取当前会话ID
   * @returns 会话ID或null
   */
  getSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * GET请求
   * @param url 请求URL
   * @param params 查询参数
   * @returns Promise<any>
   */
  async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    return this.axiosInstance.get<T>(url, { params }).then(response => response.data);
  }

  /**
   * POST请求
   * @param url 请求URL
   * @param data 请求数据
   * @returns Promise<any>
   */
  async post<T>(url: string, data?: Record<string, any>): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data);
    return response.data;
  }

  /**
   * 文件上传请求
   * @param url 请求URL
   * @param formData 表单数据
   * @returns Promise<any>
   */
  async upload<T>(url: string, formData: FormData): Promise<T> {
    return this.axiosInstance.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => response.data);
  }
}

// 创建全局API服务实例
export const apiService = new ApiService();