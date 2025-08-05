import { useState, useRef } from 'react';
import { motion, PanInfo, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { Star, ChevronDown, MapPin, Calendar, Users, Target, ExternalLink, ArrowLeft, Check, Play, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { ImageWithFallback } from './components/figma/ImageWithFallback';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from './components/ui/sheet';
import { Slider } from './components/ui/slider';
import { Checkbox } from './components/ui/checkbox';
import { Badge } from './components/ui/badge';
import svgPaths from "./imports/svg-fko3i96u3r";
import { t } from './translations';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';

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
  status: 'ongoing' | 'finished';
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
    status: 'ongoing',
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
  },
  {
    id: 4,
    title: "Emma Davis",
    author: "Emma Davis",
    collaborators: 0,
    description: "Product Manager passionate about creating user-centered digital experiences. Love working on projects that make a real impact on people's lives.",
    tags: ["Product Management", "Strategy", "User Research"],
    type: 'profile',
    cardStyle: 'profile',
    status: 'ongoing',
    media: [
      "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=300&fit=crop",
      "https://videos.pexels.com/video-files/4753989/4753989-hd_1920_1080_24fps.mp4"
    ],
    owner: {
      name: "Emma Davis",
      age: 27,
      gender: "Female",
      role: "Product Manager",
      distance: 1.2,
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
      tags: ["Product Management", "Strategy", "User Research", "Agile", "Analytics"]
    },
    collaboratorsList: [],
    detailedDescription: "Experienced Product Manager with 5+ years in tech, specializing in user-centered design and data-driven product decisions.",
    startTime: "Available Now",
    currentProgress: 0,
    content: "Looking to collaborate on meaningful projects that solve real user problems.",
    purpose: "To help teams build products that users love and that drive business success.",
    lookingFor: ["Interesting Projects", "Startup Opportunities", "Consulting Work"],
    links: ["https://linkedin.com/in/emmadavis", "https://emmadavis.dev"]
  }
];

const projectTypes = ["AI", "Design", "Sustainability", "Mobile", "VR", "Education", "Blockchain", "Gaming", "Health", "Finance"];

interface FilterState {
  cardTypes: { project: boolean; profile: boolean };
  projectStatus: { ongoing: boolean; finished: boolean };
  projectTypes: string[];
  distance: number[];
  gender: string[];
  age: number[];
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
          {t('appName')}
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
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-80 bg-gradient-to-br from-blue-50 to-blue-100 border-l-2 border-blue-200">
        <SheetHeader className="px-6 pt-6 pb-4">
          <SheetTitle className="text-blue-900 text-xl">{t('filters')}</SheetTitle>
          <SheetDescription className="text-blue-700">
            {t('filterDescription')}
          </SheetDescription>
        </SheetHeader>
        <div className="h-[calc(100%-120px)] overflow-y-auto px-6 pb-6">
          <div className="space-y-6">
            {/* Card Types */}
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-blue-200">
              <h3 className="mb-3 text-blue-900 font-semibold">{t('cardTypes')}</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Checkbox
                    id="project"
                    checked={filters.cardTypes.project}
                    onCheckedChange={(checked) =>
                      setFilters({
                        ...filters,
                        cardTypes: { ...filters.cardTypes, project: !!checked }
                      })
                    }
                    className="data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600"
                  />
                  <label htmlFor="project" className="text-blue-800 cursor-pointer">{t('projects')}</label>
                </div>
                <div className="flex items-center space-x-3">
                  <Checkbox
                    id="profile"
                    checked={filters.cardTypes.profile}
                    onCheckedChange={(checked) =>
                      setFilters({
                        ...filters,
                        cardTypes: { ...filters.cardTypes, profile: !!checked }
                      })
                    }
                    className="data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600"
                  />
                  <label htmlFor="profile" className="text-blue-800 cursor-pointer">{t('profiles')}</label>
                </div>
              </div>
            </div>

            {/* Project Status */}
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-blue-200">
              <h3 className="mb-3 text-blue-900 font-semibold">{t('projectStatus')}</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Checkbox
                    id="ongoing"
                    checked={filters.projectStatus.ongoing}
                    onCheckedChange={(checked) =>
                      setFilters({
                        ...filters,
                        projectStatus: { ...filters.projectStatus, ongoing: !!checked }
                      })
                    }
                    className="data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600"
                  />
                  <label htmlFor="ongoing" className="text-blue-800 cursor-pointer">{t('ongoing')}</label>
                </div>
                <div className="flex items-center space-x-3">
                  <Checkbox
                    id="finished"
                    checked={filters.projectStatus.finished}
                    onCheckedChange={(checked) =>
                      setFilters({
                        ...filters,
                        projectStatus: { ...filters.projectStatus, finished: !!checked }
                      })
                    }
                    className="data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600"
                  />
                  <label htmlFor="finished" className="text-blue-800 cursor-pointer">{t('finished')}</label>
                </div>
              </div>
            </div>

            {/* Project Types */}
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-blue-200">
              <h3 className="mb-3 text-blue-900 font-semibold">{t('projectTypes')}</h3>
              <div className="flex flex-wrap gap-2">
                {projectTypes.map((type) => (
                  <Badge
                    key={type}
                    variant={filters.projectTypes.includes(type) ? "default" : "outline"}
                    className={`cursor-pointer transition-all duration-200 ${
                      filters.projectTypes.includes(type)
                        ? "bg-blue-600 hover:bg-blue-700 text-white border-blue-600"
                        : "bg-white/80 hover:bg-blue-50 text-blue-700 border-blue-300 hover:border-blue-400"
                    }`}
                    onClick={() => {
                      const newTypes = filters.projectTypes.includes(type)
                        ? filters.projectTypes.filter(t => t !== type)
                        : [...filters.projectTypes, type];
                      setFilters({ ...filters, projectTypes: newTypes });
                    }}
                  >
                    {type}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Distance */}
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-blue-200">
              <h3 className="mb-3 text-blue-900 font-semibold">{t('distance')}</h3>
              <Slider
                value={filters.distance}
                onValueChange={(value) => setFilters({ ...filters, distance: value })}
                max={50}
                min={0}
                step={1}
                className="w-full [&_[role=slider]]:bg-blue-600 [&_[role=slider]]:border-blue-600"
              />
              <div className="flex justify-between text-sm text-blue-600 mt-2 font-medium">
                <span>{filters.distance[0]} km</span>
                <span>{filters.distance[1]} km</span>
              </div>
            </div>

            {/* Age */}
            <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-blue-200">
              <h3 className="mb-3 text-blue-900 font-semibold">{t('ageRange')}</h3>
              <Slider
                value={filters.age}
                onValueChange={(value) => setFilters({ ...filters, age: value })}
                max={65}
                min={18}
                step={1}
                className="w-full [&_[role=slider]]:bg-blue-600 [&_[role=slider]]:border-blue-600"
              />
              <div className="flex justify-between text-sm text-blue-600 mt-2 font-medium">
                <span>{filters.age[0]} {t('years')}</span>
                <span>{filters.age[1]} {t('years')}</span>
              </div>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
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
  const [showFeedback, setShowFeedback] = useState<'left' | 'right' | null>(null);
  
  const x = useMotionValue(0);
  const rotate = useSpring(
    useTransform(x, [-200, 0, 200], [-20, 0, 20]),
    { stiffness: 300, damping: 20 }
  );

  const handleDragEnd = (_event: any, info: PanInfo) => {
    if (isHistory) return; // No swiping in history mode
    
    const velocity = info.velocity.x;
    const offset = info.offset.x;
    const speed = Math.max(Math.abs(velocity), Math.abs(offset));
    
    // Define the decision zone
    const swipeThreshold = 100; // Distance threshold for swipe decision
    const velocityThreshold = 400; // Velocity threshold for quick flicks
    
    // Check if the movement is decisive enough
    const isDecisiveSwipe = Math.abs(offset) > swipeThreshold || Math.abs(velocity) > velocityThreshold;
    
    if (isDecisiveSwipe) {
      // Determine direction and throw the card
      const direction = velocity > 0 || (velocity === 0 && offset > 0) ? 'right' : 'left';
      const throwDistance = (direction === 'right' ? 1 : -1) * Math.max(1000, speed * 2);
      const throwHeight = -Math.abs(speed) * 0.2;
      
      setExitX(throwDistance);
      setExitY(throwHeight);
      if (direction === 'right') setShowFeedback('right');
      onSwipe(direction);
    } else {
      // Bounce back to center if the movement wasn't decisive
      setExitX(0);
      setExitY(0);
      x.set(0); // Reset position
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

  return (
    <>
      <motion.div
        className="absolute inset-0"
        style={{
          zIndex: projects.length - index,
          x,
          rotate,
        }}
        drag={isTop && !isHistory ? "x" : false}
        dragConstraints={{ left: -1000, right: 1000 }} // Allow dragging but with some resistance
        dragElastic={0.7} // Slightly reduced elasticity
        onDragEnd={handleDragEnd}
        whileHover={{ scale: isTop ? 1.02 : 1 }}
        whileDrag={{
          scale: 1.02,
          cursor: "grabbing"
        }}
        animate={{ 
          scale: isTop ? 1 : 0.98 - (index * 0.03),
          y: isTop ? 0 : index * 8,
          x: exitX,
          opacity: 1
        }}
        initial={{ scale: 0.9, opacity: 0 }}
        whileInView={{ scale: isTop ? 1 : 0.98 - (index * 0.03), opacity: 1 }}
        transition={{ 
          x: {
            type: "spring",
            stiffness: 400,
            damping: 25,
            restDelta: 0.5
          },
          scale: {
            type: "spring",
            stiffness: 300,
            damping: 20,
            mass: 0.5
          }
        }}
        exit={{ 
          x: exitX, 
          y: exitY,
          rotate: exitX > 0 ? 45 : -45,
          opacity: 0,
          transition: { 
            duration: 0.5,
            ease: [0.23, 1, 0.32, 1]
          }
        }}
      >
        <motion.div
          className="w-[357px] h-[670px] rounded-[14px] shadow-[0px_8px_32px_0px_rgba(0,0,0,0.25)] overflow-hidden relative cursor-pointer"
          whileHover={isTop ? { y: -5, boxShadow: "0px 12px 40px 0px rgba(0,0,0,0.3)" } : {}}
          onClick={onClick}
        >
          {renderCardContent()}

          {/* Floating particles effect for image/video cards */}
          {(project.cardStyle === 'image' || project.cardStyle === 'video') && [...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-white/30 rounded-full"
              style={{
                left: `${20 + i * 15}%`,
                top: `${30 + i * 8}%`,
              }}
              animate={{
                y: [0, -20, 0],
                opacity: [0.3, 0.8, 0.3],
              }}
              transition={{
                duration: 3 + i * 0.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          ))}
        </motion.div>
      </motion.div>

      {/* Swipe Feedback */}
      <AnimatePresence>
        {showFeedback && (
          <SwipeFeedback 
            direction={showFeedback} 
            onComplete={() => setShowFeedback(null)} 
          />
        )}
      </AnimatePresence>
    </>
  );
}

function MediaViewer({ media, onClose }: { media: string[]; onClose: () => void }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const panStartX = useRef(0);

  return (
    <motion.div
      className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-black/50 rounded-full text-white hover:bg-black/70 transition-colors"
        >
          <X size={24} />
        </button>
        {/* Swipeable big image/video */}
        <motion.div
          className="relative max-w-4xl max-h-[80vh] mx-4 w-full h-full flex items-center justify-center"
          whileTap={{ cursor: 'grabbing' }}
          onPanStart={(_, info) => {
            panStartX.current = info.point.x;
          }}
          onPanEnd={(_, info) => {
            const delta = info.point.x - panStartX.current;
            const threshold = 50;
            if (delta > threshold && currentIndex > 0) {
              setCurrentIndex(currentIndex - 1);
            } else if (delta < -threshold && currentIndex < media.length - 1) {
              setCurrentIndex(currentIndex + 1);
            }
          }}
        >
          {(() => {
            const url = media[currentIndex];
            if (!url) return null;
            if (url.endsWith('.mp4') || url.endsWith('.webm') || url.endsWith('.mov')) {
              return (
                <video
                  src={url}
                  className="max-w-full max-h-[80vh] object-contain rounded-lg"
                  controls
                  autoPlay
                />
              );
            }
            return (
              <ImageWithFallback
                src={url}
                alt={`Media ${currentIndex + 1}`}
                className="max-w-full max-h-[80vh] object-contain rounded-lg"
              />
            );
          })()}
        </motion.div>
        {/* Slide indicators */}
        {media.length > 1 && (
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 z-20">
            {media.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-all duration-200 ${
                  index === currentIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}
        {/* Media counter */}
        {media.length > 1 && (
          <div className="absolute top-4 right-20 bg-black/50 text-white px-2 py-1 rounded text-xs z-20">
            {currentIndex + 1} / {media.length}
          </div>
        )}
      </div>
    </motion.div>
  );
}

function ProjectDetailView({ project, onClose }: { project: Project; onClose: () => void }) {
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);

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
            <div className="relative w-full h-80 bg-gray-100 rounded-lg overflow-hidden">
              {project.media.length > 0 ? (
                <Swiper
                  spaceBetween={0}
                  slidesPerView={1}
                  onSlideChange={(swiper: any) => setCurrentSlide(swiper.activeIndex)}
                  initialSlide={currentSlide}
                  style={{ width: '100%', height: '100%' }}
                >
                  {project.media.map((url, index) => (
                    <SwiperSlide key={index}>
                      <div className="w-full h-full flex items-center justify-center">
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
                <div className="absolute top-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-xs z-20">
                  {currentSlide + 1} / {project.media.length}
                </div>
              )}
            </div>

            <div className="p-6 space-y-6">

            {/* Title and Status */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-2xl font-bold">{project.title}</h2>
                {project.type === 'project' && (
                  <Badge variant={project.status === 'ongoing' ? 'default' : 'secondary'} className="text-[10px] px-3 py-1 rounded-full whitespace-nowrap">
                    {project.status === 'ongoing' ? t('ongoing') : t('finished')}
                  </Badge>
                )}
              </div>
              {project.type === 'project' && (
                <div className="flex items-center gap-4 text-sm text-gray-600">
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

      {/* Media Viewer */}
      <AnimatePresence>
        {showMediaViewer && (
          <MediaViewer
            media={project.media}
            onClose={() => setShowMediaViewer(false)}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function App() {
  const [currentProjects, setCurrentProjects] = useState(projects);
  const [leftSwipedProjects, setLeftSwipedProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [showFilter, setShowFilter] = useState(false);
  const [isHistoryMode, setIsHistoryMode] = useState(false);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [filters, setFilters] = useState<FilterState>({
    cardTypes: { project: true, profile: true },
    projectStatus: { ongoing: true, finished: true },
    projectTypes: [],
    distance: [0, 50],
    gender: [],
    age: [18, 65]
  });

  const handleSwipe = (direction: 'left' | 'right') => {
    if (direction === 'left' && currentProjects.length > 0) {
      setLeftSwipedProjects(prev => [currentProjects[0], ...prev]);
    }
    
    setTimeout(() => {
      setCurrentProjects(prev => prev.slice(1));
    }, 600); // Increased delay for better animation
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
    if (project.type === 'project' && !filters.projectStatus[project.status]) return false;
    
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

  return (
    <div className="w-[393px] h-[852px] bg-white relative overflow-hidden mx-auto">
      {/* Header */}
      <motion.div 
        className="pt-4 pb-2 px-[19px] z-40 relative"
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
                  onSwipe={() => {}}
                  isTop={true}
                  onClick={() => setSelectedProject(currentProject)}
                  isHistory={true}
                />
                
                {/* Navigation Controls */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-4 z-10">
                  <motion.button
                    onClick={() => handleHistorySlide('left')}
                    disabled={historyIndex === 0}
                    className="w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white disabled:opacity-30 transition-all duration-200"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <ArrowLeft size={20} />
                  </motion.button>
                  <div className="flex items-center px-4 py-2 bg-black/50 backdrop-blur-sm rounded-full text-white text-sm font-medium">
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
                
                {/* Mouse wheel hint */}
                <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-white text-xs z-10">
                  Use mouse wheel to navigate
                </div>
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4">
                    <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                      <path d={svgPaths.history} fill="#9ca3af" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-medium text-gray-700 mb-2">No history yet!</h3>
                  <p className="text-gray-500">Swipe left on some projects to see them here.</p>
                </div>
              </div>
            )
          ) : (
            // Normal Mode - Card stack
            displayProjects.slice(0, 3).map((project, index) => (
              <ProjectCard
                key={project.id}
                project={project}
                index={index}
                onSwipe={handleSwipe}
                isTop={index === 0}
                onClick={() => setSelectedProject(project)}
              />
            ))
          )}
          
          {!isHistoryMode && displayProjects.length === 0 && (
            <motion.div
              className="w-full h-full flex items-center justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="text-center">
                <Star className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-gray-700 mb-2">No more projects!</h3>
                <p className="text-gray-500">Check back later for new collaboration opportunities.</p>
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
          />
        )}
      </AnimatePresence>
    </div>
  );
}