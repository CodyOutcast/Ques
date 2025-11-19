import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { FiMail } from 'react-icons/fi';

// Social Media Icons
function InstagramIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x={3} y={3} width={18} height={18} rx={5} />
      <circle cx={12} cy={12} r={3.5} />
      <circle cx={17.5} cy={6.5} r={1.1} fill="currentColor" stroke="none" />
    </svg>
  );
}

function TiktokIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M14.75 4a.75.75 0 0 1 .75-.75h2.4c.05 1.2.68 2.1 1.63 2.73a4.9 4.9 0 0 0 2.04.7.75.75 0 0 1 .63.74V9.2a.75.75 0 0 1-.9.74 7.3 7.3 0 0 1-2.48-.6v4.69a5.92 5.92 0 1 1-5.92-5.92c.2 0 .4.02.6.05v2.36a3.34 3.34 0 1 0 2.74 3.28V4.75a.75.75 0 0 1 .76-.75Z" />
    </svg>
  );
}

function FacebookIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.4} {...props}>
      <rect x={3} y={3} width={18} height={18} rx={3} />
      <path d="M13.5 8h2.25V5.75H13.5A2.75 2.75 0 0 0 10.75 8.5V10H9v2.5h1.75V18h2.75v-5.5h2.26L16 10H13.5V8.75c0-.43.32-.75.75-.75Z" fill="currentColor" stroke="none" />
    </svg>
  );
}

function YoutubeIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinejoin="round" {...props}>
      <rect x={3} y={7} width={18} height={10} rx={3} />
      <path d="m11 10.5 4 1.5-4 1.5v-3Z" fill="currentColor" stroke="none" />
    </svg>
  );
}

function LinkedinIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.4} {...props}>
      <rect x={3} y={3} width={18} height={18} rx={3} />
      <path d="M7 17V10" strokeLinecap="round" />
      <circle cx={7} cy={7} r={1} fill="currentColor" stroke="none" />
      <path d="M12 17v-3.2c0-1.54 1.24-2.8 2.78-2.8h.22a2.5 2.5 0 0 1 2.5 2.5V17" strokeLinecap="round" />
      <path d="M12 17v-4" strokeLinecap="round" />
    </svg>
  );
}

function XIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

const ContactSection = ({ isVisible }) => {
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
        className="w-full max-w-2xl text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ 
          opacity: isVisible ? 1 : 0,
          y: isVisible ? 0 : 20 
        }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {/* Title */}
        <motion.h2
          className="text-4xl md:text-5xl font-bold mb-3 font-tech tracking-wide"
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 20 
          }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          {t("contact_section.title")}
        </motion.h2>

        {/* Subtitle */}
        <motion.p
          className="text-base md:text-lg text-slate-300 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 20 
          }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {t("contact_section.subtitle")}
        </motion.p>

        {/* Email & Phone Combined Card */}
        <motion.div
          className="mb-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 30 
          }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 max-w-md mx-auto border border-slate-700/50 shadow-xl hover-glow">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Email */}
              <div className="text-center md:border-r md:border-slate-700/50 md:pr-4">
                <div className="flex items-center justify-center mb-2">
                  <FiMail className="text-cyan-400 w-6 h-6" />
                </div>
                <h3 className="text-sm font-semibold mb-2 text-cyan-400 font-mono-accent">
                  {t("contact_section.email_label")}
                </h3>
                <a
                  href="mailto:cody@quesx.com"
                  className="text-slate-300 hover:text-cyan-300 transition-colors text-sm"
                >
                  cody@quesx.com
                </a>
              </div>

              {/* Phone */}
              <div className="text-center md:pl-4">
                <div className="flex items-center justify-center mb-2">
                  <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <h3 className="text-sm font-semibold mb-2 text-cyan-400 font-mono-accent">
                  {t("about_section.contact_title")}
                </h3>
                <a
                  href={`tel:${t('about_section.contact_value')}`}
                  className="text-slate-300 hover:text-cyan-300 transition-colors text-sm"
                >
                  {t('about_section.contact_value')}
                </a>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Address Card */}
        <motion.div
          className="mb-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 30 
          }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl p-5 max-w-md mx-auto border border-slate-700/50 shadow-xl hover-glow">
            <h3 className="text-sm font-semibold mb-2 text-cyan-400 font-mono-accent">
              {t("about_section.address_title")}
            </h3>
            <p className="text-slate-300 text-xs">
              {t('about_section.address_value')}
            </p>
          </div>
        </motion.div>

        {/* Social Media */}
        <motion.div
          className="bg-slate-900/60 backdrop-blur-xl rounded-xl p-5 max-w-md mx-auto border border-slate-700/50 shadow-xl hover-glow"
          initial={{ opacity: 0, y: 30 }}
          animate={{ 
            opacity: isVisible ? 1 : 0,
            y: isVisible ? 0 : 30 
          }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          <h3 className="text-sm font-semibold mb-3 text-cyan-400 font-mono-accent">
            {t("contact_section.social_media")}
          </h3>
          <div className="flex justify-center items-center gap-5">
            <a
              href="https://x.com/GeoSeeer"
              className="text-slate-400 hover:text-cyan-400 transition-colors transform hover:scale-110"
              aria-label="X"
              target="_blank"
              rel="noopener noreferrer"
            >
              <XIcon className="w-5 h-5" />
            </a>
            <a
              href="https://www.instagram.com/geoseeer/"
              className="text-slate-400 hover:text-cyan-400 transition-colors transform hover:scale-110"
              aria-label="Instagram"
              target="_blank"
              rel="noopener noreferrer"
            >
              <InstagramIcon className="w-5 h-5" />
            </a>
            <a
              href="https://www.tiktok.com/@geoseeer"
              className="text-slate-400 hover:text-cyan-400 transition-colors transform hover:scale-110"
              aria-label="TikTok"
              target="_blank"
              rel="noopener noreferrer"
            >
              <TiktokIcon className="w-5 h-5" />
            </a>
            <a
              href="https://www.facebook.com/profile.php?id=61583773556872"
              className="text-slate-400 hover:text-cyan-400 transition-colors transform hover:scale-110"
              aria-label="Facebook"
              target="_blank"
              rel="noopener noreferrer"
            >
              <FacebookIcon className="w-5 h-5" />
            </a>
            <a
              href="https://www.youtube.com/@geoseeer"
              className="text-slate-400 hover:text-cyan-400 transition-colors transform hover:scale-110"
              aria-label="YouTube"
              target="_blank"
              rel="noopener noreferrer"
            >
              <YoutubeIcon className="w-5 h-5" />
            </a>
            <a
              href="https://www.linkedin.com/company/geoseer"
              className="text-slate-400 hover:text-cyan-400 transition-colors transform hover:scale-110"
              aria-label="LinkedIn"
              target="_blank"
              rel="noopener noreferrer"
            >
              <LinkedinIcon className="w-5 h-5" />
            </a>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default ContactSection;
