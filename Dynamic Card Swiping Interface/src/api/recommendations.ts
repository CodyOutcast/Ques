import { apiGet, apiPost } from './client';

export interface OwnerInfo {
	name: string;
	age?: number | null;
	gender?: string | null;
	role: string;
	distance?: number | null;
	avatar: string;
	tags: string[];
}

export interface Collaborator {
	name: string;
	role: string;
	avatar: string;
}

export interface LookingFor {
	tags: string[];
	description?: string;
}

export interface ProjectCard {
	id: number;
	title: string;
	description: string;
	tags: string[];
	type: 'project';
	cardStyle: 'image' | 'video' | 'text-only';
	status: 'ongoing' | 'finished' | 'not_started' | string;
	owner: OwnerInfo;
	collaborators: number;
	collaboratorsList: Collaborator[];
	detailedDescription?: string;
	startTime?: string;
	currentProgress?: number;
	content?: string;
	purpose?: string;
	lookingFor?: LookingFor; // 新接口为对象
	links: string[];
	media: string[];
	cover?: string | null; // 新接口使用 cover
	videoUrl?: string | null;
	gradientBackground?: string;
}

export interface CardsResponse {
	cards: ProjectCard[];
	message?: string;
}

export async function fetchProjectCards(): Promise<CardsResponse> {
	return apiGet<CardsResponse>(`/api/v1/recommendations/cards`);
}

export async function sendSwipe(cardId: number | string, isLike: boolean): Promise<{ message: string; card_id: number | string } | undefined> {
	return apiPost(`/api/v1/recommendations/swipe`, { card_id: typeof cardId === 'string' ? parseInt(cardId, 10) : cardId, is_like: isLike });
} 