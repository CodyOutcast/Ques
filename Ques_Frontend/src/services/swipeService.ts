import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  SwipeRecord,
  RecordSwipeRequest,
  SwipeStats,
  SwipeAction,
  PaginatedResponse
} from '../types/api';

class SwipeService {
  /**
   * 记录卡片滑动行为
   */
  async recordSwipe(request: RecordSwipeRequest): Promise<ApiResponse<SwipeRecord>> {
    try {
      const response = await httpClient.post<SwipeRecord>(
        API_CONFIG.ENDPOINTS.SWIPE.RECORD_SWIPE,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to record swipe:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 批量记录滑动行为（用于离线同步）
   */
  async recordSwipeBatch(requests: RecordSwipeRequest[]): Promise<ApiResponse<SwipeRecord[]>> {
    try {
      const response = await httpClient.post<SwipeRecord[]>(
        `${API_CONFIG.ENDPOINTS.SWIPE.RECORD_SWIPE}/batch`,
        { swipes: requests }
      );

      return response;
    } catch (error) {
      console.error('Failed to record swipe batch:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取滑动历史
   */
  async getSwipeHistory(params?: {
    page?: number;
    limit?: number;
    action?: SwipeAction;
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<PaginatedResponse<SwipeRecord>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.action) {
        searchParams.append('action', params.action);
      }
      if (params?.startDate) {
        searchParams.append('startDate', params.startDate);
      }
      if (params?.endDate) {
        searchParams.append('endDate', params.endDate);
      }

      const url = `${API_CONFIG.ENDPOINTS.SWIPE.GET_SWIPE_HISTORY}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<SwipeRecord>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get swipe history:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取滑动统计数据
   */
  async getSwipeStats(params?: {
    period?: 'day' | 'week' | 'month' | 'all';
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<SwipeStats>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.period) {
        searchParams.append('period', params.period);
      }
      if (params?.startDate) {
        searchParams.append('startDate', params.startDate);
      }
      if (params?.endDate) {
        searchParams.append('endDate', params.endDate);
      }

      const url = `${API_CONFIG.ENDPOINTS.SWIPE.GET_SWIPE_STATS}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<SwipeStats>(url);

      return response;
    } catch (error) {
      console.error('Failed to get swipe stats:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取用户的滑动偏好分析
   */
  async getSwipePreferences(): Promise<ApiResponse<{
    preferredSkills: Array<{ skill: string; frequency: number }>;
    preferredLocations: Array<{ location: string; frequency: number }>;
    preferredUniversities: Array<{ university: string; frequency: number }>;
    swipePatterns: {
      peakHours: number[];
      dayOfWeekPattern: Array<{ day: string; count: number }>;
    };
    matchSuccessFactors: {
      skillsImportance: number;
      locationImportance: number;
      universityImportance: number;
      projectsImportance: number;
    };
  }>> {
    try {
      const response = await httpClient.get<{
        preferredSkills: Array<{ skill: string; frequency: number }>;
        preferredLocations: Array<{ location: string; frequency: number }>;
        preferredUniversities: Array<{ university: string; frequency: number }>;
        swipePatterns: {
          peakHours: number[];
          dayOfWeekPattern: Array<{ day: string; count: number }>;
        };
        matchSuccessFactors: {
          skillsImportance: number;
          locationImportance: number;
          universityImportance: number;
          projectsImportance: number;
        };
      }>(`${API_CONFIG.ENDPOINTS.SWIPE.GET_SWIPE_STATS}/preferences`);

      return response;
    } catch (error) {
      console.error('Failed to get swipe preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除滑动记录（用于隐私管理）
   */
  async deleteSwipeRecord(swipeId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        `${API_CONFIG.ENDPOINTS.SWIPE.RECORD_SWIPE}/${swipeId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to delete swipe record:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 清空滑动历史
   */
  async clearSwipeHistory(params?: {
    olderThan?: string; // ISO date string
    action?: SwipeAction;
  }): Promise<ApiResponse<{ deletedCount: number }>> {
    try {
      const response = await httpClient.delete<{ deletedCount: number }>(
        `${API_CONFIG.ENDPOINTS.SWIPE.RECORD_SWIPE}/bulk`,
        params
      );

      return response;
    } catch (error) {
      console.error('Failed to clear swipe history:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 本地滑动行为缓存管理
   */
  private localSwipeCache: RecordSwipeRequest[] = [];
  private readonly MAX_CACHE_SIZE = 50;
  private readonly CACHE_KEY = 'swipe_cache';

  /**
   * 添加滑动行为到本地缓存
   */
  addToLocalCache(request: RecordSwipeRequest): void {
    try {
      this.localSwipeCache.push({
        ...request,
        // Add client timestamp for offline scenarios
        clientTimestamp: new Date().toISOString(),
      } as any);

      // Maintain cache size limit
      if (this.localSwipeCache.length > this.MAX_CACHE_SIZE) {
        this.localSwipeCache = this.localSwipeCache.slice(-this.MAX_CACHE_SIZE);
      }

      // Save to localStorage
      localStorage.setItem(this.CACHE_KEY, JSON.stringify(this.localSwipeCache));
    } catch (error) {
      console.error('Failed to add to local swipe cache:', error);
    }
  }

  /**
   * 同步本地缓存到服务器
   */
  async syncLocalCache(): Promise<void> {
    try {
      if (this.localSwipeCache.length === 0) {
        return;
      }

      const response = await this.recordSwipeBatch(this.localSwipeCache);
      
      if (response.success) {
        // Clear cache after successful sync
        this.localSwipeCache = [];
        localStorage.removeItem(this.CACHE_KEY);
      }
    } catch (error) {
      console.error('Failed to sync swipe cache:', error);
      // Keep cache for retry
    }
  }

  /**
   * 从localStorage加载缓存
   */
  loadLocalCache(): void {
    try {
      const cached = localStorage.getItem(this.CACHE_KEY);
      if (cached) {
        this.localSwipeCache = JSON.parse(cached);
      }
    } catch (error) {
      console.error('Failed to load swipe cache:', error);
      this.localSwipeCache = [];
    }
  }

  /**
   * 智能滑动建议（基于历史行为）
   */
  async getSwipeSuggestions(targetUserId: string): Promise<ApiResponse<{
    suggestedAction: SwipeAction;
    confidence: number;
    reasoning: string[];
    similarProfiles: Array<{
      userId: string;
      name: string;
      action: SwipeAction;
      similarity: number;
    }>;
  }>> {
    try {
      const response = await httpClient.get<{
        suggestedAction: SwipeAction;
        confidence: number;
        reasoning: string[];
        similarProfiles: Array<{
          userId: string;
          name: string;
          action: SwipeAction;
          similarity: number;
        }>;
      }>(`${API_CONFIG.ENDPOINTS.SWIPE.GET_SWIPE_STATS}/suggestions/${targetUserId}`);

      return response;
    } catch (error) {
      console.error('Failed to get swipe suggestions:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证滑动请求
   */
  validateSwipeRequest(request: RecordSwipeRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!request.targetUserId) {
      errors.push('Target user ID is required');
    }

    if (!request.action || !['like', 'ignore', 'super_like'].includes(request.action)) {
      errors.push('Valid action is required (like, ignore, or super_like)');
    }

    if (request.matchScore && (request.matchScore < 0 || request.matchScore > 100)) {
      errors.push('Match score must be between 0 and 100');
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

// 创建并导出滑动服务实例
export const swipeService = new SwipeService();

// 初始化时加载本地缓存
swipeService.loadLocalCache();

// 导出默认实例
export default swipeService; 