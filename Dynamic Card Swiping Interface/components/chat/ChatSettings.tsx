import React, { useState } from 'react';
import { ArrowLeft, Bell, Moon } from 'lucide-react';
import { Checkbox } from '../ui/checkbox';
import { currentLanguage as i18nCurrentLanguage } from '../../translations';

interface ChatSettingsProps {
  onNavigateBack?: () => void;
}

export default function ChatSettings({ onNavigateBack }: ChatSettingsProps) {
  const [alwaysNotify, setAlwaysNotify] = useState(true);
  const [voiceNotify, setVoiceNotify] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const goBack = () => {
    if (onNavigateBack) onNavigateBack();
  };

  const checkboxBlue = "h-5 w-5 border-2 border-[#0055F7] bg-white data-[state=checked]:bg-white data-[state=checked]:border-[#0055F7] data-[state=checked]:text-[#0055F7]";

  return (
    <div className="absolute left-0 right-0 mx-auto w-[393px] h-[852px] bg-white">
      {/* 顶部栏（对齐 SettingsPage 风格） */}
      <div className="h-[90px] px-[19px] z-0 relative bg-[#FAFAFA] border-b border-[#E8EDF2] flex items-center">
        <div className="flex items-center justify-between w-[354px]">
          <button onClick={goBack} className="p-2"><ArrowLeft className="w-6 h-6 text-[#0055F7]" /></button>
          <h1 className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Chat Settings' : '聊天设置'}</h1>
          <div className="w-10" />
        </div>
      </div>

      {/* 内容区 */}
      <div className="flex-1 overflow-y-auto px-4" style={{ height: 'calc(100% - 90px)' }}>
        <div className="py-4 space-y-6">
          {/* 通知设置 */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Bell className="w-5 h-5 text-gray-700" />
              <h2 className="font-semibold">{i18nCurrentLanguage === 'en' ? 'Notifications' : '通知'}</h2>
            </div>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100">
                <span className="text-sm text-gray-800">{i18nCurrentLanguage === 'en' ? 'Always receive notifications' : '始终接收通知'}</span>
                <Checkbox checked={alwaysNotify} onCheckedChange={(v) => setAlwaysNotify(!!v)} className={checkboxBlue} />
              </label>
              <label className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 border border-gray-100">
                <span className="text-sm text-gray-800">{i18nCurrentLanguage === 'en' ? 'Enable voice notifications' : '启用语音通知'}</span>
                <Checkbox checked={voiceNotify} onCheckedChange={(v) => setVoiceNotify(!!v)} className={checkboxBlue} />
              </label>
            </div>
          </div>

          {/* 外观设置已迁移到个人设置页 */}
        </div>
      </div>
    </div>
  );
} 