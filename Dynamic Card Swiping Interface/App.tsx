import { useState, useRef, useEffect } from 'react';
import { Button } from './components/ui/button';
import { motion, PanInfo, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { Star, ChevronDown, MapPin, Calendar, Users, Target, ExternalLink, ArrowLeft, Check, Play, X, ChevronLeft, ChevronRight, Settings } from 'lucide-react';
import { ImageWithFallback } from './components/figma/ImageWithFallback';
import { Badge } from './components/ui/badge';
import svgPaths from "./imports/svg-fko3i96u3r";
import { t, setLanguage, subscribeLanguageChange, currentLanguage as i18nCurrentLanguage } from './translations';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import { Checkbox } from './components/ui/checkbox';
import TinderCard from 'react-tinder-card';
import { AuthPhoneScreen } from './auth-components/AuthScreen';
import logo from './auth-imports/no_bg.PNG';
import BackgroundGradientAnimation from './components/ui/BackgroundGradientAnimation';
import { HeaderBar } from './components/HeaderBar';
import { fetchProjectCards, sendSwipe, CardsResponse } from './src/api/recommendations';
import { getAccessToken } from './src/api/client';

// 新增：导入启动页面组件
import { LaunchingPage } from './Interactive Ques Sign-Up_Sign-In Prototype/components/LaunchingPage';
import AISearchIntegrated from './components/AISearchIntegrated';

// 新增：导入Project Posting Interface组件
import { PostingProjectPage } from './components/project-posting/PostingProjectPage';
import { DraftsPage } from './components/project-posting/DraftsPage';
import { DraftResumeDialog } from './components/project-posting/DraftResumeDialog';

// 新增：导入聊天相关组件
import ChatHome from './components/chat/ChatHome';
import ChatChatPage from './components/chat/ChatChatPage';
import ChatNotification from './components/chat/ChatNotification';
import ChatSettings from './components/chat/ChatSettings';
import { SettingsPage } from './components/SettingsPage';
import { SupportPage } from './components/SupportPage';
import { TermsPage } from './components/TermsPage';

// 新增：导入个人资料页面
import { ProfilePage } from './components/ProfilePage';
import { toPng } from 'html-to-image';

// 调试：验证导入
console.log('📦 Component imports:', {
  PostingProjectPage: !!PostingProjectPage,
  DraftsPage: !!DraftsPage,
  DraftResumeDialog: !!DraftResumeDialog
});

// Export UI feature flag - set to false to hide camera buttons on all pages
const ENABLE_EXPORT: boolean = false;

// 新增：认证相关接口
interface SMSData {
  phoneNumber: string;
  verificationCode: string;
}

// 新增：应用状态类型
type AppState = 'launch' | 'auth' | 'main' | 'ai' | 'posting' | 'drafts' | 'resume' | 'chat' | 'chat-detail' | 'notification' | 'settings' | 'profile' | 'profile-settings' | 'support' | 'terms';

// 可调滑动参数（集中配置）
export const SWIPE_REQUIREMENT: 'position' | 'velocity' = 'position';
export const SWIPE_THRESHOLD_PX: number = 100; // 位置阈值，像素越大越难滑走
export const TAP_MAX_MOVEMENT_PX: number = 8;  // 点击判定的最大移动距离
export const TAP_MAX_DURATION_MS: number = 220; // 点击判定的最大按下时长

// Temporary: enable promo tilt visual for top card
const PROMO_TILT: boolean = false;

// 添加滑块样式
const sliderStyles = `
  input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    cursor: pointer;
  }
  
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 24px;
    height: 24px;
    background: white;
    border: 2px solid #0055F7;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 0 10px rgba(0, 85, 247, 0.5);
  }
  
  input[type="range"]::-moz-range-thumb {
    width: 24px;
    height: 24px;
    background: white;
    border: 2px solid #0055F7;
    border-radius: 50%;
    cursor: pointer;
  }
  
  /* 年龄双滑块特殊样式 */
  .age-slider-left {
    z-index: 10;
  }
  
  .age-slider-right {
    z-index: 10;
  }
  
  .age-slider-left::-webkit-slider-thumb {
    z-index: 10;
  }
  
  .age-slider-right::-webkit-slider-thumb {
    z-index: 20;
  }
  
  /* 只让滑块拇指响应事件，避免两个输入层互相遮挡 */
  .age-slider-left,
  .age-slider-right {
    pointer-events: none;
  }

  .age-slider-left::-webkit-slider-thumb,
  .age-slider-right::-webkit-slider-thumb {
    pointer-events: all;
  }

  .age-slider-left::-moz-range-thumb,
  .age-slider-right::-moz-range-thumb {
    pointer-events: all;
  }

  /* 交互时将当前滑块置于顶层 */
  .age-slider-left:focus,
  .age-slider-left:active,
  .age-slider-right:focus,
  .age-slider-right:active {
    z-index: 50;
  }
`;

interface Collaborator {
  name: string;
  role: string;
  avatar: string;
}

interface Owner {
  name: string;
  age: number;
  gender: string;
  role: string;
  distance: number;
  avatar: string;
  tags: string[];
}

export interface Project {
  id: number;
  title: string;
  author: string;
  collaborators: number;
  background?: string;
  videoUrl?: string;
  description: string;
  tags: string[];
  type: 'project';
  cardStyle: 'image' | 'video' | 'text-only';
  status: 'ongoing' | 'finished' | 'not_started';
  owner: Owner;
  collaboratorsList: Collaborator[];
  detailedDescription: string;
  startTime: string;
  currentProgress: number;
  content: string;
  purpose: string;
  lookingFor: string[];
  links: string[];
  media: string[];
  gradientBackground?: string; // Fixed gradient for each project
}

const positiveEmojis = ['😊', '😍', '🥰', '😘', '🤩', '😎', '🙌', '👍', '💖', '✨', '🎉', '🔥'];

// Random gradient backgrounds
const gradientBackgrounds = [
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
  'bg-gradient-to-br from-lime-400 via-green-500 to-emerald-600',
  'bg-gradient-to-br from-indigo-400 via-purple-500 to-pink-600'
];

const getRandomGradient = () => {
  return gradientBackgrounds[Math.floor(Math.random() * gradientBackgrounds.length)];
};

// 新增：后端卡片到本地 Project 类型的映射（使用新版字段 cover、lookingFor 对象）
function mapBackendCardToProject(card: any): Project {
  const idNum = typeof card?.id === 'string' ? parseInt(card.id, 10) : Number(card?.id || 0);
  const title: string = card?.title || 'Untitled Project';
  const description: string = card?.description || 'No description available';
  const tags: string[] = Array.isArray(card?.tags) ? card.tags : [];
  const owner = card?.owner || {};
  const collaboratorsList = Array.isArray(card?.collaboratorsList) ? card.collaboratorsList : [];
  const links: string[] = Array.isArray(card?.links) ? card.links : [];
  const media: string[] = Array.isArray(card?.media) ? card.media : [];
  const cover: string | undefined = card?.cover || undefined;
  const lookingFor = card?.lookingFor || { tags: [], description: '' };

  return {
    id: Number.isFinite(idNum) ? idNum : Math.floor(Math.random() * 1000000),
    title,
    author: owner?.name || title,
    collaborators: Number(card?.collaborators ?? collaboratorsList.length ?? 0),
    description,
    tags,
    type: 'project',
    cardStyle: (card?.cardStyle || 'text-only'),
    status: (card?.status || 'ongoing'),
    owner: {
      name: owner?.name || 'Anonymous',
      age: owner?.age ?? 25,
      gender: owner?.gender ?? 'Non-binary',
      role: owner?.role || 'Owner',
      distance: owner?.distance ?? 5,
      avatar: owner?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(owner?.name || 'user')}`,
      tags: Array.isArray(owner?.tags) ? owner.tags : []
    },
    collaboratorsList: collaboratorsList.map((c: any) => ({
      name: c?.name || 'Member',
      role: c?.role || 'Collaborator',
      avatar: c?.avatar || '' // 设置为空字符串，不显示头像
    })),
    detailedDescription: card?.detailedDescription || description,
    startTime: card?.startTime || 'Recently',
    currentProgress: card?.currentProgress ?? 40,
    content: card?.content || description,
    purpose: card?.purpose || 'Building innovative solutions',
    lookingFor: Array.isArray(lookingFor?.tags) ? lookingFor.tags : [],
    links,
    media: cover ? [cover, ...media] : media,
    gradientBackground: card?.gradientBackground || getRandomGradient(),
    background: cover,
    videoUrl: card?.videoUrl || undefined
  } as Project;
}

const projects: Project[] = [
  {
    id: 10001, // 确保唯一
    title: "Ques · Change the world",
    author: "Cody",
    collaborators: 3, // 与下方 collaboratorsList 长度保持一致
    // cardStyle 可选: 'image' | 'video' | 'text-only'
    cardStyle: 'image',
    // 如果是 image 卡片，提供背景图（建议竖图）：
    background: "/sample/cody.jpg",
    // 如果是 video 卡片，提供视频链接（放 public 后用绝对路径）：
    // videoUrl: "/sample/intro.mp4",
  
    description: "Build a revolutionary project partner matching platform",
    tags: ["AI", "Start Up", "App"],
  
    type: 'project',
    status: 'ongoing', // 'ongoing' | 'finished' | 'not_started'
    gradientBackground: 'bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700', // text-only 或 video 时作为底色
  
    owner: {
      name: "Cody",
      age: 20,
      gender: "Male", // 'Male' | 'Female' | 'Non-binary'
      role: "CEO",
      distance: 0, // km
      avatar: "/sample/cody_avatar.jpg", // 或放 public 里："/sample/avatar.png"
      tags: []
    },
  
    collaboratorsList: [
      { name: "William", role: "Backend", avatar: "" },
      { name: "Jimmy", role: "AI and algorithm", avatar: "" },
      { name: "Rhys", role: "UI and frontendd", avatar: "" }
    ],
  
    detailedDescription: `Ques is a project based social app that's reinventing the way people exchange value.
We connect ideas, resources, talent, and outcomes to build a collaborative network that helps creators change the world faster.
Every project is shown as a card you can like or skip.
When two people like each other's projects, it shows you share the same vision, and we make the connection.
Where vision meets action, and builders find their tribe.`,
    startTime: "August 2025",
    currentProgress: 50, // 百分比
    content: "我们正在构建一个用于演示导出功能的完整样例，用于验证图片/视频/标签/作者信息等在卡片上的呈现效果。",
    purpose: "向团队或用户展示卡片导出的视觉质量与信息完整性。",
    lookingFor: ["you"],
  
    links: [
      "https://github.com/your-repo",
      "https://figma.com/your-design"
    ],
  
    // 媒体轮播，可混合图片/视频。会在详情页顶部轮播显示
    // 如果提供了 background，也可以一并放在 media 里以便轮播
    media: [
      "/sample/background.webp",
      // "/sample/intro.mp4"
    ]
  },
  {
    id: 1,
    title: "The Greatest Project In the World",
    author: "Alex",
    collaborators: 3,
    background: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=600&fit=crop&crop=center",
    description: "Revolutionary AI-powered platform for creative collaboration",
    tags: ["AI", "Design", "Collaboration"],
    type: 'project',
    cardStyle: 'image',
    status: 'ongoing',
    owner: {
      name: "Alex Chen",
      age: 28,
      gender: "Male",
      role: "Product Designer",
      distance: 2.5,
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
      tags: ["UI/UX", "AI", "Leadership"]
    },
    collaboratorsList: [
      { name: "Sarah Kim", role: "Frontend Developer", avatar: "" },
      { name: "Mike Johnson", role: "AI Engineer", avatar: "" },
      { name: "Emma Davis", role: "Product Manager", avatar: "" }
    ],
    detailedDescription: "An innovative AI-powered platform designed to revolutionize how creative teams collaborate. Using machine learning algorithms to match collaborators, suggest improvements, and streamline workflows.",
    startTime: "March 2024",
    currentProgress: 75,
    content: "This project combines cutting-edge AI technology with intuitive design to create a seamless collaboration experience. Features include real-time suggestion engine, automated task distribution, and intelligent project matching.",
    purpose: "To eliminate friction in creative collaboration and help teams achieve their full potential through AI-assisted workflows.",
    lookingFor: ["Backend Developer", "Data Scientist", "Marketing Specialist"],
    links: ["https://github.com/project", "https://figma.com/design"],
    media: [
      "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop",
      "https://videos.pexels.com/video-files/4753989/4753989-hd_1920_1080_24fps.mp4"
    ]
  },
  {
    id: 2,
    title: "Sustainable Future App",
    author: "Sarah",
    collaborators: 5,
    videoUrl: "https://player.vimeo.com/external/458436864.mp4?s=20c7547e3e7b85c9f6c5d7c8b4a9c62a2e8a3cf9&profile_id=174",
    description: "Track and reduce your carbon footprint with gamification",
    tags: ["Sustainability", "Mobile", "Gamification"],
    type: 'project',
    cardStyle: 'video',
    status: 'ongoing',
    gradientBackground: 'bg-gradient-to-br from-green-400 via-blue-500 to-purple-600',
    owner: {
      name: "Sarah Williams",
      age: 26,
      gender: "Female",
      role: "Environmental Engineer",
      distance: 1.8,
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
      tags: ["Sustainability", "Mobile Dev", "Environment"]
    },
    collaboratorsList: [
      { name: "David Park", role: "Mobile Developer", avatar: "" },
      { name: "Lisa Zhang", role: "UX Designer", avatar: "" },
      { name: "Tom Brown", role: "Data Analyst", avatar: "" },
      { name: "Maya Patel", role: "Backend Developer", avatar: "" },
      { name: "James Wilson", role: "Marketing", avatar: "" }
    ],
    detailedDescription: "A gamified mobile application that helps users track, understand, and reduce their carbon footprint through daily challenges, community competitions, and educational content.",
    startTime: "January 2024",
    currentProgress: 60,
    content: "Features include carbon tracking, eco-challenges, community leaderboards, educational resources, and partnerships with sustainable brands for rewards.",
    purpose: "To make environmental consciousness accessible and engaging for everyone, driving real behavioral change through gamification.",
    lookingFor: ["Climate Scientist", "Growth Hacker", "Sustainability Expert"],
    links: ["https://sustainableapp.com", "https://github.com/sustainable-app"],
    media: [
      "https://images.unsplash.com/photo-1569163139394-de4e5f43e4e3?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=200&fit=crop"
    ]
  },
  {
    id: 3,
    title: "Innovative Blockchain Solution",
    author: "Maya",
    collaborators: 4,
    description: "Building the next generation of decentralized applications with a focus on user experience and scalability. Our platform combines the security of blockchain with the simplicity of traditional apps, making Web3 accessible to everyone.",
    tags: ["Blockchain", "Web3", "DeFi"],
    type: 'project',
    cardStyle: 'text-only',
    status: 'not_started',
    gradientBackground: 'bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600',
    owner: {
      name: "Maya Patel",
      age: 29,
      gender: "Female",
      role: "Blockchain Developer",
      distance: 3.2,
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
      tags: ["Blockchain", "Web3", "Smart Contracts"]
    },
    collaboratorsList: [
      { name: "Alex Thompson", role: "Smart Contract Developer", avatar: "" },
      { name: "Zoe Chen", role: "Frontend Developer", avatar: "" },
      { name: "Ryan Kim", role: "Backend Developer", avatar: "" },
      { name: "Sofia Rodriguez", role: "UI/UX Designer", avatar: "" }
    ],
    detailedDescription: "A comprehensive blockchain platform that bridges the gap between traditional applications and decentralized technology.",
    startTime: "February 2024",
    currentProgress: 45,
    content: "Developing smart contracts, user interfaces, and infrastructure for the next generation of decentralized applications.",
    purpose: "To make blockchain technology accessible and user-friendly for mainstream adoption.",
    lookingFor: ["Security Auditor", "Community Manager", "Business Development"],
    links: ["https://blockchain-project.com", "https://github.com/blockchain-solution"],
    media: []
  },
  {
    id: 4,
    title: "VR Education Platform",
    author: "David",
    collaborators: 6,
    background: "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=400&h=600&fit=crop&crop=center",
    description: "Immersive virtual reality learning experiences for students worldwide",
    tags: ["VR", "Education", "Technology"],
    type: 'project',
    cardStyle: 'image',
    status: 'ongoing',
    owner: {
      name: "David Chen",
      age: 31,
      gender: "Male",
      role: "VR Developer",
      distance: 4.1,
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
      tags: ["VR/AR", "Education", "Unity"]
    },
    collaboratorsList: [
      { name: "Emma Wilson", role: "3D Artist", avatar: "" },
      { name: "Michael Brown", role: "Educational Content Creator", avatar: "" },
      { name: "Sophie Lee", role: "UX Designer", avatar: "" },
      { name: "Kevin Zhang", role: "Backend Developer", avatar: "" },
      { name: "Rachel Green", role: "Marketing Specialist", avatar: "" },
      { name: "Daniel Kim", role: "Quality Assurance", avatar: "" }
    ],
    detailedDescription: "A revolutionary VR platform that transforms traditional education into immersive, interactive experiences. Students can explore historical events, conduct virtual science experiments, and visit distant locations without leaving their classroom.",
    startTime: "December 2023",
    currentProgress: 85,
    content: "Creating interactive VR modules for various subjects including history, science, geography, and art. Each module includes realistic 3D environments, interactive elements, and comprehensive learning assessments.",
    purpose: "To democratize access to high-quality educational experiences through immersive technology, making learning more engaging and effective for students of all ages.",
    lookingFor: ["Content Writer", "3D Modeler", "Educational Psychologist"],
    links: ["https://vreducation.com", "https://github.com/vr-education-platform"],
    media: [
      "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=200&fit=crop"
    ]
  },
  {
    id: 5,
    title: "Smart Home IoT Hub",
    author: "Lisa",
    collaborators: 3,
    description: "Centralized control system for all your smart home devices with AI-powered automation and energy optimization. Create the perfect living environment with intelligent scheduling and predictive maintenance.",
    tags: ["IoT", "Smart Home", "AI"],
    type: 'project',
    cardStyle: 'text-only',
    status: 'finished',
    gradientBackground: 'bg-gradient-to-br from-orange-400 via-red-500 to-pink-600',
    owner: {
      name: "Lisa Rodriguez",
      age: 27,
      gender: "Female",
      role: "IoT Engineer",
      distance: 1.2,
      avatar: "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face",
      tags: ["IoT", "Embedded Systems", "AI"]
    },
    collaboratorsList: [
      { name: "Chris Martinez", role: "Hardware Engineer", avatar: "" },
      { name: "Anna Thompson", role: "Software Developer", avatar: "" },
      { name: "Robert Johnson", role: "Security Specialist", avatar: "" }
    ],
    detailedDescription: "A comprehensive IoT hub that connects and controls all smart home devices through a single, intuitive interface. Features include AI-powered automation, energy usage optimization, and advanced security protocols.",
    startTime: "October 2023",
    currentProgress: 100,
    content: "Developed a complete smart home ecosystem including hardware controllers, mobile app, web dashboard, and cloud infrastructure. The system supports over 100 different device types and protocols.",
    purpose: "To simplify smart home management while maximizing energy efficiency and user convenience through intelligent automation.",
    lookingFor: ["Mobile Developer", "Cloud Architect", "Product Manager"],
    links: ["https://smarthomehub.com", "https://github.com/iot-hub"],
    media: []
  },
  {
    id: 6,
    title: "Fitness Tracking AI",
    author: "Ryan",
    collaborators: 4,
    videoUrl: "https://player.vimeo.com/external/434045526.mp4?s=c27eecc69a27dbc4ff2b87d38afc35f1a9e7c02d&profile_id=174",
    description: "AI-powered fitness tracking with personalized workout recommendations",
    tags: ["Health", "AI", "Mobile"],
    type: 'project',
    cardStyle: 'video',
    status: 'ongoing',
    gradientBackground: 'bg-gradient-to-br from-blue-400 via-purple-500 to-pink-600',
    owner: {
      name: "Ryan Kim",
      age: 25,
      gender: "Male",
      role: "AI Engineer",
      distance: 2.8,
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
      tags: ["Machine Learning", "Health Tech", "Mobile Dev"]
    },
    collaboratorsList: [
      { name: "Jessica Wang", role: "Data Scientist", avatar: "" },
      { name: "Marcus Davis", role: "Mobile Developer", avatar: "" },
      { name: "Nina Patel", role: "UI/UX Designer", avatar: "" },
      { name: "Thomas Lee", role: "Backend Developer", avatar: "" }
    ],
    detailedDescription: "An intelligent fitness tracking application that uses computer vision and machine learning to analyze workout form, provide real-time feedback, and generate personalized training programs.",
    startTime: "November 2023",
    currentProgress: 70,
    content: "Building a comprehensive fitness platform with pose estimation, movement analysis, progress tracking, and social features. The AI can detect improper form and suggest corrections in real-time.",
    purpose: "To make professional-quality fitness guidance accessible to everyone, helping users achieve their health goals safely and effectively.",
    lookingFor: ["Computer Vision Expert", "Fitness Trainer", "Backend Developer"],
    links: ["https://fitnessai.com", "https://github.com/fitness-tracking-ai"],
    media: [
      "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&h=200&fit=crop"
    ]
  },
  {
    id: 7,
    title: "Eco-Friendly Delivery Network",
    author: "Sophie",
    collaborators: 5,
    description: "Sustainable last-mile delivery solution using electric vehicles and AI route optimization. Reducing carbon emissions while improving delivery efficiency and customer satisfaction.",
    tags: ["Sustainability", "Logistics", "AI"],
    type: 'project',
    cardStyle: 'text-only',
    status: 'not_started',
    gradientBackground: 'bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600',
    owner: {
      name: "Sophie Anderson",
      age: 30,
      gender: "Female",
      role: "Logistics Manager",
      distance: 5.5,
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
      tags: ["Logistics", "Sustainability", "Operations"]
    },
    collaboratorsList: [
      { name: "James Wilson", role: "AI Engineer", avatar: "" },
      { name: "Maria Garcia", role: "Operations Manager", avatar: "" },
      { name: "Alex Turner", role: "Fleet Coordinator", avatar: "" },
      { name: "Sarah Miller", role: "Customer Success", avatar: "" },
      { name: "David Clark", role: "Data Analyst", avatar: "" }
    ],
    detailedDescription: "A comprehensive delivery network that prioritizes environmental sustainability through electric vehicle fleets, optimized routing algorithms, and carbon-neutral packaging solutions.",
    startTime: "Planning Phase",
    currentProgress: 15,
    content: "Designing an end-to-end delivery system that minimizes environmental impact while maximizing efficiency. Includes fleet management, route optimization, and customer communication platforms.",
    purpose: "To revolutionize the delivery industry by proving that sustainable practices can be both environmentally responsible and economically viable.",
    lookingFor: ["Supply Chain Expert", "Electric Vehicle Specialist", "Route Optimization Engineer"],
    links: ["https://ecodelivery.com", "https://github.com/eco-delivery-network"],
    media: []
  },
  {
    id: 8,
    title: "Mental Health Support App",
    author: "Emma",
    collaborators: 4,
    background: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=600&fit=crop&crop=center",
    description: "AI-powered mental health support with 24/7 availability and personalized care",
    tags: ["Health", "AI", "Mental Health"],
    type: 'project',
    cardStyle: 'image',
    status: 'ongoing',
    owner: {
      name: "Emma Davis",
      age: 29,
      gender: "Female",
      role: "Clinical Psychologist",
      distance: 3.7,
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
      tags: ["Mental Health", "AI", "Psychology"]
    },
    collaboratorsList: [
      { name: "Dr. Michael Chen", role: "Psychiatrist", avatar: "" },
      { name: "Jennifer Park", role: "AI Developer", avatar: "" },
      { name: "Robert Smith", role: "UX Researcher", avatar: "" },
      { name: "Amanda Johnson", role: "Content Creator", avatar: "" }
    ],
    detailedDescription: "A comprehensive mental health support application that provides immediate access to AI-powered therapy, mood tracking, crisis intervention, and connection to licensed professionals.",
    startTime: "September 2023",
    currentProgress: 90,
    content: "Developing an AI chatbot trained on therapeutic techniques, mood tracking algorithms, emergency contact systems, and secure video therapy integration with licensed professionals.",
    purpose: "To make mental health support accessible, affordable, and available 24/7, reducing barriers to care and improving overall mental wellness.",
    lookingFor: ["Licensed Therapist", "AI Ethics Specialist", "Security Expert"],
    links: ["https://mentalhealthapp.com", "https://github.com/mental-health-support"],
    media: [
      "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=200&fit=crop"
    ]
  },
  {
    id: 9,
    title: "Crypto Trading Bot",
    author: "Kevin",
    collaborators: 3,
    description: "Automated cryptocurrency trading system with advanced risk management and portfolio optimization. Using machine learning algorithms to analyze market trends and execute trades with precision.",
    tags: ["Cryptocurrency", "Trading", "AI"],
    type: 'project',
    cardStyle: 'text-only',
    status: 'ongoing',
    gradientBackground: 'bg-gradient-to-br from-yellow-400 via-orange-500 to-red-600',
    owner: {
      name: "Kevin Zhang",
      age: 26,
      gender: "Male",
      role: "Quantitative Analyst",
      distance: 1.9,
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
      tags: ["Quantitative Finance", "Cryptocurrency", "Machine Learning"]
    },
    collaboratorsList: [
      { name: "Rachel Green", role: "Backend Developer", avatar: "" },
      { name: "Daniel Kim", role: "Data Scientist", avatar: "" },
      { name: "Sophia Lee", role: "Security Engineer", avatar: "" }
    ],
    detailedDescription: "An intelligent trading bot that combines technical analysis, sentiment analysis, and machine learning to make profitable trading decisions while managing risk effectively.",
    startTime: "August 2023",
    currentProgress: 80,
    content: "Building a comprehensive trading platform with real-time market data analysis, automated trade execution, risk management systems, and performance tracking dashboards.",
    purpose: "To democratize access to sophisticated trading strategies while maintaining strict risk controls and regulatory compliance.",
    lookingFor: ["Financial Analyst", "Compliance Officer", "DevOps Engineer"],
    links: ["https://cryptobot.com", "https://github.com/crypto-trading-bot"],
    media: []
  },
  {
    id: 10,
    title: "Language Learning VR",
    author: "Maria",
    collaborators: 6,
    videoUrl: "https://player.vimeo.com/external/434045526.mp4?s=c27eecc69a27dbc4ff2b87d38afc35f1a9e7c02d&profile_id=174",
    description: "Immersive language learning through virtual reality conversations and cultural experiences",
    tags: ["VR", "Education", "Language"],
    type: 'project',
    cardStyle: 'video',
    status: 'not_started',
    gradientBackground: 'bg-gradient-to-br from-indigo-400 via-purple-500 to-pink-600',
    owner: {
      name: "Maria Garcia",
      age: 28,
      gender: "Female",
      role: "Language Educator",
      distance: 4.3,
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
      tags: ["Language Education", "VR", "Cultural Exchange"]
    },
    collaboratorsList: [
      { name: "Carlos Rodriguez", role: "VR Developer", avatar: "" },
      { name: "Yuki Tanaka", role: "Language Expert", avatar: "" },
      { name: "Ahmed Hassan", role: "Cultural Consultant", avatar: "" },
      { name: "Elena Popov", role: "3D Artist", avatar: "" },
      { name: "Lucas Silva", role: "Audio Engineer", avatar: "" },
      { name: "Isabella Costa", role: "Content Creator", avatar: "" }
    ],
    detailedDescription: "A revolutionary VR platform that immerses users in authentic language learning environments, from ordering coffee in Paris to negotiating business deals in Tokyo.",
    startTime: "Planning Phase",
    currentProgress: 25,
    content: "Creating immersive VR scenarios for multiple languages, including realistic environments, native speaker interactions, and cultural context learning.",
    purpose: "To make language learning more engaging and effective by providing authentic, immersive experiences that accelerate fluency development.",
    lookingFor: ["Native Language Speakers", "VR Content Creator", "Educational Psychologist"],
    links: ["https://vrlanguage.com", "https://github.com/language-learning-vr"],
    media: [
      "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1523050854058-8df90110c9e1?w=400&h=200&fit=crop"
    ]
  }
];

const projectTypes = ["AI", "Design", "Sustainability", "Mobile", "VR", "Education", "Blockchain", "Gaming", "Health", "Finance", "IoT", "Language", "Logistics", "Cryptocurrency", "Trading", "Mental Health", "Fitness"];

interface FilterState {
  projectStatus: { ongoing: boolean; finished: boolean; not_started: boolean };
  projectTypes: string[];
  distance: number[];
  gender: string[];
  age: number[];
  sameCity?: boolean;
  showOutOfDistance?: boolean;
  typeSearch?: string;
}

function PopupButton() {
  const [logoAspect, setLogoAspect] = useState<number | null>(null);
  useEffect(() => {
    const img = new Image();
    img.onload = () => setLogoAspect((img.naturalWidth && img.naturalHeight) ? (img.naturalWidth / img.naturalHeight) : 1);
    img.src = logo as any;
  }, []);
  return (
    <div
      className="flex flex-row items-end justify-center gap-0 leading-[0] px-0 py-[13px] relative"
    >
      <div
        aria-label="Ques"
        className="inline-block"
        style={{
          height: '36px',
          width: logoAspect ? `${Math.round(36 * logoAspect)}px` : 'auto',
          backgroundColor: '#0055F7',
          WebkitMaskImage: `url(${logo})`,
          maskImage: `url(${logo})`,
          WebkitMaskRepeat: 'no-repeat',
          maskRepeat: 'no-repeat',
          WebkitMaskPosition: 'left center',
          maskPosition: 'left center',
          WebkitMaskSize: 'contain',
          maskSize: 'contain'
        } as React.CSSProperties}
      />
      <p 
        className="block text-nowrap whitespace-pre"
        style={{
          marginLeft: '4px',
          color: '#0055F7',
          fontFeatureSettings: "'liga' off, 'clig' off",
          fontFamily: '"Instrument Sans"',
          fontSize: '42px',
          fontStyle: 'italic',
          fontWeight: '700',
          lineHeight: '36px',
          transform: 'translateY(2px)'
        }}
        onLoad={() => {
          const img = new Image();
          img.onload = () => setLogoAspect(img.naturalWidth / img.naturalHeight);
          img.src = logo as any;
        }}
      >
        Ques
      </p>
    </div>
  );
}

function IconButton({ children, onClick, className = "", ...rest }: { children: React.ReactNode, onClick?: () => void, className?: string, [key: string]: any }) {
  return (
    <motion.button
      className={`flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-full ${className}`}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      {...rest}
    >
      {children}
    </motion.button>
  );
}

function FilterSidebar({ isOpen, onClose, filters, setFilters, suppressMatchIndicator, onToggleMatchIndicator }: {
  isOpen: boolean;
  onClose: () => void;
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  suppressMatchIndicator: boolean;
  onToggleMatchIndicator: (enabled: boolean) => void;
}) {
  const [activeAgeSlider, setActiveAgeSlider] = useState<'left' | 'right' | null>(null);
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 bg-black/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="absolute bottom-0 left-0 right-0 w-[393px] h-[852px] mx-auto bg-white rounded-t-[32px] shadow-2xl"
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
                  onClick={onClose}
                  className="absolute left-4 p-2 text-[#0055F7] hover:text-[#0043C4] transition-colors"
                >
                  <ArrowLeft size={24} />
                </button>
                <h1 className="text-2xl font-bold text-gray-900">{t('filterTitle')}</h1>
                <div className="text-gray-400 text-sm mt-2">{t('addFiltersHint')}</div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
                {/* Distance Section */}
                <div>
                  <label className="block text-lg font-medium text-gray-800 mb-4">{t('maxDistance')}</label>
                  <div className="relative">
                    <div className="relative h-2 rounded-full bg-gray-200">
                      <div 
                        className="absolute top-0 left-0 h-2 rounded-full bg-[#0055F7]" 
                        style={{ width: `${(filters.distance[1] / 160) * 100}%` }}
                      />
                      <input 
                        className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer top-0"
                        type="range"
                        min="1"
                        max="160"
                        value={filters.distance[1]}
                        onChange={(e) => setFilters({
                        ...filters,
                          distance: [filters.distance[0], parseInt(e.target.value)]
                        })}
                      />
                </div>
                    <div className="flex justify-between text-sm text-gray-500 mt-2">
                      <span>1 km</span>
                      <span>160km+</span>
                    </div>
                    <div className="text-center text-[#0055F7] font-semibold mt-2 text-lg">
                      {filters.distance[1]} km
                    </div>
                    {/* 新增城市和超距开关 */}
                    <div className="flex flex-col gap-3 mt-4">
                      <label className="flex items-center justify-between">
                        <span className="text-base text-gray-700 min-w-[120px]">{t('sameCity')}</span>
                  <Checkbox
                          checked={filters.sameCity || false}
                          onCheckedChange={checked => setFilters({ ...filters, sameCity: !!checked })}
                          className="h-5 w-5 border-2 border-[#0055F7] bg-white data-[state=checked]:bg-white data-[state=checked]:border-[#0055F7] data-[state=checked]:text-[#0055F7]"
                        />
                      </label>
                      <label className="flex items-center justify-between">
                        <span className="text-base text-gray-700 min-w-[120px]">{t('showOutOfDistance')}</span>
                        <Checkbox
                          checked={filters.showOutOfDistance || false}
                          onCheckedChange={checked => setFilters({ ...filters, showOutOfDistance: !!checked })}
                          className="h-5 w-5 border-2 border-[#0055F7] bg-white data-[state=checked]:bg-white data-[state=checked]:border-[#0055F7] data-[state=checked]:text-[#0055F7]"
                        />
                      </label>
                </div>
              </div>
            </div>

                {/* Age Section */}
                <div>
                  <label className="block text-lg font-medium text-gray-800 mb-4">{t('age')}</label>
                  <div className="relative">
                    <div className="relative h-2 rounded-full bg-gray-200">
                      <div 
                        className="absolute top-0 h-2 rounded-full bg-[#0055F7]" 
                        style={{ 
                          left: `${((filters.age[0] - 18) / (65 - 18)) * 100}%`,
                          width: `${((filters.age[1] - filters.age[0]) / (65 - 18)) * 100}%`
                        }}
                      />
                      {/* 左滑块 */}
                      <input 
                        className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer top-0 age-slider-left"
                        type="range"
                        min="18"
                        max="65"
                        value={filters.age[0]}
                        onChange={(e) => {
                          const newMin = parseInt(e.target.value);
                          if (newMin < filters.age[1]) {
                      setFilters({
                        ...filters,
                              age: [newMin, filters.age[1]]
                            });
                          }
                        }}
                        onMouseDown={() => setActiveAgeSlider('left')}
                        onTouchStart={() => setActiveAgeSlider('left')}
                        onMouseUp={() => setActiveAgeSlider(null)}
                        onTouchEnd={() => setActiveAgeSlider(null)}
                        style={{
                          background: 'transparent',
                          zIndex: activeAgeSlider === 'left' ? 50 : 10
                        }}
                      />
                      {/* 右滑块 */}
                      <input 
                        className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer top-0 age-slider-right"
                        type="range"
                        min="18"
                        max="65"
                        value={filters.age[1]}
                        onChange={(e) => {
                          const newMax = parseInt(e.target.value);
                          if (newMax > filters.age[0]) {
                      setFilters({
                        ...filters,
                              age: [filters.age[0], newMax]
                            });
                          }
                        }}
                        onMouseDown={() => setActiveAgeSlider('right')}
                        onTouchStart={() => setActiveAgeSlider('right')}
                        onMouseUp={() => setActiveAgeSlider(null)}
                        onTouchEnd={() => setActiveAgeSlider(null)}
                        style={{
                          background: 'transparent',
                          zIndex: activeAgeSlider === 'right' ? 50 : 10
                        }}
                      />
                </div>
                    <div className="flex justify-between text-sm text-gray-500 mt-2">
                      <span>18</span>
                      <span>65+</span>
                    </div>
                    <div className="text-center text-[#0055F7] font-semibold mt-2 text-lg">
                      {filters.age[0]}-{filters.age[1]}
                    </div>
              </div>
            </div>

                {/* Project Status Section */}
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-4">{i18nCurrentLanguage === 'en' ? 'Project Status' : t('projectStatus') || '项目状态'}</h3>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setFilters({
                        ...filters,
                        projectStatus: { ...filters.projectStatus, not_started: !filters.projectStatus.not_started }
                      })}
                      className={`flex-1 py-3 px-4 rounded-full text-sm font-semibold transition-all duration-300 transform hover:scale-105 ${
                        filters.projectStatus.not_started
                          ? 'bg-gradient-to-r from-[#0055F7] to-[#0043C4] text-white shadow-lg'
                          : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-[#0055F7] hover:text-[#0055F7]'
                      }`}
                    >
                      {t('notStarted')}
                    </button>
                    <button
                      onClick={() => setFilters({
                        ...filters,
                        projectStatus: { ...filters.projectStatus, ongoing: !filters.projectStatus.ongoing }
                      })}
                      className={`flex-1 py-3 px-4 rounded-full text-sm font-semibold transition-all duration-300 transform hover:scale-105 ${
                        filters.projectStatus.ongoing
                          ? 'bg-gradient-to-r from-[#0055F7] to-[#0043C4] text-white shadow-lg'
                          : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-[#0055F7] hover:text-[#0055F7]'
                      }`}
                    >
                      {t('ongoing')}
                    </button>
                    <button
                      onClick={() => setFilters({
                        ...filters,
                        projectStatus: { ...filters.projectStatus, finished: !filters.projectStatus.finished }
                      })}
                      className={`flex-1 py-3 px-4 rounded-full text-sm font-semibold transition-all duration-300 transform hover:scale-105 ${
                        filters.projectStatus.finished
                          ? 'bg-gradient-to-r from-[#0055F7] to-[#0043C4] text-white shadow-lg'
                          : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-[#0055F7] hover:text-[#0055F7]'
                      }`}
                    >
                      {t('finished')}
                    </button>
                  </div>
                </div>

                {/* Project Types Section */}
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-4">{t('projectTypes')}</h3>
                  {/* 搜索框 */}
                  <input
                    type="text"
                    placeholder={t('searchTypePlaceholder')}
                    value={filters.typeSearch || ''}
                    onChange={e => setFilters({ ...filters, typeSearch: e.target.value })}
                    className="w-full mb-4 px-4 py-2 border border-gray-200 rounded-full focus:ring-2 focus:ring-[#0055F7] focus:border-[#0055F7] focus:outline-none transition duration-300 bg-white placeholder:text-gray-400"
                  />
                  <div className="flex flex-wrap gap-3">
                    {projectTypes.filter(type =>
                      !filters.typeSearch || type.toLowerCase().includes(filters.typeSearch.toLowerCase())
                    ).map((type) => (
                      <button
                        key={type}
                    onClick={() => {
                      const newTypes = filters.projectTypes.includes(type)
                        ? filters.projectTypes.filter(t => t !== type)
                        : [...filters.projectTypes, type];
                      setFilters({ ...filters, projectTypes: newTypes });
                    }}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 transform hover:scale-105 ${
                          filters.projectTypes.includes(type)
                            ? 'bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 hover:from-blue-200 hover:to-blue-300'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300 hover:text-gray-800'
                        }`}
                  >
                    {type}
                      </button>
                ))}
              </div>
              </div>
            </div>

              {/* Bottom Action */}
              <div className="p-6 border-t border-gray-100">
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setFilters({
                        projectStatus: { ongoing: true, finished: true, not_started: true },
                        projectTypes: [],
                        distance: [0, 50],
                        gender: [],
                        age: [18, 65],
                        sameCity: false,
                        showOutOfDistance: false,
                        typeSearch: ''
                      });
                    }}
                    className="flex-1 py-4 bg-white text-[#0055F7] border-2 border-[#0055F7] rounded-full font-semibold text-lg hover:bg-[#0055F7] hover:text-white transition-all duration-300 transform hover:scale-105"
                  >
                    {t('reset')}
                  </button>
                  <button
                    onClick={onClose}
                    className="flex-1 py-4 bg-gradient-to-r from-[#0055F7] to-[#0043C4] text-white rounded-full font-semibold text-lg shadow-lg hover:from-[#0043C4] hover:to-[#0032A3] transition-all duration-300 transform hover:scale-105"
                  >
                    {t('applyFilters')}
                  </button>
              </div>
                
                {/* Right-swipe hint toggle */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between py-3">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-800 mb-1">{i18nCurrentLanguage === 'en' ? 'Right-swipe hint popup' : '右滑提示弹窗'}</h4>
                      <p className="text-xs text-gray-500">{i18nCurrentLanguage === 'en' ? 'Show detailed match hint when right-swiping a project' : '右滑项目时显示详细匹配提示'}</p>
                    </div>
                    <Checkbox
                      checked={!suppressMatchIndicator}
                      onCheckedChange={(checked) => onToggleMatchIndicator(!!checked)}
                      className="h-5 w-5 border-2 border-[#0055F7] bg-white data-[state=checked]:bg-white data-[state=checked]:border-[#0055F7] data-[state=checked]:text-[#0055F7]"
                    />
                  </div>
                </div>
            </div>
          </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function SwipeFeedback({ direction, onComplete }: { direction: 'left' | 'right'; onComplete: () => void }) {
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
}

// 新增：匹配指示组件
function MatchIndicator({ project, onClose, onSuppress }: { project: Project; onClose: () => void; onSuppress: () => void }) {
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
          {/* 匹配图标 */}
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
          
          {/* 标题 */}
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            {i18nCurrentLanguage === 'en' ? 'Project liked' : '已右滑项目'}
          </h3>
          
          {/* 项目信息 */}
          <div className="bg-gray-50 rounded-lg p-3 mb-4">
            <h4 className="font-semibold text-gray-800 mb-1">{project.title}</h4>
            <p className="text-sm text-gray-600">{project.author}</p>
          </div>
          
          {/* 说明文字 */}
          <p className="text-gray-600 text-sm leading-relaxed mb-4">
            {i18nCurrentLanguage === 'en' ? 'Waiting for the other party to like your project as well to start a chat' : '等待对方也右滑你的项目来开启对话'}
          </p>
          
          {/* 提示图标 */}
          <div className="flex items-center justify-center gap-2 text-blue-600 text-sm mb-4">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
            <span>{i18nCurrentLanguage === 'en' ? 'Both sides must like to chat' : '双向匹配才能聊天'}</span>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
          </div>
          
          {/* 不再显示选项 */}
          <button
            onClick={onSuppress}
            className="text-gray-500 text-xs hover:text-gray-700 transition-colors underline"
          >
            {i18nCurrentLanguage === 'en' ? "Don't show this hint again" : '不再显示此提示'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// 新增：简单右滑动画组件
function SwipeAnimation() {
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
}

function ProjectCard({ project, index, onSwipe, isTop, onClick, isHistory = false, captureRef }: { 
  project: Project, 
  index: number, 
  onSwipe: (direction: 'left' | 'right') => void,
  isTop: boolean,
  onClick: () => void,
  isHistory?: boolean,
  captureRef?: React.Ref<HTMLDivElement>
}) {
  const [exitX, setExitX] = useState(0);
  const [exitY, setExitY] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [pointerDownTime, setPointerDownTime] = useState<number | null>(null);
  const [pointerDownPos, setPointerDownPos] = useState<{x: number, y: number} | null>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useSpring(
    useTransform(x, [-200, 0, 200], [-20, 0, 20]),
    { stiffness: 300, damping: 20 }
  );

  // 拖动开始
  const handlePointerDown = (e: React.PointerEvent) => {
    setPointerDownTime(Date.now());
    setPointerDownPos({ x: e.clientX, y: e.clientY });
    setDragging(false);
  };

  // 拖动中
  const handlePointerMove = (e: React.PointerEvent) => {
    if (pointerDownPos) {
      const dx = e.clientX - pointerDownPos.x;
      const dy = e.clientY - pointerDownPos.y;
      if (!dragging && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) {
        setDragging(true);
      }
    }
  };

  // 拖动/点击结束
  const handlePointerUp = (e: React.PointerEvent) => {
    if (!pointerDownTime || !pointerDownPos) return;
    const dt = Date.now() - pointerDownTime;
    const dx = e.clientX - pointerDownPos.x;
    const dy = e.clientY - pointerDownPos.y;
    if (!dragging && dt < 200 && Math.abs(dx) < 8 && Math.abs(dy) < 8) {
      // 视为点击
      onClick();
    }
    setPointerDownTime(null);
    setPointerDownPos(null);
    setDragging(false);
  };

  // 拖动松手后判断卡片中心位置
  const handleDragEnd = (_event: any, info: PanInfo) => {
    if (isHistory) return;
    // 计算拖动后卡片中心点距离原点的欧氏距离
    const distance = Math.sqrt(info.offset.x * info.offset.x + info.offset.y * info.offset.y);
    const threshold = 80; // 圆形阈值半径
    if (distance < threshold) {
      // 归位动画：更平滑的spring
      setExitX(0);
      setExitY(0);
      x.set(0);
      y.set(0);
    } else {
      // 飞出动画：带旋转和速度，方向与拖动方向一致
      const direction = info.offset.x > 0 ? 1 : -1;
      const velocity = Math.max(Math.abs(info.velocity.x), 800);
      setExitX(direction * 1200);
      setExitY(info.offset.y * 2 + info.velocity.y * 0.5);
      // 旋转角度与拖动方向相关
      // 右滑弹窗逻辑
      if (direction > 0) {
        onSwipe('right');
      } else {
        onSwipe('left');
      }
    }
  };

  const renderCardContent = () => {
    switch (project.cardStyle) {
      case 'image':
        return (
          <>
            <ImageWithFallback
              src={project.background!}
              alt={project.title}
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <h2 className="text-[32px] font-bold leading-[36px] mb-2">
                  {project.title}
                </h2>
                <p className="text-white/90 text-sm mb-3 leading-5">
                  {project.description}
                </p>
                <div className="flex items-center mb-4">
                  <span className="font-medium">{t('cardBy')}&nbsp;</span>
                  <span className="font-semibold">{project.author}</span>
                  <span className="mx-2">·</span>
                  <span className="font-semibold">{project.collaborators}</span>
                  <span className="font-medium">&nbsp;{t('cardCollaborators')}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag, i) => (
                    <motion.span
                      key={tag}
                      className="px-3 py-1 bg-white/20 text-white border border-white/30 rounded-full text-xs font-medium whitespace-nowrap"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      {tag}
                    </motion.span>
                  ))}
                </div>
              </motion.div>
            </div>
          </>
        );
      
      case 'video':
        return (
          <>
            <div className={`absolute inset-0 ${project.gradientBackground || getRandomGradient()}`} />
            <video
              className="absolute inset-0 w-full h-full object-cover"
              autoPlay
              muted
              loop
              playsInline
            >
              <source src="https://videos.pexels.com/video-files/4753989/4753989-hd_1920_1080_24fps.mp4" type="video/mp4" />
            </video>
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
            <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-full p-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
            </div>
            <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <h2 className="text-[32px] font-bold leading-[36px] mb-2">
                  {project.title}
                </h2>
                <p className="text-white/90 text-sm mb-3 leading-5">
                  {project.description}
                </p>
                <div className="flex items-center mb-4">
                  <span className="font-medium">{t('cardBy')}&nbsp;</span>
                  <span className="font-semibold">{project.author}</span>
                  <span className="mx-2">·</span>
                  <span className="font-semibold">{project.collaborators}</span>
                  <span className="font-medium">&nbsp;{t('cardCollaborators')}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag, i) => (
                    <motion.span
                      key={tag}
                      className="px-3 py-1 bg-white/20 text-white border border-white/30 rounded-full text-xs font-medium whitespace-nowrap"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      {tag}
                    </motion.span>
                  ))}
                </div>
              </motion.div>
            </div>
          </>
        );
      
      case 'text-only':
        return (
          <>
            <div className={`absolute inset-0 ${project.gradientBackground || getRandomGradient()}`} />
            <div className="absolute inset-0 bg-black/20" />
            {/* Geometric pattern background */}
            <div className="absolute inset-0 opacity-10">
              {[...Array(20)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 bg-white rounded-full"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                  }}
                  animate={{
                    scale: [0, 1, 0],
                    opacity: [0, 1, 0],
                  }}
                  transition={{
                    duration: 2 + Math.random() * 2,
                    repeat: Infinity,
                    delay: Math.random() * 2,
                  }}
                />
              ))}
            </div>
            <div className="absolute inset-0 p-6 text-white flex flex-col justify-center">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center"
              >
                <h2 className="text-[28px] font-bold leading-[32px] mb-4">
                  {project.title}
                </h2>
                <p className="text-white/90 text-base leading-6 mb-6">
                  {project.description}
                </p>
                <div className="flex items-center justify-center mb-4">
                  <span className="font-medium">{t('cardBy')}&nbsp;</span>
                  <span className="font-semibold">{project.author}</span>
                  <span className="mx-2">·</span>
                  <span className="font-semibold">{project.collaborators}</span>
                  <span className="font-medium">&nbsp;{t('cardCollaborators')}</span>
                </div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {project.tags.map((tag, i) => (
                    <motion.span
                      key={tag}
                      className="px-3 py-1 bg-white/20 text-white border border-white/30 rounded-full text-xs font-medium whitespace-nowrap"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      {tag}
                    </motion.span>
                  ))}
                </div>
              </motion.div>
            </div>
          </>
        );
      

      
      default:
        return null;
    }
  };

  // 统一"点击 vs 拖动"判断（移动端与桌面）
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
    if (isTap) onClick();
  };

  const resolveDir = (dir: string): 'left' | 'right' => {
    if (dir === 'left' || dir === 'right') return dir;
    return lastDxRef.current >= 0 ? 'right' : 'left';
  };

  const baseCardClass = `w-[357px] h-[580px] rounded-[14px] overflow-hidden relative cursor-pointer pressable`;
  const topShadow = `shadow-[0px_18px_40px_0px_rgba(0,0,0,0.30)]`;
  const underShadow = `shadow-[0px_8px_24px_0px_rgba(0,0,0,0.18)]`;

  return (
    <TinderCard
       className="absolute inset-0"
      key={project.id}
      onSwipe={(dir: string) => {
        if (isHistory) return; // disable swipe handling for preview/history cards
        const mapped = resolveDir(dir);
        handledRef.current = true;
        onSwipe(mapped);
      }}
      onCardLeftScreen={() => {
        if (isHistory) return; // disable for preview/history cards
        if (!handledRef.current) {
          const mapped = lastDxRef.current >= 0 ? 'right' : 'left';
          onSwipe(mapped);
        }
        handledRef.current = false;
        lastDxRef.current = 0;
      }}
      preventSwipe={[ 'down', ...(isHistory ? ['left', 'right', 'up'] : []) ]}
      swipeRequirementType={SWIPE_REQUIREMENT}
      swipeThreshold={SWIPE_THRESHOLD_PX}
    >
      <div
        className="absolute inset-0"
        style={{ zIndex: 999 }}
      >
                  <div
            className={`${baseCardClass} ${isTop ? topShadow : underShadow} ${isTop ? 'hover:scale-[1.02] transition-transform duration-150 will-change-transform' : ''}`}
            onMouseDown={handleDown}
            onMouseMove={handleMove}
            onMouseUp={handleUp}
            onTouchStart={handleDown}
            onTouchMove={handleMove}
            onTouchEnd={handleUp}
            ref={captureRef}
            style={isTop && PROMO_TILT ? { transform: 'translate(-50px, -16px) rotate(-6deg)', transformOrigin: 'center', boxShadow: '0px 18px 40px rgba(0,0,0,0.30)' } : undefined}
          >
          {renderCardContent()}
        </div>
      </div>
    </TinderCard>
  );
}

function MediaViewer({ media, onClose, initialIndex = 0 }: { media: string[]; onClose: () => void; initialIndex?: number }) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  // 当initialIndex变化时更新currentIndex
  useEffect(() => {
    setCurrentIndex(initialIndex);
  }, [initialIndex]);

  const handleBackgroundClick = (e: React.MouseEvent) => {
    // 检查点击的是否是背景元素
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <motion.div
      className="fixed left-0 right-0 top-0 bottom-0 w-[393px] h-[852px] mx-auto my-auto bg-black/90 z-50 flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={handleBackgroundClick}
    >
        {/* Close button */}
        <button
        onClick={(e) => {
          e.stopPropagation();
          onClose();
        }}
        className="absolute top-12 right-4 z-10 p-2 bg-black/50 rounded-full text-white hover:bg-black/70 transition-colors"
        >
          <X size={24} />
        </button>
      <div 
        className="relative w-full flex flex-col items-center justify-center"
        onClick={e => e.stopPropagation()}
      >
        {/* Swiper大图浏览 */}
        <Swiper
          spaceBetween={0}
          slidesPerView={1}
          initialSlide={currentIndex}
          onSlideChange={(swiper: any) => setCurrentIndex(swiper.activeIndex)}
          className="w-full h-full"
          style={{ width: '100%', height: '100%' }}
          onClick={(e: any) => e.stopPropagation()}
        >
          {media.map((url, index) => (
            <SwiperSlide key={index} className="w-full h-full" onClick={(e: any) => e.stopPropagation()}>
              <div 
                className="w-full h-full flex items-center justify-center"
                onClick={(e: any) => e.stopPropagation()}
              >
                {url.endsWith('.mp4') || url.endsWith('.webm') || url.endsWith('.mov') ? (
                <video
                  src={url}
                    className="max-w-full max-h-full object-contain rounded-lg"
                  controls
                  autoPlay
                    onClick={(e: any) => e.stopPropagation()}
                />
                ) : (
              <ImageWithFallback
                src={url}
                    alt={`Media ${index + 1}`}
                    className="max-w-full max-h-full object-contain rounded-lg"
                    onClick={(e: any) => e.stopPropagation()}
                  />
                )}
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
        {/* Slide indicators */}
        {media.length > 1 && (
          <div 
            className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 z-20"
            onClick={(e: any) => e.stopPropagation()}
          >
            {media.map((_, index) => (
              <button
                key={index}
                onClick={(e: any) => {
                  e.stopPropagation();
                  setCurrentIndex(index);
                }}
                className={`w-2 h-2 rounded-full transition-all duration-200 ${
                  index === currentIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

function ProjectDetailView({ project, onClose, suppressFirstTap = false, isFavorite = false, onLikeChange }: { project: Project; onClose: () => void; suppressFirstTap?: boolean, isFavorite?: boolean, onLikeChange?: (project: Project, liked: boolean) => void }) {
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showNavButtons, setShowNavButtons] = useState(false);
  const swiperRef = useRef<any>(null);
  const buttonTimerRef = useRef<number | null>(null);
  const [clickEnabled, setClickEnabled] = useState(!suppressFirstTap);
  // Like state and animation
  const [liked, setLiked] = useState(isFavorite);
  const [likeAnimate, setLikeAnimate] = useState(false);
  const [staticExporting, setStaticExporting] = useState(false);
  const detailRef = useRef<HTMLDivElement | null>(null);
  const headerRef = useRef<HTMLDivElement | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);
  const mediaWrapRef = useRef<HTMLDivElement | null>(null);

  const isVideoUrl = (url: string) => /\.(mp4|webm|mov)(\?.*)?$/i.test(url);
  const pickStaticImageFor = (idx: number): string | null => {
    const url = project.media[idx];
    if (url && !isVideoUrl(url)) return url;
    if (project.background) return project.background;
    const firstImg = project.media.find(u => u && !isVideoUrl(u));
    return firstImg || null;
  };
  const exportDetailAsImage = async () => {
    let origScrollBg: string = '';
    let origScrollPaddingRight: string = '';
    let origNodeWidth: string = '';
    let origScrollWidth: string = '';
    let origScrollOverflow: string = '';
    let origMediaRadius: string = '';
    let origMediaOverflow: string = '';
    let origMediaWidth: string = '';
    let origMediaBg: string = '';
    try {
      const node = detailRef.current;
      if (!node) return;
 
      const headerEl = headerRef.current;
      const scrollEl = scrollAreaRef.current;
      const mediaEl = mediaWrapRef.current;
 
      // Switch to static media render to avoid video/slider artifacts
      setStaticExporting(true);
      await new Promise(requestAnimationFrame);
      await new Promise(requestAnimationFrame);
 
      // Store original inline styles to restore later
      const origNodeHeight = node.style.height;
      const origNodeOverflow = node.style.overflow;
      origNodeWidth = node.style.width;
      const origScrollHeight = scrollEl ? scrollEl.style.height : '';
      origScrollOverflow = scrollEl ? scrollEl.style.overflow : '';
      origScrollWidth = scrollEl ? scrollEl.style.width : '';
      origScrollBg = scrollEl ? (scrollEl.style.background || '') : '';
      origScrollPaddingRight = scrollEl ? (scrollEl.style.paddingRight || '') : '';
      if (mediaEl) {
        origMediaRadius = mediaEl.style.borderRadius;
        origMediaOverflow = mediaEl.style.overflow;
        origMediaWidth = mediaEl.style.width;
        origMediaBg = mediaEl.style.background;
      }
 
      // Compute total content height (header + full scroll content)
      const headerH = headerEl ? headerEl.offsetHeight : 0;
      const contentH = scrollEl ? scrollEl.scrollHeight : node.scrollHeight;
      const totalH = headerH + contentH;
 
      // Expand containers to full content
      node.style.height = `${totalH}px`;
      node.style.overflow = 'visible';
      node.style.width = '393px';
      if (scrollEl) {
        scrollEl.style.height = `${contentH}px`;
        scrollEl.style.overflow = 'hidden';
        scrollEl.style.width = '393px';
        scrollEl.style.background = 'transparent';
        scrollEl.style.paddingRight = '0px';
      }
      if (mediaEl) {
        mediaEl.style.borderRadius = '0px';
        mediaEl.style.overflow = 'hidden';
        mediaEl.style.width = '393px';
        mediaEl.style.background = 'transparent';
      }
 
      // Add a scoped style to hide scrollbars and avoid gutter during export
      node.setAttribute('data-export-snap', 'true');
      const styleEl = document.createElement('style');
      styleEl.setAttribute('data-export-style', 'true');
      styleEl.textContent = `
        [data-export-snap="true"] { scrollbar-width: none; -ms-overflow-style: none; }
        [data-export-snap="true"] * { overscroll-behavior: contain; }
        [data-export-snap="true"]::-webkit-scrollbar { display: none; width: 0; height: 0; }
        [data-export-snap="true"] *::-webkit-scrollbar { display: none; width: 0; height: 0; }
        [data-export-snap="true"] [data-export-ignore="true"] { display: none !important; visibility: hidden !important; }
        [data-export-snap="true"] [data-media-wrap] { width: 393px !important; border-radius: 0 !important; overflow: hidden !important; background: transparent !important; }
        [data-export-snap="true"] [data-media-wrap] img,
        [data-export-snap="true"] [data-media-wrap] video { width: 100% !important; height: 100% !important; object-fit: cover !important; background: transparent !important; display: block !important; }
      `;
      node.appendChild(styleEl);
 
      const dataUrl = await toPng(node, {
        cacheBust: true,
        pixelRatio: window.devicePixelRatio || 2,
        skipFonts: false,
        style: { background: '#ffffff' },
        filter: (n: any) => {
          if (n instanceof HTMLElement) {
            if (n.dataset && n.dataset.exportIgnore === 'true') return false;
          }
          return true;
        }
      });
      const link = document.createElement('a');
      link.download = `card-detail-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
    } catch (e) {
      console.error('Export detail failed', e);
    } finally {
      // Restore styles
      const node = detailRef.current;
      const scrollEl = scrollAreaRef.current;
      const mediaEl = mediaWrapRef.current;
      if (node) {
        node.style.height = '';
        node.style.overflow = '';
        node.style.width = origNodeWidth;
        node.removeAttribute('data-export-snap');
        const s = node.querySelector('style[data-export-style="true"]');
        if (s) s.remove();
      }
      if (scrollEl) {
        scrollEl.style.height = '';
        scrollEl.style.overflow = origScrollOverflow;
        scrollEl.style.width = origScrollWidth;
        scrollEl.style.background = origScrollBg;
        scrollEl.style.paddingRight = origScrollPaddingRight;
      }
      if (mediaEl) {
        mediaEl.style.borderRadius = origMediaRadius;
        mediaEl.style.overflow = origMediaOverflow;
        mediaEl.style.width = origMediaWidth;
        mediaEl.style.background = origMediaBg;
        mediaEl.removeAttribute('data-media-wrap');
      }
      setStaticExporting(false);
    }
  };
  const handleLike = () => {
    setLiked(prev => {
      const next = !prev;
      if (onLikeChange) onLikeChange(project, next);
      return next;
    });
    setLikeAnimate(true);
    setTimeout(() => setLikeAnimate(false), 500);
  };
  useEffect(() => {
    if (suppressFirstTap) {
      const t = setTimeout(() => setClickEnabled(true), 200);
      return () => clearTimeout(t as any);
    }
  }, [suppressFirstTap]);

  const showButtons = () => {
    setShowNavButtons(true);
    // 清除之前的定时器
    if (buttonTimerRef.current) {
      clearTimeout(buttonTimerRef.current);
    }
    // 设置新的定时器
    buttonTimerRef.current = setTimeout(() => {
      setShowNavButtons(false);
    }, 2000);
  };

  const handleSlideChange = (swiper: any) => {
    setCurrentSlide(swiper.activeIndex);
    // 切换图片时重新显示按钮
    showButtons();
  };

  // 项目状态tag颜色映射
  const statusColorMap = {
    'not_started': 'bg-gray-300 text-gray-800',
    'ongoing': 'bg-[#0055F7] text-white',
    'finished': 'bg-green-500 text-white',
  };

  return (
    <motion.div
      className="absolute left-0 right-0 mx-auto w-[393px] bg-white z-50 top-0 bottom-0"
      initial={{ rotateY: 180, opacity: 0 }}
      animate={{ rotateY: 0, opacity: 1 }}
      exit={{ rotateY: 180, opacity: 0 }}
      transition={{ duration: 0.6, ease: "easeInOut" }}
    >
      <div ref={detailRef} className="w-full h-full flex flex-col">
        {/* Header */}
                    <div ref={headerRef} className="h-[90px] flex items-center justify-between px-4 border-b border-[#E8EDF2] bg-[#FAFAFA]">
               <button onClick={onClose} className="p-2">
                 <ArrowLeft size={24} className="text-blue-600" />
               </button>
               <h1 className="font-semibold">
                 {t('projectDetails')}
               </h1>
               <div className="w-10 flex items-center justify-end">
                <IconButton onClick={exportDetailAsImage} data-export-ignore="true">
                   <div className="w-6 h-6">
                     <svg className="block size-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                       <path d="M9 3l-1.5 2H5a2 2 0 00-2 2v10a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2h-2.5L15 3H9z" stroke="#0055F7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                       <circle cx="12" cy="12" r="3.5" stroke="#0055F7" strokeWidth="2"/>
                     </svg>
                   </div>
                 </IconButton>
               </div>
             </div>

        <div ref={scrollAreaRef} className="flex-1 overflow-y-auto">
          <div className="space-y-6">
            {/* Media Carousel */}
            <div 
              ref={mediaWrapRef}
              data-media-wrap="true"
              className="relative w-full h-96 bg-gray-100 rounded-lg overflow-hidden"
              onTouchStart={showButtons}
              onMouseEnter={() => setShowNavButtons(true)}
              onMouseLeave={() => setShowNavButtons(false)}
            >
            {staticExporting ? (
              (() => {
                const img = pickStaticImageFor(currentSlide);
                return (
                  <div className="w-full h-full flex items-center justify-center">
                    {img ? (
                      <ImageWithFallback src={img} alt="Static Export" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full bg-white" />
                    )}
                  </div>
                );
              })()
            ) : project.media.length > 0 ? (
              <Swiper
                spaceBetween={0}
                slidesPerView={1}
                onSlideChange={handleSlideChange}
                initialSlide={currentSlide}
                style={{ width: '100%', height: '100%' }}
                onSwiper={(swiper: any) => { swiperRef.current = swiper; }}
              >
                {project.media.map((url, index) => (
                  <SwiperSlide key={index}>
                    <div 
                      className="w-full h-full flex items-center justify-center cursor-pointer"
                      onClick={() => { setCurrentSlide(index); setShowMediaViewer(true); }}
                    >
                      {isVideoUrl(url) ? (
                        <video
                          src={url}
                          className="w-full h-full object-cover"
                          controls
                          muted
                        />
                      ) : (
                        <ImageWithFallback
                          src={url}
                          alt={`Media ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
            ) : (
              /* Fallback for no media */
              <div className="w-full h-48 rounded-lg overflow-hidden">
                {project.background ? (
                  <ImageWithFallback
                    src={project.background}
                    alt={project.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 flex items-center justify-center">
                    <h3 className="text-white text-2xl font-bold">{project.title}</h3>
                  </div>
                )}
              </div>
            )}
              {/* 左右切换按钮 - 手指触摸时显示 */}
              {project.media.length > 1 && (
                <>
                  <button
                    onClick={() => swiperRef.current?.slidePrev()}
                    disabled={currentSlide === 0}
                    className={`absolute left-2 top-1/2 transform -translate-y-1/2 w-10 h-10 bg-black/30 hover:bg-black/50 text-white rounded-full flex items-center justify-center transition-opacity duration-200 disabled:opacity-0 z-20 ${
                      showNavButtons ? 'opacity-100' : 'opacity-0'
                    }`}
                  >
                    <ChevronLeft size={20} />
                  </button>
                  <button
                    onClick={() => swiperRef.current?.slideNext()}
                    disabled={currentSlide === project.media.length - 1}
                    className={`absolute right-2 top-1/2 transform -translate-y-1/2 w-10 h-10 bg-black/30 hover:bg-black/50 text-white rounded-full flex items-center justify-center transition-opacity duration-200 disabled:opacity-0 z-20 ${
                      showNavButtons ? 'opacity-100' : 'opacity-0'
                    }`}
                  >
                    <ChevronRight size={20} />
                  </button>
                </>
              )}
              {/* Slide indicators */}
              {project.media.length > 1 && (
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 z-20">
                  {project.media.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentSlide(index)}
                      className={`w-2 h-2 rounded-full transition-all duration-200 ${
                        index === currentSlide ? 'bg-white' : 'bg-white/50'
                      }`}
                    />
                  ))}
                </div>
              )}
              {project.media.length > 1 && (
                <div className={`absolute top-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-xs z-20 transition-opacity duration-200 ${
                  showNavButtons ? 'opacity-100' : 'opacity-0'
                }`}>
                  {currentSlide + 1} / {project.media.length}
                </div>
              )}
            </div>

            <div className="p-6 space-y-6">

            {/* Title and Status */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-3xl font-bold w-full max-w-full whitespace-normal break-words leading-tight">{project.title}</h2>
              </div>
              {project.type === 'project' && (
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className={`inline-block px-3 py-1 rounded-full font-semibold text-xs ${statusColorMap[project.status as keyof typeof statusColorMap]}`}
                    >
                    {project.status === 'not_started' ? '未开始' : project.status === 'ongoing' ? '进行中' : '已完成'}
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar size={16} />
                    <span>{project.startTime}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Target size={16} />
                    <span>{project.currentProgress}% {t('complete')}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Owner Info */}
            <div className="border rounded-lg p-4">
              <h3 className="text-xl font-semibold mb-3">
                {t('projectOwner')}
              </h3>
              <div className="flex items-start gap-3">
                <ImageWithFallback
                  src={project.owner.avatar}
                  alt={project.owner.name}
                  className="w-16 h-16 rounded-full object-cover"
                />
                <div className="flex-1">
                  <h4 className="font-medium">{project.owner.name} {project.owner.gender !== 'Non-binary' && (
                    <span className="ml-0">
                      <svg className="inline w-4 h-4 -mt-0.5" fill="none" viewBox="0 0 24 24">
                        <path d={project.owner.gender === 'Male' ? svgPaths.male : svgPaths.female} stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </span>
                  )} <span className="text-black text-s -ml-1 mr-0.5">,</span> {project.owner.age}</h4>
                  <p className="text-sm text-gray-600">{project.owner.role}</p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <MapPin size={12} />
                      <span>{project.owner.distance} {t('kmAway')}</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {project.owner.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Collaborators - only for projects */}
            {project.type === 'project' && project.collaboratorsList.length > 0 && (
              <div className="border rounded-lg p-4">
                <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  <Users size={20} />
                  {t('collaborators')} ({project.collaboratorsList.length})
                </h3>
                <div className="space-y-3">
                  {project.collaboratorsList.map((collaborator, index) => (
                    <div key={index} className="flex items-center gap-3">
                      {collaborator.avatar ? (
                      <ImageWithFallback
                        src={collaborator.avatar}
                        alt={collaborator.name}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                          <span className="text-gray-500 text-xs font-medium">
                            {collaborator.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                      <div>
                        <p className="font-medium text-sm">{collaborator.name}</p>
                        <p className="text-xs text-gray-600">{collaborator.role}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            <div>
              <h3 className="text-xl font-semibold mb-2">{t('description')}</h3>
              <p className="text-gray-700 leading-relaxed">{project.detailedDescription}</p>
            </div>

            {/* Purpose */}
            <div>
              <h3 className="text-xl font-semibold mb-2">
                {t('purpose')}
              </h3>
              <p className="text-gray-700 leading-relaxed">{project.purpose}</p>
            </div>

            {/* Content - only for projects */}
            {project.type === 'project' && (
              <div>
                <h3 className="text-xl font-semibold mb-2">{t('whatWeAreBuilding')}</h3>
                <p className="text-gray-700 leading-relaxed">{project.content}</p>
              </div>
            )}

            {/* Looking For */}
            <div>
              <h3 className="text-xl font-semibold mb-2">{t('lookingFor')}</h3>
              <div className="flex flex-wrap gap-2 mb-3">
                {project.lookingFor.map((role) => (
                  <Badge key={role} variant="secondary">
                    {role}
                  </Badge>
                ))}
              </div>
              <p className="text-gray-700 leading-relaxed">
                {project.type === 'project' 
                  ? "We're actively seeking talented individuals to join our team and contribute to this exciting project. If you have the skills and passion we're looking for, we'd love to hear from you!"
                  : "I'm looking for interesting opportunities and collaborations that align with my skills and interests. Feel free to reach out if you think we could work well together."
                }
              </p>
            </div>



            {/* Links */}
            <div>
                              <h3 className="text-xl font-semibold mb-2">{t('links')}</h3>
              <div className="space-y-2">
                {project.links.map((link, index) => (
                  <a
                    key={index}
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-600 text-sm"
                  >
                    <ExternalLink size={16} />
                    {link}
                  </a>
                ))}
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      {/* Like button overlay */}
      <button
        onClick={handleLike}
        className={`absolute right-4 bottom-6 z-[60] rounded-full p-3 backdrop-blur-md bg-black/30 hover:bg-black/40 transition ${likeAnimate ? 'like-animation' : ''} ${liked ? 'opacity-40' : 'opacity-70'}`}
        data-export-ignore="true"
        aria-label={liked ? '取消点赞' : '点赞'}
      >
        <svg className="block w-6 h-6" viewBox="0 0 24 24" fill="none">
          <path
            d={svgPaths.like}
            fill={liked ? '#0055F7' : 'none'}
            stroke={liked ? '#0055F7' : '#ffffff'}
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* 大图浏览弹窗 */}
      <AnimatePresence>
        {showMediaViewer && (
          <MediaViewer
            media={project.media}
            onClose={() => setShowMediaViewer(false)}
            initialIndex={currentSlide}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function App() {
  // 新增：应用状态管理
  const [appState, setAppState] = useState<AppState>('launch');
  
  // 语言初始化：从 localStorage 读取并订阅变更，保证全局生效
  const [, forceRerender] = useState(0);
  useEffect(() => {
    try {
      const saved = localStorage.getItem('language');
      if (saved === 'zh' || saved === 'en') setLanguage(saved as 'zh' | 'en');
    } catch {}
    const unsubscribe = subscribeLanguageChange((_lang: 'en' | 'zh') => {
      forceRerender((x) => x + 1);
    });
    return () => { try { unsubscribe && unsubscribe(); } catch {} };
  }, []);
  
  const [smsData, setSmsData] = useState<SMSData>({
    phoneNumber: '',
    verificationCode: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ phoneNumber?: string; verificationCode?: string }>({});
  const [codeSent, setCodeSent] = useState(false);

  // 新增：发布功能相关状态
  const [resumeDraft, setResumeDraft] = useState(false);
  const [selectedDraftId, setSelectedDraftId] = useState<string | undefined>();

  // 新增：聊天功能相关状态
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
  
  // 新增：通知和设置页面导航
  const handleNavigateToNotification = () => {
    setAppState('notification');
  };
  
  const handleNavigateToSettings = () => {
    setAppState('settings');
  };

  // 原有状态管理
  const [currentProjects, setCurrentProjects] = useState(projects);
  const [leftSwipedProjects, setLeftSwipedProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [showFilter, setShowFilter] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  const [isHistoryMode, setIsHistoryMode] = useState(false);
  const [historyIndex, setHistoryIndex] = useState(0);
  // Favorites state
  const [favorites, setFavorites] = useState<Project[]>([]);
  const [isFavoritesMode, setIsFavoritesMode] = useState(false);
  const [favoritesIndex, setFavoritesIndex] = useState(0);
  const [filters, setFilters] = useState<FilterState>({
    projectStatus: { ongoing: true, finished: true, not_started: true },
    projectTypes: [],
    distance: [0, 50],
    gender: [],
    age: [18, 65],
    sameCity: false,
    showOutOfDistance: false,
    typeSearch: ''
  });

  // 新增：匹配指示状态
  const [showMatchIndicator, setShowMatchIndicator] = useState(false);
  const [lastLikedProject, setLastLikedProject] = useState<Project | null>(null);
  const [suppressMatchIndicator, setSuppressMatchIndicator] = useState<boolean>(false);
  const [showSwipeAnimation, setShowSwipeAnimation] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showPublishError, setShowPublishError] = useState<string | null>(null);

  // 新增：是否启用服务端数据（检测令牌）
  const [useServerData, setUseServerData] = useState<boolean>(false);
  useEffect(() => {
    setUseServerData(!!getAccessToken());
  }, []);

  // 初始化用户偏好设置 - 每次登录都重新启用弹窗
  useEffect(() => {
    // 每次登录都重置为显示弹窗
    console.log('Resetting to show match indicator on login'); // 调试信息
    setSuppressMatchIndicator(false);
    // 清除本地存储中的偏好设置
    try {
      localStorage.removeItem('suppressMatchIndicator');
      console.log('Cleared saved preference'); // 调试信息
    } catch (error) {
      console.error('Failed to clear preference:', error);
    }
  }, []);

  // 在进入主页面时拉取服务端项目卡片
  useEffect(() => {
    if (appState === 'main' && useServerData) {
      fetchProjectCards()
        .then((res: CardsResponse) => {
          if (Array.isArray(res?.cards) && res.cards.length > 0) {
            setCurrentProjects(res.cards.map(mapBackendCardToProject));
          }
        })
        .catch(() => {
          // 拉取失败时保持本地内置数据
        });
    }
  }, [appState, useServerData]);

  // 新增：启动页面自动跳转逻辑
  useEffect(() => {
    if (appState === 'launch') {
      const timer = setTimeout(() => {
        setAppState('auth');
      }, 600);
      return () => clearTimeout(timer);
    }
  }, [appState]);

  // Responsive canvas scaling (base design size 393x852)
  const BASE_WIDTH = 393;
  const BASE_HEIGHT = 822;
  const containerRef = useRef<HTMLDivElement | null>(null);
  const topCardWrapperRef = useRef<HTMLDivElement | null>(null);
  const topCardElementRef = useRef<HTMLDivElement | null>(null);
  const profileScrollRef = useRef<HTMLDivElement | null>(null);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState<{ left: number; top: number }>({ left: 0, top: 0 });
  useEffect(() => {
    const update = () => {
      const el = containerRef.current;
      if (!el) return;
      const cw = el.clientWidth;
      const ch = el.clientHeight;
      const s = Math.min(cw / BASE_WIDTH, ch / BASE_HEIGHT);
      setScale(s);
      setOffset({ left: (cw - BASE_WIDTH * s) / 2, top: (ch - BASE_HEIGHT * s) / 2 });
    };
    update();
    window.addEventListener('resize', update);
    window.addEventListener('orientationchange', update);
    return () => {
      window.removeEventListener('resize', update);
      window.removeEventListener('orientationchange', update);
    };
  }, []);

    // 修改handleSwipe逻辑：移除弹窗，添加新的指示方法
  const handleSwipe = (direction: 'left' | 'right') => {
    const top = currentProjects[0];
    if (top && useServerData) {
      const isLike = direction === 'right';
      void sendSwipe(top.id as any, isLike).catch(() => {});
    }
    
    if (direction === 'right') {
      console.log('Right swipe detected, suppressMatchIndicator:', suppressMatchIndicator); // 调试信息
      // 右滑时根据设置显示不同的指示
      if (suppressMatchIndicator) {
        console.log('Showing simple animation'); // 调试信息
        // 显示简单的右侧动画
        setShowSwipeAnimation(true);
        setTimeout(() => {
          setShowSwipeAnimation(false);
        }, 800);
      } else {
        console.log('Showing full match indicator'); // 调试信息
        // 显示完整的匹配指示弹窗
        setLastLikedProject(top);
        setShowMatchIndicator(true);
        // 3秒后自动隐藏指示
        setTimeout(() => {
          setShowMatchIndicator(false);
          setLastLikedProject(null);
        }, 3000);
      }
      // Add to favorites on right swipe
      if (top) {
        setFavorites(prev => (prev.find(p => p.id === top.id) ? prev : [top, ...prev]));
      }
    }
    
    if (direction === 'left' && currentProjects.length > 0) {
      setLeftSwipedProjects(prev => [currentProjects[0], ...prev]);
    }
    
    // 统一处理卡片移除
    setTimeout(() => {
      setCurrentProjects(prev => prev.slice(1));
    }, 600);
  };

  const handleHistorySlide = (direction: 'left' | 'right') => {
    if (direction === 'right' && historyIndex < leftSwipedProjects.length - 1) {
      setHistoryIndex(prev => prev + 1);
    } else if (direction === 'left' && historyIndex > 0) {
      setHistoryIndex(prev => prev - 1);
    }
  };

  const toggleHistoryMode = () => {
    setIsHistoryMode(!isHistoryMode);
    setIsFavoritesMode(false);
    setHistoryIndex(0);
  };

  // Favorites navigation
  const handleFavoriteSlide = (direction: 'left' | 'right') => {
    if (direction === 'right' && favoritesIndex < favorites.length - 1) {
      setFavoritesIndex(prev => prev + 1);
    } else if (direction === 'left' && favoritesIndex > 0) {
      setFavoritesIndex(prev => prev - 1);
    }
  };

  const toggleFavoritesMode = () => {
    setIsFavoritesMode(!isFavoritesMode);
    setIsHistoryMode(false);
    setFavoritesIndex(0);
  };

  const filteredProjects = currentProjects.filter(project => {
    // Project status filter
    if (!filters.projectStatus[project.status as 'ongoing' | 'finished' | 'not_started']) return false;
    // Project types filter
    if (filters.projectTypes.length > 0) {
      const hasMatchingTag = project.tags.some(tag => filters.projectTypes.includes(tag));
      if (!hasMatchingTag) return false;
    }
    
    // Distance filter
    if (project.owner.distance < filters.distance[0] || project.owner.distance > filters.distance[1]) {
      return false;
    }
    
    // Age filter
    if (project.owner.age < filters.age[0] || project.owner.age > filters.age[1]) {
      return false;
    }
    
    return true;
  });

  const displayProjects = isHistoryMode ? leftSwipedProjects : filteredProjects;
  const currentProject = isHistoryMode ? leftSwipedProjects[historyIndex] : null;
  const currentFavorite = isFavoritesMode ? favorites[favoritesIndex] : null;

  // 移除弹窗相关处理函数

  // 新增：认证相关函数
  const validatePhoneNumber = (phone: string) => {
    return /^\+?[\d\s\-\(\)]{10,}$/.test(phone.replace(/\s/g, ''));
  };

  const handleSendSMS = async () => {
    if (!smsData.phoneNumber) {
      setErrors({ phoneNumber: '请输入手机号' });
      return;
    }

    if (!validatePhoneNumber(smsData.phoneNumber)) {
      setErrors({ phoneNumber: '请输入有效的手机号' });
      return;
    }

    setIsLoading(true);
    setErrors({});
    setCodeSent(false);
    setSmsData(prev => ({ ...prev, verificationCode: '' }));
    
    // Simulate SMS sending API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    setCodeSent(true);
  };

  const handleVerifyCode = async () => {
    if (!smsData.verificationCode) {
      setErrors({ verificationCode: '请输入验证码' });
      return;
    }

    if (smsData.verificationCode.length !== 6) {
      setErrors({ verificationCode: '请输入6位验证码' });
      return;
    }

    setIsLoading(true);
    setErrors({});
    
    // Simulate verification API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    // 认证成功后跳转到主页面
    setAppState('main');
    console.log('SMS Authentication successful:', smsData);
  };

  // 移除弹窗相关函数，因为不再需要
  
  // 新增：切换匹配指示偏好的函数
  const toggleMatchIndicator = (enabled: boolean) => {
    console.log('Toggling match indicator:', enabled); // 调试信息
    setSuppressMatchIndicator(!enabled);
  };

  // 新增：发布功能相关处理函数
  const handlePostNewProjectClick = () => {
    console.log('🚀 handlePostNewProjectClick called!');
    console.log('🔍 Current appState:', appState);
    
    // Check if there are any saved drafts
    const savedDrafts = localStorage.getItem('project_drafts');
    let hasDrafts = false;
    
    if (savedDrafts) {
      try {
        const drafts = JSON.parse(savedDrafts);
        hasDrafts = Array.isArray(drafts) && drafts.length > 0;
        console.log('📝 Parsed drafts:', drafts);
      } catch (error) {
        console.error('❌ Error parsing drafts:', error);
        localStorage.removeItem('project_drafts');
      }
    }
    
    console.log('📊 hasDrafts:', hasDrafts);
    if (hasDrafts) {
      // Show draft resume dialog
      console.log('🔄 Setting appState to resume');
      setAppState('resume');
    } else {
      // No drafts, start new project directly
      console.log('🆕 Calling handleStartNewProject');
      handleStartNewProject();
    }
  };

  const handleResumeLatestDraft = () => {
    console.log('🔄 handleResumeLatestDraft called!');
    // Get the latest draft (most recently created)
    const savedDrafts = localStorage.getItem('project_drafts');
    console.log('📚 Saved drafts raw:', savedDrafts);
    
    if (savedDrafts) {
      try {
        const drafts = JSON.parse(savedDrafts);
        console.log('📋 Parsed drafts:', drafts);
        
        if (drafts.length > 0) {
          // Sort by createdAt and get the latest
          const sortedDrafts = drafts.sort((a: any, b: any) => 
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
          );
          const latestDraft = sortedDrafts[0];
          console.log('📑 Latest draft:', latestDraft);
          
          setSelectedDraftId(latestDraft.id);
          setResumeDraft(false);
          console.log('📝 Setting appState to posting for resume');
          setAppState('posting');
        } else {
          console.log('📭 No drafts found, starting new project');
          handleStartNewProject();
        }
      } catch (error) {
        console.error('❌ Error loading latest draft:', error);
        handleStartNewProject();
      }
    } else {
      console.log('📭 No saved drafts, starting new project');
      handleStartNewProject();
    }
  };

  const handleStartNewProject = () => {
    console.log('✨ handleStartNewProject called!');
    console.log('🔍 Before state change - resumeDraft:', resumeDraft, 'selectedDraftId:', selectedDraftId);
    setResumeDraft(false);
    setSelectedDraftId(undefined);
    console.log('📝 Setting appState to posting');
    setAppState('posting');
    console.log('✅ State change completed');
  };

  const handleBackFromPosting = () => {
    setAppState('main');
    setResumeDraft(false);
    setSelectedDraftId(undefined);
  };

  const handleBackFromDrafts = () => {
    setAppState('main');
  };

  const handleOpenDrafts = () => {
    setAppState('drafts');
  };

  const handleEditDraft = (draftId: string) => {
    setSelectedDraftId(draftId);
    setResumeDraft(false);
    setAppState('posting');
  };

  // 新增：聊天功能相关处理函数
  const handleChatSelect = (chatId: number) => {
    setSelectedChatId(chatId);
    setAppState('chat-detail');
  };

  const handleBackToChat = () => {
    setSelectedChatId(null);
    setAppState('chat');
  };

  const exportTopCardAsImage = async () => {
    try {
      const node = topCardElementRef.current || topCardWrapperRef.current;
      if (!node) return;
      // preserve original inline styles
      const origBorderRadius = (node as HTMLElement).style.borderRadius;
      const origOverflow = (node as HTMLElement).style.overflow;
      const origBackground = (node as HTMLElement).style.background;
      const origClipPath = (node as HTMLElement).style.clipPath;
      // enforce rounded clipping and transparent background during export
      (node as HTMLElement).style.borderRadius = '14px';
      (node as HTMLElement).style.overflow = 'hidden';
      (node as HTMLElement).style.background = 'transparent';
      (node as HTMLElement).style.clipPath = 'inset(0 round 14px)';
      (node as HTMLElement).setAttribute('data-card-export', 'true');
      const styleEl = document.createElement('style');
      styleEl.setAttribute('data-card-export-style', 'true');
      styleEl.textContent = `
        [data-card-export="true"] { background: transparent !important; }
        [data-card-export="true"]::before, [data-card-export="true"]::after { display: none !important; }
      `;
      node.appendChild(styleEl);
      // Ensure export ignores the outer scaling; we export the card node directly
      const dataUrl = await toPng(node, {
        cacheBust: true,
        pixelRatio: window.devicePixelRatio || 2,
        skipFonts: false,
        style: {
          // Ensure background is captured fully
          background: 'transparent'
        }
      });
      const link = document.createElement('a');
      link.download = `card-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
      // restore styles
      const s = (node as HTMLElement).querySelector('style[data-card-export-style="true"]');
      if (s) s.remove();
      (node as HTMLElement).style.borderRadius = origBorderRadius;
      (node as HTMLElement).style.overflow = origOverflow;
      (node as HTMLElement).style.background = origBackground;
      (node as HTMLElement).style.clipPath = origClipPath;
      (node as HTMLElement).removeAttribute('data-card-export');
    } catch (err) {
      console.error('Failed to export image', err);
    }
  };

  const exportFullPageAsImage = async () => {
    try {
      const node = (containerRef.current?.querySelector('[data-screen-root="true"]') as HTMLElement)
        || (containerRef.current?.querySelector('div.w-\[393px\].h-\[852px\]') as HTMLElement);
      if (!node) return;
      // Temporarily mark export scope
      node.setAttribute('data-page-export', 'true');
      const styleEl = document.createElement('style');
      styleEl.setAttribute('data-page-export-style', 'true');
      styleEl.textContent = `
        [data-page-export=\"true\"] { width: 393px !important; height: 822px !important; overflow: visible !important; background: #ffffff !important; }
        [data-page-export=\"true\"] * { scrollbar-width: none; -ms-overflow-style: none; }
        [data-page-export=\"true\"]::-webkit-scrollbar { display: none; width: 0; height: 0; }
        [data-page-export=\"true\"] *::-webkit-scrollbar { display: none; width: 0; height: 0; }
      `;
      node.appendChild(styleEl);
      // wait 2 frames to stabilize layout before capture
      await new Promise(requestAnimationFrame);
      await new Promise(requestAnimationFrame);
      const dataUrl = await toPng(node, {
        cacheBust: true,
        pixelRatio: window.devicePixelRatio || 2,
        skipFonts: false,
        style: { background: '#ffffff' },
        filter: (n: any) => {
          if (n instanceof HTMLElement) {
            if (n.dataset && n.dataset.exportIgnore === 'true') return false;
          }
          return true;
        }
      });
      const link = document.createElement('a');
      link.download = `screen-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
      // cleanup
      node.removeAttribute('data-page-export');
      const s = node.querySelector('style[data-page-export-style="true"]');
      if (s) s.remove();
    } catch (e) {
      console.error('Export full page failed', e);
    }
  };

  const exportProfilePageAsImage = async () => {
    try {
      const screenNode = (containerRef.current?.querySelector('[data-screen-root="true"]') as HTMLElement);
      const scrollEl = profileScrollRef.current as HTMLElement | null;
      if (!screenNode) return;
      // if no dedicated scroll ref, fallback to full page export
      if (!scrollEl) { await exportFullPageAsImage(); return; }
      // store originals
      const origScreenH = screenNode.style.height;
      const origScreenOverflow = screenNode.style.overflow;
      const origScreenW = screenNode.style.width;
      const origScrollH = scrollEl.style.height;
      const origScrollOverflow = scrollEl.style.overflow;
      const origScrollW = scrollEl.style.width;
      // measure
      const headerH = 0; // profile page area already excludes outer header area in our layout
      const contentH = scrollEl.scrollHeight;
      const totalH = headerH + contentH;
      // expand
      screenNode.style.height = `${totalH}px`;
      screenNode.style.overflow = 'visible';
      screenNode.style.width = '393px';
      scrollEl.style.height = `${contentH}px`;
      scrollEl.style.overflow = 'visible';
      scrollEl.style.width = '393px';
      // mark export
      screenNode.setAttribute('data-page-export', 'true');
      const styleEl = document.createElement('style');
      styleEl.setAttribute('data-page-export-style', 'true');
      styleEl.textContent = `
        [data-page-export="true"] { width: 393px !important; overflow: visible !important; background: #ffffff !important; }
        [data-page-export="true"] * { scrollbar-width: none; -ms-overflow-style: none; }
        [data-page-export="true"]::-webkit-scrollbar { display: none; width: 0; height: 0; }
        [data-page-export="true"] *::-webkit-scrollbar { display: none; width: 0; height: 0; }
      `;
      screenNode.appendChild(styleEl);
      await new Promise(requestAnimationFrame);
      await new Promise(requestAnimationFrame);
      const dataUrl = await toPng(screenNode, {
        cacheBust: true,
        pixelRatio: window.devicePixelRatio || 2,
        skipFonts: false,
        style: { background: '#ffffff' },
        filter: (n: any) => {
          if (n instanceof HTMLElement) {
            if (n.dataset && n.dataset.exportIgnore === 'true') return false;
          }
          return true;
        }
      });
      const link = document.createElement('a');
      link.download = `profile-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
      // restore
      screenNode.style.height = origScreenH;
      screenNode.style.overflow = origScreenOverflow;
      screenNode.style.width = origScreenW;
      scrollEl.style.height = origScrollH;
      scrollEl.style.overflow = origScrollOverflow;
      scrollEl.style.width = origScrollW;
      screenNode.removeAttribute('data-page-export');
      const s = screenNode.querySelector('style[data-page-export-style="true"]');
      if (s) s.remove();
    } catch (e) {
      console.error('Export profile full content failed', e);
    }
  };

  return (
    <div ref={containerRef} className={`w-full h-[100dvh] bg-white relative overflow-hidden`}>
      <div
        style={{
          position: 'absolute',
          left: appState === 'auth' ? 0 : offset.left,
          top: appState === 'auth' ? 0 : offset.top,
          width: appState === 'auth' ? '100vw' : BASE_WIDTH,
          height: appState === 'auth' ? '100vh' : BASE_HEIGHT,
          transform: appState === 'auth' ? 'none' : `scale(${scale})`,
           transformOrigin: appState === 'auth' ? undefined as any : 'top left',
        }}
      >
                 <div data-screen-root="true" className={`w-[393px] h-[822px] ${appState === 'auth' ? 'bg-transparent' : 'bg-white'} relative overflow-hidden mx-auto`} style={{ touchAction: appState === 'auth' ? 'manipulation' : undefined }}>
          <style>{`::-webkit-scrollbar{display:none;width:0;height:0;} *{scrollbar-width:none; -ms-overflow-style:none;}`} </style>
          {/* 新增：应用状态切换逻辑 */}
          <AnimatePresence initial={true}>

            {appState === 'launch' && (
              <motion.div
                key="launch"
                className="absolute inset-0"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0.6, x: -40 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              >
                <LaunchingPage />
              </motion.div>
            )}
            {appState === 'auth' && (
              <motion.div
                key="auth"
                className="absolute inset-0"
                initial={false}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -40 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              >
                <div className="absolute inset-0">
                  <BackgroundGradientAnimation
                    gradientBackgroundStart="rgb(30, 144, 255)"  
                    gradientBackgroundEnd="rgb(0, 200, 150)"    
                    firstColor="30, 144, 255"                   
                    secondColor="30, 200, 177"                  
                    thirdColor="0, 200, 150"                    
                    size="85%"
                    blendingValue="soft-light"
                    containerClassName={appState === 'auth' ? 'w-full h-screen' : 'w-[393px] h-[822px] mx-auto'}
                  >
                    <div className="relative w-[393px] h-[822px] mx-auto">
                      <AuthPhoneScreen
                        smsData={smsData}
                        onChangePhone={(v) => {
                          setSmsData((prev) => ({ ...prev, phoneNumber: v }));
                          if (errors.phoneNumber) setErrors((prev) => ({ ...prev, phoneNumber: undefined }));
                        }}
                        onChangeCode={(v) => {
                          setSmsData((prev) => ({ ...prev, verificationCode: v }));
                          if (errors.verificationCode) setErrors((prev) => ({ ...prev, verificationCode: undefined }));
                        }}
                        errors={errors}
                        isLoading={isLoading}
                        codeSent={codeSent}
                        onSendSMS={handleSendSMS}
                        onVerifyCode={handleVerifyCode}
                      />
                    </div>
                  </BackgroundGradientAnimation>
                </div>
              </motion.div>
            )}
            
            {(appState === 'main' || appState === 'ai' || appState === 'chat' || appState === 'chat-detail' || appState === 'profile') && (
              <motion.div
                key="main"
                className="absolute inset-0"
                initial={{ opacity: 0, x: -40 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 1 }}
                transition={{ duration: 0.2, ease: 'linear' }}
              >
                <>
               {/* 添加滑块样式 */}
               <style dangerouslySetInnerHTML={{ __html: sliderStyles }} />
               {/* Header - 全局 */}
               <div>
                 <HeaderBar
                   rightContent={(
                     (appState === 'chat' || appState === 'chat-detail') ? (
                       // 聊天相关页面的按钮
                       <>
                         <IconButton onClick={handleNavigateToNotification}>
                           <div className="w-6 h-6">
                             <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                               <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" stroke="#000000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                             </svg>
                           </div>
                         </IconButton>
                         <IconButton onClick={handleNavigateToSettings}>
                           <Settings className="w-6 h-6 text-black" />
                         </IconButton>
                       </>
                     ) : (
                       // 主页面和AI页面的按钮
                       appState === 'main' ? (
                         <>
                           <IconButton onClick={toggleHistoryMode}>
                             <div className="w-6 h-6">
                               <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                                 <path d={svgPaths.history} fill={isHistoryMode ? "#0055f7" : "black"} />
                               </svg>
                             </div>
                           </IconButton>
                           <IconButton onClick={toggleFavoritesMode}>
                             <div className="w-6 h-6">
                               <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                                 <path d={svgPaths.like} fill={isFavoritesMode ? "#0055f7" : "none"} stroke={isFavoritesMode ? "#0055f7" : "#000000"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                               </svg>
                             </div>
                           </IconButton>
                           <IconButton onClick={() => setShowFilter(true)}>
                             <div className="w-6 h-6">
                               <svg className="block size-full" fill="none" viewBox="0 0 25 24">
                                 <path d={svgPaths.filter} stroke={showFilter ? "#0088ff" : "#000000"} strokeWidth="2" strokeMiterlimit="10" strokeLinecap="round" />
                               </svg>
                             </div>
                           </IconButton>
                         </>
                                             ) : appState === 'profile' ? (
                        <>
                          <IconButton onClick={() => setAppState('profile-settings')}>
                            <Settings className="w-6 h-6 text-black" />
                          </IconButton>
                        </>
                      ) : (
                        // AI页面的按钮  
                        <>
                          <IconButton onClick={() => setShowFilter(true)}>
                             <div className="w-6 h-6">
                               <svg className="block size-full" fill="none" viewBox="0 0 25 24">
                                 <path d={svgPaths.filter} stroke={showFilter ? "#0088ff" : "#000000"} strokeWidth="2" strokeMiterlimit="10" strokeLinecap="round" />
                               </svg>
                             </div>
                           </IconButton>
                        </>
                      )
                     )
                   )}
                 />
               </div>
               {appState === 'main' ? (
               <>

           {/* Main Content - Card Stack */}
                     <div className="relative h-[540px] flex items-center justify-center px-4 mt-8">
            <div className="relative w-[357px] h-[560px]">
               {isHistoryMode ? (
                 // History Mode - Single card with navigation
                 leftSwipedProjects.length > 0 && currentProject ? (
                   <div 
                     className="relative w-full h-full"
                     onWheel={(e) => {
                       e.preventDefault();
                       if (e.deltaY > 0 && historyIndex < leftSwipedProjects.length - 1) {
                         handleHistorySlide('right');
                       } else if (e.deltaY < 0 && historyIndex > 0) {
                         handleHistorySlide('left');
                       }
                     }}
                   >
                     <ProjectCard
                       key={`history-${currentProject.id}-${historyIndex}`}
                       project={currentProject}
                       index={0}
                       onSwipe={(dir) => handleHistorySlide(dir)}
                       isTop={true}
                       onClick={() => setSelectedProject(currentProject)}
                       isHistory={true}
                     />
                     
                                         {/* Navigation Controls */}
                    {!selectedProject && (
                      <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 flex gap-4 z-[999]">
                        <motion.button
                          onClick={() => handleHistorySlide('left')}
                          disabled={historyIndex === 0}
                          className="w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white disabled:opacity-30 transition-all duration-200"
                           whileHover={{ scale: 1.1 }}
                           whileTap={{ scale: 0.95 }}
                         >
                           <ArrowLeft size={20} />
                         </motion.button>
                                                 <div className="inline-flex items-center px-4 py-2 bg-black/50 backdrop-blur-sm rounded-full text-white text-sm font-medium whitespace-nowrap">
                          {historyIndex + 1} / {leftSwipedProjects.length}
                        </div>
                         <motion.button
                           onClick={() => handleHistorySlide('right')}
                           disabled={historyIndex === leftSwipedProjects.length - 1}
                           className="w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white disabled:opacity-30 transition-all duration-200"
                           whileHover={{ scale: 1.1 }}
                           whileTap={{ scale: 0.95 }}
                         >
                           <ArrowLeft size={20} className="rotate-180" />
                         </motion.button>
                       </div>
                     )}
                   </div>
                 ) : (
                   <div className="w-full h-full flex items-center justify-center">
                     <div className="text-center">
                       <div className="w-16 h-16 mx-auto mb-4">
                         <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                           <path d={svgPaths.history} fill="#9ca3af" />
                         </svg>
                       </div>
                       <h3 className="text-xl font-medium text-gray-700 mb-2">{t('noHistoryTitle')}</h3>
                       <p className="text-gray-500">{t('noHistorySubtitle')}</p>
                     </div>
                   </div>
                 )
               ) : isFavoritesMode ? (
                 // Favorites Mode - Single card with navigation
                 favorites.length > 0 && currentFavorite ? (
                   <div 
                     className="relative w-full h-full"
                     onWheel={(e) => {
                       e.preventDefault();
                       if (e.deltaY > 0 && favoritesIndex < favorites.length - 1) {
                         handleFavoriteSlide('right');
                       } else if (e.deltaY < 0 && favoritesIndex > 0) {
                         handleFavoriteSlide('left');
                       }
                     }}
                   >
                     <ProjectCard
                       key={`fav-${currentFavorite.id}-${favoritesIndex}`}
                       project={currentFavorite}
                       index={0}
                       onSwipe={(dir) => handleFavoriteSlide(dir)}
                       isTop={true}
                       onClick={() => setSelectedProject(currentFavorite)}
                       isHistory={true}
                     />
                     
                     {/* Navigation Controls */}
                     {!selectedProject && (
                       <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 flex gap-4 z-[999]">
                         <motion.button
                           onClick={() => handleFavoriteSlide('left')}
                           disabled={favoritesIndex === 0}
                           className="w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white disabled:opacity-30 transition-all duration-200"
                           whileHover={{ scale: 1.1 }}
                           whileTap={{ scale: 0.95 }}
                         >
                           <ArrowLeft size={20} />
                         </motion.button>
                         <div className="inline-flex items-center px-4 py-2 bg-black/50 backdrop-blur-sm rounded-full text-white text-sm font-medium whitespace-nowrap">
                           {favoritesIndex + 1} / {favorites.length}
                         </div>
                         <motion.button
                           onClick={() => handleFavoriteSlide('right')}
                           disabled={favoritesIndex === favorites.length - 1}
                           className="w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white disabled:opacity-30 transition-all duration-200"
                           whileHover={{ scale: 1.1 }}
                           whileTap={{ scale: 0.95 }}
                         >
                           <ArrowLeft size={20} className="rotate-180" />
                         </motion.button>
                       </div>
                     )}
                   </div>
                 ) : (
                   <div className="w-full h-full flex items-center justify-center">
                     <div className="text-center">
                       <div className="w-16 h-16 mx-auto mb-4">
                         <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                           <path d={svgPaths.like} fill="#9ca3af" />
                         </svg>
                       </div>
                       <h3 className="text-xl font-medium text-gray-700 mb-2">{t('noFavoritesTitle')}</h3>
                       <p className="text-gray-500">{t('noFavoritesSubtitle')}</p>
                     </div>
                   </div>
                 )
               ) : (
                 // Normal Mode - Card stack（顶卡可滑动 + 下一张预备卡静态展示）
                 <>
                   {displayProjects.slice(0, 2).map((proj, i) => {
                     const isTopCard = i === 0;
                     return (
                       <motion.div
                         key={proj.id}
                         className={`absolute inset-0 ${!isTopCard ? 'pointer-events-none' : ''}`}
                         style={{ zIndex: isTopCard ? 2 : 1 }}
                         initial={false}
                         animate={isTopCard ? { scale: 1, y: 0 } : { scale: 0.94, y: 14 }}
                         transition={isTopCard ? { type: 'spring', stiffness: 260, damping: 26 } : { layout: { type: 'spring', stiffness: 180, damping: 24 } }}
                         layoutId={`card-${proj.id}`}
                         ref={isTopCard ? topCardWrapperRef : undefined as any}
                       >
                         <ProjectCard
                           project={proj}
                           index={i}
                           onSwipe={isTopCard ? handleSwipe : () => {}}
                           isTop={isTopCard}
                           onClick={isTopCard ? () => setSelectedProject(proj) : () => {}}
                           isHistory={!isTopCard}
                           captureRef={isTopCard ? topCardElementRef : undefined}
                         />
                       </motion.div>
                     );
                   })}
                  </>
               )}
               
               {!isHistoryMode && displayProjects.length === 0 && (
                 <motion.div
                   className="w-full h-full flex items-center justify-center"
                   initial={{ opacity: 0 }}
                   animate={{ opacity: 1 }}
                 >
                   <div className="text-center">
                     <Star className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                     <h3 className="text-xl font-medium text-gray-700 mb-2">{t('noMoreProjectsTitle')}</h3>
                     <p className="text-gray-500">{t('noMoreProjectsSubtitle')}</p>
                   </div>
                 </motion.div>
               )}
             </div>
             
             {/* 简单右滑动画 - 在主内容区域内 */}
             <AnimatePresence>
               {showSwipeAnimation && (
                 <div className="absolute inset-0 pointer-events-none z-50 flex items-center justify-end pr-4">
                   <SwipeAnimation />
                 </div>
               )}
             </AnimatePresence>
           </div>

           </>
           ) : appState === 'ai' ? (
             <AISearchIntegrated
               onBackToMain={() => setAppState('main')}
               onOpenFilter={() => setShowFilter(true)}
               onOpenProject={(p) => setSelectedProject(p)}
               onRecordLeftSwipe={(p) => setLeftSwipedProjects(prev => [p, ...prev])}
               onRecordRightSwipe={(p) => setFavorites(prev => (prev.find(x => x.id === p.id) ? prev : [p, ...prev]))}
               suppressMatchIndicator={suppressMatchIndicator}
             />
           ) : appState === 'chat' ? (
             <div className="h-[662px]">
               <ChatHome
                 onNavigateToNotification={handleNavigateToNotification}
                 onNavigateToSettings={handleNavigateToSettings}
                 onChatSelect={handleChatSelect}
               />
             </div>
           ) : appState === 'chat-detail' ? (
             <div className="h-[662px]">
               <ChatChatPage
                 onNavigateBack={handleBackToChat}
               />
             </div>
           ) : appState === 'profile' ? (
             <div className="h-[662px] overflow-y-auto" ref={profileScrollRef}>
               <ProfilePage 
                 onBack={() => setAppState('main')} 
                 onEditProject={(project) => {
                   // 跳转到项目编辑页面
                   console.log('跳转到编辑页面:', project.title);
                   setAppState('posting');
                   // 这里可以传递项目数据到编辑页面
                 }}
               />
             </div>
           ) : null}



           {/* Filter Sidebar */}
           <FilterSidebar 
             isOpen={showFilter} 
             onClose={() => setShowFilter(false)}
             filters={filters}
             setFilters={setFilters}
             suppressMatchIndicator={suppressMatchIndicator}
             onToggleMatchIndicator={toggleMatchIndicator}
           />

           {/* Project Detail View */}
           <AnimatePresence>
             {selectedProject && (
               <ProjectDetailView
                 project={selectedProject}
                 onClose={() => setSelectedProject(null)}
                 suppressFirstTap={true}
                 isFavorite={!!favorites.find(p => p.id === selectedProject.id)}
                 onLikeChange={(proj, liked) => {
                   setFavorites(prev => {
                     const exists = prev.find(p => p.id === proj.id);
                     if (liked) {
                       return exists ? prev : [proj, ...prev];
                     }
                     return prev.filter(p => p.id !== proj.id);
                   });
                 }}
               />
             )}
           </AnimatePresence>
                 </>
               </motion.div>
             )}

            {appState === 'posting' && (
              <motion.div
                key="posting"
                className="absolute inset-0"
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 1 }}
                transition={{ duration: 0.2, ease: 'linear' }}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  zIndex: 100
                }}
              >
                {(() => {
                  console.log('📄 Rendering PostingProjectPage container');
                  return null;
                })()}
                
                                <PostingProjectPage
                  onBack={handleBackFromPosting}
                  resumeDraft={resumeDraft}
                  draftId={selectedDraftId}
                  onPublished={(newProject?: any) => {
                    console.log('✅ Project published successfully');
                    try {
                      const raw = localStorage.getItem('profile_new_projects');
                      const arr = raw ? JSON.parse(raw) : [];
                      const next = Array.isArray(arr) ? [newProject, ...arr] : [newProject];
                      localStorage.setItem('profile_new_projects', JSON.stringify(next));
                    } catch (e) {
                      console.error('Failed to queue new project for profile sync', e);
                      try { localStorage.setItem('profile_new_projects', JSON.stringify([newProject])); } catch {}
                    }
                    setShowSuccess(true);
                    setTimeout(() => {
                      setShowSuccess(false);
                      setAppState('main');
                    }, 2000);
                  }}
                  onPublishError={(error) => {
                    console.error('❌ Project publish error:', error);
                    setShowPublishError(typeof error === 'string' ? error : (i18nCurrentLanguage === 'en' ? 'Publish failed, please try again' : '发布失败，请重试'));
                  }}
                />
              </motion.div>
            )}

            {appState === 'drafts' && (
              <motion.div
                key="drafts"
                className="absolute inset-0"
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 1 }}
                transition={{ duration: 0.2, ease: 'linear' }}
              >
                <DraftsPage
                  onBack={handleBackFromDrafts}
                  onEditDraft={handleEditDraft}
                />
              </motion.div>
            )}

            {appState === 'notification' && (
              <motion.div
                key="notification"
                className="absolute inset-0"
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 1 }}
                transition={{ duration: 0.2, ease: 'linear' }}
              >
                <ChatNotification onNavigateBack={() => setAppState('chat')} />
              </motion.div>
            )}

            {appState === 'settings' && (
              <motion.div
                key="settings"
                className="absolute inset-0"
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 1 }}
                transition={{ duration: 0.2, ease: 'linear' }}
              >
                <ChatSettings onNavigateBack={() => setAppState('chat')} />
              </motion.div>
            )}

                        

           </AnimatePresence>



          {/* 全局悬浮导出按钮（主页面、AI搜索、编辑页显示） */}
                    {ENABLE_EXPORT && (appState === 'main' || appState === 'ai' || appState === 'posting' || appState === 'chat' || appState === 'chat-detail' || appState === 'profile') && (
             <div className="absolute top-4 right-4 z-[2000] pointer-events-auto" data-export-ignore="true">
               <IconButton onClick={() => (appState==='profile' ? exportProfilePageAsImage() : exportFullPageAsImage())} className="bg-white/80 hover:bg-white shadow-md">
                 <div className="w-6 h-6">
                   <svg className="block size-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                     <path d="M9 3l-1.5 2H5a2 2 0 00-2 2v10a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2h-2.5L15 3H9z" stroke="#000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                     <circle cx="12" cy="12" r="3.5" stroke="#000" strokeWidth="2"/>
                   </svg>
                 </div>
               </IconButton>
             </div>
           )}

          {/* Bottom Navigation - 在主页面、AI页面、聊天页面、通知页面、设置页面和个人页面显示 */}
          {(appState === 'main' || appState === 'ai' || appState === 'chat' || appState === 'chat-detail' || appState === 'notification' || appState === 'settings' || appState === 'profile') && (
            <motion.div 
              className="absolute bottom-0 left-0 right-0 bg-neutral-50 h-[100px] border-t border-[#e8edf2] z-40"
              initial={{ y: 126 }}
              animate={{ y: 0 }}
              transition={{ duration: 0.0 }}
            >
              <div className="h-full relative">
                {/* Navigation Icons */}
                <div className="absolute left-[13px] top-[25px] flex gap-[105px]">
                  <div className="flex gap-0">
                    <IconButton className="w-[65.2px]" onClick={() => setAppState('main')}>
                      <div className="w-6 h-6">
                        <svg className="block size-full" fill="none" viewBox="0 0 18 19">
                           <path d={svgPaths.p11f24e80} fill={appState === 'main' ? '#0055F7' : '#616C78'} />
                        </svg>
                      </div>
                    </IconButton>
                    <IconButton className="w-[65.2px]" onClick={() => setAppState('ai')}>
                      <div className="w-6 h-6">
                        <svg className="block size-full" fill="none" viewBox="0 0 21 21">
                           <path d={svgPaths.p11caffd0} fill={appState === 'ai' ? '#0055F7' : '#616C78'} />
                        </svg>
                      </div>
                    </IconButton>
                  </div>
                  <div className="flex gap-0">
                    <IconButton className="w-[65.2px]" onClick={() => setAppState('chat')}>
                      <div className="w-6 h-6">
                        <svg className="block size-full" fill="none" viewBox="0 0 20 20">
                          <path d={svgPaths.p19a90780} fill={appState === 'chat' || appState === 'chat-detail' || appState === 'notification' || appState === 'settings' ? '#0055F7' : '#616C78'} />
                        </svg>
                      </div>
                    </IconButton>
                    <IconButton className="w-[65.2px]" onClick={() => setAppState('profile')}>
                      <div className="w-6 h-6">
                        <svg className="block size-full" fill="none" viewBox="0 0 20 20">
                          <path d={svgPaths.p3d54cd00} fill={appState === 'profile' ? '#0055F7' : '#616C78'} />
                        </svg>
                      </div>
                    </IconButton>
                  </div>
                </div>

                {/* Center Plus Button */}
                <motion.button
                  className="absolute left-[170px] top-[16px] w-[53px] h-[53px] bg-[#0055f7] rounded-full flex items-center justify-center shadow-lg"
                  whileHover={{ scale: 1.1, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  animate={{ rotate: [0, 180, 360] }}
                  transition={{ 
                    rotate: { duration: 4, repeat: Infinity, ease: "linear" },
                    scale: { duration: 0.2 },
                    y: { duration: 0.2 }
                  }}
                  onClick={handlePostNewProjectClick}
                >
                  <div className="w-6 h-6">
                  <svg className="block size-full" fill="none" viewBox="0 0 23 23">
                    <path d={svgPaths.p3b63e500} fill="white" stroke="white" />
                  </svg>
                </div>
                </motion.button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
            {/* 匹配指示弹窗 */}
          <AnimatePresence>
        {showMatchIndicator && lastLikedProject && (
          <MatchIndicator
            project={lastLikedProject}
            onClose={() => {
              setShowMatchIndicator(false);
              setLastLikedProject(null);
            }}
            onSuppress={() => {
              setSuppressMatchIndicator(true);
              setShowMatchIndicator(false);
              setLastLikedProject(null);
              console.log('Suppressing match indicator for current session only');
            }}
          />
        )}
      </AnimatePresence>

      {/* 发布成功弹窗 */}
      <AnimatePresence>
        {showSuccess && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowSuccess(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 w-[320px] text-center shadow-2xl"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
            >
              <motion.div
                className="mx-auto mb-3 w-14 h-14 rounded-full bg-[#0055F7] flex items-center justify-center text-white"
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.15, 1] }}
                transition={{ duration: 0.35 }}
              >
                <Check size={28} />
              </motion.div>
              <h3 className="text-xl font-bold mb-1">{i18nCurrentLanguage === 'en' ? 'Published Successfully' : '发布成功'}</h3>
              <p className="text-sm text-gray-600 mb-4">{i18nCurrentLanguage === 'en' ? 'Your project has been published. Good luck with your matches!' : '你的项目已发布。祝你匹配顺利！'}</p>
              <Button onClick={() => setShowSuccess(false)} className="w-full">{i18nCurrentLanguage === 'en' ? 'OK' : '好的'}</Button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 发布失败弹窗 */}
      <AnimatePresence>
        {showPublishError && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowPublishError(null)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 w-[320px] text-center shadow-2xl"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
            >
              <motion.div
                className="mx-auto mb-3 w-14 h-14 rounded-full bg-error-500 flex items-center justify-center text-white"
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.15, 1] }}
                transition={{ duration: 0.35 }}
              >
                <X size={28} />
              </motion.div>
              <h3 className="text-xl font-bold mb-1">{i18nCurrentLanguage === 'en' ? 'Publish Failed' : '发布失败'}</h3>
              <p className="text-sm text-gray-600 mb-4">{showPublishError}</p>
              <Button onClick={() => setShowPublishError(null)} className="w-full">{i18nCurrentLanguage === 'en' ? 'Got it' : '我知道了'}</Button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Resume Dialog - 在最外层，不受缩放影响 */}
      {appState === 'resume' && (
        <div
          className="fixed inset-0 w-full h-full flex items-center justify-center bg-black/50 z-[9999]"
          style={{ 
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 9999,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex'
          }}
        >
          {(() => {
            console.log('🔄 Rendering DraftResumeDialog in OUTERMOST container');
            console.log('🎨 Dialog should be visible with normal backdrop');
            return null;
          })()}
          <div 
            className="bg-white rounded-2xl p-6 w-[360px] max-w-[360px] shadow-2xl relative z-[10000]"
            style={{ 
              backgroundColor: '#ffffff',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              zIndex: 10000,
              maxWidth: '360px',
              width: '360px'
            }}
          >
            <div className="mb-4">
              <h2 className="text-xl font-semibold mb-2 text-gray-900">{(i18nCurrentLanguage === 'en') ? 'Resume last draft?' : '继续上次草稿？'}</h2>
              <p className="text-sm text-gray-600">
                {(i18nCurrentLanguage === 'en') ? 'A saved draft was found from your previous session. Continue editing the latest draft or start a new project?' : '检测到你在之前的会话中保存了草稿。现在要继续编辑最近的草稿，还是开始一个新项目？'}
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Button 
                onClick={() => {
                  console.log('📝 Resume draft requested');
                  handleResumeLatestDraft();
                }} 
                className="w-full h-11 text-base bg-blue-600 hover:bg-blue-700 text-white"
                style={{
                  backgroundColor: '#2563eb',
                  color: '#ffffff',
                  height: '44px',
                  width: '100%'
                }}
              >
                {(i18nCurrentLanguage === 'en') ? 'Resume latest draft' : '继续最近草稿'}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  console.log('🆕 Start new project requested');
                  handleStartNewProject();
                }} 
                className="w-full h-11 text-base border-gray-300 text-gray-700 hover:bg-gray-50"
                style={{
                  borderColor: '#d1d5db',
                  color: '#374151',
                  height: '44px',
                  width: '100%',
                  backgroundColor: '#ffffff',
                  border: '1px solid #d1d5db'
                }}
              >
                {(i18nCurrentLanguage === 'en') ? 'Start new project' : '开始新项目'}
              </Button>
            </div>
          </div>
        </div>
      )}



      {appState === 'profile-settings' && (
        <motion.div
          key="profile-settings"
          className="absolute inset-0"
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 40, scale: 1 }}
          transition={{ duration: 0.2, ease: 'linear' }}
        >
          <SettingsPage 
            onBack={() => setAppState('profile')}
            onOpenTerms={() => setAppState('terms')}
            onOpenSupport={() => setAppState('support')}
            onFeedbackSubmit={(text: string) => { if (text) console.log('用户反馈:', text); }}
            onLogout={() => { try { localStorage.removeItem('access_token'); } catch{} setAppState('auth'); }}
            onDeactivate={() => { if (window.confirm('确定要注销账号吗？此操作不可恢复。')) { try { localStorage.clear(); } catch{} setAppState('auth'); } }}
          />
        </motion.div>
      )}

      {appState === 'support' && (
        <motion.div
          key="support"
          className="absolute inset-0"
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 40, scale: 1 }}
          transition={{ duration: 0.2, ease: 'linear' }}
        >
          <SupportPage onBack={() => setAppState('profile-settings')} />
        </motion.div>
      )}

      {appState === 'terms' && (
        <motion.div
          key="terms"
          className="absolute inset-0"
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 40, scale: 1 }}
          transition={{ duration: 0.2, ease: 'linear' }}
        >
          <TermsPage onBack={() => setAppState('profile-settings')} />
        </motion.div>
      )}

    </div>
  );
}