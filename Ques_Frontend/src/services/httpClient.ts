import { API_CONFIG } from './config';
import type { ApiResponse } from '../types/api';

// HTTP方法类型
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// 请求配置
interface RequestConfig {
  method: HttpMethod;
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
}

// 错误类型
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class HttpClient {
  private baseURL: string;
  private timeout: number;

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  // 获取认证token
  private getAuthToken(): string | null {
    return localStorage.getItem(API_CONFIG.AUTH.TOKEN_KEY);
  }

  // 设置认证token
  public setAuthToken(token: string): void {
    localStorage.setItem(API_CONFIG.AUTH.TOKEN_KEY, token);
  }

  // 清除认证token
  public clearAuthToken(): void {
    localStorage.removeItem(API_CONFIG.AUTH.TOKEN_KEY);
    localStorage.removeItem(API_CONFIG.AUTH.REFRESH_TOKEN_KEY);
    localStorage.removeItem(API_CONFIG.AUTH.USER_KEY);
  }

  // 构建请求头
  private buildHeaders(customHeaders?: Record<string, string>): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...customHeaders,
    };

    // 添加认证token
    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  // 处理响应
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      // 检查响应状态
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.code,
          errorData
        );
      }

      // 尝试解析JSON
      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Failed to parse response', response.status);
    }
  }

  // 基础请求方法
  private async request<T>(
    endpoint: string, 
    config: RequestConfig
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    
    // 设置超时
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, config.timeout || this.timeout);

    try {
      const headers = this.buildHeaders(config.headers);
      
      const fetchOptions: RequestInit = {
        method: config.method,
        headers,
        signal: controller.signal,
      };

      // 添加请求体
      if (config.body && config.method !== 'GET') {
        if (config.body instanceof FormData) {
          // FormData类型，移除Content-Type让浏览器自动设置
          delete headers['Content-Type'];
          fetchOptions.body = config.body;
        } else {
          fetchOptions.body = JSON.stringify(config.body);
        }
      }

      const response = await fetch(url, fetchOptions);
      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ApiError) {
        // 处理401未授权错误
        if (error.status === 401) {
          this.clearAuthToken();
          // 可以在这里触发重新登录逻辑
          window.location.href = '/login';
        }
        throw error;
      }
      
      // 处理网络错误
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('Request timeout');
      }
      
      throw new ApiError('Network error');
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // GET 请求
  public async get<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET', headers });
  }

  // POST 请求
  public async post<T>(
    endpoint: string, 
    data?: any, 
    headers?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'POST', body: data, headers });
  }

  // PUT 请求
  public async put<T>(
    endpoint: string, 
    data?: any, 
    headers?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'PUT', body: data, headers });
  }

  // PATCH 请求
  public async patch<T>(
    endpoint: string, 
    data?: any, 
    headers?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'PATCH', body: data, headers });
  }

  // DELETE 请求
  public async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE', headers });
  }

  // 文件上传
  public async upload<T>(
    endpoint: string, 
    formData: FormData,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // 设置超时
      xhr.timeout = this.timeout;
      
      // 进度回调
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const progress = (e.loaded / e.total) * 100;
            onProgress(Math.round(progress));
          }
        });
      }
      
      // 完成回调
      xhr.addEventListener('load', () => {
        try {
          const response = JSON.parse(xhr.responseText);
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(response);
          } else {
            reject(new ApiError(
              response.message || `HTTP ${xhr.status}`,
              xhr.status,
              response.code,
              response
            ));
          }
        } catch (error) {
          reject(new ApiError('Failed to parse response', xhr.status));
        }
      });
      
      // 错误回调
      xhr.addEventListener('error', () => {
        reject(new ApiError('Upload failed'));
      });
      
      // 超时回调
      xhr.addEventListener('timeout', () => {
        reject(new ApiError('Upload timeout'));
      });
      
      // 设置请求头
      const token = this.getAuthToken();
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      
      // 发送请求
      xhr.open('POST', url);
      xhr.send(formData);
    });
  }

  // Stream请求 - 支持Server-Sent Events (SSE)
  public async stream(
    endpoint: string,
    data?: any,
    onChunk?: (chunk: any) => void
  ): Promise<void> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = this.buildHeaders();

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: data ? JSON.stringify(data) : undefined,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.code,
          errorData
        );
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new ApiError('Stream not available');
      }

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (onChunk) {
                onChunk(data);
              }
            } catch (e) {
              console.error('Failed to parse chunk:', e);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Stream error');
    }
  }
}

// 创建全局HTTP客户端实例
export const httpClient = new HttpClient();

// 导出工具方法
export const { get, post, put, patch, delete: del, upload } = httpClient; 