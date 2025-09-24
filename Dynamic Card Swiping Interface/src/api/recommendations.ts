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

// Agent Card interfaces for AI-generated project ideas
export interface AgentCard {
	card_id: number;
	project_idea_title: string;
	project_scope: string;
	description: string;
	key_features: string[];
	estimated_timeline: string;
	difficulty_level: string;
	required_skills: string[];
	similar_examples?: string[];
	relevance_score: number;
}

export interface FavoriteCard {
	like_id: number;
	liked_at: string;
	interest_level?: number;
	notes?: string;
	card: AgentCard;
}

export interface HistoryCard {
	history_id: number;
	added_at: string;
	rejection_reason?: string;
	feedback?: string;
	card: AgentCard;
}

export interface CardsResponse {
	cards: ProjectCard[];
	message?: string;
}

export interface SwipeResponse {
	message: string;
	card_id: number;
	is_match?: boolean;
}

export interface FavoritesResponse {
	likes: FavoriteCard[];
	count: number;
}

export interface HistoryResponse {
	history: HistoryCard[];
	count: number;
}

// Local storage interface
export interface LocalStorageData {
	favorites: FavoriteCard[];
	history: HistoryCard[];
	lastUpdated: string;
}

// Filtering interfaces
export interface CardFilters {
	difficultyLevels?: string[];
	projectScopes?: string[];
	requiredSkills?: string[];
	minRelevanceScore?: number;
	timelineRange?: {min: string, max: string};
}

export async function fetchProjectCards(): Promise<CardsResponse> {
	return apiGet<CardsResponse>(`/api/v1/recommendations/cards`);
}

export async function sendSwipe(cardId: number | string, isLike: boolean): Promise<SwipeResponse | undefined> {
	const payload = {
		card_id: typeof cardId === 'string' ? parseInt(cardId, 10) : cardId,
		direction: isLike ? 'like' : 'dislike'
	};
	return apiPost<SwipeResponse>(`/api/v1/recommendations/swipe`, payload);
}

// New functions for agent cards
export async function sendAgentCardSwipe(cardId: number, action: 'left' | 'right', additionalData?: {
	interest_level?: number;
	notes?: string;
	rejection_reason?: string;
	feedback?: string;
}): Promise<any> {
	const payload = {
		card_id: cardId,
		action,
		...additionalData
	};
	return apiPost<any>(`/api/agent-cards/swipe`, payload);
}

export async function fetchFavorites(limit: number = 50): Promise<FavoritesResponse> {
	return apiGet<FavoritesResponse>(`/api/agent-cards/likes?limit=${limit}`);
}

export async function fetchHistory(limit: number = 50): Promise<HistoryResponse> {
	return apiGet<HistoryResponse>(`/api/agent-cards/history?limit=${limit}`);
}

// Local storage management
export class LocalStorageManager {
	private static readonly STORAGE_KEY = 'tinder_app_data';

	static saveToLocal(data: Partial<LocalStorageData>): void {
		try {
			const existing = this.getFromLocal();
			const updated = {
				...existing,
				...data,
				lastUpdated: new Date().toISOString()
			};
			localStorage.setItem(this.STORAGE_KEY, JSON.stringify(updated));
		} catch (error) {
			console.error('Failed to save to local storage:', error);
		}
	}

	static getFromLocal(): LocalStorageData {
		try {
			const data = localStorage.getItem(this.STORAGE_KEY);
			return data ? JSON.parse(data) : {
				favorites: [],
				history: [],
				lastUpdated: new Date().toISOString()
			};
		} catch (error) {
			console.error('Failed to load from local storage:', error);
			return {
				favorites: [],
				history: [],
				lastUpdated: new Date().toISOString()
			};
		}
	}

	static syncFavorites(serverData: FavoriteCard[]): FavoriteCard[] {
		const localData = this.getFromLocal();
		const merged = [...serverData];
		
		// Add any local favorites not in server data
		localData.favorites.forEach(localFav => {
			if (!merged.find(serverFav => serverFav.like_id === localFav.like_id)) {
				merged.push(localFav);
			}
		});

		this.saveToLocal({ favorites: merged });
		return merged;
	}

	static syncHistory(serverData: HistoryCard[]): HistoryCard[] {
		const localData = this.getFromLocal();
		const merged = [...serverData];
		
		// Add any local history not in server data
		localData.history.forEach(localHist => {
			if (!merged.find(serverHist => serverHist.history_id === localHist.history_id)) {
				merged.push(localHist);
			}
		});

		this.saveToLocal({ history: merged });
		return merged;
	}

	static addToFavorites(card: FavoriteCard): void {
		const data = this.getFromLocal();
		// Check if already exists
		const exists = data.favorites.find(fav => fav.like_id === card.like_id || fav.card.card_id === card.card.card_id);
		if (!exists) {
			data.favorites.unshift(card);
			this.saveToLocal({ favorites: data.favorites });
		}
	}

	static addToHistory(card: HistoryCard): void {
		const data = this.getFromLocal();
		// Check if already exists
		const exists = data.history.find(hist => hist.history_id === card.history_id || hist.card.card_id === card.card.card_id);
		if (!exists) {
			data.history.unshift(card);
			this.saveToLocal({ history: data.history });
		}
	}
}

// Filtering functions
export function filterAgentCards(cards: AgentCard[], filters: CardFilters): AgentCard[] {
	return cards.filter(card => {
		// Filter by difficulty levels
		if (filters.difficultyLevels && filters.difficultyLevels.length > 0) {
			if (!filters.difficultyLevels.includes(card.difficulty_level)) {
				return false;
			}
		}

		// Filter by project scopes
		if (filters.projectScopes && filters.projectScopes.length > 0) {
			if (!filters.projectScopes.includes(card.project_scope)) {
				return false;
			}
		}

		// Filter by required skills
		if (filters.requiredSkills && filters.requiredSkills.length > 0) {
			const hasMatchingSkill = filters.requiredSkills.some(skill => 
				card.required_skills.some(cardSkill => 
					cardSkill.toLowerCase().includes(skill.toLowerCase())
				)
			);
			if (!hasMatchingSkill) {
				return false;
			}
		}

		// Filter by minimum relevance score
		if (filters.minRelevanceScore !== undefined) {
			if (card.relevance_score < filters.minRelevanceScore) {
				return false;
			}
		}

		// Filter by timeline range (basic implementation)
		if (filters.timelineRange) {
			// This is a simplified implementation - you might want to enhance this
			// based on your timeline format
			const cardTimeline = card.estimated_timeline.toLowerCase();
			if (filters.timelineRange.min && !cardTimeline.includes(filters.timelineRange.min.toLowerCase())) {
				// Basic filtering by timeline - can be enhanced
			}
		}

		return true;
	});
} 