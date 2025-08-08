import React, { useState } from 'react';
import { motion } from 'motion/react';
import svgPaths from "../imports/svg-mqahwcz8hx";

interface LoginScreenProps {
  onBack: () => void;
  onLogin: (email: string, password: string, rememberMe: boolean) => void;
  onForgotPassword: () => void;
  onSignUp: () => void;
  isLoading: boolean;
}

export function LoginScreen({ onBack, onLogin, onForgotPassword, onSignUp, isLoading }: LoginScreenProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const validateForm = () => {
    const newErrors: { email?: string; password?: string } = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onLogin(email, password, rememberMe);
    }
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
        Hi, Welcome Back! 👋
      </motion.div>
      
      <motion.div
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="absolute font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[28px] text-[#999ea1] text-[14px] text-left top-[115px]"
      >
        Hello again, you've been missed!
      </motion.div>

      <motion.form
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        onSubmit={handleSubmit}
        className="absolute left-[27px] top-[170px] w-[359px]"
      >
        <div className="flex flex-col gap-8">
          {/* Email Input */}
          <div className="flex flex-col gap-3">
            <div className="relative w-full">
              <label className="block font-['Manrope:Regular',_sans-serif] font-normal text-[#050607] text-[14px] text-left tracking-[0.28px] mb-3">
                Email
              </label>
              <div className={`rounded-[10px] h-[50px] ${errors.email ? 'border-red-500' : 'border-[#c6c6c6]'} border bg-white`}>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errors.email) setErrors(prev => ({ ...prev, email: undefined }));
                  }}
                  placeholder="Your Email Address"
                  className="w-full h-full bg-transparent px-3 py-2 text-[14px] font-['Manrope:Medium',_sans-serif] text-[#050607] focus:outline-none rounded-[10px]"
                />
              </div>
              {errors.email && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-1 text-red-500 text-[12px]"
                >
                  {errors.email}
                </motion.p>
              )}
            </div>

            {/* Password Input */}
            <div className="relative w-full">
              <label className="block font-['Manrope:Regular',_sans-serif] font-normal text-[#050607] text-[14px] text-left tracking-[0.28px] mb-3">
                Password
              </label>
              <div className={`relative rounded-[10px] h-[50px] ${errors.password ? 'border-red-500' : 'border-[#c6c6c6]'} border bg-white`}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password) setErrors(prev => ({ ...prev, password: undefined }));
                  }}
                  placeholder="Your Password"
                  className="w-full h-full bg-transparent px-3 py-2 pr-12 text-[14px] font-['Manrope:Medium',_sans-serif] text-[#050607] focus:outline-none rounded-[10px]"
                />
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                    {showPassword ? (
                      <g>
                        <path d={svgPaths.p2c282180} stroke="#757575" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6" />
                        <path d={svgPaths.p28db2b80} stroke="#757575" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6" />
                      </g>
                    ) : (
                      <path d={svgPaths.p3f1807e0} stroke="#757575" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6" />
                    )}
                  </svg>
                </motion.button>
              </div>
              {errors.password && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-1 text-red-500 text-[12px]"
                >
                  {errors.password}
                </motion.p>
              )}
            </div>
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between">
            <motion.label
              whileHover={{ scale: 1.02 }}
              className="flex items-center gap-3 cursor-pointer"
            >
              <div className="relative size-5">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="sr-only"
                />
                <div className={`size-5 rounded border-2 transition-colors ${rememberMe ? 'bg-[#0055f7] border-[#0055f7]' : 'bg-white border-[#CDD1E0]'}`}>
                  {rememberMe && (
                    <motion.svg
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-full h-full"
                      viewBox="0 0 20 20"
                    >
                      <path d={svgPaths.p1f7581a8} stroke="white" strokeWidth="1.5" />
                    </motion.svg>
                  )}
                </div>
              </div>
              <span className="font-['Manrope:Regular',_sans-serif] font-normal text-[#000c14] text-[14px] tracking-[0.28px]">
                Remember Me
              </span>
            </motion.label>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="button"
              onClick={onForgotPassword}
              className="font-['Manrope:SemiBold',_sans-serif] font-semibold text-[#007aff] text-[14px] underline tracking-[0.28px]"
            >
              Forgot Password?
            </motion.button>
          </div>

          {/* Login Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLoading}
            className="bg-[#0055f7] h-[45px] rounded-[10px] font-['Rubik:Bold',_sans-serif] font-bold text-white text-[17px] hover:bg-[#0045d7] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Logging in..." : "Log in"}
          </motion.button>
        </div>
      </motion.form>

      {/* Sign Up Link */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="absolute bottom-[40px] left-1/2 transform -translate-x-1/2 font-['Manrope:SemiBold',_sans-serif] font-semibold text-[14px] text-center"
      >
        <span className="text-[#999ea1]">Don't have an account? </span>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onSignUp}
          className="text-[#0055f7] hover:underline"
        >
          Sign Up
        </motion.button>
      </motion.div>
    </motion.div>
  );
}