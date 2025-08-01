import React, { useState } from 'react';
import { motion } from 'motion/react';
import svgPaths from "../imports/svg-mqahwcz8hx";

interface ForgotPasswordScreenProps {
  onBack: () => void;
  onNext: (email: string) => void;
  isLoading: boolean;
}

export function ForgotPasswordScreen({ onBack, onNext, isLoading }: ForgotPasswordScreenProps) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const validateEmail = (email: string) => {
    return /\S+@\S+\.\S+/.test(email);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setError('Email is required');
      return;
    }
    
    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    setError('');
    onNext(email);
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
        className="absolute font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[28px] text-[#999ea1] text-[14px] text-left top-[115px] right-[28px]"
      >
        Please enter your email to reset the password
      </motion.div>

      <motion.form
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        onSubmit={handleSubmit}
        className="absolute left-[27px] top-[170px] w-[359px]"
      >
        <div className="flex flex-col gap-6">
          {/* Email Input */}
          <div className="relative w-full">
            <label className="block font-['Manrope:Regular',_sans-serif] font-normal text-[#050607] text-[14px] text-left tracking-[0.28px] mb-3">
              Email
            </label>
            <div className={`rounded-[10px] h-[50px] ${error ? 'border-red-500' : 'border-[#c6c6c6]'} border bg-white`}>
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
                }}
                placeholder="Your Email Address"
                className="w-full h-full bg-transparent px-3 py-2 text-[14px] font-['Manrope:Medium',_sans-serif] text-[#050607] focus:outline-none rounded-[10px]"
              />
            </div>
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-red-500 text-[12px]"
              >
                {error}
              </motion.p>
            )}
          </div>

          {/* Next Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLoading}
            className="bg-[#0055f7] h-[45px] rounded-[10px] font-['Rubik:Bold',_sans-serif] font-bold text-white text-[17px] hover:bg-[#0045d7] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Sending..." : "Next"}
          </motion.button>
        </div>
      </motion.form>

      {/* Login Link */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="absolute bottom-[40px] left-1/2 transform -translate-x-1/2 font-['Manrope:SemiBold',_sans-serif] font-semibold text-[14px] text-center"
      >
        <span className="text-[#999ea1]">Already have an account? </span>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onBack}
          className="text-[#0055f7] hover:underline"
        >
          Log in
        </motion.button>
      </motion.div>
    </motion.div>
  );
}