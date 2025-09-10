import { apiPost } from './client';

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

export async function createProject(data: ProjectCreateRequest): Promise<ProjectResponse> {
  return apiPost<ProjectResponse>('/api/projects/', data);
} 