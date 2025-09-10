import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { MapPin, Edit3, ChevronLeft, ChevronRight, X, ArrowLeft, Calendar, Target, Users, ExternalLink, Camera } from 'lucide-react';
import { Button } from './ui/button';
import { HeaderBar } from './HeaderBar';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';

// 导入翻译函数
import { t, currentLanguage as i18nCurrentLanguage } from '../translations';

// SVG路径
const svgPaths = {
  male: "M9 12l3 3 3-3",
  female: "M9 12l3 3 3-3",
  like: "M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
};



// 隐藏滚动条的CSS
const scrollbarStyle = `
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  
  /* 项目卡片Swiper样式 */
  .project-swiper .swiper-slide {
    width: auto;
    height: auto;
  }
  
  .project-swiper .swiper-wrapper {
    align-items: stretch;
  }
  
  /* 确保Swiper可以正常滑动 */
  .project-swiper {
    overflow: visible;
    touch-action: pan-y;
  }
  
  .project-swiper .swiper-slide {
    touch-action: pan-y;
    user-select: none;
  }
`;

// 示例图片 - 实际应用中可以从props或API获取
const sampleImages = [
  "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=400&fit=crop&crop=face",
  "https://images.unsplash.com/photo-1516985080664-ed2fc6a32937?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1515378791036-0648a814c963?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1586297135537-94bc9ba060aa?w=300&h=400&fit=crop"
];



interface ProfilePageProps {
  onBack: () => void;
  onEditProject?: (project: any) => void; // 添加编辑项目回调
  readOnly?: boolean;
  showBackHeader?: boolean; // 紧凑模式：用于聊天跳转
  compactHero?: boolean; // 新增：紧凑头部布局
}

// 项目卡片组件 - 使用与主页面完全一致的样式
function ProjectCard({ 
  project, 
  isCollaboration = false, 
  onClick, 
  onLongPressStart, 
  onLongPressEnd,
  overlayChild
}: { 
  project: any; 
  isCollaboration?: boolean; 
  onClick: () => void;
  onLongPressStart?: () => void;
  onLongPressEnd?: () => void;
  overlayChild?: React.ReactNode;
}) {
  const statusColorMap = {
    '进行中': 'bg-blue-500',
    '已完成': 'bg-green-500',
    '未开始': 'bg-gray-500'
  };

  const statusDisplay = (() => {
    const zh = project.status;
    if (i18nCurrentLanguage === 'en') {
      if (zh === '进行中') return 'Ongoing';
      if (zh === '已完成') return 'Finished';
      return 'Not started';
    }
    return zh;
  })();

  // 将项目数据转换为与主页面一致的格式
  const projectData = {
    id: project.id,
    title: project.title,
    author: isCollaboration ? (i18nCurrentLanguage === 'en' ? (project.role || 'Collaborator') : (project.role || '合作者')) : (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者'),
    collaborators: 1,
    background: project.image,
    description: project.description,
    tags: project.tags,
    type: 'project' as const,
    cardStyle: 'image' as const,
    status: project.status === '进行中' ? 'ongoing' : project.status === '已完成' ? 'finished' : 'not_started',
    owner: {
      name: isCollaboration ? (project.role || (i18nCurrentLanguage === 'en' ? 'Collaborator' : '合作者')) : (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者'),
      age: 25,
      gender: 'Non-binary',
      role: isCollaboration ? (project.role || (i18nCurrentLanguage === 'en' ? 'Collaborator' : '合作者')) : (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者'),
      distance: 5,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(project.title)}`,
      tags: project.tags
    },
    collaboratorsList: [],
    detailedDescription: project.description,
    startTime: project.startDate,
    currentProgress: project.progress,
    content: project.description,
    purpose: project.description,
    lookingFor: [],
    links: [],
    media: [project.image]
  };

  return (
    <div 
      className="w-[357px] h-[600px] rounded-[14px] overflow-hidden relative cursor-pointer pressable shadow-[0px_8px_24px_0px_rgba(0,0,0,0.18)] hover:scale-[1.02] transition-transform duration-150 will-change-transform"
      onClick={onClick}
      {...(onLongPressStart && {
        onTouchStart: onLongPressStart,
        onMouseDown: onLongPressStart
      })}
      {...(onLongPressEnd && {
        onTouchEnd: onLongPressEnd,
        onMouseUp: onLongPressEnd,
        onMouseLeave: onLongPressEnd
      })}
    >
      {/* 项目图片 */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={project.image}
          alt={project.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
      </div>
      
      {/* 状态标签 */}
      <div className="absolute top-4 right-4">
        <Badge 
          variant="secondary" 
          className={`text-white text-xs ${statusColorMap[project.status as keyof typeof statusColorMap] || 'bg-blue-500'}`}
        >
          {statusDisplay}
        </Badge>
      </div>
      
      {/* 项目信息 - 与主页面完全一致的布局 */}
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
            <span className="font-medium">{i18nCurrentLanguage === 'en' ? 'By' : '发起者'}&nbsp;</span>
            <span className="font-semibold">{isCollaboration ? project.role || (i18nCurrentLanguage === 'en' ? 'Collaborator' : '合作者') : (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者')}</span>
            <span className="mx-2">·</span>
            <span className="font-semibold">1</span>
            <span className="font-medium">&nbsp;{i18nCurrentLanguage === 'en' ? 'Collaborator' : '合作者'}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {project.tags.map((tag: string, i: number) => (
              <motion.span
                key={tag}
                className="px-3 py-1 bg-white/20 text-white border border-white/30 rounded-full text-xs font-medium"
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
      {overlayChild}
    </div>
  );
}

// MediaViewer组件
function MediaViewer({ media, onClose, initialIndex = 0 }: { media: string[]; onClose: () => void; initialIndex?: number }) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  useEffect(() => {
    setCurrentIndex(initialIndex);
  }, [initialIndex]);

  const handleBackgroundClick = (e: React.MouseEvent) => {
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
        <Swiper
          spaceBetween={0}
          slidesPerView={1}
          initialSlide={currentIndex}
          onSlideChange={(swiper: any) => setCurrentIndex(swiper.activeIndex)}
          className="w-full h-full"
          style={{ width: '100%', height: '100%' }}
          onClick={(e: any) => e.stopPropagation()}
        >
          {media.map((url: string, index: number) => (
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
        {media.length > 1 && (
          <div 
            className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 z-20"
            onClick={(e: any) => e.stopPropagation()}
          >
            {media.map((_: any, index: number) => (
              <button
                key={index}
                onClick={(e) => {
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

// ProjectDetailView组件 - 与主页面完全一致
function ProjectDetailView({ project, onClose, suppressFirstTap = false, isFavorite = false, onLikeChange }: { 
  project: any; 
  onClose: () => void; 
  suppressFirstTap?: boolean, 
  isFavorite?: boolean, 
  onLikeChange?: (project: any, liked: boolean) => void 
}) {
  const [showMediaViewer, setShowMediaViewer] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showNavButtons, setShowNavButtons] = useState(false);
  const swiperRef = useRef<any>(null);
  const buttonTimerRef = useRef<number | null>(null);
  const [clickEnabled, setClickEnabled] = useState(!suppressFirstTap);
  const [liked, setLiked] = useState(isFavorite);
  const [likeAnimate, setLikeAnimate] = useState(false);

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
    if (buttonTimerRef.current) {
      clearTimeout(buttonTimerRef.current);
    }
    buttonTimerRef.current = setTimeout(() => {
      setShowNavButtons(false);
    }, 2000);
  };

  const handleSlideChange = (swiper: any) => {
    setCurrentSlide(swiper.activeIndex);
    showButtons();
  };

  // 项目状态tag颜色映射
  const statusColorMap = {
    'not_started': 'bg-gray-300 text-gray-800',
    'ongoing': 'bg-[#0055F7] text-white',
    'finished': 'bg-green-500 text-white',
  };

  // 将ProfilePage的项目数据转换为ProjectDetailView需要的格式
  const projectData = {
    id: project.id,
    title: project.title,
    author: (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者'),
    collaborators: 1,
    background: project.image,
    description: project.description,
    tags: project.tags,
    type: 'project' as const,
    cardStyle: 'image' as const,
    status: project.status === '进行中' ? 'ongoing' : project.status === '已完成' ? 'finished' : 'not_started',
    owner: {
      name: (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者'),
      age: 25,
      gender: 'Non-binary',
      role: (i18nCurrentLanguage === 'en' ? 'Initiator' : '发起者'),
      distance: 5,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(project.title)}`,
      tags: project.tags
    },
    collaboratorsList: [],
    detailedDescription: project.description,
    startTime: project.startDate,
    currentProgress: project.progress,
    content: project.description,
    purpose: project.description,
    lookingFor: [],
    links: Array.isArray(project.links) ? project.links : [],
    media: Array.isArray(project.media) && project.media.length > 0 ? project.media : [project.image]
  };

  // local date formatter for EN
  const formatMonthYearEnLocal = (val?: string) => {
    if (!val) return '';
    const m = val.match(/^(\d{4})年(\d{1,2})月$/);
    if (m) {
      const y = parseInt(m[1], 10);
      const mo = parseInt(m[2], 10) - 1;
      const d = new Date(y, mo, 1);
      try { return d.toLocaleString('en-US', { month: 'short', year: 'numeric' }); } catch {}
      return `${d.toDateString().split(' ')[1]} ${y}`;
    }
    return val;
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
        <div className="h-[90px] flex items-center justify-between px-4 border-b border-[#E8EDF2] bg-[#FAFAFA]">
          <button onClick={onClose} className="p-2">
            <ArrowLeft size={24} className="text-blue-600" />
          </button>
          <h1 className="font-semibold">{t('projectDetails') || '项目详情'}</h1>
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
              {projectData.media.length > 0 ? (
                <Swiper
                  spaceBetween={0}
                  slidesPerView={1}
                  onSlideChange={handleSlideChange}
                  initialSlide={currentSlide}
                  style={{ width: '100%', height: '100%' }}
                  onSwiper={(swiper: any) => { swiperRef.current = swiper; }}
                >
                  {projectData.media.map((url: string, index: number) => (
                    <SwiperSlide key={index}>
                      <div 
                        className="w-full h-full flex items-center justify-center cursor-pointer"
                        onClick={() => { setCurrentSlide(index); setShowMediaViewer(true); }}
                      >
                        <ImageWithFallback
                          src={url}
                          alt={`Media ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </SwiperSlide>
                  ))}
                </Swiper>
              ) : (
                <div className="w-full h-48 rounded-lg overflow-hidden">
                  <ImageWithFallback
                    src={project.image}
                    alt={project.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              
              {/* 左右切换按钮 */}
              {projectData.media.length > 1 && (
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
                    disabled={currentSlide === projectData.media.length - 1}
                    className={`absolute right-2 top-1/2 transform -translate-y-1/2 w-10 h-10 bg-black/30 hover:bg-black/50 text-white rounded-full flex items-center justify-center transition-opacity duration-200 disabled:opacity-0 z-20 ${
                      showNavButtons ? 'opacity-100' : 'opacity-0'
                    }`}
                  >
                    <ChevronRight size={20} />
                  </button>
                </>
              )}
              
              {/* Slide indicators */}
              {projectData.media.length > 1 && (
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 z-20">
                  {projectData.media.map((_: any, index: number) => (
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
              
              {projectData.media.length > 1 && (
                <div className={`absolute top-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-xs z-20 transition-opacity duration-200 ${
                  showNavButtons ? 'opacity-100' : 'opacity-0'
                }`}>
                  {currentSlide + 1} / {projectData.media.length}
                </div>
              )}
            </div>

            <div className="p-6 space-y-6">
              {/* Title and Status */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-3xl font-bold w-full max-w-full whitespace-normal break-words leading-tight">{project.title}</h2>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className={`inline-block px-3 py-1 rounded-full font-semibold text-xs ${statusColorMap[projectData.status as keyof typeof statusColorMap]}`}>
                    {project.status === '进行中' ? (t('ongoing') || '进行中') : project.status === '已完成' ? (t('finished') || '已完成') : (t('notStarted') || '未开始')}
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar size={16} />
                    <span>{i18nCurrentLanguage === 'en' ? formatMonthYearEnLocal(project.startDate) : project.startDate}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Target size={16} />
                    <span>{project.progress}% {i18nCurrentLanguage === 'en' ? 'complete' : (t('complete') || '完成')}</span>
                  </div>
                </div>
              </div>

              {/* Owner Info */}
              <div className="border rounded-lg p-4">
                <h3 className="text-xl font-semibold mb-3">{t('projectOwner') || '项目发起者'}</h3>
                <div className="flex items-start gap-3">
                  <ImageWithFallback
                    src={projectData.owner.avatar}
                    alt={projectData.owner.name}
                    className="w-16 h-16 rounded-full object-cover"
                  />
                  <div className="flex-1">
                    <h4 className="font-medium">{projectData.owner.name}</h4>
                    <p className="text-sm text-gray-600">{projectData.owner.role}</p>
                                         <div className="flex flex-wrap gap-1 mt-2">
                       {projectData.owner.tags.map((tag: string) => (
                         <Badge key={tag} variant="outline" className="text-xs">
                           {tag}
                         </Badge>
                       ))}
                     </div>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <h3 className="text-xl font-semibold mb-2">{t('description') || '描述'}</h3>
                <p className="text-gray-700 leading-relaxed">{project.description}</p>
              </div>

              {/* Purpose */}
              <div>
                <h3 className="text-xl font-semibold mb-2">{t('goals') || '目标'}</h3>
                <p className="text-gray-700 leading-relaxed">{project.description}</p>
              </div>

              {/* Content */}
              <div>
                <h3 className="text-xl font-semibold mb-2">{t('whatWeAreBuilding') || '我们正在构建什么'}</h3>
                <p className="text-gray-700 leading-relaxed">{project.description}</p>
              </div>

              {/* Looking For */}
              <div>
                <h3 className="text-xl font-semibold mb-2">{t('lookingFor') || '寻找'}</h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  <Badge variant="secondary">技术专家</Badge>
                  <Badge variant="secondary">设计师</Badge>
                  <Badge variant="secondary">产品经理</Badge>
                </div>
                <p className="text-gray-700 leading-relaxed">
                  我们正在积极寻找有才华的个人加入我们的团队并为这个令人兴奋的项目做出贡献。如果你拥有我们正在寻找的技能和热情，我们很乐意听到你的消息！
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>



      {/* 大图浏览弹窗 */}
      <AnimatePresence>
        {showMediaViewer && (
          <MediaViewer
            media={projectData.media}
            onClose={() => setShowMediaViewer(false)}
            initialIndex={currentSlide}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ProfileEditPage组件 - 编辑个人资料页面
function ProfileEditPage({ 
  formData, 
  onSave, 
  onCancel 
}: { 
  formData: any; 
  onSave: (data: any) => void; 
  onCancel: () => void; 
}) {
  const [localFormData, setLocalFormData] = useState(formData);
  const [newSkill, setNewSkill] = useState('');
  const typeTagOptions = ['正在寻找项目', '寻找合作者', '招聘伙伴', '投资人', '导师/顾问', '开放合作'];
  const [nameTouched, setNameTouched] = useState(false);

  const toggleTypeTag = (tag: string) => {
    setLocalFormData((prev: any) => {
      const exists = (prev.typeTags || []).includes(tag);
      const next = exists ? prev.typeTags.filter((t: string) => t !== tag) : [...(prev.typeTags || []), tag];
      return { ...prev, typeTags: next };
    });
  };

  const handleInputChange = (field: string, value: string | number) => {
    setLocalFormData((prev: any) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMediaAdd = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const readers: Promise<string>[] = [];
    for (let i = 0; i < files.length; i++) {
      const f = files[i];
      if (!f.type.startsWith('image/')) continue;
      readers.push(new Promise((resolve) => {
        const r = new FileReader();
        r.onloadend = () => resolve(typeof r.result === 'string' ? r.result : '');
        r.readAsDataURL(f);
      }));
    }
    Promise.all(readers).then((dataUrls) => {
      const imgs = dataUrls.filter(Boolean);
      if (imgs.length === 0) return;
      setLocalFormData((prev: any) => ({ ...prev, media: [ ...(prev.media || []), ...imgs ] }));
    });
  };

  const handleMediaRemove = (idx: number) => {
    setLocalFormData((prev: any) => ({
      ...prev,
      media: (prev.media || []).filter((_: string, i: number) => i !== idx)
    }));
  };

  const handleSkillAdd = () => {
    if (newSkill.trim() && !localFormData.skills.includes(newSkill.trim())) {
      setLocalFormData((prev: any) => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const handleSkillRemove = (skillToRemove: string) => {
    setLocalFormData((prev: any) => ({
      ...prev,
      skills: prev.skills.filter((skill: string) => skill !== skillToRemove)
    }));
  };

  const handleSave = () => {
    // 仅姓名必填：空时标红并提示
    if (!localFormData?.name || String(localFormData.name).trim() === '') {
      setNameTouched(true);
      return;
    }
    onSave(localFormData);
  };

  const handleAvatarAdd = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const f = files[0];
    if (!f.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = typeof reader.result === 'string' ? reader.result : '';
      if (!dataUrl) return;
      setLocalFormData((prev: any) => ({ ...prev, avatar: dataUrl }));
    };
    reader.readAsDataURL(f);
  };

  // 初始化时从本地存储恢复编辑态头像/媒体
  useEffect(() => {
    try {
      const saved = localStorage.getItem('profile_edit_data');
      if (saved) {
        const parsed = JSON.parse(saved);
        setLocalFormData((prev: any) => ({
          ...prev,
          avatar: typeof parsed?.avatar === 'string' ? parsed.avatar : prev.avatar,
          media: Array.isArray(parsed?.media) ? parsed.media : prev.media,
        }));
      }
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 监听编辑态头像/媒体变化，立即持久化（即使未按保存）
  useEffect(() => {
    try {
      const payload = {
        avatar: localFormData?.avatar,
        media: localFormData?.media,
      };
      localStorage.setItem('profile_edit_data', JSON.stringify(payload));
    } catch {}
  }, [localFormData?.avatar, localFormData?.media]);

  return (
    <motion.div
      className="absolute left-0 right-0 mx-auto w-[393px] bg-white z-50 top-0 bottom-0"
      initial={{ y: '100%', opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: '100%', opacity: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <div className="w-full h-full flex flex-col">
        {/* Header */}
        <div className="h-[90px] flex items-center justify-between px-4 border-b border-[#E8EDF2] bg-[#FAFAFA]">
          <button onClick={onCancel} className="p-2">
            <ArrowLeft size={24} className="text-blue-600" />
          </button>
          <h1 className="font-bold text-lg">{t('editProfile') || '编辑个人资料'}</h1>
          <button 
            onClick={handleSave}
            className="px-4 py-2 bg-[#0055F7] text-white rounded-lg font-bold hover:bg-[#0043C4] transition-colors"
          >
            {t('save') || '保存'}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* 基本信息 */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('basicInfo') || '基本信息'}</h3>
            
            {/* 姓名 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('name') || '姓名'}</label>
              <input
                type="text"
                value={localFormData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                onBlur={() => setNameTouched(true)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none ${nameTouched && (!localFormData?.name || String(localFormData.name).trim() === '') ? 'border-red-500 focus:ring-red-500' : 'border-gray-300'}`}
                placeholder={t('enterName') || '请输入姓名'}
              />
              {nameTouched && (!localFormData?.name || String(localFormData.name).trim() === '') && (
                <p className="mt-1 text-xs text-red-600">{t('enterName') || '请输入姓名'}</p>
              )}
            </div>

            {/* 生日（用于计算年龄） */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('birthday') || '生日'}</label>
              <input
                type="date"
                value={localFormData.birthday || ''}
                onChange={(e) => handleInputChange('birthday', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none"
                placeholder={t('enterBirthday') || '请选择生日'}
              />
            </div>

            {/* 位置 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('location') || '位置'}</label>
              <input
                type="text"
                value={localFormData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none"
                placeholder={t('enterLocation') || '请输入位置'}
              />
            </div>
          </div>

          {/* 个人简介 */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('about') || '个人简介'}</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('about') || '个人简介'}</label>
              <textarea
                value={localFormData.bio || ''}
                onChange={(e) => handleInputChange('bio', e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none resize-none"
                placeholder={t('introduceYourself') || '请介绍你自己...'}
              />
            </div>
          </div>

          {/* 目标 */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('goals') || '目标'}</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('yourGoals') || '你的目标是什么？'}</label>
              <textarea
                value={localFormData.objective || ''}
                onChange={(e) => handleInputChange('objective', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none resize-none"
                placeholder={t('describeYourGoals') || '请描述你的目标...'}
              />
            </div>
          </div>

          {/* 寻找 */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('lookingFor') || '寻找'}</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('whatAreYouLookingFor') || '你在寻找什么？'}</label>
              <textarea
                value={localFormData.lookingFor || ''}
                onChange={(e) => handleInputChange('lookingFor', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none resize-none"
                placeholder={t('describeWhatYouAreLookingFor') || '请描述你在寻找什么...'}
              />
            </div>
          </div>

          {/* 媒体（第一张图片作为主页背景） */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('media') || '媒体'}</h3>
            <p className="text-xs text-gray-500 mt-1">{(i18nCurrentLanguage === 'en') ? 'First image will be used as background' : (t('firstImageAsBackground') || '第一张图片将作为个人页背景显示')}</p>
            <div>
              <input
                id="profile-media-input"
                type="file"
                accept="image/*"
                multiple
                onChange={(e) => handleMediaAdd(e.target.files)}
                className="hidden"
              />
              <label
                htmlFor="profile-media-input"
                className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-blue-50 text-blue-700 text-sm font-semibold hover:bg-blue-100 cursor-pointer"
              >
                {(i18nCurrentLanguage === 'en') ? 'Upload images' : (t('uploadImages') || '选择图片')}
              </label>
            </div>
            {(localFormData.media && localFormData.media.length > 0) && (
              <div className="grid grid-cols-3 gap-2">
                {localFormData.media.map((url: string, idx: number) => (
                  <div key={idx} className="relative group aspect-[3/4]">
                    <img src={url} alt={`media-${idx}`} className="w-full h-full object-cover rounded-lg" />
                    <button
                      type="button"
                      onClick={() => handleMediaRemove(idx)}
                      className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition bg-black/50 text-white text-xs px-2 py-1 rounded"
                    >
                      {t('remove') || '移除'}
                    </button>
                    {idx === 0 && (
                      <div className="absolute bottom-1 left-1 bg-black/60 text-white text-[10px] px-1.5 py-0.5 rounded">
                        {t('background') || '背景'}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 类型标签（第一排） */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('typeTags') || '类型标签'}</h3>
            <div className="flex flex-wrap gap-2">
              {typeTagOptions.map((tag) => {
                const active = (localFormData.typeTags || []).includes(tag);
                return (
                  <button
                    key={tag}
                    onClick={() => toggleTypeTag(tag)}
                    className={`px-3 py-1 rounded-full border text-sm font-semibold transition-colors ${active ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}`}
                  >
                    {tag}
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-gray-500">{t('typeTagsHint') || '这些标签将显示在个人主页第一排，用于说明你的身份类型。'}</p>
          </div>

          {/* 技能标签 */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">{t('skillTags') || '技能标签'}</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('addNewSkill') || '添加新技能'}</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none"
                  placeholder={t('enterNewSkill') || '输入新技能'}
                  onKeyPress={(e) => e.key === 'Enter' && handleSkillAdd()}
                />
                <button
                  onClick={handleSkillAdd}
                  className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors font-medium"
                >
                  {t('add') || '添加'}
                </button>
              </div>
            </div>
            
            {/* 现有技能标签 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('existingSkills') || '现有技能'}</label>
              <div className="flex flex-wrap gap-2">
                {(localFormData.skills || []).map((skill: string, index: number) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                  >
                    <span>{skill}</span>
                    <button
                      onClick={() => handleSkillRemove(skill)}
                      className="w-4 h-4 rounded-full bg-blue-200 hover:bg-blue-300 flex items-center justify-center text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function ProfilePage({ onBack, onEditProject, readOnly = false, showBackHeader = false, compactHero = false }: ProfilePageProps) {
  const [activeTab, setActiveTab] = useState<'profile' | 'project'>('profile');
  const [planLevel, setPlanLevel] = useState<'Basic' | 'Pro' | 'Ai-Powered'>('Basic');
  const [planExpiry, setPlanExpiry] = useState<number | null>(null);
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [needsPurchase, setNeedsPurchase] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({
    name: '李晨',
    birthday: '1997-01-01',
    gender: 'Non-binary' as 'Male' | 'Female' | 'Non-binary',
    location: '深圳, 中国',
    bio: '👋 大家好，我是 李晨，一名热爱技术与创意的全栈开发者.\n我擅长 React / Node.js / Python，有丰富的移动端与Web应用开发经验。\n过去三年里，我参与过多个初创团队项目，主要负责前端架构设计、后端API开发以及用户体验优化。',
    objective: '和志同道合的伙伴一起，打造真正能解决问题、改变生活的产品。\n我特别关注教育科技与AI应用领域，如果你也对这些方向有兴趣，欢迎一起交流！',
    lookingFor: '能够让我持续成长，并与伙伴们一起从0到1打造产品的项目机会。',
    typeTags: ['寻找合作者', '正在寻找项目', '投资人'],
    skills: ['全栈开发者', 'React专家', 'Python', 'AI/ML', '创业经验'],
    media: [] as string[],
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face'
  });
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const contentSectionRef = useRef<HTMLDivElement>(null);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [showLongPressMenu, setShowLongPressMenu] = useState(false);
  const [longPressedProject, setLongPressedProject] = useState<any>(null);
  const [longPressTimer, setLongPressTimer] = useState<number | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingProject, setDeletingProject] = useState<any>(null);
  const [archivedProjects, setArchivedProjects] = useState<any[]>([]);

  // 只读模式下禁用编辑与交互
  const isReadOnly = !!readOnly;

  // 将静态数据转换为状态变量，以便修改
  const [initiatedProjects, setInitiatedProjects] = useState([
    {
      id: 1,
      title: "智能健康管理平台",
      description: "基于AI的健康数据分析平台，帮助用户追踪健康指标并提供个性化建议",
      status: "进行中",
      progress: 75,
      image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop",
      tags: ["AI", "健康", "数据分析"],
      startDate: "2024年1月",
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 30
    },
    {
      id: 2,
      title: "在线教育协作工具",
      description: "为远程教育设计的实时协作平台，支持多人同时编辑和互动",
      status: "已完成",
      progress: 100,
      image: "https://images.unsplash.com/photo-1523050854058-8df90110c9e1?w=400&h=200&fit=crop",
      tags: ["教育", "协作", "实时"],
      startDate: "2023年6月",
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 60
    },
    {
      id: 3,
      title: "可持续生活社区App",
      description: "连接环保爱好者的社交平台，分享可持续生活方式和环保项目",
      status: "进行中",
      progress: 45,
      image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=200&fit=crop",
      tags: ["环保", "社交", "社区"],
      startDate: "2024年3月",
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 10
    }
  ]);

  const [collaboratedProjects, setCollaboratedProjects] = useState([
    {
      id: 4,
      title: "区块链供应链追踪",
      description: "利用区块链技术实现产品供应链的透明化追踪和管理",
      status: "已完成",
      progress: 100,
      image: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=200&fit=crop",
      tags: ["区块链", "供应链", "追踪"],
      startDate: "2023年3月",
      role: "前端开发"
    },
    {
      id: 5,
      title: "VR建筑设计工具",
      description: "基于VR技术的建筑设计可视化工具，支持实时3D预览和协作",
      status: "进行中",
      progress: 60,
      image: "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=400&h=200&fit=crop",
      tags: ["VR", "建筑", "3D"],
      startDate: "2023年9月",
      role: "全栈开发"
    },
    {
      id: 6,
      title: "智能家居控制系统",
      description: "集成多种智能设备的统一控制平台，支持语音控制和自动化场景",
      status: "进行中",
      progress: 80,
      image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop",
      tags: ["IoT", "智能家居", "自动化"],
      startDate: "2023年12月",
      role: "后端开发"
    }
  ]);

  // 初始化：从本地存储加载项目与归档，并消费新发布队列
  useEffect(() => {
    try {
      const savedInitiated = localStorage.getItem('profile_initiated_projects');
      const savedArchived = localStorage.getItem('profile_archived_projects');
      if (savedInitiated) {
        const parsed = JSON.parse(savedInitiated);
        if (Array.isArray(parsed)) setInitiatedProjects(parsed);
      }
      if (savedArchived) {
        const parsed = JSON.parse(savedArchived);
        if (Array.isArray(parsed)) setArchivedProjects(parsed);
      }
    } catch {}
  }, []);

  // 消费新发布队列（根据套餐放置位置）
  useEffect(() => {
    try {
      const queueRaw = localStorage.getItem('profile_new_projects');
      if (!queueRaw) return;
      const queue = JSON.parse(queueRaw);
      if (!Array.isArray(queue) || queue.length === 0) return;

      setInitiatedProjects(prevInitiated => {
        let workingInitiated = [...prevInitiated];
        const toArchive: any[] = [];
        for (const p of queue) {
          const activeCount = workingInitiated.length;
          if (planLevel === 'Basic' && activeCount >= 2) {
            toArchive.push({ ...p, autoArchived: true, archivedAt: Date.now() });
          } else {
            // 新项目插入到最前
            workingInitiated = [p, ...workingInitiated];
          }
        }
        if (toArchive.length > 0) {
          setArchivedProjects(prev => {
            const exists = new Set(prev.map(x => x.id));
            const merged = [...prev, ...toArchive.filter(x => !exists.has(x.id))];
            return merged;
          });
        }
        return workingInitiated;
      });

      localStorage.removeItem('profile_new_projects');
    } catch {}
  }, [planLevel]);

  // Basic 限制：不再自动裁剪已有卡片，新发布超过 2 张时已在上面的队列消费里处理
  useEffect(() => {
    // no-op: 保留现有两张，新增的放入卡槽
  }, [planLevel]);

  // 持久化 initiated 与 archived
  useEffect(() => {
    try { localStorage.setItem('profile_initiated_projects', JSON.stringify(initiatedProjects)); } catch {}
  }, [initiatedProjects]);
  useEffect(() => {
    try { localStorage.setItem('profile_archived_projects', JSON.stringify(archivedProjects)); } catch {}
  }, [archivedProjects]);

  // 处理项目点击
  const handleProjectClick = (project: any) => {
    setSelectedProject(project);
  };

  // 处理长按开始
  const handleLongPressStart = (project: any) => {
    const timer = setTimeout(() => {
      setLongPressedProject(project);
      setShowLongPressMenu(true);
    }, 500); // 500ms长按触发
    setLongPressTimer(timer);
  };

  // 处理长按结束
  const handleLongPressEnd = () => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
  };

  // 处理长按菜单操作
  const handleLongPressAction = (action: 'edit' | 'archive' | 'delete') => {
    if (!longPressedProject) return;
    
    switch (action) {
      case 'edit':
        console.log('编辑项目:', longPressedProject.title);
        // 跳转到项目编辑页面
        handleEditProject(longPressedProject);
        break;
      case 'archive':
        // 检查项目是否已存档
        const isArchived = archivedProjects.find(p => p.id === longPressedProject.id);
        if (isArchived) {
          console.log('取消存档项目:', longPressedProject.title);
          // 取消存档：移出归档，回到"发起的项目"
          setArchivedProjects(prev => prev.filter(p => p.id !== longPressedProject.id));
          setInitiatedProjects(prev => [{ ...longPressedProject, autoArchived: false }, ...prev]);
        } else {
          console.log('存档项目:', longPressedProject.title);
          handleArchiveProject(longPressedProject);
        }
        break;
      case 'delete':
        console.log('删除项目:', longPressedProject.title);
        // 显示删除确认弹窗
        setDeletingProject(longPressedProject);
        setShowDeleteConfirm(true);
        break;
    }
    
    setShowLongPressMenu(false);
    setLongPressedProject(null);
  };

  // 编辑项目 - 跳转到编辑页面
  const handleEditProject = (project: any) => {
    if (onEditProject) {
      onEditProject(project);
    } else {
      console.log('跳转到编辑页面:', project.title);
      // 如果没有传入编辑回调，可以在这里实现默认的跳转逻辑
    }
  };

  // 存档项目
  const handleArchiveProject = (project: any) => {
    // 将项目添加到已存档列表
    setArchivedProjects(prev => [...prev, { ...project, archivedAt: new Date().toISOString() }]);
    
    // 从原列表中移除项目
    if (project.role) {
      // 合作的项目
      setCollaboratedProjects(prev => prev.filter(p => p.id !== project.id));
    } else {
      // 发起的项目
      setInitiatedProjects(prev => prev.filter(p => p.id !== project.id));
    }
    
    // 显示存档成功提示
    console.log('项目已存档:', project.title);
  };

  // 取消存档项目
  const handleUnarchiveProject = (project: any) => {
    // 从已存档列表中移除
    setArchivedProjects(prev => prev.filter(p => p.id !== project.id));
    
    // 根据项目类型，恢复到原列表
    if (project.role) {
      // 合作的项目
      setCollaboratedProjects(prev => [...prev, { ...project }]);
    } else {
      // 发起的项目
      setInitiatedProjects(prev => [...prev, { ...project }]);
    }
    
    console.log('项目已取消存档:', project.title);
  };

  // 确认删除项目
  const handleConfirmDelete = () => {
    if (!deletingProject) return;
    
    // 直接删除项目：如果在归档中则从归档删除，否则从对应列表删除
    setArchivedProjects(prev => prev.filter(p => p.id !== deletingProject.id));
    if (deletingProject.role) {
      setCollaboratedProjects(prev => prev.filter(p => p.id !== deletingProject.id));
    } else {
      setInitiatedProjects(prev => prev.filter(p => p.id !== deletingProject.id));
    }
    
    // 隐藏弹窗
    setShowDeleteConfirm(false);
    setDeletingProject(null);
    
    console.log('项目已删除:', deletingProject.title);
  };

  // 调试信息
  useEffect(() => {
    if (scrollContainerRef.current && contentSectionRef.current) {
      const scrollHeight = scrollContainerRef.current.scrollHeight;
      const clientHeight = scrollContainerRef.current.clientHeight;
      const contentBottom = contentSectionRef.current.getBoundingClientRect().bottom;
      
      console.log('🔍 ProfilePage Debug Info:');
      console.log('📏 Scroll Container Height:', clientHeight);
      console.log('📏 Scroll Content Height:', scrollHeight);
      console.log('📏 Content Section Bottom:', contentBottom);
      console.log('📏 Window Height:', window.innerHeight);
      console.log('📏 Header Height: 90px');
      console.log('📏 Bottom Nav Height: 100px');
      console.log('📏 ProfilePage Height: 662px');
      console.log('📏 Scroll Container Height: 572px (662 - 90)');
    }
  }, [activeTab]);

  // ===== 自适应背景高度与密度控制 =====
  const heroRef = useRef<HTMLDivElement>(null);
  const infoRef = useRef<HTMLDivElement>(null);
  const bgImgLoadedRef = useRef<boolean>(false);
  const avatarLoadedRef = useRef<boolean>(false);
  const requestRecompute = () => {
    // 延后一帧计算，确保布局稳定
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const event = new Event('resize');
        window.dispatchEvent(event);
        try { console.log('[ProfilePage] dispatch resize for recompute'); } catch {}
      });
    });
  };
  const [heroHeight, setHeroHeight] = useState<number>(i18nCurrentLanguage === 'zh' ? 460 : 500);
  const [denseInfo, setDenseInfo] = useState<boolean>(false);
  const [infoTop, setInfoTop] = useState<number>(0);
  const hasTypeTags = (editFormData.typeTags?.length || 0) > 0;
  const hasSkills = (editFormData.skills?.length || 0) > 0;
  // 随机渐变背景（无背景图片时使用）
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
    'bg-gradient-to-br from-orange-400 via-red-500 to-pink-600'
  ];
  const heroBgClassRef = useRef<string>(gradientBackgrounds[Math.floor(Math.random() * gradientBackgrounds.length)]);

  useEffect(() => {
    const computeDensity = () => {
      // 依据标签与技能数量、姓名长度粗略判定紧凑/放宽
      const tagCount = (editFormData.typeTags?.length || 0) + (editFormData.skills?.length || 0);
      const nameLen = (editFormData.name || '').length;
      // 阈值：标签多或名字长时使用紧凑布局
      setDenseInfo(tagCount >= 8 || nameLen >= 10);
    };
    computeDensity();
  }, [editFormData]);

  useLayoutEffect(() => {
    const recomputeHero = () => {
      let infoH = 0;
      if (infoRef.current) {
        const el = infoRef.current as HTMLElement;
        infoH = el.offsetHeight;
        // 把最后一个子元素的 margin-bottom 也计入测量，避免视觉高度与测量不一致
        const lastChild = el.lastElementChild as HTMLElement | null;
        if (lastChild) {
          const mb = parseFloat(getComputedStyle(lastChild).marginBottom || '0');
          if (!Number.isNaN(mb)) infoH += mb;
        }
      }
      // 头像参数：位置与尺寸
      const avatarTop = compactHero ? 56 : 40; // tailwind: top-14=56px, top-10=40px
      const avatarSize = 120; // 120px
      const bottomPadding = 12; // 与 pb-3 对齐
      const fixedGap = 16; // 头像与信息之间的固定间距
      const computedInfoTop = avatarTop + avatarSize + fixedGap;
      setInfoTop(computedInfoTop);
      // 计算需要的高度：信息区顶部 + 信息区高度 + 底部内边距，确保至少包含头像区域
      const needed = Math.max(avatarTop + avatarSize + fixedGap, computedInfoTop + infoH + bottomPadding);
      setHeroHeight(needed);
    };

    // 初次与数据变化后计算
    recomputeHero();
    // 再延时一次防止首帧字体/图片尚未就绪
    const t = setTimeout(recomputeHero, 50);

    // 监听窗口尺寸变化
    const onResize = () => recomputeHero();
    window.addEventListener('resize', onResize);

    // 监听信息块尺寸变化（标签换行、文案长度变化、按钮显隐等）
    let ro: ResizeObserver | null = null;
    if (typeof ResizeObserver !== 'undefined' && infoRef.current) {
      ro = new ResizeObserver(() => {
        // 在下一帧计算，避免抖动
        requestAnimationFrame(recomputeHero);
        try { console.log('[ProfilePage] ResizeObserver: info changed'); } catch {}
      });
      ro.observe(infoRef.current);
    }

    // 部分环境中字体/图片加载后会引起尺寸变化，load 再计算一次
    const onLoad = () => recomputeHero();
    window.addEventListener('load', onLoad);

    return () => {
      window.removeEventListener('resize', onResize);
      window.removeEventListener('load', onLoad);
      if (ro && infoRef.current) ro.unobserve(infoRef.current);
      clearTimeout(t);
    };
  }, [compactHero, i18nCurrentLanguage, editFormData]);

  const calculateAge = (dateStr?: string) => {
    if (!dateStr) return undefined as number | undefined;
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return undefined;
    const today = new Date();
    let age = today.getFullYear() - d.getFullYear();
    const m = today.getMonth() - d.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < d.getDate())) age--;
    return age >= 0 ? age : undefined;
  };
  const displayAge = calculateAge(editFormData.birthday);

  // 主页头像立即更新处理
  const handleAvatarAddTop = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const f = files[0];
    if (!f.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = typeof reader.result === 'string' ? reader.result : '';
      if (!dataUrl) return;
      setEditFormData(prev => ({ ...prev, avatar: dataUrl }));
    };
    reader.readAsDataURL(f);
  };

  // 英文日期格式化（将"YYYY年M月"转换为 "Mon YYYY"）
  const formatMonthYearEn = (val?: string) => {
    if (!val) return '';
    const m = val.match(/^(\d{4})年(\d{1,2})月$/);
    if (m) {
      const y = parseInt(m[1], 10);
      const mo = parseInt(m[2], 10) - 1;
      const d = new Date(y, mo, 1);
      try {
        return d.toLocaleString('en-US', { month: 'short', year: 'numeric' });
      } catch {}
      return `${d.toDateString().split(' ')[1]} ${y}`;
    }
    return val;
  };

  // 恢复完整资料（跨页面保持）
  useEffect(() => {
    try {
      const saved = localStorage.getItem('profile_full_data');
      if (saved) {
        const parsed = JSON.parse(saved);
        setEditFormData(prev => ({
          ...prev,
          ...parsed,
          // 防止损坏的数据覆盖为非数组
          typeTags: Array.isArray(parsed?.typeTags) ? parsed.typeTags : prev.typeTags,
          skills: Array.isArray(parsed?.skills) ? parsed.skills : prev.skills,
          media: Array.isArray(parsed?.media) ? parsed.media : prev.media,
          gender: parsed?.gender || prev.gender,
        }));
      }
    } catch {}
  }, []);

  // 保存完整资料
  useEffect(() => {
    try {
      localStorage.setItem('profile_full_data', JSON.stringify(editFormData));
    } catch {}
  }, [editFormData]);

  // Basic 套餐强制对齐：若已存在超过 2 张公开项目，自动移动多余的到卡槽
  useEffect(() => {
    if (planLevel !== 'Basic') return;
    setInitiatedProjects(prev => {
      if (!Array.isArray(prev) || prev.length <= 2) return prev;
      const sorted = [...prev].sort((a, b) => ((b.createdAt || 0) - (a.createdAt || 0)));
      const keep = sorted.slice(0, 2);
      const extras = sorted.slice(2).map(p => ({ ...p, autoArchived: true, archivedAt: Date.now() }));
      if (extras.length > 0) {
        setArchivedProjects(ap => {
          const exists = new Set(ap.map(x => x.id));
          const merged = [...ap, ...extras.filter(x => !exists.has(x.id))];
          return merged;
        });
      }
      return keep;
    });
  }, [planLevel, initiatedProjects.length]);

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: scrollbarStyle }} />
      <div 
        className="h-full bg-white overflow-hidden relative"
      >
        {showBackHeader && (
          <div className="h-[90px] flex items-center justify-between px-4 border-b border-[#E8EDF2] bg-[#FAFAFA] absolute top-0 left-0 right-0 z-10">
            <button onClick={onBack} className="p-2">
              <ArrowLeft size={24} className="text-blue-600" />
            </button>
            <h1 className="font-semibold">{t('profileDetails') || '个人资料'}</h1>
            <div className="w-10" />
          </div>
        )}
        {/* Scrollable Content */}
        <div 
          ref={scrollContainerRef}
          className="overflow-y-auto overflow-x-hidden scrollbar-hide" 
          style={{ 
            scrollBehavior: 'smooth',
            height: showBackHeader ? '572px' : '662px',
            marginTop: showBackHeader ? '90px' : '0px'
          }}
        >
          {/* Hero Section */}
          <div className={`relative w-full`} style={{ height: heroHeight, transition: 'height 200ms ease' }} ref={heroRef}>
            {/* Background Image / Gradient */}
            <div className="absolute inset-0">
              {(editFormData.media && editFormData.media[0]) ? (
                <ImageWithFallback
                  src={editFormData.media[0]}
                  alt="Profile background"
                  className="w-full h-full object-cover"
                  onLoad={() => { bgImgLoadedRef.current = true; try { console.log('[ProfilePage] bg image loaded'); } catch {}; requestRecompute(); }}
                />
              ) : (
                <div className={`w-full h-full ${heroBgClassRef.current}`} />
              )}
              <div className="absolute inset-0 bg-black/50" />
            </div>
            
            {/* Top-left Back Button for chat -> profile navigation (no header bar) */}
            {compactHero && (
              <button
                onClick={onBack}
                className="absolute top-4 left-4 z-20 p-2 bg-black/40 rounded-full text-white hover:bg-black/60 transition-colors"
                aria-label="返回"
              >
                <ArrowLeft size={22} />
              </button>
            )}
            
            {/* Profile Avatar */}
            <div className={`absolute left-1/2 transform -translate-x-1/2 ${compactHero ? 'top-14' : 'top-10'} w-[120px] h-[120px]`}>
              <ImageWithFallback
                key={editFormData.avatar || 'default-avatar'}
                src={editFormData.avatar || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face'}
                alt="Profile avatar"
                className="w-full h-full rounded-full object-cover border-4 border-white"
                onLoad={() => { avatarLoadedRef.current = true; try { console.log('[ProfilePage] avatar image loaded'); } catch {}; requestRecompute(); }}
              />
              <input
                id="profile-avatar-input"
                type="file"
                accept="image/*"
                onChange={(e) => { handleAvatarAddTop(e.target.files); try { if (e.target) (e.target as HTMLInputElement).value = ''; } catch {} }}
                className="hidden"
              />
              <label
                htmlFor="profile-avatar-input"
                className="hidden"
                title={i18nCurrentLanguage === 'en' ? 'Change avatar' : '更换头像'}
              >
                {/* Camera button hidden */}
              </label>
            </div>

            {/* Profile Info */}
            <div className="absolute left-0 right-0 px-6 pb-3" ref={infoRef} style={{ top: infoTop }}>
              <div className={`text-center ${denseInfo ? 'mb-3' : 'mb-4'}`}>
                {/* Name and Gender */}
                <div className={`flex items-center justify-center gap-2 mb-1`}>
                  <h1 className="text-white text-3xl font-bold" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>{editFormData.name}{typeof displayAge === 'number' ? `, ${displayAge}` : ''}</h1>
                  <button
                    type="button"
                    onClick={() => setShowPlanModal(true)}
                    className={`inline-flex items-center h-6 px-2 rounded-full text-xs font-semibold ${planLevel === 'Basic' ? 'bg-white/20 text-white' : planLevel === 'Pro' ? 'bg-amber-400 text-white' : 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-white'} hover:opacity-90 transition`}
                  >
                    {planLevel}
                  </button>
                  {editFormData.gender !== 'Non-binary' && (
                    <div className="w-6 h-6">
                      <svg viewBox="0 0 24 24" fill="none">
                        <path d={svgPaths.male} stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                  )}
                </div>
                
                {/* Location */}
                <div className={`flex items-center justify-center gap-1 ${(!hasTypeTags && !hasSkills) ? 'mb-1' : (denseInfo ? 'mb-2' : 'mb-3')}`}>
                  <MapPin size={16} className="text-white" />
                  <span className="text-white text-sm" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                    {(() => {
                      const lang = i18nCurrentLanguage || 'zh';
                      const loc = editFormData.location;
                      if (lang === 'en') {
                        if (loc === '深圳, 中国') return 'Shenzhen, China';
                      }
                      return loc;
                    })()}
                  </span>
                </div>
                
                {/* Tags */}
                {hasTypeTags && (
                  <div className={`flex flex-wrap gap-2 justify-center ${denseInfo ? 'mb-1' : (compactHero ? 'mb-2' : 'mb-3')}`}>
                    {editFormData.typeTags.map((tag: string, index: number) => {
                      const lang = i18nCurrentLanguage || 'zh';
                      const tagMap: Record<string, string> = {
                        '寻找合作者': 'Looking for collaborators',
                        '正在寻找项目': 'Looking for projects',
                        '招聘伙伴': 'Hiring partners',
                        '投资人': 'Investor',
                        '导师/顾问': 'Mentor/Advisor',
                        '开放合作': 'Open to collaboration'
                      };
                      const display = lang === 'en' ? (tagMap[tag] || tag) : tag;
                      return (
                        <Badge key={`type-${index}`} variant="secondary" className="bg-white text-[#0055F7] border-white rounded-full font-semibold">
                          {display}
                        </Badge>
                      );
                    })}
                  </div>
                )}
                
                <div className={`flex flex-wrap gap-2 justify-center ${!hasTypeTags ? 'mb-1' : (denseInfo ? 'mb-2' : (compactHero ? 'mb-3' : 'mb-4'))}`}>
                  {editFormData.skills.map((skill: string, index: number) => (
                    <Badge key={`skill-${index}`} variant="secondary" className="bg-white/20 text-white border-white/30">
                      {skill}
                    </Badge>
                  ))}
                </div>

                {/* Edit Profile Button */}
                {!isReadOnly && (
                  <div className="flex justify-center">
                    <Button 
                      onClick={() => setIsEditing(true)}
                      className="bg-[#0055F7] hover:bg-[#0043C4] text-white px-6 py-2 rounded-full flex items-center gap-2 w-[203px] justify-center font-bold" 
                      style={{ fontFamily: 'Instrument Sans, sans-serif' }}
                    >
                      <span>{t('editProfile') || 'Edit Profile'}</span>
                      <Edit3 size={16} />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Content Section */}
          <div 
            ref={contentSectionRef}
            className="bg-white rounded-t-[30px] relative -mt-6 z-10"
            style={{ minHeight: '500px' }}
          >
            {/* Tab Buttons */}
            <div className="px-4 pt-4 pb-1">
              <div className="flex gap-4 max-w-sm mx-auto">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`flex-1 py-3 px-6 rounded-lg font-bold text-sm transition-colors ${
                    activeTab === 'profile'
                      ? 'bg-[#0055F7] text-white'
                      : 'bg-transparent text-gray-600 hover:bg-gray-100'
                  }`}
                  style={{ fontFamily: 'Instrument Sans, sans-serif' }}
                >
                  {t('profile') || '个人资料'}
                </button>
                <button
                  onClick={() => setActiveTab('project')}
                  className={`flex-1 py-3 px-6 rounded-lg font-bold text-sm transition-colors ${
                    activeTab === 'project'
                      ? 'bg-[#0055F7] text-white'
                      : 'bg-transparent text-gray-600 hover:bg-gray-100'
                  }`}
                  style={{ fontFamily: 'Instrument Sans, sans-serif' }}
                >
                  {t('projects') || '项目经历'}
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="px-6 pb-10">
              {activeTab === 'profile' ? (
                <div className="space-y-6">
                  {/* Bio Quote */}
                  {editFormData.bio && (
                  <div className="relative">
                    <div style={{ 
                      fontSize: '3.75rem', 
                      fontFamily: '"Impact"', 
                      fontWeight: 'normal', 
                      color: '#0055F7', 
                      lineHeight: '1', 
                      marginBottom: '0.25rem' 
                    }}>
                      "
                    </div>
                    <div className="text-sm text-gray-700 leading-relaxed pl-8 -mt-6 font-bold" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                      {editFormData.bio.split('\n').map((line: string, index: number) => (
                        <React.Fragment key={index}>
                          {line}
                          {index < editFormData.bio.split('\n').length - 1 && <br />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                  )}

                  {/* Objective */}
                  {editFormData.objective && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-3" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>{t('goals') || 'Goals'}</h3>
                    <p className="text-sm text-gray-700 leading-relaxed" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                      {editFormData.objective.split('\n').map((line: string, index: number) => (
                        <React.Fragment key={index}>
                          {line}
                          {index < editFormData.objective.split('\n').length - 1 && <br />}
                        </React.Fragment>
                      ))}
                    </p>
                  </div>
                  )}

                  {/* Looking For */}
                  {editFormData.lookingFor && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-3" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>{t('lookingFor') || 'Looking For'}</h3>
                    <p className="text-sm text-gray-700 leading-relaxed" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                      {editFormData.lookingFor}
                    </p>
                  </div>
                  )}

                  {/* Media */}
                  {(sampleImages && sampleImages.length > 0) && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>{t('media') || 'Media'}</h3>
                    
                    {/* First row */}
                    <div className="grid grid-cols-3 gap-2 mb-2">
                      {sampleImages.slice(0, 3).map((img, index) => (
                        <div key={index} className="aspect-[3/4]">
                          <ImageWithFallback
                            src={img}
                            alt={`Media ${index + 1}`}
                            className="w-full h-full object-cover rounded-lg"
                          />
                        </div>
                      ))}
                    </div>
                    
                    {/* Second row */}
                    <div className="grid grid-cols-3 gap-2">
                      {sampleImages.slice(3, 6).map((img, index) => (
                        <div key={index + 3} className="aspect-[3/4]">
                          <ImageWithFallback
                            src={img}
                            alt={`Media ${index + 4}`}
                            className="w-full h-full object-cover rounded-lg"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                  )}
                </div>
              ) : (
                <div className="space-y-8">
                  {/* 发起的项目 */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                      {t('initiatedProjects') || '发起的项目'} ({initiatedProjects.length})
                    </h3>
                    <div className="relative">
                      <Swiper
                        spaceBetween={24}
                        slidesPerView="auto"
                        className="project-swiper"
                        style={{ paddingLeft: '0', paddingRight: '0' }}
                        allowTouchMove={true}
                        grabCursor={true}
                        slidesPerGroup={1}
                        watchSlidesProgress={true}
                      >
                        {initiatedProjects.map((project) => (
                          <SwiperSlide key={project.id} style={{ width: '357px' }}>
                            <ProjectCard 
                              project={project} 
                              onClick={() => handleProjectClick(project)}
                              onLongPressStart={() => handleLongPressStart(project)}
                              onLongPressEnd={handleLongPressEnd}
                            />
                          </SwiperSlide>
                        ))}
                      </Swiper>
                    </div>
                  </div>

                  {/* 合作的项目 */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                      {t('collaboratedProjects') || '合作的项目'} ({collaboratedProjects.length})
                    </h3>
                    <div className="relative">
                      <Swiper
                        spaceBetween={24}
                        slidesPerView="auto"
                        className="project-swiper"
                        style={{ paddingLeft: '0', paddingRight: '0' }}
                        allowTouchMove={true}
                        grabCursor={true}
                        slidesPerGroup={1}
                        watchSlidesProgress={true}
                      >
                        {collaboratedProjects.map((project) => (
                          <SwiperSlide key={project.id} style={{ width: '357px' }}>
                            <ProjectCard 
                              project={project} 
                              isCollaboration={true}
                              onClick={() => handleProjectClick(project)}
                              onLongPressStart={undefined} 
                              onLongPressEnd={undefined}
                            />
                          </SwiperSlide>
                        ))}
                      </Swiper>
                    </div>
                  </div>

                  {/* 归档卡槽：展示已存档的卡片（灰色蒙版），自动归档的显示锁图标 */}
                  {archivedProjects.length > 0 && (
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 mb-4" style={{ fontFamily: 'Instrument Sans, sans-serif' }}>
                        {i18nCurrentLanguage === 'en' ? 'Card Slot(archived)' : '卡槽(归档的卡片)'} ({archivedProjects.length})
                      </h3>
                      <div className="grid grid-cols-1 gap-4">
                        {archivedProjects.map((project) => (
                          <div key={`archslot-${project.id}`} className="relative w-[357px]">
                            <ProjectCard 
                              project={project} 
                              isCollaboration={!!project.role}
                              onClick={() => handleProjectClick(project)}
                              onLongPressStart={() => handleLongPressStart(project)}
                              onLongPressEnd={handleLongPressEnd}
                              overlayChild={
                                <>
                                  <div className="absolute inset-0 bg-black/50 rounded-[14px] pointer-events-none" />
                                  {project.autoArchived && (
                                    <div className="absolute top-2 right-2 bg-white/90 rounded-full w-8 h-8 flex items-center justify-center shadow pointer-events-none">
                                      <svg className="w-4 h-4 text-gray-800" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M7 11V7a5 5 0 0110 0v4" />
                                        <rect x="5" y="11" width="14" height="10" rx="2" />
                                      </svg>
                                    </div>
                                  )}
                                </>
                              }
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 项目详情弹窗 - 使用与主页面完全一致的样式 */}
      <AnimatePresence>
        {selectedProject && !isReadOnly && (
          <ProjectDetailView
            project={selectedProject}
            onClose={() => setSelectedProject(null)}
            suppressFirstTap={false}
            isFavorite={false}
          />
        )}
      </AnimatePresence>

      {/* 长按菜单弹窗 */}
      <AnimatePresence>
        {!isReadOnly && showLongPressMenu && longPressedProject && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowLongPressMenu(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 mx-4 w-80 shadow-2xl"
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 50 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* 项目信息 */}
              <div className="text-center mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-2">{longPressedProject.title}</h3>
                <p className="text-sm text-gray-600">{t('chooseAction') || '选择要执行的操作'}</p>
              </div>

              {/* 操作按钮 */}
              <div className="space-y-3">
                <button
                  onClick={() => handleLongPressAction('edit')}
                  className="w-full py-3 px-4 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Edit3 size={18} />
                  {t('editProject') || '编辑项目'}
                </button>
                {(!longPressedProject.autoArchived) && (
                <button
                  onClick={() => handleLongPressAction('archive')}
                  className="w-full py-3 px-4 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-14 0h14" />
                  </svg>
                  {archivedProjects.find(p => p.id === longPressedProject.id) ? (t('unarchiveProject') || '取消存档') : (t('archiveProject') || '存档项目')}
                </button>
                )}
                <button
                  onClick={() => handleLongPressAction('delete')}
                  className="w-full py-3 px-4 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M3 4 7h16" />
                  </svg>
                  {t('deleteProject') || '删除项目'}
                </button>
              </div>

              {/* 取消按钮 */}
              <button
                onClick={() => setShowLongPressMenu(false)}
                className="w-full py-3 px-4 mt-4 text-gray-500 hover:text-gray-700 font-medium transition-colors"
              >
                {t('cancel') || '取消'}
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 删除确认弹窗 */}
      <AnimatePresence>
        {!isReadOnly && showDeleteConfirm && deletingProject && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowDeleteConfirm(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 mx-4 w-80 shadow-2xl"
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 50 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* 警告图标 */}
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{t('confirmDelete') || '确认删除'}</h3>
                <p className="text-sm text-gray-600 mb-2">{t('project') || '项目'}：{deletingProject.title}</p>
                <p className="text-sm text-red-600 font-medium">{t('cannotUndo') || '删除后无法恢复！'}</p>
              </div>

              {/* 操作按钮 */}
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="flex-1 py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  {t('cancel') || '取消'}
                </button>
                <button
                  onClick={handleConfirmDelete}
                  className="flex-1 py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
                >
                  {t('confirmDelete') || '确认删除'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 编辑个人资料弹窗 */}
      <AnimatePresence>
        {!isReadOnly && isEditing && (
          <ProfileEditPage
            formData={editFormData}
            onSave={(data) => {
              setEditFormData({
                ...editFormData,
                name: String(data.name || '').trim(),
                birthday: data.birthday || '',
                gender: data.gender || editFormData.gender,
                location: data.location || '',
                bio: data.bio || '',
                objective: data.objective || '',
                lookingFor: data.lookingFor || '',
                typeTags: Array.isArray(data.typeTags) ? data.typeTags : [],
                skills: Array.isArray(data.skills) ? data.skills : [],
                media: Array.isArray(data.media) ? data.media : [],
                avatar: data.avatar || editFormData.avatar
              });
              try { localStorage.setItem('profile_full_data', JSON.stringify({
                ...editFormData,
                name: String(data.name || '').trim(),
                birthday: data.birthday || '',
                gender: data.gender || editFormData.gender,
                location: data.location || '',
                bio: data.bio || '',
                objective: data.objective || '',
                lookingFor: data.lookingFor || '',
                typeTags: Array.isArray(data.typeTags) ? data.typeTags : [],
                skills: Array.isArray(data.skills) ? data.skills : [],
                media: Array.isArray(data.media) ? data.media : [],
                avatar: data.avatar || editFormData.avatar
              })); } catch {}
              setIsEditing(false);
            }}
            onCancel={() => setIsEditing(false)}
          />
        )}
      </AnimatePresence>

      {/* Plan purchase modal */}
      <AnimatePresence>
        {showPlanModal && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowPlanModal(false)}
          >
            <motion.div
              className="bg-white rounded-2xl w-[360px] max-w-[92vw] p-5 shadow-2xl"
              initial={{ scale: 0.95, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.96, y: 10, opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-bold mb-2">{i18nCurrentLanguage === 'en' ? 'Choose your plan' : '选择你的计划'}</h3>
              {/* Current plan summary at top */}
              <div className="mb-3 text-xs text-gray-600">
                {i18nCurrentLanguage === 'en' ? 'Current plan:' : '当前计划：'} <span className="font-semibold">{i18nCurrentLanguage === 'en' ? planLevel : (planLevel === 'Basic' ? '基础版' : planLevel === 'Pro' ? '高级版' : 'AI增强版')}</span>
                {planLevel !== 'Basic' && planExpiry && (
                  <>
                    <span className="mx-1">·</span>
                    {i18nCurrentLanguage === 'en' ? 'Expires:' : '到期：'} {new Date(planExpiry).toLocaleDateString(i18nCurrentLanguage === 'en' ? 'en-CA' : 'zh-CN')}
                  </>
                )}
              </div>

              <div className="space-y-3">
                {/* Basic */}
                <button
                  onClick={() => { setPlanLevel('Basic'); setPlanExpiry(null); setNeedsPurchase(false); }}
                  className={`w-full text-left border rounded-xl p-3 hover:bg-gray-50 ${planLevel === 'Basic' ? 'border-blue-500' : 'border-gray-200'}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Basic' : '基础版'}</div>
                    <div className="text-xs text-gray-500">{i18nCurrentLanguage === 'en' ? 'Free' : '免费'}</div>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    {i18nCurrentLanguage === 'en'
                      ? '30 swipes/day · 2 active posts · 1 agent search/day'
                      : '30个滑动次数/每天 · 2个可公开项目 · 1个AI agent搜索次数/每天'}
                  </div>
                </button>

                {/* Pro */}
                <div className={`w-full border rounded-xl p-3 ${planLevel === 'Pro' ? 'border-blue-500' : 'border-gray-200'}`}>
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Pro' : '高级版'}</div>
                    <div className="text-xs text-gray-500">
                      {i18nCurrentLanguage === 'en' ? '4.99￥/month · 29.9￥/year' : '4.99￥/月 · 29.9￥/年'}
                    </div>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    {i18nCurrentLanguage === 'en'
                      ? 'unlimited swipes/day · unlimited active posts · 1 agent search/day'
                      : '不限滑动次数/每天 · 无限可公开项目 · 1个AI agent搜索次数/每天'}
                  </div>
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={() => { setPlanLevel('Pro'); setBillingCycle('monthly'); setPlanExpiry(Date.now() + 1000*60*60*24*30); setNeedsPurchase(true); }}
                      className={`flex-1 text-sm rounded-lg px-3 py-2 border ${planLevel==='Pro' && billingCycle==='monthly' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}
                    >{i18nCurrentLanguage === 'en' ? 'Choose monthly' : '选择月付'}</button>
                    <button
                      onClick={() => { setPlanLevel('Pro'); setBillingCycle('yearly'); setPlanExpiry(Date.now() + 1000*60*60*24*365); setNeedsPurchase(true); }}
                      className={`flex-1 text-sm rounded-lg px-3 py-2 border ${planLevel==='Pro' && billingCycle==='yearly' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}
                    >{i18nCurrentLanguage === 'en' ? 'Choose yearly' : '选择年付'}</button>
                  </div>
                </div>

                {/* AI-Powered */}
                <div className={`w-full border rounded-xl p-3 ${planLevel === 'Ai-Powered' ? 'border-blue-500' : 'border-gray-200'}`}>
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Ai-Powered' : 'AI增强版'}</div>
                    <div className="text-xs text-gray-500">{i18nCurrentLanguage === 'en' ? '19.9￥/month · 69.9￥/year' : '19.9￥/月 · 69.9￥/年'}</div>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    {i18nCurrentLanguage === 'en' ? 'all unlimited' : '全部次数不限'}
                  </div>
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={() => { setPlanLevel('Ai-Powered'); setBillingCycle('monthly'); setPlanExpiry(Date.now() + 1000*60*60*24*30); setNeedsPurchase(true); }}
                      className={`flex-1 text-sm rounded-lg px-3 py-2 border ${planLevel==='Ai-Powered' && billingCycle==='monthly' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}
                    >{i18nCurrentLanguage === 'en' ? 'Choose monthly' : '选择月付'}</button>
                    <button
                      onClick={() => { setPlanLevel('Ai-Powered'); setBillingCycle('yearly'); setPlanExpiry(Date.now() + 1000*60*60*24*365); setNeedsPurchase(true); }}
                      className={`flex-1 text-sm rounded-lg px-3 py-2 border ${planLevel==='Ai-Powered' && billingCycle==='yearly' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}
                    >{i18nCurrentLanguage === 'en' ? 'Choose yearly' : '选择年付'}</button>
                  </div>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-end">
                <button onClick={() => setShowPlanModal(false)} className="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700">
                  { (planLevel !== 'Basic' && needsPurchase) ? (i18nCurrentLanguage === 'en' ? 'Purchase' : '去购买') : (i18nCurrentLanguage === 'en' ? 'Done' : '完成') }
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </>
  );
} 