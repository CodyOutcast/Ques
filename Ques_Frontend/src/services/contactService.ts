import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  ContactedUser,
  AddContactRequest,
  UpdateContactRequest,
  ReportContactRequest,
  PaginatedResponse,
  UserRecommendation
} from '../types/api';

class ContactService {
  /**
   * 获取联系人列表
   */
  async getContacts(params?: {
    page?: number;
    limit?: number;
    status?: 'active' | 'blocked' | 'archived';
    tags?: string[];
    searchQuery?: string;
  }): Promise<ApiResponse<PaginatedResponse<ContactedUser>>> {
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
      if (params?.tags?.length) {
        params.tags.forEach(tag => searchParams.append('tags[]', tag));
      }
      if (params?.searchQuery) {
        searchParams.append('q', params.searchQuery);
      }

      const url = `${API_CONFIG.ENDPOINTS.CONTACTS.GET_CONTACTS}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<ContactedUser>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get contacts:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 添加联系人
   */
  async addContact(request: AddContactRequest): Promise<ApiResponse<ContactedUser>> {
    try {
      const response = await httpClient.post<ContactedUser>(
        API_CONFIG.ENDPOINTS.CONTACTS.ADD_CONTACT,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to add contact:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新联系人信息
   */
  async updateContact(request: UpdateContactRequest): Promise<ApiResponse<ContactedUser>> {
    try {
      const response = await httpClient.put<ContactedUser>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.UPDATE_CONTACT}/${request.contactId}`,
        {
          notes: request.notes,
          tags: request.tags,
          status: request.status
        }
      );

      return response;
    } catch (error) {
      console.error('Failed to update contact:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除联系人
   */
  async deleteContact(contactId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.DELETE_CONTACT}/${contactId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to delete contact:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 举报联系人
   */
  async reportContact(request: ReportContactRequest): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.post<void>(
        API_CONFIG.ENDPOINTS.CONTACTS.REPORT_CONTACT,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to report contact:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取联系人历史记录
   */
  async getContactHistory(contactId: string): Promise<ApiResponse<{
    conversationCount: number;
    lastContactedAt: string;
    firstContactedAt: string;
    interactions: Array<{
      id: string;
      type: 'message' | 'call' | 'meeting' | 'email';
      timestamp: string;
      summary?: string;
    }>;
  }>> {
    try {
      const response = await httpClient.get<{
        conversationCount: number;
        lastContactedAt: string;
        firstContactedAt: string;
        interactions: Array<{
          id: string;
          type: 'message' | 'call' | 'meeting' | 'email';
          timestamp: string;
          summary?: string;
        }>;
      }>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.GET_CONTACT_HISTORY}/${contactId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to get contact history:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 从推荐用户转换为联系人
   */
  convertRecommendationToContact(recommendation: UserRecommendation): ContactedUser {
    return {
      id: recommendation.id,
      name: recommendation.name,
      age: recommendation.age,
      gender: recommendation.gender,
      avatar: recommendation.avatar,
      location: recommendation.location,
      hobbies: recommendation.hobbies,
      languages: recommendation.languages,
      skills: recommendation.skills,
      resources: recommendation.resources,
      projects: recommendation.projects,
      goals: recommendation.goals,
      demands: recommendation.demands,
      institutions: recommendation.institutions,
      university: recommendation.university,
      matchScore: recommendation.matchScore,
      bio: recommendation.bio,
      oneSentenceIntro: recommendation.oneSentenceIntro,
      whyMatch: recommendation.whyMatch,
      receivesLeft: recommendation.receivesLeft,
      contactedAt: new Date().toISOString(),
      reported: false,
      status: 'active',
      tags: [],
      notes: ''
    };
  }

  /**
   * 批量添加联系人
   */
  async addMultipleContacts(
    recommendations: UserRecommendation[],
    defaultNotes?: string,
    defaultTags?: string[]
  ): Promise<ApiResponse<ContactedUser[]>> {
    try {
      const requests = recommendations.map(rec => ({
        contactId: rec.id,
        notes: defaultNotes,
        tags: defaultTags || []
      }));

      const response = await httpClient.post<ContactedUser[]>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.ADD_CONTACT}/batch`,
        { contacts: requests }
      );

      return response;
    } catch (error) {
      console.error('Failed to add multiple contacts:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取联系人统计信息
   */
  async getContactStats(): Promise<ApiResponse<{
    total: number;
    active: number;
    blocked: number;
    archived: number;
    recentlyAdded: number;
    topSkills: Array<{ skill: string; count: number }>;
    topLocations: Array<{ location: string; count: number }>;
  }>> {
    try {
      const response = await httpClient.get<{
        total: number;
        active: number;
        blocked: number;
        archived: number;
        recentlyAdded: number;
        topSkills: Array<{ skill: string; count: number }>;
        topLocations: Array<{ location: string; count: number }>;
      }>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.GET_CONTACTS}/stats`
      );

      return response;
    } catch (error) {
      console.error('Failed to get contact stats:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 搜索联系人
   */
  async searchContacts(query: string, filters?: {
    skills?: string[];
    location?: string;
    university?: string;
    tags?: string[];
  }): Promise<ApiResponse<ContactedUser[]>> {
    try {
      const response = await httpClient.post<ContactedUser[]>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.GET_CONTACTS}/search`,
        {
          query,
          filters: filters || {}
        }
      );

      return response;
    } catch (error) {
      console.error('Failed to search contacts:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 导出联系人数据
   */
  async exportContacts(format: 'csv' | 'json' = 'csv'): Promise<ApiResponse<{
    downloadUrl: string;
    filename: string;
  }>> {
    try {
      const response = await httpClient.post<{
        downloadUrl: string;
        filename: string;
      }>(
        `${API_CONFIG.ENDPOINTS.CONTACTS.GET_CONTACTS}/export`,
        { format }
      );

      return response;
    } catch (error) {
      console.error('Failed to export contacts:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取推荐的标签
   */
  getSuggestedTags(): string[] {
    return [
      'Co-founder',
      'Mentor',
      'Investor',
      'Collaborator',
      'Networking',
      'Technical',
      'Business',
      'Design',
      'Marketing',
      'Research',
      'Startup',
      'AI/ML',
      'Product',
      'Engineering',
      'High Priority',
      'Follow Up',
      'Potential Partner',
      'Industry Expert'
    ];
  }

  /**
   * 验证联系人操作
   */
  validateContactRequest(request: AddContactRequest | UpdateContactRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // 检查联系人ID
    if (!request.contactId || !request.contactId.trim()) {
      errors.push('Contact ID is required');
    }

    // 检查notes长度
    if (request.notes && request.notes.length > 500) {
      errors.push('Notes are too long (maximum 500 characters)');
    }

    // 检查tags数量和长度
    if (request.tags) {
      if (request.tags.length > 10) {
        errors.push('Too many tags (maximum 10)');
      }

      const invalidTags = request.tags.filter(tag => !tag.trim() || tag.length > 20);
      if (invalidTags.length > 0) {
        errors.push('Tags must be 1-20 characters long');
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 格式化联系人显示信息
   */
  formatContactForDisplay(contact: ContactedUser): {
    displayName: string;
    displayLocation: string;
    skillsSummary: string;
    statusBadge: {
      text: string;
      color: 'green' | 'red' | 'yellow' | 'gray';
    };
    contactedAgo: string;
  } {
    return {
      displayName: contact.name,
      displayLocation: contact.location,
      skillsSummary: contact.skills.slice(0, 3).join(', ') + 
        (contact.skills.length > 3 ? ` +${contact.skills.length - 3} more` : ''),
      statusBadge: {
        text: contact.status.charAt(0).toUpperCase() + contact.status.slice(1),
        color: contact.status === 'active' ? 'green' : 
               contact.status === 'blocked' ? 'red' :
               contact.status === 'archived' ? 'yellow' : 'gray'
      },
      contactedAgo: this.getRelativeTime(contact.contactedAt)
    };
  }

  /**
   * 获取相对时间
   */
  private getRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) {
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
      if (diffInHours === 0) {
        const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
        return `${diffInMinutes} minutes ago`;
      }
      return `${diffInHours} hours ago`;
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else if (diffInDays < 7) {
      return `${diffInDays} days ago`;
    } else if (diffInDays < 30) {
      const diffInWeeks = Math.floor(diffInDays / 7);
      return `${diffInWeeks} week${diffInWeeks > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString();
    }
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

// 创建并导出联系人服务实例
export const contactService = new ContactService();

// 导出默认实例
export default contactService; 