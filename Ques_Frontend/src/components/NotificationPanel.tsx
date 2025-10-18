import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Quote, User, Copy, MessageCircle, Check, Eye, Gift, Share2, ChevronDown, ChevronUp, MessageSquare } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';
import { WhisperMessageDialog } from './WhisperMessageDialog';
import { calculateAge } from '../utils/dateUtils';

export interface FriendRequest {
  id: string;
  name: string;
  birthday: string;
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
  receivesLeft?: number;
  requestedAt: Date;
  mutualInterest: string;
  wechatId?: string; // WeChat ID they whispered to you
  giftedReceives?: number; // Number of receives this person gifted to you
  message?: string; // Whisper message from sender
}

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  friendRequests: FriendRequest[];
  onQuoteContact: (contact: FriendRequest) => void;
  onRemoveRequest: (requestId: string) => void;
  onAddToHistory: (request: FriendRequest, message?: string) => void;
  onViewOriginalCard?: (contact: FriendRequest) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
  whispersLeft?: number;
  onWhisperSent?: () => void;
}

export function NotificationPanel({ 
  isOpen, 
  onClose, 
  friendRequests, 
  onQuoteContact,
  onRemoveRequest,
  onAddToHistory,
  onViewOriginalCard,
  onGiftReceives,
  whispersLeft = 0,
  onWhisperSent
}: NotificationPanelProps) {
  const { t } = useLanguage();
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  
  // Debug: Log friend requests to verify message field
  useEffect(() => {
    if (friendRequests.length > 0) {
      console.log('Friend Requests:', friendRequests.map(r => ({ name: r.name, hasMessage: !!r.message, message: r.message })));
    }
  }, [friendRequests]);
  const [animatingRequests, setAnimatingRequests] = useState<Set<string>>(new Set());
  const [copiedIds, setCopiedIds] = useState<Set<string>>(new Set());
  const [viewingProfile, setViewingProfile] = useState<FriendRequest | null>(null);
  const [showFullProfile, setShowFullProfile] = useState(false);
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [selectedForGift, setSelectedForGift] = useState<FriendRequest | null>(null);
  const [giftAmount, setGiftAmount] = useState('');
  const [showWhisperDialog, setShowWhisperDialog] = useState(false);
  const [pendingWhisperRequest, setPendingWhisperRequest] = useState<FriendRequest | null>(null);

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return t('notifications.justNow');
    if (diffInHours < 24) return `${diffInHours}${t('notifications.hoursAgo')}`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}${t('notifications.daysAgo')}`;
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
    toast.success(`${t('notifications.copied')} ${name}'s WeChat ID`);
    
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
    // Show whisper dialog before sending
    setPendingWhisperRequest(request);
    setShowWhisperDialog(true);
  };

  const handleWhisperSend = (message: string) => {
    if (!pendingWhisperRequest) return;

    // Check if user has whispers left
    if (whispersLeft <= 0) {
      toast.error('You have no whispers left this month. Please upgrade to Pro or wait for next month.');
      setShowWhisperDialog(false);
      setPendingWhisperRequest(null);
      return;
    }

    // Decrease whisper count
    onWhisperSent?.();
    console.log('💬 Whisper back sent! Whispers left:', whispersLeft - 1);

    // Add to animating requests set to trigger animation
    setAnimatingRequests(prev => new Set(prev).add(pendingWhisperRequest.id));
    setShowWhisperDialog(false);
    
    // Wait for animation to complete, then remove the request permanently
    setTimeout(() => {
      toast.success(`${t('notifications.whisperBackSuccess')} ${pendingWhisperRequest.name}`);
      
      // Add to contact history before removing (with message)
      onAddToHistory(pendingWhisperRequest, message);
      
      // Remove from animating set and remove from requests list
      setAnimatingRequests(prev => {
        const newSet = new Set(prev);
        newSet.delete(pendingWhisperRequest.id);
        return newSet;
      });
      
      // Remove the request from the parent state
      onRemoveRequest(pendingWhisperRequest.id);
      setPendingWhisperRequest(null);
    }, 2500);
  };

  const handleWhisperDialogClose = () => {
    setShowWhisperDialog(false);
    setPendingWhisperRequest(null);
  };

  const handleViewOriginalCard = (request: FriendRequest) => {
    setViewingProfile(request);
    setSelectedCardId(null);
    setShowFullProfile(false);
  };

  const closeProfileView = () => {
    setViewingProfile(null);
    setShowFullProfile(false);
  };

  const toggleExtendedProfile = () => {
    setShowFullProfile(!showFullProfile);
  };

  const handleShareProfile = () => {
    if (viewingProfile) {
      console.log('Sharing profile:', viewingProfile.name);
    }
  };

  const openGiftModal = (request: FriendRequest) => {
    setSelectedForGift(request);
    setGiftAmount('');
    setShowGiftModal(true);
  };

  const handleGiftConfirm = () => {
    if (selectedForGift && giftAmount && onGiftReceives) {
      const amount = parseInt(giftAmount);
      if (amount > 0) {
        onGiftReceives(selectedForGift.name, amount);
        setShowGiftModal(false);
        setSelectedForGift(null);
        setGiftAmount('');
      }
    }
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
              <h2 className="text-lg font-medium">{t('notifications.title')}</h2>
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
            <div className="flex-1 overflow-y-auto" onClick={() => setSelectedCardId(null)}>
              {friendRequests.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-6">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <User size={24} className="text-gray-400" />
                  </div>
                  <h3 className="text-base font-medium text-gray-600 mb-2">{t('notifications.noRequests')}</h3>
                  <p className="text-sm text-gray-500">
                    {t('notifications.noRequestsDesc')}
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
                          onClick={(e) => {
                            e.stopPropagation();
                            if (!animatingRequests.has(request.id)) {
                              handleCardClick(request.id);
                            }
                          }}
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
                            
                            {/* Whisper Message Section */}
                            {request.message && (
                              <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 mb-2">
                                <div className="flex items-start gap-2">
                                  <MessageSquare size={14} className="text-blue-600 mt-0.5 flex-shrink-0" />
                                  <div className="flex-1 min-w-0">
                                    <p className="text-xs text-blue-600 mb-1 font-medium">{t('notifications.whisperMessage')}</p>
                                    <p className="text-xs text-blue-900 leading-relaxed break-words">{request.message}</p>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* WeChat ID Section */}
                            {request.wechatId && (
                              <div className="bg-gray-50 rounded-lg p-2 mb-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <p className="text-xs text-gray-500 mb-1">{t('notifications.sharedWeChatId')}</p>
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
                                {animatingRequests.has(request.id) ? `${t('notifications.whisperBack')} ✓` : t('notifications.whisperBack')}
                              </Button>
                            </div>
                          </div>
                        </Card>
                        
                        {/* Floating Action Buttons */}
                        {selectedCardId === request.id && !animatingRequests.has(request.id) && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="absolute inset-0 flex items-center justify-center z-10 bg-black/20 backdrop-blur-sm rounded-lg"
                            onClick={() => setSelectedCardId(null)}
                          >
                            <div className="flex gap-3" onClick={(e) => e.stopPropagation()}>
                              {/* View Original Card Button */}
                              {onViewOriginalCard && (
                                <Button
                                  size="lg"
                                  variant="outline"
                                  className="rounded-full w-14 h-14 p-0 bg-white hover:bg-purple-50 shadow-lg border-purple-200"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleViewOriginalCard(request);
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

          {/* Profile Card Modal */}
          <AnimatePresence>
            {viewingProfile && (
              <>
                {/* Modal Backdrop */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
                  style={{ zIndex: 120 }}
                  onClick={closeProfileView}
                />
                
                {/* Profile Card */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: 20 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="fixed inset-0 flex items-center justify-center z-50 p-4"
                  style={{ zIndex: 130 }}
                  onClick={closeProfileView}
                >
                  <div
                    className="relative bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden"
                    style={{ width: '300px', height: '400px' }}
                    onClick={(e) => e.stopPropagation()}
                  >
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
                              {viewingProfile.avatar}
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                          </div>

                          {/* Bottom content area */}
                          <div className="absolute bottom-0 left-0 right-0 p-6 text-white z-30">
                            <div className="flex items-center justify-between mb-2">
                              <h2 className="text-lg font-bold">
                                {viewingProfile.name}
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
                              {viewingProfile.oneSentenceIntro || viewingProfile.bio}
                            </p>
                            
                            {/* Receives Bar - integrated as last line in collapsed view */}
                            <div className="absolute bottom-4 left-0 right-0 px-6 text-white text-xs z-40">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1 flex-1">
                                  <span className="font-medium">Receives Left:</span>
                                  <span className="font-bold">{viewingProfile.receivesLeft || 0}</span>
                                </div>
                                <div className="flex items-center gap-2 ml-4">
                                  <div className="w-16 h-2 bg-gray-400/80 rounded-full overflow-hidden">
                                    <div 
                                      className="h-full bg-blue-500 rounded-full transition-all duration-300" 
                                      style={{ width: `${Math.min((viewingProfile.receivesLeft || 0) / 50 * 100, 100)}%` }}
                                    />
                                  </div>
                                  <button
                                    className="p-1.5 rounded-full bg-white/30 hover:bg-white/40 transition-colors z-50"
                                    title="Gift Receives"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openGiftModal(viewingProfile);
                                    }}
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
                                  {viewingProfile.avatar}
                                </div>
                                <div>
                                  <h3 className="font-semibold text-gray-900">{viewingProfile.name}</h3>
                                  <p className="text-sm text-gray-600">{viewingProfile.location} • {calculateAge(viewingProfile.birthday)}岁</p>
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
                                  {viewingProfile.resources.map((resource, index) => (
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
                                  {viewingProfile.skills.map((skill, index) => (
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
                                  <div className="flex flex-wrap gap-1 overflow-x-hidden min-w-0">
                                    {viewingProfile.languages.map((language, index) => (
                                      <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs max-w-full whitespace-normal break-all">
                                        {language}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-semibold text-gray-900 text-sm mb-2">Hobbies</h4>
                                  <div className="flex flex-wrap gap-1 overflow-x-hidden min-w-0">
                                    {viewingProfile.hobbies.map((hobby, index) => (
                                      <span key={index} className="px-2 py-1 bg-pink-100 text-pink-800 rounded-full text-xs max-w-full whitespace-normal break-all">
                                        {hobby}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              </div>

                              {/* Projects */}
                              {viewingProfile.projects.length > 0 && (
                                <div>
                                  <h4 className="font-semibold text-gray-900 text-sm mb-2">Projects</h4>
                                  <div className="space-y-3">
                                    {viewingProfile.projects.map((project, index) => (
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
                                    {viewingProfile.goals.map((goal, index) => (
                                      <p key={index} className="text-gray-700 text-xs">• {goal}</p>
                                    ))}
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-semibold text-gray-900 text-sm mb-2">Looking For</h4>
                                  <div className="space-y-1">
                                    {viewingProfile.demands.map((demand, index) => (
                                      <p key={index} className="text-orange-600 text-xs">• {demand}</p>
                                    ))}
                                  </div>
                                </div>
                              </div>

                              {/* Institutions */}
                              {viewingProfile.institutions.length > 0 && (
                                <div>
                                  <h4 className="font-semibold text-gray-900 text-sm mb-2">Institutions</h4>
                                  <div className="space-y-3">
                                    {viewingProfile.institutions.map((institution, index) => (
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
                              {viewingProfile.university && (
                                <div>
                                  <h4 className="font-semibold text-gray-900 text-sm mb-2">University</h4>
                                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
                                    <div className="flex items-start justify-between gap-2 mb-1">
                                      <h5 className="font-medium text-gray-900 text-xs leading-tight flex-1 min-w-0 pr-2">
                                        {viewingProfile.university.name}
                                      </h5>
                                      {viewingProfile.university.verified && (
                                        <span className="text-blue-600 text-xs font-medium bg-blue-100 px-2 py-1 rounded-full whitespace-nowrap flex-shrink-0 flex items-center gap-1">
                                          <span>🎓</span>
                                          <span>Verified</span>
                                        </span>
                                      )}
                                    </div>
                                    <p className="text-blue-700 text-xs">Current University</p>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </>
      )}
      
      {/* Gift Modal */}
      <AnimatePresence>
        {showGiftModal && selectedForGift && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" style={{ zIndex: 140 }}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl p-6 w-full max-w-sm"
            >
              <h3 className="font-semibold text-gray-900 mb-4">Gift Receives to {selectedForGift.name}</h3>
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
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send Gift
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Whisper Message Dialog */}
      {pendingWhisperRequest && (
        <WhisperMessageDialog
          isOpen={showWhisperDialog}
          recipientName={pendingWhisperRequest.name}
          recipientAvatar={pendingWhisperRequest.avatar}
          onClose={handleWhisperDialogClose}
          onSend={handleWhisperSend}
        />
      )}
    </AnimatePresence>
  );
}