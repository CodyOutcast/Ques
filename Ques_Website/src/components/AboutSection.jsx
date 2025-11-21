import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { optimizeAnimation } from '../utils/optimizeAnimation';

const AboutSection = ({ isVisible }) => {
  const { t } = useTranslation();

  return (
    <motion.div 
      className='absolute w-full h-full flex flex-col 
        items-center justify-center text-white lg:px-20 px-10'
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
        className="w-full max-w-6xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ 
          opacity: isVisible ? 1 : 0,
          y: isVisible ? 0 : 20 
        }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {/* Title */}
        <motion.h2
          className="text-5xl md:text-6xl lg:text-7xl font-bold mb-8 text-center font-tech text-glitch"
          data-text={t("about_section.title")}
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 20 
          }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          {t("about_section.title")}
        </motion.h2>

        {/* Description */}
        <motion.p
          className="text-base md:text-lg text-slate-300 leading-relaxed mb-8 text-center max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 20 
          }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {t("about_section.description")}
        </motion.p>

        {/* Mission and Vision Cards */}
        <motion.div
          className="grid md:grid-cols-2 gap-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 30 
          }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {/* Mission */}
          <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl p-8 border border-slate-700/50 shadow-2xl shadow-black/50 hover-glow">
            <h4 className="text-2xl md:text-3xl font-bold mb-4 bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent font-mono-accent">
              {t("about_section.mission_title")}
            </h4>
            <p className="text-base md:text-lg text-slate-300 leading-relaxed">
              {t("about_section.mission_description")}
            </p>
          </div>

          {/* Vision */}
          <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl p-8 border border-slate-700/50 shadow-2xl shadow-black/50 hover-glow">
            <h4 className="text-2xl md:text-3xl font-bold mb-4 bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent font-mono-accent">
              {t("about_section.vision_title")}
            </h4>
            <p className="text-base md:text-lg text-slate-300 leading-relaxed">
              {t("about_section.vision_description")}
            </p>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default AboutSection;
