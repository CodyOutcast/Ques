import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  UserSettings,
  UpdateNotificationSettingsRequest,
  UpdateUserPreferencesRequest,
  UserStats,
  LogoutRequest,
  DeleteAccountRequest,
  DeleteAccountResponse
} from '../types/api';

class SettingsService {
  /**
   * 获取用户设置
   */
  async getUserSettings(): Promise<ApiResponse<UserSettings>> {
    try {
      const response = await httpClient.get<UserSettings>(
        API_CONFIG.ENDPOINTS.SETTINGS.GET_USER_SETTINGS
      );

      return response;
    } catch (error) {
      console.error('Failed to get user settings:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新通知设置
   */
  async updateNotificationSettings(
    request: UpdateNotificationSettingsRequest
  ): Promise<ApiResponse<UserSettings>> {
    try {
      const response = await httpClient.put<UserSettings>(
        API_CONFIG.ENDPOINTS.SETTINGS.UPDATE_NOTIFICATION_SETTINGS,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to update notification settings:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新用户偏好设置
   */
  async updateUserPreferences(
    request: UpdateUserPreferencesRequest
  ): Promise<ApiResponse<UserSettings>> {
    try {
      const response = await httpClient.put<UserSettings>(
        API_CONFIG.ENDPOINTS.SETTINGS.UPDATE_USER_PREFERENCES,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to update user preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取用户统计信息
   */
  async getUserStats(): Promise<ApiResponse<UserStats>> {
    try {
      const response = await httpClient.get<UserStats>(
        API_CONFIG.ENDPOINTS.SETTINGS.GET_USER_STATS
      );

      return response;
    } catch (error) {
      console.error('Failed to get user stats:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 用户登出
   */
  async logout(request?: LogoutRequest): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.post<void>(
        API_CONFIG.ENDPOINTS.ACCOUNT.LOGOUT,
        request || {}
      );

      // 清除本地存储的认证信息
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_profile');

      return response;
    } catch (error) {
      console.error('Failed to logout:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除账户
   */
  async deleteAccount(request: DeleteAccountRequest): Promise<ApiResponse<DeleteAccountResponse>> {
    try {
      const response = await httpClient.post<DeleteAccountResponse>(
        API_CONFIG.ENDPOINTS.ACCOUNT.DELETE_ACCOUNT,
        request
      );

      // 删除成功后清除所有本地数据
      localStorage.clear();
      sessionStorage.clear();

      return response;
    } catch (error) {
      console.error('Failed to delete account:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 导出用户数据
   */
  async exportUserData(): Promise<ApiResponse<{ downloadUrl: string; expiresAt: string }>> {
    try {
      const response = await httpClient.post<{ downloadUrl: string; expiresAt: string }>(
        API_CONFIG.ENDPOINTS.ACCOUNT.EXPORT_DATA
      );

      return response;
    } catch (error) {
      console.error('Failed to export user data:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取账户信息
   */
  async getAccountInfo(): Promise<ApiResponse<{
    userId: string;
    email: string;
    createdAt: string;
    lastLoginAt: string;
    dataRetentionDays: number;
  }>> {
    try {
      const response = await httpClient.get<{
        userId: string;
        email: string;
        createdAt: string;
        lastLoginAt: string;
        dataRetentionDays: number;
      }>(API_CONFIG.ENDPOINTS.ACCOUNT.GET_ACCOUNT_INFO);

      return response;
    } catch (error) {
      console.error('Failed to get account info:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 本地设置管理
   */

  /**
   * 获取本地存储的微信ID
   */
  getLocalWechatId(): string | null {
    return localStorage.getItem('user_wechat_id');
  }

  /**
   * 保存微信ID到本地
   */
  setLocalWechatId(wechatId: string): void {
    localStorage.setItem('user_wechat_id', wechatId);
  }

  /**
   * 获取本地存储的自定义whisper消息
   */
  getLocalCustomWhisperMessage(): string | null {
    return localStorage.getItem('custom_whisper_message');
  }

  /**
   * 保存自定义whisper消息到本地
   */
  setLocalCustomWhisperMessage(message: string): void {
    localStorage.setItem('custom_whisper_message', message);
  }

  /**
   * 获取本地通知设置
   */
  getLocalNotificationSettings(): { whisperRequests: boolean } {
    const saved = localStorage.getItem('notification_settings');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        console.error('Failed to parse notification settings:', error);
      }
    }
    return { whisperRequests: true }; // 默认值
  }

  /**
   * 保存通知设置到本地
   */
  setLocalNotificationSettings(settings: { whisperRequests: boolean }): void {
    localStorage.setItem('notification_settings', JSON.stringify(settings));
  }

  /**
   * 清除所有本地设置
   */
  clearLocalSettings(): void {
    localStorage.removeItem('user_wechat_id');
    localStorage.removeItem('custom_whisper_message');
    localStorage.removeItem('notification_settings');
  }

  /**
   * 验证删除账户请求
   */
  validateDeleteAccountRequest(request: DeleteAccountRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!request.confirmPassword) {
      errors.push('Password confirmation is required');
    }

    if (request.confirmPassword && request.confirmPassword.length < 6) {
      errors.push('Password must be at least 6 characters');
    }

    if (request.reason && request.reason.length > 500) {
      errors.push('Reason must be 500 characters or less');
    }

    if (request.feedback && request.feedback.length > 1000) {
      errors.push('Feedback must be 1000 characters or less');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
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

// 创建并导出设置服务实例
export const settingsService = new SettingsService();

// 导出默认实例
export default settingsService; 