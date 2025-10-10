import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X, RefreshCw } from 'lucide-react';
import { Button } from './button';

interface ErrorMessageProps {
  message: string;
  onClose?: () => void;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({ message, onClose, onRetry, className = '' }: ErrorMessageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-red-800 text-sm">{message}</p>
          {onRetry && (
            <Button
              size="sm"
              variant="ghost"
              onClick={onRetry}
              className="mt-2 text-red-600 hover:text-red-700 p-0 h-auto"
            >
              <RefreshCw size={14} className="mr-1" />
              Try again
            </Button>
          )}
        </div>
        {onClose && (
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="text-red-500 hover:text-red-700 p-0 h-6 w-6"
          >
            <X size={14} />
          </Button>
        )}
      </div>
    </motion.div>
  );
}

interface ErrorBoundaryFallbackProps {
  error: Error;
  onRetry?: () => void;
  onReset?: () => void;
}

export function ErrorBoundaryFallback({ error, onRetry, onReset }: ErrorBoundaryFallbackProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-96 p-6 text-center">
      <div className="mb-4">
        <AlertTriangle size={48} className="text-red-500 mx-auto mb-2" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h2>
        <p className="text-gray-600 max-w-md">
          {error.message || 'An unexpected error occurred. Please try again.'}
        </p>
      </div>
      
      <div className="flex gap-3">
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw size={16} className="mr-2" />
            Try Again
          </Button>
        )}
        {onReset && (
          <Button onClick={onReset}>
            Go Back
          </Button>
        )}
      </div>
    </div>
  );
}

interface ErrorToastProps {
  message: string;
  isVisible: boolean;
  onClose: () => void;
  duration?: number;
}

export function ErrorToast({ message, isVisible, onClose, duration = 5000 }: ErrorToastProps) {
  React.useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.95 }}
          className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-red-500 text-white px-4 py-3 rounded-lg shadow-lg max-w-sm"
        >
          <div className="flex items-center gap-2">
            <AlertTriangle size={18} />
            <span className="text-sm font-medium flex-1">{message}</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={onClose}
              className="text-white hover:bg-red-600 p-0 h-6 w-6"
            >
              <X size={14} />
            </Button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
} 