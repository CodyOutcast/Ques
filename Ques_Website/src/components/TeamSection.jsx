import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { optimizeAnimation } from '../utils/optimizeAnimation';
import CodyPic from '../assets/profile_pic/Cody_Chen.jpg';
import WilliamPic from '../assets/profile_pic/William_Kusnomo.jpg';
import IrenePic from '../assets/profile_pic/irene_chen.png';
import JimmyPic from '../assets/profile_pic/Jimmy_Chen.png';

const TeamSection = ({ isVisible }) => {
  const { t } = useTranslation();

  const teamMembers = [
    {
      name: "Cody",
      title: t("team_section.ceo_role"),
      image: CodyPic,
      bio: t("team_section.ceo_bio"),
      xLink: "https://x.com/CodyOutcast"
    },
    {
      name: "William",
      title: t("team_section.coo_role"),
      image: WilliamPic,
      bio: t("team_section.coo_bio"),
      xLink: "https://x.com/William41681372"
    },
    {
      name: "Irene",
      title: t("team_section.cmo_role"),
      image: IrenePic,
      bio: t("team_section.cmo_bio"),
      xLink: "https://x.com/imIreneChen"
    },
    {
      name: "Jimmy",
      title: t("team_section.cto_role"),
      image: JimmyPic,
      bio: t("team_section.cto_bio"),
      xLink: "https://x.com/J1mmyC231"
    }
  ];

  return (
    <motion.div 
      className='absolute w-full h-full flex flex-col
        items-center justify-start overflow-auto py-6 md:py-10 lg:py-16 text-white lg:px-20 px-3 sm:px-5'
      initial={{ opacity: 0, y: 50 }}
      animate={{
        opacity: isVisible ? 1 : 0,
        y: isVisible ? 0 : -50
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
        className="text-center w-full mt-16 sm:mt-14 md:mt-10 lg:mt-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ 
          opacity: isVisible ? 1 : 0,
          y: isVisible ? 0 : 20 
        }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-5">
          {t("team_section.title")}
        </h2>
        <p className="text-lg md:text-xl text-gray-100 max-w-2xl mx-auto mb-6 md:mb-10">
          {t("team_section.tagline")}
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 md:gap-8 lg:gap-10 mt-4 md:mt-8">
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              animate={{ 
                opacity: isVisible ? 1 : 0,
                y: isVisible ? 0 : 50 
              }}
              transition={{ 
                duration: 0.5,
                delay: isVisible ? 0.3 + (index * 0.1) : 0,
                ...optimizeAnimation.optimizedSpring
              }}
              style={optimizeAnimation.gpuAcceleration}
              className="bg-white/10 backdrop-blur-lg rounded-xl p-3 sm:p-4 md:p-6 lg:p-8 flex flex-col items-center"
            >
              <a 
                href={member.xLink}
                target="_blank"
                rel="noopener noreferrer"
                className="w-16 h-16 sm:w-20 sm:h-20 md:w-28 md:h-28 lg:w-32 lg:h-32 rounded-full overflow-hidden mb-2 md:mb-4 border-2 border-blue-400 transition-transform hover:scale-110 cursor-pointer"
              >
                <img 
                  src={member.image} 
                  alt={member.name} 
                  className="w-full h-full object-cover"
                />
              </a>
              <a 
                href={member.xLink}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-300 transition-colors cursor-pointer"
              >
                <h3 className="text-sm sm:text-base md:text-lg lg:text-xl font-bold mb-1 md:mb-2">{member.name}</h3>
              </a>
              <p className="text-blue-300 mb-1 md:mb-3 text-xs sm:text-sm md:text-base">{member.title}</p>
              <p className="text-gray-200 text-xs leading-tight sm:leading-normal md:leading-relaxed text-center line-clamp-3 sm:line-clamp-none md:text-sm lg:text-base">{member.bio}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default TeamSection;
