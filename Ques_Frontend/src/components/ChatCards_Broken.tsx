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
          {/* Main Card Container */}
          <motion.div
            key={currentProfile.id}
            className="relative cursor-grab active:cursor-grabbing bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden"
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
            {!showFullProfile ? (
              /* Collapsed Card View */
              <motion.div
                initial={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="h-full"
              >
                {/* Profile Background */}
                <div className="relative w-full h-full flex items-center justify-center">
                  <div className="text-9xl select-none" style={{ fontSize: '12rem', lineHeight: '1' }}>
                    {currentProfile.avatar}
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                </div>

                {/* Bottom content area */}
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
                        <ChevronDown size={16} />
                      </button>
                    </div>
                  </div>
                  <p className="text-white/90 text-xs line-clamp-1">
                    {currentProfile.oneSentenceIntro || currentProfile.bio}
                  </p>
                </div>
              </motion.div>
            ) : (
              /* Expanded Card View */
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="h-full flex flex-col"
              >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
                        {currentProfile.avatar}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{currentProfile.name}</h3>
                        <p className="text-sm text-gray-600">{currentProfile.location} • {currentProfile.age}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleShareProfile}
                        className="p-2 bg-white rounded-full shadow-sm hover:bg-gray-50 transition-colors"
                      >
                        <Share2 size={16} className="text-gray-600" />
                      </button>
                      <button
                        onClick={toggleExtendedProfile}
                        className="p-2 bg-blue-500 rounded-full hover:bg-blue-600 transition-colors"
                      >
                        <ChevronUp size={16} className="text-white" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto" style={{ height: 'calc(400px - 80px)' }}>
                  <div className="p-4 space-y-4">
                    {/* Resources */}
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-2">Resources</h4>
                      <div className="flex flex-wrap gap-1">
                        {currentProfile.resources.map((resource, index) => (
                          <span key={index} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                            {resource}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Skills */}
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-2">Skills</h4>
                      <div className="flex flex-wrap gap-1">
                        {currentProfile.skills.map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Languages & Hobbies */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Languages</h4>
                        <div className="flex flex-wrap gap-1">
                          {currentProfile.languages.map((language, index) => (
                            <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                              {language}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Hobbies</h4>
                        <div className="flex flex-wrap gap-1">
                          {currentProfile.hobbies.map((hobby, index) => (
                            <span key={index} className="px-2 py-1 bg-pink-100 text-pink-800 rounded-full text-xs">
                              {hobby}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* About */}
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-2">About</h4>
                      <p className="text-gray-700 text-xs leading-relaxed">{currentProfile.bio}</p>
                    </div>

                    {/* Projects */}
                    {currentProfile.projects.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Projects</h4>
                        <div className="space-y-3">
                          {currentProfile.projects.map((project, index) => (
                            <div key={index} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                              <h5 className="font-medium text-gray-900 text-xs mb-1">{project.title}</h5>
                              <p className="text-blue-600 text-xs mb-1">{project.role}</p>
                              <p className="text-gray-700 text-xs mb-2 leading-relaxed">{project.description}</p>
                              {project.referenceLinks.length > 0 && (
                                <div className="space-y-1">
                                  {project.referenceLinks.map((link, linkIndex) => (
                                    <a 
                                      key={linkIndex} 
                                      href={link} 
                                      className="text-xs text-blue-500 block hover:underline break-all"
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
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Goals</h4>
                        <div className="space-y-1">
                          {currentProfile.goals.map((goal, index) => (
                            <p key={index} className="text-gray-700 text-xs">• {goal}</p>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Looking For</h4>
                        <div className="space-y-1">
                          {currentProfile.demands.map((demand, index) => (
                            <p key={index} className="text-orange-600 text-xs">• {demand}</p>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Institutions */}
                    {currentProfile.institutions.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm mb-2">Institutions</h4>
                        <div className="space-y-3">
                          {currentProfile.institutions.map((institution, index) => (
                            <div key={index} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                              <div className="flex items-center justify-between mb-1">
                                <h5 className="font-medium text-gray-900 text-xs">{institution.name}</h5>
                                {institution.verified && (
                                  <span className="text-green-600 text-xs font-medium">✓ Verified</span>
                                )}
                              </div>
                              <p className="text-blue-600 text-xs mb-1">{institution.role}</p>
                              <p className="text-gray-700 text-xs">{institution.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Why We Match */}
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-2">Why We Match</h4>
                      <p className="text-gray-700 text-xs leading-relaxed">{currentProfile.whyMatch}</p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Progress dots */}
      <div className="flex gap-2 mt-4">
        {profiles.slice(0, Math.min(5, profiles.length)).map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-colors ${
              index === currentIndex 
                ? 'bg-blue-500' 
                : index < currentIndex 
                  ? 'bg-gray-400' 
                  : 'bg-gray-200'
            }`}
          />
        ))}
        {profiles.length > 5 && (
          <span className="text-xs text-gray-500 ml-2">
            +{profiles.length - 5} more
          </span>
        )}
      </div>
    </div>
  );
}