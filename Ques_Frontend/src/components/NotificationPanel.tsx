import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Quote, User, Copy, MessageCircle, Check, Eye, Gift } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { toast } from 'sonner@2.0.3';

export interface FriendRequest {
  id: string;
  name: string;
  avatar: string;
  skills: string[];
  location: string;
  bio: string;
  matchScore: number;
  requestedAt: Date;
  mutualInterest: string;
  wechatId?: string; // WeChat ID they whispered to you
  giftedReceives?: number; // Number of receives this person gifted to you
}

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  friendRequests: FriendRequest[];
  onQuoteContact: (contact: FriendRequest) => void;
  onRemoveRequest: (requestId: string) => void;
  onAddToHistory: (request: FriendRequest) => void;
  onViewOriginalCard?: (contact: FriendRequest) => void;
}

export function NotificationPanel({ 
  isOpen, 
  onClose, 
  friendRequests, 
  onQuoteContact,
  onRemoveRequest,
  onAddToHistory,
  onViewOriginalCard
}: NotificationPanelProps) {
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [animatingRequests, setAnimatingRequests] = useState<Set<string>>(new Set());
  const [copiedIds, setCopiedIds] = useState<Set<string>>(new Set());

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  const handleCardClick = (requestId: string) => {
    setSelectedCardId(selectedCardId === requestId ? null : requestId);
  };

  const handleQuoteContact = (request: FriendRequest) => {
    onQuoteContact(request);
    setSelectedCardId(null);
  };

  const handleCopyWechatId = (wechatId: string, name: string, requestId: string) => {
    navigator.clipboard.writeText(wechatId);
    toast.success(`Copied ${name}'s WeChat ID`);
    
    // Add copy animation
    setCopiedIds(prev => new Set(prev).add(requestId));
    setTimeout(() => {
      setCopiedIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(requestId);
        return newSet;
      });
    }, 1000);
  };

  const handleWhisperBack = (request: FriendRequest) => {
    // Add to animating requests set to trigger animation
    setAnimatingRequests(prev => new Set(prev).add(request.id));
    
    // Wait for animation to complete, then remove the request permanently
    setTimeout(() => {
      toast.success(`Whispered your WeChat ID to ${request.name}`);
      
      // Add to contact history before removing
      onAddToHistory(request);
      
      // Remove from animating set and remove from requests list
      setAnimatingRequests(prev => {
        const newSet = new Set(prev);
        newSet.delete(request.id);
        return newSet;
      });
      
      // Remove the request from the parent state
      onRemoveRequest(request.id);
    }, 2500);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 z-50"
            onClick={onClose}
          />
          
          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-x-4 top-16 bottom-20 bg-white rounded-lg shadow-2xl z-50 flex flex-col max-w-sm mx-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium">Whispers</h2>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={onClose}
                className="h-8 w-8 p-0"
              >
                <X size={16} />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {friendRequests.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-6">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <User size={24} className="text-gray-400" />
                  </div>
                  <h3 className="text-base font-medium text-gray-600 mb-2">No friend requests</h3>
                  <p className="text-sm text-gray-500">
                    When people send you friend requests through Ques, they'll appear here
                  </p>
                </div>
              ) : (
                <div className="p-3 space-y-2">
                  <AnimatePresence mode="popLayout">
                    {friendRequests.map((request) => (
                      <motion.div
                        key={request.id}
                        layout
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ 
                          opacity: animatingRequests.has(request.id) ? [1, 1, 0] : 1, 
                          y: animatingRequests.has(request.id) ? [0, 0, 20] : 0,
                          scale: animatingRequests.has(request.id) ? [1, 0.95, 0.8] : 1
                        }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        transition={{ 
                          duration: animatingRequests.has(request.id) ? 2.5 : 0.3, 
                          times: animatingRequests.has(request.id) ? [0, 0.6, 1] : undefined,
                          ease: "easeInOut",
                          layout: { duration: 0.3, ease: "easeInOut" }
                        }}
                        className="relative"
                      >
                        <Card 
                          className={`p-3 hover:shadow-md transition-all cursor-pointer relative overflow-hidden ${
                            selectedCardId === request.id ? 'blur-sm' : ''
                          } ${animatingRequests.has(request.id) ? 'opacity-50' : ''}`}
                          onClick={() => !animatingRequests.has(request.id) && handleCardClick(request.id)}
                        >
                          {/* Blur overlay with checkmark for animating requests */}
                          <AnimatePresence>
                            {animatingRequests.has(request.id) && (
                              <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.3 }}
                                className="absolute inset-0 bg-white/90 flex items-center justify-center z-20"
                                style={{ 
                                  backdropFilter: 'blur(4px)',
                                  WebkitBackdropFilter: 'blur(4px)'
                                }}
                              >
                                <motion.div
                                  initial={{ scale: 0, rotate: 0 }}
                                  animate={{ scale: 1, rotate: 360 }}
                                  transition={{ 
                                    duration: 0.6,
                                    ease: "easeOut"
                                  }}
                                  className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center shadow-2xl"
                                >
                                  <Check size={20} className="text-white" />
                                </motion.div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                          
                          <div className="text-center">
                            {/* Profile Picture */}
                            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-lg mx-auto mb-2">
                              {request.avatar}
                            </div>
                            
                            {/* Name and Time */}
                            <div className="flex items-center justify-center gap-2 mb-1">
                              <h3 className="text-sm font-medium">{request.name}</h3>
                              <span className="text-xs text-gray-500">
                                {formatTimeAgo(request.requestedAt)}
                              </span>
                            </div>
                            
                            {/* Gift Label */}
                            {request.giftedReceives && request.giftedReceives > 0 && (
                              <div className="flex items-center justify-center mb-2">
                                <div className="inline-flex items-center gap-1 bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-medium">
                                  <Gift size={10} />
                                  x{request.giftedReceives}
                                </div>
                              </div>
                            )}
                            
                            {/* WeChat ID Section */}
                            {request.wechatId && (
                              <div className="bg-gray-50 rounded-lg p-2 mb-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <p className="text-xs text-gray-500 mb-1">Shared WeChat ID:</p>
                                    <p className="text-sm font-medium text-gray-700">{request.wechatId}</p>
                                  </div>
                                  <motion.div
                                    animate={{ 
                                      scale: copiedIds.has(request.id) ? [1, 1.2, 1] : 1,
                                      backgroundColor: copiedIds.has(request.id) ? ['transparent', '#10b981', 'transparent'] : 'transparent'
                                    }}
                                    transition={{ 
                                      duration: 0.6,
                                      times: [0, 0.3, 1],
                                      ease: "easeInOut"
                                    }}
                                    className="rounded"
                                  >
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className={`h-8 w-8 p-0 transition-colors ${
                                        copiedIds.has(request.id) 
                                          ? 'text-white' 
                                          : 'text-gray-600 hover:text-gray-800'
                                      }`}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleCopyWechatId(request.wechatId!, request.name, request.id);
                                      }}
                                    >
                                      <Copy size={14} />
                                    </Button>
                                  </motion.div>
                                </div>
                              </div>
                            )}
                            
                            {/* Action Buttons */}
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className={`flex-1 h-8 text-xs transition-all duration-300 ${
                                  animatingRequests.has(request.id) 
                                    ? 'bg-green-50 border-green-200 text-green-700' 
                                    : ''
                                }`}
                                disabled={animatingRequests.has(request.id)}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleWhisperBack(request);
                                }}
                              >
                                <MessageCircle size={12} className="mr-1" />
                                {animatingRequests.has(request.id) ? 'Whispered ✓' : 'Whisper Back'}
                              </Button>
                            </div>
                          </div>
                        </Card>
                        
                        {/* Floating Action Buttons */}
                        {selectedCardId === request.id && !animatingRequests.has(request.id) && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="absolute inset-0 flex items-center justify-center z-10 bg-black/20 backdrop-blur-sm"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div className="flex gap-3">
                              {/* View Original Card Button */}
                              {onViewOriginalCard && (
                                <Button
                                  size="lg"
                                  variant="outline"
                                  className="rounded-full w-14 h-14 p-0 bg-white hover:bg-purple-50 shadow-lg border-purple-200"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    onViewOriginalCard(request);
                                    setSelectedCardId(null);
                                    onClose();
                                  }}
                                >
                                  <Eye size={18} className="text-purple-600" />
                                </Button>
                              )}
                              
                              {/* Quote Button */}
                              <Button
                                size="lg"
                                className="rounded-full w-14 h-14 p-0 bg-blue-500 hover:bg-blue-600 shadow-lg"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleQuoteContact(request);
                                }}
                              >
                                <Quote size={18} />
                              </Button>
                              
                              {/* Remove Button */}
                              <Button
                                size="lg"
                                variant="outline"
                                className="rounded-full w-14 h-14 p-0 bg-white hover:bg-gray-50 shadow-lg border-gray-200"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onRemoveRequest(request.id);
                                  setSelectedCardId(null);
                                }}
                              >
                                <X size={18} className="text-gray-600" />
                              </Button>
                            </div>
                          </motion.div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}