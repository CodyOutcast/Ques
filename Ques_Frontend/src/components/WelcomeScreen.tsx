import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Phone, MessageSquare, Send } from 'lucide-react';
import logoIcon from '../assets/icon_inverted.webp';
import { useLanguage } from '../contexts/LanguageContext';

interface WelcomeScreenProps {
  onGetStarted: () => void;
}

export function WelcomeScreen({ onGetStarted }: WelcomeScreenProps) {
  const { t } = useLanguage();
  const [phone, setPhone] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [isCodeSent, setIsCodeSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const handleSendCode = async () => {
    if (!phone.trim() || phone.length < 11) {
      alert(t('welcome.invalidPhone'));
      return;
    }

    setLoading(true);
    try {
      // TODO: Actual API call to send verification code
      console.log('Sending verification code to:', phone);
      setIsCodeSent(true);
      
      // 60 second countdown
      let count = 60;
      setCountdown(count);
      const timer = setInterval(() => {
        count--;
        setCountdown(count);
        if (count <= 0) {
          clearInterval(timer);
          setCountdown(0);
        }
      }, 1000);
      
    } catch (error) {
      console.error('Failed to send verification code:', error);
      alert(t('welcome.sendCodeFailed'));
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    if (!phone.trim() || !verificationCode.trim()) {
      alert(t('welcome.invalidCode'));
      return;
    }

    setLoading(true);
    try {
      // TODO: Actual login/registration API call
      console.log('Login/Register:', phone, verificationCode);
      
      // Simulate successful login, proceed to registration flow
      setTimeout(() => {
        onGetStarted();
      }, 1000);
      
    } catch (error) {
      console.error('Login failed:', error);
      alert(t('welcome.loginFailed'));
    } finally {
      setLoading(false);
    }
  };

  const handleWechatLogin = async () => {
    // TODO: Implement WeChat login logic
    console.log('WeChat login');
    alert(t('welcome.wechatInDev'));
  };

  return (
    <div className="h-full flex flex-col items-center justify-center px-8 bg-white">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex flex-col items-center w-full max-w-sm"
      >
        {/* Logo */}
        <div className="mb-8">
          <img 
            src={logoIcon} 
            alt="Ques Logo" 
            className="w-20 h-20 rounded-full shadow-lg object-cover"
          />
        </div>

        {/* App Name */}
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-3xl font-medium text-gray-900 mb-4 text-center"
        >
          {t('welcome.title')}
        </motion.h1>

        {/* Tagline */}
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="text-lg text-gray-600 text-center mb-8 leading-relaxed"
        >
          {t('welcome.subtitle')}
        </motion.p>

        {/* Login Form */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="w-full space-y-4"
        >
          {/* Phone Input */}
          <div className="relative flex items-center">
            <Phone className="absolute left-3 text-gray-400 z-10" size={18} />
            <Input
              type="tel"
              placeholder={t('welcome.phoneNumber')}
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 11))}
              className="w-full h-12 text-base pl-10"
              style={{ paddingLeft: '2.5rem' }}
              maxLength={11}
            />
          </div>

          {/* Verification Code Input */}
          <div className="flex space-x-2">
            <div className="relative flex items-center flex-1">
              <MessageSquare className="absolute left-3 text-gray-400 z-10" size={18} />
              <Input
                type="text"
                placeholder={t('welcome.verificationCode')}
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                className="w-full h-12 text-base pl-10"
                style={{ paddingLeft: '2.5rem' }}
                maxLength={6}
              />
            </div>
            <Button
              onClick={handleSendCode}
              disabled={loading || countdown > 0 || !phone.trim() || phone.length < 11}
              className="h-12 px-4 whitespace-nowrap bg-gray-100 hover:bg-gray-200 text-gray-700 border"
              variant="outline"
            >
              {loading ? (
                <Send className="animate-spin" size={16} />
              ) : countdown > 0 ? (
                `${countdown}s`
              ) : (
                t('welcome.sendCode')
              )}
            </Button>
          </div>

          {/* Login Button */}
          <Button
            onClick={handleLogin}
            disabled={loading || !phone.trim() || !verificationCode.trim()}
            className="w-full h-12 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all duration-200 transform hover:scale-105 disabled:transform-none"
          >
            {loading ? t('welcome.loggingIn') : t('welcome.login')}
          </Button>

          {/* WeChat Login Button */}
          <Button
            onClick={handleWechatLogin}
            className="w-full h-12 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-all duration-200 transform hover:scale-105 mt-3"
          >
            <div className="flex items-center justify-center space-x-2">
              <MessageSquare size={18} />
              <span>{t('welcome.wechatLogin')}</span>
            </div>
          </Button>

          {/* Login Notice */}
          <p className="text-xs text-gray-500 text-center mt-4 leading-relaxed">
            {t('welcome.termsNotice')}
            <br />
            {t('welcome.autoRegister')}
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}