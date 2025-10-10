import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  UserProfile,
  ProjectInfo,
  InstitutionInfo,
  FileUploadResponse,
  ProfileSection,
  UpdateProfileSectionRequest,
  ProfileCompleteness,
  AISuggestion,
  GenerateAISuggestionsRequest,
  ApplyAISuggestionRequest,
  BatchProfileUpdateRequest,
  ProfileAnalysis,
  ProfileStats,
  PhotoUploadRequest,
  PhotoUploadResponse
} from '../types/api';

class ProfileService {
  /**
   * 获取用户资料
   */
  async getProfile(): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.get<UserProfile>(
        API_CONFIG.ENDPOINTS.PROFILE.GET
      );
    } catch (error) {
      console.error('Failed to get profile:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新用户资料
   */
  async updateProfile(profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.put<UserProfile>(
        API_CONFIG.ENDPOINTS.PROFILE.UPDATE,
        profile
      );
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新基本信息
   */
  async updateDemographics(demographics: UserProfile['demographics']): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.patch<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/demographics`,
        { demographics }
      );
    } catch (error) {
      console.error('Failed to update demographics:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新技能列表
   */
  async updateSkills(skills: string[]): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.patch<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/skills`,
        { skills }
      );
    } catch (error) {
      console.error('Failed to update skills:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新资源列表
   */
  async updateResources(resources: string[]): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.patch<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/resources`,
        { resources }
      );
    } catch (error) {
      console.error('Failed to update resources:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 添加项目
   */
  async addProject(project: ProjectInfo): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.post<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/projects`,
        { project }
      );
    } catch (error) {
      console.error('Failed to add project:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新项目
   */
  async updateProject(projectId: string, project: Partial<ProjectInfo>): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.put<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/projects/${projectId}`,
        { project }
      );
    } catch (error) {
      console.error('Failed to update project:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除项目
   */
  async deleteProject(projectId: string): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.delete<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/projects/${projectId}`
      );
    } catch (error) {
      console.error('Failed to delete project:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新目标列表
   */
  async updateGoals(goals: string[]): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.patch<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/goals`,
        { goals }
      );
    } catch (error) {
      console.error('Failed to update goals:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新需求列表
   */
  async updateDemands(demands: string[]): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.patch<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/demands`,
        { demands }
      );
    } catch (error) {
      console.error('Failed to update demands:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 添加机构经历
   */
  async addInstitution(institution: InstitutionInfo): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.post<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/institutions`,
        { institution }
      );
    } catch (error) {
      console.error('Failed to add institution:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新机构经历
   */
  async updateInstitution(institutionId: string, institution: Partial<InstitutionInfo>): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.put<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/institutions/${institutionId}`,
        { institution }
      );
    } catch (error) {
      console.error('Failed to update institution:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 删除机构经历
   */
  async deleteInstitution(institutionId: string): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.delete<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/institutions/${institutionId}`
      );
    } catch (error) {
      console.error('Failed to delete institution:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 上传头像
   */
  async uploadAvatar(file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<FileUploadResponse>> {
    try {
      const formData = new FormData();
      formData.append('avatar', file);

      return await httpClient.upload<FileUploadResponse>(
        API_CONFIG.ENDPOINTS.PROFILE.UPLOAD_AVATAR,
        formData,
        onProgress
      );
    } catch (error) {
      console.error('Avatar upload failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 上传文件（通用）
   */
  async uploadFile(file: File, type: 'image' | 'document' = 'image', onProgress?: (progress: number) => void): Promise<ApiResponse<FileUploadResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const endpoint = type === 'image' ? 
        API_CONFIG.ENDPOINTS.UPLOAD.IMAGE : 
        API_CONFIG.ENDPOINTS.UPLOAD.FILE;

      return await httpClient.upload<FileUploadResponse>(
        endpoint,
        formData,
        onProgress
      );
    } catch (error) {
      console.error('File upload failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证资料完整性
   */
  async validateProfile(profile: UserProfile): Promise<{
    isValid: boolean;
    errors: string[];
    warnings: string[];
  }> {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 检查必填项
    if (!profile.demographics?.name?.trim()) {
      errors.push('Name is required');
    }

    if (!profile.demographics?.age?.trim()) {
      errors.push('Age is required');
    }

    if (!profile.demographics?.gender) {
      errors.push('Gender is required');
    }

    if (!profile.demographics?.location?.trim()) {
      errors.push('Location is required');
    }

    // 检查推荐项
    if (!profile.skills?.length) {
      warnings.push('Adding skills can help with better matching');
    }

    if (!profile.goals?.length) {
      warnings.push('Adding goals can help others understand what you\'re looking for');
    }

    if (!profile.demographics?.oneSentenceIntro?.trim()) {
      warnings.push('Adding an introduction can make your profile more engaging');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * 批量更新资料
   */
  async batchUpdateProfile(updates: {
    demographics?: Partial<UserProfile['demographics']>;
    skills?: string[];
    resources?: string[];
    goals?: string[];
    demands?: string[];
    projects?: ProjectInfo[];
    institutions?: InstitutionInfo[];
  }): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.patch<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE}/batch`,
        updates
      );
    } catch (error) {
      console.error('Failed to batch update profile:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 更新资料的指定部分
   */
  async updateProfileSection(request: UpdateProfileSectionRequest): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.put<UserProfile>(
        API_CONFIG.ENDPOINTS.PROFILE.UPDATE_SECTION,
        request
      );
    } catch (error) {
      console.error('Failed to update profile section:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取资料完整度分析
   */
  async getProfileCompleteness(): Promise<ApiResponse<ProfileCompleteness>> {
    try {
      return await httpClient.get<ProfileCompleteness>(
        API_CONFIG.ENDPOINTS.PROFILE.GET_COMPLETENESS
      );
    } catch (error) {
      console.error('Failed to get profile completeness:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 生成AI改进建议
   */
  async generateAISuggestions(request?: GenerateAISuggestionsRequest): Promise<ApiResponse<AISuggestion[]>> {
    try {
      return await httpClient.post<AISuggestion[]>(
        API_CONFIG.ENDPOINTS.PROFILE.AI_SUGGESTIONS,
        request || {}
      );
    } catch (error) {
      console.error('Failed to generate AI suggestions:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 应用AI改进建议
   */
  async applyAISuggestion(request: ApplyAISuggestionRequest): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.post<UserProfile>(
        API_CONFIG.ENDPOINTS.PROFILE.APPLY_AI_SUGGESTION,
        request
      );
    } catch (error) {
      console.error('Failed to apply AI suggestion:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 批量应用AI建议
   */
  async batchApplyAISuggestions(suggestionIds: string[]): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.post<UserProfile>(
        `${API_CONFIG.ENDPOINTS.PROFILE.APPLY_AI_SUGGESTION}/batch`,
        { suggestionIds }
      );
    } catch (error) {
      console.error('Failed to batch apply AI suggestions:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取资料分析报告
   */
  async analyzeProfile(): Promise<ApiResponse<ProfileAnalysis>> {
    try {
      return await httpClient.get<ProfileAnalysis>(
        API_CONFIG.ENDPOINTS.PROFILE.ANALYZE_PROFILE
      );
    } catch (error) {
      console.error('Failed to analyze profile:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取资料统计数据
   */
  async getProfileStats(): Promise<ApiResponse<ProfileStats>> {
    try {
      return await httpClient.get<ProfileStats>(
        API_CONFIG.ENDPOINTS.PROFILE.GET_PROFILE_STATS
      );
    } catch (error) {
      console.error('Failed to get profile stats:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 高级照片上传（包含AI分析）
   */
  async uploadPhoto(request: PhotoUploadRequest, onProgress?: (progress: number) => void): Promise<ApiResponse<PhotoUploadResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', request.file);
      formData.append('type', request.type);
      
      if (request.cropData) {
        formData.append('cropData', JSON.stringify(request.cropData));
      }
      
      if (request.quality) {
        formData.append('quality', request.quality);
      }
      
      if (request.autoEnhance !== undefined) {
        formData.append('autoEnhance', request.autoEnhance.toString());
      }

      return await httpClient.upload<PhotoUploadResponse>(
        API_CONFIG.ENDPOINTS.PROFILE.UPLOAD_PHOTO,
        formData,
        onProgress
      );
    } catch (error) {
      console.error('Photo upload failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 批量更新资料（增强版）
   */
  async batchUpdateProfileEnhanced(request: BatchProfileUpdateRequest): Promise<ApiResponse<UserProfile>> {
    try {
      return await httpClient.post<UserProfile>(
        API_CONFIG.ENDPOINTS.PROFILE.BATCH_UPDATE,
        request
      );
    } catch (error) {
      console.error('Failed to batch update profile (enhanced):', error);
      throw this.handleError(error);
    }
  }

  /**
   * 生成个人简介
   */
  async generateBio(params?: {
    style?: 'professional' | 'casual' | 'academic' | 'creative';
    length?: 'short' | 'medium' | 'long';
    includeSkills?: boolean;
    includeGoals?: boolean;
    includeExperience?: boolean;
  }): Promise<ApiResponse<{ 
    original?: string;
    generated: string; 
    alternatives: string[];
    reasoning: string[];
  }>> {
    try {
      return await httpClient.post<{ 
        original?: string;
        generated: string; 
        alternatives: string[];
        reasoning: string[];
      }>(
        API_CONFIG.ENDPOINTS.PROFILE.GENERATE_BIO,
        params || {}
      );
    } catch (error) {
      console.error('Failed to generate bio:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证资料部分的内容
   */
  async validateProfileSection(section: ProfileSection, data: any): Promise<{
    isValid: boolean;
    errors: string[];
    warnings: string[];
    suggestions: string[];
  }> {
    try {
      const response = await httpClient.post<{
        isValid: boolean;
        errors: string[];
        warnings: string[];
        suggestions: string[];
      }>(
        `${API_CONFIG.ENDPOINTS.PROFILE.UPDATE_SECTION}/validate`,
        { section, data }
      );

      return response.data || { isValid: false, errors: [], warnings: [], suggestions: [] };
    } catch (error) {
      console.error('Failed to validate profile section:', error);
      return this.getLocalValidation(section, data);
    }
  }

  /**
   * 本地资料验证（备用）
   */
  private getLocalValidation(section: ProfileSection, data: any): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    suggestions: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    switch (section) {
      case 'basic-info':
        if (!data.name?.trim()) errors.push('Name is required');
        if (!data.age?.trim()) errors.push('Age is required');
        if (!data.location?.trim()) errors.push('Location is required');
        if (!data.oneSentenceIntro?.trim()) {
          warnings.push('Adding a personal introduction makes your profile more engaging');
          suggestions.push('Write 1-2 sentences describing your professional background or interests');
        }
        break;

      case 'skills':
        if (!Array.isArray(data) || data.length === 0) {
          warnings.push('Adding skills helps with better matching');
          suggestions.push('Add 3-8 key skills that represent your expertise');
        } else if (data.length < 3) {
          suggestions.push('Consider adding more skills to showcase your full expertise');
        }
        break;

      case 'projects':
        if (!Array.isArray(data) || data.length === 0) {
          warnings.push('Adding projects showcases your experience');
          suggestions.push('Include 1-3 key projects that demonstrate your abilities');
        } else {
          data.forEach((project: any, index: number) => {
            if (!project.title?.trim()) errors.push(`Project ${index + 1}: Title is required`);
            if (!project.description?.trim()) warnings.push(`Project ${index + 1}: Description helps others understand your work`);
          });
        }
        break;

      case 'goals':
        if (!Array.isArray(data) || data.length === 0) {
          warnings.push('Adding goals helps others understand what you\'re looking for');
          suggestions.push('Describe 2-4 key professional or personal goals');
        }
        break;

      default:
        break;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  }

  /**
   * 计算本地资料完整度（备用方法）
   */
  calculateLocalCompleteness(profile: UserProfile): ProfileCompleteness {
    const sections: Record<ProfileSection, { completed: boolean; weight: number; suggestions?: string[] }> = {
      'basic-info': {
        completed: !!(profile.demographics?.name && profile.demographics?.age && profile.demographics?.location),
        weight: 20,
        suggestions: []
      },
      'skills': {
        completed: !!(profile.skills && profile.skills.length >= 3),
        weight: 15,
        suggestions: profile.skills?.length < 3 ? ['Add more skills to showcase your expertise'] : []
      },
      'resources': {
        completed: !!(profile.resources && profile.resources.length > 0),
        weight: 10,
        suggestions: !profile.resources?.length ? ['Add resources you can offer to collaborators'] : []
      },
      'projects': {
        completed: !!(profile.projects && profile.projects.length > 0),
        weight: 15,
        suggestions: !profile.projects?.length ? ['Add projects to demonstrate your experience'] : []
      },
      'goals': {
        completed: !!(profile.goals && profile.goals.length > 0),
        weight: 15,
        suggestions: !profile.goals?.length ? ['Add goals to help others understand what you\'re seeking'] : []
      },
      'demands': {
        completed: !!(profile.demands && profile.demands.length > 0),
        weight: 10,
        suggestions: !profile.demands?.length ? ['Specify what kind of collaborators you\'re looking for'] : []
      },
      'institutions': {
        completed: !!(profile.institutions && profile.institutions.length > 0),
        weight: 10,
        suggestions: !profile.institutions?.length ? ['Add your educational or work background'] : []
      },
      'university': {
        completed: !!(profile.university && profile.university.name),
        weight: 5,
        suggestions: !profile.university ? ['Add your university for better networking'] : []
      }
    };

    const completedWeight = Object.values(sections)
      .filter(section => section.completed)
      .reduce((sum, section) => sum + section.weight, 0);

    const totalWeight = Object.values(sections)
      .reduce((sum, section) => sum + section.weight, 0);

    const overall = Math.round((completedWeight / totalWeight) * 100);

    const missingFields = Object.entries(sections)
      .filter(([_, section]) => !section.completed)
      .map(([sectionId, section]) => ({
        section: sectionId as ProfileSection,
        field: sectionId,
        importance: section.weight >= 15 ? 'high' as const : 
                   section.weight >= 10 ? 'medium' as const : 'low' as const,
        suggestion: section.suggestions?.[0] || `Complete your ${sectionId} section`
      }));

    return {
      overall,
      sections,
      missingFields
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

// 创建并导出用户资料服务实例
export const profileService = new ProfileService();

// 导出默认实例
export default profileService; 