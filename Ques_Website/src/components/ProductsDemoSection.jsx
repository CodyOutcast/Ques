import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { FiAlertCircle } from 'react-icons/fi';

const ProductsDemoSection = ({ isVisible }) => {
  const { t } = useTranslation();
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const videoRef = useRef(null);

  const handleLoadedData = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    setIsLoaded(true);
  };

  return (
    <motion.div 
      className='absolute w-full h-full flex flex-col 
        items-center justify-center text-white lg:px-20 px-6'
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
        <div className="text-center mb-4">
          <motion.h2
            className="text-4xl md:text-5xl font-bold mb-4 font-tech tracking-wide"
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

        {/* Demo Video Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 30 
          }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="max-w-4xl mx-auto"
        >
          <div className="group relative">
            {/* Glow effect layer */}
            <div className="absolute -inset-1 bg-gradient-to-br from-cyan-600/20 via-blue-600/20 to-cyan-600/20 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            {/* Video container */}
            <motion.div
              className="relative rounded-3xl border border-slate-700/50 backdrop-blur-sm bg-slate-900/60 overflow-hidden shadow-2xl shadow-black/50"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.3 }}
            >
              {/* Loading shimmer */}
              {!isLoaded && !hasError && (
                <div className="absolute inset-0 z-2 overflow-hidden bg-white/0.03">
                  <div className="skeleton-shimmer" />
                </div>
              )}

              {/* Error state */}
              {hasError && (
                <div className="absolute inset-0 z-2 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm">
                  <FiAlertCircle className="w-12 h-12 text-red-400 mb-4" />
                  <p className="text-white text-lg font-semibold mb-2">Failed to load demo video</p>
                  <p className="text-slate-400 text-sm">Please check the video file</p>
                </div>
              )}

              {/* Video element */}
              <video
                ref={videoRef}
                autoPlay
                loop
                muted
                playsInline
                onLoadedData={handleLoadedData}
                onError={handleError}
                className={`w-full h-auto transition-opacity duration-500 ${
                  isLoaded && !hasError ? 'opacity-100' : 'opacity-0'
                }`}
              >
                <source src="/demo.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default ProductsDemoSection;
