import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  UniversityVerificationRequest,
  VerificationCodeRequest,
  CodeVerificationRequest,
  UniversityListResponse,
  UniversityVerificationStatus,
  SearchParams
} from '../types/api';

// 大学基本信息
export interface University {
  id: string;
  name: string;
  nameEn?: string;
  domain: string[];
  country: string;
  province?: string;
  city?: string;
  website?: string;
  logo?: string;
  verified: boolean;
  rank?: number;
  type: 'university' | 'college' | 'institute';
}

// 大学验证状态
export interface UniversityVerification {
  id: string;
  universityId: string;
  university: University;
  email: string;
  status: 'pending' | 'verified' | 'failed' | 'expired';
  verifiedAt?: string;
  createdAt: string;
  updatedAt: string;
}

class UniversityService {
  /**
   * 搜索大学
   */
  async searchUniversities(params: SearchParams): Promise<ApiResponse<UniversityListResponse>> {
    try {
      const searchParams = new URLSearchParams();
      searchParams.append('page', params.page.toString());
      searchParams.append('limit', params.limit.toString());
      
      if (params.query) {
        searchParams.append('q', params.query);
      }
      
      if (params.filters) {
        Object.entries(params.filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            searchParams.append(key, value.toString());
          }
        });
      }

      return await httpClient.get<UniversityListResponse>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.SEARCH}?${searchParams.toString()}`
      );
    } catch (error) {
      console.error('Failed to search universities:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取热门大学列表
   */
  async getPopularUniversities(country?: string, limit = 10): Promise<ApiResponse<University[]>> {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('popular', 'true');
      
      if (country) {
        params.append('country', country);
      }

      return await httpClient.get<University[]>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.SEARCH}?${params.toString()}`
      );
    } catch (error) {
      console.error('Failed to get popular universities:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 根据邮箱域名获取大学信息
   */
  async getUniversityByDomain(domain: string): Promise<ApiResponse<University | null>> {
    try {
      return await httpClient.get<University | null>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.SEARCH}/domain/${encodeURIComponent(domain)}`
      );
    } catch (error) {
      console.error('Failed to get university by domain:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取中国大学列表（预设）
   */
  getChineseUniversities(): University[] {
    return [
      { id: '1', name: 'Tsinghua University', domain: ['tsinghua.edu.cn'], country: 'China', verified: true, type: 'university', rank: 1 },
      { id: '2', name: 'Peking University', domain: ['pku.edu.cn'], country: 'China', verified: true, type: 'university', rank: 2 },
      { id: '3', name: 'Fudan University', domain: ['fudan.edu.cn'], country: 'China', verified: true, type: 'university', rank: 3 },
      { id: '4', name: 'Shanghai Jiao Tong University', domain: ['sjtu.edu.cn'], country: 'China', verified: true, type: 'university', rank: 4 },
      { id: '5', name: 'Zhejiang University', domain: ['zju.edu.cn'], country: 'China', verified: true, type: 'university', rank: 5 },
      { id: '6', name: 'University of Science and Technology of China', domain: ['ustc.edu.cn'], country: 'China', verified: true, type: 'university', rank: 6 },
      { id: '7', name: 'Nanjing University', domain: ['nju.edu.cn'], country: 'China', verified: true, type: 'university', rank: 7 },
      { id: '8', name: 'Xi\'an Jiaotong University', domain: ['xjtu.edu.cn'], country: 'China', verified: true, type: 'university', rank: 8 },
      { id: '9', name: 'Harbin Institute of Technology', domain: ['hit.edu.cn'], country: 'China', verified: true, type: 'university', rank: 9 },
      { id: '10', name: 'Beijing Institute of Technology', domain: ['bit.edu.cn'], country: 'China', verified: true, type: 'university', rank: 10 },
      { id: '11', name: 'Huazhong University of Science and Technology', domain: ['hust.edu.cn'], country: 'China', verified: true, type: 'university', rank: 11 },
      { id: '12', name: 'Sun Yat-sen University', domain: ['sysu.edu.cn'], country: 'China', verified: true, type: 'university', rank: 12 },
      { id: '13', name: 'Beihang University', domain: ['buaa.edu.cn'], country: 'China', verified: true, type: 'university', rank: 13 },
      { id: '14', name: 'Tianjin University', domain: ['tju.edu.cn'], country: 'China', verified: true, type: 'university', rank: 14 },
      { id: '15', name: 'Southeast University', domain: ['seu.edu.cn'], country: 'China', verified: true, type: 'university', rank: 15 }
    ];
  }

  /**
   * 发送大学邮箱验证码
   */
  async sendUniversityVerification(request: UniversityVerificationRequest): Promise<ApiResponse<{
    sent: boolean;
    expiresIn: number;
    verificationId: string;
  }>> {
    try {
      return await httpClient.post(
        API_CONFIG.ENDPOINTS.UNIVERSITY.SEND_VERIFICATION,
        request
      );
    } catch (error) {
      console.error('Failed to send university verification:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证大学邮箱
   */
  async verifyUniversity(verificationId: string, code: string): Promise<ApiResponse<{
    verified: boolean;
    universityInfo?: University;
  }>> {
    try {
      return await httpClient.post(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/${verificationId}`,
        { code }
      );
    } catch (error) {
      console.error('University verification failed:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取用户的大学验证状态
   */
  async getVerificationStatus(): Promise<ApiResponse<UniversityVerification | null>> {
    try {
      return await httpClient.get<UniversityVerification | null>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/status`
      );
    } catch (error) {
      console.error('Failed to get verification status:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证邮箱域名格式
   */
  validateEmailDomain(email: string, universityDomains: string[]): boolean {
    if (!email || !email.includes('@')) {
      return false;
    }

    const domain = email.split('@')[1]?.toLowerCase();
    if (!domain) {
      return false;
    }

    // 检查是否匹配大学域名
    return universityDomains.some(uniDomain => 
      domain === uniDomain.toLowerCase() || domain.endsWith('.' + uniDomain.toLowerCase())
    );
  }

  /**
   * 验证中国大学邮箱格式
   */
  validateChineseUniversityEmail(email: string): {
    isValid: boolean;
    university?: University;
    suggestion?: string;
  } {
    if (!email || !email.includes('@')) {
      return { isValid: false };
    }

    const domain = email.split('@')[1]?.toLowerCase();
    if (!domain) {
      return { isValid: false };
    }

    // 检查是否是.edu.cn结尾
    const isEduCn = domain.endsWith('.edu.cn');
    
    // 检查预设大学列表
    const universities = this.getChineseUniversities();
    const matchedUniversity = universities.find(uni => 
      uni.domain.some(uniDomain => 
        domain === uniDomain.toLowerCase() || domain.endsWith('.' + uniDomain.toLowerCase())
      )
    );

    if (matchedUniversity) {
      return { 
        isValid: true, 
        university: matchedUniversity 
      };
    }

    // 如果是.edu.cn但不在预设列表中，仍然认为可能有效
    if (isEduCn) {
      return { 
        isValid: true,
        suggestion: 'This appears to be a valid Chinese university email'
      };
    }

    return { 
      isValid: false,
      suggestion: 'Please use your university email ending with .edu.cn'
    };
  }

  /**
   * 自动补全大学名称
   */
  async autoCompleteUniversity(query: string, limit = 5): Promise<University[]> {
    if (!query || query.length < 2) {
      return [];
    }

    const universities = this.getChineseUniversities();
    const lowerQuery = query.toLowerCase();

    return universities
      .filter(uni => 
        uni.name.toLowerCase().includes(lowerQuery) ||
        (uni.nameEn && uni.nameEn.toLowerCase().includes(lowerQuery))
      )
      .slice(0, limit);
  }

  /**
   * 获取大学详细信息
   */
  async getUniversityDetails(universityId: string): Promise<ApiResponse<University>> {
    try {
      return await httpClient.get<University>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.SEARCH}/${universityId}`
      );
    } catch (error) {
      console.error('Failed to get university details:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取增强的大学验证状态
   */
  async getEnhancedVerificationStatus(verificationId: string): Promise<ApiResponse<UniversityVerificationStatus>> {
    try {
      return await httpClient.get<UniversityVerificationStatus>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/status/${verificationId}`
      );
    } catch (error) {
      console.error('Failed to get enhanced verification status:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 增强的大学验证请求
   */
  async requestEnhancedVerification(request: UniversityVerificationRequest): Promise<ApiResponse<{
    verificationId: string;
    status: UniversityVerificationStatus;
    nextSteps: Array<{
      action: string;
      description: string;
      required: boolean;
      deadline?: string;
    }>;
  }>> {
    try {
      return await httpClient.post<{
        verificationId: string;
        status: UniversityVerificationStatus;
        nextSteps: Array<{
          action: string;
          description: string;
          required: boolean;
          deadline?: string;
        }>;
      }>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/enhanced`,
        request
      );
    } catch (error) {
      console.error('Failed to request enhanced verification:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证大学邮箱域名
   */
  async validateUniversityDomain(email: string, universityName: string): Promise<{
    isValid: boolean;
    university?: University;
    domain: string;
    suggestions: string[];
    confidence: number; // 1-100
  }> {
    try {
      const response = await httpClient.post<{
        isValid: boolean;
        university?: University;
        domain: string;
        suggestions: string[];
        confidence: number;
      }>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/validate-domain`,
        { email, universityName }
      );

      return response.data || {
        isValid: false,
        domain: '',
        suggestions: [],
        confidence: 0
      };
    } catch (error) {
      console.error('Failed to validate university domain:', error);
      return this.getLocalDomainValidation(email, universityName);
    }
  }

  /**
   * 获取大学验证福利
   */
  async getVerificationBenefits(universityId: string): Promise<ApiResponse<{
    benefits: Array<{
      type: 'badge' | 'priority' | 'access' | 'discount' | 'feature';
      title: string;
      description: string;
      icon?: string;
      value?: string;
      active: boolean;
      conditions?: string[];
    }>;
    eligibility: {
      requirements: string[];
      currentStatus: 'eligible' | 'partial' | 'ineligible';
      missingRequirements: string[];
    };
  }>> {
    try {
      return await httpClient.get<{
        benefits: Array<{
          type: 'badge' | 'priority' | 'access' | 'discount' | 'feature';
          title: string;
          description: string;
          icon?: string;
          value?: string;
          active: boolean;
          conditions?: string[];
        }>;
        eligibility: {
          requirements: string[];
          currentStatus: 'eligible' | 'partial' | 'ineligible';
          missingRequirements: string[];
        };
      }>(`${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/benefits/${universityId}`);
    } catch (error) {
      console.error('Failed to get verification benefits:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 多种验证方法支持
   */
  async requestAlternativeVerification(params: {
    universityId: string;
    method: 'document' | 'social' | 'third_party' | 'manual';
    data: any;
  }): Promise<ApiResponse<{
    verificationId: string;
    method: string;
    status: 'pending' | 'processing' | 'review_required';
    estimatedProcessingTime: string;
    requirements: string[];
  }>> {
    try {
      return await httpClient.post<{
        verificationId: string;
        method: string;
        status: 'pending' | 'processing' | 'review_required';
        estimatedProcessingTime: string;
        requirements: string[];
      }>(
        `${API_CONFIG.ENDPOINTS.UNIVERSITY.VERIFY}/alternative`,
        params
      );
    } catch (error) {
      console.error('Failed to request alternative verification:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取大学排名和统计信息
   */
  async getUniversityStats(universityId: string): Promise<ApiResponse<{
    ranking: {
      national?: number;
      global?: number;
      subject?: Array<{ subject: string; rank: number; source: string }>;
    };
    statistics: {
      totalStudents?: number;
      internationalStudents?: number;
      facultyCount?: number;
      foundedYear?: number;
    };
    programs: Array<{
      name: string;
      level: 'bachelor' | 'master' | 'phd';
      duration: string;
      language: string;
    }>;
    verifiedAlumni: {
      count: number;
      notableAlumni: Array<{
        name: string;
        field: string;
        achievement: string;
      }>;
    };
  }>> {
    try {
      return await httpClient.get<{
        ranking: {
          national?: number;
          global?: number;
          subject?: Array<{ subject: string; rank: number; source: string }>;
        };
        statistics: {
          totalStudents?: number;
          internationalStudents?: number;
          facultyCount?: number;
          foundedYear?: number;
        };
        programs: Array<{
          name: string;
          level: 'bachelor' | 'master' | 'phd';
          duration: string;
          language: string;
        }>;
        verifiedAlumni: {
          count: number;
          notableAlumni: Array<{
            name: string;
            field: string;
            achievement: string;
          }>;
        };
      }>(`${API_CONFIG.ENDPOINTS.UNIVERSITY.SEARCH}/stats/${universityId}`);
    } catch (error) {
      console.error('Failed to get university stats:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 本地域名验证（备用方法）
   */
  private getLocalDomainValidation(email: string, universityName: string): {
    isValid: boolean;
    university?: University;
    domain: string;
    suggestions: string[];
    confidence: number;
  } {
    if (!email || !universityName) {
      return {
        isValid: false,
        domain: '',
        suggestions: ['Please provide both email and university name'],
        confidence: 0
      };
    }

    const domain = email.split('@')[1]?.toLowerCase() || '';
    const universityLower = universityName.toLowerCase();

    // 中国大学常见域名模式
    const eduCnPattern = /\.edu\.cn$/;
    const isEduCn = eduCnPattern.test(domain);

    // 知名大学域名映射
    const knownDomains: Record<string, { name: string; confidence: number }> = {
      'tsinghua.edu.cn': { name: 'Tsinghua University', confidence: 100 },
      'pku.edu.cn': { name: 'Peking University', confidence: 100 },
      'fudan.edu.cn': { name: 'Fudan University', confidence: 100 },
      'sjtu.edu.cn': { name: 'Shanghai Jiao Tong University', confidence: 100 },
      'zju.edu.cn': { name: 'Zhejiang University', confidence: 100 },
      'ustc.edu.cn': { name: 'University of Science and Technology of China', confidence: 100 },
      'nju.edu.cn': { name: 'Nanjing University', confidence: 100 },
      'xjtu.edu.cn': { name: 'Xi\'an Jiaotong University', confidence: 100 },
    };

    const knownDomain = knownDomains[domain];
    
    if (knownDomain) {
      const nameMatch = knownDomain.name.toLowerCase().includes(universityLower) ||
                       universityLower.includes(knownDomain.name.toLowerCase().split(' ')[0]);
      
      return {
        isValid: nameMatch,
        domain,
        suggestions: nameMatch ? [] : [`Domain ${domain} belongs to ${knownDomain.name}, not ${universityName}`],
        confidence: nameMatch ? knownDomain.confidence : 20
      };
    }

    if (isEduCn) {
      const domainParts = domain.replace('.edu.cn', '').split('.');
      const universityAbbr = domainParts[domainParts.length - 1];
      
      return {
        isValid: true,
        domain,
        suggestions: [],
        confidence: 80
      };
    }

    return {
      isValid: false,
      domain,
      suggestions: [
        'Email domain does not appear to be a Chinese university domain',
        'Please use your official university email (.edu.cn domain)',
        'Contact support if you believe this is an error'
      ],
      confidence: 10
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

// 创建并导出大学服务实例
export const universityService = new UniversityService();

// 导出默认实例
export default universityService; 