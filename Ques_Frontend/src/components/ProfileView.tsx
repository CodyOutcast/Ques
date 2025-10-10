import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Edit, User, Briefcase, Target, GraduationCap, Globe, Clock, Heart, MapPin, Building, Camera, Info, Package, Search, Sparkles, Check, X, Plus, Save, Undo, Languages, MessageCircle, CheckCircle, Mail } from 'lucide-react';
import type { UserProfile } from '../App';
import { useLanguage } from '../contexts';

interface ProfileViewProps {
  userProfile: UserProfile;
  onUpdate: (profile: UserProfile) => void;
}

export function ProfileView({ userProfile, onUpdate }: ProfileViewProps) {
  const { t } = useLanguage();
  const [isEditing, setIsEditing] = useState(false);
  const [showPhotoTip, setShowPhotoTip] = useState(false);
  const [showCompletenessTip, setShowCompletenessTip] = useState(false);
  const [activeSuggestions, setActiveSuggestions] = useState<Set<string>>(new Set());
  
  // Individual section editing states
  const [editingSections, setEditingSections] = useState<Set<string>>(new Set());
  
  // Temporary editing values
  const [tempValues, setTempValues] = useState<Partial<UserProfile>>({});
  const [tempSkill, setTempSkill] = useState('');
  const [tempResource, setTempResource] = useState('');
  const [tempDemand, setTempDemand] = useState('');
  const [tempGoal, setTempGoal] = useState('');
  const [tempHobby, setTempHobby] = useState('');
  const [tempLanguage, setTempLanguage] = useState('');

  // University verification states
  const [universityEmail, setUniversityEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [emailVerified, setEmailVerified] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  
  // Word count error states for tag inputs
  const [hobbyWordError, setHobbyWordError] = useState(false);
  const [languageWordError, setLanguageWordError] = useState(false);
  const [skillWordError, setSkillWordError] = useState(false);
  const [resourceWordError, setResourceWordError] = useState(false);
  const [goalWordError, setGoalWordError] = useState(false);
  const [demandWordError, setDemandWordError] = useState(false);

  const startEditing = (sectionId: string) => {
    setEditingSections(prev => new Set([...prev, sectionId]));
    // Initialize temp values for this section
    if (sectionId === 'basic-info') {
      setTempValues(prev => ({
        ...prev,
        name: userProfile.name,
        age: userProfile.age,
        gender: userProfile.gender,
        location: userProfile.location,
        oneSentenceIntro: userProfile.oneSentenceIntro,
        hobbies: [...(userProfile.hobbies || [])],
        languages: [...(userProfile.languages || [])]
      }));
    } else if (sectionId === 'skills') {
      setTempValues(prev => ({
        ...prev,
        skills: [...(userProfile.skills || [])]
      }));
    } else if (sectionId === 'resources') {
      setTempValues(prev => ({
        ...prev,
        resources: [...(userProfile.resources || [])]
      }));
    } else if (sectionId === 'projects') {
      setTempValues(prev => ({
        ...prev,
        projects: userProfile.projects.map(p => ({ ...p, referenceLinks: [...p.referenceLinks] }))
      }));
    } else if (sectionId === 'goals') {
      setTempValues(prev => ({
        ...prev,
        goals: [...(userProfile.goals || [])]
      }));
    } else if (sectionId === 'demands') {
      setTempValues(prev => ({
        ...prev,
        demands: [...(userProfile.demands || [])]
      }));
    } else if (sectionId === 'institutions') {
      setTempValues(prev => ({
        ...prev,
        institutions: userProfile.institutions.map(i => ({ ...i }))
      }));
    } else if (sectionId === 'university') {
      setTempValues(prev => ({
        ...prev,
        university: userProfile.university ? { ...userProfile.university } : { name: '', verified: false }
      }));
      // Reset verification states when starting to edit
      resetUniversityVerification();
    }
  };

  const cancelEditing = (sectionId: string) => {
    setEditingSections(prev => {
      const newSet = new Set(prev);
      newSet.delete(sectionId);
      return newSet;
    });
    // Clear temp values for this section
    const keysToRemove = getSectionKeys(sectionId);
    setTempValues(prev => {
      const newValues = { ...prev };
      keysToRemove.forEach(key => delete newValues[key as keyof typeof newValues]);
      return newValues;
    });
    // Reset temp input states
    setTempSkill('');
    setTempResource('');
    setTempDemand('');
    setTempGoal('');
    setTempHobby('');
    setTempLanguage('');
    
    // Reset university verification states if canceling university editing
    if (sectionId === 'university') {
      resetUniversityVerification();
    }
  };

  const saveEditing = (sectionId: string) => {
    const sectionKeys = getSectionKeys(sectionId);
    const updatedProfile = { ...userProfile };
    
    sectionKeys.forEach(key => {
      if (tempValues[key] !== undefined) {
        (updatedProfile as any)[key] = tempValues[key];
      }
    });

    onUpdate(updatedProfile);
    cancelEditing(sectionId);
  };

  const saveAllEditing = () => {
    // Create a copy of editing sections to avoid modifying the set during iteration
    const sectionsToSave = Array.from(editingSections);
    
    // Merge all changes into one update
    let updatedProfile = { ...userProfile };
    
    sectionsToSave.forEach(sectionId => {
      const sectionKeys = getSectionKeys(sectionId);
      
      sectionKeys.forEach(key => {
        if (tempValues[key] !== undefined) {
          (updatedProfile as any)[key] = tempValues[key];
        }
      });
    });
    
    // Single update call
    onUpdate(updatedProfile);
    
    // Clear all editing states
    setEditingSections(new Set());
    setTempValues({});
    
    // Reset all temp input states
    setTempSkill('');
    setTempResource('');
    setTempDemand('');
    setTempGoal('');
    setTempHobby('');
    setTempLanguage('');
    
    // Exit global editing mode
    setIsEditing(false);
  };

  const toggleEditing = () => {
    if (isEditing) {
      // Save all and exit editing mode
      saveAllEditing();
    } else {
      // Enter editing mode
      setIsEditing(true);
    }
  };

  const getSectionKeys = (sectionId: string): (keyof UserProfile)[] => {
    switch (sectionId) {
      case 'basic-info':
        return ['name', 'age', 'gender', 'location', 'oneSentenceIntro', 'hobbies', 'languages'];
      case 'skills':
        return ['skills'];
      case 'resources':
        return ['resources'];
      case 'projects':
        return ['projects'];
      case 'goals':
        return ['goals'];
      case 'demands':
        return ['demands'];
      case 'institutions':
        return ['institutions'];
      case 'university':
        return ['university'];
      default:
        return [];
    }
  };

  const updateTempValue = (key: keyof UserProfile, value: any) => {
    setTempValues(prev => ({ ...prev, [key]: value }));
  };

  // Helper function to check word count
  const checkWordCount = (value: string) => {
    if (!value.trim()) return 0;
    return value.trim().split(/\s+/).length;
  };

  const addToTempArray = (key: keyof UserProfile, value: string, tempSetter?: (val: string) => void, errorSetter?: (error: boolean) => void) => {
    if (value.trim()) {
      const currentArray = (tempValues[key] as string[]) || [];
      
      // Check if array already has 5 items
      if (currentArray.length >= 5) {
        return;
      }
      
      // Check if value exceeds 15 words
      const wordCount = checkWordCount(value);
      if (wordCount > 15) {
        if (errorSetter) errorSetter(true);
        return;
      }
      
      updateTempValue(key, [...currentArray, value.trim()]);
      if (tempSetter) tempSetter('');
      if (errorSetter) errorSetter(false);
    }
  };

  const removeFromTempArray = (key: keyof UserProfile, index: number) => {
    const currentArray = (tempValues[key] as string[]) || [];
    updateTempValue(key, currentArray.filter((_, i) => i !== index));
  };

  const addTempProject = () => {
    const currentProjects = (tempValues.projects || []) as UserProfile['projects'];
    const newProject = {
      title: '',
      role: '',
      description: '',
      referenceLinks: []
    };
    updateTempValue('projects', [...currentProjects, newProject]);
  };

  const updateTempProject = (index: number, field: string, value: any) => {
    const currentProjects = (tempValues.projects || []) as UserProfile['projects'];
    const updatedProjects = [...currentProjects];
    updatedProjects[index] = { ...updatedProjects[index], [field]: value };
    updateTempValue('projects', updatedProjects);
  };

  const removeTempProject = (index: number) => {
    const currentProjects = (tempValues.projects || []) as UserProfile['projects'];
    updateTempValue('projects', currentProjects.filter((_, i) => i !== index));
  };

  const addTempInstitution = () => {
    const currentInstitutions = (tempValues.institutions || []) as UserProfile['institutions'];
    const newInstitution = {
      name: '',
      role: '',
      description: '',
      verified: false
    };
    updateTempValue('institutions', [...currentInstitutions, newInstitution]);
  };

  const updateTempInstitution = (index: number, field: string, value: any) => {
    const currentInstitutions = (tempValues.institutions || []) as UserProfile['institutions'];
    const updatedInstitutions = [...currentInstitutions];
    updatedInstitutions[index] = { ...updatedInstitutions[index], [field]: value };
    updateTempValue('institutions', updatedInstitutions);
  };

  const removeTempInstitution = (index: number) => {
    const currentInstitutions = (tempValues.institutions || []) as UserProfile['institutions'];
    updateTempValue('institutions', currentInstitutions.filter((_, i) => i !== index));
  };

  const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        const updatedProfile = { ...userProfile, profilePhoto: result };
        onUpdate(updatedProfile);
      };
      reader.readAsDataURL(file);
    }
  };

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
        if (!userProfile.goals || !userProfile.goals.length) return null;
        const currentGoals = userProfile.goals.join('\n');
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
        updatedProfile.goals = [suggestion.improved as string];
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

  const validateUniversityEmail = (email: string, universityName: string) => {
    if (!email || !universityName) return false;
    
    const eduCnPattern = /\.edu\.cn$/;
    const commonDomains = [
      'tsinghua.edu.cn', 'pku.edu.cn', 'fudan.edu.cn', 'sjtu.edu.cn',
      'zju.edu.cn', 'ustc.edu.cn', 'nju.edu.cn', 'xjtu.edu.cn'
    ];
    
    return eduCnPattern.test(email) || 
           commonDomains.some(domain => email.endsWith(domain));
  };

  const sendVerificationCode = () => {
    const universityName = tempValues.university?.name || '';
    if (universityEmail && validateUniversityEmail(universityEmail, universityName)) {
      setCodeSent(true);
      console.log('Verification code sent to:', universityEmail);
    }
  };

  const verifyCode = () => {
    if (verificationCode.length === 6) {
      setEmailVerified(true);
      // Update temp university with verified status
      updateTempValue('university', { 
        name: tempValues.university?.name || '', 
        verified: true 
      });
      console.log('Code verified:', verificationCode);
    }
  };

  const resetUniversityVerification = () => {
    setUniversityEmail('');
    setVerificationCode('');
    setEmailVerified(false);
    setCodeSent(false);
  };

  // Basic Info Edit Component
  const renderBasicInfoEdit = () => (
    <div className="space-y-4">
      {/* Profile Photo - Side by side with basic info */}
      <div className="grid grid-cols-3 gap-3 items-start">
        <div className="col-span-1 flex flex-col items-center">
          <div className="relative">
            <div 
              className="bg-gray-100 border-2 border-gray-200 rounded-lg cursor-pointer flex items-center justify-center overflow-hidden"
              style={{ width: '90px', height: '120px' }}
              onClick={() => document.getElementById('photo-upload-edit')?.click()}
            >
              {userProfile.profilePhoto ? (
                <img 
                  src={userProfile.profilePhoto} 
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
            <Button 
              size="sm" 
              variant="outline" 
              className="absolute -bottom-1 -right-1 rounded-full w-6 h-6 p-0"
              onClick={() => document.getElementById('photo-upload-edit')?.click()}
            >
              <Camera size={12} />
            </Button>
          </div>
          <input
            id="photo-upload-edit"
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            className="hidden"
          />
        </div>

        <div className="col-span-2 space-y-3">
          <div>
            <Label className="text-sm">{t('profile.name')} *</Label>
            <Input
              value={tempValues.name || ''}
              onChange={(e) => updateTempValue('name', e.target.value)}
              placeholder={t('profile.namePlaceholder')}
              className="h-8"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className="text-sm">{t('profile.age')} *</Label>
              <Input
                value={tempValues.age || ''}
                onChange={(e) => updateTempValue('age', e.target.value)}
                placeholder="25"
                type="number"
                min="1"
                max="120"
                className="h-8"
              />
            </div>
            <div>
              <Label className="text-sm">{t('profile.gender')} *</Label>
              <Select value={tempValues.gender || ''} onValueChange={(value) => updateTempValue('gender', value)}>
                <SelectTrigger className="h-8">
                  <SelectValue placeholder={t('profile.selectGender')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">{t('profile.male')}</SelectItem>
                  <SelectItem value="female">{t('profile.female')}</SelectItem>
                  <SelectItem value="other">{t('profile.other')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>

      {/* Location */}
      <div>
        <Label className="text-sm">{t('profile.location')} *</Label>
        <div className="relative">
          <MapPin size={14} className="absolute left-3 top-2 text-gray-400" />
          <Input
            value={tempValues.location || ''}
            onChange={(e) => updateTempValue('location', e.target.value)}
            placeholder={t('profile.locationPlaceholder')}
            className="pl-9 h-8"
          />
        </div>
      </div>

      {/* One sentence intro */}
      <div>
        <Label className="text-sm">{t('profile.oneSentence')}</Label>
        <div className="relative">
          <MessageCircle size={14} className="absolute left-3 top-2 text-gray-400" />
          <Input
            value={tempValues.oneSentenceIntro || ''}
            onChange={(e) => updateTempValue('oneSentenceIntro', e.target.value)}
            placeholder={t('profile.oneSentencePlaceholder')}
            className="pl-9 h-8"
            maxLength={150}
          />
        </div>
      </div>

      {/* Hobbies */}
      <div>
        <Label className="text-sm">{t('profile.hobbies')} <span className="text-xs text-gray-400">({(tempValues.hobbies || []).length}/5, {t('profile.maxItemsNote')})</span></Label>
        <div className="flex gap-2 mb-2">
          <Input
            value={tempHobby}
            onChange={(e) => {
              const value = e.target.value;
              setTempHobby(value);
              const wordCount = checkWordCount(value);
              setHobbyWordError(wordCount > 15);
            }}
            placeholder={t('profile.addHobby')}
            onKeyPress={(e) => e.key === 'Enter' && addToTempArray('hobbies', tempHobby, setTempHobby, setHobbyWordError)}
            className={`h-8 text-sm ${hobbyWordError ? 'border-red-500' : ''}`}
            disabled={(tempValues.hobbies || []).length >= 5}
          />
          <Button 
            type="button" 
            size="sm"
            onClick={() => addToTempArray('hobbies', tempHobby, setTempHobby, setHobbyWordError)}
            className="h-8 px-2"
            disabled={(tempValues.hobbies || []).length >= 5 || hobbyWordError}
          >
            <Plus size={12} />
          </Button>
        </div>
        {hobbyWordError && (
          <p className="text-xs text-red-500 mb-1">{t('profile.wordLimitError')} {checkWordCount(tempHobby)} {t('profile.words')}</p>
        )}
        <div className="flex flex-wrap gap-1">
          {(tempValues.hobbies || []).map((hobby, index) => (
            <Badge key={index} variant="secondary" className="text-xs pr-0.5 h-6">
              <span className="max-w-20 truncate">{hobby}</span>
              <Button
                size="sm"
                variant="ghost"
                className="h-3 w-3 p-0 ml-0.5"
                onClick={() => removeFromTempArray('hobbies', index)}
              >
                <X size={8} />
              </Button>
            </Badge>
          ))}
        </div>
      </div>

      {/* Languages */}
      <div>
        <Label className="text-sm">{t('profile.languages')} <span className="text-xs text-gray-400">({(tempValues.languages || []).length}/5, {t('profile.maxItemsNote')})</span></Label>
        <div className="flex gap-2 mb-2">
          <div className="relative flex-1">
            <Languages size={14} className="absolute left-3 top-1.5 text-gray-400" />
            <Input
              value={tempLanguage}
              onChange={(e) => {
                const value = e.target.value;
                setTempLanguage(value);
                const wordCount = checkWordCount(value);
                setLanguageWordError(wordCount > 15);
              }}
              placeholder={t('profile.addLanguage')}
              className={`pl-9 h-8 text-sm ${languageWordError ? 'border-red-500' : ''}`}
              onKeyPress={(e) => e.key === 'Enter' && addToTempArray('languages', tempLanguage, setTempLanguage, setLanguageWordError)}
              disabled={(tempValues.languages || []).length >= 5}
            />
          </div>
          <Button 
            type="button" 
            size="sm"
            onClick={() => addToTempArray('languages', tempLanguage, setTempLanguage, setLanguageWordError)}
            className="h-8 px-2"
            disabled={(tempValues.languages || []).length >= 5 || languageWordError}
          >
            <Plus size={12} />
          </Button>
        </div>
        {languageWordError && (
          <p className="text-xs text-red-500 mb-1">{t('profile.wordLimitError')} {checkWordCount(tempLanguage)} {t('profile.words')}</p>
        )}
        <div className="flex flex-wrap gap-1">
          {(tempValues.languages || []).map((language, index) => (
            <Badge key={index} variant="secondary" className="text-xs pr-0.5 h-6">
              <span className="max-w-20 truncate">{language}</span>
              <Button
                size="sm"
                variant="ghost"
                className="h-3 w-3 p-0 ml-0.5"
                onClick={() => removeFromTempArray('languages', index)}
              >
                <X size={8} />
              </Button>
            </Badge>
          ))}
        </div>
      </div>
    </div>
  );

  // Skills Edit Component
  const renderSkillsEdit = () => (
    <div className="space-y-3">
      <Label className="text-xs text-gray-500">({(tempValues.skills || []).length}/5, {t('profile.maxItemsNote')})</Label>
      <div className="flex gap-2 mb-2">
        <Input
          value={tempSkill}
          onChange={(e) => {
            const value = e.target.value;
            setTempSkill(value);
            const wordCount = checkWordCount(value);
            setSkillWordError(wordCount > 15);
          }}
          placeholder={t('profile.addSkill')}
          onKeyPress={(e) => e.key === 'Enter' && addToTempArray('skills', tempSkill, setTempSkill, setSkillWordError)}
          className={`h-8 text-sm ${skillWordError ? 'border-red-500' : ''}`}
          disabled={(tempValues.skills || []).length >= 5}
        />
        <Button 
          type="button" 
          size="sm"
          onClick={() => addToTempArray('skills', tempSkill, setTempSkill, setSkillWordError)}
          className="h-8 px-2"
          disabled={(tempValues.skills || []).length >= 5 || skillWordError}
        >
          <Plus size={12} />
        </Button>
      </div>
      {skillWordError && (
        <p className="text-xs text-red-500 mb-1">{t('profile.wordLimitError')} {checkWordCount(tempSkill)} {t('profile.words')}</p>
      )}
      <div className="flex flex-wrap gap-2">
        {(tempValues.skills || []).map((skill, index) => (
          <Badge key={index} variant="secondary" className="pr-1 break-words whitespace-normal max-w-full">
            {skill}
            <Button
              size="sm"
              variant="ghost"
              className="h-4 w-4 p-0 ml-1 flex-shrink-0"
              onClick={() => removeFromTempArray('skills', index)}
            >
              <X size={10} />
            </Button>
          </Badge>
        ))}
      </div>
    </div>
  );

  // Resources Edit Component  
  const renderResourcesEdit = () => (
    <div className="space-y-3">
      <Label className="text-xs text-gray-500">({(tempValues.resources || []).length}/5, {t('profile.maxItemsNote')})</Label>
      <div className="flex gap-2 mb-2">
        <Input
          value={tempResource}
          onChange={(e) => {
            const value = e.target.value;
            setTempResource(value);
            const wordCount = checkWordCount(value);
            setResourceWordError(wordCount > 15);
          }}
          placeholder={t('profile.addResource')}
          onKeyPress={(e) => e.key === 'Enter' && addToTempArray('resources', tempResource, setTempResource, setResourceWordError)}
          className={`h-8 text-sm ${resourceWordError ? 'border-red-500' : ''}`}
          disabled={(tempValues.resources || []).length >= 5}
        />
        <Button 
          type="button" 
          size="sm"
          onClick={() => addToTempArray('resources', tempResource, setTempResource, setResourceWordError)}
          className="h-8 px-2"
          disabled={(tempValues.resources || []).length >= 5 || resourceWordError}
        >
          <Plus size={12} />
        </Button>
      </div>
      {resourceWordError && (
        <p className="text-xs text-red-500 mb-1">{t('profile.wordLimitError')} {checkWordCount(tempResource)} {t('profile.words')}</p>
      )}
      <div className="flex flex-wrap gap-2">
        {(tempValues.resources || []).map((resource, index) => (
          <Badge key={index} variant="outline" className="text-green-700 border-green-300 pr-1 break-words whitespace-normal max-w-full">
            {resource}
            <Button
              size="sm"
              variant="ghost"
              className="h-4 w-4 p-0 ml-1 flex-shrink-0"
              onClick={() => removeFromTempArray('resources', index)}
            >
              <X size={10} />
            </Button>
          </Badge>
        ))}
      </div>
    </div>
  );

  // Projects Edit Component
  const renderProjectsEdit = () => (
    <div className="space-y-4">
      {(tempValues.projects || []).map((project, index) => (
        <Card key={index} className="p-4">
          <div className="space-y-3">
            <div className="flex justify-between items-start">
              <h5 className="font-medium text-sm">{t('profile.projectNumber')} {index + 1}</h5>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => removeTempProject(index)}
                className="text-red-500 hover:text-red-700"
              >
                <X size={16} />
              </Button>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-sm">{t('profile.projectTitle')}</Label>
                <Input
                  value={project.title}
                  onChange={(e) => updateTempProject(index, 'title', e.target.value)}
                  placeholder={t('profile.projectTitlePlaceholder')}
                  className="h-8"
                />
              </div>
              <div>
                <Label className="text-sm">{t('profile.yourRole')}</Label>
                <Input
                  value={project.role}
                  onChange={(e) => updateTempProject(index, 'role', e.target.value)}
                  placeholder={t('profile.yourRolePlaceholder')}
                  className="h-8"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-sm">{t('profile.description')}</Label>
              <Textarea
                value={project.description}
                onChange={(e) => updateTempProject(index, 'description', e.target.value)}
                placeholder={t('profile.descriptionPlaceholder')}
                rows={3}
                className="text-sm"
              />
            </div>
            
            <div>
              <Label className="text-sm">{t('profile.referenceLinks')}</Label>
              <Input
                value={project.referenceLinks.join(', ')}
                onChange={(e) => updateTempProject(index, 'referenceLinks', e.target.value.split(', ').filter(link => link.trim()))}
                placeholder={t('profile.referenceLinksPlaceholder')}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </Card>
      ))}
      <Button onClick={addTempProject} variant="outline" className="w-full">
        <Plus size={16} className="mr-2" />
        {t('profile.addProject')}
      </Button>
    </div>
  );

  // Goals Edit Component
  const renderGoalsEdit = () => (
    <div className="space-y-3">
      <Label className="text-xs text-gray-500">({(tempValues.goals || []).length}/5, {t('profile.maxItemsNote')})</Label>
      <div className="flex gap-2 mb-2">
        <Input
          value={tempGoal}
          onChange={(e) => {
            const value = e.target.value;
            setTempGoal(value);
            const wordCount = checkWordCount(value);
            setGoalWordError(wordCount > 15);
          }}
          placeholder={t('profile.goalPlaceholder')}
          onKeyPress={(e) => e.key === 'Enter' && addToTempArray('goals', tempGoal, setTempGoal, setGoalWordError)}
          className={`h-8 text-sm ${goalWordError ? 'border-red-500' : ''}`}
          disabled={(tempValues.goals || []).length >= 5}
        />
        <Button 
          type="button" 
          size="sm"
          onClick={() => addToTempArray('goals', tempGoal, setTempGoal, setGoalWordError)}
          className="h-8 px-2"
          disabled={(tempValues.goals || []).length >= 5 || goalWordError}
        >
          <Plus size={12} />
        </Button>
      </div>
      {goalWordError && (
        <p className="text-xs text-red-500 mb-1">{t('profile.wordLimitError')} {checkWordCount(tempGoal)} {t('profile.words')}</p>
      )}
      <div className="flex flex-wrap gap-2">
        {(tempValues.goals || []).map((goal, index) => (
          <Badge key={index} variant="outline" className="text-blue-700 border-blue-300 pr-1 break-words whitespace-normal max-w-full">
            {goal}
            <Button
              size="sm"
              variant="ghost"
              className="h-4 w-4 p-0 ml-1 flex-shrink-0"
              onClick={() => removeFromTempArray('goals', index)}
            >
              <X size={10} />
            </Button>
          </Badge>
        ))}
      </div>
    </div>
  );

  // Demands Edit Component
  const renderDemandsEdit = () => (
    <div className="space-y-3">
      <Label className="text-xs text-gray-500">({(tempValues.demands || []).length}/5, {t('profile.maxItemsNote')})</Label>
      <div className="flex gap-2 mb-2">
        <Input
          value={tempDemand}
          onChange={(e) => {
            const value = e.target.value;
            setTempDemand(value);
            const wordCount = checkWordCount(value);
            setDemandWordError(wordCount > 15);
          }}
          placeholder={t('profile.demandPlaceholder')}
          onKeyPress={(e) => e.key === 'Enter' && addToTempArray('demands', tempDemand, setTempDemand, setDemandWordError)}
          className={`h-8 text-sm ${demandWordError ? 'border-red-500' : ''}`}
          disabled={(tempValues.demands || []).length >= 5}
        />
        <Button 
          type="button" 
          size="sm"
          onClick={() => addToTempArray('demands', tempDemand, setTempDemand, setDemandWordError)}
          className="h-8 px-2"
          disabled={(tempValues.demands || []).length >= 5 || demandWordError}
        >
          <Plus size={12} />
        </Button>
      </div>
      {demandWordError && (
        <p className="text-xs text-red-500 mb-1">{t('profile.wordLimitError')} {checkWordCount(tempDemand)} {t('profile.words')}</p>
      )}
      <div className="flex flex-wrap gap-2">
        {(tempValues.demands || []).map((demand, index) => (
          <Badge key={index} variant="outline" className="text-orange-700 border-orange-300 pr-1 break-words whitespace-normal max-w-full">
            {demand}
            <Button
              size="sm"
              variant="ghost"
              className="h-4 w-4 p-0 ml-1 flex-shrink-0"
              onClick={() => removeFromTempArray('demands', index)}
            >
              <X size={10} />
            </Button>
          </Badge>
        ))}
      </div>
    </div>
  );

  // Institutions Edit Component
  const renderInstitutionsEdit = () => (
    <div className="space-y-4">
      {(tempValues.institutions || []).map((institution, index) => (
        <Card key={index} className="p-4 bg-gray-50">
          <div className="space-y-3">
            <div className="flex justify-between items-start">
              <h5 className="font-medium text-sm">{t('profile.institutionNumber')} {index + 1}</h5>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => removeTempInstitution(index)}
                className="text-red-500 hover:text-red-700"
              >
                <X size={16} />
              </Button>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-sm">{t('profile.institutionName')}</Label>
                <Input
                  value={institution.name}
                  onChange={(e) => updateTempInstitution(index, 'name', e.target.value)}
                  placeholder={t('profile.institutionNamePlaceholder')}
                  className="h-8"
                />
              </div>
              <div>
                <Label className="text-sm">{t('profile.institutionRole')}</Label>
                <Input
                  value={institution.role}
                  onChange={(e) => updateTempInstitution(index, 'role', e.target.value)}
                  placeholder={t('profile.institutionRolePlaceholder')}
                  className="h-8"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-sm">{t('profile.institutionDescription')}</Label>
              <Textarea
                value={institution.description}
                onChange={(e) => updateTempInstitution(index, 'description', e.target.value)}
                placeholder={t('profile.institutionDescriptionPlaceholder')}
                rows={3}
                className="text-sm"
              />
            </div>
          </div>
        </Card>
      ))}
      <Button onClick={addTempInstitution} variant="outline" className="w-full">
        <Plus size={16} className="mr-2" />
        {t('profile.addInstitution')}
      </Button>
    </div>
  );

  // University Edit Component
  const renderUniversityEdit = () => (
    <div className="space-y-4">
      <div>
        <Label className="text-sm">{t('profile.universityName')} *</Label>
        <Input
          value={tempValues.university?.name || ''}
          onChange={(e) => {
            updateTempValue('university', { 
              name: e.target.value, 
              verified: false // Reset verified status when name changes
            });
            resetUniversityVerification(); // Reset verification process
          }}
          placeholder={t('profile.universityNamePlaceholder')}
          className="h-8"
        />
      </div>
      
      {tempValues.university?.name && (
        <>
          <div>
            <Label className="text-sm">{t('profile.universityEmail')} *</Label>
            <div className="relative">
              <Mail size={14} className="absolute left-3 top-2 text-gray-400" />
              <Input
                value={universityEmail}
                onChange={(e) => setUniversityEmail(e.target.value)}
                placeholder={t('profile.universityEmailPlaceholder')}
                className="pl-9 h-8"
                disabled={emailVerified}
              />
              {emailVerified && (
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                  <CheckCircle size={16} className="text-green-600" />
                </div>
              )}
            </div>
          </div>

          {universityEmail && !codeSent && !emailVerified && (
            <Button
              onClick={sendVerificationCode}
              disabled={!validateUniversityEmail(universityEmail, tempValues.university?.name || '')}
              className="w-full h-8 text-sm"
              size="sm"
            >
              {t('profile.sendVerificationCode')}
            </Button>
          )}

          {codeSent && !emailVerified && (
            <div className="space-y-3">
              <div>
                <Label className="text-sm">{t('profile.verificationCode')}</Label>
                <Input
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder={t('profile.verificationCodePlaceholder')}
                  className="h-8"
                  maxLength={6}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={verifyCode}
                  disabled={verificationCode.length !== 6}
                  className="flex-1 h-8 text-sm"
                  size="sm"
                >
                  {t('profile.verifyCode')}
                </Button>
                <Button
                  onClick={() => {
                    setCodeSent(false);
                    setVerificationCode('');
                  }}
                  variant="outline"
                  className="flex-1 h-8 text-sm"
                  size="sm"
                >
                  {t('profile.resendCode')}
                </Button>
              </div>
            </div>
          )}

          {emailVerified && (
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
              <CheckCircle size={16} className="text-green-600" />
              <span className="text-sm text-green-700 font-medium">{t('profile.emailVerified')}</span>
            </div>
          )}

          {!validateUniversityEmail(universityEmail, tempValues.university?.name || '') && universityEmail && (
            <p className="text-xs text-red-500">
              {t('profile.emailVerificationNote')}
            </p>
          )}
        </>
      )}
    </div>
  );

  const profileSections = [
    {
      id: 'skills',
      title: t('profile.skills'),
      icon: Briefcase,
      content: (
        <div className="space-y-3">
          {editingSections.has('skills') ? (
            renderSkillsEdit()
          ) : (
            <>
              {userProfile.skills && userProfile.skills.length > 0 ? (
                <>
                  <div className="flex flex-wrap gap-2">
                    {userProfile.skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="break-words whitespace-normal max-w-full">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                  
                  {activeSuggestions.has('skills') && (() => {
                    const suggestion = generateSuggestion('skills');
                    return suggestion ? (
                      <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                        <div className="flex items-start gap-2 mb-3">
                          <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <h5 className="text-sm font-medium text-purple-800 mb-1">{t('profile.aiSuggestion')}</h5>
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
                <p className="text-sm text-gray-400 italic">{t('profile.noSkillsAdded')}</p>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'resources',
      title: t('profile.resources'),
      icon: Package,
      content: (
        <div className="space-y-3">
          {editingSections.has('resources') ? (
            renderResourcesEdit()
          ) : (
            <>
              {userProfile.resources && userProfile.resources.length > 0 ? (
                <>
                  <div className="flex flex-wrap gap-2">
                    {userProfile.resources.map((resource, index) => (
                      <Badge key={index} variant="outline" className="text-green-700 border-green-300 break-words whitespace-normal max-w-full">
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
                            <h5 className="text-sm font-medium text-purple-800 mb-1">{t('profile.aiSuggestion')}</h5>
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
                <p className="text-sm text-gray-400 italic">{t('profile.noResourcesAdded')}</p>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'projects',
      title: t('profile.pastProjects'),
      icon: Target,
      content: (
        <div className="space-y-4">
          {editingSections.has('projects') ? (
            renderProjectsEdit()
          ) : (
            <>
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
                            <p className="text-xs font-medium text-gray-500 mb-1">{t('profile.references')}</p>
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
                            <h5 className="text-sm font-medium text-purple-800 mb-1">{t('profile.aiSuggestion')}</h5>
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
                <p className="text-sm text-gray-400 italic">{t('profile.noProjectsAdded')}</p>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'goals',
      title: t('profile.goals'),
      icon: Target,
      content: (
        <div className="space-y-3">
          {editingSections.has('goals') ? (
            renderGoalsEdit()
          ) : (
            <>
              {userProfile.goals && userProfile.goals.length > 0 ? (
                <>
                  <div className="flex flex-wrap gap-2">
                    {userProfile.goals.map((goal, index) => (
                      <Badge key={index} variant="outline" className="text-blue-700 border-blue-300 break-words whitespace-normal max-w-full">
                        {goal}
                      </Badge>
                    ))}
                  </div>
                  
                  {activeSuggestions.has('goals') && (() => {
                    const suggestion = generateSuggestion('goals');
                    return suggestion ? (
                      <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                        <div className="flex items-start gap-2 mb-3">
                          <Sparkles size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <h5 className="text-sm font-medium text-purple-800 mb-1">{t('profile.aiSuggestion')}</h5>
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
                <p className="text-sm text-gray-400 italic">{t('profile.noGoalsAdded')}</p>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'demands',
      title: t('profile.demands'),
      icon: Search,
      content: (
        <div className="space-y-3">
          {editingSections.has('demands') ? (
            renderDemandsEdit()
          ) : (
            <>
              {userProfile.demands && userProfile.demands.length > 0 ? (
                <>
                  <div className="flex flex-wrap gap-2">
                    {userProfile.demands.map((demand, index) => (
                      <Badge key={index} variant="outline" className="text-orange-700 border-orange-300 break-words whitespace-normal max-w-full">
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
                            <h5 className="text-sm font-medium text-purple-800 mb-1">{t('profile.aiSuggestion')}</h5>
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
                <p className="text-sm text-gray-400 italic">{t('profile.noDemandsAdded')}</p>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'institutions',
      title: t('profile.institutions'),
      icon: Building,
      content: (
        <div className="space-y-3">
          {editingSections.has('institutions') ? (
            renderInstitutionsEdit()
          ) : (
            <>
              {userProfile.institutions && userProfile.institutions.length > 0 ? (
                <>
                  <div className="space-y-3">
                    {userProfile.institutions.map((institution, index) => (
                      <Card key={index} className="p-3 bg-gray-50">
                        <div className="flex items-start justify-between mb-1">
                          <h5 className="font-medium text-sm">{institution.name}</h5>
                          {institution.verified && (
                            <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                              {t('profile.verified')}
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
                            <h5 className="text-sm font-medium text-purple-800 mb-1">{t('profile.aiSuggestion')}</h5>
                            <p className="text-xs text-purple-700 mb-3">{suggestion.reason}</p>
                          </div>
                        </div>
                        
                        <Card className="p-3 bg-white mb-4">
                          <div className="flex items-start justify-between mb-1">
                            <h5 className="font-medium text-sm">{(suggestion.improved as any).name}</h5>
                            {(suggestion.improved as any).verified && (
                              <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                                {t('profile.verified')}
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
                <p className="text-sm text-gray-400 italic">{t('profile.noInstitutionsAdded')}</p>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'university',
      title: t('profile.university'),
      icon: GraduationCap,
      content: (
        <div className="space-y-3">
          {editingSections.has('university') ? (
            renderUniversityEdit()
          ) : (
            <>
              {userProfile.university ? (
                <div className="space-y-3">
                  <Card className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                    <div className="flex items-start justify-between mb-1">
                      <h5 className="font-medium text-sm">{userProfile.university.name}</h5>
                      {userProfile.university.verified && (
                        <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-700">
                          🎓 {t('profile.verified')}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-blue-600">{t('profile.currentUniversity')}</p>
                  </Card>
                </div>
              ) : (
                <p className="text-sm text-gray-400 italic">{t('profile.noUniversityAdded')}</p>
              )}
            </>
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
      userProfile.goals && userProfile.goals.length > 0,
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
    <div className="h-full overflow-y-auto overflow-x-hidden bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-medium">{t('profile.myProfile')}</h1>
            <p className="text-sm text-gray-500">{t('profile.manageProfile')}</p>
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
                  if (section.id === 'goals') return userProfile.goals && userProfile.goals.length > 0;
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
              onClick={toggleEditing}
              className="w-10 h-10 p-0"
            >
              {isEditing ? <Save size={16} /> : <Edit size={16} />}
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
          <Card className="p-6 bg-gradient-to-r from-blue-50 to-blue-100 relative overflow-x-hidden">
            {/* Suggestion Buttons - Only show in view mode */}
            {!editingSections.has('basic-info') && (
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
            )}

            {editingSections.has('basic-info') ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-medium">{t('profile.editBasicInfo')}</h2>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => saveEditing('basic-info')}
                      className="h-8 bg-green-600 hover:bg-green-700 text-white"
                    >
                      <Save size={14} className="mr-1" />
                      {t('common.save')}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => cancelEditing('basic-info')}
                      className="h-8"
                    >
                      <Undo size={14} className="mr-1" />
                      {t('common.cancel')}
                    </Button>
                  </div>
                </div>
                {renderBasicInfoEdit()}
              </div>
            ) : (
              <>
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
                      <h2 className="text-xl font-medium">{userProfile.name || t('profile.yourName')}</h2>
                      {userProfile.oneSentenceIntro && (
                        <p className="text-sm text-gray-600 italic mt-1">"{userProfile.oneSentenceIntro}"</p>
                      )}
                    </div>
                    {isEditing && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => startEditing('basic-info')}
                        className="h-8 w-8 p-0"
                      >
                        <Edit size={14} />
                      </Button>
                    )}
                  </div>
                  
                  {/* Demographics & Personal Details Tags */}
                  <div className="flex flex-wrap gap-2 overflow-x-hidden min-w-0">
                    {userProfile.age && (
                      <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-blue-200">
                        {userProfile.age} {t('profile.yearsOld')}
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
                      <Badge key={index} variant="secondary" className="bg-purple-100 text-purple-700 border-purple-200 max-w-full whitespace-normal break-all">
                        {language}
                      </Badge>
                    ))}
                    {userProfile.hobbies && userProfile.hobbies.map((hobby, index) => (
                      <Badge key={index} variant="outline" className="text-pink-700 border-pink-300 bg-pink-50 max-w-full whitespace-normal break-all">
                        {hobby}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                {/* Profile Completeness */}
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">{t('profile.profileCompleteness')}</span>
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
              </>
            )}
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
                {isEditing && !editingSections.has(section.id) && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="ml-auto p-1"
                    onClick={() => startEditing(section.id)}
                  >
                    <Edit size={14} />
                  </Button>
                )}
                {editingSections.has(section.id) && (
                  <div className="ml-auto flex gap-1">
                    <Button
                      size="sm"
                      onClick={() => saveEditing(section.id)}
                      className="h-7 bg-green-600 hover:bg-green-700 text-white px-2"
                    >
                      <Save size={12} />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => cancelEditing(section.id)}
                      className="h-7 px-2"
                    >
                      <Undo size={12} />
                    </Button>
                  </div>
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
                <h3 className="text-lg font-medium">{t('profile.photoQualityTitle')}</h3>
              </div>
              
              <div className="space-y-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  {t('profile.photoQualityDesc')}
                </p>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-purple-800 mb-2">{t('profile.idealPhotos')}</h4>
                  <ul className="text-xs text-purple-700 space-y-1">
                    <li>{t('profile.photoTip1')}</li>
                    <li>{t('profile.photoTip2')}</li>
                    <li>{t('profile.photoTip3')}</li>
                    <li>{t('profile.photoTip4')}</li>
                  </ul>
                </div>
                
                <p className="text-xs text-gray-500">
                  {t('profile.photoTrustNote')}
                </p>
              </div>
              
              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowPhotoTip(false)}
                >
                  {t('profile.alreadyDid')}
                </Button>
                <Button
                  className="flex-1 bg-purple-500 hover:bg-purple-600"
                  onClick={() => {
                    setShowPhotoTip(false);
                    startEditing('basic-info');
                  }}
                >
                  {t('profile.changePhoto')}
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
                <h3 className="text-lg font-medium">{t('profile.completenessTitle')}</h3>
              </div>
              
              <div className="space-y-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  {t('profile.completenessDesc')}
                </p>

                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">{t('profile.currentCompleteness')}</span>
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
                  {t('profile.closeThisTip')}
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}