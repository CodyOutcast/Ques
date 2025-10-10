import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  UserProfile,
  ProfileSection,
  AISuggestion,
  AISuggestionType,
  GenerateAISuggestionsRequest,
  ApplyAISuggestionRequest
} from '../types/api';

class ProfileAIService {
  /**
   * 为指定部分生成AI润色建议
   */
  async generateSectionSuggestion(
    section: ProfileSection, 
    content: any, 
    options?: {
      type?: AISuggestionType;
      style?: 'professional' | 'casual' | 'academic' | 'creative';
      targetAudience?: 'general' | 'technical' | 'business' | 'academic';
      focusAreas?: string[];
    }
  ): Promise<ApiResponse<AISuggestion>> {
    try {
      const response = await httpClient.post<AISuggestion>(
        `${API_CONFIG.ENDPOINTS.PROFILE.AI_SUGGESTIONS}/section`,
        {
          section,
          content,
          ...options
        }
      );

      return response;
    } catch (error) {
      console.error('Failed to generate section suggestion:', error);
      // 如果API失败，返回本地生成的建议
      return {
        success: true,
        data: this.generateLocalSuggestion(section, content, options)
      };
    }
  }

  /**
   * 批量生成多个部分的AI建议
   */
  async generateBatchSuggestions(
    sections: Array<{ section: ProfileSection; content: any }>,
    options?: {
      style?: 'professional' | 'casual' | 'academic' | 'creative';
      targetAudience?: 'general' | 'technical' | 'business' | 'academic';
      priority?: 'speed' | 'quality';
    }
  ): Promise<ApiResponse<AISuggestion[]>> {
    try {
      const response = await httpClient.post<AISuggestion[]>(
        `${API_CONFIG.ENDPOINTS.PROFILE.AI_SUGGESTIONS}/batch`,
        {
          sections,
          ...options
        }
      );

      return response;
    } catch (error) {
      console.error('Failed to generate batch suggestions:', error);
      // 如果API失败，返回本地生成的建议
      const suggestions = sections.map(({ section, content }, index) => 
        this.generateLocalSuggestion(section, content, options, index)
      );
      
      return {
        success: true,
        data: suggestions
      };
    }
  }

  /**
   * 智能内容增强
   */
  async enhanceContent(
    section: ProfileSection,
    content: any,
    enhancementType: 'clarity' | 'professionalism' | 'engagement' | 'completeness' | 'conciseness'
  ): Promise<ApiResponse<{
    original: any;
    enhanced: any;
    improvements: Array<{
      type: string;
      description: string;
      impact: number; // 1-10
    }>;
    confidence: number;
  }>> {
    try {
      const response = await httpClient.post<{
        original: any;
        enhanced: any;
        improvements: Array<{
          type: string;
          description: string;
          impact: number;
        }>;
        confidence: number;
      }>(
        `${API_CONFIG.ENDPOINTS.PROFILE.AI_SUGGESTIONS}/enhance`,
        {
          section,
          content,
          enhancementType
        }
      );

      return response;
    } catch (error) {
      console.error('Failed to enhance content:', error);
      return this.getLocalEnhancement(section, content, enhancementType);
    }
  }

  /**
   * 内容质量分析
   */
  async analyzeContentQuality(
    section: ProfileSection,
    content: any
  ): Promise<ApiResponse<{
    overallScore: number; // 1-100
    dimensions: {
      clarity: number;
      professionalism: number;
      completeness: number;
      engagement: number;
      uniqueness: number;
    };
    suggestions: string[];
    strengths: string[];
    weaknesses: string[];
  }>> {
    try {
      const response = await httpClient.post<{
        overallScore: number;
        dimensions: {
          clarity: number;
          professionalism: number;
          completeness: number;
          engagement: number;
          uniqueness: number;
        };
        suggestions: string[];
        strengths: string[];
        weaknesses: string[];
      }>(
        `${API_CONFIG.ENDPOINTS.PROFILE.AI_SUGGESTIONS}/analyze-quality`,
        {
          section,
          content
        }
      );

      return response;
    } catch (error) {
      console.error('Failed to analyze content quality:', error);
      return this.getLocalQualityAnalysis(section, content);
    }
  }

  /**
   * 生成个性化写作建议
   */
  async getWritingTips(
    section: ProfileSection,
    userStyle?: 'technical' | 'business' | 'creative' | 'academic',
    industry?: string
  ): Promise<ApiResponse<{
    tips: Array<{
      category: string;
      title: string;
      description: string;
      example?: string;
      priority: 'high' | 'medium' | 'low';
    }>;
    templates: Array<{
      name: string;
      content: string;
      suitableFor: string[];
    }>;
    commonMistakes: string[];
  }>> {
    try {
      const searchParams = new URLSearchParams();
      if (section) searchParams.append('section', section);
      if (userStyle) searchParams.append('userStyle', userStyle);
      if (industry) searchParams.append('industry', industry);

      const url = `${API_CONFIG.ENDPOINTS.PROFILE.AI_SUGGESTIONS}/writing-tips${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<{
        tips: Array<{
          category: string;
          title: string;
          description: string;
          example?: string;
          priority: 'high' | 'medium' | 'low';
        }>;
        templates: Array<{
          name: string;
          content: string;
          suitableFor: string[];
        }>;
        commonMistakes: string[];
      }>(url);

      return response;
    } catch (error) {
      console.error('Failed to get writing tips:', error);
      return this.getLocalWritingTips(section, userStyle, industry);
    }
  }

  /**
   * 本地AI建议生成（备用方法）
   */
  private generateLocalSuggestion(
    section: ProfileSection,
    content: any,
    options?: any,
    index = 0
  ): AISuggestion {
    const baseId = `local_${section}_${Date.now()}_${index}`;
    
    switch (section) {
      case 'skills':
        return this.generateSkillsSuggestion(baseId, content);
      case 'resources':
        return this.generateResourcesSuggestion(baseId, content);
      case 'projects':
        return this.generateProjectsSuggestion(baseId, content);
      case 'goals':
        return this.generateGoalsSuggestion(baseId, content);
      case 'demands':
        return this.generateDemandsSuggestion(baseId, content);
      case 'basic-info':
        return this.generateBasicInfoSuggestion(baseId, content);
      default:
        return this.generateGenericSuggestion(baseId, section, content);
    }
  }

  private generateSkillsSuggestion(id: string, skills: string[]): AISuggestion {
    const enhancedSkills = skills.map(skill => {
      if (skill.toLowerCase().includes('python')) return 'Full-stack Python Development';
      if (skill.toLowerCase().includes('react')) return 'Modern React & TypeScript';
      if (skill.toLowerCase().includes('design')) return 'User-centered Product Design';
      if (skill.toLowerCase().includes('marketing')) return 'Growth-driven Digital Marketing';
      if (skill.toLowerCase().includes('ai') || skill.toLowerCase().includes('ml')) 
        return 'AI/ML Innovation & Implementation';
      return `Advanced ${skill}`;
    });

    return {
      id,
      section: 'skills',
      type: 'enhancement',
      priority: 'medium',
      title: 'Enhanced Skill Descriptions',
      description: 'Make your skills more specific and attractive with descriptive prefixes',
      originalContent: skills,
      suggestedContent: enhancedSkills,
      reasoning: [
        'More specific and attractive skill descriptions',
        'Highlight expertise level and impact',
        'Stand out in search results',
        'Attract higher-quality matches'
      ],
      impactScore: 75,
      confidence: 85,
      tags: ['professional', 'descriptive', 'marketable'],
      createdAt: new Date().toISOString()
    };
  }

  private generateProjectsSuggestion(id: string, projects: any[]): AISuggestion {
    if (!projects.length) {
      return {
        id,
        section: 'projects',
        type: 'addition',
        priority: 'high',
        title: 'Add Key Projects',
        description: 'Showcase your experience with 1-3 impactful projects',
        originalContent: projects,
        suggestedContent: [{
          title: 'Project Name (Your Role)',
          role: 'Lead Developer/Designer/Manager',
          description: 'Brief description highlighting your contributions, technologies used, and measurable impact or results achieved.',
          referenceLinks: ['https://github.com/username/project', 'https://project-demo.com']
        }],
        reasoning: [
          'Projects demonstrate practical experience',
          'Show your ability to execute ideas',
          'Provide concrete examples for discussions',
          'Help others understand your expertise level'
        ],
        impactScore: 90,
        confidence: 95,
        tags: ['essential', 'experience', 'credibility'],
        createdAt: new Date().toISOString()
      };
    }

    const enhancedProjects = projects.map(project => ({
      ...project,
      title: project.title.includes('(') ? project.title : `${project.title} (${project.role || 'Lead'})`,
      description: project.description + ' This project demonstrated strong problem-solving skills and resulted in measurable impact for users and stakeholders.'
    }));

    return {
      id,
      section: 'projects',
      type: 'enhancement',
      priority: 'medium',
      title: 'Enhanced Project Descriptions',
      description: 'Add role clarity and impact statements to showcase contributions',
      originalContent: projects,
      suggestedContent: enhancedProjects,
      reasoning: [
        'Added role clarity in project titles',
        'Emphasized impact and results',
        'Highlighted problem-solving abilities',
        'Made achievements more prominent'
      ],
      impactScore: 70,
      confidence: 80,
      tags: ['impact', 'clarity', 'achievements'],
      createdAt: new Date().toISOString()
    };
  }

  private generateGoalsSuggestion(id: string, goals: string[]): AISuggestion {
    if (!goals.length) {
      return {
        id,
        section: 'goals',
        type: 'addition',
        priority: 'high',
        title: 'Define Your Professional Goals',
        description: 'Help others understand what you\'re working toward',
        originalContent: goals,
        suggestedContent: [
          'Build innovative products that solve real-world problems',
          'Develop expertise in emerging technologies',
          'Lead cross-functional teams in dynamic environments',
          'Create meaningful impact through collaboration'
        ],
        reasoning: [
          'Goals help others understand your direction',
          'Attract like-minded collaborators',
          'Show ambition and forward thinking',
          'Enable better matching with opportunities'
        ],
        impactScore: 85,
        confidence: 90,
        tags: ['essential', 'direction', 'matching'],
        createdAt: new Date().toISOString()
      };
    }

    const improvedGoals = goals.map(goal => 
      goal.replace(/I want to/gi, 'Actively building towards')
          .replace(/I hope to/gi, 'Committed to achieving')
          .replace(/maybe/gi, 'strategically planning to')
          .replace(/I think/gi, 'I\'m focused on')
    ).join(' ') + ' Looking for like-minded collaborators who share this vision and can contribute complementary expertise.';

    return {
      id,
      section: 'goals',
      type: 'rewrite',
      priority: 'medium',
      title: 'More Confident Goal Expression',
      description: 'Use confident language and add call-to-action for collaborators',
      originalContent: goals,
      suggestedContent: [improvedGoals],
      reasoning: [
        'More confident and decisive language',
        'Clear call-to-action for potential collaborators',
        'Shows commitment and determination',
        'Encourages engagement from others'
      ],
      impactScore: 65,
      confidence: 75,
      tags: ['confidence', 'engagement', 'collaboration'],
      createdAt: new Date().toISOString()
    };
  }

  private generateResourcesSuggestion(id: string, resources: string[]): AISuggestion {
    const enhancedResources = resources.map(resource => {
      if (resource.toLowerCase().includes('mentorship')) return 'Expert mentorship & strategic guidance';
      if (resource.toLowerCase().includes('funding')) return 'Seed funding & investor connections';
      if (resource.toLowerCase().includes('network')) return 'Premium industry network access';
      if (resource.toLowerCase().includes('office')) return 'Co-working space & office facilities';
      return `Premium ${resource.toLowerCase()}`;
    });

    return {
      id,
      section: 'resources',
      type: 'enhancement',
      priority: 'medium',
      title: 'Enhanced Resource Descriptions',
      description: 'Emphasize value and exclusivity of your resources',
      originalContent: resources,
      suggestedContent: enhancedResources,
      reasoning: [
        'Enhanced descriptions emphasize value',
        'Highlight exclusivity and premium nature',
        'Make resources more attractive',
        'Better positioning for collaborations'
      ],
      impactScore: 70,
      confidence: 80,
      tags: ['value', 'premium', 'attractive'],
      createdAt: new Date().toISOString()
    };
  }

  private generateDemandsSuggestion(id: string, demands: string[]): AISuggestion {
    const enhancedDemands = demands.map(demand => {
      if (demand.toLowerCase().includes('co-founder')) return 'Technical co-founder with proven track record';
      if (demand.toLowerCase().includes('investor')) return 'Strategic investors & venture partners';
      if (demand.toLowerCase().includes('mentor')) return 'Industry mentor with scaling experience';
      if (demand.toLowerCase().includes('developer')) return 'Senior developer with startup experience';
      return `Experienced ${demand.toLowerCase()}`;
    });

    return {
      id,
      section: 'demands',
      type: 'enhancement',
      priority: 'medium',
      title: 'More Specific Requirements',
      description: 'Attract higher-quality matches with specific requirements',
      originalContent: demands,
      suggestedContent: enhancedDemands,
      reasoning: [
        'More specific requirements attract quality matches',
        'Set clear expectations upfront',
        'Reduce time spent on unsuitable connections',
        'Improve matching accuracy'
      ],
      impactScore: 75,
      confidence: 85,
      tags: ['specific', 'quality', 'matching'],
      createdAt: new Date().toISOString()
    };
  }

  private generateBasicInfoSuggestion(id: string, basicInfo: any): AISuggestion {
    const currentIntro = basicInfo.oneSentenceIntro || '';
    const improvedIntro = currentIntro || 
      'Passionate professional focused on innovation and meaningful collaboration.';

    return {
      id,
      section: 'basic-info',
      type: currentIntro ? 'enhancement' : 'addition',
      priority: currentIntro ? 'low' : 'high',
      title: currentIntro ? 'Enhanced Personal Introduction' : 'Add Personal Introduction',
      description: 'A compelling introduction makes your profile more engaging',
      originalContent: basicInfo,
      suggestedContent: {
        ...basicInfo,
        oneSentenceIntro: improvedIntro
      },
      reasoning: [
        'Personal introductions create immediate connection',
        'Shows personality beyond just skills and experience',
        'Helps others remember you',
        'Increases profile engagement'
      ],
      impactScore: currentIntro ? 60 : 80,
      confidence: 85,
      tags: ['personality', 'engagement', 'memorable'],
      createdAt: new Date().toISOString()
    };
  }

  private generateGenericSuggestion(id: string, section: ProfileSection, content: any): AISuggestion {
    return {
      id,
      section,
      type: 'enhancement',
      priority: 'low',
      title: `Improve ${section} Section`,
      description: 'Consider enhancing this section for better profile completeness',
      originalContent: content,
      suggestedContent: content,
      reasoning: ['Better profile completeness', 'Improved matching potential'],
      impactScore: 50,
      confidence: 60,
      tags: ['completeness'],
      createdAt: new Date().toISOString()
    };
  }

  /**
   * 本地内容增强（备用方法）
   */
  private getLocalEnhancement(
    section: ProfileSection,
    content: any,
    enhancementType: string
  ): ApiResponse<{
    original: any;
    enhanced: any;
    improvements: Array<{ type: string; description: string; impact: number }>;
    confidence: number;
  }> {
    // 简单的本地增强逻辑
    let enhanced = content;
    const improvements: Array<{ type: string; description: string; impact: number }> = [];

    if (enhancementType === 'professionalism' && typeof content === 'string') {
      enhanced = content.replace(/\b(good|nice|ok|fine)\b/gi, 'excellent')
                        .replace(/\b(work on|working on)\b/gi, 'developing')
                        .replace(/\b(help with)\b/gi, 'contribute to');
      improvements.push({
        type: 'vocabulary',
        description: 'Replaced casual words with professional alternatives',
        impact: 7
      });
    }

    return {
      success: true,
      data: {
        original: content,
        enhanced,
        improvements,
        confidence: 70
      }
    };
  }

  /**
   * 本地质量分析（备用方法）
   */
  private getLocalQualityAnalysis(section: ProfileSection, content: any): ApiResponse<{
    overallScore: number;
    dimensions: {
      clarity: number;
      professionalism: number;
      completeness: number;
      engagement: number;
      uniqueness: number;
    };
    suggestions: string[];
    strengths: string[];
    weaknesses: string[];
  }> {
    // 简单的本地分析逻辑
    const hasContent = content && (
      Array.isArray(content) ? content.length > 0 : 
      typeof content === 'object' ? Object.keys(content).length > 0 :
      content.toString().length > 0
    );

    const wordCount = typeof content === 'string' ? content.split(' ').length : 0;
    
    return {
      success: true,
      data: {
        overallScore: hasContent ? 70 : 30,
        dimensions: {
          clarity: hasContent ? 75 : 40,
          professionalism: hasContent ? 70 : 35,
          completeness: hasContent ? 80 : 20,
          engagement: wordCount > 20 ? 75 : 50,
          uniqueness: 65
        },
        suggestions: hasContent ? 
          ['Consider adding more specific details', 'Use action-oriented language'] :
          ['Add content to this section', 'Include relevant examples'],
        strengths: hasContent ? ['Section is not empty'] : [],
        weaknesses: hasContent ? [] : ['Section needs content']
      }
    };
  }

  /**
   * 本地写作建议（备用方法）
   */
  private getLocalWritingTips(
    section: ProfileSection,
    userStyle?: string,
    industry?: string
  ): ApiResponse<any> {
    const genericTips = {
      tips: [
        {
          category: 'General',
          title: 'Be Specific',
          description: 'Use concrete examples and specific details rather than general statements',
          priority: 'high' as const
        },
        {
          category: 'Language',
          title: 'Use Active Voice',
          description: 'Write in active voice to make your content more engaging and direct',
          example: 'Instead of "The project was completed by me", write "I completed the project"',
          priority: 'medium' as const
        }
      ],
      templates: [
        {
          name: 'Basic Template',
          content: 'Start with a strong opening statement, provide specific examples, and end with your goals or what you\'re seeking.',
          suitableFor: ['general']
        }
      ],
      commonMistakes: [
        'Being too vague or general',
        'Using passive voice extensively',
        'Not providing specific examples'
      ]
    };

    return {
      success: true,
      data: genericTips
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

// 创建并导出AI润色服务实例
export const profileAIService = new ProfileAIService();

// 导出默认实例
export default profileAIService; 