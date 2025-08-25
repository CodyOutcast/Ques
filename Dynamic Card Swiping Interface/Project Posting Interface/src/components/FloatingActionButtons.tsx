import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Plus, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface FloatingActionButtonsProps {
  isOpen: boolean;
  onCreateNew: () => void;
  onOpenDrafts: () => void;
  onClose: () => void;
}

export function FloatingActionButtons({ 
  isOpen, 
  onCreateNew, 
  onOpenDrafts, 
  onClose 
}: FloatingActionButtonsProps) {
  
  useEffect(() => {
    if (isOpen) {
      const handleClickOutside = (event: MouseEvent) => {
        const target = event.target as Element;
        if (!target.closest('[data-floating-buttons]')) {
          onClose();
        }
      };
      
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isOpen, onClose]);

  return (
    <div className="relative" data-floating-buttons>
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              onClick={onClose}
            />
            
            {/* Floating Buttons */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 z-50 space-y-4 mb-4">
              {/* Create New Project Button */}
              <motion.div
                initial={{ opacity: 0, y: 20, scale: 0.8 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 20, scale: 0.8 }}
                transition={{ delay: 0.1 }}
                className="flex flex-col items-center"
              >
                <Button
                  onClick={onCreateNew}
                  size="lg"
                  className="w-16 h-16 rounded-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xl transition-all duration-200 hover:shadow-3xl hover:scale-105"
                >
                  <Plus className="h-8 w-8" />
                </Button>
                <span className="text-sm font-medium text-foreground mt-2 bg-card/90 backdrop-blur-sm px-3 py-1 rounded-md border border-border/50 shadow-lg">
                  Create New Project
                </span>
              </motion.div>
              
              {/* Drafts Button */}
              <motion.div
                initial={{ opacity: 0, y: 20, scale: 0.8 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 20, scale: 0.8 }}
                transition={{ delay: 0.05 }}
                className="flex flex-col items-center"
              >
                <Button
                  onClick={onOpenDrafts}
                  size="lg"
                  variant="outline"
                  className="w-16 h-16 rounded-full bg-card/90 hover:bg-card border-2 border-primary/20 hover:border-primary/40 text-primary shadow-2xl transition-all duration-200 hover:shadow-3xl hover:scale-105 backdrop-blur-sm"
                >
                  <FileText className="h-8 w-8" />
                </Button>
                <span className="text-sm font-medium text-foreground mt-2 bg-card/90 backdrop-blur-sm px-3 py-1 rounded-md border border-border/50 shadow-lg">
                  Drafts
                </span>
              </motion.div>
            </div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}