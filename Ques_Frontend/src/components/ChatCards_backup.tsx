import React, { useState, useRef } from 'react';
import { motion, AnimatePresence, PanInfo } from 'motion/react';
import { X } from 'lucide-react';

interface UserRecommendation {
  id: string;
  name: string;
  avatar: string;
  skills: string[];
  location: string;
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  projects: string[];
  whyMatch: string;
}

interface ChatCardsProps {
  recommendations: UserRecommendation[];
  onWhisper: (contact: UserRecommendation) => void;
  onIgnore: (contact: UserRecommendation) => void;
  onClose: () => void;
  currentPlan?: 'basic' | 'pro';
  receivesLeft?: number;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
}

export function ChatCards({ 
  recommendations, 
  onWhisper, 
  onIgnore, 
  onClose,
  currentPlan = 'basic',
  receivesLeft = 3,
  onTopUpReceives,
  onGiftReceives
}: ChatCardsProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
  const [dragDirection, setDragDirection] = useState<'left' | 'right' | null>(null);
  const [showFullProfile, setShowFullProfile] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const currentCard = recommendations[currentIndex];

  const handleSwipe = (direction: 'left' | 'right') => {
    if (!currentCard) return;

    setExitDirection(direction);
    
    if (direction === 'right') {
      onWhisper(currentCard);
    } else {
      onIgnore(currentCard);
    }

    // Move to next card after animation
    setTimeout(() => {
      if (currentIndex >= recommendations.length - 1) {
        onClose(); // All cards done
      } else {
        setCurrentIndex(prev => prev + 1);
        setExitDirection(null);
        setDragDirection(null);
        setShowFullProfile(false);
      }
    }, 300);
  };

  const handleDrag = (event: any, info: PanInfo) => {
    const threshold = 50;
    if (Math.abs(info.offset.x) > threshold) {
      setDragDirection(info.offset.x > 0 ? 'right' : 'left');
    } else {
      setDragDirection(null);
    }
  };

  const handleDragEnd = (event: any, info: PanInfo) => {
    const swipeThreshold = 100;
    const swipeVelocityThreshold = 500;
    
    const { offset, velocity } = info;
    
    setDragDirection(null);
    
    if (Math.abs(offset.x) > swipeThreshold || Math.abs(velocity.x) > swipeVelocityThreshold) {
      if (offset.x > 0 || velocity.x > 0) {
        handleSwipe('right');
      } else {
        handleSwipe('left');
      }
    }
  };

  const handleShare = (e: React.MouseEvent) => {
    e.stopPropagation();
    // TODO: Implement share functionality
    console.log('Share profile:', currentCard.name);
  };

  const toggleFullProfile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowFullProfile(!showFullProfile);
  };

  if (!currentCard) {
    return null;
  }

  return (
    <div className="relative w-full max-w-sm mx-auto">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentCard.id}
          ref={cardRef}
          className="w-full cursor-grab active:cursor-grabbing"
          initial={{ scale: 1, x: 0, rotate: 0 }}
          animate={{ 
            scale: 1, 
            x: 0, 
            rotate: 0,
            transition: { type: "spring", damping: 20, stiffness: 300 }
          }}
          exit={{
            x: exitDirection === 'right' ? 300 : exitDirection === 'left' ? -300 : 0,
            rotate: exitDirection === 'right' ? 15 : exitDirection === 'left' ? -15 : 0,
            opacity: 0,
            transition: { duration: 0.3 }
          }}
          drag="x"
          dragConstraints={{ left: -150, right: 150 }}
          dragElastic={0.7}
          onDrag={handleDrag}
          onDragEnd={handleDragEnd}
          whileDrag={{ scale: 1.02 }}
        >
          <div className={`p-4 cursor-pointer transition-all duration-200 relative overflow-hidden w-full bg-white rounded-xl border shadow-sm ${
            dragDirection === 'left' ? 'border-2 border-red-300' :
            dragDirection === 'right' ? 'border-2 border-green-300' :
            'border border-gray-200'
          }`} 
          style={{ height: '457px' }}>
            {/* Profile Picture Background - Large emoji filling entire card */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 opacity-30">
              <div className="w-full h-full flex items-center justify-center text-9xl leading-none">
                {currentCard.avatar}
              </div>
            </div>

            {/* Dark fade at bottom for text readability */}
            <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>

            {/* Drag indicators */}
            {dragDirection && (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20 rounded-xl">
                <div className="text-3xl font-bold text-white">
                  {dragDirection === 'left' ? 'PASS' : 'CONNECT'}
                </div>
              </div>
            )}

            {/* Close button */}
            <button 
              onClick={onClose}
              className="absolute top-3 right-3 p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full z-10 backdrop-blur-sm"
            >
              <X size={16} className="text-white" />
            </button>

            {/* Bottom content area */}
            <div className="absolute bottom-0 left-0 right-0 p-4 z-10">
              <div className="flex items-end justify-between">
                {/* Name and description */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-xl text-white mb-1">{currentCard.name}</h3>
                  <p className="text-white text-sm opacity-90 leading-tight line-clamp-2">
                    {currentCard.oneSentenceIntro || currentCard.bio}
                  </p>
                </div>

                {/* Action buttons */}
                <div className="flex flex-col gap-2 ml-4 flex-shrink-0">
                  <button 
                    onClick={handleShare}
                    className="text-white text-sm bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-2 rounded-full backdrop-blur-sm font-medium"
                  >
                    Share
                  </button>
                  <button 
                    onClick={toggleFullProfile}
                    className="text-white text-sm bg-white bg-opacity-30 hover:bg-opacity-40 px-3 py-2 rounded-full backdrop-blur-sm font-medium"
                  >
                    {showFullProfile ? '↑' : '↓'}
                  </button>
                </div>
              </div>
            </div>

            {/* Extended profile info - scrollable */}
            {showFullProfile && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="absolute inset-x-0 bottom-0 bg-white rounded-b-xl max-h-96 overflow-y-auto z-20"
              >
                <div className="p-6 space-y-4">
                  {/* Location */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">📍 Location</h4>
                    <p className="text-gray-700">{currentCard.location}</p>
                  </div>

                  {/* Skills */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">🎯 Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {currentCard.skills.map((skill, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Projects */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">🚀 Projects</h4>
                    <div className="space-y-2">
                      {currentCard.projects.map((project, index) => (
                        <div key={index} className="bg-gray-50 p-3 rounded-lg">
                          <p className="text-gray-800 text-sm">{project}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Why Match */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">💫 Why you match</h4>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-blue-800 text-sm leading-relaxed">
                        {currentCard.whyMatch}
                      </p>
                    </div>
                  </div>

                  {/* Match Score */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">🎯 Match Score</h4>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-500" 
                          style={{ width: `${currentCard.matchScore}%` }}
                        ></div>
                      </div>
                      <span className="text-lg font-bold text-gray-900">{currentCard.matchScore}%</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>            {/* Extended profile info */}
            {showFullProfile && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-white p-4 mt-32"
              >
                <div className="space-y-3">
                  {/* Location */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-800 mb-1">Location</h4>
                    <p className="text-sm text-gray-600">{currentCard.location}</p>
                  </div>

                  {/* Skills */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-800 mb-1">Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {currentCard.skills.map((skill, index) => (
                        <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Projects */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-800 mb-1">Projects</h4>
                    <div className="space-y-1">
                      {currentCard.projects.map((project, index) => (
                        <p key={index} className="text-sm text-gray-600">• {project}</p>
                      ))}
                    </div>
                  </div>

                  {/* Why Match */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-800 mb-1">Why you match</h4>
                    <div className="bg-blue-50 rounded-lg p-2">
                      <p className="text-xs text-blue-700 leading-relaxed">
                        {currentCard.whyMatch}
                      </p>
                    </div>
                  </div>

                  {/* Match Score */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-800 mb-1">Match Score</h4>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Progress dots */}
      <div className="flex justify-center gap-1 mt-2">
        {recommendations.map((_, index) => (
          <div
            key={index}
            className={`w-1.5 h-1.5 rounded-full transition-colors ${
              index === currentIndex ? 'bg-blue-500' : 
              index < currentIndex ? 'bg-green-500' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  );
}