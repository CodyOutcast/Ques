import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Globe, MapPin, Info, FileText, HeartHandshake, MessageSquare, LogOut, Trash2, Moon } from 'lucide-react';
import { HeaderBar } from './HeaderBar';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { setLanguage as i18nSetLanguage, currentLanguage as i18nCurrentLanguage } from '../translations';
import { Checkbox } from './ui/checkbox';

export function SettingsPage({ onBack, onOpenTerms, onOpenSupport, onFeedbackSubmit, onLogout, onDeactivate }: {
  onBack: () => void;
  onOpenTerms: () => void;
  onOpenSupport: () => void;
  onFeedbackSubmit: (text: string) => void;
  onLogout: () => void;
  onDeactivate: () => void;
}) {
  const [language, setLanguage] = useState<'zh' | 'en'>(() => {
    try {
      const saved = localStorage.getItem('language');
      if (saved === 'zh' || saved === 'en') return saved;
    } catch {}
    return i18nCurrentLanguage || 'zh';
  });
  const [location, setLocation] = useState<string>('深圳, 中国');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackEmail, setFeedbackEmail] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const checkboxBlue = "h-5 w-5 border-2 border-[#0055F7] bg-white data-[state=checked]:bg-white data-[state=checked]:border-[#0055F7] data-[state=checked]:text-[#0055F7]";

  return (
    <motion.div className="absolute left-0 right-0 mx-auto w-[393px] h-[852px] bg-white">
      {/* 顶部栏 */}
      <div className="h-[90px] px-[19px] z-0 relative bg-[#FAFAFA] border-b border-[#E8EDF2] flex items-center">
        <div className="flex items-center justify-between w-[354px]">
          <button onClick={onBack} className="p-2"><ArrowLeft className="w-6 h-6 text-[#0055F7]" /></button>
          <h1 className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Settings' : '设置'}</h1>
          <div className="w-10" />
        </div>
      </div>

      {/* 内容 */}
      <div className="flex-1 overflow-y-auto px-4" style={{ height: 'calc(100% - 90px)' }}>
        <div className="py-4 space-y-6">
          {/* 语言 */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Globe className="w-5 h-5 text-gray-700" />
              <h2 className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Language' : '语言'}</h2>
            </div>
            <div className="flex gap-2">
              <button className={`px-3 py-1 rounded-full border ${language==='zh' ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-gray-300 text-gray-700'}`} onClick={() => { setLanguage('zh'); try { i18nSetLanguage('zh'); localStorage.setItem('language','zh'); } catch {}; }}>
                中文
              </button>
              <button className={`px-3 py-1 rounded-full border ${language==='en' ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-gray-300 text-gray-700'}`} onClick={() => { setLanguage('en'); try { i18nSetLanguage('en'); localStorage.setItem('language','en'); } catch {}; }}>
                English
              </button>
            </div>
          </div>

          {/* 当前位置 */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-5 h-5 text-gray-700" />
              <h2 className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Current Location' : '当前位置'}</h2>
            </div>
            <div className="flex gap-2">
              <input value={location} onChange={(e) => setLocation(e.target.value)} className="flex-1 px-3 py-2 border border-gray-300 rounded-lg" placeholder={i18nCurrentLanguage === 'en' ? 'Enter your location' : '输入你的位置'} />
              <button className="px-3 py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-200" onClick={() => {
                navigator.geolocation?.getCurrentPosition?.(() => {}, () => {});
              }}>{i18nCurrentLanguage === 'en' ? 'Locate' : '定位'}</button>
            </div>
          </div>

          {/* 关于我们 */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-5 h-5 text-gray-700" />
              <h2 className="font-semibold">{i18nCurrentLanguage === 'en' ? 'About Us' : '关于我们'}</h2>
            </div>
            <div className="space-y-2">
              <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100" onClick={onOpenTerms}>
                <span className="flex items-center gap-2"><FileText className="w-4 h-4" /> {i18nCurrentLanguage === 'en' ? 'Terms of Service' : '服务条款'}</span>
                <span className="text-gray-400">›</span>
              </button>
              <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100" onClick={onOpenSupport}>
                <span className="flex items-center gap-2"><HeartHandshake className="w-4 h-4" /> {i18nCurrentLanguage === 'en' ? 'Support the Developers' : '支持开发者'}</span>
                <span className="text-gray-400">›</span>
              </button>
              <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100" onClick={() => setShowFeedback(true)}>
                <span className="flex items-center gap-2"><MessageSquare className="w-4 h-4" /> {i18nCurrentLanguage === 'en' ? 'Feedback' : '反馈'}</span>
                <span className="text-gray-400">›</span>
              </button>
            </div>
          </div>

          {/* Appearance */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Moon className="w-5 h-5 text-gray-700" />
              <h2 className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Appearance' : '外观'}</h2>
            </div>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100">
                <span className="text-sm text-gray-800">{i18nCurrentLanguage === 'en' ? 'Dark mode' : '深色模式'}</span>
                <Checkbox checked={darkMode} onCheckedChange={(v) => setDarkMode(!!v)} className={checkboxBlue} />
              </label>
            </div>
          </div>

          {/* 账户相关设置 */}
          <div className="border rounded-lg p-4">
            <h2 className="font-semibold mb-3">{i18nCurrentLanguage === 'en' ? 'Account' : '账户相关'}</h2>
            <div className="space-y-2">
              <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100" onClick={onLogout}>
                <span className="flex items-center gap-2 text-blue-700"><LogOut className="w-4 h-4" /> {i18nCurrentLanguage === 'en' ? 'Log out' : '退出登录'}</span>
                <span className="text-gray-400">›</span>
              </button>
              <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-red-50 border border-red-100" onClick={onDeactivate}>
                <span className="flex items-center gap-2 text-red-700"><Trash2 className="w-4 h-4" /> {i18nCurrentLanguage === 'en' ? 'Deactivate account' : '注销账号'}</span>
                <span className="text-gray-400">›</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 反馈弹窗 */}
      <AnimatePresence>
        {showFeedback && (
          <motion.div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setShowFeedback(false)}>
            <motion.div className="bg-white rounded-2xl p-6 w-[340px]" onClick={(e) => e.stopPropagation()} initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }}>
              <h3 className="text-lg font-bold mb-3">{i18nCurrentLanguage === 'en' ? 'Feedback' : '反馈'}</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{i18nCurrentLanguage === 'en' ? 'Your email' : '您的邮箱'}</label>
                  <input type="email" value={feedbackEmail} onChange={(e) => setFeedbackEmail(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="name@example.com" />
                  <p className="text-xs text-gray-500 mt-1">{i18nCurrentLanguage === 'en' ? 'We will send a copy of your feedback to your email' : '我们会将反馈发送到您的邮箱'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{i18nCurrentLanguage === 'en' ? 'Feedback' : '反馈内容'}</label>
                  <textarea value={feedbackText} onChange={(e) => setFeedbackText(e.target.value)} rows={5} className="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder={i18nCurrentLanguage === 'en' ? 'Please write your suggestions or issues...' : '请写下你的意见或建议...'} />
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <Button className="flex-1" variant="secondary" onClick={() => setShowFeedback(false)}>{i18nCurrentLanguage === 'en' ? 'Cancel' : '取消'}</Button>
                <Button className="flex-1" onClick={() => { onFeedbackSubmit(`${feedbackEmail || ''} | ${feedbackText.trim()}`); setShowFeedback(false); setFeedbackText(''); setFeedbackEmail(''); }}>{i18nCurrentLanguage === 'en' ? 'Submit' : '提交'}</Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
} 