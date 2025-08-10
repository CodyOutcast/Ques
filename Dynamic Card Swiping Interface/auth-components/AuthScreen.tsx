import React, { useEffect, useState } from 'react';

interface SMSData {
  phoneNumber: string;
  verificationCode: string;
}

export interface AuthPhoneScreenProps {
  smsData: SMSData;
  onChangePhone: (value: string) => void;
  onChangeCode: (value: string) => void;
  errors: { phoneNumber?: string; verificationCode?: string };
  isLoading: boolean;
  codeSent: boolean;
  onSendSMS: () => void;
  onVerifyCode: () => void;
}

export function AuthPhoneScreen(props: AuthPhoneScreenProps) {
  const { smsData, onChangePhone, onChangeCode, errors, isLoading, codeSent, onSendSMS, onVerifyCode } = props;
  const [countdown, setCountdown] = useState<number>(0);

  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setInterval(() => {
      setCountdown((s) => Math.max(0, s - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [countdown]);
  const isPhoneValid = /^\+?[\d\s\-\(\)]{10,}$/.test(smsData.phoneNumber.replace(/\s/g, ''));
  return (
    <div className="absolute bg-black h-[874px] overflow-hidden w-[402px]">
      <div className="absolute inset-0" style={{ background: 'linear-gradient(to top right, #286CFF, #4ade80)' }} />
      {/* Title section - Fixed positioning at top */}
      <div className="absolute left-1/2 top-[80px] transform -translate-x-1/2 text-center w-[350px]">
        <div className="font-['Instrument Sans',_sans-serif] font-bold italic text-white text-[64px] mb-4">
          Ques
        </div>
        <div className="font-['Inria_Sans:Bold',_sans-serif] font-bold text-white text-[28px] leading-[1.1] whitespace-nowrap">
          立即找到你的伙伴。
        </div>
      </div>

      {/* SMS Authentication Form - Single page layout */}
      <div className="absolute left-[27px] top-[320px] w-[348px] space-y-6">
        <div className="flex flex-col gap-6">
          {/* Phone Number Input */}
          <div className="flex flex-col">
            <label className="block font-['Manrope:Regular',_sans-serif] font-semibold text-white text-[14px] mb-3 drop-shadow-md">
              手机号
            </label>
            <input
              type="tel"
              value={smsData.phoneNumber}
              onChange={(e) => onChangePhone(e.target.value)}
              placeholder="请输入手机号"
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

          {/* Verification Code Input with Send/Countdown on the right */}
          <div className="flex flex-col">
            <label className="block font-['Manrope:Regular',_sans-serif] font-semibold text-white text-[14px] mb-3 drop-shadow-md">
              验证码
            </label>
            <div className="flex items-center gap-3 w-full">
              <input
                type="text"
                value={smsData.verificationCode}
                onChange={(e) => onChangeCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="123456"
                maxLength={6}
                disabled={!codeSent}
                className={`h-[50px] px-4 rounded-2xl bg-white/90 backdrop-blur-sm text-black text-[16px] text-center font-['Manrope:SemiBold',_sans-serif] tracking-[0.2em] focus:outline-none focus:ring-2 focus:ring-[#0055f7] transition-all disabled:opacity-50 flex-1 min-w-0 ${
                  errors.verificationCode ? 'ring-2 ring-red-500' : ''
                }`}
              />
              <button
                type="button"
                onClick={() => {
                  if (isLoading || countdown > 0 || !isPhoneValid) return;
                  onSendSMS();
                  setCountdown(60);
                }}
                disabled={isLoading || countdown > 0 || !isPhoneValid}
                className="h-[50px] w-[128px] flex-shrink-0 rounded-2xl font-['Rubik:Bold',_sans-serif] font-bold text-white text-[14px] transition-colors duration-200 disabled:opacity-60 disabled:cursor-not-allowed bg-[#0055f7] hover:bg-[#0045d7] whitespace-nowrap text-center inline-flex items-center justify-center"
              >
                {(isLoading && !codeSent) ? '发送中...' : countdown > 0 ? `${countdown}s` : '发送'}
              </button>
            </div>
            {/* Confirm button below */}
            <button
              type="button"
              onClick={onVerifyCode}
              disabled={isLoading}
              className="mt-3 bg-[#0055f7] h-[50px] w-full rounded-2xl font-['Rubik:Bold',_sans-serif] font-bold text-white text-[16px] hover:bg-[#0045d7] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              确认
            </button>
            {errors.verificationCode && (
              <p className="mt-2 text-red-400 text-[12px]">
                {errors.verificationCode}
              </p>
            )}
          </div>

          {/* Info text */}
          <div className="text-center mt-4">
            <p className="font-['Manrope:Regular',_sans-serif] text-white text-[13px] leading-[0]">
              首次登录将自动为你创建账号
            </p>
          </div>
        </div>
      </div>

      {/* Terms and Privacy */}
      <div className="absolute bottom-[40px] left-1/2 transform -translate-x-1/2 w-[85%] max-w-[300px] text-center">
        <p className="font-['Rubik:Medium',_sans-serif] font-medium text-white text-[12px] leading-[16px]">
          <span className="text-[#bcbcbc]">继续即表示你同意我们的</span>{' '}
          <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold cursor-pointer hover:underline">服务条款</span>{' '}
          <span className="text-[#bcbcbc]">和</span>{' '}
          <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold cursor-pointer hover:underline">隐私政策</span>
        </p>
      </div>
    </div>
  );
} 