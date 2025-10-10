import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { ErrorMessage } from './ui/error';
import { LoadingOverlay, InlineLoading } from './ui/loading';
import { useProfileWizard } from '../hooks/useProfileWizard';
import { useLanguage } from '../contexts/LanguageContext';
import type { UserProfile } from '../App';
import { Camera, CheckCircle, X } from 'lucide-react';

interface ProfileSetupWizardAPIProps {
  onComplete: (profile: UserProfile) => void;
  onBack: () => void;
}

export function ProfileSetupWizardAPI({ onComplete, onBack }: ProfileSetupWizardAPIProps) {
  const { t } = useLanguage();
  const [currentStep, setCurrentStep] = useState(0);
  const [profile, setProfile] = useState<UserProfile>({
    name: '',
    age: '',
    gender: '',
    location: '',
    hobbies: [],
    languages: [],
    skills: [],
    resources: [],
    projects: [],
    goals: [],
    demands: [],
    institutions: [],
  });

  // 使用自定义hook
  const {
    isLoading,
    isSubmitting,
    error,
    uploadProgress,
    verificationSent,
    emailVerified,
    wechatAuthenticated,
    uploadAvatar,
    searchUniversities,
    sendUniversityVerification,
    verifyUniversityEmail,
    authenticateWechat,
    submitRegistration,
    validateProfile,
    validateChineseEmail,
    clearError,
  } = useProfileWizard();

  const [universityEmail, setUniversityEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [selectedUniversity, setSelectedUniversity] = useState('');
  const [verificationId, setVerificationId] = useState('');
  const [universitySearchQuery, setUniversitySearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // 处理头像上传
  const handlePhotoUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const url = await uploadAvatar(file);
      if (url) {
        setProfile(prev => ({ ...prev, profilePhoto: url }));
      }
    }
  }, [uploadAvatar]);

  // 处理大学搜索
  const handleUniversitySearch = useCallback(async (query: string) => {
    setUniversitySearchQuery(query);
    if (query.length > 1) {
      const results = await searchUniversities(query);
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [searchUniversities]);

  // 发送大学验证邮件
  const handleSendVerification = useCallback(async () => {
    if (!selectedUniversity || !universityEmail) return;

    const success = await sendUniversityVerification(selectedUniversity, universityEmail);
    if (success) {
      setVerificationId('mock_verification_id'); // 实际应从API响应获取
    }
  }, [selectedUniversity, universityEmail, sendUniversityVerification]);

  // 验证邮箱
  const handleVerifyEmail = useCallback(async () => {
    if (!verificationId || !verificationCode) return;

    await verifyUniversityEmail(verificationId, verificationCode);
  }, [verificationId, verificationCode, verifyUniversityEmail]);

  // 完成注册
  const handleComplete = useCallback(async () => {
    const success = await submitRegistration(profile);
    if (success) {
      onComplete(profile);
    }
  }, [profile, submitRegistration, onComplete]);

  // 渲染基本信息步骤
  const renderBasicInfo = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">{t('profileSetup.demographics')}</h2>
        <p className="text-gray-600">{t('profileSetup.tellUsAbout')}</p>
      </div>

      {/* 错误显示 */}
      <AnimatePresence>
        {error && (
          <ErrorMessage
            message={error}
            onClose={clearError}
            className="mb-4"
          />
        )}
      </AnimatePresence>

      {/* 头像上传 - 3:4 竖向比例 */}
      <div className="flex flex-col items-center">
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
                <span>{t('profileSetup.photo')}*</span>
              </div>
            )}
          </div>
          {isLoading && uploadProgress > 0 && (
            <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
              <div className="text-white text-sm">{uploadProgress}%</div>
            </div>
          )}
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
          <Label className="text-xs text-gray-500 mt-1">{t('profileSetup.photo')}</Label>
        )}
        <input
          id="photo-upload"
          type="file"
          accept="image/*"
          onChange={handlePhotoUpload}
          className="hidden"
        />
      </div>

      {/* 基本字段 */}
      <div className="space-y-4">
        <div>
          <Label>{t('profileSetup.name')} *</Label>
          <Input
            value={profile.name}
            onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
            placeholder={t('profileSetup.name')}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>{t('profileSetup.age')} *</Label>
            <Input
              type="number"
              value={profile.age}
              onChange={(e) => setProfile(prev => ({ ...prev, age: e.target.value }))}
              placeholder="25"
            />
          </div>
          <div>
            <Label>{t('profileSetup.gender')} *</Label>
            <select
              className="w-full p-2 border rounded-md"
              value={profile.gender}
              onChange={(e) => setProfile(prev => ({ ...prev, gender: e.target.value }))}
            >
              <option value="">{t('profileSetup.selectGender')}</option>
              <option value="male">{t('profileSetup.male')}</option>
              <option value="female">{t('profileSetup.female')}</option>
              <option value="other">{t('profileSetup.other')}</option>
            </select>
          </div>
        </div>

        <div>
          <Label>{t('profileSetup.location')} *</Label>
          <Input
            value={profile.location}
            onChange={(e) => setProfile(prev => ({ ...prev, location: e.target.value }))}
            placeholder={t('profileSetup.locationPlaceholder')}
          />
        </div>
      </div>
    </div>
  );

  // 渲染大学验证步骤
  const renderUniversityVerification = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">{t('profileSetup.university')}</h2>
        <p className="text-gray-600">{t('profileSetup.universityConnect')}</p>
      </div>

      {/* 错误显示 */}
      <AnimatePresence>
        {error && (
          <ErrorMessage
            message={error}
            onClose={clearError}
            className="mb-4"
          />
        )}
      </AnimatePresence>

      {/* 大学搜索 */}
      <div>
        <Label>{t('profileSetup.selectUniversity')}</Label>
        <Input
          value={universitySearchQuery}
          onChange={(e) => handleUniversitySearch(e.target.value)}
          placeholder={t('profileSetup.universitySearchPlaceholder')}
        />
        
        {isLoading && universitySearchQuery && (
                     <div className="mt-2">
             <InlineLoading message="Searching..." />
           </div>
        )}

        {searchResults.length > 0 && (
          <div className="mt-2 border rounded-md max-h-40 overflow-y-auto">
            {searchResults.map((uni) => (
              <button
                key={uni.id}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 border-b last:border-b-0"
                onClick={() => {
                  setSelectedUniversity(uni.name);
                  setUniversitySearchQuery(uni.name);
                  setSearchResults([]);
                }}
              >
                {uni.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 大学邮箱 */}
      {selectedUniversity && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div>
            <Label>{t('profileSetup.universityEmail')}</Label>
            <Input
              type="email"
              value={universityEmail}
              onChange={(e) => setUniversityEmail(e.target.value)}
              placeholder={t('profileSetup.universityEmailPlaceholder')}
            />
          </div>

          {!verificationSent && (
            <Button
              onClick={handleSendVerification}
              disabled={!universityEmail || isLoading}
            >
              {isLoading ? <InlineLoading /> : t('profileSetup.sendVerificationCode')}
            </Button>
          )}

          {/* 验证码输入 */}
          {verificationSent && !emailVerified && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3"
            >
              <div>
                <Label>{t('profileSetup.verificationCode')}</Label>
                <Input
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder={t('profileSetup.verificationCodePlaceholder')}
                  maxLength={6}
                />
              </div>
              <Button
                onClick={handleVerifyEmail}
                disabled={verificationCode.length !== 6 || isLoading}
              >
                {isLoading ? <InlineLoading /> : t('profileSetup.verifyCode')}
              </Button>
            </motion.div>
          )}

          {/* 验证成功 */}
          {emailVerified && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200"
            >
              <CheckCircle size={20} className="text-green-600" />
              <span className="text-green-700">{t('profileSetup.emailVerified')}</span>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );

  // 渲染微信认证步骤
  const renderWechatAuth = () => (
    <div className="space-y-6 text-center">
      <div>
        <h2 className="text-xl font-semibold mb-2">{t('profileSetup.authentication')}</h2>
        <p className="text-gray-600">{t('profileSetup.completeWechat')}</p>
      </div>

      {!wechatAuthenticated ? (
        <Button
          onClick={authenticateWechat}
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700"
        >
          {isLoading ? <InlineLoading message={t('common.loading')} /> : t('profileSetup.signInWeChat')}
        </Button>
      ) : (
        <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
          <CheckCircle size={20} className="text-green-600" />
          <span className="text-green-700">{t('profileSetup.wechatVerified')}</span>
        </div>
      )}

      {wechatAuthenticated && (
        <Button
          onClick={handleComplete}
          disabled={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? <InlineLoading message={t('common.loading')} /> : t('profileSetup.complete')}
        </Button>
      )}
    </div>
  );

  const steps = [
    t('profileSetup.demographics'),
    t('profileSetup.university'),
    t('profileSetup.authentication')
  ];
  
  return (
    <div className="w-full h-full flex flex-col relative">
      {/* 加载覆盖层 */}
      <AnimatePresence>
        {(isLoading && uploadProgress > 0) && (
          <LoadingOverlay
            message={t('common.loading')}
            progress={uploadProgress}
          />
        )}
      </AnimatePresence>

      {/* 进度条 */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-500">{steps[currentStep]}</span>
          <span className="text-sm text-gray-500">{currentStep + 1} {t('profileSetup.stepOf')} {steps.length}</span>
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

      {/* 步骤内容 */}
      <div className="flex-1 px-6 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {currentStep === 0 && renderBasicInfo()}
            {currentStep === 1 && renderUniversityVerification()}
            {currentStep === 2 && renderWechatAuth()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* 导航按钮 */}
      <div className="p-6 flex gap-4">
        <Button
          variant="outline"
          onClick={() => currentStep === 0 ? onBack() : setCurrentStep(prev => prev - 1)}
          className="flex-1"
        >
          {currentStep === 0 ? t('profileSetup.back') : t('profileSetup.previous')}
        </Button>
        {currentStep < steps.length - 1 && (
          <Button
            onClick={() => setCurrentStep(prev => prev + 1)}
            disabled={currentStep === 0 && (!profile.name || !profile.age || !profile.gender || !profile.location)}
            className="flex-1"
          >
            {t('profileSetup.next')}
          </Button>
        )}
      </div>
    </div>
  );
} 