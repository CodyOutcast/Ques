import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { Share2, ChevronDown, ChevronUp, Gift } from 'lucide-react';

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
    if (isDragging && (Math.abs(offset.x) > 100 || Math.abs(velocity.x) > 500)) {
      if (offset.x > 0) {
        setExitDirection('right');
        onSwipeRight(currentProfile);
      } else {
        setExitDirection('left');
        onSwipeLeft(currentProfile);
      }
      
      setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
        setExitDirection(null);
        setShowFullProfile(false);
        setDragDirection(null);
        setIsDragging(false);
      }, 300);
    } else {
      setDragDirection(null);
      setIsDragging(false);
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

  return (
    <div className="relative w-full flex flex-col items-center">
      <div className="relative" ref={constraintsRef}>
        <AnimatePresence mode="wait">
          {/* Main Card Container */}
          <motion.div
            key={currentProfile.id}
            className="relative bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden"
            style={{ width: '300px', height: '400px' }}
            initial={{ opacity: 1, x: 0, rotate: 0 }}
            exit={{
              x: exitDirection === 'left' ? -400 : exitDirection === 'right' ? 400 : 0,
              opacity: 0,
              rotate: exitDirection === 'left' ? -45 : exitDirection === 'right' ? 45 : 0,
              scale: 0.8
            }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            animate={{
              rotate: dragDirection === 'left' ? -10 : dragDirection === 'right' ? 10 : 0,
              scale: dragDirection ? 0.95 : 1
            }}
          >
            {/* Drag Area - only for collapsed view or non-scrollable areas when expanded */}
            {!showFullProfile ? (
              <motion.div
                className="absolute inset-0 cursor-grab active:cursor-grabbing z-10"
                drag="x"
                dragConstraints={constraintsRef}
                onDragStart={handleDragStart}
                onDrag={handleDrag}
                onDragEnd={handleDragEnd}
                dragElastic={0.2}
              />
            ) : (
              /* Drag Area for expanded view - only covers header, excludes scrollable content */
              <motion.div
                className="absolute top-0 left-0 right-0 cursor-grab active:cursor-grabbing z-10"
                style={{ height: '80px' }} // Only cover the header area
                drag="x"
                dragConstraints={constraintsRef}
                onDragStart={handleDragStart}
                onDrag={handleDrag}
                onDragEnd={handleDragEnd}
                dragElastic={0.2}
              />
            )}

            {/* Drag Feedback Overlays */}
            <motion.div
              className="absolute inset-0 bg-red-500/20 flex items-center justify-center z-20 pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: dragDirection === 'left' ? 1 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-6xl">✕</div>
            </motion.div>
            
            <motion.div
              className="absolute inset-0 bg-green-500/20 flex items-center justify-center z-20 pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: dragDirection === 'right' ? 1 : 0 }}
              transition={{ duration: 0.2 }}
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

                  {/* Drag Area - limited to top, excluding bottom buttons */}
                  <motion.div
                    className="absolute top-0 left-0 right-0 cursor-grab active:cursor-grabbing z-10"
                    style={{ height: 'calc(100% - 80px)' }} // Leave bottom 80px for buttons
                    drag="x"
                    dragConstraints={constraintsRef}
                    onDragStart={handleDragStart}
                    onDrag={handleDrag}
                    onDragEnd={handleDragEnd}
                    dragElastic={0.2}
                  />

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
                          <span className="font-medium">Receives Left:</span>
                          <span className="font-bold">{currentProfile.receivesLeft || 0}</span>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <div className="w-16 h-2 bg-gray-400/80 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500 rounded-full transition-all duration-300" 
                              style={{ width: `${Math.min((currentProfile.receivesLeft || 0) / 10 * 100, 100)}%` }}
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
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Resources</h4>
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
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Skills</h4>
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
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">Languages</h4>
                          <div className="flex flex-wrap gap-1">
                            {currentProfile.languages.map((language, index) => (
                              <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                                {language}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">Hobbies</h4>
                          <div className="flex flex-wrap gap-1">
                            {currentProfile.hobbies.map((hobby, index) => (
                              <span key={index} className="px-2 py-1 bg-pink-100 text-pink-800 rounded-full text-xs">
                                {hobby}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* About */}
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">About</h4>
                        <p className="text-gray-700 text-xs leading-relaxed">{currentProfile.bio}</p>
                      </div>

                      {/* Projects */}
                      {currentProfile.projects.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">Projects</h4>
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
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">Goals</h4>
                          <div className="space-y-1">
                            {currentProfile.goals.map((goal, index) => (
                              <p key={index} className="text-gray-700 text-xs">• {goal}</p>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">Looking For</h4>
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
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">Institutions</h4>
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
                          <h4 className="font-semibold text-gray-900 text-sm mb-2">University</h4>
                          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
                            <div className="flex items-center justify-between mb-1">
                              <h5 className="font-medium text-gray-900 text-xs">{currentProfile.university.name}</h5>
                              {currentProfile.university.verified && (
                                <span className="text-blue-600 text-xs font-medium bg-blue-100 px-2 py-1 rounded-full">🎓 Verified</span>
                              )}
                            </div>
                            <p className="text-blue-700 text-xs">Current University</p>
                          </div>
                        </div>
                      )}

                      {/* Why We Match */}
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Why We Match</h4>
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
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
