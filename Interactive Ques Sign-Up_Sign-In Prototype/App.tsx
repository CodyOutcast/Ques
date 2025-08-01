import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import imgBg from "figma:asset/0a896a0b08b9541d523f8e45d6b853a936c4233c.png";
import { LaunchingPage } from './components/LaunchingPage';
import { LoginScreen } from './components/LoginScreen';
import { SignUpScreen } from './components/SignUpScreen';
import { ForgotPasswordScreen } from './components/ForgotPasswordScreen';
import { OTPScreen } from './components/OTPScreen';
import { ResetPasswordScreen } from './components/ResetPasswordScreen';
import { SuccessScreen } from './components/SuccessScreen';

interface UserData {
  email: string;
  password: string;
  confirmPassword: string;
  rememberMe: boolean;
}

type Screen = 
  | 'launch'
  | 'welcome' 
  | 'login'
  | 'signup'
  | 'forgot-password'
  | 'forgot-otp'
  | 'reset-password'
  | 'success';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('launch');
  const [userData, setUserData] = useState<UserData>({
    email: '',
    password: '',
    confirmPassword: '',
    rememberMe: false
  });
  const [otpCode, setOtpCode] = useState(['', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);

  // Auto-advance from launch screen after 3 seconds
  React.useEffect(() => {
    if (currentScreen === 'launch') {
      const timer = setTimeout(() => {
        setCurrentScreen('welcome');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [currentScreen]);

  // Direct navigation without loading delay for button clicks
  const handleNavigation = (screen: Screen) => {
    setCurrentScreen(screen);
  };

  const handleLogin = async (email: string, password: string, rememberMe: boolean) => {
    setIsLoading(true);
    setUserData(prev => ({ ...prev, email, password, rememberMe }));
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    // For demo purposes, just show success
    console.log('Login successful:', { email, password, rememberMe });
    alert('Login successful! (Demo mode)');
  };

  const handleSignUp = async (email: string, password: string, confirmPassword: string, rememberMe: boolean) => {
    setIsLoading(true);
    setUserData({ email, password, confirmPassword, rememberMe });
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    console.log('Sign up successful:', { email, password, confirmPassword, rememberMe });
    alert('Account created successfully! (Demo mode)');
  };

  const handleForgotPassword = async (email: string) => {
    setIsLoading(true);
    setUserData(prev => ({ ...prev, email }));
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsLoading(false);
    setCurrentScreen('forgot-otp');
  };

  const handleOTPVerification = async (otp: string[]) => {
    setIsLoading(true);
    setOtpCode(otp);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsLoading(false);
    setCurrentScreen('reset-password');
  };

  const handleResetPassword = async (password: string, confirmPassword: string) => {
    setIsLoading(true);
    setUserData(prev => ({ ...prev, password, confirmPassword }));
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsLoading(false);
    setCurrentScreen('success');
  };

  const WelcomeScreen = () => (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.5 }}
      className="absolute bg-black h-[874px] overflow-clip w-[402px]"
    >
      <div
        className="absolute bg-no-repeat bg-size-[156.61%_100%] bg-top h-[874px] left-[-266px] top-0 w-[837px]"
        style={{ backgroundImage: `url('${imgBg}')` }}
      />
      <div className="absolute bg-[rgba(26,26,26,0.57)] h-[874px] left-0 top-0 w-[402px]" />
      
      {/* Fixed positioning for title section to prevent overlap */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="absolute left-[30px] top-[200px] w-[342px]"
      >
        <motion.div
          className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic text-white text-[64px] text-center mb-6"
        >
          Ques
        </motion.div>
        <motion.div
          className="font-['Inria_Sans:Bold',_sans-serif] font-bold text-white text-[32px] text-center leading-[40px]"
        >
          Find your partner now.
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
        className="absolute box-border content-stretch flex flex-col gap-2.5 items-start justify-start left-[29px] p-0 top-[671px]"
      >
        <motion.button
          whileHover={{ scale: 1.02, boxShadow: "0 8px 25px rgba(0, 85, 247, 0.3)" }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleNavigation('signup')}
          className="bg-[#0055f7] box-border content-stretch flex flex-row gap-2.5 h-[49px] items-center justify-center px-[113px] py-[18px] relative rounded-2xl shrink-0 w-[343px] font-['Rubik:Bold',_sans-serif] font-bold leading-[0] text-white text-[16px] text-center hover:bg-[#0045d7] transition-all duration-200"
        >
          Join
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.02, backgroundColor: "rgba(42, 42, 42, 1)" }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleNavigation('login')}
          className="bg-[#1a1a1a] border border-[#8e8e8e] box-border content-stretch flex flex-row gap-2.5 h-[49px] items-center justify-center px-[113px] py-[18px] relative rounded-2xl shrink-0 w-[343px] font-['Rubik:Bold',_sans-serif] font-bold leading-[0] text-white text-[16px] text-center transition-all duration-200"
        >
          Log in
        </motion.button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7, duration: 0.6 }}
        className="absolute font-['Rubik:Medium',_sans-serif] font-medium leading-[0] left-[196px] text-white text-[12px] text-center top-[803px] translate-x-[-50%] w-[290px]"
      >
        <p className="leading-[16px]">
          <span className="font-['Rubik:Medium',_sans-serif] font-medium text-[#bcbcbc]">
            By joining Ques, you agreed to our
          </span>{" "}
          <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold cursor-pointer hover:underline">
            Terms of service
          </span>{" "}
          <span className="font-['Rubik:Medium',_sans-serif] font-medium text-[#bcbcbc]">
            and
          </span>{" "}
          <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold cursor-pointer hover:underline">
            Privacy policy
          </span>
        </p>
      </motion.div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="relative w-[402px] h-[874px] bg-gray-900 rounded-[25px] overflow-hidden shadow-2xl">
        <AnimatePresence mode="wait">
          {currentScreen === 'launch' && (
            <div key="launch" className="absolute inset-0">
              <LaunchingPage />
            </div>
          )}
          {currentScreen === 'welcome' && <WelcomeScreen key="welcome" />}
          {currentScreen === 'login' && (
            <LoginScreen
              key="login"
              onBack={() => setCurrentScreen('welcome')}
              onLogin={handleLogin}
              onForgotPassword={() => setCurrentScreen('forgot-password')}
              onSignUp={() => setCurrentScreen('signup')}
              isLoading={isLoading}
            />
          )}
          {currentScreen === 'signup' && (
            <SignUpScreen
              key="signup"
              onBack={() => setCurrentScreen('welcome')}
              onSignUp={handleSignUp}
              onLogin={() => setCurrentScreen('login')}
              isLoading={isLoading}
            />
          )}
          {currentScreen === 'forgot-password' && (
            <ForgotPasswordScreen
              key="forgot-password"
              onBack={() => setCurrentScreen('login')}
              onNext={handleForgotPassword}
              isLoading={isLoading}
            />
          )}
          {currentScreen === 'forgot-otp' && (
            <OTPScreen
              key="forgot-otp"
              email={userData.email}
              onBack={() => setCurrentScreen('forgot-password')}
              onVerify={handleOTPVerification}
              onResend={() => console.log('Resend OTP')}
              isLoading={isLoading}
            />
          )}
          {currentScreen === 'reset-password' && (
            <ResetPasswordScreen
              key="reset-password"
              onBack={() => setCurrentScreen('forgot-otp')}
              onReset={handleResetPassword}
              isLoading={isLoading}
            />
          )}
          {currentScreen === 'success' && (
            <SuccessScreen
              key="success"
              onBack={() => setCurrentScreen('welcome')}
              onLogin={() => setCurrentScreen('login')}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}