import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  Notification,
  FriendRequest,
  SendFriendRequestRequest,
  RespondFriendRequestRequest,
  ReceivesStatus,
  TopUpRequest,
  GiftReceivesRequest,
  PaginatedResponse
} from '../types/api';

class NotificationService {
  /**
   * 获取通知列表
   */
  async getNotifications(params?: {
    page?: number;
    limit?: number;
    type?: 'friend_request' | 'message' | 'match' | 'system' | 'gift';
    unreadOnly?: boolean;
  }): Promise<ApiResponse<PaginatedResponse<Notification>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.type) {
        searchParams.append('type', params.type);
      }
      if (params?.unreadOnly) {
        searchParams.append('unreadOnly', params.unreadOnly.toString());
      }

      const url = `${API_CONFIG.ENDPOINTS.NOTIFICATIONS.GET_NOTIFICATIONS}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<Notification>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get notifications:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 标记通知为已读
   */
  async markAsRead(notificationIds: string | string[]): Promise<ApiResponse<void>> {
    try {
      const ids = Array.isArray(notificationIds) ? notificationIds : [notificationIds];
      
      const response = await httpClient.post<void>(
        API_CONFIG.ENDPOINTS.NOTIFICATIONS.MARK_AS_READ,
        { notificationIds: ids }
      );

      return response;
    } catch (error) {
      console.error('Failed to mark notifications as read:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除通知
   */
  async deleteNotification(notificationId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        `${API_CONFIG.ENDPOINTS.NOTIFICATIONS.DELETE_NOTIFICATION}/${notificationId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to delete notification:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取好友请求列表
   */
  async getFriendRequests(params?: {
    page?: number;
    limit?: number;
    status?: 'pending' | 'accepted' | 'declined' | 'expired';
    direction?: 'sent' | 'received' | 'all';
  }): Promise<ApiResponse<PaginatedResponse<FriendRequest>>> {
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
      if (params?.direction) {
        searchParams.append('direction', params.direction);
      }

      const url = `${API_CONFIG.ENDPOINTS.NOTIFICATIONS.GET_FRIEND_REQUESTS}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<FriendRequest>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get friend requests:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 发送好友请求
   */
  async sendFriendRequest(request: SendFriendRequestRequest): Promise<ApiResponse<FriendRequest>> {
    try {
      const response = await httpClient.post<FriendRequest>(
        API_CONFIG.ENDPOINTS.NOTIFICATIONS.SEND_FRIEND_REQUEST,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to send friend request:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 回应好友请求
   */
  async respondToFriendRequest(request: RespondFriendRequestRequest): Promise<ApiResponse<FriendRequest>> {
    try {
      const response = await httpClient.post<FriendRequest>(
        API_CONFIG.ENDPOINTS.NOTIFICATIONS.RESPOND_FRIEND_REQUEST,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to respond to friend request:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取接收数量状态
   */
  async getReceivesStatus(): Promise<ApiResponse<ReceivesStatus>> {
    try {
      const response = await httpClient.get<ReceivesStatus>(
        API_CONFIG.ENDPOINTS.RECEIVES.GET_STATUS
      );

      return response;
    } catch (error) {
      console.error('Failed to get receives status:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 充值接收数量
   */
  async topUpReceives(request: TopUpRequest): Promise<ApiResponse<ReceivesStatus>> {
    try {
      const response = await httpClient.post<ReceivesStatus>(
        API_CONFIG.ENDPOINTS.RECEIVES.TOP_UP,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to top up receives:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 赠送接收数量
   */
  async giftReceives(request: GiftReceivesRequest): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.post<void>(
        API_CONFIG.ENDPOINTS.RECEIVES.GIFT,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to gift receives:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取接收历史记录
   */
  async getReceivesHistory(params?: {
    page?: number;
    limit?: number;
    type?: 'purchase' | 'gift_sent' | 'gift_received' | 'usage';
  }): Promise<ApiResponse<PaginatedResponse<{
    id: string;
    type: 'purchase' | 'gift_sent' | 'gift_received' | 'usage';
    amount: number;
    description: string;
    relatedUserId?: string;
    relatedUserName?: string;
    timestamp: string;
  }>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.type) {
        searchParams.append('type', params.type);
      }

      const url = `${API_CONFIG.ENDPOINTS.RECEIVES.GET_HISTORY}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<{
        id: string;
        type: 'purchase' | 'gift_sent' | 'gift_received' | 'usage';
        amount: number;
        description: string;
        relatedUserId?: string;
        relatedUserName?: string;
        timestamp: string;
      }>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get receives history:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 模拟好友请求数据（开发阶段使用）
   */
  getMockFriendRequests(): FriendRequest[] {
    return [
      {
        id: 'req_1',
        name: 'Emma Zhang',
        age: '26',
        gender: 'Female',
        avatar: '👩‍💼',
        location: 'Shanghai, China',
        hobbies: ['Design', 'Photography', 'Coffee'],
        languages: ['English', 'Mandarin', 'Japanese'],
        skills: ['Product Design', 'UX Research', 'Figma', 'Sketch', 'User Testing'],
        resources: ['Design Team', 'Research Lab', 'Prototyping Tools', 'User Testing Platform'],
        projects: [
          {
            title: 'Mobile Banking App',
            role: 'Lead Designer',
            description: 'Redesigned mobile banking experience for 2M+ users',
            referenceLinks: ['https://dribbble.com/emma-banking-redesign']
          },
          {
            title: 'Design System Framework',
            role: 'Creator',
            description: 'Built comprehensive design system for startup ecosystem',
            referenceLinks: []
          }
        ],
        goals: ['Start design consultancy', 'Publish design book', 'Teach UX workshops'],
        demands: ['Technical co-founder', 'Frontend developer', 'Business partner'],
        institutions: [
          {
            name: 'ByteDance',
            role: 'Senior Product Designer',
            description: 'Lead designer for TikTok\'s creator tools and monetization features',
            verified: true
          }
        ],
        university: {
          name: 'Shanghai University of Finance and Economics',
          verified: true
        },
        matchScore: 92,
        bio: 'Senior Product Designer at tech startup with passion for creating user-centered experiences',
        oneSentenceIntro: 'I design digital experiences that make complex tasks feel effortless.',
        mutualInterest: 'Perfect design-tech match! 🎨 You have the Python skills she needs for her design tool project, while she offers the UX expertise for your AI platform. Both looking for co-founders in China.',
        receivesLeft: 8,
        requestedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        wechatId: 'Emma_Designer2024',
        giftedReceives: 2,
        message: 'Hi! I saw your profile and think we could be great co-founders. I\'d love to discuss how we can combine design and tech!',
        status: 'pending'
      },
      {
        id: 'req_2',
        name: 'David Liu',
        age: '31',
        gender: 'Male',
        avatar: '👨‍💻',
        location: 'Beijing, China',
        hobbies: ['Blockchain', 'Gaming', 'Investing'],
        languages: ['Mandarin', 'English', 'Korean'],
        skills: ['Blockchain', 'Smart Contracts', 'Web3', 'Solidity', 'DeFi', 'Rust'],
        resources: ['Blockchain Infrastructure', 'Crypto Community', 'VC Network', 'Mining Farm Access'],
        projects: [
          {
            title: 'DeFi Lending Protocol',
            role: 'Lead Developer',
            description: 'Built decentralized lending platform with $50M+ TVL',
            referenceLinks: ['https://github.com/davidliu/defi-protocol']
          },
          {
            title: 'NFT Marketplace',
            role: 'Co-founder & CTO',
            description: 'Launched NFT platform for digital artists in Asia',
            referenceLinks: ['https://nftasia.com']
          }
        ],
        goals: ['Build next unicorn startup', 'Create Web3 ecosystem', 'Mentor blockchain developers'],
        demands: ['Business co-founder', 'Marketing expert', 'Regulatory advisor'],
        institutions: [
          {
            name: 'Binance',
            role: 'Former Blockchain Engineer',
            description: 'Core contributor to Binance Smart Chain development',
            verified: true
          }
        ],
        university: {
          name: 'Tsinghua University',
          verified: true
        },
        matchScore: 88,
        bio: 'Blockchain developer and crypto enthusiast building the future of decentralized finance',
        oneSentenceIntro: 'I build blockchain solutions that democratize access to financial services.',
        mutualInterest: 'Great tech synergy! ⚡ Your AI background complements his blockchain expertise perfectly for building next-gen fintech solutions. He\'s seeking technical co-founders with your skill set.',
        receivesLeft: 12,
        requestedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
        wechatId: 'DavidLiu_BlockDev',
        message: 'Your AI expertise would be perfect for our blockchain project. Let\'s build the future together!',
        status: 'pending'
      }
    ];
  }

  /**
   * 获取未读通知数量
   */
  async getUnreadCount(): Promise<ApiResponse<{
    total: number;
    friendRequests: number;
    messages: number;
    matches: number;
    system: number;
    gifts: number;
  }>> {
    try {
      const response = await httpClient.get<{
        total: number;
        friendRequests: number;
        messages: number;
        matches: number;
        system: number;
        gifts: number;
      }>(`${API_CONFIG.ENDPOINTS.NOTIFICATIONS.GET_NOTIFICATIONS}/unread-count`);

      return response;
    } catch (error) {
      console.error('Failed to get unread count:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 批量操作通知
   */
  async batchOperateNotifications(
    notificationIds: string[],
    operation: 'read' | 'delete'
  ): Promise<ApiResponse<void>> {
    try {
      const endpoint = operation === 'read' 
        ? API_CONFIG.ENDPOINTS.NOTIFICATIONS.MARK_AS_READ
        : `${API_CONFIG.ENDPOINTS.NOTIFICATIONS.DELETE_NOTIFICATION}/batch`;

      const response = await httpClient.post<void>(endpoint, {
        notificationIds
      });

      return response;
    } catch (error) {
      console.error(`Failed to ${operation} notifications:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * 设置通知偏好
   */
  async updateNotificationPreferences(preferences: {
    emailNotifications: boolean;
    pushNotifications: boolean;
    friendRequests: boolean;
    matches: boolean;
    messages: boolean;
    system: boolean;
    gifts: boolean;
  }): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.put<void>(
        `${API_CONFIG.ENDPOINTS.NOTIFICATIONS.GET_NOTIFICATIONS}/preferences`,
        preferences
      );

      return response;
    } catch (error) {
      console.error('Failed to update notification preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取通知偏好
   */
  async getNotificationPreferences(): Promise<ApiResponse<{
    emailNotifications: boolean;
    pushNotifications: boolean;
    friendRequests: boolean;
    matches: boolean;
    messages: boolean;
    system: boolean;
    gifts: boolean;
  }>> {
    try {
      const response = await httpClient.get<{
        emailNotifications: boolean;
        pushNotifications: boolean;
        friendRequests: boolean;
        matches: boolean;
        messages: boolean;
        system: boolean;
        gifts: boolean;
      }>(`${API_CONFIG.ENDPOINTS.NOTIFICATIONS.GET_NOTIFICATIONS}/preferences`);

      return response;
    } catch (error) {
      console.error('Failed to get notification preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证好友请求数据
   */
  validateFriendRequest(request: SendFriendRequestRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!request.recipientId || !request.recipientId.trim()) {
      errors.push('Recipient ID is required');
    }

    if (request.message && request.message.length > 500) {
      errors.push('Message is too long (maximum 500 characters)');
    }

    if (request.giftReceives && (request.giftReceives < 1 || request.giftReceives > 100)) {
      errors.push('Gift receives must be between 1 and 100');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 格式化通知显示
   */
  formatNotification(notification: Notification): {
    title: string;
    content: string;
    timeAgo: string;
    icon: string;
    color: string;
  } {
    const timeAgo = this.getRelativeTime(notification.createdAt);
    
    const typeConfig = {
      friend_request: { icon: '👥', color: 'blue' },
      message: { icon: '💬', color: 'green' },
      match: { icon: '⭐', color: 'yellow' },
      system: { icon: '🔔', color: 'gray' },
      gift: { icon: '🎁', color: 'purple' }
    };

    const config = typeConfig[notification.type] || typeConfig.system;

    return {
      title: notification.title,
      content: notification.content,
      timeAgo,
      icon: config.icon,
      color: config.color
    };
  }

  /**
   * 获取相对时间
   */
  private getRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
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

// 创建并导出通知服务实例
export const notificationService = new NotificationService();

// 导出默认实例
export default notificationService; 