import React, { useEffect, useState } from 'react';
import logoUrl from '../auth-imports/no_bg.PNG?url';

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
  // Add touched states for blur-only validation feedback
  const [phoneTouched, setPhoneTouched] = useState<boolean>(false);
  const [codeTouched, setCodeTouched] = useState<boolean>(false);

  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setInterval(() => {
      setCountdown((s) => Math.max(0, s - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [countdown]);
  const isPhoneValid = /^\+?[\d\s\-\(\)]{10,}$/.test(smsData.phoneNumber.replace(/\s/g, ''));
  // Derive local errors only after blur (touched)
  const phoneErrorToShow = errors.phoneNumber ?? (phoneTouched && !isPhoneValid ? '请输入有效的手机号' : undefined);
  const codeErrorToShow = errors.verificationCode ?? (codeTouched && codeSent && smsData.verificationCode.length !== 6 ? '请输入6位验证码' : undefined);
  return (
    <div className="absolute h-[822px] overflow-hidden w-[393px]">
      {/* Title section - Fixed positioning at top */}
      <div className="absolute left-1/2 top-[80px] transform -translate-x-1/2 text-center w-[350px]">
        <div className="mb-4 flex items-center justify-center gap-3">
          <img src={logoUrl} alt="Ques" style={{ height: 55, width: 'auto' }} />
          <div className="font-['Instrument Sans',_sans-serif] font-bold italic text-white text-[64px] leading-[1]">
          Ques
          </div>
        </div>
        <div className="font-['Inria_Sans:Bold',_sans-serif] font-bold text-white text-[28px] leading-[1.1] whitespace-nowrap">
          即刻找到你的合作伙伴
        </div>
      </div>

      {/* 原型版本提示 - 新增 */}
      <div className="absolute left-1/2 top-[200px] transform -translate-x-1/2 w-[340px] text-center">
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
          <div className="font-['Manrope:SemiBold',_sans-serif] font-semibold text-white text-[16px] mb-2">
            原型版本，请直接点击"确认"登录
          </div>
          <div className="font-['Manrope:Regular',_sans-serif] text-white/80 text-[14px]">
            Prototype, please click "confirm" button to log in directly
          </div>
        </div>
      </div>

      {/* SMS Authentication Form - Single page layout */}
      <div className="absolute left-[27px] top-[350px] w-[348px] space-y-6">
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
              onBlur={() => setPhoneTouched(true)}
              placeholder="请输入手机号"
              className={`h-[50px] px-4 rounded-2xl backdrop-blur-sm text-black text-[16px] font-['Manrope:Medium',_sans-serif] focus:outline-none focus:ring-2 transition-all ${
                phoneErrorToShow ? 'ring-2 ring-rose-500 bg-rose-50 placeholder:text-rose-400' : 'bg-white/90 focus:ring-[#0055f7]'
              }`}
            />
            {phoneErrorToShow && (
              <p className="mt-2 text-rose-600 text-[12px]">
                {phoneErrorToShow}
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
                onBlur={() => setCodeTouched(true)}
                placeholder="123456"
                maxLength={6}
                disabled={!codeSent}
                className={`h-[50px] px-4 rounded-2xl backdrop-blur-sm text-black text-[16px] text-center font-['Manrope:SemiBold',_sans-serif] tracking-[0.2em] focus:outline-none focus:ring-2 transition-all disabled:opacity-50 flex-1 min-w-0 ${
                  codeErrorToShow ? 'ring-2 ring-rose-500 bg-rose-50 placeholder:text-rose-400' : 'bg-white/90 focus:ring-[#0055f7]'
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
            {/* Confirm button below - 修改为始终可点击 */}
            <button
              type="button"
              onClick={onVerifyCode}
              disabled={isLoading}
              className="mt-3 bg-[#0055f7] h-[50px] w-full rounded-2xl font-['Rubik:Bold',_sans-serif] font-bold text-white text-[16px] hover:bg-[#0045d7] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              确认
            </button>
            {codeErrorToShow && (
              <p className="mt-2 text-rose-600 text-[12px]">
                {codeErrorToShow}
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