import { useState, useCallback } from 'react';
import { authService, profileService, universityService, ApiError } from '../services';
import type { 
  UserProfile as ApiUserProfile, 
  RegisterRequest,
  UniversityVerificationRequest,
  CodeVerificationRequest 
} from '../types/api';
import type { UserProfile } from '../App';
import type { University } from '../services/universityService';

// 状态类型定义
interface WizardState {
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  uploadProgress: number;
  verificationSent: boolean;
  emailVerified: boolean;
  wechatAuthenticated: boolean;
}

// 转换函数：将App的UserProfile转换为API的UserProfile
function convertToApiProfile(profile: UserProfile): ApiUserProfile {
  return {
    demographics: {
      name: profile.name,
      birthday: profile.birthday,
      gender: profile.gender as 'male' | 'female' | 'other',
      location: profile.location,
      hobbies: profile.hobbies,
      languages: profile.languages,
      oneSentenceIntro: profile.oneSentenceIntro,
      profilePhoto: profile.profilePhoto,
    },
    skills: profile.skills,
    resources: profile.resources,
    projects: profile.projects.map(p => ({
      title: p.title,
      role: p.role,
      description: p.description,
      referenceLinks: p.referenceLinks,
    })),
    goals: profile.goals,
    demands: profile.demands,
    institutions: profile.institutions.map(inst => ({
      name: inst.name,
      role: inst.role,
      description: inst.description,
      email: inst.email,
      verified: inst.verified,
    })),
    university: profile.university ? {
      name: profile.university.name,
      verified: profile.university.verified,
    } : undefined,
  };
}

export function useProfileWizard() {
  const [state, setState] = useState<WizardState>({
    isLoading: false,
    isSubmitting: false,
    error: null,
    uploadProgress: 0,
    verificationSent: false,
    emailVerified: false,
    wechatAuthenticated: false,
  });

  // 更新状态的辅助函数
  const updateState = useCallback((updates: Partial<WizardState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  // 设置错误
  const setError = useCallback((error: string | null) => {
    updateState({ error, isLoading: false, isSubmitting: false });
  }, [updateState]);

  // 清除错误
  const clearError = useCallback(() => {
    updateState({ error: null });
  }, [updateState]);

  // 上传头像
  const uploadAvatar = useCallback(async (file: File): Promise<string | null> => {
    try {
      updateState({ isLoading: true, uploadProgress: 0, error: null });

      const response = await profileService.uploadAvatar(file, (progress) => {
        updateState({ uploadProgress: progress });
      });

      if (response.success && response.data) {
        updateState({ isLoading: false, uploadProgress: 100 });
        return response.data.url;
      } else {
        throw new Error(response.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Avatar upload failed:', error);
      setError(error instanceof ApiError ? error.message : 'Upload failed');
      return null;
    }
  }, [updateState, setError]);

  // 搜索大学
  const searchUniversities = useCallback(async (query: string): Promise<University[]> => {
    try {
      if (query.length < 2) {
        return [];
      }

      updateState({ isLoading: true, error: null });
      
      // 首先尝试本地搜索（中国大学）
      const localResults = await universityService.autoCompleteUniversity(query);
      
      if (localResults.length > 0) {
        updateState({ isLoading: false });
        return localResults;
      }

      // 如果本地没有结果，尝试在线搜索
      const response = await universityService.searchUniversities({
        page: 1,
        limit: 10,
        query,
        filters: { country: 'China' }
      });

      updateState({ isLoading: false });

      if (response.success && response.data?.data) {
        return response.data.data.map(uni => ({
          id: uni.id,
          name: uni.name,
        }));
      }

      return [];
    } catch (error) {
      console.error('University search failed:', error);
      setError(error instanceof ApiError ? error.message : 'Search failed');
      return [];
    }
  }, [updateState, setError]);

  // 发送大学验证邮件
  const sendUniversityVerification = useCallback(async (
    universityName: string, 
    email: string
  ): Promise<boolean> => {
    try {
      updateState({ isLoading: true, error: null });

      const request: UniversityVerificationRequest = {
        universityName,
        email,
      };

      const response = await universityService.sendUniversityVerification(request);

      if (response.success && response.data?.sent) {
        updateState({ 
          isLoading: false, 
          verificationSent: true 
        });
        return true;
      } else {
        throw new Error(response.error || 'Failed to send verification email');
      }
    } catch (error) {
      console.error('Failed to send verification:', error);
      setError(error instanceof ApiError ? error.message : 'Failed to send verification email');
      return false;
    }
  }, [updateState, setError]);

  // 验证大学邮箱
  const verifyUniversityEmail = useCallback(async (
    verificationId: string,
    code: string
  ): Promise<boolean> => {
    try {
      updateState({ isLoading: true, error: null });

      const response = await universityService.verifyUniversity(verificationId, code);

      if (response.success && response.data?.verified) {
        updateState({ 
          isLoading: false, 
          emailVerified: true 
        });
        return true;
      } else {
        throw new Error(response.error || 'Verification failed');
      }
    } catch (error) {
      console.error('Email verification failed:', error);
      setError(error instanceof ApiError ? error.message : 'Verification failed');
      return false;
    }
  }, [updateState, setError]);

  // 微信认证
  const authenticateWechat = useCallback(async (): Promise<boolean> => {
    try {
      updateState({ isLoading: true, error: null });

      // 模拟微信认证流程
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      updateState({ 
        isLoading: false, 
        wechatAuthenticated: true 
      });
      return true;
    } catch (error) {
      console.error('WeChat authentication failed:', error);
      setError('WeChat authentication failed');
      return false;
    }
  }, [updateState, setError]);

  // 提交注册
  const submitRegistration = useCallback(async (profile: UserProfile): Promise<boolean> => {
    try {
      updateState({ isSubmitting: true, error: null });

      // 转换资料格式
      const apiProfile = convertToApiProfile(profile);

      // 构建注册请求
      const registerRequest: RegisterRequest = {
        ...apiProfile,
        wechatId: state.wechatAuthenticated ? `user_${Date.now()}` : undefined,
                 universityEmail: state.emailVerified ? 'verified@email.com' : undefined, // 这里需要从其他状态获取
      };

      const response = await authService.register(registerRequest);

      if (response.success) {
        updateState({ 
          isSubmitting: false 
        });
        return true;
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      setError(error instanceof ApiError ? error.message : 'Registration failed');
      return false;
    }
  }, [state.wechatAuthenticated, state.emailVerified, updateState, setError]);

  // 验证资料
  const validateProfile = useCallback(async (profile: UserProfile) => {
    const apiProfile = convertToApiProfile(profile);
    return await profileService.validateProfile(apiProfile);
  }, []);

  // 验证中国大学邮箱
  const validateChineseEmail = useCallback((email: string) => {
    return universityService.validateChineseUniversityEmail(email);
  }, []);

  return {
    // 状态
    ...state,
    
    // 操作方法
    uploadAvatar,
    searchUniversities,
    sendUniversityVerification,
    verifyUniversityEmail,
    authenticateWechat,
    submitRegistration,
    validateProfile,
    validateChineseEmail,
    
    // 工具方法
    setError,
    clearError,
  };
} 