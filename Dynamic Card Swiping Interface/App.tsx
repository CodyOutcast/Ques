import { useState, useRef, useEffect } from 'react';
import { motion, PanInfo, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { Star, ChevronDown, MapPin, Calendar, Users, Target, ExternalLink, ArrowLeft, Check, Play, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { ImageWithFallback } from './components/figma/ImageWithFallback';
import { Badge } from './components/ui/badge';
import svgPaths from "./imports/svg-fko3i96u3r";
import { t } from './translations';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import { Checkbox } from './components/ui/checkbox';
import InteractivePopup from './Popup Frame Component/components/InteractivePopup';
import './styles/popup-custom.css';
import { createPortal } from 'react-dom';
import TinderCard from 'react-tinder-card';
import { AuthPhoneScreen } from './auth-components/AuthScreen';

// 新增：导入启动页面组件
import { LaunchingPage } from './Interactive Ques Sign-Up_Sign-In Prototype/components/LaunchingPage';

// 新增：认证相关接口
interface SMSData {
  phoneNumber: string;
  verificationCode: string;
}

// 新增：应用状态类型
type AppState = 'launch' | 'auth' | 'main';

// 可调滑动参数（集中配置）
export const SWIPE_REQUIREMENT: 'position' | 'velocity' = 'position';
export const SWIPE_THRESHOLD_PX: number = 100; // 位置阈值，像素越大越难滑走
export const TAP_MAX_MOVEMENT_PX: number = 8;  // 点击判定的最大移动距离
export const TAP_MAX_DURATION_MS: number = 220; // 点击判定的最大按下时长

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

interface Project {
  id: number;
  title: string;
  author: string;
  collaborators: number;
  background?: string;
  videoUrl?: string;
  description: string;
  tags: string[];
  type: 'project' | 'profile';
  cardStyle: 'image' | 'video' | 'text-only' | 'profile';
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

const projects: Project[] = [
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
      { name: "Sarah Kim", role: "Frontend Developer", avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face" },
      { name: "Mike Johnson", role: "AI Engineer", avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face" },
      { name: "Emma Davis", role: "Product Manager", avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face" }
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
      { name: "David Park", role: "Mobile Developer", avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face" },
      { name: "Lisa Zhang", role: "UX Designer", avatar: "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face" },
      { name: "Tom Brown", role: "Data Analyst", avatar: "https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=150&h=150&fit=crop&crop=face" },
      { name: "Maya Patel", role: "Backend Developer", avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face" },
      { name: "James Wilson", role: "Marketing", avatar: "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face" }
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
      { name: "Alex Thompson", role: "Smart Contract Developer", avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face" },
      { name: "Zoe Chen", role: "Frontend Developer", avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face" },
      { name: "Ryan Kim", role: "Backend Developer", avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face" },
      { name: "Sofia Rodriguez", role: "UI/UX Designer", avatar: "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face" }
    ],
    detailedDescription: "A comprehensive blockchain platform that bridges the gap between traditional applications and decentralized technology.",
    startTime: "February 2024",
    currentProgress: 45,
    content: "Developing smart contracts, user interfaces, and infrastructure for the next generation of decentralized applications.",
    purpose: "To make blockchain technology accessible and user-friendly for mainstream adoption.",
    lookingFor: ["Security Auditor", "Community Manager", "Business Development"],
    links: ["https://blockchain-project.com", "https://github.com/blockchain-solution"],
    media: []
  }
];

const projectTypes = ["AI", "Design", "Sustainability", "Mobile", "VR", "Education", "Blockchain", "Gaming", "Health", "Finance"];

interface FilterState {
  cardTypes: { project: boolean; profile: boolean };
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
  return (
    <div className="flex flex-row gap-[3px] items-center justify-center leading-[0] px-0 py-[13px] relative">
      <motion.div
        className="relative"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      >
        <p 
          className="block text-nowrap whitespace-pre"
          style={{
            color: 'var(--Accent-blue1, #0055F7)',
            fontFeatureSettings: "'liga' off, 'clig' off",
            fontFamily: '"Instrument Sans"',
            fontSize: '40px',
            fontStyle: 'italic',
            fontWeight: '700',
            lineHeight: '9px'
          }}
        >
          Ques
        </p>
      </motion.div>
      <div className="flex flex-col font-normal justify-center relative text-[#0088ff]">
        <ChevronDown size={18} className="text-[#0088ff]" />
      </div>
    </div>
  );
}

function IconButton({ children, onClick, className = "" }: { children: React.ReactNode, onClick?: () => void, className?: string }) {
  return (
    <motion.button
      className={`flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-full ${className}`}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
    >
      {children}
    </motion.button>
  );
}

function FilterSidebar({ isOpen, onClose, filters, setFilters }: {
  isOpen: boolean;
  onClose: () => void;
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
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
                <h1 className="text-2xl font-bold text-gray-900">筛选器</h1>
                <div className="text-gray-400 text-sm mt-2">添加筛选条件以找到完美的合作伙伴</div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
                {/* Distance Section */}
                <div>
                  <label className="block text-lg font-medium text-gray-800 mb-4">最大距离</label>
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
                        <span className="text-base text-gray-700 min-w-[120px]">与我在同一个城市</span>
                  <Checkbox
                          checked={filters.sameCity || false}
                          onCheckedChange={checked => setFilters({ ...filters, sameCity: !!checked })}
                          className="h-5 w-5 border-2 border-[#0055F7] bg-white data-[state=checked]:bg-white data-[state=checked]:border-[#0055F7] data-[state=checked]:text-[#0055F7]"
                        />
                      </label>
                      <label className="flex items-center justify-between">
                        <span className="text-base text-gray-700 min-w-[120px]">当我可看的卡片浏览完后向我显示超出距离的卡片</span>
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
                  <label className="block text-lg font-medium text-gray-800 mb-4">年龄</label>
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
                  <h3 className="text-lg font-medium text-gray-800 mb-4">项目状态</h3>
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
                      未开始
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
                      进行中
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
                      已完成
                    </button>
                  </div>
                </div>

                {/* Project Types Section */}
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-4">项目类型</h3>
                  {/* 搜索框 */}
                  <input
                    type="text"
                    placeholder="搜索类型..."
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
                        cardTypes: { project: true, profile: true },
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
                    重置
                  </button>
                  <button
                    onClick={onClose}
                    className="flex-1 py-4 bg-gradient-to-r from-[#0055F7] to-[#0043C4] text-white rounded-full font-semibold text-lg shadow-lg hover:from-[#0043C4] hover:to-[#0032A3] transition-all duration-300 transform hover:scale-105"
                  >
                    应用筛选
                  </button>
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

function ProjectCard({ project, index, onSwipe, isTop, onClick, isHistory = false }: { 
  project: Project, 
  index: number, 
  onSwipe: (direction: 'left' | 'right') => void,
  isTop: boolean,
  onClick: () => void,
  isHistory?: boolean
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
                      className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium"
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
                      className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium"
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
                      className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium"
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
      
      case 'profile':
        return (
          <>
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600" />
            <div className="absolute inset-0 bg-black/10" />
            {/* Profile pattern */}
            <div className="absolute inset-0 opacity-20">
              <svg className="w-full h-full" viewBox="0 0 400 600">
                <defs>
                  <pattern id="profile-pattern" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                    <circle cx="20" cy="20" r="2" fill="white" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#profile-pattern)" />
              </svg>
            </div>
            <div className="absolute inset-0 p-6 text-white flex flex-col items-center justify-center">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center"
              >
                <div className="mb-6">
                  <ImageWithFallback
                    src={project.owner.avatar}
                    alt={project.owner.name}
                    className="w-24 h-24 rounded-full object-cover mx-auto mb-4 border-4 border-white/30"
                  />
                </div>
                <h2 className="text-[32px] font-bold leading-[36px] mb-2">
                  {project.owner.name}
                </h2>
                <p className="text-white/90 text-sm mb-4 leading-5">
                  {project.description}
                </p>
                <div className="flex flex-wrap gap-2 justify-center mb-4">
                  {project.tags.slice(0, 3).map((tag, i) => (
                    <motion.span
                      key={tag}
                      className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      {tag}
                    </motion.span>
                  ))}
                </div>
                <div className="text-white/80 text-sm">
                  <span className="font-medium">{project.owner.role}</span>
                  <span className="mx-2">·</span>
                  <span>{project.owner.distance} {t('kmAway')}</span>
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

  const baseCardClass = `w-[357px] h-[670px] rounded-[14px] overflow-hidden relative cursor-pointer pressable`;
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

function ProjectDetailView({ project, onClose, suppressFirstTap = false }: { project: Project; onClose: () => void; suppressFirstTap?: boolean }) {
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showNavButtons, setShowNavButtons] = useState(false);
  const swiperRef = useRef<any>(null);
  const buttonTimerRef = useRef<number | null>(null);
  const [clickEnabled, setClickEnabled] = useState(!suppressFirstTap);
  // Like state and animation
  const [liked, setLiked] = useState(false);
  const [likeAnimate, setLikeAnimate] = useState(false);
  const handleLike = () => {
    setLiked(prev => !prev);
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
      <div className="w-full h-full flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <button onClick={onClose} className="p-2">
            <ArrowLeft size={24} className="text-blue-600" />
          </button>
          <h1 className="font-semibold">
            {project.type === 'profile' ? t('profileDetails') : t('projectDetails')}
          </h1>
          <div className="w-10" />
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="space-y-6">
            {/* Media Carousel */}
            <div 
              className="relative w-full h-96 bg-gray-100 rounded-lg overflow-hidden"
              onTouchStart={showButtons}
              onMouseEnter={() => setShowNavButtons(true)}
              onMouseLeave={() => setShowNavButtons(false)}
            >
            {project.media.length > 0 ? (
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
                        {url.endsWith('.mp4') || url.endsWith('.webm') || url.endsWith('.mov') ? (
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
                {project.cardStyle === 'profile' ? (
                  <div className="w-full h-full bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600 flex items-center justify-center">
                    <ImageWithFallback
                      src={project.owner.avatar}
                      alt={project.owner.name}
                      className="w-32 h-32 rounded-full object-cover border-4 border-white"
                    />
                  </div>
                ) : project.background ? (
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
                {project.type === 'profile' ? t('about') : t('projectOwner')}
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
                      <ImageWithFallback
                        src={collaborator.avatar}
                        alt={collaborator.name}
                        className="w-10 h-10 rounded-full object-cover"
                      />
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
                {project.type === 'profile' ? t('goals') : t('purpose')}
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
  const [smsData, setSmsData] = useState<SMSData>({
    phoneNumber: '',
    verificationCode: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ phoneNumber?: string; verificationCode?: string }>({});
  const [codeSent, setCodeSent] = useState(false);

  // 原有状态管理
  const [currentProjects, setCurrentProjects] = useState(projects);
  const [leftSwipedProjects, setLeftSwipedProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [showFilter, setShowFilter] = useState(false);
  const [isHistoryMode, setIsHistoryMode] = useState(false);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [filters, setFilters] = useState<FilterState>({
    cardTypes: { project: true, profile: true },
    projectStatus: { ongoing: true, finished: true, not_started: true },
    projectTypes: [],
    distance: [0, 50],
    gender: [],
    age: [18, 65],
    sameCity: false,
    showOutOfDistance: false,
    typeSearch: ''
  });

  // 新增：启动页面自动跳转逻辑
  useEffect(() => {
    if (appState === 'launch') {
      const timer = setTimeout(() => {
        setAppState('auth');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [appState]);

  // Responsive canvas scaling (base design size 393x852)
  const BASE_WIDTH = 393;
  const BASE_HEIGHT = 852;
  const containerRef = useRef<HTMLDivElement | null>(null);
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

  // 在App组件内添加弹窗控制状态
  const [showPopup, setShowPopup] = useState(false);
  const [pendingSwipe, setPendingSwipe] = useState<null | (() => void)>(null);
  // 是否抑制右滑弹窗（默认问候）
  const [suppressGreetingPopup, setSuppressGreetingPopup] = useState<boolean>(false);
  // 调试阶段：每次刷新都重置为可显示弹窗
  useEffect(() => {
    // 如果你需要持久化，请改为从 localStorage 读取并写入
    // try { setSuppressGreetingPopup(localStorage.getItem('suppressGreetingPopup') === '1'); } catch {}
  }, []);

  // 修改handleSwipe逻辑
  const handleSwipe = (direction: 'left' | 'right') => {
    if (direction === 'right') {
      if (suppressGreetingPopup) {
        // 直接移除顶部卡片，不展示弹窗
        setTimeout(() => {
          setCurrentProjects(prev => prev.slice(1));
        }, 600);
        return;
      }
      setShowPopup(true);
      setPendingSwipe(() => () => {
        setShowPopup(false);
        setCurrentProjects(prev => prev.slice(1));
      });
      return;
    }
    if (direction === 'left' && currentProjects.length > 0) {
      setLeftSwipedProjects(prev => [currentProjects[0], ...prev]);
    }
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
    setHistoryIndex(0);
  };

  const filteredProjects = currentProjects.filter(project => {
    // Card type filter
    if (!filters.cardTypes[project.type]) return false;
    // Project status filter
    if (project.type === 'project' && !filters.projectStatus[project.status as 'ongoing' | 'finished' | 'not_started']) return false;
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

  // 添加弹窗关闭处理函数
  const handlePopupClose = () => {
    setShowPopup(false);
    // 如果有待处理的滑动，立即执行
    if (pendingSwipe) {
      pendingSwipe();
      setPendingSwipe(null);
    }
  };

  const popupWidthPx = Math.round(Math.min(0.88 * BASE_WIDTH * scale, 360));

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

  const handleDefaultGreetingChange = (checked: boolean) => {
    setSuppressGreetingPopup(checked);
  };

  return (
    <div ref={containerRef} className="w-full h-screen bg-white relative overflow-hidden">
      <div
        style={{
          position: 'absolute',
          left: offset.left,
          top: offset.top,
          width: BASE_WIDTH,
          height: BASE_HEIGHT,
          transform: appState === 'auth' ? 'none' : `scale(${scale})`,
           transformOrigin: appState === 'auth' ? undefined as any : 'top left',
        }}
      >
        <div className="w-[393px] h-[852px] bg-white relative overflow-hidden mx-auto" style={{ touchAction: appState === 'auth' ? 'manipulation' : undefined }}>
          {/* 新增：应用状态切换逻辑 */}
          <AnimatePresence mode="wait" initial={true}>
            {appState === 'launch' && (
              <motion.div
                key="launch"
                className="absolute inset-0"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
              >
                <LaunchingPage />
              </motion.div>
            )}
            {appState === 'auth' && (
              <motion.div
                key="auth"
                className="absolute inset-0"
                initial={{ opacity: 1, x: 0, scale: 1 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: -40, scale: 0.98 }}
                transition={{ duration: 0.35, ease: 'easeOut' }}
              >
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
              </motion.div>
            )}
            
            {appState === 'main' && (
              <motion.div
                key="main"
                className="absolute inset-0"
                initial={{ opacity: 0, x: 40, scale: 1.02 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 1.02 }}
                transition={{ duration: 0.45, ease: 'easeOut' }}
              >
                <>
               {/* 添加滑块样式 */}
               <style dangerouslySetInnerHTML={{ __html: sliderStyles }} />
               {/* Header */}
               <motion.div 
                 className="pt-4 pb-2 px-[19px] z-0 relative"
                 initial={{ y: -50, opacity: 0 }}
                 animate={{ y: 0, opacity: 1 }}
                 transition={{ duration: 0.5 }}
               >
                 <div className="flex items-center justify-between w-[354px]">
                   <PopupButton />
                   <div className="flex gap-2">
                     <IconButton onClick={toggleHistoryMode}>
                       <div className="w-6 h-6">
                         <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                           <path d={svgPaths.history} fill={isHistoryMode ? "#0055f7" : "black"} />
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
                   </div>
                 </div>
               </motion.div>

           {/* Main Content - Card Stack */}
           <div className="relative h-[580px] flex items-center justify-center px-4 mt-8">
             <div className="relative w-[357px] h-[614px]">
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
                       <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-4 z-[999]">
                         <motion.button
                           onClick={() => handleHistorySlide('left')}
                           disabled={historyIndex === 0}
                           className="w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white disabled:opacity-30 transition-all duration-200"
                           whileHover={{ scale: 1.1 }}
                           whileTap={{ scale: 0.95 }}
                         >
                           <ArrowLeft size={20} />
                         </motion.button>
                         <div className="flex items-center px-4 py-2 bg-black/50 backdrop-blur-sm rounded-full text-white text-sm font-medium min-w-[60px] justify-center">
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
                       <h3 className="text-xl font-medium text-gray-700 mb-2">暂无历史记录！</h3>
                       <p className="text-gray-500">左滑一些项目即可在这里查看。</p>
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
                       >
                         <ProjectCard
                           project={proj}
                           index={i}
                           onSwipe={isTopCard ? handleSwipe : () => {}}
                           isTop={isTopCard}
                           onClick={isTopCard ? () => setSelectedProject(proj) : () => {}}
                           isHistory={!isTopCard}
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
                     <h3 className="text-xl font-medium text-gray-700 mb-2">没有更多项目了！</h3>
                     <p className="text-gray-500">稍后再来看看新的合作机会。</p>
                   </div>
                 </motion.div>
               )}
             </div>
           </div>

           {/* Bottom Navigation */}
           <motion.div 
             className="absolute bottom-0 left-0 right-0 bg-neutral-50 h-[100px] border-t border-[#e8edf2]"
             initial={{ y: 126 }}
             animate={{ y: 0 }}
             transition={{ delay: 0.7, duration: 0.5 }}
           >
             <div className="h-full relative">
               {/* Navigation Icons */}
               <div className="absolute left-[13px] top-[25px] flex gap-[105px]">
                 <div className="flex gap-0">
                   <IconButton className="w-[65.2px]">
                     <div className="w-6 h-6">
                       <svg className="block size-full" fill="none" viewBox="0 0 18 19">
                         <path d={svgPaths.p11f24e80} fill="#0055F7" />
                       </svg>
                     </div>
                   </IconButton>
                   <IconButton className="w-[65.2px]">
                     <div className="w-6 h-6">
                       <svg className="block size-full" fill="none" viewBox="0 0 21 21">
                         <path d={svgPaths.p11caffd0} fill="#616C78" />
                       </svg>
                     </div>
                   </IconButton>
                 </div>
                 <div className="flex gap-0">
                   <IconButton className="w-[65.2px]">
                     <div className="w-6 h-6">
                       <svg className="block size-full" fill="none" viewBox="0 0 20 20">
                         <path d={svgPaths.p19a90780} fill="#616C78" />
                       </svg>
                     </div>
                   </IconButton>
                   <IconButton className="w-[65.2px]">
                     <div className="w-6 h-6">
                       <svg className="block size-full" fill="none" viewBox="0 0 20 20">
                         <path d={svgPaths.p3d54cd00} fill="#616C78" />
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
               >
                 <div className="w-6 h-6">
                 <svg className="block size-full" fill="none" viewBox="0 0 23 23">
                   <path d={svgPaths.p3b63e500} fill="white" stroke="white" />
                 </svg>
               </div>
               </motion.button>
             </div>
           </motion.div>

           {/* Filter Sidebar */}
           <FilterSidebar 
             isOpen={showFilter} 
             onClose={() => setShowFilter(false)}
             filters={filters}
             setFilters={setFilters}
           />

           {/* Project Detail View */}
           <AnimatePresence>
             {selectedProject && (
               <ProjectDetailView
                 project={selectedProject}
                 onClose={() => setSelectedProject(null)}
                 suppressFirstTap={true}
               />
             )}
           </AnimatePresence>
                 </>
               </motion.div>
             )}
           </AnimatePresence>
        </div>
      </div>
      {showPopup && createPortal(
        <div
          style={{
            position: 'fixed',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            pointerEvents: 'none'
          }}
        >
          <AnimatePresence>
            <motion.div
              key="popup"
              initial={{ y: '100vh', opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: '100vh', opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              style={{
                width: popupWidthPx + 'px',
                height: 'auto',
                background: 'transparent',
                boxShadow: 'none',
                pointerEvents: 'auto'
              }}
            >
              <InteractivePopup 
                onClose={handlePopupClose}
                defaultChecked={suppressGreetingPopup}
                onDefaultChange={handleDefaultGreetingChange}
              />
            </motion.div>
          </AnimatePresence>
        </div>,
        document.body
      )}
    </div>
  );
}