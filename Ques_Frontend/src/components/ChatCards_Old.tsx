import { useState, useRef } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { Share2, ChevronDown, ChevronUp } from 'lucide-react';

interface Profile {
  id: string;
  name: string;
  age: string;
  gender: string;
  avatar: string;
  location: string;
  hobbies: string[];
  languages: string[];
  skills: string[];
  resources: string[];
  projects: { 
    title: string; 
    role: string; 
    description: string; 
    referenceLinks: string[] 
  }[];
  goals: string[];
  demands: string[];
  institutions: { 
    name: string; 
    role: string; 
    description: string; 
    verified: boolean;
  }[];
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  whyMatch: string;
}

interface ChatCardsProps {
  profiles: Profile[];
  onSwipeLeft: (profile: Profile) => void;
  onSwipeRight: (profile: Profile) => void;
}

export default function ChatCards({ profiles, onSwipeLeft, onSwipeRight }: ChatCardsProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showFullProfile, setShowFullProfile] = useState(false);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
  const constraintsRef = useRef(null);
  
  if (profiles.length === 0 || currentIndex >= profiles.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">No more profiles to show</p>
      </div>
    );
  }

  const currentProfile = profiles[currentIndex];

  const handleDragEnd = (event: any, info: PanInfo) => {
    const { offset, velocity } = info;
    
    if (Math.abs(offset.x) > 100 || Math.abs(velocity.x) > 500) {
      if (offset.x > 0) {
        setExitDirection('right');
        onSwipeRight(currentProfile);
      } else {
        setExitDirection('left');
        onSwipeLeft(currentProfile);
      }
      
      setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
        setExitDirection(null);
        setShowFullProfile(false);
      }, 300);
    }
  };

  const handleShareProfile = () => {
    console.log('Sharing profile:', currentProfile.name);
  };

  const toggleExtendedProfile = () => {
    setShowFullProfile(!showFullProfile);
  };

  return (
    <div className="relative w-full flex flex-col items-center">
      <div className="relative" ref={constraintsRef}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentProfile.id}
            className="relative cursor-grab active:cursor-grabbing"
            style={{ width: '300px', height: '400px' }}
            drag={showFullProfile ? false : "x"}
            dragConstraints={constraintsRef}
            onDragEnd={handleDragEnd}
            initial={{ opacity: 1, x: 0, rotate: 0 }}
            exit={{
              x: exitDirection === 'left' ? -300 : exitDirection === 'right' ? 300 : 0,
              opacity: 0,
              rotate: exitDirection === 'left' ? -30 : exitDirection === 'right' ? 30 : 0
            }}
            transition={{ duration: 0.3 }}
          >
            <div className="relative w-full h-full bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
              <div className="relative w-full h-full flex items-center justify-center">
                <div className="text-9xl select-none" style={{ fontSize: '12rem', lineHeight: '1' }}>
                  {currentProfile.avatar}
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-6 text-white z-10">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-bold">
                    {currentProfile.name}
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={handleShareProfile}
                      className="p-2 bg-white/20 backdrop-blur-sm rounded-full hover:bg-white/30 transition-colors"
                    >
                      <Share2 size={16} />
                    </button>
                    <button
                      onClick={toggleExtendedProfile}
                      className="p-2 bg-blue-500 rounded-full hover:bg-blue-600 transition-colors"
                    >
                      {showFullProfile ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </button>
                  </div>
                </div>
                <p className="text-white/90 text-xs line-clamp-1">
                  {currentProfile.oneSentenceIntro || currentProfile.bio}
                </p>

                {/* Expanded profile content */}
                {showFullProfile && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden mt-4"
                  >
                    <div className="bg-black/20 backdrop-blur-sm rounded-xl p-4 max-h-48 overflow-y-auto space-y-3">
                      {/* Resources */}
                      <div>
                        <h4 className="text-white font-medium text-sm mb-1">Resources</h4>
                        <div className="flex flex-wrap gap-1">
                          {currentProfile.resources.map((resource, index) => (
                            <span key={index} className="px-2 py-1 bg-green-500/20 rounded-full text-xs text-white">
                              {resource}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Skills */}
                      <div>
                        <h4 className="text-white font-medium text-sm mb-1">Skills</h4>
                        <div className="flex flex-wrap gap-1">
                          {currentProfile.skills.map((skill, index) => (
                            <span key={index} className="px-2 py-1 bg-white/20 rounded-full text-xs text-white">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Languages & Hobbies */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <h4 className="text-white font-medium text-sm mb-1">Languages</h4>
                          <div className="flex flex-wrap gap-1">
                            {currentProfile.languages.map((language, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-500/20 rounded-full text-xs text-white">
                                {language}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-white font-medium text-sm mb-1">Hobbies</h4>
                          <div className="flex flex-wrap gap-1">
                            {currentProfile.hobbies.map((hobby, index) => (
                              <span key={index} className="px-2 py-1 bg-purple-500/20 rounded-full text-xs text-white">
                                {hobby}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Full Bio */}
                      <div>
                        <h4 className="text-white font-medium text-sm mb-1">About</h4>
                        <p className="text-white/80 text-xs leading-relaxed">{currentProfile.bio}</p>
                      </div>

                      {/* Projects */}
                      {currentProfile.projects.length > 0 && (
                        <div>
                          <h4 className="text-white font-medium text-sm mb-1">Projects</h4>
                          <div className="space-y-2">
                            {currentProfile.projects.map((project, index) => (
                              <div key={index} className="bg-white/10 rounded-lg p-3">
                                <h5 className="text-white font-medium text-xs mb-1">{project.title}</h5>
                                <p className="text-blue-300 text-xs mb-1">{project.role}</p>
                                <p className="text-white/80 text-xs mb-2">{project.description}</p>
                                {project.referenceLinks.length > 0 && (
                                  <div>
                                    {project.referenceLinks.map((link, linkIndex) => (
                                      <a 
                                        key={linkIndex} 
                                        href={link} 
                                        className="text-xs text-blue-300 block hover:underline"
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                      >
                                        {link}
                                      </a>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Goals & Demands */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <h4 className="text-white font-medium text-sm mb-1">Goals</h4>
                          <div className="space-y-1">
                            {currentProfile.goals.map((goal, index) => (
                              <p key={index} className="text-white/80 text-xs">• {goal}</p>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-white font-medium text-sm mb-1">Looking For</h4>
                          <div className="space-y-1">
                            {currentProfile.demands.map((demand, index) => (
                              <p key={index} className="text-orange-300 text-xs">• {demand}</p>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Institutions */}
                      {currentProfile.institutions.length > 0 && (
                        <div>
                          <h4 className="text-white font-medium text-sm mb-1">Institutions</h4>
                          <div className="space-y-2">
                            {currentProfile.institutions.map((institution, index) => (
                              <div key={index} className="bg-white/10 rounded-lg p-3">
                                <div className="flex items-center justify-between mb-1">
                                  <h5 className="text-white font-medium text-xs">{institution.name}</h5>
                                  {institution.verified && (
                                    <span className="text-green-400 text-xs">✓ Verified</span>
                                  )}
                                </div>
                                <p className="text-blue-300 text-xs mb-1">{institution.role}</p>
                                <p className="text-white/80 text-xs">{institution.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Match Info */}
                      <div>
                        <h4 className="text-white font-medium text-sm mb-1">Why We Match</h4>
                        <p className="text-white/80 text-xs leading-relaxed">{currentProfile.whyMatch}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
