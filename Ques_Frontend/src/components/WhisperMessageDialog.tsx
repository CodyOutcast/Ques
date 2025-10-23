import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Info } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { useLanguage } from '../contexts/LanguageContext';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from './ui/popover';

interface WhisperMessageDialogProps {
  isOpen: boolean;
  recipientName: string;
  recipientAvatar: string;
  onClose: () => void;
  onSend: (message: string) => void;
  defaultMessage?: string;
}

export function WhisperMessageDialog({
  isOpen,
  recipientName,
  recipientAvatar,
  onClose,
  onSend,
  defaultMessage = ''
}: WhisperMessageDialogProps) {
  const { t } = useLanguage();
  const [message, setMessage] = useState(defaultMessage);
  const maxWords = 100;
  
  // Count words in the message (handles both English and Chinese)
  const countWords = (text: string): number => {
    if (!text.trim()) return 0;
    
    // Remove extra whitespace
    const cleaned = text.trim().replace(/\s+/g, ' ');
    
    // For mixed content: split by whitespace and count
    // This works well for English and space-separated content
    const words = cleaned.split(/\s+/);
    
    // For Chinese characters, each character can be counted as part of a word
    // But we'll use a simple word count based on spaces for consistency
    return words.length;
  };
  
  const wordCount = countWords(message);
  const isOverLimit = wordCount > maxWords;
  
  console.log('🌟 WhisperMessageDialog render:', { 
    isOpen, 
    recipientName,
    hasBackdrop: isOpen 
  });

  useEffect(() => {
    if (isOpen) {
      setMessage(defaultMessage);
    }
  }, [isOpen, defaultMessage]);

  const handleSend = () => {
    if (message.trim()) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleSkip = () => {
    onSend('');
    setMessage('');
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
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            style={{ zIndex: 9999 }}
            onClick={onClose}
          />

          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-2xl mx-auto"
            style={{ 
              zIndex: 10000,
              width: 'calc(min(100vw, 450px) - 2rem)',
              maxWidth: 'calc(min(100vw, 450px) - 2rem)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-xl">
                  {recipientAvatar}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {t('whisper.sendingTo')} {recipientName}
                  </h3>
                  <p className="text-xs text-gray-500">{t('whisper.messageOptional')}</p>
                </div>
              </div>
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
            <div className="p-4 space-y-4">
              {/* Message Input */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    {t('whisper.yourMessage')}
                  </label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <button className="inline-flex items-center justify-center w-5 h-5 rounded-full hover:bg-gray-100 transition-colors">
                        <Info size={14} className="text-blue-500" />
                      </button>
                    </PopoverTrigger>
                    <PopoverContent 
                      className="w-80 p-3" 
                      align="start"
                      style={{ zIndex: 10001 }}
                    >
                      <div className="space-y-2">
                        <p className="text-xs text-gray-700 leading-relaxed">
                          {t('whisper.messageInfo')}
                        </p>
                        {message && message === defaultMessage && (
                          <div className="flex items-start gap-1.5 text-xs text-purple-600 bg-purple-50 px-2 py-1.5 rounded-md">
                            <Info size={12} className="flex-shrink-0 mt-0.5" />
                            <span>{t('whisper.aiGenerated')}</span>
                          </div>
                        )}
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>
                
                <Textarea
                  value={message}
                  onChange={(e) => {
                    const newValue = e.target.value;
                    const newWordCount = countWords(newValue);
                    
                    // Only update if within word limit
                    if (newWordCount <= maxWords) {
                      setMessage(newValue);
                    }
                  }}
                  placeholder={t('whisper.messagePlaceholder')}
                  className="min-h-[120px] resize-none"
                />
                <div className="flex items-center justify-end mt-1">
                  <p className={`text-xs font-medium ${isOverLimit ? 'text-red-500' : wordCount >= maxWords * 0.9 ? 'text-orange-500' : 'text-gray-400'}`}>
                    {wordCount}/{maxWords} {t('whisper.words') || 'words'}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex gap-3 p-4 border-t border-gray-200">
              <Button
                variant="outline"
                className="flex-1"
                onClick={handleSkip}
              >
                {t('whisper.skipMessage')}
              </Button>
              <Button
                className="flex-1 bg-blue-500 hover:bg-blue-600"
                onClick={handleSend}
                disabled={!message.trim() || isOverLimit}
              >
                <Send size={16} className="mr-2" />
                {t('whisper.sendWhisper')}
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

