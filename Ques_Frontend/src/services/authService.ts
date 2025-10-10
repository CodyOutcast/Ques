import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  RegisterRequest,
  LoginRequest,
  LoginResponse,
  VerificationCodeRequest,
  CodeVerificationRequest,
  UserAuth,
  FileUploadResponse
} from '../types/api';

class AuthService {
  /**
   * 用户注册
   */
  async register(userData: RegisterRequest): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await httpClient.post<LoginResponse>(
        API_CONFIG.ENDPOINTS.AUTH.REGISTER,
        userData
      );

      // 注册成功后自动保存token
      if (response.success && response.data) {
        this.saveAuthData(response.data);
      }

      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 用户登录
   */
  async login(loginData: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await httpClient.post<LoginResponse>(
        API_CONFIG.ENDPOINTS.AUTH.LOGIN,
        loginData
      );

      // 登录成功后保存认证数据
      if (response.success && response.data) {
        this.saveAuthData(response.data);
      }

      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 发送验证码
   */
  async sendVerificationCode(request: VerificationCodeRequest): Promise<ApiResponse<{ 
    sent: boolean; 
    expiresIn: number; 
  }>> {
    try {
      return await httpClient.post(
        API_CONFIG.ENDPOINTS.AUTH.SEND_CODE,
        request
      );
    } catch (error) {
      console.error('Failed to send verification code:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证验证码
   */
  async verifyCode(request: CodeVerificationRequest): Promise<ApiResponse<{ 
    verified: boolean;
    token?: string;
  }>> {
    try {
      return await httpClient.post(
        API_CONFIG.ENDPOINTS.AUTH.VERIFY_CODE,
        request
      );
    } catch (error) {
      console.error('Code verification failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 刷新token
   */
  async refreshToken(): Promise<ApiResponse<{ 
    token: string; 
    refreshToken: string; 
  }>> {
    try {
      const refreshToken = localStorage.getItem(API_CONFIG.AUTH.REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        throw new ApiError('No refresh token available');
      }

      const response = await httpClient.post<{ 
        token: string; 
        refreshToken: string; 
      }>(
        API_CONFIG.ENDPOINTS.AUTH.REFRESH,
        { refreshToken }
      );

      // 更新token
      if (response.success && response.data) {
        httpClient.setAuthToken(response.data.token);
        localStorage.setItem(API_CONFIG.AUTH.REFRESH_TOKEN_KEY, response.data.refreshToken);
      }

      return response;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // 刷新失败，清除所有认证数据
      this.logout();
      throw this.handleError(error);
    }
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    try {
      await httpClient.post(API_CONFIG.ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout request failed:', error);
      // 即使服务器请求失败，也要清除本地数据
    } finally {
      this.clearAuthData();
    }
  }

  /**
   * 检查用户是否已登录
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem(API_CONFIG.AUTH.TOKEN_KEY);
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  /**
   * 获取当前用户信息
   */
  getCurrentUser(): UserAuth | null {
    try {
      const userStr = localStorage.getItem(API_CONFIG.AUTH.USER_KEY);
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Failed to parse user data:', error);
      return null;
    }
  }

  /**
   * 获取当前token
   */
  getCurrentToken(): string | null {
    return localStorage.getItem(API_CONFIG.AUTH.TOKEN_KEY);
  }

  /**
   * 上传头像
   */
  async uploadAvatar(file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<FileUploadResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', 'avatar');

      return await httpClient.upload<FileUploadResponse>(
        API_CONFIG.ENDPOINTS.UPLOAD.IMAGE,
        formData,
        onProgress
      );
    } catch (error) {
      console.error('Avatar upload failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 微信登录授权
   */
  async wechatAuth(): Promise<ApiResponse<{ 
    authUrl: string; 
    state: string; 
  }>> {
    try {
      return await httpClient.get('/auth/wechat/authorize');
    } catch (error) {
      console.error('WeChat auth failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 微信登录回调处理
   */
  async wechatCallback(code: string, state: string): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await httpClient.post<LoginResponse>('/auth/wechat/callback', {
        code,
        state
      });

      if (response.success && response.data) {
        this.saveAuthData(response.data);
      }

      return response;
    } catch (error) {
      console.error('WeChat callback failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 保存认证数据
   */
  private saveAuthData(authData: LoginResponse): void {
    const { token, refreshToken, user } = authData;
    
    localStorage.setItem(API_CONFIG.AUTH.TOKEN_KEY, token);
    localStorage.setItem(API_CONFIG.AUTH.REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(API_CONFIG.AUTH.USER_KEY, JSON.stringify(user));
    
    // 设置HTTP客户端的token
    httpClient.setAuthToken(token);
  }

  /**
   * 清除认证数据
   */
  private clearAuthData(): void {
    httpClient.clearAuthToken();
  }

  /**
   * 统一错误处理
   */
  private handleError(error: any): Error {
    if (error instanceof ApiError) {
      return error;
    }
    
    if (error instanceof Error) {
      return new ApiError(error.message);
    }
    
    return new ApiError('Unknown error occurred');
  }
}

// 创建并导出认证服务实例
export const authService = new AuthService();

// 导出默认实例
export default authService; 