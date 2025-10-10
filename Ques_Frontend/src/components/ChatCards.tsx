import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo, useMotionValue, useTransform, animate } from 'framer-motion';
import { Share2, ChevronDown, ChevronUp, Gift } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

interface Profile {
  id: string;
  name: string;
  age: string;
  gender: string;
  avatar: string;
  location: string;
  hobbies: string[];
  languages: string[];
  skills: string[];
  resources: string[];
  projects: { 
    title: string; 
    role: string; 
    description: string; 
    referenceLinks: string[] 
  }[];
  goals: string[];
  demands: string[];
  institutions: { 
    name: string; 
    role: string; 
    description: string; 
    verified: boolean;
  }[];
  university?: {
    name: string;
    verified: boolean;
  };
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  whyMatch: string;
  receivesLeft?: number;
}

interface ChatCardsProps {
  profiles: Profile[];
  onSwipeLeft: (profile: Profile) => void;
  onSwipeRight: (profile: Profile) => void;
  onAllCardsFinished?: () => void;
  onGiftReceives?: (name: string, amount: number) => void;
}

export default function ChatCards({ profiles, onSwipeLeft, onSwipeRight, onAllCardsFinished, onGiftReceives }: ChatCardsProps) {
  const { t } = useLanguage();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showFullProfile, setShowFullProfile] = useState(false);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
  const [dragDirection, setDragDirection] = useState<'left' | 'right' | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [giftAmount, setGiftAmount] = useState('');
  const constraintsRef = useRef(null);
  
  // Motion values for smooth dragging
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-500, -200, 0, 200, 500], [-45, -20, 0, 20, 45]); // Rotate based on drag distance
  
  // Reset motion values when card changes
  useEffect(() => {
    x.set(0);
  }, [currentIndex, x]);
  
  // Check if all cards are finished
  useEffect(() => {
    if ((profiles.length === 0 || currentIndex >= profiles.length) && onAllCardsFinished) {
      onAllCardsFinished();
    }
  }, [currentIndex, profiles.length, onAllCardsFinished]);

  if (profiles.length === 0 || currentIndex >= profiles.length) {
    return null;
  }

  const currentProfile = profiles[currentIndex];

  const handleDragStart = (event: any, info: PanInfo) => {
    setDragStart({ x: info.point.x, y: info.point.y });
    setIsDragging(false);
  };

  const handleDrag = (event: any, info: PanInfo) => {
    const { offset, point } = info;
    const deltaX = Math.abs(point.x - dragStart.x);
    const deltaY = Math.abs(point.y - dragStart.y);
    
    // Determine if this is horizontal drag or vertical scroll
    if (!isDragging && (deltaX > 10 || deltaY > 10)) {
      // If horizontal movement is more dominant, treat as drag
      if (deltaX > deltaY * 1.5) {
        setIsDragging(true);
      }
    }
    
    // Only show drag feedback if we're actually dragging horizontally
    if (isDragging && Math.abs(offset.x) > 20) {
      setDragDirection(offset.x > 0 ? 'right' : 'left');
    } else if (!isDragging) {
      setDragDirection(null);
    }
  };

  const handleDragEnd = (event: any, info: PanInfo) => {
    const { offset, velocity } = info;
    
    // Only process swipe if we were actually dragging (not scrolling)
    // Lower threshold for more responsive swiping like Tinder
    if (isDragging && (Math.abs(offset.x) > 80 || Math.abs(velocity.x) > 400)) {
      // Set exit direction immediately for instant response
      const direction = offset.x > 0 ? 'right' : 'left';
      
      // Trigger swipe callback first
      if (direction === 'right') {
        onSwipeRight(currentProfile);
      } else {
        onSwipeLeft(currentProfile);
      }
      
      // Animate the x motion value directly for smooth exit (rotate will follow automatically)
      animate(x, direction === 'left' ? -500 : 500, {
        duration: 0.3,
        ease: [0.32, 0.72, 0, 1]
      });
      
      // Set exit direction for opacity and scale animation
      setExitDirection(direction);
      setDragDirection(null);
      setIsDragging(false);
      
      // Update state after animation completes
      setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
        setExitDirection(null);
        setShowFullProfile(false);
      }, 300); // Match animation duration
    } else {
      setDragDirection(null);
      setIsDragging(false);
      // Animate back to center if swipe was not successful (rotate will follow automatically)
      animate(x, 0, {
        type: "spring",
        damping: 30,
        stiffness: 400
      });
    }
  };

  const handleShareProfile = () => {
    console.log('Sharing profile:', currentProfile.name);
  };

  const toggleExtendedProfile = () => {
    setShowFullProfile(!showFullProfile);
  };

  const openGiftModal = (profile: Profile) => {
    setSelectedProfile(profile);
    setGiftAmount('');
    setShowGiftModal(true);
  };

  const handleGiftConfirm = () => {
    if (selectedProfile && giftAmount && onGiftReceives) {
      const amount = parseInt(giftAmount);
      if (amount > 0) {
        onGiftReceives(selectedProfile.name, amount);
        setShowGiftModal(false);
        setSelectedProfile(null);
      }
    }
  };

  const nextProfiles = profiles.slice(currentIndex + 1, currentIndex + 3); // Get next 2 profiles for stack effect

  return (
    <div className="relative w-full flex flex-col items-center">
      <div className="relative" ref={constraintsRef} style={{ width: '300px', height: '420px' }}>
        {/* Background cards (stack effect) - Show next 2 cards */}
        {nextProfiles.map((profile, index) => (
          <motion.div
            key={`bg-${profile.id}`}
            className="absolute"
            style={{ 
              width: '300px', 
              height: '400px',
              top: (index + 1) * 10,
              left: 0,
              zIndex: nextProfiles.length - index
            }}
            initial={false}
            animate={{ 
              scale: 0.96 - (index * 0.02), 
              y: (index + 1) * 10
            }}
            transition={{ 
              type: "spring", 
              damping: 25, 
              stiffness: 300
            }}
          >
            <div 
              className="relative bg-white rounded-2xl overflow-hidden w-full h-full"
              style={{
                boxShadow: index === 0 
                  ? '0 8px 24px rgba(0, 0, 0, 0.15), 0 2px 8px rgba(0, 0, 0, 0.1)'
                  : '0 12px 32px rgba(0, 0, 0, 0.2), 0 4px 12px rgba(0, 0, 0, 0.15)'
              }}
            >
              {/* Background card - full collapsed view (non-interactive) */}
              <div className="relative w-full h-full pointer-events-none">
                {/* Profile Background */}
                <div className="relative w-full h-full flex items-center justify-center">
                  <div className="text-9xl select-none" style={{ fontSize: '12rem', lineHeight: '1' }}>
                    {profile.avatar}
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                </div>

                {/* Bottom content area */}
                <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                  <div className="flex items-center justify-between mb-2">
                    <h2 className="text-lg font-bold">
                      {profile.name}
                    </h2>
                    <div className="flex gap-2">
                      <div className="p-2 bg-white/20 backdrop-blur-sm rounded-full">
                        <Share2 size={16} />
                      </div>
                      <div className="p-2 bg-blue-500 rounded-full">
                        <ChevronDown size={16} />
                      </div>
                    </div>
                  </div>
                  <p className="text-white/90 text-xs line-clamp-1 mb-3">
                    {profile.oneSentenceIntro || profile.bio}
                  </p>
                  
                  {/* Receives Bar */}
                  <div className="absolute bottom-4 left-0 right-0 px-6 text-white text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 flex-1">
                        <span className="font-medium">{t('cards.receivesLeft')}</span>
                        <span className="font-bold">{profile.receivesLeft || 0}</span>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <div className="w-16 h-2 bg-gray-400/80 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 rounded-full transition-all duration-300" 
                            style={{ width: `${Math.min((profile.receivesLeft || 0) / 50 * 100, 100)}%` }}
                          />
                        </div>
                        <div className="p-1.5 rounded-full bg-white/30">
                          <Gift size={12} className="text-white" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
        
        <AnimatePresence>
          {/* Main Card Container */}
          <motion.div
            key={currentProfile.id}
            className="absolute top-0 left-0 bg-white rounded-2xl overflow-hidden"
            style={{ 
              width: '300px', 
              height: '400px', 
              zIndex: exitDirection ? 50 : 10, // Higher z-index when exiting
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.3), 0 10px 20px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.1)',
              x: x, // Always use motion value
              rotate: rotate // Always use motion value
            }}
            initial={{ scale: 0.96, y: 10, opacity: 1 }}
            animate={exitDirection ? {
              opacity: 0,
              scale: 0.8,
              transition: { duration: 0.3, ease: [0.32, 0.72, 0, 1] }
            } : { 
              scale: 1, 
              y: 0, 
              opacity: 1,
              transition: { 
                type: "spring", 
                damping: 30, 
                stiffness: 400
              }
            }}
            exit={{
              opacity: 0,
              transition: { duration: 0.1 }
            }}
          >
            {/* Drag Area - only for collapsed view or non-scrollable areas when expanded */}
            {!exitDirection && !showFullProfile && (
              <motion.div
                className="absolute inset-0 cursor-grab active:cursor-grabbing z-10"
                drag="x"
                dragElastic={0}
                onDragStart={handleDragStart}
                onDrag={handleDrag}
                onDragEnd={handleDragEnd}
                style={{ x }}
                dragMomentum={false}
                whileDrag={{ scale: 1.02 }}
              />
            )}
            {!exitDirection && showFullProfile && (
              /* Drag Area for expanded view - only covers header, excludes scrollable content */
              <motion.div
                className="absolute top-0 left-0 right-0 cursor-grab active:cursor-grabbing z-10"
                style={{ height: '80px', x }} // Only cover the header area
                drag="x"
                dragElastic={0}
                onDragStart={handleDragStart}
                onDrag={handleDrag}
                onDragEnd={handleDragEnd}
                dragMomentum={false}
              />
            )}

            {/* Drag Feedback Overlays */}
            <motion.div
              className="absolute inset-0 bg-red-500/20 flex items-center justify-center z-20 pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: dragDirection === 'left' ? 1 : 0 }}
              transition={{ duration: 0.1 }}
            >
              <div className="text-6xl">✕</div>
            </motion.div>
            
            <motion.div
              className="absolute inset-0 bg-green-500/20 flex items-center justify-center z-20 pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: dragDirection === 'right' ? 1 : 0 }}
              transition={{ duration: 0.1 }}
            >
              <div className="text-6xl">💬</div>
            </motion.div>

            <AnimatePresence mode="wait">
              {!showFullProfile ? (
                /* Collapsed Card View */
                <motion.div
                  key="collapsed"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="relative w-full h-full"
                >
                  {/* Profile Background */}
                  <div className="relative w-full h-full flex items-center justify-center">
                    <div className="text-9xl select-none" style={{ fontSize: '12rem', lineHeight: '1' }}>
                      {currentProfile.avatar}
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                  </div>

                  {/* Bottom content area */}
                  <div className="absolute bottom-0 left-0 right-0 p-6 text-white z-30">
                    <div className="flex items-center justify-between mb-2">
                      <h2 className="text-lg font-bold">
                        {currentProfile.name}
                      </h2>
                      <div className="flex gap-2 relative z-50">
                        <button
                          onClick={handleShareProfile}
                          className="p-2 bg-white/20 backdrop-blur-sm rounded-full hover:bg-white/30 transition-colors relative z-50"
                        >
                          <Share2 size={16} />
                        </button>
                        <button
                          onClick={toggleExtendedProfile}
                          className="p-2 bg-blue-500 rounded-full hover:bg-blue-600 transition-colors relative z-50"
                        >
                          <ChevronDown size={16} />
                        </button>
                      </div>
                    </div>
                    <p className="text-white/90 text-xs line-clamp-1 mb-3">
                      {currentProfile.oneSentenceIntro || currentProfile.bio}
                    </p>
                    
                    {/* Receives Bar - integrated as last line in collapsed view */}
                    <div className="absolute bottom-4 left-0 right-0 px-6 text-white text-xs z-40">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 flex-1">
                          <span className="font-medium">{t('cards.receivesLeft')}</span>
                          <span className="font-bold">{currentProfile.receivesLeft || 0}</span>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <div className="w-16 h-2 bg-gray-400/80 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500 rounded-full transition-all duration-300" 
                              style={{ width: `${Math.min((currentProfile.receivesLeft || 0) / 50 * 100, 100)}%` }}
                            />
                          </div>
                          <button
                            onClick={() => openGiftModal(currentProfile)}
                            className="p-1.5 rounded-full bg-white/30 hover:bg-white/40 transition-colors z-50"
                            title="Gift Receives"
                          >
                            <Gift size={12} className="text-white" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                /* Expanded Card View */
                <motion.div
                  key="expanded"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="relative w-full h-full flex flex-col"
                >
                  {/* Header with avatar and basic info */}
                  <div className="bg-gray-50 p-4 border-b border-gray-200 flex-shrink-0 relative" style={{ height: '80px' }}>
                    <div className="flex items-center justify-between h-full">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
                          {currentProfile.avatar}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{currentProfile.name}</h3>
                          <p className="text-sm text-gray-600">{currentProfile.location} • {currentProfile.age}</p>
                        </div>
                      </div>
                      <div className="flex gap-2 relative z-50">
                        <button
                          onClick={handleShareProfile}
                          className="p-2 bg-white rounded-full shadow-sm hover:bg-gray-50 transition-colors relative z-50"
                        >
                          <Share2 size={16} className="text-gray-600" />
                        </button>
                        <button
                          onClick={toggleExtendedProfile}
                          className="p-2 bg-blue-500 rounded-full hover:bg-blue-600 transition-colors relative z-50"
                        >
                          <ChevronUp size={16} className="text-white" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Scrollable Content */}
                  <div 
                    className="flex-1 overflow-y-auto" 
                    style={{ height: 'calc(400px - 80px)' }}
                  >
                    <div className="p-4 space-y-4">
                      {/* Resources */}
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.resources')}</h4>
                        <div className="flex flex-wrap gap-1">
                          {currentProfile.resources.map((resource, index) => (
                            <span key={index} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                              {resource}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Skills */}
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.skills')}</h4>
                        <div className="flex flex-wrap gap-1">
                          {currentProfile.skills.map((skill, index) => (
                            <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Languages & Hobbies */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.languages')}</h4>
                          <div className="flex flex-wrap gap-1 overflow-x-hidden min-w-0">
                            {currentProfile.languages.map((language, index) => (
                              <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs max-w-full whitespace-normal break-all">
                                {language}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.hobbies')}</h4>
                          <div className="flex flex-wrap gap-1 overflow-x-hidden min-w-0">
                            {currentProfile.hobbies.map((hobby, index) => (
                              <span key={index} className="px-2 py-1 bg-pink-100 text-pink-800 rounded-full text-xs max-w-full whitespace-normal break-all">
                                {hobby}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Projects */}
                      {currentProfile.projects.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.projects')}</h4>
                          <div className="space-y-3">
                            {currentProfile.projects.map((project, index) => (
                              <div key={index} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                                <h5 className="font-medium text-gray-900 text-xs mb-1">{project.title}</h5>
                                <p className="text-blue-600 text-xs mb-1">{project.role}</p>
                                <p className="text-gray-700 text-xs mb-2 leading-relaxed">{project.description}</p>
                                {project.referenceLinks.length > 0 && (
                                  <div className="space-y-1">
                                    {project.referenceLinks.map((link, linkIndex) => (
                                      <a 
                                        key={linkIndex} 
                                        href={link} 
                                        className="text-xs text-blue-500 block hover:underline break-all"
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                      >
                                        {link}
                                      </a>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Goals & Demands */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.goals')}</h4>
                          <div className="space-y-1">
                            {currentProfile.goals.map((goal, index) => (
                              <p key={index} className="text-gray-700 text-xs">• {goal}</p>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.demands')}</h4>
                          <div className="space-y-1">
                            {currentProfile.demands.map((demand, index) => (
                              <p key={index} className="text-orange-600 text-xs">• {demand}</p>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Institutions */}
                      {currentProfile.institutions.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.institutions')}</h4>
                          <div className="space-y-3">
                            {currentProfile.institutions.map((institution, index) => (
                              <div key={index} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                                <h5 className="font-medium text-gray-900 text-xs mb-1">{institution.name}</h5>
                                <p className="text-blue-600 text-xs mb-1">{institution.role}</p>
                                <p className="text-gray-700 text-xs">{institution.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* University */}
                      {currentProfile.university && (
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">{t('cards.university')}</h4>
                          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
                            <div className="flex items-start justify-between gap-2 mb-1">
                              <h5 className="font-medium text-gray-900 text-xs leading-tight flex-1 min-w-0 pr-2">
                                {currentProfile.university.name}
                              </h5>
                              {currentProfile.university.verified && (
                                <span className="text-blue-600 text-xs font-medium bg-blue-100 px-2 py-1 rounded-full whitespace-nowrap flex-shrink-0 flex items-center gap-1">
                                  <span>🎓</span>
                                  <span>{t('cards.verified')}</span>
                                </span>
                              )}
                            </div>
                            <p className="text-blue-700 text-xs">{t('cards.currentUniversity')}</p>
                          </div>
                        </div>
                      )}

                      {/* Why We Match */}
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-gray-900 text-sm">{t('cards.whyMatch')}</h4>
                          <span 
                            className="text-white text-xs px-2 py-0.5 rounded-full font-medium"
                            style={{
                              background: 'linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%)',
                              backgroundImage: 'linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%)'
                            }}
                          >
                            AI
                          </span>
                        </div>
                        <p className="text-gray-700 text-xs leading-relaxed">{currentProfile.whyMatch}</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Gift Modal */}
      {showGiftModal && selectedProfile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl p-6 w-full max-w-sm"
          >
            <h3 className="font-semibold text-gray-900 mb-4">Gift Receives to {selectedProfile.name}</h3>
            <p className="text-sm text-gray-600 mb-4">How many receives would you like to send?</p>
            <div className="flex gap-2 mb-6">
              <input
                type="number"
                value={giftAmount}
                onChange={(e) => setGiftAmount(e.target.value)}
                min="1"
                max="100"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter amount"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowGiftModal(false)}
                className="flex-1 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleGiftConfirm}
                disabled={!giftAmount || parseInt(giftAmount) < 1}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Send Gift
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
