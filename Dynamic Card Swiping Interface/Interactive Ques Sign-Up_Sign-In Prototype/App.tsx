import React, { useState } from 'react';
import imgBg from "figma:asset/0a896a0b08b9541d523f8e45d6b853a936c4233c.png";
import { LaunchingPage } from './components/LaunchingPage';

interface SMSData {
  phoneNumber: string;
  verificationCode: string;
}

type Screen = 'launch' | 'welcome';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('launch');
  const [smsData, setSmsData] = useState<SMSData>({
    phoneNumber: '',
    verificationCode: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ phoneNumber?: string; verificationCode?: string }>({});
  const [codeSent, setCodeSent] = useState(false);

  // Auto-advance from launch screen after 3 seconds
  React.useEffect(() => {
    if (currentScreen === 'launch') {
      const timer = setTimeout(() => {
        setCurrentScreen('welcome');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [currentScreen]);

  const validatePhoneNumber = (phone: string) => {
    return /^\+?[\d\s\-\(\)]{10,}$/.test(phone.replace(/\s/g, ''));
  };

  const handleSendSMS = async () => {
    if (!smsData.phoneNumber) {
      setErrors({ phoneNumber: 'Phone number is required' });
      return;
    }

    if (!validatePhoneNumber(smsData.phoneNumber)) {
      setErrors({ phoneNumber: 'Please enter a valid phone number' });
      return;
    }

    setIsLoading(true);
    setErrors({});
    
    // Simulate SMS sending API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    setCodeSent(true);
  };

  const handleVerifyCode = async () => {
    if (!smsData.verificationCode) {
      setErrors({ verificationCode: 'Verification code is required' });
      return;
    }

    if (smsData.verificationCode.length !== 6) {
      setErrors({ verificationCode: 'Please enter a 6-digit code' });
      return;
    }

    setIsLoading(true);
    setErrors({});
    
    // Simulate verification API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    alert('SMS Verification Successful! Welcome to Ques!');
    console.log('SMS Authentication successful:', smsData);
  };

  const WelcomeScreen = () => {
    return (
      <div className="absolute bg-black h-[874px] overflow-hidden w-[402px]">
        <div
          className="absolute bg-no-repeat bg-cover bg-center inset-0 scale-150"
          style={{ backgroundImage: `url('${imgBg}')` }}
        />
        <div className="absolute bg-[rgba(26,26,26,0.57)] inset-0" />
        
        {/* Title section - Fixed positioning at top */}
        <div className="absolute left-1/2 top-[80px] transform -translate-x-1/2 text-center w-[350px]">
          <div className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic text-white text-[64px] mb-4">
            Ques
          </div>
          <div className="font-['Inria_Sans:Bold',_sans-serif] font-bold text-white text-[28px] leading-[1.1] whitespace-nowrap">
            Find your partner now.
          </div>
        </div>

        {/* SMS Authentication Form - Single page layout */}
        <div className="absolute left-[27px] top-[320px] w-[348px]">
          <div className="flex flex-col gap-6">
            {/* Phone Number Input */}
            <div className="flex flex-col">
              <label className="block font-['Manrope:Regular',_sans-serif] font-normal text-white text-[14px] mb-3">
                Phone Number
              </label>
              <input
                type="tel"
                value={smsData.phoneNumber}
                onChange={(e) => {
                  setSmsData(prev => ({ ...prev, phoneNumber: e.target.value }));
                  if (errors.phoneNumber) setErrors(prev => ({ ...prev, phoneNumber: undefined }));
                }}
                placeholder="+1 (555) 123-4567"
                className={`h-[50px] px-4 rounded-2xl bg-white/90 backdrop-blur-sm text-black text-[16px] font-['Manrope:Medium',_sans-serif] focus:outline-none focus:ring-2 focus:ring-[#0055f7] transition-all ${
                  errors.phoneNumber ? 'ring-2 ring-red-500' : ''
                }`}
              />
              {errors.phoneNumber && (
                <p className="mt-2 text-red-400 text-[12px]">
                  {errors.phoneNumber}
                </p>
              )}
            </div>

            {/* Verification Code Input with Send Button */}
            <div className="flex flex-col">
              <label className="block font-['Manrope:Regular',_sans-serif] font-normal text-white text-[14px] mb-3">
                Verification Code
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={smsData.verificationCode}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                    setSmsData(prev => ({ ...prev, verificationCode: value }));
                    if (errors.verificationCode) setErrors(prev => ({ ...prev, verificationCode: undefined }));
                  }}
                  placeholder="123456"
                  maxLength={6}
                  disabled={!codeSent}
                  className={`flex-1 h-[50px] px-4 rounded-2xl bg-white/90 backdrop-blur-sm text-black text-[16px] text-center font-['Manrope:SemiBold',_sans-serif] tracking-[0.2em] focus:outline-none focus:ring-2 focus:ring-[#0055f7] transition-all disabled:opacity-50 ${
                    errors.verificationCode ? 'ring-2 ring-red-500' : ''
                  }`}
                />
                <button
                  onClick={codeSent ? handleVerifyCode : handleSendSMS}
                  disabled={isLoading}
                  className="bg-[#0055f7] h-[50px] px-6 rounded-2xl font-['Rubik:Bold',_sans-serif] font-bold text-white text-[16px] hover:bg-[#0045d7] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                >
                  {isLoading ? (codeSent ? "Verifying..." : "Sending...") : (codeSent ? "Verify" : "Send")}
                </button>
              </div>
              {errors.verificationCode && (
                <p className="mt-2 text-red-400 text-[12px]">
                  {errors.verificationCode}
                </p>
              )}
            </div>

            {/* Info text */}
            <div className="text-center mt-4">
              <p className="font-['Manrope:Regular',_sans-serif] text-[#bcbcbc] text-[14px] leading-[1.4]">
                We will automatically create an account for first sign up
              </p>
            </div>

            {/* Resend option - only show after code is sent */}
            {codeSent && (
              <div className="text-center mt-4">
                <p className="font-['Manrope:Regular',_sans-serif] text-[#bcbcbc] text-[12px] mb-2">
                  Didn't receive the code?
                </p>
                <button
                  onClick={handleSendSMS}
                  disabled={isLoading}
                  className="text-[#0055f7] text-[14px] font-['Manrope:SemiBold',_sans-serif] hover:underline disabled:opacity-50"
                >
                  Resend Code
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Terms and Privacy */}
        <div className="absolute bottom-[40px] left-1/2 transform -translate-x-1/2 w-[85%] max-w-[300px] text-center">
          <p className="font-['Rubik:Medium',_sans-serif] font-medium text-white text-[12px] leading-[16px]">
            <span className="text-[#bcbcbc]">
              By continuing, you agree to our
            </span>{" "}
            <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold cursor-pointer hover:underline">
              Terms of service
            </span>{" "}
            <span className="text-[#bcbcbc]">
              and
            </span>{" "}
            <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold cursor-pointer hover:underline">
              Privacy policy
            </span>
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="relative w-[402px] h-[874px] bg-gray-900 rounded-[25px] overflow-hidden shadow-2xl">
        {currentScreen === 'launch' && (
          <div className="absolute inset-0">
            <LaunchingPage />
          </div>
        )}
        {currentScreen === 'welcome' && <WelcomeScreen />}
      </div>
    </div>
  );
}