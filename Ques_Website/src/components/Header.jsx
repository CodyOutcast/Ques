import { motion, AnimatePresence } from 'framer-motion';
import { FiMenu, FiX } from 'react-icons/fi';
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { optimizeAnimation } from '../utils/optimizeAnimation';
import logo from '../assets/logo.ico';

const Header = ({ isChinese, toggleLanguage, onNavigate, activeSection }) => {
    const [isOpen, setIsOpen] = useState(false);
    const { t } = useTranslation();

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    };

    // Navigation items for the new 4-section design
    const NAVIGATION_ITEMS = [
      { name: t("header.about"), id: "about" },
      { name: t("header.products"), id: "products" },
      { name: t("header.team"), id: "team" },
      { name: t("header.contact"), id: "contact" },
    ];

    const handleNavClick = (sectionId) => {
        onNavigate(sectionId);
        setIsOpen(false);
    };

    return (
        <>
        <style>
          {`
            .gradient-overlay {
              position: fixed;
              top: 0;
              left: 0;
              right: 16px;
              height: calc(200px + env(safe-area-inset-top, 0px));
              pointer-events: none;
              z-index: 20;
              background: linear-gradient(
                to bottom,
                rgba(29, 78, 216, 1.0) 0%,
                rgba(29, 78, 216, 0.9) calc(30px + env(safe-area-inset-top, 0px)),
                transparent calc(80px + env(safe-area-inset-top, 0px))
              );
            }
          `}
        </style>
        
        <header className="absolute w-full z-50 transition-all duration-300" 
                style={{ 
                  paddingTop: 'env(safe-area-inset-top, 0px)',
                  top: 0
                }}>
          <div className="relative z-30">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16 md:h-20 relative">
              <motion.div 
                initial={{ opacity: 0, x: -100 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ 
                  ...optimizeAnimation.optimizedSpring,
                  delay: 0.2,
                }}
                style={optimizeAnimation.gpuAcceleration}
                className="flex items-center"
              >
                <div className="h-10 w-10 rounded-xl bg-gradient-to-r from-blue-500 to-green-400 flex items-center justify-center mr-3">
                  <img 
                    src={logo} 
                    alt="Logo" 
                    className="h-full w-full object-contain"
                  />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-200 to-green-300 bg-clip-text text-transparent">
                  {t("header.logo_text")}
                </span>
              </motion.div>
  
              <nav className="lg:flex hidden items-center justify-center absolute left-1/2 transform -translate-x-1/2">
                <div className="flex items-center space-x-16">
                  {NAVIGATION_ITEMS.map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: -20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        ...optimizeAnimation.optimizedSpring,
                        delay: 0.5 + index * 0.05,
                      }}
                      style={optimizeAnimation.gpuAcceleration}
                    >
                      <button
                        onClick={() => handleNavClick(item.id)}
                        className={`relative text-gray-200 
                          ${activeSection === item.id 
                            ? 'text-blue-400' 
                            : 'hover:text-blue-400'}
                          bg-transparent
                          h-8 flex items-center
                          font-medium text-lg rounded-md
                          transition-all duration-300 group`}
                      >
                        {item.name}
                        <span className={`absolute bottom-0 left-0 h-0.5
                          bg-blue-400
                          transition-all duration-300 ease-out
                          ${activeSection === item.id 
                            ? 'w-full' 
                            : 'w-0 group-hover:w-full'}`}
                        />
                      </button>
                    </motion.div>
                  ))}
                </div>
              </nav>
  
              <div className="md:flex hidden space-x-4 items-center">
                <motion.div
                  initial={{ opacity: 0, scale: 0.5 }} 
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.2, duration: 0.5 }}
                  className="relative w-12 h-6 bg-gray-600 rounded-full p-1 cursor-pointer"
                  onClick={toggleLanguage}
                >
                  <motion.div
                    className="w-4 h-4 bg-white rounded-full shadow-md"
                    animate={{ x: isChinese ? 0 : 24 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  />
                  <span className="absolute inset-0 flex items-center justify-end pr-2 text-xs text-white" style={{ opacity: isChinese ? 1 : 0 }}>CN</span>
                  <span className="absolute inset-0 flex items-center justify-start pl-2 text-xs text-white" style={{ opacity: isChinese ? 0 : 1 }}>EN</span>
                </motion.div>
              </div>
  
              <div className="md:hidden flex items-center">
                <motion.button 
                  whileTap={{ scale: 0.9 }}
                  onClick={toggleMenu} 
                  className="text-gray-200 hover:text-blue-500 transition-colors duration-300 p-2 rounded-md">
                  {isOpen ? <FiX className="h-8 w-8" /> : <FiMenu className="h-8 w-8" />}
                </motion.button>
              </div>
            </div>

            {/* Mobile menu */}
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ 
                opacity: isOpen ? 1 : 0, 
                height: isOpen ? 'auto' : 0 
              }}
              transition={{
                opacity: { duration: 0.2, ease: "easeOut" },
                height: { 
                  duration: 0.25,
                  ease: [0.4, 0, 0.2, 1]
                }
              }}
              className="md:hidden overflow-hidden bg-gradient-to-b from-[#2f50dd]/95 to-gray-800 shadow-lg px-4 py-5 space-y-5"
            >
              <nav className="flex flex-col space-y-3">
                {NAVIGATION_ITEMS.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => handleNavClick(item.id)}
                    className={`text-gray-300 font-medium py-2 text-left
                      ${activeSection === item.id ? 'text-blue-400' : ''}`}
                  >
                    {item.name}
                  </button>
                ))}
              </nav>

              {/* Mobile Language Toggle */}
              <div className="pt-4 border-t border-white flex space-x-4">
                <span className="font-medium text-gray-300">{t("header.language")}</span>
                <motion.div
                    className="relative w-12 h-6 bg-gray-600 rounded-full p-1 cursor-pointer"
                    onClick={toggleLanguage}
                >
                    <motion.div
                        className="w-4 h-4 bg-white rounded-full shadow-md"
                        animate={{ x: isChinese ? 0 : 24 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    />
                    <span className="absolute inset-0 flex items-center justify-end pr-2 text-xs text-white" style={{ opacity: isChinese ? 1 : 0 }}>CN</span>
                    <span className="absolute inset-0 flex items-center justify-start pl-2 text-xs text-white" style={{ opacity: isChinese ? 0 : 1 }}>EN</span>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </header>
        </>
    );
};

export default Header;
