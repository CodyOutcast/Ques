import React from 'react';
import { currentLanguage, setLanguage, t } from '../translations';

interface LanguageSwitcherProps {
  className?: string;
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = "" }) => {
  const toggleLanguage = () => {
    const newLanguage = currentLanguage === 'zh' ? 'en' : 'zh';
    setLanguage(newLanguage);
    // Force a re-render by updating the component state
    window.location.reload();
  };

  return (
    <button
      onClick={toggleLanguage}
      className={`px-3 py-1 text-sm font-medium rounded-md border transition-colors ${className}`}
    >
      {currentLanguage === 'zh' ? 'English' : '中文'}
    </button>
  );
};

// Hook for language switching
export const useLanguage = () => {
  const switchLanguage = (language: 'en' | 'zh') => {
    setLanguage(language);
    window.location.reload();
  };

  return {
    currentLanguage,
    switchLanguage,
    t,
  };
}; 