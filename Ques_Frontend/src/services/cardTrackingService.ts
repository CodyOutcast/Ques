import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  UpdateLatestCardRequest,
  GetLatestCardResponse,
  LatestCardInfo,
  UserRecommendation
} from '../types/api';

/**
 * 卡片跟踪服务
 * 用于跟踪和管理当前聊天窗口中最新显示的卡片
 */
class CardTrackingService {
  // 本地缓存最新卡片（避免重复上传）
  private latestCardCache: LatestCardInfo | null = null;
  private lastUpdateTime: number = 0;
  private readonly UPDATE_THROTTLE_MS = 1000; // 1秒内不重复更新

  /**
   * 更新最新卡片信息到后端
   */
  async updateLatestCard(request: UpdateLatestCardRequest): Promise<ApiResponse<LatestCardInfo>> {
    try {
      // 检查是否需要节流（避免频繁更新）
      const now = Date.now();
      if (now - this.lastUpdateTime < this.UPDATE_THROTTLE_MS) {
        console.log('Throttling card update - too frequent');
        return {
          success: true,
          data: this.latestCardCache || undefined,
          message: 'Card update throttled'
        };
      }

      // 构建完整的卡片信息
      const cardInfo: LatestCardInfo = {
        cardData: request.cardData,
        sessionId: request.sessionId,
        messageId: request.messageId,
        displayedAt: new Date().toISOString(),
        context: request.context
      };

      const response = await httpClient.post<LatestCardInfo>(
        API_CONFIG.ENDPOINTS.CARD_TRACKING.UPDATE_LATEST_CARD,
        cardInfo
      );

      if (response.success) {
        // 更新本地缓存
        this.latestCardCache = cardInfo;
        this.lastUpdateTime = now;
        console.log('Latest card updated successfully:', cardInfo.cardData.name);
      }

      return response;
    } catch (error) {
      console.error('Failed to update latest card:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取最新卡片信息
   */
  async getLatestCard(): Promise<ApiResponse<GetLatestCardResponse>> {
    try {
      const response = await httpClient.get<GetLatestCardResponse>(
        API_CONFIG.ENDPOINTS.CARD_TRACKING.GET_LATEST_CARD
      );

      // 更新本地缓存
      if (response.success && response.data?.card) {
        this.latestCardCache = response.data.card;
      }

      return response;
    } catch (error) {
      console.error('Failed to get latest card:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 清除最新卡片信息
   */
  async clearLatestCard(): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        API_CONFIG.ENDPOINTS.CARD_TRACKING.CLEAR_LATEST_CARD
      );

      if (response.success) {
        // 清除本地缓存
        this.latestCardCache = null;
        this.lastUpdateTime = 0;
        console.log('Latest card cleared');
      }

      return response;
    } catch (error) {
      console.error('Failed to clear latest card:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取本地缓存的最新卡片（不调用API）
   */
  getCachedLatestCard(): LatestCardInfo | null {
    return this.latestCardCache;
  }

  /**
   * 检查是否有最新卡片
   */
  hasLatestCard(): boolean {
    return this.latestCardCache !== null;
  }

  /**
   * 快速更新卡片（带自动上下文提取）
   * 这是一个便捷方法，自动从当前状态提取必要信息
   */
  async quickUpdateCard(
    cardData: UserRecommendation,
    options?: {
      sessionId?: string;
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
      cardPosition?: number;
    }
  ): Promise<ApiResponse<LatestCardInfo>> {
    const request: UpdateLatestCardRequest = {
      cardData,
      sessionId: options?.sessionId,
      context: {
        searchQuery: options?.searchQuery,
        searchMode: options?.searchMode || 'inside',
        cardPosition: options?.cardPosition || 0
      }
    };

    return this.updateLatestCard(request);
  }

  /**
   * 批量更新多张卡片的最新显示（只保留第一张）
   */
  async updateFromCardStack(
    cards: UserRecommendation[],
    currentIndex: number,
    options?: {
      sessionId?: string;
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
    }
  ): Promise<ApiResponse<LatestCardInfo> | null> {
    if (cards.length === 0 || currentIndex >= cards.length) {
      return null;
    }

    // 只更新当前显示的第一张卡片
    const currentCard = cards[currentIndex];
    return this.quickUpdateCard(currentCard, {
      ...options,
      cardPosition: currentIndex
    });
  }

  /**
   * 验证卡片数据完整性
   */
  validateCardData(cardData: UserRecommendation): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!cardData.id) {
      errors.push('Card ID is required');
    }

    if (!cardData.name) {
      errors.push('Card name is required');
    }

    if (!cardData.avatar) {
      errors.push('Card avatar is required');
    }

    if (!cardData.location) {
      errors.push('Card location is required');
    }

    if (!cardData.skills || cardData.skills.length === 0) {
      errors.push('Card must have at least one skill');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 格式化卡片信息用于显示
   */
  formatCardInfo(card: LatestCardInfo): {
    displayName: string;
    displayTime: string;
    displayContext: string;
  } {
    const displayTime = new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      month: 'short',
      day: 'numeric'
    }).format(new Date(card.displayedAt));

    const displayContext = card.context?.searchQuery 
      ? `搜索: ${card.context.searchQuery}`
      : '推荐卡片';

    return {
      displayName: card.cardData.name,
      displayTime,
      displayContext
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
    
    return new ApiError('Unknown error occurred in card tracking service');
  }
}

// 创建并导出卡片跟踪服务实例
export const cardTrackingService = new CardTrackingService();

// 导出默认实例
export default cardTrackingService;

