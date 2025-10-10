import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  UserRecommendation,
  MatchingCriteria,
  MatchScore,
  MatchExplanation,
  PaginatedResponse,
  SearchParams
} from '../types/api';

class MatchingService {
  /**
   * 搜索用户
   */
  async searchUsers(params: SearchParams & {
    criteria?: MatchingCriteria;
  }): Promise<ApiResponse<PaginatedResponse<UserRecommendation>>> {
    try {
      const response = await httpClient.post<PaginatedResponse<UserRecommendation>>(
        API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS,
        params
      );

      return response;
    } catch (error) {
      console.error('Failed to search users:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取匹配分数
   */
  async getMatchScore(
    targetUserId: string,
    criteria?: MatchingCriteria
  ): Promise<ApiResponse<MatchScore>> {
    try {
      const response = await httpClient.post<MatchScore>(
        `${API_CONFIG.ENDPOINTS.MATCHING.GET_MATCH_SCORE}/${targetUserId}`,
        criteria || {}
      );

      return response;
    } catch (error) {
      console.error('Failed to get match score:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取匹配解释
   */
  async getMatchExplanation(
    targetUserId: string,
    criteria?: MatchingCriteria
  ): Promise<ApiResponse<MatchExplanation>> {
    try {
      const response = await httpClient.post<MatchExplanation>(
        `${API_CONFIG.ENDPOINTS.MATCHING.GET_MATCH_EXPLANATION}/${targetUserId}`,
        criteria || {}
      );

      return response;
    } catch (error) {
      console.error('Failed to get match explanation:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新匹配标准
   */
  async updateMatchingCriteria(criteria: MatchingCriteria): Promise<ApiResponse<MatchingCriteria>> {
    try {
      const response = await httpClient.put<MatchingCriteria>(
        API_CONFIG.ENDPOINTS.MATCHING.UPDATE_CRITERIA,
        criteria
      );

      return response;
    } catch (error) {
      console.error('Failed to update matching criteria:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取匹配标准
   */
  async getMatchingCriteria(): Promise<ApiResponse<MatchingCriteria>> {
    try {
      const response = await httpClient.get<MatchingCriteria>(
        API_CONFIG.ENDPOINTS.MATCHING.GET_CRITERIA
      );

      return response;
    } catch (error) {
      console.error('Failed to get matching criteria:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 高级搜索
   */
  async advancedSearch(filters: {
    searchMode?: 'inside' | 'global';
    location?: {
      countries?: string[];
      cities?: string[];
      radius?: number; // km
    };
    demographics?: {
      ageRange?: [number, number];
      genders?: string[];
    };
    skills?: {
      required?: string[];
      preferred?: string[];
      exclude?: string[];
    };
    experience?: {
      levels?: string[];
      industries?: string[];
      roles?: string[];
    };
    education?: {
      universities?: string[];
      degrees?: string[];
      verified?: boolean;
    };
    availability?: {
      collaborationTypes?: string[];
      timeCommitment?: string[];
      remoteFriendly?: boolean;
    };
    other?: {
      hasProjects?: boolean;
      isOnline?: boolean;
      responseRate?: number; // minimum percentage
      mutualConnections?: boolean;
    };
    pagination?: {
      page: number;
      limit: number;
    };
    sorting?: {
      by: 'relevance' | 'match_score' | 'recent' | 'response_rate';
      order: 'asc' | 'desc';
    };
  }): Promise<ApiResponse<PaginatedResponse<UserRecommendation>>> {
    try {
      const response = await httpClient.post<PaginatedResponse<UserRecommendation>>(
        `${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/advanced`,
        filters
      );

      return response;
    } catch (error) {
      console.error('Failed to perform advanced search:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取搜索建议
   */
  async getSearchSuggestions(query: string): Promise<ApiResponse<{
    queries: string[];
    skills: string[];
    locations: string[];
    universities: string[];
    industries: string[];
  }>> {
    try {
      const response = await httpClient.get<{
        queries: string[];
        skills: string[];
        locations: string[];
        universities: string[];
        industries: string[];
      }>(`${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/suggestions?q=${encodeURIComponent(query)}`);

      return response;
    } catch (error) {
      console.error('Failed to get search suggestions:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取热门搜索
   */
  async getTrendingSearches(): Promise<ApiResponse<{
    queries: string[];
    skills: string[];
    collaborationTypes: string[];
  }>> {
    try {
      const response = await httpClient.get<{
        queries: string[];
        skills: string[];
        collaborationTypes: string[];
      }>(`${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/trending`);

      return response;
    } catch (error) {
      console.error('Failed to get trending searches:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 保存搜索
   */
  async saveSearch(params: {
    name: string;
    query?: string;
    filters: any;
  }): Promise<ApiResponse<{
    id: string;
    name: string;
    createdAt: string;
  }>> {
    try {
      const response = await httpClient.post<{
        id: string;
        name: string;
        createdAt: string;
      }>(`${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/save`, params);

      return response;
    } catch (error) {
      console.error('Failed to save search:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取保存的搜索
   */
  async getSavedSearches(): Promise<ApiResponse<Array<{
    id: string;
    name: string;
    query?: string;
    filters: any;
    createdAt: string;
    lastUsed?: string;
  }>>> {
    try {
      const response = await httpClient.get<Array<{
        id: string;
        name: string;
        query?: string;
        filters: any;
        createdAt: string;
        lastUsed?: string;
      }>>(`${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/saved`);

      return response;
    } catch (error) {
      console.error('Failed to get saved searches:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除保存的搜索
   */
  async deleteSavedSearch(searchId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        `${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/saved/${searchId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to delete saved search:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取搜索分析
   */
  async getSearchAnalytics(searchId?: string): Promise<ApiResponse<{
    totalSearches: number;
    averageResults: number;
    topQueries: Array<{ query: string; count: number }>;
    topFilters: Array<{ filter: string; value: string; count: number }>;
    searchSuccess: {
      withResults: number;
      withoutResults: number;
      contactRate: number;
    };
  }>> {
    try {
      const url = searchId 
        ? `${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/analytics/${searchId}`
        : `${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_USERS}/analytics`;
        
      const response = await httpClient.get<{
        totalSearches: number;
        averageResults: number;
        topQueries: Array<{ query: string; count: number }>;
        topFilters: Array<{ filter: string; value: string; count: number }>;
        searchSuccess: {
          withResults: number;
          withoutResults: number;
          contactRate: number;
        };
      }>(url);

      return response;
    } catch (error) {
      console.error('Failed to get search analytics:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 智能匹配推荐
   */
  async getSmartRecommendations(params?: {
    limit?: number;
    excludeContacted?: boolean;
    refreshData?: boolean;
  }): Promise<ApiResponse<UserRecommendation[]>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.excludeContacted) {
        searchParams.append('excludeContacted', params.excludeContacted.toString());
      }
      if (params?.refreshData) {
        searchParams.append('refreshData', params.refreshData.toString());
      }

      const url = `${API_CONFIG.ENDPOINTS.RECOMMENDATIONS.GET_RECOMMENDATIONS}/smart${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<UserRecommendation[]>(url);

      return response;
    } catch (error) {
      console.error('Failed to get smart recommendations:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证搜索参数
   */
  validateSearchParams(params: SearchParams): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (params.page && params.page < 1) {
      errors.push('Page must be greater than 0');
    }

    if (params.limit && (params.limit < 1 || params.limit > 100)) {
      errors.push('Limit must be between 1 and 100');
    }

    if (params.query && params.query.length > 200) {
      errors.push('Query is too long (maximum 200 characters)');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 计算匹配分数（本地算法）
   */
  calculateLocalMatchScore(
    userProfile: any,
    targetProfile: UserRecommendation,
    criteria?: MatchingCriteria
  ): MatchScore {
    let skillsMatch = 0;
    let goalsAlignment = 0;
    let locationMatch = 0;
    let networkOverlap = 0;
    let availabilityMatch = 0;
    let experienceMatch = 0;

    // 技能匹配
    if (userProfile.skills && targetProfile.skills) {
      const commonSkills = userProfile.skills.filter((skill: string) =>
        targetProfile.skills.some(s => s.toLowerCase().includes(skill.toLowerCase()))
      );
      skillsMatch = Math.min((commonSkills.length / Math.max(userProfile.skills.length, 1)) * 100, 100);
    }

    // 目标对齐
    if (userProfile.goals && targetProfile.goals) {
      const alignedGoals = userProfile.goals.filter((goal: string) =>
        targetProfile.goals.some(g => g.toLowerCase().includes(goal.toLowerCase()))
      );
      goalsAlignment = Math.min((alignedGoals.length / Math.max(userProfile.goals.length, 1)) * 100, 100);
    }

    // 位置匹配
    if (userProfile.location && targetProfile.location) {
      const userCity = userProfile.location.split(',')[0].trim();
      const targetCity = targetProfile.location.split(',')[0].trim();
      locationMatch = userCity.toLowerCase() === targetCity.toLowerCase() ? 100 : 50;
    }

    // 网络重叠（模拟）
    networkOverlap = targetProfile.mutualConnections ? Math.min(targetProfile.mutualConnections * 10, 100) : 0;

    // 可用性匹配（基于响应率）
    availabilityMatch = targetProfile.responseRate || 70;

    // 经验匹配（基于机构和项目）
    const userInstitutions = userProfile.institutions?.length || 0;
    const targetInstitutions = targetProfile.institutions?.length || 0;
    const userProjects = userProfile.projects?.length || 0;
    const targetProjects = targetProfile.projects?.length || 0;
    
    experienceMatch = Math.min(
      ((Math.min(userInstitutions, targetInstitutions) + 
        Math.min(userProjects, targetProjects)) / 4) * 100,
      100
    );

    // 计算总分
    const overall = Math.round(
      (skillsMatch * 0.25 + 
       goalsAlignment * 0.2 + 
       locationMatch * 0.15 + 
       networkOverlap * 0.15 + 
       availabilityMatch * 0.15 + 
       experienceMatch * 0.1)
    );

    return {
      overall,
      skillsMatch: Math.round(skillsMatch),
      goalsAlignment: Math.round(goalsAlignment),
      locationMatch: Math.round(locationMatch),
      networkOverlap: Math.round(networkOverlap),
      availabilityMatch: Math.round(availabilityMatch),
      experienceMatch: Math.round(experienceMatch)
    };
  }

  /**
   * 生成匹配解释（本地算法）
   */
  generateLocalMatchExplanation(
    userProfile: any,
    targetProfile: UserRecommendation,
    matchScore: MatchScore
  ): MatchExplanation {
    const reasons: string[] = [];
    const mutualBenefits: string[] = [];
    const potentialChallenges: string[] = [];

    // 基于匹配分数生成原因
    if (matchScore.skillsMatch > 70) {
      reasons.push(`Strong technical alignment with ${matchScore.skillsMatch}% skill overlap`);
      mutualBenefits.push('Complementary skills enable knowledge sharing and collaboration');
    } else if (matchScore.skillsMatch < 30) {
      potentialChallenges.push('Limited skill overlap may require additional coordination');
    }

    if (matchScore.goalsAlignment > 70) {
      reasons.push(`Aligned vision with ${matchScore.goalsAlignment}% goal compatibility`);
      mutualBenefits.push('Shared objectives create strong foundation for partnership');
    }

    if (matchScore.locationMatch > 80) {
      reasons.push('Geographic proximity enables in-person collaboration');
      mutualBenefits.push('Same timezone and local market knowledge');
    }

    if (matchScore.networkOverlap > 50) {
      reasons.push('Mutual connections provide trust and validation');
      mutualBenefits.push('Warm introductions and shared professional network');
    }

    if (targetProfile.responseRate && targetProfile.responseRate > 80) {
      reasons.push('High responsiveness indicates active engagement');
    }

    // 建议行动
    let suggestedAction = 'Send a connection request with personalized message';
    if (matchScore.overall > 85) {
      suggestedAction = 'Highly recommended - reach out immediately with detailed collaboration proposal';
    } else if (matchScore.overall < 60) {
      suggestedAction = 'Consider refining your search criteria for better matches';
    }

    return {
      reasons,
      mutualBenefits,
      potentialChallenges,
      suggestedAction
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

// 创建并导出匹配服务实例
export const matchingService = new MatchingService();

// 导出默认实例
export default matchingService; 