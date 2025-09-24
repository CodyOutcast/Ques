import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { 
  ChevronRight, 
  User, 
  MessageCircle, 
  Camera, 
  MapPin,
  Languages,
  Lightbulb,
  Package,
  Target,
  Search,
  Building,
  Shield,
  Plus,
  X,
  Mail,
  CheckCircle
} from 'lucide-react';
import type { UserProfile } from '../App';

interface ProfileSetupWizardProps {
  onComplete: (profile: UserProfile) => void;
  onBack: () => void;
}

export function ProfileSetupWizard({ onComplete, onBack }: ProfileSetupWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [profile, setProfile] = useState<UserProfile>({
    name: '',
    age: '',
    gender: '',
    location: '',
    hobbies: [],
    languages: [],
    oneSentenceIntro: '',
    skills: [],
    resources: [],
    projects: [],
    goals: [],
    demands: [],
    institutions: [],
  });

  // Temporary input states for adding items
  const [tempHobby, setTempHobby] = useState('');
  const [tempLanguage, setTempLanguage] = useState('');
  const [tempSkill, setTempSkill] = useState('');
  const [tempResource, setTempResource] = useState('');
  const [tempDemand, setTempDemand] = useState('');
  const [tempGoal, setTempGoal] = useState('');
  const [currentUniversity, setCurrentUniversity] = useState('');
  const [universityEmail, setUniversityEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [emailVerified, setEmailVerified] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [universitySearchInput, setUniversitySearchInput] = useState('');
  const [showUniversityDropdown, setShowUniversityDropdown] = useState(false);
  const [isUniversitySelected, setIsUniversitySelected] = useState(false);
  const [wechatAuthenticated, setWechatAuthenticated] = useState(false);

  const steps = useMemo(() => [
    'Demographics', 
    'Skills',
    'Resources',
    'Past Projects',
    'Goals',
    'Demands',
    'Past Institutions',
    'Your Affiliated University',
    'Authentication'
  ], []);

  // Chinese universities list - memoized to prevent recreating on each render
  const chineseUniversities = useMemo(() => [
    'Tsinghua University',
    'Peking University', 
    'Fudan University',
    'Shanghai Jiao Tong University',
    'Zhejiang University',
    'University of Science and Technology of China',
    'Nanjing University',
    'Xi\'an Jiaotong University',
    'Harbin Institute of Technology',
    'Beijing Institute of Technology',
    'Huazhong University of Science and Technology',
    'Sun Yat-sen University',
    'Beihang University',
    'Tianjin University',
    'Southeast University',
    'Beijing Normal University',
    'Dalian University of Technology',
    'Sichuan University',
    'South China University of Technology',
    'Central South University',
    'Northwestern Polytechnical University',
    'East China Normal University',
    'Beijing University of Technology',
    'Tongji University',
    'Xidian University',
    'Wuhan University',
    'Renmin University of China',
    'Beijing Jiaotong University',
    'Northeastern University',
    'Lanzhou University'
  ], []);

  const handleInputChange = useCallback((field: keyof UserProfile, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }));
    
    // Backdoor: Skip onboarding if name is "skip"
    if (field === 'name' && value.toLowerCase() === 'skip') {
      const skipProfile: UserProfile = {
        profilePhoto: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRTVFN0VCIi8+CjxwYXRoIGQ9Ik0zMiA0MEMzNi40MTgzIDQwIDQwIDM2LjQxODMgNDAgMzJTMzYuNDE4MyAyNCAzMiAyNFMyNCAyNy41ODE3IDI0IDMyUzI3LjU4MTcgNDAgMzIgNDBaIiBmaWxsPSIjOUI5Qjk2Ii8+Cjwvc3ZnPgo=',
        name: 'Skip User',
        age: '25',
        gender: 'other',
        location: 'Skip City',
        hobbies: ['Testing'],
        languages: ['English'],
        oneSentenceIntro: 'Skipped onboarding process',
        skills: ['Skip Testing'],
        resources: ['Skip Resources'],
        projects: [],
        goals: ['Skip Goals'],
        demands: ['Skip Demands'],
        institutions: [],
        currentUniversity: 'Skip University',
        universityEmail: 'skip@skip.edu',
        wechatVerified: true,
        wechatId: 'skip_user'
      };
      
      setTimeout(() => {
        onComplete(skipProfile);
      }, 500); // Small delay for smooth transition
    }
  }, [onComplete]);

  const handlePhotoUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        handleInputChange('profilePhoto', result);
      };
      reader.readAsDataURL(file);
    }
  }, [handleInputChange]);

  const addToArray = useCallback((field: keyof UserProfile, value: string, tempSetter: (val: string) => void) => {
    if (value.trim()) {
      const currentArray = profile[field] as string[];
      handleInputChange(field, [...currentArray, value.trim()]);
      tempSetter('');
    }
  }, [profile, handleInputChange]);

  const removeFromArray = useCallback((field: keyof UserProfile, index: number) => {
    const currentArray = profile[field] as string[];
    handleInputChange(field, currentArray.filter((_, i) => i !== index));
  }, [profile, handleInputChange]);

  // Helper function to check if a project is empty
  const isProjectEmpty = useCallback((project: any) => {
    return !project.title.trim() && !project.role.trim() && !project.description.trim();
  }, []);

  // Helper function to check if an institution is empty  
  const isInstitutionEmpty = useCallback((institution: any) => {
    return !institution.name.trim() && !institution.role.trim() && !institution.description.trim();
  }, []);

  const addProject = useCallback(() => {
    // Don't add a new project if the current one is empty
    if (profile.projects.length > 0) {
      const lastProject = profile.projects[profile.projects.length - 1];
      if (isProjectEmpty(lastProject)) {
        return; // Exit early if last project is empty
      }
    }

    const newProject = {
      title: '',
      role: '',
      description: '',
      referenceLinks: []
    };
    handleInputChange('projects', [...profile.projects, newProject]);
  }, [profile.projects, handleInputChange, isProjectEmpty]);

  const updateProject = useCallback((index: number, field: string, value: any) => {
    const updatedProjects = [...profile.projects];
    updatedProjects[index] = { ...updatedProjects[index], [field]: value };
    handleInputChange('projects', updatedProjects);
  }, [profile.projects, handleInputChange]);

  const removeProject = useCallback((index: number) => {
    handleInputChange('projects', profile.projects.filter((_, i) => i !== index));
  }, [profile.projects, handleInputChange]);

  const addInstitution = useCallback(() => {
    // Don't add a new institution if the current one is empty
    if (profile.institutions.length > 0) {
      const lastInstitution = profile.institutions[profile.institutions.length - 1];
      if (isInstitutionEmpty(lastInstitution)) {
        return; // Exit early if last institution is empty
      }
    }

    const newInstitution = {
      name: '',
      role: '',
      description: '',
      verified: false
    };
    handleInputChange('institutions', [...profile.institutions, newInstitution]);
  }, [profile.institutions, handleInputChange, isInstitutionEmpty]);

  const updateInstitution = useCallback((index: number, field: string, value: any) => {
    const updatedInstitutions = [...profile.institutions];
    updatedInstitutions[index] = { ...updatedInstitutions[index], [field]: value };
    handleInputChange('institutions', updatedInstitutions);
  }, [profile.institutions, handleInputChange]);

  const removeInstitution = useCallback((index: number) => {
    handleInputChange('institutions', profile.institutions.filter((_, i) => i !== index));
  }, [profile.institutions, handleInputChange]);

  const sendVerificationCode = useCallback(() => {
    if (universityEmail && validateUniversityEmail()) {
      setCodeSent(true);
      console.log('Verification code sent to:', universityEmail);
    }
  }, [universityEmail]);

  const validateUniversityEmail = useCallback(() => {
    if (!universityEmail || !currentUniversity) return false;
    
    const eduCnPattern = /\.edu\.cn$/;
    const commonDomains = [
      'tsinghua.edu.cn', 'pku.edu.cn', 'fudan.edu.cn', 'sjtu.edu.cn',
      'zju.edu.cn', 'ustc.edu.cn', 'nju.edu.cn', 'xjtu.edu.cn'
    ];
    
    return eduCnPattern.test(universityEmail) || 
           commonDomains.some(domain => universityEmail.endsWith(domain));
  }, [universityEmail, currentUniversity]);

  const verifyCode = useCallback(() => {
    if (verificationCode.length === 6) {
      setEmailVerified(true);
      console.log('Code verified:', verificationCode);
    }
  }, [verificationCode]);

  const handleUniversitySearch = useCallback((value: string) => {
    setUniversitySearchInput(value);
    setShowUniversityDropdown(value.length > 0);
  }, []);

  const selectUniversity = useCallback((university: string) => {
    setCurrentUniversity(university);
    setUniversitySearchInput('');
    setShowUniversityDropdown(false);
    setIsUniversitySelected(true);
  }, []);

  const filteredUniversities = useMemo(() => {
    if (!universitySearchInput) return [];
    return chineseUniversities.filter(uni => 
      uni.toLowerCase().includes(universitySearchInput.toLowerCase())
    ).slice(0, 5); // Show max 5 suggestions
  }, [universitySearchInput, chineseUniversities]);

  const handleNext = useCallback(() => {
    // Filter out empty projects and institutions before proceeding
    const cleanedProfile = {
      ...profile,
      projects: profile.projects.filter(project => !isProjectEmpty(project)),
      institutions: profile.institutions.filter(institution => !isInstitutionEmpty(institution))
    };

    if (currentStep === steps.length - 1) {
      // Complete setup
      onComplete({
        ...cleanedProfile,
        wechatVerified: true,
        wechatId: 'user_' + Date.now()
      });
    } else {
      // Update profile with cleaned data before moving to next step
      setProfile(cleanedProfile);
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep, steps.length, onComplete, profile, isProjectEmpty, isInstitutionEmpty]);

  const handlePrevious = useCallback(() => {
    if (currentStep === 0) {
      onBack();
    } else {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep, onBack]);

  const canProceed = useCallback(() => {
    switch (currentStep) {
      case 0: return profile.name && profile.age && profile.gender && profile.location && profile.profilePhoto;
      case 1: return true;
      case 2: return true;
      case 3: return true;
      case 4: return true; // Goals are now optional
      case 5: return true;
      case 6: return true;
      case 7: return emailVerified; // University step requires email verification
      case 8: return wechatAuthenticated; // Require WeChat authentication on final step
      default: return false;
    }
  }, [currentStep, profile, wechatAuthenticated, currentUniversity, emailVerified]);

  // Render functions for each step
  const renderDemographics = useCallback(() => (
    <div className="space-y-3">
      {/* Ultra-Compact Header */}
      <div className="text-center mb-3">
        <div className="flex items-center justify-center gap-2">
          <User size={20} className="text-blue-500" />
          <h2>Tell us about yourself</h2>
        </div>
      </div>

      {/* Profile Photo - Side by side with basic info */}
      <div className="grid grid-cols-3 gap-3 items-start">
        <div className="col-span-1 flex flex-col items-center">
          <div className="relative">
            <div 
              className="bg-gray-100 border-2 border-gray-200 rounded-lg cursor-pointer flex items-center justify-center overflow-hidden"
              style={{ width: '90px', height: '120px' }}
              onClick={() => document.getElementById('photo-upload')?.click()}
            >
              {profile.profilePhoto ? (
                <img 
                  src={profile.profilePhoto} 
                  alt="Profile" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex flex-col items-center justify-center text-xs text-gray-500">
                  <Camera size={18} className="mb-1" />
                  <span>Photo</span>
                </div>
              )}
            </div>
            {profile.profilePhoto && (
              <Button 
                size="sm" 
                variant="outline" 
                className="absolute -bottom-1 -right-1 rounded-full w-5 h-5 p-0"
                onClick={() => document.getElementById('photo-upload')?.click()}
              >
                <Camera size={10} />
              </Button>
            )}
          </div>
          {profile.profilePhoto && (
            <Label className="text-xs text-gray-500 mt-1">Photo</Label>
          )}
          <input
            id="photo-upload"
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            className="hidden"
          />
        </div>

        <div className="col-span-2 space-y-2">
          <div>
            <Label className="text-sm">Name *</Label>
            <Input
              value={profile.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Your full name"
              className="h-8"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className="text-sm">Age *</Label>
              <Input
                value={profile.age}
                onChange={(e) => handleInputChange('age', e.target.value)}
                placeholder="25"
                type="number"
                className="h-8"
              />
            </div>
            <div>
              <Label className="text-sm">Gender *</Label>
              <Select value={profile.gender} onValueChange={(value) => handleInputChange('gender', value)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder="Select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>

      {/* Location */}
      <div>
        <Label className="text-sm">Location *</Label>
        <div className="relative">
          <MapPin size={14} className="absolute left-3 top-2 text-gray-400" />
          <Input
            value={profile.location}
            onChange={(e) => handleInputChange('location', e.target.value)}
            placeholder="Beijing, China"
            className="pl-9 h-8"
          />
        </div>
      </div>

      {/* One sentence intro */}
      <div>
        <Label className="text-sm">Describe yourself in one sentence</Label>
        <div className="relative">
          <MessageCircle size={14} className="absolute left-3 top-2 text-gray-400" />
          <Input
            value={profile.oneSentenceIntro || ''}
            onChange={(e) => handleInputChange('oneSentenceIntro', e.target.value)}
            placeholder="I'm a passionate designer..."
            className="pl-9 h-8"
            maxLength={150}
          />
        </div>
      </div>

      {/* Fixed Height Hobbies with Horizontal Scroll */}
      <div>
        <Label className="text-sm">Hobbies & Interests</Label>
        <div className="flex gap-2 mb-1">
          <Input
            value={tempHobby}
            onChange={(e) => setTempHobby(e.target.value)}
            placeholder="Add a hobby"
            onKeyPress={(e) => e.key === 'Enter' && addToArray('hobbies', tempHobby, setTempHobby)}
            className="h-7 text-sm"
          />
          <Button 
            type="button" 
            size="sm"
            onClick={() => addToArray('hobbies', tempHobby, setTempHobby)}
            className="h-7 px-2"
          >
            <Plus size={12} />
          </Button>
        </div>
        {/* Fixed height container for tags */}
        <div className="h-8 overflow-hidden">
          {profile.hobbies.length > 0 ? (
            <div className="flex gap-1 overflow-x-auto pb-1" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
              {profile.hobbies.map((hobby, index) => (
                <Badge key={index} variant="secondary" className="text-xs pr-0.5 h-6 whitespace-nowrap flex-shrink-0">
                  <span className="max-w-20 truncate">{hobby}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-3 w-3 p-0 ml-0.5"
                    onClick={() => removeFromArray('hobbies', index)}
                  >
                    <X size={8} />
                  </Button>
                </Badge>
              ))}
            </div>
          ) : (
            <div className="h-8 flex items-center">
              <span className="text-xs text-gray-400">No hobbies added yet</span>
            </div>
          )}
        </div>
      </div>

      {/* Fixed Height Languages with Horizontal Scroll */}
      <div>
        <Label className="text-sm">Languages</Label>
        <div className="flex gap-2 mb-1">
          <div className="relative flex-1">
            <Languages size={14} className="absolute left-3 top-1.5 text-gray-400" />
            <Input
              value={tempLanguage}
              onChange={(e) => setTempLanguage(e.target.value)}
              placeholder="Add a language"
              className="pl-9 h-7 text-sm"
              onKeyPress={(e) => e.key === 'Enter' && addToArray('languages', tempLanguage, setTempLanguage)}
            />
          </div>
          <Button 
            type="button" 
            size="sm"
            onClick={() => addToArray('languages', tempLanguage, setTempLanguage)}
            className="h-7 px-2"
          >
            <Plus size={12} />
          </Button>
        </div>
        {/* Fixed height container for tags */}
        <div className="h-8 overflow-hidden">
          {profile.languages.length > 0 ? (
            <div className="flex gap-1 overflow-x-auto pb-1" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
              {profile.languages.map((language, index) => (
                <Badge key={index} variant="secondary" className="text-xs pr-0.5 h-6 whitespace-nowrap flex-shrink-0">
                  <span className="max-w-20 truncate">{language}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-3 w-3 p-0 ml-0.5"
                    onClick={() => removeFromArray('languages', index)}
                  >
                    <X size={8} />
                  </Button>
                </Badge>
              ))}
            </div>
          ) : (
            <div className="h-8 flex items-center">
              <span className="text-xs text-gray-400">No languages added yet</span>
            </div>
          )}  
        </div>
      </div>
    </div>
  ), [profile, tempHobby, tempLanguage, handleInputChange, addToArray, removeFromArray]);

  const renderSkills = useCallback(() => {
    const skillSuggestions = [
      'Programming', 'Design', 'Project Management', 'Leadership', 'Communication',
      'Data Analysis', 'Marketing', 'Sales', 'Research', 'Problem Solving',
      'Strategy', 'Teaching', 'Writing', 'Public Speaking', 'Finance'
    ];

    return (
      <div className="flex flex-col h-full py-6 relative">
        {/* Header */}
        <div className="text-center mb-6">
          <Lightbulb size={28} className="text-blue-500 mx-auto mb-2" />
          <h2>What are your skills?</h2>
          <p className="text-sm text-gray-500">Add tags to showcase your expertise</p>
        </div>

        {/* Added Skills - Center of screen */}
        <div className="flex-1 flex items-center justify-center pb-32">
          <AnimatePresence>
            {profile.skills.length > 0 ? (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-wrap gap-2 justify-center max-w-sm"
              >
                {profile.skills.map((skill, index) => (
                  <motion.div
                    key={`skill-${skill}-${index}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                  >
                    <Badge variant="outline" className="pr-1">
                      {skill}
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-4 w-4 p-0 ml-1"
                        onClick={() => removeFromArray('skills', index)}
                      >
                        <X size={10} />
                      </Button>
                    </Badge>
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <div className="text-center text-gray-400">
                <p className="text-sm">Your skills will appear here</p>
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Bottom Section - Suggestions + Input */}
        <div className="absolute bottom-0 left-6 right-6 space-y-4">
          {/* Suggestion Bubbles */}
          <div>
            <Label className="text-xs text-gray-500 mb-2 block">Quick suggestions:</Label>
            <div className="flex flex-wrap gap-2">
              {skillSuggestions
                .filter(suggestion => !profile.skills.includes(suggestion))
                .slice(0, 4)
                .map((suggestion) => (
                  <motion.div
                    key={suggestion}
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => addToArray('skills', suggestion, () => {})}
                      className="h-7 px-3 text-xs border border-gray-200 hover:bg-blue-50 hover:border-blue-300 rounded-full"
                    >
                      + {suggestion}
                    </Button>
                  </motion.div>
                ))
              }
            </div>
          </div>

          {/* Input at bottom */}
          <div>
            <Label className="text-sm">Skills & Expertise</Label>
            <div className="flex gap-2">
              <Input
                value={tempSkill}
                onChange={(e) => setTempSkill(e.target.value)}
                placeholder="e.g., Programming, Design, Marketing"
                onKeyPress={(e) => e.key === 'Enter' && addToArray('skills', tempSkill, setTempSkill)}
                className="h-9 flex-1"
              />
              <Button
                type="button"
                onClick={() => addToArray('skills', tempSkill, setTempSkill)}
                disabled={!tempSkill.trim()}
                className="h-9 px-3"
              >
                +
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }, [profile.skills, tempSkill, addToArray, removeFromArray]);

  const renderResources = useCallback(() => {
    const resourceSuggestions = [
      'Mentorship', 'Funding', 'Network Access', 'Office Space', 'Equipment',
      'Marketing Support', 'Technical Guidance', 'Business Connections', 'Design Help',
      'Legal Advice', 'Accounting Services', 'Industry Insights', 'Partnership Opportunities'
    ];

    return (
      <div className="flex flex-col h-full py-6 relative">
        {/* Header */}
        <div className="text-center mb-6">
          <Package size={28} className="text-blue-500 mx-auto mb-2" />
          <h2>What resources do you have?</h2>
          <p className="text-sm text-gray-500">Share what you can offer to others</p>
        </div>

        {/* Added Resources - Center of screen */}
        <div className="flex-1 flex items-center justify-center pb-32">
          <AnimatePresence>
            {profile.resources.length > 0 ? (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-wrap gap-2 justify-center max-w-sm"
              >
                {profile.resources.map((resource, index) => (
                  <motion.div
                    key={`resource-${resource}-${index}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                  >
                    <Badge variant="outline" className="pr-1 bg-green-50 text-green-700 border-green-200">
                      {resource}
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-4 w-4 p-0 ml-1"
                        onClick={() => removeFromArray('resources', index)}
                      >
                        <X size={10} />
                      </Button>
                    </Badge>
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <div className="text-center text-gray-400">
                <p className="text-sm">Your resources will appear here</p>
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Bottom Section - Suggestions + Input */}
        <div className="absolute bottom-0 left-6 right-6 space-y-4">
          {/* Suggestion Bubbles */}
          <div>
            <Label className="text-xs text-gray-500 mb-2 block">Quick suggestions:</Label>
            <div className="flex flex-wrap gap-2">
              {resourceSuggestions
                .filter(suggestion => !profile.resources.includes(suggestion))
                .slice(0, 4)
                .map((suggestion) => (
                  <motion.div
                    key={suggestion}
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => addToArray('resources', suggestion, () => {})}
                      className="h-7 px-3 text-xs border border-gray-200 hover:bg-green-50 hover:border-green-300 rounded-full"
                    >
                      + {suggestion}
                    </Button>
                  </motion.div>
                ))
              }
            </div>
          </div>

          {/* Input at bottom */}
          <div>
            <Label className="text-sm">Available Resources</Label>
            <div className="flex gap-2">
              <Input
                value={tempResource}
                onChange={(e) => setTempResource(e.target.value)}
                placeholder="e.g., Mentorship, Funding, Network Access"
                onKeyPress={(e) => e.key === 'Enter' && addToArray('resources', tempResource, setTempResource)}
                className="h-9 flex-1"
              />
              <Button
                type="button"
                onClick={() => addToArray('resources', tempResource, setTempResource)}
                disabled={!tempResource.trim()}
                className="h-9 px-3"
              >
                +
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }, [profile.resources, tempResource, addToArray, removeFromArray]);

  const renderProjects = useCallback(() => (
    <div className="flex flex-col h-full py-6 relative">
      {/* Header */}
      <div className="text-center mb-6">
        <Target size={28} className="text-blue-500 mx-auto mb-2" />
        <h2>Your Past Projects</h2>
        <p className="text-sm text-gray-500">Showcase your experience and achievements</p>
      </div>

      {/* Project Cards - Center/scrollable area */}
      <div className="flex-1 overflow-y-auto pb-16">
        <AnimatePresence>
          {profile.projects.length > 0 ? (
            <div className="space-y-4">
              {profile.projects.map((project, index) => (
                <motion.div
                  key={`project-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card className="p-4">
                    <CardContent className="p-0 space-y-1">
                      <div className="flex justify-between items-start">
                        <h3>Project {index + 1}</h3>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeProject(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X size={16} />
                        </Button>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-sm">Project Title</Label>
                          <Input
                            value={project.title}
                            onChange={(e) => updateProject(index, 'title', e.target.value)}
                            placeholder="Project name"
                          />
                        </div>
                        <div>
                          <Label className="text-sm">Your Role</Label>
                          <Input
                            value={project.role}
                            onChange={(e) => updateProject(index, 'role', e.target.value)}
                            placeholder="e.g., Lead Developer"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <Label className="text-sm">Description</Label>
                        <Textarea
                          value={project.description}
                          onChange={(e) => updateProject(index, 'description', e.target.value)}
                          placeholder="Describe your project and achievements"
                          rows={3}
                        />
                      </div>
                      
                      <div>
                        <Label className="text-sm">Reference Links</Label>
                        <Input
                          value={project.referenceLinks.join(', ')}
                          onChange={(e) => updateProject(index, 'referenceLinks', e.target.value.split(', ').filter(link => link.trim()))}
                          placeholder="URLs separated by commas"
                        />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8">
              <p className="text-sm">Add your projects to showcase your experience</p>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Add Project Button - Fixed at bottom */}
      <div className="absolute bottom-0 left-6 right-6">
        <Button onClick={addProject} className="w-full">
          <Plus size={16} className="mr-2" />
          Add Project
        </Button>
      </div>
    </div>
  ), [profile.projects, addProject, updateProject, removeProject]);

  const renderGoals = useCallback(() => (
    <div className="flex flex-col h-full py-6 relative">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center gap-2">
          <Search size={24} className="text-blue-500" />
          <h2>What are your goals?</h2>
        </div>
      </div>

      {/* Goals Display - Center area */}
      <div className="flex-1 flex items-center justify-center pb-24">
        <div className="w-full max-w-sm">
          <AnimatePresence>
            {profile.goals.length > 0 ? (
              <div className="space-y-2">
                {profile.goals.map((goal, index) => (
                  <motion.div
                    key={`goal-${goal}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2 }}
                    className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-100"
                  >
                    <span className="text-sm">{goal}</span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeFromArray('goals', index)}
                      className="text-red-500 hover:text-red-700 h-6 w-6 p-0"
                    >
                      <X size={14} />
                    </Button>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400">
                <p className="text-sm">Add your goals to get started</p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Add Goal Input - Bottom */}
      <div className="absolute bottom-0 left-6 right-6">
        <Label className="text-sm">Add a Goal</Label>
        <div className="flex gap-2">
          <Input
            value={tempGoal}
            onChange={(e) => setTempGoal(e.target.value)}
            placeholder="e.g., Find a co-founder, Learn new skills, Build a network"
            onKeyPress={(e) => e.key === 'Enter' && addToArray('goals', tempGoal, setTempGoal)}
            className="flex-1 h-9"
          />
          <Button
            type="button"
            onClick={() => addToArray('goals', tempGoal, setTempGoal)}
            disabled={!tempGoal.trim()}
            className="px-4 h-9"
          >
            <Plus size={16} />
          </Button>
        </div>
      </div>
    </div>
  ), [profile.goals, tempGoal, addToArray, removeFromArray]);

  const renderDemands = useCallback(() => (
    <div className="flex flex-col h-full py-6 relative">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center gap-2">
          <Target size={24} className="text-purple-500" />
          <h2>What do you need?</h2>
        </div>
        <p className="text-sm text-gray-500">Tell us what you're looking for</p>
      </div>

      {/* Demands Display - Center area */}
      <div className="flex-1 flex items-center justify-center pb-24">
        <div className="w-full max-w-sm">
          <AnimatePresence>
            {profile.demands.length > 0 ? (
              <div className="space-y-2">
                {profile.demands.map((demand, index) => (
                  <motion.div
                    key={`demand-${demand}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2 }}
                    className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-100"
                  >
                    <span className="text-sm">{demand}</span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeFromArray('demands', index)}
                      className="text-red-500 hover:text-red-700 h-6 w-6 p-0"
                    >
                      <X size={14} />
                    </Button>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400">
                <p className="text-sm">Add what you need help with</p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Add Demand Input - Bottom */}
      <div className="absolute bottom-0 left-6 right-6">
        <Label className="text-sm">What do you need?</Label>
        <div className="flex gap-2">
          <Input
            value={tempDemand}
            onChange={(e) => setTempDemand(e.target.value)}
            placeholder="e.g., Technical expertise, Funding, Marketing help"
            onKeyPress={(e) => e.key === 'Enter' && addToArray('demands', tempDemand, setTempDemand)}
            className="flex-1 h-9"
          />
          <Button
            type="button"
            onClick={() => addToArray('demands', tempDemand, setTempDemand)}
            disabled={!tempDemand.trim()}
            className="px-4 h-9"
          >
            <Plus size={16} />
          </Button>
        </div>
      </div>
    </div>
  ), [profile.demands, tempDemand, addToArray, removeFromArray]);

  const renderInstitutions = useCallback(() => (
    <div className="flex flex-col h-full py-6 relative">
      {/* Header */}
      <div className="text-center mb-6">
        <Building size={28} className="text-blue-500 mx-auto mb-2" />
        <h2>Your Past Institutions</h2>
        <p className="text-sm text-gray-500">Schools, companies, organizations you've been part of</p>
      </div>

      {/* Institution Cards - Center/scrollable area */}
      <div className="flex-1 overflow-y-auto pb-16">
        <AnimatePresence>
          {profile.institutions.length > 0 ? (
            <div className="space-y-4">
              {profile.institutions.map((institution, index) => (
                <motion.div
                  key={`institution-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card className="p-4">
                    <CardContent className="p-0 space-y-3">
                      <div className="flex justify-between items-start">
                        <h3>Institution {index + 1}</h3>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeInstitution(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X size={16} />
                        </Button>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-sm">Institution Name</Label>
                          <Input
                            value={institution.name}
                            onChange={(e) => updateInstitution(index, 'name', e.target.value)}
                            placeholder="University/Company name"
                          />
                        </div>
                        <div>
                          <Label className="text-sm">Your Role</Label>
                          <Input
                            value={institution.role}
                            onChange={(e) => updateInstitution(index, 'role', e.target.value)}
                            placeholder="e.g., Student, Engineer"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <Label className="text-sm">Description</Label>
                        <Textarea
                          value={institution.description}
                          onChange={(e) => updateInstitution(index, 'description', e.target.value)}
                          placeholder="Describe your experience and achievements"
                          rows={3}
                        />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8">
              <p className="text-sm">Add institutions to showcase your background</p>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Add Institution Button - Fixed at bottom */}
      <div className="absolute bottom-0 left-6 right-6">
        <Button onClick={addInstitution} className="w-full">
          <Plus size={16} className="mr-2" />
          Add Institution
        </Button>
      </div>
    </div>
  ), [profile.institutions, addInstitution, updateInstitution, removeInstitution]);

  const renderCurrentUniversity = useCallback(() => (
    <div className="flex flex-col h-full py-6 relative">
      {/* Header */}
      <div className="text-center mb-6">
        <Building size={28} className="text-blue-500 mx-auto mb-2" />
        <h2>Your Affiliated University</h2>
        <p className="text-sm text-gray-500">Connect with your university community</p>
      </div>

      {/* University Details - Center area */}
      <div className="flex-1 flex items-center justify-center pb-40">
        <div className="w-full max-w-sm space-y-4 p-[0px] mt-16">
          {/* Selected University - Appears in center */}
          <AnimatePresence>
            {currentUniversity && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="p-4 bg-blue-50 rounded-lg border border-blue-200"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm">{currentUniversity}</h3>
                    <p className="text-xs text-gray-500">Selected University</p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setCurrentUniversity('');
                      setIsUniversitySelected(false);
                      setUniversityEmail('');
                      setCodeSent(false);
                      setEmailVerified(false);
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X size={16} />
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* University Email - Float up when university selected */}
          <AnimatePresence>
            {isUniversitySelected && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="space-y-3"
              >
                <div>
                  <Label className="text-sm">University Email</Label>
                  <div className="relative">
                    <Mail size={14} className="absolute left-3 top-2.5 text-gray-400" />
                    <Input
                      value={universityEmail}
                      onChange={(e) => setUniversityEmail(e.target.value)}
                      placeholder="your.name@university.edu.cn"
                      className="pl-9 h-9"
                    />
                  </div>
                </div>

                {universityEmail && !codeSent && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <Button
                      onClick={sendVerificationCode}
                      disabled={!validateUniversityEmail()}
                      className="w-full h-9"
                    >
                      Send Verification Code
                    </Button>
                  </motion.div>
                )}

                {codeSent && !emailVerified && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-2"
                  >
                    <div>
                      <Label className="text-sm">Verification Code</Label>
                      <Input
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value)}
                        placeholder="Enter 6-digit code"
                        className="h-9"
                        maxLength={6}
                      />
                    </div>
                    <Button
                      onClick={verifyCode}
                      disabled={verificationCode.length !== 6}
                      className="w-full h-9"
                    >
                      Verify Code
                    </Button>
                  </motion.div>
                )}

                {emailVerified && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-2 p-2 bg-green-50 rounded-lg border border-green-200"
                  >
                    <CheckCircle size={16} className="text-green-600" />
                    <span className="text-sm text-green-700">Email verified successfully!</span>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {!currentUniversity && (
            <div className="text-center text-gray-400">
              <p className="text-sm">Search for your university below</p>
            </div>
          )}
        </div>
      </div>

      {/* University Search - Bottom */}
      <div className="absolute bottom-0 left-6 right-6">
        <div className="relative">
          <Label className="text-sm">Select University</Label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Building size={14} className="absolute left-3 top-2.5 text-gray-400" />
              <Input
                value={universitySearchInput}
                onChange={(e) => handleUniversitySearch(e.target.value)}
                onFocus={() => setShowUniversityDropdown(universitySearchInput.length > 0)}
                onBlur={() => setTimeout(() => setShowUniversityDropdown(false), 200)}
                placeholder="Search for your university..."
                className="pl-9 h-9"
              />
              
              {/* Auto-completion dropdown */}
              <AnimatePresence>
                {showUniversityDropdown && filteredUniversities.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-40 overflow-y-auto"
                  >
                    {filteredUniversities.map((university, index) => (
                      <button
                        key={university}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg"
                        onMouseDown={() => selectUniversity(university)}
                      >
                        {university}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <Button
              type="button"
              onClick={() => {
                if (universitySearchInput.trim()) {
                  selectUniversity(universitySearchInput.trim());
                }
              }}
              disabled={!universitySearchInput.trim()}
              className="h-9 w-9 p-0"
            >
              <CheckCircle size={16} />
            </Button>
          </div>
        </div>
      </div>
    </div>
  ), [
    currentUniversity, 
    isUniversitySelected, 
    universityEmail, 
    universitySearchInput, 
    showUniversityDropdown, 
    filteredUniversities, 
    codeSent, 
    emailVerified, 
    verificationCode,
    handleUniversitySearch,
    selectUniversity,
    sendVerificationCode,
    verifyCode,
    validateUniversityEmail
  ]);

  const renderAuthentication = useCallback(() => (
    <div className="flex flex-col h-full py-6 relative">
      <div className="text-center space-y-6">
        <div>
          <Shield size={32} className="text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Profile Complete</h2>
          <p className="text-sm text-gray-600">
            Complete WeChat verification to join the community
          </p>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle size={20} className="text-green-600" />
            <span className="text-sm font-medium">Profile completed</span>
          </div>
          
          {emailVerified && (
            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <CheckCircle size={20} className="text-green-600" />
              <span className="text-sm font-medium">University email verified</span>
            </div>
          )}

          {wechatAuthenticated && (
            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <CheckCircle size={20} className="text-green-600" />
              <span className="text-sm font-medium">WeChat verified</span>
            </div>
          )}
        </div>

        {!wechatAuthenticated && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 justify-center mb-2">
              <MessageCircle size={18} className="text-blue-600" />
              <span className="text-sm font-medium text-blue-800">WeChat Verification Required</span>
            </div>
            <p className="text-xs text-blue-700">
              Verify your identity for secure networking
            </p>
          </div>
        )}

        <p className="text-xs text-gray-500">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>

      {/* WeChat Sign In Button - Fixed at bottom */}
      {!wechatAuthenticated && (
        <div className="absolute bottom-0 left-6 right-6">
          <Button 
            className="w-full bg-green-600 hover:bg-green-700 text-white py-3 text-sm font-medium"
            onClick={() => {
              // Simulate WeChat authentication
              setWechatAuthenticated(true);
              console.log('WeChat authentication completed');
            }}
          >
            <MessageCircle size={18} className="mr-2" />
            Sign in with WeChat
          </Button>
        </div>
      )}
    </div>
  ), [emailVerified, wechatAuthenticated]);

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: return renderDemographics();
      case 1: return renderSkills();
      case 2: return renderResources();
      case 3: return renderProjects();
      case 4: return renderGoals();
      case 5: return renderDemands();
      case 6: return renderInstitutions();
      case 7: return renderCurrentUniversity();
      case 8: return renderAuthentication();
      default: return null;
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Progress Bar */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-500">{steps[currentStep]}</span>
          <span className="text-sm text-gray-500">{currentStep + 1}/{steps.length}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div 
            className="bg-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Step Content */}
      <div className="flex-1 px-6 overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="h-full"
          >
            {renderStepContent()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation Buttons */}
      <div className="p-6 flex gap-4">
        <Button 
          variant="outline" 
          onClick={handlePrevious}
          className="flex-1"
        >
          {currentStep === 0 ? 'Back' : 'Previous'}
        </Button>
        <Button 
          onClick={handleNext} 
          disabled={!canProceed()}
          className="flex-1"
        >
          {currentStep === steps.length - 1 ? (
            <>
              Complete
              <ChevronRight size={16} className="ml-1" />
            </>
          ) : (
            <>
              Next
              <ChevronRight size={16} className="ml-1" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}