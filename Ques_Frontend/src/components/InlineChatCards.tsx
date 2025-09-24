import React, { useState, useRef } from 'react';
import { motion, AnimatePresence, PanInfo } from 'motion/react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { X, Heart, MapPin, Star } from 'lucide-react';

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

interface InlineChatCardsProps {
  recommendations: UserRecommendation[];
  onWhisper: (contact: UserRecommendation) => void;
  onIgnore: (contact: UserRecommendation) => void;
  onClose: () => void;
  currentPlan?: 'basic' | 'pro';
  receivesLeft?: number;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
}

export function InlineChatCards({ 
  recommendations, 
  onWhisper, 
  onIgnore, 
  onClose,
  currentPlan = 'basic',
  receivesLeft = 3,
  onTopUpReceives,
  onGiftReceives
}: InlineChatCardsProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  const currentCard = recommendations[currentIndex];
  const nextCards = recommendations.slice(currentIndex + 1, currentIndex + 3); // Show next 2 cards for 3-card stack

  console.log('InlineChatCards props:', {
    recommendationsLength: recommendations.length,
    currentIndex,
    currentCard: currentCard?.name,
    currentCardAvatar: currentCard?.avatar,
    nextCardsLength: nextCards.length
  });

  console.log('Current card full data:', currentCard);

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
        onClose(); // All cards done, close the card view
      } else {
        setCurrentIndex(prev => prev + 1);
        setExitDirection(null);
      }
    }, 300);
  };

  const handleDragEnd = (event: any, info: PanInfo) => {
    const swipeThreshold = 80;
    const swipeVelocityThreshold = 400;
    
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
    console.log('No current card available');
    return null;
  }

  console.log('Rendering InlineChatCards with:', currentCard.name);

  return (
    <div className="relative w-full h-full">
      {/* Background cards (next cards preview) */}
      {nextCards.map((card, index) => (
        <motion.div
          key={card.id}
          className="absolute inset-0"
          initial={{ 
            scale: 0.95 - (index * 0.05), 
            y: 8 + (index * 8) 
          }}
          animate={{ 
            scale: 0.95 - (index * 0.05), 
            y: 8 + (index * 8) 
          }}
          style={{ zIndex: 1 - index }}
        >
          <Card className="w-full h-full min-h-[480px] min-w-[320px] overflow-hidden shadow-lg bg-white" style={{ opacity: 0.5 - (index * 0.1) }}>
            <div className="h-3/5 bg-gradient-to-br from-blue-400 to-purple-500 relative flex items-center justify-center">
              {card.avatar.startsWith('http') || card.avatar.startsWith('data:') ? (
                <>
                  <img 
                    src={card.avatar} 
                    alt={card.name}
                    className="w-16 h-16 rounded-full object-cover border-2 border-white"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const fallback = target.nextElementSibling as HTMLDivElement;
                      if (fallback) fallback.style.display = 'flex';
                    }}
                  />
                  <div 
                    className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 border-2 border-white flex items-center justify-center text-white text-xl font-bold"
                    style={{ display: 'none' }}
                  >
                    {card.name.charAt(0)}
                  </div>
                </>
              ) : (
                <div className="w-16 h-16 rounded-full bg-white border-2 border-white flex items-center justify-center text-2xl">
                  {card.avatar}
                </div>
              )}
            </div>
            <div className="p-3">
              <h3 className="font-medium text-sm">{card.name}</h3>
              <p className="text-xs text-gray-500">{card.location}</p>
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
            x: exitDirection === 'right' ? 400 : exitDirection === 'left' ? -400 : 0,
            rotate: exitDirection === 'right' ? 15 : exitDirection === 'left' ? -15 : 0,
            opacity: 0,
            transition: { duration: 0.3 }
          }}
          drag="x"
          dragConstraints={{ left: -100, right: 100 }}
          dragElastic={0.7}
          onDragEnd={handleDragEnd}
        >
          <Card className="w-full h-full min-h-[480px] min-w-[320px] overflow-hidden shadow-xl bg-white flex flex-col">
            {/* Profile Image Section */}
            <div className="h-2/5 bg-gradient-to-br from-blue-400 to-purple-500 relative">
              {/* Avatar */}
              <div className="absolute inset-0 flex items-center justify-center">
                {/* Check if avatar is an emoji/text or URL */}
                {currentCard.avatar.startsWith('http') || currentCard.avatar.startsWith('data:') ? (
                  <>
                    <img 
                      src={currentCard.avatar} 
                      alt={currentCard.name}
                      className="w-20 h-20 rounded-full object-cover border-4 border-white shadow-lg"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const fallback = target.nextElementSibling as HTMLDivElement;
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                    <div 
                      className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 border-4 border-white shadow-lg flex items-center justify-center text-white text-2xl font-bold"
                      style={{ display: 'none' }}
                    >
                      {currentCard.name.charAt(0)}
                    </div>
                  </>
                ) : (
                  /* Emoji/Text Avatar */
                  <div className="w-20 h-20 rounded-full bg-white border-4 border-white shadow-lg flex items-center justify-center text-4xl">
                    {currentCard.avatar}
                  </div>
                )}
              </div>

              {/* Gradient overlay for text readability */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

              {/* Name and info overlay */}
              <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
                <h3 className="text-lg font-medium mb-1">{currentCard.name}</h3>
                <div className="flex items-center gap-1 text-sm opacity-90">
                  <MapPin size={12} />
                  <span>{currentCard.location}</span>
                  <Star size={12} className="ml-2" />
                  <span>{currentCard.matchScore}% match</span>
                </div>
              </div>
            </div>

            {/* Info Section */}
            <div className="flex-1 p-3 space-y-2">
              <p className="text-sm text-gray-700 leading-relaxed line-clamp-2">
                {currentCard.oneSentenceIntro || currentCard.bio}
              </p>
              
              <div className="flex flex-wrap gap-1">
                {currentCard.skills.slice(0, 3).map((skill, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {skill}
                  </Badge>
                ))}
                {currentCard.skills.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{currentCard.skills.length - 3}
                  </Badge>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="p-3 flex justify-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSwipe('left')}
                className="w-12 h-12 rounded-full border-2 border-red-500 text-red-500 hover:bg-red-50"
              >
                <X size={18} />
              </Button>
              
              <Button
                size="sm"
                onClick={() => handleSwipe('right')}
                className="w-12 h-12 rounded-full bg-blue-500 hover:bg-blue-600 text-white"
              >
                <Heart size={18} />
              </Button>
            </div>
          </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}