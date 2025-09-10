import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring, PanInfo } from 'framer-motion';
import { Send, Search, Settings, ArrowLeft, ExternalLink, Check } from 'lucide-react';
import svgPaths from '../imports/svg-fko3i96u3r';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import type { Project } from '../App';
import { HeaderBar } from './HeaderBar';
import TinderCard from 'react-tinder-card';
import { SWIPE_REQUIREMENT, SWIPE_THRESHOLD_PX, TAP_MAX_MOVEMENT_PX, TAP_MAX_DURATION_MS } from '../App';
import { getAccessToken } from '../src/api/client';
import { sendSwipe } from '../src/api/recommendations';
import { Button } from './ui/button';
import { Star } from 'lucide-react';
import { createPortal } from 'react-dom';
import { t } from '../translations';

// New interface for AI-generated project ideas
interface ProjectIdea {
	project_idea_title: string;
	project_scope: string;
	description: string;
	key_features: string[];
	estimated_timeline: string;
	difficulty_level: string;
	required_skills: string[];
	similar_examples: string[];
	relevance_score: number;
}

interface AISearchIntegratedProps {
	onBackToMain: () => void;
	onOpenFilter: () => void;
	onOpenProject: (project: Project) => void;
	// New: record swipes to main page collections
	onRecordLeftSwipe: (project: Project) => void;
	onRecordRightSwipe: (project: Project) => void;
	// New: global filter settings for right-swipe feedback
	suppressMatchIndicator: boolean;
}

const positiveEmojis = ['😊', '😍', '🥰', '😘', '🤩', '😎', '🙌', '👍', '💖', '✨', '🎉', '🔥'];

const mockProjects: Project[] = [
			{
			id: 10001,
			title: 'AI Research Collaboration Platform',
			author: 'Alex',
			collaborators: 3,
			description: 'Revolutionary AI-powered platform for creative collaboration',
			tags: ['AI', 'Design', 'Collaboration'],
			type: 'project',
			cardStyle: 'text-only',
			status: 'ongoing',
		owner: {
			name: 'Alex Chen',
			age: 28,
			gender: 'Male',
			role: 'Product Designer',
			distance: 2.5,
			avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
			tags: ['UI/UX', 'AI', 'Leadership']
		},
		collaboratorsList: [],
		detailedDescription: 'An innovative AI-powered platform designed to revolutionize how creative teams collaborate.',
		startTime: 'March 2024',
		currentProgress: 75,
		content: 'This project combines cutting-edge AI technology with intuitive design.',
		purpose: 'To eliminate friction in creative collaboration',
		lookingFor: ['Backend Developer'],
		links: [],
		media: [],
		gradientBackground: 'bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700'
	},
];

// Mock data builders for 20-card results
const gradientOptions = [
	'bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700',
	'bg-gradient-to-br from-pink-500 via-red-500 to-purple-600',
	'bg-gradient-to-br from-green-400 via-blue-500 to-purple-600',
	'bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500',
	'bg-gradient-to-br from-teal-400 via-blue-500 to-indigo-600',
	'bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600',
	'bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600',
	'bg-gradient-to-br from-rose-400 via-pink-500 to-purple-600',
	'bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600',
	'bg-gradient-to-br from-orange-400 via-red-500 to-pink-600',
];

const placeholderImages = [
	'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop&crop=center',
	'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop&crop=center',
	'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop&crop=center',
	'https://images.unsplash.com/photo-1569163139394-de4e5f43e4e3?w=800&h=600&fit=crop&crop=center',
];

function pick<T>(arr: T[], idx: number): T {
	return arr[idx % arr.length];
}

function buildMockProjects(query: string, count: number): Project[] {
	const baseTitles = [
		'AI Agent for Idea Discovery',
		'Open Source Dev Collaboration',
		'Sustainability Tracker',
		'Health Insights Platform',
		'Creative Coding Toolkit',
		'Community Knowledge Graph',
		'Realtime Collab Whiteboard',
		'XR Learning Playground',
		'FinTech Risk Dashboard',
		'Blockchain Research Hub',
		'LLM Prompt Marketplace',
		'Code Mentor Network',
		'Product Analytics Studio',
		'Campus Project Finder',
		'Edge AI Vision Kit',
		'Generative Art Studio',
		'Audio AI Workbench',
		'Open Data Explorer',
		'Crowdsourced Design Lab',
		'Autonomous Research Agent',
	];
	const baseTags = ['AI', 'Design', 'Collaboration', 'Education', 'Mobile', 'Web', 'Open Source', 'Research', 'Data', 'Analytics'];

	const projects: Project[] = Array.from({ length: count }).map((_, i) => {
		const titleCore = baseTitles[i % baseTitles.length];
		// Remove query suffix from generated titles
		const title = titleCore;
		const id = Number(`${Date.now()}${i}`);
		const tagA = pick(baseTags, i);
		const tagB = pick(baseTags, i + 3);
		const gradient = pick(gradientOptions, i);
		const style: Project['cardStyle'] = i % 3 === 0 ? 'text-only' : 'image';
		const ownerName = ['Alex Chen', 'Sarah Lee', 'Mike Johnson', 'Zoe Park', 'Ryan Kim'][i % 5];

		return {
			id,
			title,
			author: ownerName,
			collaborators: 1 + ((i * 3) % 6),
			description: 'Auto-generated mock result for AI search. Explore and open to view more details.',
			tags: [tagA, tagB],
			type: 'project',
			cardStyle: style,
			status: (['ongoing', 'finished', 'not_started'] as const)[i % 3],
			owner: {
				name: ownerName,
				age: 22 + (i % 20),
				gender: i % 2 === 0 ? 'Male' : 'Female',
				role: ['Developer', 'Designer', 'Researcher', 'PM'][i % 4],
				distance: 1 + (i % 15),
				avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(ownerName)}`,
				tags: [tagA, 'Team Player']
			},
			collaboratorsList: [],
			detailedDescription: 'This is a generated project card for demonstrating AI search results in the prototype.',
			startTime: 'Recently',
			currentProgress: 20 + (i % 75),
			content: 'Generated content for demonstration. Replace with real data when API is ready.',
			purpose: 'Connect with collaborators and iterate on ideas fast.',
			lookingFor: ['Frontend', 'Backend', 'Research'][i % 3] ? [pick(['Frontend Developer', 'Backend Engineer', 'Data Scientist'], i)] : [],
			links: [],
			media: style === 'image' ? [pick(placeholderImages, i)] : [],
			gradientBackground: gradient,
			background: style === 'image' ? pick(placeholderImages, i) : undefined,
		} as Project;
	});

	return projects;
}

// Mock data builder for AI-generated project ideas (3 cards per search)
function buildMockProjectIdeas(query: string): ProjectIdea[] {
	const baseIdeas = [
		{
			project_idea_title: "AI-Powered Study Assistant for College Students",
			project_scope: "Small team (2-4 people)",
			description: "An intelligent study planner that adapts to learning patterns and schedules, helping students optimize their study time and improve retention.",
			key_features: ["Personalized study schedules", "Progress tracking", "Smart reminders", "Learning analytics"],
			estimated_timeline: "4-6 weeks",
			difficulty_level: "Intermediate",
			required_skills: ["React", "Node.js", "Machine Learning basics", "UI/UX Design"],
			similar_examples: ["https://notion.so", "https://forestapp.cc"],
			relevance_score: 0.92
		},
		{
			project_idea_title: "Community-Driven Recipe Sharing Platform",
			project_scope: "Medium team (5-8 people)",
			description: "A social platform where home cooks can share recipes, get feedback, and discover new dishes from around the world.",
			key_features: ["Recipe creation tools", "Social sharing", "Rating system", "Search filters"],
			estimated_timeline: "8-12 weeks",
			difficulty_level: "Beginner",
			required_skills: ["HTML/CSS", "JavaScript", "Database design", "API integration"],
			similar_examples: ["https://allrecipes.com", "https://food52.com"],
			relevance_score: 0.87
		},
		{
			project_idea_title: "Smart Home Energy Monitor Dashboard",
			project_scope: "Small team (2-4 people)",
			description: "Real-time monitoring system for home energy consumption with actionable insights to reduce electricity bills.",
			key_features: ["Real-time monitoring", "Energy analytics", "Cost calculations", "Mobile alerts"],
			estimated_timeline: "6-8 weeks",
			difficulty_level: "Advanced",
			required_skills: ["IoT development", "Data visualization", "Backend systems", "Mobile development"],
			similar_examples: ["https://sense.com", "https://wiser.energy"],
			relevance_score: 0.95
		}
	];

	// Customize ideas based on search query
	return baseIdeas.map((idea, index) => ({
		...idea,
		// Remove query suffix from idea titles
		project_idea_title: idea.project_idea_title,
		relevance_score: Math.max(0.1, Math.min(1.0, idea.relevance_score + (Math.random() - 0.5) * 0.1))
	}));
}



export default function AISearchIntegrated({ onBackToMain, onOpenFilter, onOpenProject, onRecordLeftSwipe, onRecordRightSwipe, suppressMatchIndicator }: AISearchIntegratedProps) {
	const [searchQuery, setSearchQuery] = useState('');
	const [isLoading, setIsLoading] = useState(false);
	const [results, setResults] = useState<Project[]>([]);
	const [ideaResults, setIdeaResults] = useState<ProjectIdea[]>([]);
	const [hasSearched, setHasSearched] = useState(false);
	const [showSettings, setShowSettings] = useState(false);
	const [searchMode, setSearchMode] = useState<'basic' | 'multi-resources'>('basic');
	const [selectedIdea, setSelectedIdea] = useState<ProjectIdea | null>(null);
	// Swipe and grouping state (local visual state only)
	const [useServerData, setUseServerData] = useState<boolean>(false);
	// Right-swipe feedback state
	const [showSwipeAnimation, setShowSwipeAnimation] = useState(false);
	const [showMatchIndicator, setShowMatchIndicator] = useState(false);
	const [lastLikedProject, setLastLikedProject] = useState<Project | null>(null);
	const [lastResultsQuery, setLastResultsQuery] = useState('');
	useEffect(() => { setUseServerData(!!getAccessToken()); }, []);

	// 处理模式切换，清除搜索内容
	const handleModeChange = (mode: 'basic' | 'multi-resources') => {
		setSearchMode(mode);
		// 清除搜索相关状态
		setSearchQuery('');
		setResults([]);
		setIdeaResults([]);
		setHasSearched(false);
		setSelectedIdea(null);
	};

	const handleSearch = async () => {
		if (!searchQuery.trim()) return;
		// Snapshot the current query so banner and results are tied to this search
		const q = searchQuery;
		setIsLoading(true);
		setHasSearched(true);
		setResults([]);
		setIdeaResults([]);
		
		setTimeout(() => {
			if (searchMode === 'basic') {
				// Basic mode: return 20 project cards
				const generated = buildMockProjects(q, 20);
				setResults(generated);
			} else {
				// Agent mode: return 3 idea cards
				const generatedIdeas = buildMockProjectIdeas(q);
				setIdeaResults(generatedIdeas);
			}
			// Update banner with the query tied to these results
			setLastResultsQuery(q);
			setIsLoading(false);
		}, 1200);
	};

	const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === 'Enter') handleSearch();
	};

	// Map agent idea to a lightweight Project for main collections
	const mapIdeaToProject = (idea: ProjectIdea, idx: number): Project => ({
		id: Number(`${Date.now()}${idx}`),
		title: idea.project_idea_title,
		author: 'AI Agent',
		collaborators: 0,
		description: idea.description,
		tags: ['AI', 'Idea'],
		type: 'project',
		cardStyle: 'text-only',
		status: 'not_started',
		owner: { name: 'AI Agent', age: 25, gender: 'Non-binary', role: 'Agent', distance: 0, avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=agent`, tags: ['AI'] },
		collaboratorsList: [],
		detailedDescription: idea.description,
		startTime: 'Recently',
		currentProgress: 0,
		content: idea.description,
		purpose: 'Explore generated idea',
		lookingFor: [],
		links: idea.similar_examples,
		media: [],
		gradientBackground: 'bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700',
		background: undefined,
		videoUrl: undefined
	});

	// 修复的handleSwipe函数 - 与主页面保持一致的逻辑
	const handleSwipe = (direction: 'left' | 'right') => {
		const isBasic = searchMode === 'basic';
		const topItem = isBasic ? results[0] : ideaResults[0];
		if (!topItem) return;
		
		const projectToRecord: Project = isBasic ? (topItem as Project) : mapIdeaToProject(topItem as ProjectIdea, 0);
		
		// 只发送一次到后端（仅basic模式）
		if (isBasic && useServerData && direction === 'right') {
			try { void sendSwipe((projectToRecord as any).id, true); } catch {}
		}
		
		if (direction === 'right') {
			// 右滑反馈逻辑 - 与主页面完全一致
			if (suppressMatchIndicator) {
				// 显示简单的右侧动画
				setShowSwipeAnimation(true);
				setTimeout(() => {
					setShowSwipeAnimation(false);
				}, 800);
			} else {
				// 显示完整的匹配指示弹窗
				setLastLikedProject(projectToRecord);
				setShowMatchIndicator(true);
				// 3秒后自动隐藏指示
				setTimeout(() => {
					setShowMatchIndicator(false);
					setLastLikedProject(null);
				}, 3000);
			}
			
			// 记录右滑
			onRecordRightSwipe(projectToRecord);
		} else {
			// 记录左滑
			onRecordLeftSwipe(projectToRecord);
		}
		
		// 关键修复：与主页面保持一致的600ms延迟移除卡片
		setTimeout(() => {
			if (isBasic) {
				setResults(prev => prev.slice(1));
			} else {
				setIdeaResults(prev => prev.slice(1));
			}
		}, 600);
	};

	// Right-swipe feedback components (matching main page exactly)
	const SwipeFeedback = ({ direction, onComplete }: { direction: 'left' | 'right'; onComplete: () => void }) => {
		const randomEmoji = positiveEmojis[Math.floor(Math.random() * positiveEmojis.length)];
		
		if (direction === 'right') {
			return (
				<motion.div
					className="absolute inset-0 flex items-center justify-center pointer-events-none z-50"
					initial={{ opacity: 0, scale: 0 }}
					animate={{ opacity: 1, scale: 1 }}
					exit={{ opacity: 0, y: -100 }}
					transition={{ duration: 0.8, ease: "easeOut" }}
					onAnimationComplete={onComplete}
				>
					<div className="flex flex-col items-center gap-4">
						<motion.div
							className="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center"
							animate={{ 
								scale: [1, 1.2, 1],
								rotate: [0, 360]
							}}
							transition={{ 
								scale: { duration: 0.6, times: [0, 0.5, 1] },
								rotate: { duration: 0.8 }
							}}
						>
							<Check size={40} className="text-white" />
						</motion.div>
						<motion.div
							className="text-4xl"
							animate={{ 
								y: [0, -20, 0],
								scale: [1, 1.3, 1]
							}}
							transition={{ duration: 0.8, ease: "easeOut" }}
						>
							{randomEmoji}
						</motion.div>
					</div>
				</motion.div>
			);
		}
		
		return null;
	};

	const MatchIndicator = ({ project, onClose, onSuppress }: { project: Project; onClose: () => void; onSuppress: () => void }) => {
		return (
			<motion.div
				className="fixed inset-0 z-50 flex items-center justify-center bg-black/20"
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				exit={{ opacity: 0 }}
				onClick={onClose}
			>
				<motion.div
					className="bg-white rounded-2xl p-6 mx-4 max-w-sm shadow-2xl"
					initial={{ scale: 0.8, y: 50 }}
					animate={{ scale: 1, y: 0 }}
					exit={{ scale: 0.8, y: 50 }}
					transition={{ type: "spring", damping: 25, stiffness: 300 }}
					onClick={(e) => e.stopPropagation()}
				>
					<div className="text-center">
						<motion.div
							className="w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center mx-auto mb-4"
							animate={{ 
								scale: [1, 1.1, 1],
								rotate: [0, 5, -5, 0]
							}}
							transition={{ 
								scale: { duration: 1, repeat: Infinity, ease: "easeInOut" },
								rotate: { duration: 2, repeat: Infinity, ease: "easeInOut" }
							}}
						>
							<Check size={32} className="text-white" />
						</motion.div>
						
						<h3 className="text-xl font-bold text-gray-900 mb-2">
							已右滑项目
						</h3>
						
						<div className="bg-gray-50 rounded-lg p-3 mb-4">
							<h4 className="font-semibold text-gray-800 mb-1">{project.title}</h4>
							<p className="text-sm text-gray-600">{project.author}</p>
						</div>
						
						<p className="text-gray-600 text-sm leading-relaxed mb-4">
							等待对方也右滑你的项目来开启对话
						</p>
						
						<div className="flex items-center justify-center gap-2 text-blue-600 text-sm mb-4">
							<div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
							<span>双向匹配才能聊天</span>
							<div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
						</div>
						
						<button
							onClick={onSuppress}
							className="text-gray-500 text-xs hover:text-gray-700 transition-colors underline"
						>
							不再显示此提示
						</button>
					</div>
				</motion.div>
			</motion.div>
		);
	};

	const SwipeAnimation = () => {
		return (
			<motion.div
				className="pointer-events-none"
				initial={{ opacity: 0, x: 50 }}
				animate={{ opacity: 1, x: 0 }}
				exit={{ opacity: 0, x: 50 }}
				transition={{ duration: 0.2 }}
			>
				<motion.div
					className="bg-gradient-to-r from-blue-500 to-green-500 text-white p-2 rounded-full shadow-lg"
					initial={{ scale: 0.8 }}
					animate={{ scale: 1 }}
					exit={{ scale: 0.8 }}
					transition={{ duration: 0.2 }}
				>
					<Check size={30} />
				</motion.div>
			</motion.div>
		);
	};

	// Lightweight swipeable card renderers - matching main page exactly
	const baseCardClass = `w-[357px] h-[420px] rounded-[14px] overflow-hidden relative cursor-pointer`;
	const topShadow = `shadow-[0px_18px_40px_0px_rgba(0,0,0,0.30)]`;
	const underShadow = `shadow-[0px_8px_24px_0px_rgba(0,0,0,0.18)]`;

	const ProjectSwipeCard = ({ project, isTop }: { project: Project; isTop: boolean }) => {
		// Exact same tap/drag detection logic as main page
		const tapStartRef = useRef<{ x: number; y: number; t: number } | null>(null);
		const isDraggingRef = useRef<boolean>(false);
		const lastDxRef = useRef<number>(0);
		const handledRef = useRef<boolean>(false);

		const getPoint = (e: any) => {
			if (e.touches && e.touches[0]) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
			if (e.changedTouches && e.changedTouches[0]) return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
			return { x: e.clientX, y: e.clientY };
		};

		const handleDown = (e: any) => {
			const p = getPoint(e);
			tapStartRef.current = { x: p.x, y: p.y, t: Date.now() };
			isDraggingRef.current = false;
			lastDxRef.current = 0;
			handledRef.current = false;
		};

		const handleMove = (e: any) => {
			if (!tapStartRef.current) return;
			const p = getPoint(e);
			const dx = p.x - tapStartRef.current.x;
			const dy = p.y - tapStartRef.current.y;
			lastDxRef.current = dx;
			if (Math.abs(dx) > TAP_MAX_MOVEMENT_PX || Math.abs(dy) > TAP_MAX_MOVEMENT_PX) {
				isDraggingRef.current = true;
			}
		};

		const handleUp = (e: any) => {
			if (!tapStartRef.current) return;
			const p = getPoint(e);
			const dt = Date.now() - tapStartRef.current.t;
			const dx = Math.abs(p.x - tapStartRef.current.x);
			const dy = Math.abs(p.y - tapStartRef.current.y);
			const isTap = !isDraggingRef.current && dt <= TAP_MAX_DURATION_MS && dx <= TAP_MAX_MOVEMENT_PX && dy <= TAP_MAX_MOVEMENT_PX;
			tapStartRef.current = null;
			isDraggingRef.current = false;
			if (isTap) onOpenProject(project);
		};

		const resolveDir = (dir: string): 'left' | 'right' => {
			if (dir === 'left' || dir === 'right') return dir;
			return lastDxRef.current >= 0 ? 'right' : 'left';
		};

		return (
			<TinderCard
				className="absolute inset-0"
				key={project.id}
				onSwipe={(dir: string) => {
					if (!isTop) return; // Only handle swipes on the top card
					const mapped = resolveDir(dir);
					handledRef.current = true;
					handleSwipe(mapped); // 直接调用外部定义的handleSwipe
				}}
				onCardLeftScreen={() => {
					if (!isTop) return; // Only handle on top card
					if (!handledRef.current) {
						const mapped = lastDxRef.current >= 0 ? 'right' : 'left';
						handleSwipe(mapped); // 直接调用外部定义的handleSwipe
					}
					handledRef.current = false;
					lastDxRef.current = 0;
				}}
				preventSwipe={[ 'down', ...(isTop ? [] : ['left', 'right', 'up']) ]}
				swipeRequirementType={SWIPE_REQUIREMENT}
				swipeThreshold={SWIPE_THRESHOLD_PX}
			>
				<div className="absolute inset-0" style={{ zIndex: 999 }}>
					<div
						className={`${baseCardClass} ${isTop ? topShadow : underShadow} ${isTop ? 'hover:scale-[1.02] transition-transform duration-150 will-change-transform' : ''}`}
						onMouseDown={handleDown}
						onMouseMove={handleMove}
						onMouseUp={handleUp}
						onTouchStart={handleDown}
						onTouchMove={handleMove}
						onTouchEnd={handleUp}
					>
						{project.cardStyle === 'image' && project.background ? (
							<>
								<div className="absolute inset-0">
									<img src={project.background} alt={project.title} className="w-full h-full object-cover" />
								</div>
								<div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
								<div className="absolute bottom-0 left-0 right-0 p-6 text-white">
									<h2 className="text-[24px] font-bold leading-[28px] mb-2">{project.title}</h2>
									<p className="text-white/90 text-sm mb-2 leading-5">{project.description}</p>
									<div className="flex flex-wrap gap-2">
										{project.tags.map(tag => (
											<Badge key={tag} variant="secondary" className="text-xs bg-white/20 text-white border-white/30">{tag}</Badge>
										))}
									</div>
								</div>
							</>
						) : (
							<>
								<div className={`absolute inset-0 ${project.gradientBackground || 'bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700'}`} />
								<div className="absolute inset-0 bg-black/20" />
								<div className="absolute inset-0 p-6 text-white flex flex-col justify-center">
									<h2 className="text-[24px] font-bold leading-[28px] mb-2 text-center">{project.title}</h2>
									<p className="text-white/90 text-sm leading-5 text-center max-w-[85%] mx-auto">{project.description}</p>
								</div>
							</>
						)}
					</div>
				</div>
			</TinderCard>
		);
	};

	const IdeaSwipeCard = ({ idea, isTop, idx }: { idea: ProjectIdea; isTop: boolean; idx: number }) => {
		// Exact same tap/drag detection logic as main page
		const tapStartRef = useRef<{ x: number; y: number; t: number } | null>(null);
		const isDraggingRef = useRef<boolean>(false);
		const lastDxRef = useRef<number>(0);
		const handledRef = useRef<boolean>(false);

		const getPoint = (e: any) => {
			if (e.touches && e.touches[0]) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
			if (e.changedTouches && e.changedTouches[0]) return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
			return { x: e.clientX, y: e.clientY };
		};

		const handleDown = (e: any) => {
			const p = getPoint(e);
			tapStartRef.current = { x: p.x, y: p.y, t: Date.now() };
			isDraggingRef.current = false;
			lastDxRef.current = 0;
			handledRef.current = false;
		};

		const handleMove = (e: any) => {
			if (!tapStartRef.current) return;
			const p = getPoint(e);
			const dx = p.x - tapStartRef.current.x;
			const dy = p.y - tapStartRef.current.y;
			lastDxRef.current = dx;
			if (Math.abs(dx) > TAP_MAX_MOVEMENT_PX || Math.abs(dy) > TAP_MAX_MOVEMENT_PX) {
				isDraggingRef.current = true;
			}
		};

		const handleUp = (e: any) => {
			if (!tapStartRef.current) return;
			const p = getPoint(e);
			const dt = Date.now() - tapStartRef.current.t;
			const dx = Math.abs(p.x - tapStartRef.current.x);
			const dy = Math.abs(p.y - tapStartRef.current.y);
			const isTap = !isDraggingRef.current && dt <= TAP_MAX_DURATION_MS && dx <= TAP_MAX_MOVEMENT_PX && dy <= TAP_MAX_MOVEMENT_PX;
			tapStartRef.current = null;
			isDraggingRef.current = false;
			if (isTap) setSelectedIdea(idea);
		};

		const resolveDir = (dir: string): 'left' | 'right' => {
			if (dir === 'left' || dir === 'right') return dir;
			return lastDxRef.current >= 0 ? 'right' : 'left';
		};

		return (
			<TinderCard
				className="absolute inset-0"
				key={`${idea.project_idea_title}-${idx}`}
				onSwipe={(dir: string) => {
					if (!isTop) return; // Only handle swipes on the top card
					const mapped = resolveDir(dir);
					handledRef.current = true;
					handleSwipe(mapped); // 直接调用外部定义的handleSwipe
				}}
				onCardLeftScreen={() => {
					if (!isTop) return; // Only handle on top card
					if (!handledRef.current) {
						const mapped = lastDxRef.current >= 0 ? 'right' : 'left';
						handleSwipe(mapped); // 直接调用外部定义的handleSwipe
					}
					handledRef.current = false;
					lastDxRef.current = 0;
				}}
				preventSwipe={[ 'down', ...(isTop ? [] : ['left', 'right', 'up']) ]}
				swipeRequirementType={SWIPE_REQUIREMENT}
				swipeThreshold={SWIPE_THRESHOLD_PX}
			>
				<div className="absolute inset-0" style={{ zIndex: 999 }}>
					<div
						className={`${baseCardClass} ${isTop ? topShadow : underShadow} ${isTop ? 'hover:scale-[1.02] transition-transform duration-150 will-change-transform' : ''}`}
						onMouseDown={handleDown}
						onMouseMove={handleMove}
						onMouseUp={handleUp}
						onTouchStart={handleDown}
						onTouchMove={handleMove}
						onTouchEnd={handleUp}
					>
						<div className={`absolute inset-0 ${pick(gradientOptions, idx)}`} />
						<div className="absolute inset-0 bg-black/20" />
						<div className="absolute inset-0 p-6 text-white flex flex-col justify-center">
							<h2 className="text-[22px] font-bold leading-[26px] mb-2 text-center">{idea.project_idea_title}</h2>
							<p className="text-white/90 text-sm leading-5 text-center max-w-[85%] mx-auto line-clamp-3">{idea.description}</p>
						</div>
					</div>
				</div>
			</TinderCard>
		);
	};

	// ProjectIdeaDetailView component
	const ProjectIdeaDetailView = ({ idea, onClose }: { idea: ProjectIdea; onClose: () => void }) => {
		return (
			<motion.div
				className="absolute inset-0 bg-white z-50"
				initial={{ rotateY: 180, opacity: 0 }}
				animate={{ rotateY: 0, opacity: 1 }}
				exit={{ rotateY: 180, opacity: 0 }}
				transition={{ duration: 0.6, ease: "easeInOut" }}
			>
				<div className="w-full h-full flex flex-col">
					{/* Header */}
					<div className="h-[90px] flex items-center justify-between px-4 border-b border-[#E8EDF2] bg-[#FAFAFA]">
						<button onClick={onClose} className="p-2">
							<ArrowLeft size={24} className="text-blue-600" />
						</button>
						<h1 className="font-semibold flex-1 text-center">Idea Details</h1>
						<div className="w-10" />
					</div>

					<div className="flex-1 overflow-y-auto">
						<div className="space-y-6 p-6">
							{/* Title */}
							<div>
								<h2 className="text-3xl font-bold leading-tight mb-4">{idea.project_idea_title}</h2>
							</div>

							{/* Project Scope & Difficulty */}
							<div className="flex gap-4">
								<div className="flex-1 p-4 bg-blue-50 rounded-lg border border-blue-200">
									<h3 className="text-lg font-semibold text-blue-800 mb-2">Project Scope</h3>
									<p className="text-blue-700">{idea.project_scope}</p>
								</div>
								<div className="flex-1 p-4 bg-green-50 rounded-lg border border-green-200">
									<h3 className="text-lg font-semibold text-green-800 mb-2">Difficulty Level</h3>
									<p className="text-green-700">{idea.difficulty_level}</p>
								</div>
							</div>

							{/* Description */}
							<div>
								<h3 className="text-xl font-semibold mb-3">Description</h3>
								<p className="text-gray-700 leading-relaxed">{idea.description}</p>
							</div>

							{/* Key Features */}
							<div>
								<h3 className="text-xl font-semibold mb-3">Key Features</h3>
								<div className="grid grid-cols-2 gap-3">
									{idea.key_features.map((feature, index) => (
										<div key={index} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
											<div className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0 min-w-[6px] min-h-[6px]"></div>
											<span className="text-gray-700">{feature}</span>
										</div>
									))}
								</div>
							</div>

							{/* Timeline & Skills */}
							<div className="grid grid-cols-2 gap-6">
								<div>
									<h3 className="text-xl font-semibold mb-3">Estimated Timeline</h3>
									<div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
										<p className="text-orange-700 font-medium">{idea.estimated_timeline}</p>
									</div>
								</div>
								<div>
									<h3 className="text-xl font-semibold mb-3">Required Skills</h3>
									<div className="flex flex-wrap gap-2">
										{idea.required_skills.map((skill, index) => (
											<Badge key={index} variant="secondary" className="bg-purple-100 text-purple-800 border-purple-200">
												{skill}
											</Badge>
										))}
									</div>
								</div>
							</div>

							{/* Similar Examples */}
							<div>
								<h3 className="text-xl font-semibold mb-3">Similar Examples</h3>
								<div className="space-y-2">
									{idea.similar_examples.map((example, index) => (
										<a
											key={index}
											href={example}
											target="_blank"
											rel="noopener noreferrer"
											className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
										>
											<ExternalLink size={16} />
											{example}
										</a>
									))}
								</div>
							</div>

							{/* Relevance Score */}
							<div className="text-center p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
								<h3 className="text-lg font-semibold text-gray-800 mb-2">AI Relevance Score</h3>
								<div className="text-4xl font-bold text-blue-600">
									{Math.round(idea.relevance_score * 100)}%
								</div>
								<p className="text-gray-600 mt-2">This idea matches your search criteria</p>
							</div>
						</div>
					</div>
				</div>
			</motion.div>
		);
	};

	return (
		<div className="absolute inset-0 bg-white">
			{/* ProjectIdeaDetailView */}
			<AnimatePresence>
				{selectedIdea && (
					<ProjectIdeaDetailView
						idea={selectedIdea}
						onClose={() => setSelectedIdea(null)}
					/>
				)}
			</AnimatePresence>
			
			{/* Right-swipe feedback components */}
			<AnimatePresence>
				{showMatchIndicator && lastLikedProject && (
					<MatchIndicator
						project={lastLikedProject}
						onClose={() => {
							setShowMatchIndicator(false);
							setLastLikedProject(null);
						}}
						onSuppress={() => {
							// 在搜索页面中，我们只关闭当前弹窗，不修改全局设置
							// 全局suppressMatchIndicator设置由主页面管理
							setShowMatchIndicator(false);
							setLastLikedProject(null);
						}}
					/>
				)}
			</AnimatePresence>
			
			{/* Header: keep original buttons (settings + optional filter) */}
			<HeaderBar
				rightContent={(
					<>
						{/* 设置按钮 */}
						<button onClick={() => setShowSettings(true)} className="flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-full hover:bg-gray-100">
							<Settings className="w-6 h-6 text-black" />
						</button>
						{/* 筛选按钮 - 只在basic模式下显示 */}
						{searchMode === 'basic' && (
							<button onClick={onOpenFilter} className="flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-full">
								<div className="w-6 h-6">
									<svg className="block size-full" fill="none" viewBox="0 0 25 24">
										<path d={svgPaths.filter} stroke="#000000" strokeWidth="2" strokeMiterlimit="10" strokeLinecap="round" />
									</svg>
								</div>
							</button>
						)}
					</>
				)}
			/>

			{/* 设置抽屉 */}
					{showSettings && createPortal(
						<AnimatePresence>
							<motion.div
								className="fixed inset-0 z-[9999] bg-black/20"
								initial={{ opacity: 0 }}
								animate={{ opacity: 1 }}
								exit={{ opacity: 0 }}
								onClick={() => setShowSettings(false)}
							>
								<motion.div
									className="absolute bottom-0 left-0 right-0 w-[393px] h-auto mx-auto bg-white rounded-t-[32px] shadow-2xl z-[10000]"
									initial={{ y: "100%" }}
									animate={{ y: 0 }}
									exit={{ y: "100%" }}
									transition={{ type: "spring", damping: 25, stiffness: 300 }}
									onClick={(e) => e.stopPropagation()}
								>
									<div className="w-full h-full flex flex-col">
										{/* Header */}
										<div className="relative flex flex-col items-center justify-center pt-6 pb-4 border-b border-gray-100">
											<button 
												onClick={() => setShowSettings(false)}
												className="absolute left-4 p-2 text-[#0055F7] hover:text-[#0043C4] transition-colors"
											>
												<ArrowLeft size={24} />
											</button>
											<h1 className="text-2xl font-bold text-gray-900">{t('searchModeSettingsTitle') || 'Search Mode Settings'}</h1>
											<div className="text-gray-400 text-sm mt-2 px-14 text-center">{t('searchModeSettingsSubtitle') || 'Choose your search mode to customize how Ques finds results.'}</div>
										</div>

										{/* Content */}
										<div className="px-6 py-4 space-y-4">
											<div 
												className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
													searchMode === "basic" ? "border-blue-500 bg-blue-50" : "border-gray-200"
												}`}
												onClick={() => handleModeChange("basic")}
											>
												<div className="flex items-center justify-between">
													<div>
														<h3 className="text-lg font-semibold">{t('searchModeTitle') || 'Search Mode'}</h3>
														<p className="text-sm text-gray-600 mt-1">
															{t('searchModeDesc') || 'Search projects within the platform'}
														</p>
													</div>
													<div className={`w-4 h-4 rounded-full border-2 ${
														searchMode === "basic" ? "border-blue-500 bg-blue-500" : "border-gray-300"
													}`}/>
												</div>
											</div>

											<div 
												className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
													searchMode === "multi-resources" ? "border-blue-500 bg-blue-50" : "border-gray-200"
												}`}
												onClick={() => handleModeChange("multi-resources")}
											>
												<div className="flex items-center justify-between">
													<div className="flex-1">
														<div className="flex items-center gap-2">
															<h3 className="text-lg font-semibold">{t('agentModeTitle') || 'Agent Mode'}</h3>
															<Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
															<Badge variant="secondary" className="text-xs">PRO</Badge>
														</div>
														<p className="text-sm text-gray-600 mt-1">
															{t('agentModeDesc') || 'Use LLM to search the web for relevant ideas'}
														</p>
													</div>
													<div className={`w-4 h-4 rounded-full border-2 ${
														searchMode === "multi-resources" ? "border-blue-500 bg-blue-500" : "border-gray-300"
													}`}/>
												</div>
											</div>
										</div>

										{/* Bottom Action */}
										<div className="px-6 pb-4 pt-3 border-t border-gray-100">
											<Button 
												className="w-full py-4 bg-gradient-to-r from-[#0055F7] to-[#0043C4] text-white rounded-full font-semibold text-lg shadow-lg hover:from-[#0043C4] hover:to-[#0032A3] transition-all duration-300 transform hover:scale-105" 
												onClick={() => setShowSettings(false)}
											>
												{t('applySettings') || 'Apply Settings'}
											</Button>
										</div>
									</div>
								</motion.div>
							</motion.div>
						</AnimatePresence>, document.body)}

			{/* Search content area */}
			<div className="flex-1 overflow-hidden px-4" style={{ height: 'calc(100% - 90px - 96px)' }}>
				<AnimatePresence>
					{hasSearched && (
						<motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
							<p className="text-gray-700">
								<span className="text-blue-600">
									{searchMode === 'basic' ? (t('youSearchedFor') || 'You searched for:') : (t('aiSearchedIdeasFor') || 'AI searched ideas for:')}
								</span> "{lastResultsQuery}"
							</p>
						</motion.div>
					)}
				</AnimatePresence>
				{/* Swipe stack between banner and search bar */}
				<div className="h-[440px] flex items-center justify-center">
					{isLoading ? (
						<div className="w-[357px] h-[420px] rounded-[14px] bg-gray-200 animate-pulse" />
					) : hasSearched && ((searchMode === 'basic' ? results.length : ideaResults.length) > 0) ? (
						<div className="relative w-[357px] h-[420px]">
							{(searchMode === 'basic' ? results.slice(0, 2) : ideaResults.slice(0, 2)).map((item: any, i: number) => {
								const isTop = i === 0;
								return (
									<motion.div 
										key={(searchMode === 'basic' ? item.id : `${item.project_idea_title}-${i}`)} 
										className={`absolute inset-0 ${!isTop ? 'pointer-events-none' : ''}`} 
										style={{ zIndex: isTop ? 2 : 1 }} 
										initial={false} 
										animate={isTop ? { scale: 1, y: 0 } : { scale: 0.94, y: 12 }} 
										transition={isTop ? { type: 'spring', stiffness: 260, damping: 26 } : { type: 'spring', stiffness: 180, damping: 24 }}
									>
										{searchMode === 'basic' ? (
											<ProjectSwipeCard project={item as Project} isTop={isTop} />
										) : (
											<IdeaSwipeCard idea={item as ProjectIdea} isTop={isTop} idx={i} />
										)}
									</motion.div>
								);
							})}
							
							{/* Simple right-swipe animation overlay */}
							<AnimatePresence>
								{showSwipeAnimation && (
									<div className="absolute inset-0 pointer-events-none z-50 flex items-center justify-end pr-4">
										<SwipeAnimation />
									</div>
								)}
							</AnimatePresence>
								</div>
					) : hasSearched ? (
						<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center w-full text-gray-500">
							<Search size={48} className="mb-4 text-gray-300" />
							<p>{t('noResults') || `No ${searchMode === 'basic' ? 'projects' : 'ideas'} found. Try a different search term.`}</p>
						</motion.div>
					) : (
						<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center w-full text-gray-500">
							<Search size={48} className="mb-4 text-gray-300" />
							<h3 className="text-xl mb-2">{t('aiProjectSearchTitle') || 'AI Project Search'}</h3>
							<p className="text-center max-w-md">
								{searchMode === 'basic' 
									? (t('aiProjectSearchBasic') || "Describe what kind of project or collaborator you're looking for, and our AI will find the perfect matches.")
									: (t('aiProjectSearchAgent') || "Describe your project idea and our AI will generate innovative project concepts and suggestions.")
								}
							</p>
						</motion.div>
					)}
				</div>
			</div>

			{/* Search bar docked above main bottom nav */}
			<motion.div initial={{ y: 100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="absolute bg-white border-t border-gray-200 p-6 shadow-lg" style={{ bottom: '96px', left: 0, right: 0, height: '96px' }}>
				<div className="flex items-center gap-3 mx-auto w-[357px]">
					<div className="flex-1 relative">
						<Input 
							value={searchQuery} 
							onChange={(e) => setSearchQuery(e.target.value)} 
							onKeyDown={handleKeyPress} 
							placeholder={searchMode === 'basic' ? (t('searchBarPlaceholderBasic') || 'Ask AI to find projects or collaborators...') : (t('searchBarPlaceholderAgent') || 'Describe your project idea for AI suggestions...')} 
							className="pr-12 h-12 rounded-full border-2 border-gray-200 bg-gray-50 focus-visible:!border-blue-500 focus-visible:!ring-2 focus-visible:!ring-blue-500/20 focus-visible:!ring-offset-0" 
							disabled={isLoading} 
						/>
						<div className="absolute right-3 top-1/2 -translate-y-1/2">
							<Search size={20} className="text-gray-400" />
						</div>
					</div>
					<button onClick={handleSearch} disabled={!searchQuery.trim() || isLoading} className="h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center">
						{isLoading ? (
							<motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }} className="w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
						) : (
							<Send size={20} className="text-white" />
						)}
					</button>
				</div>
			</motion.div>
		</div>
	);
} 