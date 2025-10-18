import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { X, Flag, User, Quote, Trash2, Upload, File, Image, Eye, Share2, ChevronDown, ChevronUp, Gift, MessageSquare } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { calculateAge } from '../utils/dateUtils';

export interface ContactedUser {
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
  whyMatch: string;
  receivesLeft?: number;
  contactedAt: Date;
  reported?: boolean;
  reportReason?: string;
  reportAttachments?: FileAttachment[];
  message?: string; // Whisper message sent to this user
}

export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
}

interface ContactHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  contacts: ContactedUser[];
  onReportContact: (contactId: string, reason: string, attachments?: FileAttachment[]) => void;
  onQuoteContact?: (contact: ContactedUser) => void;
  onRemoveContact?: (contactId: string) => void;
  onViewOriginalCard?: (contact: ContactedUser) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
}

export function ContactHistory({ isOpen, onClose, contacts, onReportContact, onQuoteContact, onRemoveContact, onViewOriginalCard, onGiftReceives }: ContactHistoryProps) {
  const { t } = useLanguage();
  const [reportingContact, setReportingContact] = useState<string | null>(null);
  const [reportReason, setReportReason] = useState('');
  const [reportAttachments, setReportAttachments] = useState<FileAttachment[]>([]);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [viewingProfile, setViewingProfile] = useState<ContactedUser | null>(null);
  const [showFullProfile, setShowFullProfile] = useState(false);
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [selectedForGift, setSelectedForGift] = useState<ContactedUser | null>(null);
  const [giftAmount, setGiftAmount] = useState('');

  const handleReport = () => {
    if (reportingContact && reportReason.trim()) {
      onReportContact(reportingContact, reportReason.trim(), reportAttachments);
      setReportingContact(null);
      setReportReason('');
      setReportAttachments([]);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      // Validate file type
      const allowedTypes = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'application/msword', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        alert('Please upload only images (JPG, PNG, GIF, WebP) or documents (PDF, DOC, DOCX, TXT)');
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }

      // Create file URL for preview
      const fileUrl = URL.createObjectURL(file);
      
      const attachment: FileAttachment = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        name: file.name,
        type: file.type,
        size: file.size,
        url: fileUrl,
      };

      setReportAttachments(prev => [...prev, attachment]);
    });

    // Reset input
    event.target.value = '';
  };

  const removeAttachment = (attachmentId: string) => {
    setReportAttachments(prev => {
      const attachment = prev.find(a => a.id === attachmentId);
      if (attachment) {
        URL.revokeObjectURL(attachment.url);
      }
      return prev.filter(a => a.id !== attachmentId);
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const isImageFile = (type: string) => {
    return type.startsWith('image/');
  };

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 60) return `${diffMinutes}${t('history.minutesAgo')}`;
    if (diffHours < 24) return `${diffHours}${t('history.hoursAgo')}`;
    if (diffDays < 7) return `${diffDays}${t('history.daysAgo')}`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}${t('history.weeksAgo')}`;
    return `${Math.floor(diffDays / 30)}${t('history.monthsAgo')}`;
  };

  const handleCardClick = (contactId: string) => {
    setSelectedCardId(selectedCardId === contactId ? null : contactId);
  };

  const handleViewOriginalCard = (contact: ContactedUser) => {
    setViewingProfile(contact);
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

  const openGiftModal = (contact: ContactedUser) => {
    setSelectedForGift(contact);
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

  if (!isOpen) return null;

  return (
    <>
      {/* Profile Card Modal - 移到最外层 */}
      <AnimatePresence>
        {viewingProfile && (
          <>
            {/* Modal Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
              style={{ zIndex: 100 }}
              onClick={closeProfileView}
            />
            
            {/* Profile Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="fixed inset-0 flex items-center justify-center z-50 p-4"
              style={{ zIndex: 110 }}
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

                          {/* Why We Match - 这里包含了该字段 */}
                          <div>
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-semibold text-gray-900 text-sm">Why We Match</h4>
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
                            <p className="text-gray-700 text-xs leading-relaxed">{viewingProfile.whyMatch}</p>
                          </div>
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

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
        onClick={onClose}
      />
      
      <motion.div
        initial={{ opacity: 0, y: '100%' }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: '100%' }}
        transition={{ duration: 0.3 }}
        className="fixed inset-x-0 bottom-0 z-50 bg-white rounded-t-3xl max-h-[80vh] overflow-hidden"
        style={{ maxWidth: '375px', margin: '0 auto' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <User size={16} className="text-white" />
            </div>
            <div>
              <h2 className="font-medium">{t('history.title')}</h2>
              <p className="text-xs text-gray-500">{contacts.length} people contacted</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {contacts.length === 0 ? (
            <div className="text-center py-12">
              <User size={48} className="text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 mb-2">{t('history.noContacts')}</p>
              <p className="text-sm text-gray-400">{t('history.noContactsDesc')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {contacts.map((contact) => (
                <Card 
                  key={contact.id} 
                  className={`p-4 cursor-pointer transition-all duration-200 relative ${
                    selectedCardId === contact.id ? 'ring-2 ring-blue-500 ring-opacity-50 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleCardClick(contact.id)}
                >
                  <div 
                    className={`flex items-center gap-3 transition-all duration-200 ${
                      selectedCardId === contact.id ? 'blur-sm opacity-60' : ''
                    }`}
                  >
                    <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-lg">
                      {contact.avatar}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium">{contact.name}</h3>
                        <span className="text-sm text-gray-500">
                          {formatRelativeTime(contact.contactedAt)}
                        </span>
                      </div>
                      
                      {contact.message && (
                        <div className="mt-2 bg-blue-50 border border-blue-200 rounded-lg p-2">
                          <div className="flex items-start gap-2">
                            <MessageSquare size={12} className="text-blue-600 mt-0.5 flex-shrink-0" />
                            <p className="text-xs text-blue-900 leading-relaxed break-words line-clamp-2">
                              {contact.message}
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {contact.reported && (
                        <div className="mt-2">
                          <Badge className="bg-red-100 text-red-700 text-xs">
                            {t('history.reported')}
                          </Badge>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Floating Action Buttons */}
                  {selectedCardId === contact.id && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8, x: 10 }}
                      animate={{ opacity: 1, scale: 1, x: 0 }}
                      className="absolute top-1/2 right-2 transform -translate-y-1/2 z-10 flex flex-row gap-2"
                    >
                      {/* View Original Card Button */}
                      {onViewOriginalCard && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="rounded-full w-12 h-12 p-0 bg-white hover:bg-purple-50 shadow-lg border-purple-200"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewOriginalCard(contact);
                          }}
                        >
                          <Eye size={16} className="text-purple-600" />
                        </Button>
                      )}
                      
                      {/* Quote Button */}
                      {onQuoteContact && (
                        <Button
                          size="sm"
                          className="rounded-full w-12 h-12 p-0 bg-blue-500 hover:bg-blue-600 shadow-lg"
                          onClick={(e) => {
                            e.stopPropagation();
                            onQuoteContact(contact);
                            setSelectedCardId(null);
                          }}
                        >
                          <Quote size={16} />
                        </Button>
                      )}
                      
                      {/* Remove Button */}
                      {onRemoveContact && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="rounded-full w-12 h-12 p-0 bg-white hover:bg-gray-50 shadow-lg border-gray-200"
                          onClick={(e) => {
                            e.stopPropagation();
                            onRemoveContact(contact.id);
                            setSelectedCardId(null);
                          }}
                        >
                          <X size={16} className="text-gray-600" />
                        </Button>
                      )}
                      
                      {/* Report Button */}
                      {!contact.reported && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="rounded-full w-12 h-12 p-0 bg-white hover:bg-red-50 shadow-lg border-red-200"
                          onClick={(e) => {
                            e.stopPropagation();
                            setReportingContact(contact.id);
                            setSelectedCardId(null);
                          }}
                        >
                          <Flag size={16} className="text-red-600" />
                        </Button>
                      )}
                    </motion.div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </motion.div>

      {/* Report Dialog */}
      <AnimatePresence>
        {reportingContact && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
              style={{ zIndex: 70 }}
              onClick={() => setReportingContact(null)}
            />
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 z-50 bg-white rounded-2xl p-6 flex flex-col"
              style={{ zIndex: 75, maxWidth: '320px', maxHeight: '400px', margin: 'auto' }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                  <Flag size={16} className="text-white" />
                </div>
                <h3 className="font-medium">{t('history.reportUser')}</h3>
              </div>
              
              <p className="text-sm text-gray-600 mb-4">
                {t('history.reportReason')}
              </p>
              
              <Textarea
                placeholder={t('history.reportPlaceholder')}
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                className="resize-none mb-4"
                rows={3}
              />
              
              {/* File Upload Section */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    {t('history.reportAttachments')}
                  </label>
                  <label className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors">
                    <Upload size={14} />
                    <span className="text-sm">{t('common.add')}</span>
                    <input
                      type="file"
                      multiple
                      accept="image/*,.pdf,.doc,.docx,.txt"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                </div>
                
                <p className="text-xs text-gray-500 mb-3">
                  {t('history.uploadDesc')}
                </p>
                
                {/* Attachments List */}
                {reportAttachments.length > 0 && (
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {reportAttachments.map(attachment => (
                      <div key={attachment.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                        {isImageFile(attachment.type) ? (
                          <div className="relative">
                            <img
                              src={attachment.url}
                              alt={attachment.name}
                              className="w-8 h-8 object-cover rounded"
                            />
                          </div>
                        ) : (
                          <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                            <File size={16} className="text-blue-600" />
                          </div>
                        )}
                        
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{attachment.name}</p>
                          <p className="text-xs text-gray-500">{formatFileSize(attachment.size)}</p>
                        </div>
                        
                        <button
                          onClick={() => removeAttachment(attachment.id)}
                          className="p-1 hover:bg-gray-200 rounded"
                        >
                          <Trash2 size={14} className="text-red-500" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setReportingContact(null)}
                >
                  {t('common.cancel')}
                </Button>
                <Button
                  className="flex-1 bg-red-500 hover:bg-red-600"
                  onClick={handleReport}
                  disabled={!reportReason.trim()}
                >
                  {t('history.submitReport')}
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Gift Modal */}
      <AnimatePresence>
        {showGiftModal && selectedForGift && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" style={{ zIndex: 150 }}>
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
    </>
  );
}