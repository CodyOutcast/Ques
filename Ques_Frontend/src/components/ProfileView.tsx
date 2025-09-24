import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Edit, User, Briefcase, Target, GraduationCap, Globe, Clock, Heart, MapPin, Building, Camera, Info, Package, Search, Sparkles, Check, X } from 'lucide-react';
import type { UserProfile } from '../App';

interface ProfileViewProps {
  userProfile: UserProfile;
  onUpdate: (profile: UserProfile) => void;
}

export function ProfileView({ userProfile, onUpdate }: ProfileViewProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [showPhotoTip, setShowPhotoTip] = useState(false);
  const [showCompletenessTip, setShowCompletenessTip] = useState(false);
  const [activeSuggestions, setActiveSuggestions] = useState<Set<string>>(new Set());

  const generateSuggestion = (sectionId: string) => {
    switch (sectionId) {
      case 'skills':
        if (!userProfile.skills?.length) return null;
        const currentSkills = userProfile.skills.join(', ');
        return {
          original: currentSkills,
          improved: userProfile.skills.map(skill => {
            // Add descriptive prefixes to make skills more attractive
            if (skill.toLowerCase().includes('python')) return 'Full-stack Python Development';
            if (skill.toLowerCase().includes('react')) return 'Modern React & TypeScript';
            if (skill.toLowerCase().includes('design')) return 'User-centered Product Design';
            if (skill.toLowerCase().includes('marketing')) return 'Growth-driven Digital Marketing';
            if (skill.toLowerCase().includes('ai') || skill.toLowerCase().includes('ml')) return 'AI/ML Innovation & Implementation';
            return `Advanced ${skill}`;
          }),
          reason: 'More specific and attractive skill descriptions that highlight your expertise level and impact.'
        };

      case 'resources':
        if (!userProfile.resources?.length) return null;
        return {
          original: userProfile.resources,
          improved: userProfile.resources.map(resource => {
            if (resource.toLowerCase().includes('mentorship')) return 'Expert mentorship & strategic guidance';
            if (resource.toLowerCase().includes('funding')) return 'Seed funding & investor connections';
            if (resource.toLowerCase().includes('network')) return 'Premium industry network access';
            if (resource.toLowerCase().includes('office')) return 'Co-working space & office facilities';
            return `Premium ${resource.toLowerCase()}`;
          }),
          reason: 'Enhanced descriptions that emphasize the value and exclusivity of your resources.'
        };

      case 'goals':
        if (!userProfile.goals?.trim()) return null;
        const currentGoals = userProfile.goals;
        // Generate an improved version that's more specific and compelling
        const improvedGoals = currentGoals
          .replace(/I want to/gi, 'Actively building towards')
          .replace(/I hope to/gi, 'Committed to achieving')
          .replace(/maybe/gi, 'strategically planning to')
          .replace(/I think/gi, 'I\'m focused on');
        return {
          original: currentGoals,
          improved: `${improvedGoals} Looking for like-minded collaborators who share this vision and can contribute complementary expertise.`,
          reason: 'More confident language and clear call-to-action for potential collaborators.'
        };

      case 'demands':
        if (!userProfile.demands?.length) return null;
        return {
          original: userProfile.demands,
          improved: userProfile.demands.map(demand => {
            if (demand.toLowerCase().includes('co-founder')) return 'Technical co-founder with proven track record';
            if (demand.toLowerCase().includes('investor')) return 'Strategic investors & venture partners';
            if (demand.toLowerCase().includes('mentor')) return 'Industry mentor with scaling experience';
            if (demand.toLowerCase().includes('developer')) return 'Senior developer with startup experience';
            return `Experienced ${demand.toLowerCase()}`;
          }),
          reason: 'More specific requirements that attract higher-quality matches and set clear expectations.'
        };

      case 'projects':
        if (!userProfile.projects?.length) return null;
        const currentProject = userProfile.projects[0]; // Show suggestion for first project
        return {
          original: currentProject,
          improved: {
            ...currentProject,
            title: `${currentProject.title} (${currentProject.role || 'Lead'})`,
            description: `${currentProject.description} This project demonstrated strong problem-solving skills and resulted in measurable impact for users and stakeholders.`,
          },
          reason: 'Added role clarity and impact statements to showcase your contributions and results.'
        };

      case 'institutions':
        if (!userProfile.institutions?.length) return null;
        const currentInstitution = userProfile.institutions[0];
        return {
          original: currentInstitution,
          improved: {
            ...currentInstitution,
            description: `${currentInstitution.description} Successfully contributed to key initiatives and built valuable industry relationships during tenure.`,
          },
          reason: 'Highlighted achievements and networking value to increase credibility and appeal.'
        };

      default:
        return null;
    }
  };

  const handleAcceptSuggestion = (sectionId: string) => {
    const suggestion = generateSuggestion(sectionId);
    if (!suggestion) return;

    const updatedProfile = { ...userProfile };
    
    switch (sectionId) {
      case 'skills':
        updatedProfile.skills = suggestion.improved as string[];
        break;
      case 'resources':
        updatedProfile.resources = suggestion.improved as string[];
        break;
      case 'goals':
        updatedProfile.goals = suggestion.improved as string;
        break;
      case 'demands':
        updatedProfile.demands = suggestion.improved as string[];
        break;
      case 'projects':
        updatedProfile.projects[0] = suggestion.improved as typeof userProfile.projects[0];
        break;
      case 'institutions':
        updatedProfile.institutions[0] = suggestion.improved as typeof userProfile.institutions[0];
        break;
    }

    onUpdate(updatedProfile);
    setActiveSuggestions(prev => {
      const newSet = new Set(prev);
      newSet.delete(sectionId);
      return newSet;
    });
  };

  const handleRejectSuggestion = (sectionId: string) => {
    setActiveSuggestions(prev => {
      const newSet = new Set(prev);
      newSet.delete(sectionId);
      return newSet;
    });
  };

  const profileSections = [
    {
      id: 'skills',
      title: 'Skills',
      icon: Briefcase,
      content: (
        <div className="space-y-3">
          {userProfile.skills && userProfile.skills.length > 0 ? (
            <>
              <div className="flex flex-wrap gap-2">
                {userProfile.skills.map((skill, index) => (
                  <Badge key={index} variant="secondary">{skill}</Badge>
                ))}
              </div>
              
              {activeSuggestions.has('skills') && (() => {
                const suggestion = generateSuggestion('skills');
                return suggestion ? (
                  <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-purple-800 mb-1">AI Suggested Improvement</h5>
                        <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex flex-wrap gap-2">
                        {(suggestion.improved as string[]).map((skill, index) => (
                          <Badge key={index} variant="secondary" className="bg-purple-100 text-purple-700 border-purple-200">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleAcceptSuggestion('skills')}
                        className="bg-green-600 hover:bg-green-700 text-white w-8 h-8 p-0"
                      >
                        <Check size={16} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRejectSuggestion('skills')}
                        className="border-gray-300 text-gray-600 hover:bg-gray-50 w-8 h-8 p-0"
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>
                ) : null;
              })()}
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No skills added yet</p>
          )}
        </div>
      )
    },
    {
      id: 'resources',
      title: 'Resources',
      icon: Package,
      content: (
        <div className="space-y-3">
          {userProfile.resources && userProfile.resources.length > 0 ? (
            <>
              <div className="flex flex-wrap gap-2">
                {userProfile.resources.map((resource, index) => (
                  <Badge key={index} variant="outline" className="text-green-700 border-green-300">
                    {resource}
                  </Badge>
                ))}
              </div>
              
              {activeSuggestions.has('resources') && (() => {
                const suggestion = generateSuggestion('resources');
                return suggestion ? (
                  <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-purple-800 mb-1">AI Suggested Improvement</h5>
                        <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex flex-wrap gap-2">
                        {(suggestion.improved as string[]).map((resource, index) => (
                          <Badge key={index} variant="outline" className="text-green-700 border-green-300 bg-green-50">
                            {resource}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleAcceptSuggestion('resources')}
                        className="bg-green-600 hover:bg-green-700 text-white w-8 h-8 p-0"
                      >
                        <Check size={16} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRejectSuggestion('resources')}
                        className="border-gray-300 text-gray-600 hover:bg-gray-50 w-8 h-8 p-0"
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>
                ) : null;
              })()}
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No resources added yet</p>
          )}
        </div>
      )
    },
    {
      id: 'projects',
      title: 'Past Projects',
      icon: Target,
      content: (
        <div className="space-y-4">
          {userProfile.projects && userProfile.projects.length > 0 ? (
            <>
              <div className="space-y-3">
                {userProfile.projects.map((project, index) => (
                  <Card key={index} className="p-4 bg-gray-50">
                    <h5 className="font-medium text-sm mb-1">{project.title}</h5>
                    <p className="text-xs text-blue-600 mb-2">{project.role}</p>
                    <p className="text-sm text-gray-600 mb-2">{project.description}</p>
                    {project.referenceLinks && project.referenceLinks.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-1">References:</p>
                        <div className="space-y-1">
                          {project.referenceLinks.map((link, linkIndex) => (
                            <a 
                              key={linkIndex} 
                              href={link} 
                              className="text-xs text-blue-500 block hover:underline"
                              target="_blank" 
                              rel="noopener noreferrer"
                            >
                              {link}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
              
              {activeSuggestions.has('projects') && (() => {
                const suggestion = generateSuggestion('projects');
                return suggestion ? (
                  <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-purple-800 mb-1">AI Suggested Improvement</h5>
                        <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                      </div>
                    </div>
                    
                    <Card className="p-4 bg-white mb-4">
                      <h5 className="font-medium text-sm mb-1">{(suggestion.improved as any).title}</h5>
                      <p className="text-xs text-blue-600 mb-2">{(suggestion.improved as any).role}</p>
                      <p className="text-sm text-gray-600">{(suggestion.improved as any).description}</p>
                    </Card>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleAcceptSuggestion('projects')}
                        className="bg-green-600 hover:bg-green-700 text-white w-8 h-8 p-0"
                      >
                        <Check size={16} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRejectSuggestion('projects')}
                        className="border-gray-300 text-gray-600 hover:bg-gray-50 w-8 h-8 p-0"
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>
                ) : null;
              })()}
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No projects added yet</p>
          )}
        </div>
      )
    },
    {
      id: 'goals',
      title: 'Goals',
      icon: Target,
      content: (
        <div className="space-y-3">
          {userProfile.goals ? (
            <>
              <p className="text-sm text-gray-600 leading-relaxed">{userProfile.goals}</p>
              
              {activeSuggestions.has('goals') && (() => {
                const suggestion = generateSuggestion('goals');
                return suggestion ? (
                  <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-purple-800 mb-1">AI Suggested Improvement</h5>
                        <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <p className="text-sm text-gray-700 leading-relaxed bg-white p-3 rounded border">
                        {suggestion.improved as string}
                      </p>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleAcceptSuggestion('goals')}
                        className="bg-green-600 hover:bg-green-700 text-white w-8 h-8 p-0"
                      >
                        <Check size={16} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRejectSuggestion('goals')}
                        className="border-gray-300 text-gray-600 hover:bg-gray-50 w-8 h-8 p-0"
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>
                ) : null;
              })()}
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No goals added yet</p>
          )}
        </div>
      )
    },
    {
      id: 'demands',
      title: 'Demands',
      icon: Search,
      content: (
        <div className="space-y-3">
          {userProfile.demands && userProfile.demands.length > 0 ? (
            <>
              <div className="flex flex-wrap gap-2">
                {userProfile.demands.map((demand, index) => (
                  <Badge key={index} variant="outline" className="text-orange-700 border-orange-300">
                    {demand}
                  </Badge>
                ))}
              </div>
              
              {activeSuggestions.has('demands') && (() => {
                const suggestion = generateSuggestion('demands');
                return suggestion ? (
                  <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-purple-800 mb-1">AI Suggested Improvement</h5>
                        <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex flex-wrap gap-2">
                        {(suggestion.improved as string[]).map((demand, index) => (
                          <Badge key={index} variant="outline" className="text-orange-700 border-orange-300 bg-orange-50">
                            {demand}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleAcceptSuggestion('demands')}
                        className="bg-green-600 hover:bg-green-700 text-white w-8 h-8 p-0"
                      >
                        <Check size={16} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRejectSuggestion('demands')}
                        className="border-gray-300 text-gray-600 hover:bg-gray-50 w-8 h-8 p-0"
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>
                ) : null;
              })()}
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No demands added yet</p>
          )}
        </div>
      )
    },
    {
      id: 'institutions',
      title: 'Institutions',
      icon: Building,
      content: (
        <div className="space-y-3">
          {userProfile.institutions && userProfile.institutions.length > 0 ? (
            <>
              <div className="space-y-3">
                {userProfile.institutions.map((institution, index) => (
                  <Card key={index} className="p-3 bg-gray-50">
                    <div className="flex items-start justify-between mb-1">
                      <h5 className="font-medium text-sm">{institution.name}</h5>
                      {institution.verified && (
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                          Verified
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-blue-600 mb-1">{institution.role}</p>
                    <p className="text-sm text-gray-600">{institution.description}</p>
                  </Card>
                ))}
              </div>
              
              {activeSuggestions.has('institutions') && (() => {
                const suggestion = generateSuggestion('institutions');
                return suggestion ? (
                  <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-purple-800 mb-1">AI Suggested Improvement</h5>
                        <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                      </div>
                    </div>
                    
                    <Card className="p-3 bg-white mb-4">
                      <div className="flex items-start justify-between mb-1">
                        <h5 className="font-medium text-sm">{(suggestion.improved as any).name}</h5>
                        {(suggestion.improved as any).verified && (
                          <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                            Verified
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-blue-600 mb-1">{(suggestion.improved as any).role}</p>
                      <p className="text-sm text-gray-600">{(suggestion.improved as any).description}</p>
                    </Card>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleAcceptSuggestion('institutions')}
                        className="bg-green-600 hover:bg-green-700 text-white w-8 h-8 p-0"
                      >
                        <Check size={16} />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRejectSuggestion('institutions')}
                        className="border-gray-300 text-gray-600 hover:bg-gray-50 w-8 h-8 p-0"
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>
                ) : null;
              })()}
            </>
          ) : (
            <p className="text-sm text-gray-400 italic">No institutions added yet</p>
          )}
        </div>
      )
    },
    {
      id: 'university',
      title: 'University',
      icon: GraduationCap,
      content: (
        <div className="space-y-3">
          {userProfile.university ? (
            <div className="space-y-3">
              <Card className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                <div className="flex items-start justify-between mb-1">
                  <h5 className="font-medium text-sm">{userProfile.university.name}</h5>
                  {userProfile.university.verified && (
                    <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-700">
                      🎓 Verified
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-blue-600">Current University</p>
              </Card>
            </div>
          ) : (
            <p className="text-sm text-gray-400 italic">No university added yet</p>
          )}
        </div>
      )
    },
  ];

  const calculateCompleteness = () => {
    const checks = [
      userProfile.name,
      userProfile.age,
      userProfile.gender,
      userProfile.location,
      userProfile.skills && userProfile.skills.length > 0,
      userProfile.goals,

      userProfile.hobbies && userProfile.hobbies.length > 0,
      userProfile.languages && userProfile.languages.length > 0,
      userProfile.resources && userProfile.resources.length > 0,
      userProfile.demands && userProfile.demands.length > 0,
      userProfile.projects && userProfile.projects.length > 0,
      userProfile.institutions && userProfile.institutions.length > 0,
      userProfile.university,
    ];
    
    const filledFields = checks.filter(Boolean).length;
    return Math.round((filledFields / checks.length) * 100);
  };

  const completeness = calculateCompleteness();

  return (
    <div className="h-full overflow-y-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-medium">My Profile</h1>
            <p className="text-sm text-gray-500">Manage your profile information</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                // Toggle suggestions for all sections with content
                const sectionsWithContent = profileSections.filter(section => {
                  if (section.id === 'skills') return userProfile.skills?.length > 0;
                  if (section.id === 'resources') return userProfile.resources?.length > 0;
                  if (section.id === 'projects') return userProfile.projects?.length > 0;
                  if (section.id === 'goals') return userProfile.goals?.trim();
                  if (section.id === 'demands') return userProfile.demands?.length > 0;
                  if (section.id === 'institutions') return userProfile.institutions?.length > 0;
                  return false;
                });
                
                const sectionIds = sectionsWithContent.map(s => s.id);
                const allActive = sectionIds.every(id => activeSuggestions.has(id));
                
                if (allActive) {
                  setActiveSuggestions(new Set());
                } else {
                  setActiveSuggestions(new Set(sectionIds));
                }
              }}
              className="w-10 h-10 p-0 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 text-purple-700 hover:from-purple-100 hover:to-blue-100"
            >
              <Sparkles size={16} />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
              className="w-10 h-10 p-0"
            >
              <Edit size={16} />
            </Button>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Profile Summary Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="p-6 bg-gradient-to-r from-blue-50 to-blue-100 relative">
            {/* Suggestion Buttons */}
            <div className="absolute top-3 right-3 flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-7 w-7 p-0 bg-purple-100 border-purple-200 text-purple-700 hover:bg-purple-200"
                onClick={() => setShowPhotoTip(true)}
              >
                <Camera size={14} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 w-7 p-0 bg-blue-100 border-blue-200 text-blue-700 hover:bg-blue-200"
                onClick={() => setShowCompletenessTip(true)}
              >
                <Info size={14} />
              </Button>
            </div>

            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-4">
                <div className="w-15 h-20 bg-blue-500 rounded-lg flex items-center justify-center overflow-hidden" style={{ width: '60px', height: '80px' }}>
                  {userProfile.profilePhoto ? (
                    <img src={userProfile.profilePhoto} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    <User size={20} className="text-white" />
                  )}
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-medium">{userProfile.name || 'Your Name'}</h2>
                  {userProfile.oneSentenceIntro && (
                    <p className="text-sm text-gray-600 italic mt-1">"{userProfile.oneSentenceIntro}"</p>
                  )}
                </div>
              </div>
              
              {/* Demographics & Personal Details Tags */}
              <div className="flex flex-wrap gap-2">
                {userProfile.age && (
                  <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-blue-200">
                    {userProfile.age} years old
                  </Badge>
                )}
                {userProfile.gender && (
                  <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-blue-200">
                    {userProfile.gender}
                  </Badge>
                )}
                {userProfile.location && (
                  <Badge variant="secondary" className="bg-green-100 text-green-700 border-green-200">
                    <MapPin size={12} className="mr-1" />
                    {userProfile.location}
                  </Badge>
                )}
                {userProfile.languages && userProfile.languages.map((language, index) => (
                  <Badge key={index} variant="secondary" className="bg-purple-100 text-purple-700 border-purple-200">
                    {language}
                  </Badge>
                ))}
                {userProfile.hobbies && userProfile.hobbies.map((hobby, index) => (
                  <Badge key={index} variant="outline" className="text-pink-700 border-pink-300 bg-pink-50">
                    {hobby}
                  </Badge>
                ))}
              </div>
            </div>
            
            {/* Profile Completeness */}
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">Profile Completeness</span>
                <span className="font-medium">{completeness}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${completeness}%` }}
                  transition={{ duration: 0.5 }}
                  className="bg-blue-500 h-2 rounded-full"
                />
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Profile Sections */}
        {profileSections.map((section, index) => (
          <motion.div
            key={section.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <section.icon size={20} className="text-gray-600" />
                <h3 className="font-medium">{section.title}</h3>
                {isEditing && (
                  <Button variant="ghost" size="sm" className="ml-auto p-1">
                    <Edit size={14} />
                  </Button>
                )}
              </div>
              
              {/* Render content if it exists */}
              {section.content && section.content}
            </Card>
          </motion.div>
        ))}

        {/* Safe area for bottom navigation */}
        <div className="h-20"></div>
      </div>

      {/* Photo Tip Modal */}
      <AnimatePresence>
        {showPhotoTip && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 z-50"
              onClick={() => setShowPhotoTip(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-4 z-50 bg-white rounded-2xl p-6 flex flex-col max-w-sm mx-auto my-auto h-fit"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                  <Camera size={20} className="text-white" />
                </div>
                <h3 className="text-lg font-medium">Photo Quality Matters</h3>
              </div>
              
              <div className="space-y-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  For the best networking experience, use a clear, recent photo that clearly shows your face. 
                  Avoid group photos, filtered images, or non-human photos.
                </p>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-purple-800 mb-2">Ideal profile photos:</h4>
                  <ul className="text-xs text-purple-700 space-y-1">
                    <li>• Clear view of your face</li>
                    <li>• Recent and authentic</li>
                    <li>• Professional or casual, but real</li>
                    <li>• Good lighting and resolution</li>
                  </ul>
                </div>
                
                <p className="text-xs text-gray-500">
                  A genuine photo builds trust and helps create meaningful professional connections.
                </p>
              </div>
              
              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowPhotoTip(false)}
                >
                  Already Did
                </Button>
                <Button
                  className="flex-1 bg-purple-500 hover:bg-purple-600"
                  onClick={() => {
                    setShowPhotoTip(false);
                    setIsEditing(true);
                  }}
                >
                  Change Photo
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Completeness Tip Modal */}
      <AnimatePresence>
        {showCompletenessTip && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 z-50"
              onClick={() => setShowCompletenessTip(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-4 z-50 bg-white rounded-2xl p-6 flex flex-col max-w-sm mx-auto my-auto h-fit"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                  <Info size={20} className="text-white" />
                </div>
                <h3 className="text-lg font-medium">Profile Completeness</h3>
              </div>
              
              <div className="space-y-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  Complete profiles receive better AI recommendations and more relevant connections.
                </p>

                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">Current completeness</span>
                    <span className="font-medium">{completeness}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${completeness}%` }}
                    />
                  </div>
                </div>
                
                <p className="text-xs text-gray-500">
                  Tap anywhere to close this tip.
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>


    </div>
  );
}