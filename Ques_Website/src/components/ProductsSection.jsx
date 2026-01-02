import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { optimizeAnimation } from '../utils/optimizeAnimation';

const ProductsSection = ({ isVisible }) => {
  const { t } = useTranslation();

  const features = [
    t("products_section.geoseer_feature_1"),
    t("products_section.geoseer_feature_2"),
    t("products_section.geoseer_feature_3"),
    t("products_section.geoseer_feature_4"),
    t("products_section.geoseer_feature_5"),
    t("products_section.geoseer_feature_6"),
  ];

  return (
    <motion.div 
      className='absolute w-full h-full flex flex-col 
        items-center justify-start md:justify-center text-white lg:px-20 md:px-10 px-4 py-16 md:py-0 overflow-y-auto'
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
        className="w-full max-w-5xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ 
          opacity: isVisible ? 1 : 0,
          y: isVisible ? 0 : 20 
        }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {/* Header */}
        <div className="text-center mb-4 md:mb-6">
          <motion.h2
            className="text-2xl sm:text-3xl md:text-5xl font-bold mb-4 md:mb-6 font-tech tracking-wide"
            initial={{ opacity: 0, y: 20 }}
            animate={{ 
              opacity: isVisible ? 1 : 0,
              y: isVisible ? 0 : 20 
            }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            {t("products_section.title")}
          </motion.h2>
        </div>

        {/* GeoSeer Product Card */}
        <motion.div
          className="bg-slate-900/60 backdrop-blur-xl rounded-2xl p-5 md:p-6 border border-slate-700/50 shadow-2xl shadow-black/50 hover-glow"
          initial={{ opacity: 0, y: 30 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 30 
          }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          {/* Product Header */}
          <div className="flex items-center gap-3 mb-4">
            <a 
              href="https://geoseeer.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex-shrink-0 transition-transform hover:scale-110 cursor-pointer"
            >
              <div className="w-12 h-12 md:w-14 md:h-14 rounded-full bg-gradient-to-br from-cyan-600 to-blue-600 p-2 flex items-center justify-center overflow-hidden shadow-lg shadow-cyan-500/20">
                <img 
                  src="/geoseer-logo.png" 
                  alt="GeoSeer Logo" 
                  className="w-full h-full object-cover rounded-full"
                />
              </div>
            </a>
            <div>
              <a 
                href="https://geoseeer.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-cyan-300 transition-colors cursor-pointer"
              >
                <h3 className="text-xl md:text-2xl font-bold mb-0.5">
                  {t("products_section.geoseer_title")}
                </h3>
              </a>
              <p className="text-sm md:text-base bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent font-mono-accent">
                {t("products_section.geoseer_tagline")}
              </p>
            </div>
          </div>

          {/* Description */}
          <p className="text-xs md:text-sm text-slate-300 leading-relaxed mb-4">
            {t("products_section.geoseer_description")}
          </p>

          {/* Features Grid - Hidden on mobile */}
          <div className="mb-4 hidden sm:block">
            <h4 className="text-base md:text-lg font-bold mb-2 bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent font-mono-accent">
              {t("products_section.geoseer_features_title")}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 sm:gap-2">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ 
                    opacity: isVisible ? 1 : 0,
                    x: isVisible ? 0 : -20 
                  }}
                  transition={{ duration: 0.4, delay: 0.7 + (index * 0.1) }}
                  className="flex items-start gap-1.5 sm:gap-2 bg-slate-800/50 border border-slate-700/30 rounded-lg p-2 sm:p-2.5"
                >
                  <div className="w-1 h-1 bg-cyan-400 rounded-full mt-1.5 flex-shrink-0" />
                  <p className="text-slate-300 text-xs leading-relaxed">
                    {feature}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* CTA Button */}
          <div className="flex justify-center">
            <a
              href="https://geoseeer.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold px-5 py-2.5 text-sm rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg shadow-cyan-500/20"
            >
              {t("products_section.visit_website")}
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </a>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default ProductsSection;
