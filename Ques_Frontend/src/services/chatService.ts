import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  ChatMessage,
  ChatSession,
  ChatRequest,
  ChatResponse,
  UserRecommendation,
  PaginatedResponse,
  StreamChunk,
  ChatStreamResponse,
  StreamCallbacks
} from '../types/api';

class ChatService {
  /**
   * 发送聊天消息
   */
  async sendMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    try {
      const response = await httpClient.post<ChatResponse>(
        API_CONFIG.ENDPOINTS.CHAT.SEND_MESSAGE,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 创建新的聊天会话
   */
  async createSession(): Promise<ApiResponse<ChatSession>> {
    try {
      const response = await httpClient.post<ChatSession>(
        API_CONFIG.ENDPOINTS.CHAT.CREATE_SESSION
      );

      return response;
    } catch (error) {
      console.error('Failed to create chat session:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取聊天会话详情
   */
  async getSession(sessionId: string): Promise<ApiResponse<ChatSession>> {
    try {
      const response = await httpClient.get<ChatSession>(
        `${API_CONFIG.ENDPOINTS.CHAT.GET_SESSION}/${sessionId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to get chat session:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取聊天历史记录
   */
  async getChatHistory(params?: {
    page?: number;
    limit?: number;
    sessionId?: string;
  }): Promise<ApiResponse<PaginatedResponse<ChatSession>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.sessionId) {
        searchParams.append('sessionId', params.sessionId);
      }

      const url = `${API_CONFIG.ENDPOINTS.CHAT.GET_HISTORY}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<ChatSession>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get chat history:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除聊天会话
   */
  async deleteSession(sessionId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.delete<void>(
        `${API_CONFIG.ENDPOINTS.CHAT.DELETE_SESSION}/${sessionId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to delete chat session:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 生成推荐用户的匹配解释
   */
  generateMatchExplanation(
    recommendation: UserRecommendation,
    userQuery: string,
    userProfile?: any
  ): string {
    const userSkills = userProfile?.skills?.join(', ') || 'technical skills';
    const userLocation = userProfile?.location || 'your location';
    const userGoals = userProfile?.goals || [];

    // 根据查询类型生成个性化解释
    const queryLower = userQuery.toLowerCase();
    
    if (queryLower.includes('co-founder')) {
      return `Perfect mutual match! ✨ You offer the ${userSkills} they need for their next venture, while they bring ${recommendation.skills.slice(0, 2).join(' and ')} expertise you're seeking. Both actively looking for co-founders with complementary skills.`;
    } else if (queryLower.includes('mentor')) {
      return `Excellent mentoring match! 🎯 They're looking to mentor someone with your ${userSkills} background, while you gain from their ${recommendation.skills[0]} expertise. Your goals align with their mentoring focus.`;
    } else if (queryLower.includes('investor')) {
      return `Strong investor-founder fit! 💰 Your ${userSkills} expertise matches their investment thesis, while their portfolio experience aligns with your sector. Mutual interest in ${userLocation} market.`;
    } else if (queryLower.includes('ai') || queryLower.includes('python')) {
      return `Great technical match! 🤖 Your shared interest in ${queryLower.includes('ai') ? 'AI' : 'Python'} creates strong collaboration potential. They have ${recommendation.skills[0]} skills that complement your background perfectly.`;
    } else {
      return `Great bidirectional match! 🤝 You complement each other's skills (your ${userSkills} + their ${recommendation.skills[0]}), share similar goals, and they're also looking for someone with your background in ${userLocation}.`;
    }
  }

  /**
   * 模拟AI响应（开发阶段使用）
   */
  async simulateAIResponse(
    message: string,
    searchMode: 'inside' | 'global' = 'inside',
    userProfile?: any
  ): Promise<ChatResponse> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1500));

    const responses = [
      "I'll help you find the perfect connections! Can you tell me more about what kind of collaboration you're looking for?",
      "Great! Let me search for people who match your criteria. This might take a moment...",
      "Based on your profile and request, I found some excellent matches. Here are the top recommendations:",
      "Would you like me to refine these results or search for different criteria?"
    ];

    let aiResponse = responses[Math.floor(Math.random() * responses.length)];
    let recommendations: UserRecommendation[] = [];

    // 基于消息内容生成推荐
    const messageLower = message.toLowerCase();
    
    if (messageLower.includes('co-founder') || 
        messageLower.includes('startup') ||
        messageLower.includes('python') ||
        messageLower.includes('ai')) {
      
      // 模拟推荐数据
      recommendations = this.getMockRecommendations().map(rec => ({
        ...rec,
        whyMatch: this.generateMatchExplanation(rec, message, userProfile)
      }));

      if (recommendations.length > 0) {
        aiResponse = "I found some excellent matches for you! Let me show them in an interactive format...";
      } else {
        aiResponse = "I couldn't find any matches for your specific criteria. Try broadening your search or changing your requirements.";
      }
    }

    const chatMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      type: 'ai',
      content: aiResponse,
      timestamp: new Date().toISOString(),
      metadata: {
        query: message,
        searchMode,
        recommendations
      }
    };

    return {
      message: chatMessage,
      sessionId: `session_${Date.now()}`,
      recommendations,
      suggestedQueries: this.getSuggestedQueries(message)
    };
  }

  /**
   * 获取建议查询
   */
  private getSuggestedQueries(currentMessage: string): string[] {
    const suggestions = [
      "Find me a Python co-founder",
      "Connect me with AI researchers", 
      "Looking for startup mentors",
      "Need investors for tech startup",
      "Find design collaborators",
      "Connect with product managers"
    ];

    // 过滤掉与当前消息相似的建议
    return suggestions
      .filter(suggestion => 
        !suggestion.toLowerCase().includes(currentMessage.toLowerCase().split(' ')[0])
      )
      .slice(0, 4);
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
        languages: ['English', 'Mandarin', 'Python'],
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
        bio: 'AI researcher passionate about ethical machine learning and startup innovation. PhD in Computer Science with 5 years of industry experience at Google AI.',
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
        skills: ['Product Management', 'Startup Scaling', 'Design Thinking', 'Growth Hacking', 'UX Strategy'],
        resources: ['VC Network', 'Mentor Network', 'Marketing Channels', 'International Connections'],
        projects: [
          {
            title: 'EdTech Platform',
            role: 'Co-founder & CEO',
            description: 'Built and scaled online learning platform to $10M ARR',
            referenceLinks: ['https://techcrunch.com/alex-kumar-edtech']
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
        bio: 'Serial entrepreneur with 3 successful exits, now mentoring and building. Former Product Director at Alibaba, expert in scaling 0-to-1 products.',
        oneSentenceIntro: 'I turn technical innovations into market-winning products that users love.',
        whyMatch: '',
        receivesLeft: 3,
        isOnline: false,
        lastSeen: '2 hours ago',
        mutualConnections: 7,
        responseRate: 92
      }
    ];
  }

  /**
   * 验证消息内容
   */
  validateMessage(message: string): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!message || !message.trim()) {
      errors.push('Message cannot be empty');
    }

    if (message.length > 1000) {
      errors.push('Message is too long (maximum 1000 characters)');
    }

    // 检查敏感内容（基本过滤）
    const sensitiveWords = ['spam', 'scam', 'fraud'];
    const messageLower = message.toLowerCase();
    
    if (sensitiveWords.some(word => messageLower.includes(word))) {
      errors.push('Message contains inappropriate content');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 格式化聊天消息
   */
  formatMessage(message: ChatMessage): {
    displayContent: string;
    timestamp: string;
    hasRecommendations: boolean;
  } {
    return {
      displayContent: message.content,
      timestamp: new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      }).format(new Date(message.timestamp)),
      hasRecommendations: !!(message.metadata?.recommendations?.length)
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

  /**
   * 发送消息并获取流式响应（同时处理思考流和结果流）
   */
  async sendMessageStream(
    request: ChatRequest,
    callbacks: StreamCallbacks
  ): Promise<void> {
    try {
      const streamResponse: ChatStreamResponse = {
        thinking: '',
        result: '',
        recommendations: [],
        suggestedQueries: [],
        isDone: false
      };

      await httpClient.stream(
        API_CONFIG.ENDPOINTS.CHAT.SEND_MESSAGE + '/stream',
        request,
        (chunk: StreamChunk) => {
          try {
            switch (chunk.type) {
              case 'thinking':
                if (chunk.content) {
                  streamResponse.thinking += chunk.content;
                  callbacks.onThinkingChunk?.(
                    chunk.content,
                    streamResponse.thinking
                  );
                }
                break;

              case 'result':
                if (chunk.content) {
                  streamResponse.result += chunk.content;
                  callbacks.onResultChunk?.(
                    chunk.content,
                    streamResponse.result
                  );
                }
                break;

              case 'done':
                streamResponse.isDone = true;
                if (chunk.data) {
                  if (chunk.data.recommendations) {
                    streamResponse.recommendations = chunk.data.recommendations;
                    callbacks.onRecommendations?.(chunk.data.recommendations);
                  }
                  if (chunk.data.suggestedQueries) {
                    streamResponse.suggestedQueries = chunk.data.suggestedQueries;
                  }
                  if (chunk.data.sessionId) {
                    streamResponse.sessionId = chunk.data.sessionId;
                  }
                }
                callbacks.onComplete?.(streamResponse);
                break;

              case 'error':
                throw new ApiError(chunk.content || 'Stream error');

              default:
                console.warn('Unknown chunk type:', chunk.type);
            }
          } catch (error) {
            console.error('Error processing chunk:', error);
            callbacks.onError?.(error as Error);
          }
        }
      );
    } catch (error) {
      console.error('Failed to send message with stream:', error);
      callbacks.onError?.(this.handleError(error));
      throw this.handleError(error);
    }
  }

  /**
   * 模拟流式AI响应（开发阶段使用）
   * 模拟思考流和结果流
   */
  async simulateStreamResponse(
    message: string,
    callbacks: StreamCallbacks,
    searchMode: 'inside' | 'global' = 'inside',
    userProfile?: any
  ): Promise<void> {
    const streamResponse: ChatStreamResponse = {
      thinking: '',
      result: '',
      recommendations: [],
      suggestedQueries: [],
      isDone: false
    };

    try {
      // 判断是否需要思考流
      const needsThinking = message.toLowerCase().includes('co-founder') || 
                          message.toLowerCase().includes('startup') ||
                          message.toLowerCase().includes('python') ||
                          message.toLowerCase().includes('ai');

      // 第一阶段：思考流（如果需要）
      if (needsThinking) {
        const thinkingSteps = [
          '正在分析你的查询...',
          '检查用户资料匹配度...',
          '筛选符合条件的候选人...',
          '计算匹配分数...',
          '生成个性化推荐理由...'
        ];

        for (let i = 0; i < thinkingSteps.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));
          const thinkingChunk = thinkingSteps[i] + '\n';
          streamResponse.thinking += thinkingChunk;
          callbacks.onThinkingChunk?.(thinkingChunk, streamResponse.thinking);
        }

        // 思考完成后稍作停顿
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // 第二阶段：结果流
      const resultText = needsThinking
        ? '我找到了一些非常匹配的候选人！让我为你展示他们的资料...'
        : '让我帮你搜索一下相关的人选...';

      const words = resultText.split('');
      for (const word of words) {
        await new Promise(resolve => setTimeout(resolve, 30 + Math.random() * 20));
        streamResponse.result += word;
        callbacks.onResultChunk?.(word, streamResponse.result);
      }

      // 第三阶段：返回推荐结果（如果有）
      if (needsThinking) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const recommendations = this.getMockRecommendations().map(rec => ({
          ...rec,
          whyMatch: this.generateMatchExplanation(rec, message, userProfile)
        }));

        streamResponse.recommendations = recommendations;
        streamResponse.suggestedQueries = this.getSuggestedQueries(message);
        streamResponse.sessionId = `session_${Date.now()}`;

        callbacks.onRecommendations?.(recommendations);
      }

      // 完成
      streamResponse.isDone = true;
      callbacks.onComplete?.(streamResponse);

    } catch (error) {
      console.error('Simulation error:', error);
      callbacks.onError?.(error as Error);
    }
  }
}

// 创建并导出聊天服务实例
export const chatService = new ChatService();

// 导出默认实例
export default chatService; 