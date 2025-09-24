import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring, PanInfo } from 'framer-motion';
import { Send, Search, Settings, ArrowLeft, ExternalLink, Check, ChevronDown, ChevronUp } from 'lucide-react';
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
import { t, currentLanguage as i18nCurrentLanguage } from '../translations';

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
	
	// 新增：搜索状态持久化
	searchQuery: string;
	setSearchQuery: (query: string) => void;
	searchMode: 'basic' | 'multi-resources';
	setSearchMode: (mode: 'basic' | 'multi-resources') => void;
	results: Project[];
	setResults: (results: Project[]) => void;
	ideaResults: any[];
	setIdeaResults: (results: any[]) => void;
	hasSearched: boolean;
	setHasSearched: (searched: boolean) => void;
	lastResultsQuery: string;
	setLastResultsQuery: (query: string) => void;
	
	// 思考流状态持久化
	showThinkingStream: boolean;
	setShowThinkingStream: (show: boolean) => void;
	thinkingStreamCollapsed: boolean;
	setThinkingStreamCollapsed: (collapsed: boolean) => void;
	thinkingQuery: string;
	setThinkingQuery: (query: string) => void;
	thinkingSteps: any[];
	setThinkingSteps: (steps: any[]) => void;
	currentStepIndex: number;
	setCurrentStepIndex: (index: number) => void;
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

// 新增：思考步骤接口
interface ThinkingStep {
	id: string;
	content: string;
	timestamp: number;
	completed: boolean;
}



export default function AISearchIntegrated({ onBackToMain, onOpenFilter, onOpenProject, onRecordLeftSwipe, onRecordRightSwipe, suppressMatchIndicator, searchQuery, setSearchQuery, searchMode, setSearchMode, results, setResults, ideaResults, setIdeaResults, hasSearched, setHasSearched, lastResultsQuery, setLastResultsQuery, showThinkingStream, setShowThinkingStream, thinkingStreamCollapsed, setThinkingStreamCollapsed, thinkingQuery, setThinkingQuery, thinkingSteps, setThinkingSteps, currentStepIndex, setCurrentStepIndex }: AISearchIntegratedProps) {
	// 本地状态（不需要持久化）
	const [isSearching, setIsSearching] = useState(false);
	const [selectedProject, setSelectedProject] = useState<Project | null>(null);
	const [selectedIdea, setSelectedIdea] = useState<ProjectIdea | null>(null);
	const [useServerData] = useState(!!getAccessToken());
	const [showSettings, setShowSettings] = useState(false);

	// 生成思考步骤的函数
	const generateThinkingSteps = (query: string): ThinkingStep[] => {
		return [
			{
				id: '1',
				content: `正在分析你的搜索关键词："${query}"...`,
				timestamp: Date.now(),
				completed: false
			},
			{
				id: '2',
				content: '识别项目领域和技术栈需求...',
				timestamp: Date.now() + 800,
				completed: false
			},
			{
				id: '3', 
				content: '搜索相关的开源项目和案例...',
				timestamp: Date.now() + 1600,
				completed: false
			},
			{
				id: '4',
				content: '分析技术可行性和难度等级...',
				timestamp: Date.now() + 2400,
				completed: false
			},
			{
				id: '5',
				content: '生成个性化项目建议...',
				timestamp: Date.now() + 3200,
				completed: false
			}
		];
	};

	// 修复：使用ref而不是state来跟踪处理状态，避免竞争条件
	const isSwipeHandledRef = useRef(false);
	
	// 右滑反馈状态
	const [showMatchIndicator, setShowMatchIndicator] = useState(false);
	const [lastLikedProject, setLastLikedProject] = useState<Project | null>(null);
	const [showSwipeAnimation, setShowSwipeAnimation] = useState(false);

	useEffect(() => {
		isSwipeHandledRef.current = false;
		// 同时清除任何正在进行的弹窗状态
		setShowMatchIndicator(false);
		setShowSwipeAnimation(false);
		setLastLikedProject(null);
	}, [results, ideaResults, searchMode]);

	// 思考流逻辑
	useEffect(() => {
		if (showThinkingStream && !thinkingStreamCollapsed && thinkingQuery && thinkingSteps.length === 0) {
			const steps = generateThinkingSteps(thinkingQuery);
			setThinkingSteps(steps);
			setCurrentStepIndex(0);

			// 逐步显示每个思考步骤
			let currentIndex = 0;
			const timer = setInterval(() => {
				currentIndex++;
				if (currentIndex >= steps.length) {
					clearInterval(timer);
					// 标记所有步骤为已完成
					const completedSteps = steps.map(step => ({ ...step, completed: true }));
					setThinkingSteps(completedSteps);
					setCurrentStepIndex(currentIndex - 1);
				} else {
					setCurrentStepIndex(currentIndex);
				}
			}, 800);

			return () => clearInterval(timer);
		}
	}, [showThinkingStream, thinkingStreamCollapsed, thinkingQuery, thinkingSteps.length]);

	// 处理模式切换，清除搜索内容
	const handleModeChange = (mode: 'basic' | 'multi-resources') => {
		setSearchMode(mode);
		// 清除搜索相关状态
		setSearchQuery('');
		setResults([]);
		setIdeaResults([]);
		setHasSearched(false);
		setSelectedProject(null);
		setSelectedIdea(null);
		// 新增：清除思考流状态
		setShowThinkingStream(false);
		setThinkingStreamCollapsed(false);
		setThinkingQuery('');
		setThinkingSteps([]);
		setCurrentStepIndex(0);
	};

	const handleSearch = async () => {
		if (!searchQuery.trim()) return;
		// Snapshot the current query so banner and results are tied to this search
		const q = searchQuery;
		setIsSearching(true);
		setHasSearched(true);
		setResults([]);
		setIdeaResults([]);
		
		// 清除滑动相关状态
		isSwipeHandledRef.current = false;
		setShowMatchIndicator(false);
		setShowSwipeAnimation(false);
		setLastLikedProject(null);
		
		// 新增：在agent模式下显示思考流
		if (searchMode === 'multi-resources') {
			setThinkingQuery(q);
			setShowThinkingStream(true);
			setThinkingStreamCollapsed(false);
		}
		
		setTimeout(() => {
			if (searchMode === 'basic') {
				// Basic mode: return 20 project cards
				const generated = buildMockProjects(q, 20);
				setResults(generated);
			} else {
				// Agent mode: return 3 idea cards
				const generatedIdeas = buildMockProjectIdeas(q);
				setIdeaResults(generatedIdeas);
				// 新增：当结果返回时，确保所有思考流步骤都标记为完成
				const completedSteps = thinkingSteps.map(step => ({ ...step, completed: true }));
				setThinkingSteps(completedSteps);
				// 设置currentStepIndex为步骤总数，表示全部完成
				setCurrentStepIndex(completedSteps.length);
				// 自动折叠思考流
				setThinkingStreamCollapsed(true);
			}
			// Update banner with the query tied to these results
			setLastResultsQuery(q);
			setIsSearching(false);
		}, 1200); // 恢复原本的搜索时间
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
		console.log('📱 AI Search handleSwipe - called', { 
			direction, 
			isSwipeHandled: isSwipeHandledRef.current, 
			searchMode, 
			basicResultsCount: results.length,
			ideaResultsCount: ideaResults.length 
		});

		// 防止重复处理同一次滑动
		if (isSwipeHandledRef.current) {
			console.log('⚠️ AI Search handleSwipe - already handled, skipping');
			return;
		}
		isSwipeHandledRef.current = true;
		
		const isBasic = searchMode === 'basic';
		const topItem = isBasic ? results[0] : ideaResults[0];
		if (!topItem) {
			console.log('❌ AI Search handleSwipe - no top item found');
			isSwipeHandledRef.current = false;
			return;
		}
		
		const projectToRecord: Project = isBasic ? (topItem as Project) : mapIdeaToProject(topItem as ProjectIdea, 0);
		console.log('📋 AI Search handleSwipe - processing item', { 
			isBasic, 
			itemTitle: isBasic ? (topItem as Project).title : (topItem as ProjectIdea).project_idea_title,
			direction 
		});
		
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
		
		// 🎯 关键修复：与主页面一致，在handleSwipe中延迟移除卡片
		setTimeout(() => {
			if (isBasic) {
				const prevCount = results.length;
				const newResults = results.length > 0 ? results.slice(1) : results;
				setResults(newResults);
				console.log('📝 AI Search handleSwipe - removed basic card (600ms delay)', { prevCount, newCount: prevCount - 1 });
			} else {
				const prevCount = ideaResults.length;
				const newIdeaResults = ideaResults.length > 0 ? ideaResults.slice(1) : ideaResults;
				setIdeaResults(newIdeaResults);
				console.log('💡 AI Search handleSwipe - removed idea card (600ms delay)', { prevCount, newCount: prevCount - 1 });
			}
			// 重置防抖状态，允许下一张卡片的滑动
			isSwipeHandledRef.current = false;
			console.log('🔄 AI Search handleSwipe - reset isSwipeHandled to false (delayed)');
		}, 600);
		
		console.log('✅ AI Search handleSwipe - completed, card will be removed in 600ms');
	};
	
	// 处理卡片飞出屏幕事件 - 简化为不做任何操作，让handleSwipe处理一切
	const handleCardLeftScreen = () => {
		console.log('🚪 AI Search handleCardLeftScreen - called (no action needed)', { 
			searchMode, 
			basicResultsCount: results.length,
			ideaResultsCount: ideaResults.length,
			isSwipeHandled: isSwipeHandledRef.current 
		});
		// 不做任何操作，卡片移除由handleSwipe中的setTimeout处理
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
					className="bg-white rounded-2xl p-5 mx-4 w-[320px] max-w-[320px] shadow-2xl"
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
							{i18nCurrentLanguage === 'en' ? 'Project liked' : '已右滑项目'}
						</h3>
						
						<div className="bg-gray-50 rounded-lg p-3 mb-4">
							<h4 className="font-semibold text-gray-800 mb-1">{project.title}</h4>
							<p className="text-sm text-gray-600">{project.author}</p>
						</div>
						
						<p className="text-gray-600 text-sm leading-relaxed mb-4 px-1">
							{i18nCurrentLanguage === 'en' ? 'Waiting for the other party to like your project as well to start a chat' : '等待对方也右滑你的项目来开启对话'}
						</p>
						
						<div className="flex items-center justify-center gap-2 text-blue-600 text-xs mb-4 px-1">
							<div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
							<span className="text-center">{i18nCurrentLanguage === 'en' ? 'Both sides must like to chat' : '双向匹配才能聊天'}</span>
							<div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
						</div>
						
						<button
							onClick={onSuppress}
							className="text-gray-500 text-xs hover:text-gray-700 transition-colors underline px-1"
						>
							{i18nCurrentLanguage === 'en' ? "Don't show this hint again" : '不再显示此提示'}
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

	const ProjectSwipeCard = ({ project, isTop, onOpenProject }: { project: Project; isTop: boolean; onOpenProject: (project: Project) => void }) => {
		// 完整的飞出动画状态管理，与主页面保持一致
		const [exitX, setExitX] = useState(0);
		const [exitY, setExitY] = useState(0);
		const [exitRotate, setExitRotate] = useState(0);
		const [isExiting, setIsExiting] = useState(false);
		const x = useMotionValue(0);
		const y = useMotionValue(0);
		const rotateTransform = useTransform(x, [-200, 0, 200], [-20, 0, 20]);
		const rotate = useSpring(
			isExiting ? exitRotate : rotateTransform,
			{ stiffness: 300, damping: 20 }
		);
		
		// 重置卡片状态的函数
		const resetCardState = () => {
			setIsExiting(false);
			setExitX(0);
			setExitY(0);
			setExitRotate(0);
			x.set(0);
			y.set(0);
		};
		
		// 重置卡片状态当项目ID变化时
		useEffect(() => {
			resetCardState();
		}, [project.id]);
		
		// Badge overlay system (DOM-driven, matching main page)
		const captureRef = useRef<HTMLDivElement | null>(null);
		const badgeStartRef = useRef<{ x: number; y: number } | null>(null);
		const badgeRafRef = useRef<number | null>(null);
		const pickRef = useRef<HTMLDivElement | null>(null);
		const passRef = useRef<HTMLDivElement | null>(null);
		const glowRef = useRef<HTMLDivElement | null>(null);
		const overlaysVisibleRef = useRef<boolean>(false);
		const initialCardTransformRef = useRef<string>('');

		// Capture initial inline transform of the inner card once
		useEffect(() => {
			const el = captureRef.current;
			if (el && !initialCardTransformRef.current) {
				initialCardTransformRef.current = el.style.transform || '';
			}
		}, []);

		const updateBadgeStyles = (dx: number) => {
			const pick = pickRef.current;
			const pass = passRef.current;
			const glow = glowRef.current;
			const cardEl = captureRef.current;
			if (!pick || !pass || !glow) return;
			const show = Math.abs(dx) > 8;
			if (!show) {
				pick.style.opacity = '0';
				pass.style.opacity = '0';
				glow.style.boxShadow = 'none';
				if (cardEl) cardEl.style.transform = initialCardTransformRef.current || '';
				return;
			}
			const rightIntensity = Math.max(0, Math.min(1, (dx - 8) / 28));
			const leftIntensity = Math.max(0, Math.min(1, (-dx - 8) / 28));
			pick.style.opacity = String(rightIntensity);
			pick.style.transform = `rotate(-12deg) scale(${1 + Math.max(0, Math.min(1, dx / 70)) * 0.06})`;
			pass.style.opacity = String(leftIntensity);
			pass.style.transform = `rotate(12deg) scale(${1 + Math.max(0, Math.min(1, -dx / 70)) * 0.06})`;
			glow.style.boxShadow = dx > 10
				? `inset 24px 0 96px -36px rgba(34,197,94,${Math.max(0, Math.min(0.70, (dx - 10) / 110))}), inset -24px 0 96px -36px rgba(59,130,246,${Math.max(0, Math.min(0.55, (dx - 10) / 110))})`
				: dx < -10
				? `inset -24px 0 96px -36px rgba(244,63,94,${Math.max(0, Math.min(0.70, (-dx - 10) / 110))}), inset 24px 0 96px -36px rgba(168,85,247,${Math.max(0, Math.min(0.55, (-dx - 10) / 110))})`
				: 'none';

			// Dynamic tilt of the inner card (rotate with drag direction)
			if (cardEl) {
				const clamped = Math.max(-14, Math.min(14, dx / 8));
				const base = initialCardTransformRef.current || '';
				const baseTrimmed = base.trim();
				const sep = baseTrimmed && !baseTrimmed.endsWith(')') ? ' ' : baseTrimmed ? ' ' : '';
				cardEl.style.transform = `${baseTrimmed}${sep}rotate(${clamped}deg)`;
			}
		};

		// Passive, global listeners to drive badge only (no React state, no swipe interference)
		useEffect(() => {
			const getXY = (e: any) => ({
				x: e?.clientX ?? e?.touches?.[0]?.clientX ?? e?.changedTouches?.[0]?.clientX,
				y: e?.clientY ?? e?.touches?.[0]?.clientY ?? e?.changedTouches?.[0]?.clientY,
			});
			const onDown = (e: any) => {
				const cardEl = captureRef.current;
				if (!cardEl) return;
				if (!cardEl.contains(e.target as Node)) return;
				const p = getXY(e);
				if (typeof p.x !== 'number') return;
				badgeStartRef.current = { x: p.x, y: p.y };
				overlaysVisibleRef.current = true;
				// reset styles immediate
				updateBadgeStyles(0);
			};
			const onMove = (e: any) => {
				if (!badgeStartRef.current || !overlaysVisibleRef.current) return;
				const p = getXY(e);
				if (typeof p.x !== 'number') return;
				const bdx = p.x - badgeStartRef.current.x;
				if (badgeRafRef.current) cancelAnimationFrame(badgeRafRef.current!);
				badgeRafRef.current = requestAnimationFrame(() => updateBadgeStyles(bdx));
			};
			const onUp = () => {
				badgeStartRef.current = null;
				if (badgeRafRef.current) cancelAnimationFrame(badgeRafRef.current);
				badgeRafRef.current = null;
				overlaysVisibleRef.current = false;
				updateBadgeStyles(0);
			};
			window.addEventListener('pointerdown', onDown, { passive: true, capture: true } as any);
			window.addEventListener('pointermove', onMove, { passive: true, capture: true } as any);
			window.addEventListener('pointerup', onUp, { passive: true, capture: true } as any);
			window.addEventListener('touchstart', onDown as any, { passive: true, capture: true } as any);
			window.addEventListener('touchmove', onMove as any, { passive: true, capture: true } as any);
			window.addEventListener('touchend', onUp as any, { passive: true, capture: true } as any);
			return () => {
				window.removeEventListener('pointerdown', onDown as any, true);
				window.removeEventListener('pointermove', onMove as any, true);
				window.removeEventListener('pointerup', onUp as any, true);
				window.removeEventListener('touchstart', onDown as any, true);
				window.removeEventListener('touchmove', onMove as any, true);
				window.removeEventListener('touchend', onUp as any, true);
			};
		}, []);
		
		// 统一"点击 vs 拖动"判断逻辑
		const tapStartRef = useRef<{ x: number; y: number; t: number } | null>(null);
		const isDraggingRef = useRef<boolean>(false);
		const lastDxRef = useRef<number>(0);
		const handledRef = useRef<boolean>(false);

		const getPoint = (e: any) => {
			if (e.touches && e.touches[0]) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
			if (e.changedTouches && e.changedTouches[0]) return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
			return { x: e.clientX, y: e.clientY };
		};

		const onCardPointerDown = (e: any) => {
			if (!isTop) return;
			const p = getPoint(e);
			tapStartRef.current = { x: p.x, y: p.y, t: Date.now() };
			isDraggingRef.current = false;
			lastDxRef.current = 0;
			handledRef.current = false;
			console.log('🔽 AI Search Card - Pointer Down', { isTop, project: project.title });
		};

		const onCardPointerMove = (e: any) => {
			if (!tapStartRef.current || !isTop) return;
			const p = getPoint(e);
			const dx = p.x - tapStartRef.current.x;
			const dy = p.y - tapStartRef.current.y;
			lastDxRef.current = dx;
			if (Math.abs(dx) > TAP_MAX_MOVEMENT_PX || Math.abs(dy) > TAP_MAX_MOVEMENT_PX) {
				isDraggingRef.current = true;
			}
		};

		const onCardPointerUp = (e: any) => {
			if (!tapStartRef.current || !isTop) return;
			const p = getPoint(e);
			const dt = Date.now() - tapStartRef.current.t;
			const dx = Math.abs(p.x - tapStartRef.current.x);
			const dy = Math.abs(p.y - tapStartRef.current.y);
			const isTap = !isDraggingRef.current && dt <= TAP_MAX_DURATION_MS && dx <= TAP_MAX_MOVEMENT_PX && dy <= TAP_MAX_MOVEMENT_PX;
			console.log('🔺 AI Search Card - Pointer Up', { 
				isTop, 
				project: project.title, 
				isDragging: isDraggingRef.current, 
				dt, dx, dy, 
				isTap, 
				lastDx: lastDxRef.current 
			});
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
					if (!isTop) return; // 只处理顶部卡片
					const mapped = resolveDir(dir);
					console.log('🚀 AI Search Card - onSwipe triggered', { 
						isTop, 
						project: project.title, 
						originalDir: dir, 
						mappedDir: mapped,
						lastDx: lastDxRef.current,
						swipeRequirementType: SWIPE_REQUIREMENT,
						swipeThreshold: SWIPE_THRESHOLD_PX
					});
					handledRef.current = true;
					
					// 触发飞出动画
					const direction = mapped === 'right' ? 1 : -1;
					const currentRotation = rotateTransform.get();
					setExitRotate(currentRotation);
					setIsExiting(true);
					setExitX(direction * 1200);
					setExitY(0);
					
					// 调用处理函数
					handleSwipe(mapped);
				}}
				onCardLeftScreen={() => {
					if (!isTop) return; // 只处理顶部卡片
					console.log('👋 AI Search Card - onCardLeftScreen triggered', { 
						isTop, 
						project: project.title, 
						wasHandled: handledRef.current 
					});
					if (!handledRef.current) {
						const mapped = lastDxRef.current >= 0 ? 'right' : 'left';
						console.log('🔄 AI Search Card - handling missed swipe', { mapped, lastDx: lastDxRef.current });
						handleSwipe(mapped);
					}
					handleCardLeftScreen(); // 仅用于日志记录
					handledRef.current = false;
					lastDxRef.current = 0;
				}}
				preventSwipe={[ 'down', ...(isTop ? [] : ['left', 'right', 'up']) ]}
				swipeRequirementType={SWIPE_REQUIREMENT}
				swipeThreshold={SWIPE_THRESHOLD_PX}
			>
				<motion.div
					className={`${baseCardClass} ${isTop ? topShadow : underShadow}`}
					ref={captureRef}
					style={{
						x: isExiting ? exitX : x,
						y: isExiting ? exitY : y,
						rotate: rotate
					}}
					animate={isExiting ? {
						x: exitX,
						y: exitY,
						rotate: exitRotate
					} : undefined}
					transition={isExiting ? {
						type: "tween",
						duration: 0.6,
						ease: "easeOut"
					} : undefined}
					onMouseDown={onCardPointerDown}
					onMouseMove={onCardPointerMove}
					onMouseUp={onCardPointerUp}
					onTouchStart={onCardPointerDown}
					onTouchMove={onCardPointerMove}
					onTouchEnd={onCardPointerUp}
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

					{/* Swipe overlays (DOM refs, pointer-events none) */}
					{isTop && (
						<>
							{/* PICK (right) */}
							<div
								ref={pickRef}
								className="absolute top-6 left-6 z-[1000] select-none pointer-events-none"
								style={{
									opacity: 0,
									transform: 'rotate(-12deg) scale(1)',
									filter: 'drop-shadow(0 0 12px rgba(16,185,129,0.55)) drop-shadow(0 0 24px rgba(59,130,246,0.35))',
								}}
							>
								<div className="px-4 py-2 rounded-xl border-4 text-white font-extrabold tracking-widest uppercase backdrop-blur-sm pointer-events-none"
									 style={{
										 background: 'linear-gradient(135deg, rgba(34,197,94,0.42) 0%, rgba(59,130,246,0.42) 100%)',
										 borderColor: 'rgba(34,197,94,1)',
									 }}
								>
									Pick
								</div>
							</div>

							{/* PASS (left) */}
							<div
								ref={passRef}
								className="absolute top-6 right-6 z-[1000] select-none pointer-events-none"
								style={{
									opacity: 0,
									transform: 'rotate(12deg) scale(1)',
									filter: 'drop-shadow(0 0 12px rgba(244,63,94,0.55)) drop-shadow(0 0 24px rgba(168,85,247,0.35))',
								}}
							>
								<div className="px-4 py-2 rounded-xl border-4 text-white font-extrabold tracking-widest uppercase backdrop-blur-sm pointer-events-none"
									 style={{
										 background: 'linear-gradient(135deg, rgba(244,63,94,0.42) 0%, rgba(168,85,247,0.42) 100%)',
										 borderColor: 'rgba(244,63,94,1)',
									 }}
								>
									Pass
								</div>
							</div>

							{/* dynamic edge glow */}
							<div
								ref={glowRef}
								className="pointer-events-none absolute inset-0 z-[900]"
								style={{ boxShadow: 'none', transition: 'box-shadow 80ms linear' }}
							/>
						</>
					)}
				</motion.div>
			</TinderCard>
		);
	};

	const IdeaSwipeCard = ({ idea, isTop, idx }: { idea: ProjectIdea; isTop: boolean; idx: number }) => {
		// 完整的飞出动画状态管理，与主页面保持一致
		const [exitX, setExitX] = useState(0);
		const [exitY, setExitY] = useState(0);
		const [exitRotate, setExitRotate] = useState(0);
		const [isExiting, setIsExiting] = useState(false);
		const x = useMotionValue(0);
		const y = useMotionValue(0);
		const rotateTransform = useTransform(x, [-200, 0, 200], [-20, 0, 20]);
		const rotate = useSpring(
			isExiting ? exitRotate : rotateTransform,
			{ stiffness: 300, damping: 20 }
		);
		
		// 重置卡片状态的函数
		const resetCardState = () => {
			setIsExiting(false);
			setExitX(0);
			setExitY(0);
			setExitRotate(0);
			x.set(0);
			y.set(0);
		};
		
		// 重置卡片状态当想法ID变化时
		useEffect(() => {
			resetCardState();
		}, [idea.project_idea_title]);
		
		// Badge overlay system (DOM-driven, matching main page)
		const captureRef = useRef<HTMLDivElement | null>(null);
		const badgeStartRef = useRef<{ x: number; y: number } | null>(null);
		const badgeRafRef = useRef<number | null>(null);
		const pickRef = useRef<HTMLDivElement | null>(null);
		const passRef = useRef<HTMLDivElement | null>(null);
		const glowRef = useRef<HTMLDivElement | null>(null);
		const overlaysVisibleRef = useRef<boolean>(false);
		const initialCardTransformRef = useRef<string>('');

		// Capture initial inline transform of the inner card once
		useEffect(() => {
			const el = captureRef.current;
			if (el && !initialCardTransformRef.current) {
				initialCardTransformRef.current = el.style.transform || '';
			}
		}, []);

		const updateBadgeStyles = (dx: number) => {
			const pick = pickRef.current;
			const pass = passRef.current;
			const glow = glowRef.current;
			const cardEl = captureRef.current;
			if (!pick || !pass || !glow) return;
			const show = Math.abs(dx) > 8;
			if (!show) {
				pick.style.opacity = '0';
				pass.style.opacity = '0';
				glow.style.boxShadow = 'none';
				if (cardEl) cardEl.style.transform = initialCardTransformRef.current || '';
				return;
			}
			const rightIntensity = Math.max(0, Math.min(1, (dx - 8) / 28));
			const leftIntensity = Math.max(0, Math.min(1, (-dx - 8) / 28));
			pick.style.opacity = String(rightIntensity);
			pick.style.transform = `rotate(-12deg) scale(${1 + Math.max(0, Math.min(1, dx / 70)) * 0.06})`;
			pass.style.opacity = String(leftIntensity);
			pass.style.transform = `rotate(12deg) scale(${1 + Math.max(0, Math.min(1, -dx / 70)) * 0.06})`;
			glow.style.boxShadow = dx > 10
				? `inset 24px 0 96px -36px rgba(34,197,94,${Math.max(0, Math.min(0.70, (dx - 10) / 110))}), inset -24px 0 96px -36px rgba(59,130,246,${Math.max(0, Math.min(0.55, (dx - 10) / 110))})`
				: dx < -10
				? `inset -24px 0 96px -36px rgba(244,63,94,${Math.max(0, Math.min(0.70, (-dx - 10) / 110))}), inset 24px 0 96px -36px rgba(168,85,247,${Math.max(0, Math.min(0.55, (-dx - 10) / 110))})`
				: 'none';

			// Dynamic tilt of the inner card (rotate with drag direction)
			if (cardEl) {
				const clamped = Math.max(-14, Math.min(14, dx / 8));
				const base = initialCardTransformRef.current || '';
				const baseTrimmed = base.trim();
				const sep = baseTrimmed && !baseTrimmed.endsWith(')') ? ' ' : baseTrimmed ? ' ' : '';
				cardEl.style.transform = `${baseTrimmed}${sep}rotate(${clamped}deg)`;
			}
		};

		// Passive, global listeners to drive badge only (no React state, no swipe interference)
		useEffect(() => {
			const getXY = (e: any) => ({
				x: e?.clientX ?? e?.touches?.[0]?.clientX ?? e?.changedTouches?.[0]?.clientX,
				y: e?.clientY ?? e?.touches?.[0]?.clientY ?? e?.changedTouches?.[0]?.clientY,
			});
			const onDown = (e: any) => {
				const cardEl = captureRef.current;
				if (!cardEl) return;
				if (!cardEl.contains(e.target as Node)) return;
				const p = getXY(e);
				if (typeof p.x !== 'number') return;
				badgeStartRef.current = { x: p.x, y: p.y };
				overlaysVisibleRef.current = true;
				// reset styles immediate
				updateBadgeStyles(0);
			};
			const onMove = (e: any) => {
				if (!badgeStartRef.current || !overlaysVisibleRef.current) return;
				const p = getXY(e);
				if (typeof p.x !== 'number') return;
				const bdx = p.x - badgeStartRef.current.x;
				if (badgeRafRef.current) cancelAnimationFrame(badgeRafRef.current!);
				badgeRafRef.current = requestAnimationFrame(() => updateBadgeStyles(bdx));
			};
			const onUp = () => {
				badgeStartRef.current = null;
				if (badgeRafRef.current) cancelAnimationFrame(badgeRafRef.current);
				badgeRafRef.current = null;
				overlaysVisibleRef.current = false;
				updateBadgeStyles(0);
			};
			window.addEventListener('pointerdown', onDown, { passive: true, capture: true } as any);
			window.addEventListener('pointermove', onMove, { passive: true, capture: true } as any);
			window.addEventListener('pointerup', onUp, { passive: true, capture: true } as any);
			window.addEventListener('touchstart', onDown as any, { passive: true, capture: true } as any);
			window.addEventListener('touchmove', onMove as any, { passive: true, capture: true } as any);
			window.addEventListener('touchend', onUp as any, { passive: true, capture: true } as any);
			return () => {
				window.removeEventListener('pointerdown', onDown as any, true);
				window.removeEventListener('pointermove', onMove as any, true);
				window.removeEventListener('pointerup', onUp as any, true);
				window.removeEventListener('touchstart', onDown as any, true);
				window.removeEventListener('touchmove', onMove as any, true);
				window.removeEventListener('touchend', onUp as any, true);
			};
		}, []);
		
		// 统一"点击 vs 拖动"判断逻辑
		const tapStartRef = useRef<{ x: number; y: number; t: number } | null>(null);
		const isDraggingRef = useRef<boolean>(false);
		const lastDxRef = useRef<number>(0);
		const handledRef = useRef<boolean>(false);

		const getPoint = (e: any) => {
			if (e.touches && e.touches[0]) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
			if (e.changedTouches && e.changedTouches[0]) return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
			return { x: e.clientX, y: e.clientY };
		};

		const onCardPointerDown = (e: any) => {
			if (!isTop) return;
			const p = getPoint(e);
			tapStartRef.current = { x: p.x, y: p.y, t: Date.now() };
			isDraggingRef.current = false;
			lastDxRef.current = 0;
			handledRef.current = false;
			console.log('🔽 AI Search Idea - Pointer Down', { isTop, idea: idea.project_idea_title });
		};

		const onCardPointerMove = (e: any) => {
			if (!tapStartRef.current || !isTop) return;
			const p = getPoint(e);
			const dx = p.x - tapStartRef.current.x;
			const dy = p.y - tapStartRef.current.y;
			lastDxRef.current = dx;
			if (Math.abs(dx) > TAP_MAX_MOVEMENT_PX || Math.abs(dy) > TAP_MAX_MOVEMENT_PX) {
				isDraggingRef.current = true;
			}
		};

		const onCardPointerUp = (e: any) => {
			if (!tapStartRef.current || !isTop) return;
			const p = getPoint(e);
			const dt = Date.now() - tapStartRef.current.t;
			const dx = Math.abs(p.x - tapStartRef.current.x);
			const dy = Math.abs(p.y - tapStartRef.current.y);
			const isTap = !isDraggingRef.current && dt <= TAP_MAX_DURATION_MS && dx <= TAP_MAX_MOVEMENT_PX && dy <= TAP_MAX_MOVEMENT_PX;
			console.log('🔺 AI Search Idea - Pointer Up', { 
				isTop, 
				idea: idea.project_idea_title, 
				isDragging: isDraggingRef.current, 
				dt, dx, dy, 
				isTap, 
				lastDx: lastDxRef.current 
			});
			tapStartRef.current = null;
			isDraggingRef.current = false;
			if (isTap) setSelectedIdea(idea); // 修改：显示AI idea的专用详情页面，而不是通用的项目详情页面
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
					if (!isTop) return; // 只处理顶部卡片
					const mapped = resolveDir(dir);
					console.log('🚀 AI Search Idea - onSwipe triggered', { 
						isTop, 
						idea: idea.project_idea_title, 
						originalDir: dir, 
						mappedDir: mapped,
						lastDx: lastDxRef.current,
						swipeRequirementType: SWIPE_REQUIREMENT,
						swipeThreshold: SWIPE_THRESHOLD_PX
					});
					handledRef.current = true;
					
					// 触发飞出动画
					const direction = mapped === 'right' ? 1 : -1;
					const currentRotation = rotateTransform.get();
					setExitRotate(currentRotation);
					setIsExiting(true);
					setExitX(direction * 1200);
					setExitY(0);
					
					// 调用处理函数
					handleSwipe(mapped);
				}}
				onCardLeftScreen={() => {
					if (!isTop) return; // 只处理顶部卡片
					console.log('👋 AI Search Idea - onCardLeftScreen triggered', { 
						isTop, 
						idea: idea.project_idea_title, 
						wasHandled: handledRef.current 
					});
					if (!handledRef.current) {
						const mapped = lastDxRef.current >= 0 ? 'right' : 'left';
						console.log('🔄 AI Search Idea - handling missed swipe', { mapped, lastDx: lastDxRef.current });
						handleSwipe(mapped);
					}
					handleCardLeftScreen(); // 仅用于日志记录
					handledRef.current = false;
					lastDxRef.current = 0;
				}}
				preventSwipe={[ 'down', ...(isTop ? [] : ['left', 'right', 'up']) ]}
				swipeRequirementType={SWIPE_REQUIREMENT}
				swipeThreshold={SWIPE_THRESHOLD_PX}
			>
				<motion.div
					className={`${baseCardClass} ${isTop ? topShadow : underShadow}`}
					ref={captureRef}
					style={{
						x: isExiting ? exitX : x,
						y: isExiting ? exitY : y,
						rotate: rotate
					}}
					animate={isExiting ? {
						x: exitX,
						y: exitY,
						rotate: exitRotate
					} : undefined}
					transition={isExiting ? {
						type: "tween",
						duration: 0.6,
						ease: "easeOut"
					} : undefined}
					onMouseDown={onCardPointerDown}
					onMouseMove={onCardPointerMove}
					onMouseUp={onCardPointerUp}
					onTouchStart={onCardPointerDown}
					onTouchMove={onCardPointerMove}
					onTouchEnd={onCardPointerUp}
				>
					<div className={`absolute inset-0 ${pick(gradientOptions, idx)}`} />
					<div className="absolute inset-0 bg-black/20" />
					<div className="absolute inset-0 p-6 text-white flex flex-col justify-center">
						<h2 className="text-[22px] font-bold leading-[26px] mb-2 text-center">{idea.project_idea_title}</h2>
						<p className="text-white/90 text-sm leading-5 text-center max-w-[85%] mx-auto line-clamp-3">{idea.description}</p>
					</div>

					{/* Swipe overlays (DOM refs, pointer-events none) */}
					{isTop && (
						<>
							{/* PICK (right) */}
							<div
								ref={pickRef}
								className="absolute top-6 left-6 z-[1000] select-none pointer-events-none"
								style={{
									opacity: 0,
									transform: 'rotate(-12deg) scale(1)',
									filter: 'drop-shadow(0 0 12px rgba(16,185,129,0.55)) drop-shadow(0 0 24px rgba(59,130,246,0.35))',
								}}
							>
								<div className="px-4 py-2 rounded-xl border-4 text-white font-extrabold tracking-widest uppercase backdrop-blur-sm pointer-events-none"
									 style={{
										 background: 'linear-gradient(135deg, rgba(34,197,94,0.42) 0%, rgba(59,130,246,0.42) 100%)',
										 borderColor: 'rgba(34,197,94,1)',
									 }}
								>
									Pick
								</div>
							</div>

							{/* PASS (left) */}
							<div
								ref={passRef}
								className="absolute top-6 right-6 z-[1000] select-none pointer-events-none"
								style={{
									opacity: 0,
									transform: 'rotate(12deg) scale(1)',
									filter: 'drop-shadow(0 0 12px rgba(244,63,94,0.55)) drop-shadow(0 0 24px rgba(168,85,247,0.35))',
								}}
							>
								<div className="px-4 py-2 rounded-xl border-4 text-white font-extrabold tracking-widest uppercase backdrop-blur-sm pointer-events-none"
									 style={{
										 background: 'linear-gradient(135deg, rgba(244,63,94,0.42) 0%, rgba(168,85,247,0.42) 100%)',
										 borderColor: 'rgba(244,63,94,1)',
									 }}
								>
									Pass
								</div>
							</div>

							{/* dynamic edge glow */}
							<div
								ref={glowRef}
								className="pointer-events-none absolute inset-0 z-[900]"
								style={{ boxShadow: 'none', transition: 'box-shadow 80ms linear' }}
							/>
						</>
					)}
				</motion.div>
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
		<div className="absolute inset-0 bg-white flex flex-col">
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
			<div className="flex-shrink-0">
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
			</div>

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
			<div className="flex-1 flex flex-col overflow-y-auto px-4 relative">
				{/* 搜索结果提示栏 - 自适应高度 */}
				<div className="flex-shrink-0 mt-4">
					<AnimatePresence>
						{hasSearched && (
							<motion.div 
								initial={{ opacity: 0, y: -20 }} 
								animate={{ opacity: 1, y: 0 }} 
								className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500"
							>
								{/* 标题行 - 在agent模式下添加折叠按钮 */}
								<div className="flex items-center justify-between">
									<p className="text-gray-700">
										<span className="text-blue-600">
											{searchMode === 'basic' ? (t('youSearchedFor') || 'You searched for:') : (t('aiSearchedIdeasFor') || 'AI searched ideas for:')}
										</span> "{lastResultsQuery}"
									</p>
									{/* 在agent模式下添加折叠/展开按钮 */}
									{searchMode === 'multi-resources' && showThinkingStream && (
										<button
											onClick={() => setThinkingStreamCollapsed(!thinkingStreamCollapsed)}
											className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
										>
											<motion.div
												animate={{ rotate: thinkingStreamCollapsed ? 0 : 180 }}
												transition={{ duration: 0.2 }}
											>
												<ChevronDown className="w-4 h-4" />
											</motion.div>
										</button>
									)}
								</div>
								
								{/* 思考流内容 - 自适应高度，最大高度限制 */}
								{searchMode === 'multi-resources' && showThinkingStream && (
									<AnimatePresence>
										{!thinkingStreamCollapsed && (
											<motion.div
												className="mt-3 space-y-2 overflow-y-auto"
												style={{ maxHeight: '160px' }}
												initial={{ opacity: 0, height: 0 }}
												animate={{ opacity: 1, height: 'auto' }}
												exit={{ opacity: 0, height: 0 }}
												transition={{ duration: 0.2 }}
											>
												{thinkingSteps.slice(0, currentStepIndex + 1).map((step, index) => (
													<motion.div
														key={step.id}
														className="flex items-start gap-3"
														initial={{ opacity: 0, x: -20 }}
														animate={{ opacity: 1, x: 0 }}
														transition={{ duration: 0.5 }}
													>
														<div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
															step.completed ? 'bg-green-500' : 'bg-blue-500'
														}`} />
														<div className="flex-1">
															<p className="text-sm text-gray-700">
																{step.content}
															</p>
															{step.completed && (
																<motion.div
																	initial={{ scale: 0 }}
																	animate={{ scale: 1 }}
																	className="inline-flex items-center gap-1 mt-1 text-xs text-green-600"
																>
																	<Check className="w-3 h-3" />
																	<span>完成</span>
																</motion.div>
															)}
														</div>
													</motion.div>
												))}

												{/* 思考中的动画指示器或完成状态 */}
												{currentStepIndex < thinkingSteps.length ? (
													<motion.div
														className="flex items-center gap-3 opacity-60"
														initial={{ opacity: 0 }}
														animate={{ opacity: 0.6 }}
													>
														<div className="flex gap-1">
															{[0, 1, 2].map((i) => (
																<motion.div
																	key={i}
																	className="w-1 h-1 bg-blue-500 rounded-full"
																	animate={{ 
																		scale: [1, 1.2, 1],
																		opacity: [0.4, 1, 0.4]
																	}}
																	transition={{ 
																		duration: 0.8,
																		repeat: Infinity,
																		delay: i * 0.2
																	}}
																/>
															))}
														</div>
														<p className="text-xs text-gray-500">思考中...</p>
													</motion.div>
												) : thinkingSteps.length > 0 && (
													<motion.div
														className="flex items-center gap-3"
														initial={{ opacity: 0 }}
														animate={{ opacity: 1 }}
														transition={{ delay: 0.3 }}
													>
														<motion.div
															className="w-2 h-2 bg-green-500 rounded-full"
															initial={{ scale: 0 }}
															animate={{ scale: 1 }}
															transition={{ delay: 0.5 }}
														/>
														<p className="text-xs text-green-600 font-medium">完成思考</p>
													</motion.div>
												)}
											</motion.div>
										)}
									</AnimatePresence>
								)}
							</motion.div>
						)}
					</AnimatePresence>
				</div>
				
				{/* 卡片区域或默认提示 */}
				{!hasSearched && !isSearching ? (
					/* 默认状态提示 - 在页面中央显示 */
					<div className="flex-1 flex items-center justify-center">
						<motion.div 
							initial={{ opacity: 0 }} 
							animate={{ opacity: 1 }} 
							className="flex flex-col items-center justify-center text-gray-500 max-w-md text-center px-4"
						>
							<Search size={48} className="mb-4 text-gray-300" />
							<h3 className="text-xl mb-2">{t('aiProjectSearchTitle') || 'AI Project Search'}</h3>
							<p className="text-center">
								{searchMode === 'basic' 
									? (t('aiProjectSearchBasic') || "Describe what kind of project or collaborator you're looking for, and our AI will find the perfect matches.")
									: (t('aiProjectSearchAgent') || "Describe your project idea and our AI will generate innovative project concepts and suggestions.")
								}
							</p>
						</motion.div>
					</div>
				) : (
					/* 搜索结果或加载状态的卡片区域 */
					<div className="flex-shrink-0 flex items-center justify-center mt-6 mb-[120px]">
						<div className="relative w-[357px] h-[420px]">
							{isSearching ? (
								<div className="w-full h-full rounded-[14px] bg-gray-200 animate-pulse" />
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
													<ProjectSwipeCard project={item as Project} isTop={isTop} onOpenProject={onOpenProject} />
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
							) : (
								<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center w-full h-full text-gray-500">
									<Search size={48} className="mb-4 text-gray-300" />
									<p>{t('noResults') || `No ${searchMode === 'basic' ? 'projects' : 'ideas'} found. Try a different search term.`}</p>
								</motion.div>
							)}
						</div>
					</div>
				)}
			</div>

			{/* Search bar - 固定在底部导航上方 */}
			<motion.div 
				initial={{ y: 100, opacity: 0 }} 
				animate={{ y: 0, opacity: 1 }} 
				className="flex-shrink-0 bg-white border-t border-gray-200 p-6 shadow-lg" 
				style={{ height: '96px', marginBottom: '96px' }}
			>
				<div className="flex items-center gap-3 mx-auto w-[357px]">
					<div className="flex-1 relative">
						<Input 
							value={searchQuery} 
							onChange={(e) => setSearchQuery(e.target.value)} 
							onKeyDown={handleKeyPress} 
							placeholder={searchMode === 'basic' ? (t('searchBarPlaceholderBasic') || 'Ask AI to find projects or collaborators...') : (t('searchBarPlaceholderAgent') || 'Describe your project idea for AI suggestions...')} 
							className="pr-12 h-12 rounded-full border-2 border-gray-200 bg-gray-50 focus-visible:!border-blue-500 focus-visible:!ring-2 focus-visible:!ring-blue-500/20 focus-visible:!ring-offset-0" 
							disabled={isSearching} 
						/>
						<div className="absolute right-3 top-1/2 -translate-y-1/2">
							<Search size={20} className="text-gray-400" />
						</div>
					</div>
					<button onClick={handleSearch} disabled={!searchQuery.trim() || isSearching} className="h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center">
						{isSearching ? (
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