import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import logoImage from '../assets/logo.ico';

const HomeSection = ({ isVisible }) => {
  const { t } = useTranslation();

  return (
    <motion.div 
      className='absolute w-full h-full flex flex-col 
        items-center justify-center text-white'
      initial={{ opacity: 0, y: 50 }}
      animate={{
        opacity: isVisible ? 1 : 0,
        y: isVisible ? 0 : (isVisible === false ? -50 : 50)
      }}
      transition={{
        duration: 0.5,
        ease: "easeInOut"
      }}
      style={{
        pointerEvents: isVisible ? 'auto' : 'none'
      }}
    >
      <motion.div
        className="flex flex-col items-center justify-center"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ 
          opacity: isVisible ? 1 : 0,
          scale: isVisible ? 1 : 0.8
        }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {/* Logo */}
        <motion.img
          src={logoImage}
          alt="Ques Logo"
          className="w-32 h-32 md:w-40 md:h-40 lg:w-48 lg:h-48 mb-8 object-contain"
          initial={{ opacity: 0, y: -20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : -20 
          }}
          transition={{ duration: 0.5, delay: 0.3 }}
        />

        {/* Company Name */}
        <motion.h1
          className="text-3xl md:text-4xl lg:text-5xl font-semibold mb-4 bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent font-mono-accent text-center tracking-tight px-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 20 
          }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {t("home_section.company_name")}
        </motion.h1>

        {/* Tagline */}
        <motion.p
          className="text-xl md:text-2xl lg:text-3xl font-medium bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent font-mono-accent text-center px-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 20 
          }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          {t("home_section.tagline")}
        </motion.p>
      </motion.div>
    </motion.div>
  );
};

export default HomeSection;
