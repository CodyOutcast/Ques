import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'motion/react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { PersonReceivesBar } from './PersonReceivesBar';
import { X, Heart, MapPin, Star, ArrowLeft, ChevronDown, ChevronUp, Briefcase, GraduationCap, Target, Users, Globe, Mail, CheckCircle, Share } from 'lucide-react';

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

interface SwipeableCardStackProps {
  recommendations: UserRecommendation[];
  onWhisper: (contact: UserRecommendation) => void;
  onIgnore: (contact: UserRecommendation) => void;
  onClose: () => void;
  currentPlan?: 'basic' | 'pro';
  receivesLeft?: number;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
  inline?: boolean;
}

export function SwipeableCardStack({ 
  recommendations, 
  onWhisper, 
  onIgnore, 
  onClose,
  currentPlan = 'basic',
  receivesLeft = 3,
  onTopUpReceives,
  onGiftReceives,
  inline = false
}: SwipeableCardStackProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const currentCard = recommendations[currentIndex];
  const nextCards = recommendations.slice(currentIndex + 1, currentIndex + 3); // Show next 2 cards in stack

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
        onClose(); // All cards done, return to chat
      } else {
        setCurrentIndex(prev => prev + 1);
        setExitDirection(null);
        setIsExpanded(false); // Reset expanded state for next card
      }
    }, 300);
  };

  const handleDragEnd = (event: any, info: PanInfo) => {
    const swipeThreshold = 100;
    const swipeVelocityThreshold = 500;
    
    const { offset, velocity } = info;
    
    if (Math.abs(offset.x) > swipeThreshold || Math.abs(velocity.x) > swipeVelocityThreshold) {
      if (offset.x > 0 || velocity.x > 0) {
        handleSwipe('right');
      } else {
        handleSwipe('left');
      }
    }
  };

  if (!currentCard) {
    return null;
  }

  return (
    <div className={inline ? "relative w-full flex flex-col" : "fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex flex-col"}>
      {/* Main Content */}
      <div className={inline ? "flex-1 flex items-center justify-center" : "flex-1 flex items-center justify-center p-4"}>
        {/* Header */}
        <div className={inline ? "absolute top-0 left-0 right-0 flex items-center justify-between z-10 mb-4" : "absolute top-20 left-4 right-4 flex items-center justify-between z-10"}>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className={inline ? "bg-gray-100 hover:bg-gray-200" : "bg-white/90 backdrop-blur-sm hover:bg-white"}
          >
            <ArrowLeft size={16} />
          </Button>
          <div className={inline ? "text-gray-600 text-sm bg-gray-100 px-3 py-1 rounded-full" : "text-white text-sm bg-black/30 backdrop-blur-sm px-3 py-1 rounded-full"}>
            {currentIndex + 1} / {recommendations.length}
          </div>
        </div>

        {/* Card Stack */}
        <div className={inline ? "relative w-full max-w-sm h-[500px] mt-12" : "relative w-full max-w-sm h-[600px]"}>
          {/* Background cards (stack effect) */}
          {nextCards.map((card, index) => (
            <motion.div
              key={card.id}
              className="absolute inset-0"
              initial={{ scale: 0.95 - (index * 0.05), y: (index + 1) * 8 }}
              animate={{ scale: 0.95 - (index * 0.05), y: (index + 1) * 8 }}
              style={{ zIndex: nextCards.length - index }}
            >
              <Card className="w-full h-full overflow-hidden shadow-2xl opacity-60 flex flex-col">
                {/* Receives bar for background cards */}
                <div className="bg-gray-100 border-b border-gray-200 p-3">
                  <div className="w-16 bg-gray-300 rounded-full h-1.5"></div>
                </div>
                <div className="flex-1 bg-gray-200 flex items-center justify-center text-6xl">
                  {card.avatar}
                </div>
              </Card>
            </motion.div>
          ))}

          {/* Main card */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentCard.id}
              ref={cardRef}
              className="absolute inset-0 cursor-grab active:cursor-grabbing"
              style={{ zIndex: 10 }}
              initial={{ scale: 1, rotate: 0, x: 0, y: 0 }}
              animate={{ 
                scale: 1, 
                rotate: 0, 
                x: 0, 
                y: 0,
                transition: { type: "spring", damping: 20, stiffness: 300 }
              }}
              exit={{
                x: exitDirection === 'right' ? 1000 : exitDirection === 'left' ? -1000 : 0,
                rotate: exitDirection === 'right' ? 30 : exitDirection === 'left' ? -30 : 0,
                opacity: 0,
                transition: { duration: 0.3 }
              }}
              drag="x"
              dragConstraints={{ left: -200, right: 200 }}
              dragElastic={0.7}
              onDragEnd={handleDragEnd}
              whileDrag={{
                rotate: (info: any) => info.offset.x * 0.1,
                scale: 1.05
              }}
            >
              <Card className="w-full h-full overflow-hidden shadow-2xl bg-white flex flex-col">
                {/* Person-specific Receives Bar */}
                <PersonReceivesBar
                  personName={currentCard.name}
                  currentPlan={currentPlan}
                  receivesLeft={receivesLeft}
                  onGiftReceives={onGiftReceives}
                />
                
                {/* Profile Image Section */}
                <div className={`w-full relative transition-all duration-300 ${
                  isExpanded ? 'h-1/4' : 'flex-1'
                }`}>
                  {/* Background with gradient fade effect for longer cards */}
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500" />
                  <div className="absolute inset-0 bg-gradient-to-t from-blue-500/20 via-transparent to-transparent" />
                  
                  {/* Avatar */}
                  <div className="absolute inset-0 flex items-center justify-center text-6xl">
                    {currentCard.avatar}
                  </div>

                  {/* Gradient overlay for text readability - only when not expanded */}
                  {!isExpanded && (
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                  )}

                  {/* Name and intro text overlay - only show when not expanded */}
                  {!isExpanded && (
                    <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                      <h3 className="text-xl font-medium mb-2 text-white">{currentCard.name}</h3>
                      <p className="text-sm text-white/90 line-clamp-2 leading-relaxed">
                        {currentCard.oneSentenceIntro || currentCard.bio}
                      </p>
                    </div>
                  )}

                  {/* Share Button - bottom left of expand button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Handle share functionality
                      console.log('Sharing profile:', currentCard.name);
                    }}
                    className="absolute bottom-4 right-14 bg-black/20 backdrop-blur-sm hover:bg-black/30 text-white border border-white/30 rounded-full w-8 h-8 p-0"
                  >
                    <Share size={16} />
                  </Button>

                  {/* Expand/Collapse Button - bottom right */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsExpanded(!isExpanded);
                    }}
                    className="absolute bottom-4 right-4 bg-black/20 backdrop-blur-sm hover:bg-black/30 text-white border border-white/30 rounded-full w-8 h-8 p-0"
                  >
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </Button>
                </div>

                {/* Info Section - only shows when expanded */}
                {isExpanded && (
                  <div className="flex-1 overflow-hidden">
                    {/* Expanded View with Full Profile */}
                    <ScrollArea className="h-full">
                      <div 
                        className="p-4 space-y-4"
                        onTouchStart={(e) => e.stopPropagation()}
                        onMouseDown={(e) => e.stopPropagation()}
                      >
                        {/* Header */}
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <h3 className="text-lg font-medium">{currentCard.name}</h3>
                          </div>
                          
                          <div className="flex items-center text-gray-500 text-sm mb-3">
                            <MapPin size={12} className="mr-1" />
                            {currentCard.location}
                          </div>

                          <p className="text-sm text-gray-700 mb-3">
                            {currentCard.bio}
                          </p>
                        </div>

                        <Separator />

                        {/* Skills & Expertise */}
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Briefcase size={14} className="text-blue-600" />
                            <h4 className="font-medium text-sm">Skills & Expertise</h4>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {currentCard.skills.map((skill, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <Separator />

                        {/* Projects */}
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Target size={14} className="text-green-600" />
                            <h4 className="font-medium text-sm">Key Projects</h4>
                          </div>
                          <div className="space-y-2">
                            {currentCard.projects.map((project, index) => (
                              <div key={index} className="bg-gray-50 rounded-lg p-3">
                                <h5 className="font-medium text-sm text-gray-800">{project}</h5>
                              </div>
                            ))}
                          </div>
                        </div>

                        <Separator />

                        {/* Why Match */}
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Users size={14} className="text-purple-600" />
                            <h4 className="font-medium text-sm">Why You Match</h4>
                          </div>
                          <div className="bg-blue-50 rounded-lg p-3">
                            <p className="text-xs text-blue-700 leading-relaxed">
                              {currentCard.whyMatch}
                            </p>
                          </div>
                        </div>

                        {/* Mock additional profile sections */}
                        <Separator />

                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <GraduationCap size={14} className="text-orange-600" />
                            <h4 className="font-medium text-sm">Education & Experience</h4>
                          </div>
                          <div className="space-y-2">
                            <div className="bg-gray-50 rounded-lg p-3">
                              <div className="flex items-center justify-between mb-1">
                                <h5 className="font-medium text-sm text-gray-800">Tsinghua University</h5>
                                <CheckCircle size={12} className="text-green-500" />
                              </div>
                              <p className="text-xs text-gray-600">Computer Science • 2018-2022</p>
                            </div>
                            <div className="bg-gray-50 rounded-lg p-3">
                              <h5 className="font-medium text-sm text-gray-800">Tech Lead at ByteDance</h5>
                              <p className="text-xs text-gray-600">Leading AI research team • 2022-Present</p>
                            </div>
                          </div>
                        </div>

                        <Separator />

                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Globe size={14} className="text-indigo-600" />
                            <h4 className="font-medium text-sm">Languages & Interests</h4>
                          </div>
                          <div className="space-y-2">
                            <div>
                              <p className="text-xs text-gray-600 mb-1">Languages:</p>
                              <div className="flex flex-wrap gap-1">
                                <Badge variant="outline" className="text-xs">English (Fluent)</Badge>
                                <Badge variant="outline" className="text-xs">Mandarin (Native)</Badge>
                                <Badge variant="outline" className="text-xs">Japanese (Basic)</Badge>
                              </div>
                            </div>
                            <div>
                              <p className="text-xs text-gray-600 mb-1">Interests:</p>
                              <div className="flex flex-wrap gap-1">
                                <Badge variant="outline" className="text-xs">AI Ethics</Badge>
                                <Badge variant="outline" className="text-xs">Startup Building</Badge>
                                <Badge variant="outline" className="text-xs">Rock Climbing</Badge>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Bottom padding for scroll */}
                        <div className="pb-4"></div>
                      </div>
                    </ScrollArea>
                  </div>
                )}
              </Card>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Action Buttons - hide when expanded */}
        <AnimatePresence>
          {!isExpanded && (
            <motion.div
              initial={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.2 }}
              className="absolute bottom-20 left-1/2 transform -translate-x-1/2 flex items-center gap-6"
            >
              <Button
                variant="outline"
                size="lg"
                onClick={() => handleSwipe('left')}
                className="w-14 h-14 rounded-full border-2 border-red-500 text-red-500 hover:bg-red-50 hover:border-red-600 hover:text-red-600 bg-white shadow-lg"
              >
                <X size={24} />
              </Button>
              
              <Button
                size="lg"
                onClick={() => handleSwipe('right')}
                className="w-14 h-14 rounded-full bg-blue-500 hover:bg-blue-600 text-white shadow-lg"
              >
                <Heart size={24} />
              </Button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Swipe Hints */}
        <div className={`absolute left-1/2 transform -translate-x-1/2 text-center transition-all duration-300 ${
          isExpanded ? 'bottom-6' : 'bottom-32'
        }`}>
          <p className={inline ? "text-gray-600 text-sm opacity-75" : "text-white text-sm opacity-75"}>
            Swipe right to whisper • Swipe left to pass
          </p>
        </div>
      </div>
    </div>
  );
}