import { apiPost } from './client';

// ===== 原有的简单Projects API =====
export interface ProjectCreateRequest {
  short_description: string;
  long_description?: string | null;
  start_time: string; // ISO string
  status?: 'ONGOING' | 'ON_HOLD' | 'FINISHED';
  media_link_id?: number | null;
}

export interface ProjectResponse {
  project_id: number;
  short_description: string;
  long_description?: string | null;
  start_time: string;
  status: 'ONGOING' | 'ON_HOLD' | 'FINISHED';
  media_link_id?: number | null;
  created_at: string;
  updated_at: string;
}

// ===== 新增：丰富的Project Cards API =====
export interface ProjectCardCreateRequest {
  title: string;
  description: string;
  short_description?: string | null;
  category?: string | null;
  industry?: string | null;
  project_type?: 'startup' | 'side_project' | 'investment' | 'collaboration';
  stage?: string | null;
  looking_for?: string[] | null;
  skills_needed?: string[] | null;
  image_urls?: string[] | null;
  video_url?: string | null;
  demo_url?: string | null;
  pitch_deck_url?: string | null;
  funding_goal?: number | null;
  equity_offered?: number | null;
  current_valuation?: number | null;
  revenue?: number | null;
  feature_tags?: string[] | null;
}

export interface ProjectCardResponse {
  project_id: number;
  title: string;
  description: string;
  short_description?: string | null;
  category?: string | null;
  industry?: string | null;
  project_type: string;
  stage?: string | null;
  looking_for?: string[] | null;
  skills_needed?: string[] | null;
  image_urls?: string[] | null;
  video_url?: string | null;
  demo_url?: string | null;
  pitch_deck_url?: string | null;
  funding_goal?: number | null;
  equity_offered?: number | null;
  current_valuation?: number | null;
  revenue?: number | null;
  feature_tags?: string[] | null;
  created_at: string;
  updated_at: string;
}

// ===== 前端ProjectData接口（来自PostingProjectPage）=====
export interface FrontendProjectData {
  title: string;
  shortDescription: string;
  media: File[];
  projectTags: string[];
  ownRole: string[];
  startTime: string;
  currentProgress: number;
  detailedDescription: string;
  purpose: string;
  whatWeAreDoing: string;
  peopleLookingFor: string;
  lookingForTags: string[];
  links: string[];
}

// ===== 字段映射函数 =====
export function mapFrontendToProjectCard(frontendData: FrontendProjectData): ProjectCardCreateRequest {
  // 确定项目类型
  const getProjectType = (): 'startup' | 'side_project' | 'investment' | 'collaboration' => {
    const title = frontendData.title.toLowerCase();
    const description = frontendData.detailedDescription.toLowerCase();
    
    if (title.includes('startup') || description.includes('startup')) return 'startup';
    if (title.includes('investment') || description.includes('funding')) return 'investment';
    if (title.includes('collaborat') || description.includes('collaborat')) return 'collaboration';
    return 'side_project'; // 默认
  };

  // 确定项目阶段
  const getProjectStage = (): string => {
    const progress = frontendData.currentProgress || 0;
    if (progress <= 0) return 'idea';
    if (progress <= 25) return 'planning';
    if (progress <= 50) return 'prototype';
    if (progress <= 75) return 'mvp';
    return 'scaling';
  };

  // 处理链接 - 分类不同类型的链接
  const categorizeLinks = (links: string[]) => {
    const result: { demo_url?: string; pitch_deck_url?: string; video_url?: string } = {};
    
    links.forEach(link => {
      const lowerLink = link.toLowerCase();
      if (lowerLink.includes('demo') || lowerLink.includes('preview')) {
        result.demo_url = link;
      } else if (lowerLink.includes('pitch') || lowerLink.includes('deck')) {
        result.pitch_deck_url = link;
      } else if (lowerLink.includes('video') || lowerLink.includes('youtube') || lowerLink.includes('vimeo')) {
        result.video_url = link;
      }
    });
    
    return result;
  };

  const categorizedLinks = categorizeLinks(frontendData.links || []);

  return {
    title: frontendData.title || 'Untitled Project',
    description: frontendData.detailedDescription || frontendData.whatWeAreDoing || frontendData.shortDescription || 'No description provided',
    short_description: frontendData.shortDescription || null,
    category: null, // 前端暂无category字段
    industry: null, // 前端暂无industry字段
    project_type: getProjectType(),
    stage: getProjectStage(),
    looking_for: frontendData.lookingForTags?.length > 0 ? frontendData.lookingForTags : null,
    skills_needed: frontendData.projectTags?.length > 0 ? frontendData.projectTags : null,
    image_urls: null, // 将在文件上传后填充
    video_url: categorizedLinks.video_url || null,
    demo_url: categorizedLinks.demo_url || null,
    pitch_deck_url: categorizedLinks.pitch_deck_url || null,
    funding_goal: null, // 前端暂无funding相关字段
    equity_offered: null,
    current_valuation: null,
    revenue: null,
    feature_tags: frontendData.projectTags?.length > 0 ? frontendData.projectTags : null,
  };
}

// ===== 文件上传函数 =====
export async function uploadMediaFiles(files: File[]): Promise<string[]> {
  const uploadedUrls: string[] = [];
  
  for (const file of files) {
    try {
      // 这里需要根据你的实际文件上传API进行调整
      // 现在使用Object URL作为临时方案
      const objectUrl = URL.createObjectURL(file);
      uploadedUrls.push(objectUrl);
      
      // TODO: 实现真实的文件上传
      // const formData = new FormData();
      // formData.append('file', file);
      // const response = await apiPost<{url: string}>('/api/upload', formData);
      // uploadedUrls.push(response.url);
    } catch (error) {
      console.error('Failed to upload file:', file.name, error);
      // 继续处理其他文件
    }
  }
  
  return uploadedUrls;
}

// ===== API调用函数 =====
export async function createProject(data: ProjectCreateRequest): Promise<ProjectResponse> {
  return apiPost<ProjectResponse>('/api/projects/', data);
}

export async function createProjectCard(data: ProjectCardCreateRequest): Promise<ProjectCardResponse> {
  return apiPost<ProjectCardResponse>('/api/project-cards/', data);
}

// ===== 统一的项目创建函数 =====
export async function createProjectFromFrontend(frontendData: FrontendProjectData | any): Promise<{
  success: boolean;
  data?: ProjectCardResponse;
  error?: string;
}> {
  try {
    // 1. 上传媒体文件
    let imageUrls: string[] = [];
    if (frontendData.media && frontendData.media.length > 0) {
      try {
        imageUrls = await uploadMediaFiles(frontendData.media);
      } catch (uploadError) {
        console.warn('Media upload failed, proceeding without images:', uploadError);
      }
    }

    // 2. 映射字段
    const projectCardData = mapFrontendToProjectCard(frontendData);
    
    // 3. 添加上传的图片URL
    if (imageUrls.length > 0) {
      projectCardData.image_urls = imageUrls;
    }

    // 4. 创建项目卡片
    const result = await createProjectCard(projectCardData);
    
    return {
      success: true,
      data: result
    };
  } catch (error) {
    console.error('Failed to create project:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
} 