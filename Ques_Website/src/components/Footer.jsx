import React from 'react';
import { useTranslation } from 'react-i18next';

const Footer = () => {
  const { t } = useTranslation();
  
  return (
    <footer 
      className="absolute bottom-0 w-full py-2 text-center text-slate-400 text-xs flex flex-col items-center"
      style={{
        paddingBottom: 'calc(env(safe-area-inset-bottom) + 0.5rem)',
        marginBottom: 'env(safe-area-inset-bottom, 20px)'
      }}
    >
      <p className="flex items-center space-x-2">
        <span>{t('footer.company')}</span>
        <span>|</span>
        <a 
          href="https://beian.miit.gov.cn/" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="hover:text-cyan-400 transition-colors"
        >
          {t('footer.icp')}
        </a>
        <span>|</span>
        <a 
          href=" " 
          rel="noreferrer" 
          target="_blank"
          className="inline-flex items-center hover:text-cyan-400 transition-colors"
        >
          <img 
            src="/police_logo.jpg" 
            alt="Police Logo" 
            className="h-4 mr-1" 
          />
          <span className="text-xs">粤公网安备44030002008139号</span>
        </a>
      </p>
    </footer>
  );
};

export default Footer;
