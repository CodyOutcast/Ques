import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { X, Flag, User, Quote, Trash2, Upload, File, Image, Eye } from 'lucide-react';

export interface ContactedUser {
  id: string;
  name: string;
  avatar: string;
  skills: string[];
  location: string;
  matchScore: number;
  bio: string;
  projects: string[];
  contactedAt: Date;
  reported?: boolean;
  reportReason?: string;
  reportAttachments?: FileAttachment[];
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
}

export function ContactHistory({ isOpen, onClose, contacts, onReportContact, onQuoteContact, onRemoveContact, onViewOriginalCard }: ContactHistoryProps) {
  const [reportingContact, setReportingContact] = useState<string | null>(null);
  const [reportReason, setReportReason] = useState('');
  const [reportAttachments, setReportAttachments] = useState<FileAttachment[]>([]);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);

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
    
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    return `${Math.floor(diffDays / 30)}mo ago`;
  };

  const handleCardClick = (contactId: string) => {
    setSelectedCardId(selectedCardId === contactId ? null : contactId);
  };

  if (!isOpen) return null;

  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
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
              <h2 className="font-medium">Contact History</h2>
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
              <p className="text-gray-500 mb-2">No contacts yet</p>
              <p className="text-sm text-gray-400">Start networking to see your connections here</p>
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
                      
                      {contact.reported && (
                        <div className="mt-2">
                          <Badge className="bg-red-100 text-red-700 text-xs">
                            Reported
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
                            onViewOriginalCard(contact);
                            setSelectedCardId(null);
                            onClose();
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
              className="fixed inset-0 bg-black bg-opacity-50 z-60"
              onClick={() => setReportingContact(null)}
            />
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 z-60 bg-white rounded-2xl p-6 flex flex-col"
              style={{ maxWidth: '320px', maxHeight: '400px', margin: 'auto' }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                  <Flag size={16} className="text-white" />
                </div>
                <h3 className="font-medium">Report Contact</h3>
              </div>
              
              <p className="text-sm text-gray-600 mb-4">
                Please describe what dishonest information this person provided:
              </p>
              
              <Textarea
                placeholder="e.g., Claimed skills they don't have, misrepresented their role, provided false contact information..."
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                className="resize-none mb-4"
                rows={3}
              />
              
              {/* File Upload Section */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    Attach Proof (Optional)
                  </label>
                  <label className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors">
                    <Upload size={14} />
                    <span className="text-sm">Upload</span>
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
                  Upload images or documents as evidence (Max 10MB per file)
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
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-red-500 hover:bg-red-600"
                  onClick={handleReport}
                  disabled={!reportReason.trim()}
                >
                  Submit Report
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}