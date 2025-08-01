import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import svgPaths from "../imports/svg-mqahwcz8hx";

interface OTPScreenProps {
  email: string;
  onBack: () => void;
  onVerify: (otp: string[]) => void;
  onResend: () => void;
  isLoading: boolean;
}

export function OTPScreen({ email, onBack, onVerify, onResend, isLoading }: OTPScreenProps) {
  const [otp, setOtp] = useState(['', '', '', '', '']);
  const [error, setError] = useState('');
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    // Auto-focus first input on mount
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, []);

  const handleOtpChange = (index: number, value: string) => {
    if (value.length <= 1 && /^\d*$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);
      setError('');

      // Auto-focus next input
      if (value && index < 4) {
        inputRefs.current[index + 1]?.focus();
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const otpString = otp.join('');
    if (otpString.length !== 5) {
      setError('Please enter all 5 digits');
      return;
    }
    
    onVerify(otp);
  };

  const handleResend = () => {
    setOtp(['', '', '', '', '']);
    setError('');
    onResend();
    // Auto-focus first input after resend
    setTimeout(() => {
      inputRefs.current[0]?.focus();
    }, 100);
  };

  const BackButton = () => (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onBack}
      className="absolute left-[17px] top-[30px] p-2 rounded-full hover:bg-gray-100 transition-colors"
    >
      <svg className="w-6 h-6" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <path d={svgPaths.pa00bfc0} stroke="#B3B3B3" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
      </svg>
    </motion.button>
  );

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.5 }}
      className="absolute bg-white h-[874px] overflow-clip w-[402px]"
    >
      <BackButton />
      
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="absolute font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[28px] text-black text-[25px] text-left top-[80px]"
      >
        Forgot Password?
      </motion.div>
      
      <motion.div
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="absolute font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[normal] left-[28px] right-[28px] text-[#999ea1] text-[14px] text-left top-[115px]"
      >
        <p className="mb-1">
          <span>We sent a verification code to </span>
          <span className="text-[#050607]">{email} </span>
        </p>
        <p>
          Please check your email and enter the code below
        </p>
      </motion.div>

      <motion.form
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        onSubmit={handleSubmit}
        className="absolute left-[25px] top-[200px] w-[359px]"
      >
        <div className="flex flex-col gap-8 items-center">
          {/* OTP Input */}
          <div className="flex gap-6 justify-center w-full">
            {otp.map((digit, index) => (
              <motion.div
                key={index}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1 * index, duration: 0.3 }}
                className="relative size-14"
              >
                <input
                  ref={(ref) => (inputRefs.current[index] = ref)}
                  type="text"
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  maxLength={1}
                  className={`size-14 text-center text-[24px] font-['Manrope:SemiBold',_sans-serif] font-semibold border-2 rounded-xl transition-all duration-200 focus:outline-none ${
                    digit
                      ? 'border-[#0055f7] bg-white text-black shadow-[0px_4px_4px_0px_inset_rgba(0,0,0,0.25)]'
                      : 'border-[#e1e1e1] bg-white focus:border-[#0055f7]'
                  } ${error ? 'border-red-500' : ''}`}
                />
              </motion.div>
            ))}
          </div>
          
          {error && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-500 text-[14px] text-center"
            >
              {error}
            </motion.p>
          )}

          {/* Next Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLoading || otp.join('').length !== 5}
            className="bg-[#0055f7] h-[45px] w-full rounded-[10px] font-['Rubik:Bold',_sans-serif] font-bold text-white text-[17px] hover:bg-[#0045d7] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Verifying..." : "Next"}
          </motion.button>
        </div>
      </motion.form>

      {/* Resend Link */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="absolute left-1/2 transform -translate-x-1/2 top-[400px] flex gap-2 items-center justify-center font-['Manrope:SemiBold',_sans-serif] font-semibold text-[14px]"
      >
        <span className="text-[#999ea1]">Haven't got the email yet? </span>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleResend}
          className="text-[#0055f7] underline"
        >
          Resend Email
        </motion.button>
      </motion.div>
    </motion.div>
  );
}