import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  SendWhisperRequest,
  WhisperMessage,
  RespondWhisperRequest,
  WhisperSettings,
  PaginatedResponse
} from '../types/api';

class WhisperService {
  /**
   * 发送whisper消息
   */
  async sendWhisper(request: SendWhisperRequest): Promise<ApiResponse<WhisperMessage>> {
    try {
      const response = await httpClient.post<WhisperMessage>(
        API_CONFIG.ENDPOINTS.WHISPERS.SEND_WHISPER,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to send whisper:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取收到的whisper消息
   */
  async getReceivedWhispers(params?: {
    page?: number;
    limit?: number;
    status?: 'pending' | 'accepted' | 'declined' | 'expired';
  }): Promise<ApiResponse<PaginatedResponse<WhisperMessage>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.status) {
        searchParams.append('status', params.status);
      }

      const url = `${API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPERS}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<WhisperMessage>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get whispers:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取发送的whisper消息
   */
  async getSentWhispers(params?: {
    page?: number;
    limit?: number;
    status?: 'pending' | 'accepted' | 'declined' | 'expired';
  }): Promise<ApiResponse<PaginatedResponse<WhisperMessage>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.status) {
        searchParams.append('status', params.status);
      }

      const url = `${API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPERS}/sent${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<WhisperMessage>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get sent whispers:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 回复whisper消息
   */
  async respondToWhisper(request: RespondWhisperRequest): Promise<ApiResponse<WhisperMessage>> {
    try {
      const response = await httpClient.post<WhisperMessage>(
        API_CONFIG.ENDPOINTS.WHISPERS.RESPOND_WHISPER,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to respond to whisper:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取whisper设置
   */
  async getWhisperSettings(): Promise<ApiResponse<WhisperSettings>> {
    try {
      const response = await httpClient.get<WhisperSettings>(
        API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPER_SETTINGS
      );

      return response;
    } catch (error) {
      console.error('Failed to get whisper settings:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新whisper设置
   */
  async updateWhisperSettings(settings: Partial<WhisperSettings>): Promise<ApiResponse<WhisperSettings>> {
    try {
      const response = await httpClient.put<WhisperSettings>(
        API_CONFIG.ENDPOINTS.WHISPERS.UPDATE_WHISPER_SETTINGS,
        settings
      );

      return response;
    } catch (error) {
      console.error('Failed to update whisper settings:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取特定whisper消息详情
   */
  async getWhisperById(whisperId: string): Promise<ApiResponse<WhisperMessage>> {
    try {
      const response = await httpClient.get<WhisperMessage>(
        `${API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPERS}/${whisperId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to get whisper by id:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除whisper消息
   */
  async deleteWhisper(whisperId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        `${API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPERS}/${whisperId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to delete whisper:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 标记whisper为已读
   */
  async markWhisperAsRead(whisperId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.patch<void>(
        `${API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPERS}/${whisperId}/read`
      );

      return response;
    } catch (error) {
      console.error('Failed to mark whisper as read:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 批量标记whisper为已读
   */
  async markWhispersAsRead(whisperIds: string[]): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.patch<void>(
        `${API_CONFIG.ENDPOINTS.WHISPERS.GET_WHISPERS}/read/batch`,
        { whisperIds }
      );

      return response;
    } catch (error) {
      console.error('Failed to mark whispers as read:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证whisper请求数据
   */
  validateWhisperRequest(request: SendWhisperRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!request.recipientId) {
      errors.push('Recipient ID is required');
    }

    if (!request.senderProfile) {
      errors.push('Sender profile is required');
    } else {
      const profile = request.senderProfile;
      
      if (!profile.id) {
        errors.push('Sender profile ID is required');
      }
      if (!profile.name) {
        errors.push('Sender profile name is required');
      }
      if (!profile.wechatId) {
        errors.push('WeChat ID is required');
      }
      if (!profile.bio) {
        errors.push('Bio is required');
      }
      if (!profile.skills || profile.skills.length === 0) {
        errors.push('At least one skill is required');
      }
      if (profile.matchScore && (profile.matchScore < 0 || profile.matchScore > 100)) {
        errors.push('Match score must be between 0 and 100');
      }
    }

    if (request.message && request.message.length > 500) {
      errors.push('Message must be 500 characters or less');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 构建完整的whisper请求对象
   */
  buildWhisperRequest(
    recipientId: string,
    senderProfile: any,
    context?: {
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
      matchExplanation?: string;
      giftReceives?: number;
    },
    customMessage?: string
  ): SendWhisperRequest {
    const request: SendWhisperRequest = {
      recipientId,
      message: customMessage,
      senderProfile: {
        id: senderProfile.id || 'user_' + Date.now(),
        name: senderProfile.name,
        avatar: senderProfile.profilePhoto || senderProfile.avatar || '👤',
        age: senderProfile.age,
        gender: senderProfile.gender,
        location: senderProfile.location,
        skills: senderProfile.skills || [],
        resources: senderProfile.resources || [],
        projects: senderProfile.projects || [],
        goals: senderProfile.goals || [],
        demands: senderProfile.demands || [],
        institutions: senderProfile.institutions || [],
        university: senderProfile.university,
        bio: senderProfile.bio || senderProfile.oneSentenceIntro || 'No bio available',
        oneSentenceIntro: senderProfile.oneSentenceIntro,
        hobbies: senderProfile.hobbies || [],
        languages: senderProfile.languages || [],
        matchScore: context?.matchExplanation ? 85 : 75, // 默认匹配分数
        wechatId: senderProfile.wechatId || 'wechat_' + senderProfile.name?.replace(/\s+/g, '_').toLowerCase()
      },
      context: context
    };

    return request;
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

// 创建并导出whisper服务实例
export const whisperService = new WhisperService();

// 导出默认实例
export default whisperService; 