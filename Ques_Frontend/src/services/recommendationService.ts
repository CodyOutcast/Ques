import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import { swipeService } from './swipeService';
import type {
  ApiResponse,
  UserRecommendation,
  RecommendationRequest,
  MatchingCriteria,
  MatchScore,
  MatchExplanation,
  PaginatedResponse,
  SwipeAction,
  RecordSwipeRequest
} from '../types/api';

class RecommendationService {
  /**
   * 获取推荐用户列表
   */
  async getRecommendations(request: RecommendationRequest): Promise<ApiResponse<UserRecommendation[]>> {
    try {
      const response = await httpClient.post<UserRecommendation[]>(
        API_CONFIG.ENDPOINTS.RECOMMENDATIONS.GET_RECOMMENDATIONS,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to get recommendations:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取匹配用户
   */
  async getMatches(criteria: MatchingCriteria): Promise<ApiResponse<PaginatedResponse<UserRecommendation>>> {
    try {
      const response = await httpClient.post<PaginatedResponse<UserRecommendation>>(
        API_CONFIG.ENDPOINTS.RECOMMENDATIONS.GET_MATCHES,
        criteria
      );

      return response;
    } catch (error) {
      console.error('Failed to get matches:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新推荐偏好
   */
  async updatePreferences(preferences: MatchingCriteria): Promise<ApiResponse<MatchingCriteria>> {
    try {
      const response = await httpClient.put<MatchingCriteria>(
        API_CONFIG.ENDPOINTS.RECOMMENDATIONS.UPDATE_PREFERENCES,
        preferences
      );

      return response;
    } catch (error) {
      console.error('Failed to update preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取推荐偏好
   */
  async getPreferences(): Promise<ApiResponse<MatchingCriteria>> {
    try {
      const response = await httpClient.get<MatchingCriteria>(
        API_CONFIG.ENDPOINTS.RECOMMENDATIONS.GET_PREFERENCES
      );

      return response;
    } catch (error) {
      console.error('Failed to get preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 计算用户匹配分数
   */
  async calculateMatchScore(targetUserId: string, criteria?: MatchingCriteria): Promise<ApiResponse<MatchScore>> {
    try {
      const response = await httpClient.post<MatchScore>(
        `${API_CONFIG.ENDPOINTS.MATCHING.GET_MATCH_SCORE}/${targetUserId}`,
        criteria || {}
      );

      return response;
    } catch (error) {
      console.error('Failed to calculate match score:', error);
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
   * 智能推荐基于查询
   */
  async getIntelligentRecommendations(
    query: string,
    searchMode: 'inside' | 'global' = 'inside',
    userProfile?: any,
    excludeIds?: string[]
  ): Promise<UserRecommendation[]> {
    try {
      // 在实际应用中，这会调用后端API
      // 这里使用模拟数据进行开发
      return this.simulateIntelligentRecommendations(query, searchMode, userProfile, excludeIds);
    } catch (error) {
      console.error('Failed to get intelligent recommendations:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 模拟智能推荐（开发阶段使用）
   */
  private async simulateIntelligentRecommendations(
    query: string,
    searchMode: 'inside' | 'global',
    userProfile?: any,
    excludeIds?: string[]
  ): Promise<UserRecommendation[]> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));

    const allRecommendations = this.getMockRecommendations();
    const queryLower = query.toLowerCase();

    // 根据查询过滤推荐
    let filteredRecommendations = allRecommendations.filter(rec => {
      // 排除已添加的联系人
      if (excludeIds?.includes(rec.id)) return false;

      // 基于查询内容进行匹配
      if (queryLower.includes('co-founder') || queryLower.includes('startup')) {
        return rec.goals.some(goal => 
          goal.toLowerCase().includes('company') || 
          goal.toLowerCase().includes('startup') ||
          goal.toLowerCase().includes('founder')
        );
      }

      if (queryLower.includes('mentor')) {
        return rec.skills.length > 3 || rec.institutions.some(inst => inst.role.includes('Senior'));
      }

      if (queryLower.includes('investor')) {
        return rec.resources.some(res => 
          res.toLowerCase().includes('network') || 
          res.toLowerCase().includes('funding')
        );
      }

      if (queryLower.includes('python') || queryLower.includes('ai')) {
        return rec.skills.some(skill => 
          skill.toLowerCase().includes('python') ||
          skill.toLowerCase().includes('ai') ||
          skill.toLowerCase().includes('machine learning')
        );
      }

      return true; // 默认返回所有
    });

    // 生成个性化匹配解释
    filteredRecommendations = filteredRecommendations.map(rec => ({
      ...rec,
      whyMatch: this.generateMatchExplanation(rec, query, userProfile),
      matchScore: this.calculateSimulatedMatchScore(rec, query, userProfile)
    }));

    // 按匹配分数排序
    filteredRecommendations.sort((a, b) => b.matchScore - a.matchScore);

    return filteredRecommendations.slice(0, 5); // 返回前5个最佳匹配
  }

  /**
   * 生成匹配解释
   */
  private generateMatchExplanation(
    recommendation: UserRecommendation,
    query: string,
    userProfile?: any
  ): string {
    const userSkills = userProfile?.skills?.join(', ') || 'your skills';
    const userLocation = userProfile?.location || 'your location';
    const queryLower = query.toLowerCase();

    if (queryLower.includes('co-founder')) {
      return `Perfect co-founder match! 🚀 You bring ${userSkills} expertise while they offer ${recommendation.skills.slice(0, 2).join(' and ')} skills. Both seeking co-founders with complementary abilities in ${userLocation}.`;
    } else if (queryLower.includes('mentor')) {
      return `Excellent mentoring opportunity! 🎯 Their ${recommendation.skills[0]} expertise and ${recommendation.institutions[0]?.name} background make them ideal to guide your ${userSkills} development.`;
    } else if (queryLower.includes('investor')) {
      return `Strong investor alignment! 💰 Their investment focus matches your ${userSkills} sector, with proven track record in ${recommendation.projects[0]?.title} type ventures.`;
    } else if (queryLower.includes('ai') || queryLower.includes('python')) {
      const tech = queryLower.includes('ai') ? 'AI' : 'Python';
      return `Great technical synergy! 🤖 Shared ${tech} passion creates perfect collaboration potential. They need ${userSkills} while offering ${recommendation.skills[0]} expertise.`;
    } else {
      return `Strong mutual fit! 🤝 Complementary skills (${userSkills} + ${recommendation.skills[0]}), shared goals, and mutual interest in ${userLocation} collaboration opportunities.`;
    }
  }

  /**
   * 计算模拟匹配分数
   */
  private calculateSimulatedMatchScore(
    recommendation: UserRecommendation,
    query: string,
    userProfile?: any
  ): number {
    let score = 70; // 基础分数
    const queryLower = query.toLowerCase();

    // 基于查询类型调整分数
    if (queryLower.includes('co-founder') && 
        recommendation.goals.some(g => g.toLowerCase().includes('company'))) {
      score += 15;
    }

    if (queryLower.includes('python') && 
        recommendation.skills.some(s => s.toLowerCase().includes('python'))) {
      score += 20;
    }

    if (queryLower.includes('ai') && 
        recommendation.skills.some(s => s.toLowerCase().includes('machine learning'))) {
      score += 18;
    }

    // 基于位置匹配
    if (userProfile?.location && 
        recommendation.location.includes(userProfile.location.split(',')[0])) {
      score += 10;
    }

    // 基于大学匹配
    if (userProfile?.university?.name === recommendation.university?.name) {
      score += 12;
    }

    // 基于技能重叠
    if (userProfile?.skills) {
      const skillOverlap = userProfile.skills.filter((skill: string) => 
        recommendation.skills.some(s => s.toLowerCase().includes(skill.toLowerCase()))
      ).length;
      score += skillOverlap * 3;
    }

    // 确保分数在合理范围内
    return Math.min(Math.max(score + Math.random() * 10 - 5, 60), 98);
  }

  /**
   * 获取模拟推荐数据
   */
  private getMockRecommendations(): UserRecommendation[] {
    return [
      {
        id: '1',
        name: 'Sarah Chen',
        age: '24',
        gender: 'Female',
        avatar: '👩‍💻',
        location: 'Beijing, China',
        hobbies: ['Rock Climbing', 'Photography', 'Cooking'],
        languages: ['English', 'Mandarin'],
        skills: ['Python', 'Machine Learning', 'TensorFlow', 'Deep Learning', 'PyTorch'],
        resources: ['GPU Cluster Access', 'Research Lab', 'Datasets', 'ML Infrastructure'],
        projects: [
          {
            title: 'ML Ethics Framework',
            role: 'Lead Developer',
            description: 'Open-source framework for evaluating bias in ML models',
            referenceLinks: ['https://github.com/sarahchen/ml-ethics']
          }
        ],
        goals: ['Build ethical AI products', 'Start a tech company', 'Publish research papers'],
        demands: ['Co-founder with business experience', 'Funding connections', 'Industry mentorship'],
        institutions: [
          {
            name: 'Tsinghua University',
            role: 'PhD Student - Computer Science',
            description: 'Research focus on ethical AI and machine learning safety',
            verified: true
          }
        ],
        university: {
          name: 'Tsinghua University',
          verified: true
        },
        matchScore: 95,
        bio: 'AI researcher passionate about ethical machine learning and startup innovation.',
        oneSentenceIntro: 'I build AI systems that solve real-world problems while keeping humans at the center.',
        whyMatch: '',
        receivesLeft: 5,
        isOnline: true,
        mutualConnections: 3,
        responseRate: 85
      },
      {
        id: '2',
        name: 'Alex Kumar',
        age: '29',
        gender: 'Male',
        avatar: '👨‍💼',
        location: 'Shanghai, China',
        hobbies: ['Chess', 'Travel', 'Wine Tasting'],
        languages: ['English', 'Hindi', 'Mandarin'],
        skills: ['Product Management', 'Startup Scaling', 'Design Thinking', 'Growth Hacking'],
        resources: ['VC Network', 'Mentor Network', 'Marketing Channels', 'International Connections'],
        projects: [
          {
            title: 'EdTech Platform',
            role: 'Co-founder & CEO',
            description: 'Built and scaled online learning platform to $10M ARR',
            referenceLinks: []
          }
        ],
        goals: ['Scale next startup to $100M', 'Expand to global markets', 'Build category-defining product'],
        demands: ['Technical co-founder', 'Engineering team', 'Series A funding'],
        institutions: [
          {
            name: 'Alibaba Group',
            role: 'Former Product Director',
            description: 'Led product strategy for cloud computing division',
            verified: true
          }
        ],
        university: {
          name: 'Shanghai Jiao Tong University',
          verified: true
        },
        matchScore: 88,
        bio: 'Serial entrepreneur with 3 successful exits, expert in scaling products.',
        oneSentenceIntro: 'I turn technical innovations into market-winning products that users love.',
        whyMatch: '',
        receivesLeft: 3,
        isOnline: false,
        lastSeen: '2 hours ago',
        mutualConnections: 7,
        responseRate: 92
      },
      {
        id: '3',
        name: 'Maria Rodriguez',
        age: '26',
        gender: 'Female',
        avatar: '👩‍🔬',
        location: 'Guangzhou, China',
        hobbies: ['Hiking', 'Reading', 'Volunteer Work'],
        languages: ['Spanish', 'English', 'Portuguese'],
        skills: ['Data Science', 'Python', 'Research', 'Statistical Analysis', 'R'],
        resources: ['Research Database Access', 'Academic Network', 'Grant Writing'],
        projects: [
          {
            title: 'Bias Detection Framework',
            role: 'Research Lead',
            description: 'Academic research on detecting and mitigating AI bias',
            referenceLinks: []
          }
        ],
        goals: ['Commercialize research', 'Impact healthcare with AI', 'Build diverse tech team'],
        demands: ['Business development partner', 'Healthcare industry connections'],
        institutions: [
          {
            name: 'Sun Yat-sen University',
            role: 'Postdoc Researcher',
            description: 'Research in AI ethics and fairness in machine learning',
            verified: true
          }
        ],
        university: {
          name: 'Sun Yat-sen University',
          verified: true
        },
        matchScore: 82,
        bio: 'Data scientist passionate about AI ethics and open source contributions.',
        oneSentenceIntro: 'I use data science to solve real-world problems with ethical AI.',
        whyMatch: '',
        receivesLeft: 8,
        isOnline: true,
        mutualConnections: 2,
        responseRate: 78
      }
    ];
  }

  /**
   * 获取推荐的建议查询
   */
  getSuggestedQueries(): string[] {
    return [
      "Find me a Python co-founder",
      "Connect me with AI researchers", 
      "Looking for startup mentors",
      "Need investors for tech startup",
      "Find design collaborators",
      "Connect with product managers",
      "Looking for blockchain developers",
      "Need marketing co-founder"
    ];
  }

  /**
   * 处理卡片滑动行为 - 右滑（喜欢）
   */
  async handleCardLike(
    recommendation: UserRecommendation,
    context?: {
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
      sessionId?: string;
      cardPosition?: number;
    }
  ): Promise<void> {
    try {
      const swipeRequest: RecordSwipeRequest = {
        targetUserId: recommendation.id,
        action: 'like',
        searchQuery: context?.searchQuery,
        searchMode: context?.searchMode || 'inside',
        matchScore: recommendation.matchScore,
        sourceContext: {
          sessionId: context?.sessionId,
          cardPosition: context?.cardPosition,
        }
      };

      // 记录滑动行为
      await swipeService.recordSwipe(swipeRequest);

      console.log(`Liked user: ${recommendation.name} (ID: ${recommendation.id})`);
    } catch (error) {
      console.error('Failed to record like:', error);
      // 如果网络失败，添加到本地缓存
      swipeService.addToLocalCache({
        targetUserId: recommendation.id,
        action: 'like',
        searchQuery: context?.searchQuery,
        searchMode: context?.searchMode || 'inside',
        matchScore: recommendation.matchScore,
        sourceContext: {
          sessionId: context?.sessionId,
          cardPosition: context?.cardPosition,
        }
      });
    }
  }

  /**
   * 处理卡片滑动行为 - 左滑（忽略）
   */
  async handleCardIgnore(
    recommendation: UserRecommendation,
    context?: {
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
      sessionId?: string;
      cardPosition?: number;
    }
  ): Promise<void> {
    try {
      const swipeRequest: RecordSwipeRequest = {
        targetUserId: recommendation.id,
        action: 'ignore',
        searchQuery: context?.searchQuery,
        searchMode: context?.searchMode || 'inside',
        matchScore: recommendation.matchScore,
        sourceContext: {
          sessionId: context?.sessionId,
          cardPosition: context?.cardPosition,
        }
      };

      // 记录滑动行为
      await swipeService.recordSwipe(swipeRequest);

      console.log(`Ignored user: ${recommendation.name} (ID: ${recommendation.id})`);
    } catch (error) {
      console.error('Failed to record ignore:', error);
      // 如果网络失败，添加到本地缓存
      swipeService.addToLocalCache({
        targetUserId: recommendation.id,
        action: 'ignore',
        searchQuery: context?.searchQuery,
        searchMode: context?.searchMode || 'inside',
        matchScore: recommendation.matchScore,
        sourceContext: {
          sessionId: context?.sessionId,
          cardPosition: context?.cardPosition,
        }
      });
    }
  }

  /**
   * 处理超级喜欢
   */
  async handleCardSuperLike(
    recommendation: UserRecommendation,
    context?: {
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
      sessionId?: string;
      cardPosition?: number;
    }
  ): Promise<void> {
    try {
      const swipeRequest: RecordSwipeRequest = {
        targetUserId: recommendation.id,
        action: 'super_like',
        searchQuery: context?.searchQuery,
        searchMode: context?.searchMode || 'inside',
        matchScore: recommendation.matchScore,
        sourceContext: {
          sessionId: context?.sessionId,
          cardPosition: context?.cardPosition,
        }
      };

      // 记录滑动行为
      await swipeService.recordSwipe(swipeRequest);

      console.log(`Super liked user: ${recommendation.name} (ID: ${recommendation.id})`);
    } catch (error) {
      console.error('Failed to record super like:', error);
      // 如果网络失败，添加到本地缓存
      swipeService.addToLocalCache({
        targetUserId: recommendation.id,
        action: 'super_like',
        searchQuery: context?.searchQuery,
        searchMode: context?.searchMode || 'inside',
        matchScore: recommendation.matchScore,
        sourceContext: {
          sessionId: context?.sessionId,
          cardPosition: context?.cardPosition,
        }
      });
    }
  }

  /**
   * 批量处理滑动行为（用于快速滑动场景）
   */
  async handleBatchSwipes(swipes: Array<{
    recommendation: UserRecommendation;
    action: SwipeAction;
    context?: {
      searchQuery?: string;
      searchMode?: 'inside' | 'global';
      sessionId?: string;
      cardPosition?: number;
    };
  }>): Promise<void> {
    try {
      const swipeRequests: RecordSwipeRequest[] = swipes.map(swipe => ({
        targetUserId: swipe.recommendation.id,
        action: swipe.action,
        searchQuery: swipe.context?.searchQuery,
        searchMode: swipe.context?.searchMode || 'inside',
        matchScore: swipe.recommendation.matchScore,
        sourceContext: {
          sessionId: swipe.context?.sessionId,
          cardPosition: swipe.context?.cardPosition,
        }
      }));

      await swipeService.recordSwipeBatch(swipeRequests);

      console.log(`Batch recorded ${swipes.length} swipe actions`);
    } catch (error) {
      console.error('Failed to record batch swipes:', error);
      // 如果网络失败，逐个添加到本地缓存
      swipes.forEach(swipe => {
        swipeService.addToLocalCache({
          targetUserId: swipe.recommendation.id,
          action: swipe.action,
          searchQuery: swipe.context?.searchQuery,
          searchMode: swipe.context?.searchMode || 'inside',
          matchScore: swipe.recommendation.matchScore,
          sourceContext: {
            sessionId: swipe.context?.sessionId,
            cardPosition: swipe.context?.cardPosition,
          }
        });
      });
    }
  }

  /**
   * 获取基于滑动历史的个性化推荐
   */
  async getPersonalizedRecommendations(params?: {
    excludeContacted?: boolean;
    limit?: number;
    includeSimilarToLiked?: boolean;
  }): Promise<ApiResponse<UserRecommendation[]>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.excludeContacted !== undefined) {
        searchParams.append('excludeContacted', params.excludeContacted.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.includeSimilarToLiked !== undefined) {
        searchParams.append('includeSimilarToLiked', params.includeSimilarToLiked.toString());
      }

      const url = `${API_CONFIG.ENDPOINTS.RECOMMENDATIONS.GET_RECOMMENDATIONS}/personalized${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<UserRecommendation[]>(url);

      return response;
    } catch (error) {
      console.error('Failed to get personalized recommendations:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 同步本地滑动缓存
   */
  async syncSwipeCache(): Promise<void> {
    try {
      await swipeService.syncLocalCache();
    } catch (error) {
      console.error('Failed to sync swipe cache:', error);
    }
  }

  /**
   * 验证推荐请求
   */
  validateRecommendationRequest(request: RecommendationRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (request.limit && (request.limit < 1 || request.limit > 50)) {
      errors.push('Limit must be between 1 and 50');
    }

    if (request.offset && request.offset < 0) {
      errors.push('Offset must be non-negative');
    }

    if (request.query && request.query.length > 200) {
      errors.push('Query is too long (maximum 200 characters)');
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

// 创建并导出推荐服务实例
export const recommendationService = new RecommendationService();

// 导出默认实例
export default recommendationService; 