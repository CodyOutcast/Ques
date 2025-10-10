import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { useLanguage } from '../contexts/LanguageContext';

import { 
  Bell, 
  MessageCircle,
  CreditCard, 
  FileText,
  LogOut, 
  Trash2,
  Crown,
  Plus,
  Gift,
  Globe,
  Moon,
  Sun
} from 'lucide-react';

interface SettingsScreenProps {
  currentPlan?: 'basic' | 'pro';
  receivesLeft?: number;
  onPlanChange?: (plan: 'basic' | 'pro') => void;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
}

export function SettingsScreen({ 
  currentPlan = 'basic', 
  receivesLeft = 3,
  onPlanChange,
  onTopUpReceives,
  onGiftReceives
}: SettingsScreenProps) {
  const { language, setLanguage, t } = useLanguage();
  
  const [notifications, setNotifications] = useState({
    whisperRequests: true,
  });

  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const [wechatId, setWechatId] = useState(() => {
    // 从localStorage加载保存的微信ID
    return localStorage.getItem('user_wechat_id') || 'your_wechat_id';
  });
  const [whisperCount, setWhisperCount] = useState(3); // Remaining whispers for basic plan
  const [customWhisperMessage, setCustomWhisperMessage] = useState(() => {
    // 从localStorage加载保存的自定义消息
    return localStorage.getItem('custom_whisper_message') || 'Hi! I found your profile through Ques and would love to connect. Looking forward to chatting!';
  });
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('');

  // Calculate maximum purchase amount (cap at 50)
  const maxPurchaseAmount = Math.max(0, 50 - receivesLeft);

  const handleTopUpConfirm = () => {
    const amount = parseInt(topUpAmount);
    if (amount && amount > 0 && amount <= maxPurchaseAmount) {
      onTopUpReceives?.(amount);
      setShowTopUpModal(false);
      setTopUpAmount('');
    }
  };

  const settingSections = [
    {
      title: t('settings.language.title'),
      icon: Globe,
      description: t('settings.language.description'),
      content: (
        <div className="space-y-3">
          {/* English Option */}
          <div 
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              language === 'en' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => {
              setLanguage('en');
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">{t('settings.language.english')}</h4>
                <p className="text-xs text-gray-500">{t('settings.language.englishDesc')}</p>
              </div>
              {language === 'en' && (
                <Badge variant="default" className="text-xs">{t('settings.language.current')}</Badge>
              )}
            </div>
          </div>

          {/* Chinese Option */}
          <div 
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              language === 'zh' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => {
              setLanguage('zh');
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">{t('settings.language.chinese')}</h4>
                <p className="text-xs text-gray-500">{t('settings.language.chineseDesc')}</p>
              </div>
              {language === 'zh' && (
                <Badge variant="default" className="text-xs">{t('settings.language.current')}</Badge>
              )}
            </div>
          </div>
        </div>
      )
    },
    {
      title: t('settings.appearance.title'),
      icon: Moon,
      description: t('settings.appearance.description'),
      content: (
        <div className="space-y-3">
          {/* Light Mode Option */}
          <div 
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              theme === 'light' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => {
              setTheme('light');
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Sun size={20} className="text-yellow-500" />
                <div>
                  <h4 className="font-medium">{t('settings.appearance.lightMode')}</h4>
                  <p className="text-xs text-gray-500">{t('settings.appearance.lightModeDesc')}</p>
                </div>
              </div>
              {theme === 'light' && (
                <Badge variant="default" className="text-xs">{t('settings.appearance.current')}</Badge>
              )}
            </div>
          </div>

          {/* Dark Mode Option */}
          <div 
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              theme === 'dark' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => {
              setTheme('dark');
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Moon size={20} className="text-indigo-500" />
                <div>
                  <h4 className="font-medium">{t('settings.appearance.darkMode')}</h4>
                  <p className="text-xs text-gray-500">{t('settings.appearance.darkModeDesc')}</p>
                </div>
              </div>
              {theme === 'dark' && (
                <Badge variant="default" className="text-xs">{t('settings.appearance.current')}</Badge>
              )}
            </div>
          </div>
        </div>
      )
    },
    {
      title: t('settings.whispers.title'),
      icon: MessageCircle,
      description: t('settings.whispers.description'),
      content: (
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">{t('settings.whispers.wechatTitle')}</h4>
            <p className="text-xs text-gray-500 mb-3">
              {t('settings.whispers.wechatDesc')}
            </p>
            <Input
              placeholder={t('settings.whispers.wechatPlaceholder')}
              value={wechatId}
              onChange={(e) => {
                const newWechatId = e.target.value;
                setWechatId(newWechatId);
                // 立即保存到localStorage
                localStorage.setItem('user_wechat_id', newWechatId);
              }}
            />
          </div>

          {currentPlan === 'pro' && (
            <div>
              <h4 className="text-sm font-medium mb-2">{t('settings.whispers.customMessageTitle')}</h4>
              <p className="text-xs text-gray-500 mb-3">
                {t('settings.whispers.customMessageDesc')}
              </p>
              <Textarea
                placeholder={t('settings.whispers.customMessagePlaceholder')}
                value={customWhisperMessage}
                onChange={(e) => {
                  const newValue = e.target.value;
                  if (newValue.length <= 200) {
                    setCustomWhisperMessage(newValue);
                    // 立即保存到localStorage
                    localStorage.setItem('custom_whisper_message', newValue);
                  }
                }}
                rows={3}
                maxLength={200}
                className="resize-none"
              />
              <p className="text-xs text-gray-400 mt-1">
                {customWhisperMessage.length}/200 {t('settings.whispers.charactersCount')}
              </p>
            </div>
          )}
          
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{t('settings.whispers.usageTitle')}</span>
              <Badge variant={currentPlan === 'pro' ? 'default' : 'secondary'}>
                {currentPlan === 'pro' ? t('settings.whispers.proPlan') : t('settings.whispers.basicPlan')}
              </Badge>
            </div>
            <p className="text-xs text-gray-600">
              {currentPlan === 'pro' 
                ? t('settings.whispers.unlimitedWhispers')
                : `${whisperCount} ${t('settings.whispers.whispersRemaining')}`
              }
            </p>
            {currentPlan === 'basic' && (
              <p className="text-xs text-gray-500 mt-1">
                {t('settings.whispers.upgradeNotice')}
              </p>
            )}
          </div>
        </div>
      )
    },
    {
      title: t('settings.payment.title'),
      icon: CreditCard,
      description: t('settings.payment.description'),
      content: (
        <div className="space-y-4">
          {/* Receives Status */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{t('settings.payment.receivesLeft')}</span>
                  <span className="text-sm font-medium text-blue-600">
                    {currentPlan === 'pro' ? '∞' : receivesLeft}
                  </span>
                  {currentPlan === 'basic' && receivesLeft <= 2 && (
                    <Badge variant="destructive" className="text-xs">{t('settings.payment.low')}</Badge>
                  )}
                </div>

                {currentPlan === 'basic' && (
                  <div className="w-16 bg-gray-200 rounded-full h-1.5">
                    <div 
                      className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min((receivesLeft / 50) * 100, 100)}%` }}
                    />
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                {currentPlan === 'basic' && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => setShowTopUpModal(true)}
                    disabled={receivesLeft >= 50}
                    title={receivesLeft >= 50 ? 'Maximum limit reached' : 'Top up receives'}
                  >
                    <Plus size={12} />
                  </Button>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {/* Basic Plan */}
            <div className={`p-4 rounded-lg border-2 ${currentPlan === 'basic' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{t('settings.payment.basicPlan')}</h4>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{t('settings.payment.free')}</span>
                  {currentPlan === 'basic' && (
                    <Badge variant="default" className="text-xs">{t('settings.payment.currentPlan')}</Badge>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-600 mb-1">• {t('settings.payment.basicFeature1')}</p>
              <p className="text-xs text-gray-600 mb-2">• {t('settings.payment.basicFeature2')}</p>
              <p className="text-xs text-gray-500">{t('settings.payment.basicDesc')}</p>
            </div>

            {/* Pro Plan */}
            <div className={`p-4 rounded-lg border-2 ${currentPlan === 'pro' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">{t('settings.payment.proPlan')}</h4>
                  <Crown size={16} className="text-yellow-500" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">¥10{t('settings.payment.perMonth')}</span>
                  {currentPlan === 'pro' && (
                    <Badge variant="default" className="text-xs">{t('settings.payment.currentPlan')}</Badge>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-600 mb-1">• {t('settings.payment.proFeature1')}</p>
              <p className="text-xs text-gray-600 mb-1">• {t('settings.payment.proFeature2')}</p>
              <p className="text-xs text-gray-600 mb-2">• {t('settings.payment.proFeature3')}</p>
              <p className="text-xs text-gray-500">{t('settings.payment.proDesc')}</p>
            </div>
          </div>

          {currentPlan === 'basic' && (
            <Button 
              className="w-full" 
              onClick={() => onPlanChange?.('pro')}
            >
              {t('settings.payment.upgradeToPro')} - ¥10{t('settings.payment.perMonth')}
            </Button>
          )}

          {currentPlan === 'pro' && (
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => onPlanChange?.('basic')}
            >
              {t('settings.payment.downgradeTo')}
            </Button>
          )}
        </div>
      )
    },
    {
      title: t('settings.notifications.title'),
      icon: Bell,
      description: t('settings.notifications.description'),
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">{t('settings.notifications.whisperRequests')}</span>
              <p className="text-xs text-gray-500">{t('settings.notifications.whisperRequestsDesc')}</p>
            </div>
            <Switch 
              checked={notifications.whisperRequests}
              onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, whisperRequests: checked }))}
            />
          </div>
        </div>
      )
    },
    {
      title: t('settings.terms.title'),
      icon: FileText,
      description: t('settings.terms.description'),
      content: (
        <div className="space-y-3">
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">{t('settings.terms.termsOfService')}</p>
              <p className="text-xs text-gray-500">{t('settings.terms.termsDesc')}</p>
            </div>
          </Button>
          
          <Separator />
          
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">{t('settings.terms.privacyPolicy')}</p>
              <p className="text-xs text-gray-500">{t('settings.terms.privacyDesc')}</p>
            </div>
          </Button>
          
          <Separator />
          
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">{t('settings.terms.dataProtection')}</p>
              <p className="text-xs text-gray-500">{t('settings.terms.dataProtectionDesc')}</p>
            </div>
          </Button>
          
          <Separator />
          
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">{t('settings.terms.communityGuidelines')}</p>
              <p className="text-xs text-gray-500">{t('settings.terms.communityDesc')}</p>
            </div>
          </Button>
        </div>
      )
    }
  ];

  return (
    <div className="h-full overflow-y-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200 sticky top-0 z-10">
        <h1 className="text-xl font-medium">{t('settings.title')}</h1>
        <p className="text-sm text-gray-500">{t('settings.subtitle')}</p>
      </div>

      <div className="p-4 space-y-4">

        {/* Settings Sections */}
        {settingSections.map((section, index) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <section.icon size={20} className="text-gray-600" />
                <div>
                  <h3 className="font-medium">{section.title}</h3>
                  <p className="text-xs text-gray-500">{section.description}</p>
                </div>
              </div>
              {section.content}
            </Card>
          </motion.div>
        ))}

        {/* Account Actions */}
        <Card className="p-4">
          <h3 className="font-medium mb-3">{t('settings.account.title')}</h3>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-center gap-2">
              <LogOut size={16} />
              {t('settings.account.signOut')}
            </Button>
            
            <Button variant="destructive" className="w-full justify-center gap-2">
              <Trash2 size={16} />
              {t('settings.account.deleteAccount')}
            </Button>
          </div>
          
          <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
            <p className="text-xs text-yellow-700">
              <strong>{t('settings.account.dataNotice')}</strong> {t('settings.account.dataNoticeText')}
            </p>
          </div>
        </Card>

        {/* Safe area for bottom navigation */}
        <div className="h-20"></div>
      </div>

      {/* Top-up Modal */}
      <Dialog open={showTopUpModal} onOpenChange={setShowTopUpModal}>
        <DialogContent className="sm:max-w-md mx-auto px-4">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus size={18} className="text-blue-500" />
              {t('settings.topUp.title')}
            </DialogTitle>
            <DialogDescription>
              {t('settings.topUp.description')}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-2 block">{t('settings.topUp.amountLabel')}</label>
              <Input
                type="number"
                placeholder={t('settings.topUp.amountPlaceholder')}
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                min="1"
                max={maxPurchaseAmount}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                {maxPurchaseAmount > 0 
                  ? `Maximum you can purchase: ${maxPurchaseAmount} (cap at 50 total)`
                  : 'You have reached the maximum limit of 50 receives'}
              </p>
            </div>
            
            {topUpAmount && parseInt(topUpAmount) > 0 && (
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="flex justify-between text-sm">
                  <span>{t('settings.topUp.receives')}</span>
                  <span>{topUpAmount}</span>
                </div>
                <div className="flex justify-between text-sm font-medium">
                  <span>{t('settings.topUp.totalCost')}</span>
                  <span>¥{topUpAmount}</span>
                </div>
              </div>
            )}
          </div>
          
          <DialogFooter className="gap-2 sm:gap-0">
            <Button 
              variant="outline" 
              onClick={() => {
                setShowTopUpModal(false);
                setTopUpAmount('');
              }}
            >
              {t('settings.topUp.cancel')}
            </Button>
            <Button 
              onClick={handleTopUpConfirm}
              disabled={!topUpAmount || parseInt(topUpAmount) <= 0 || parseInt(topUpAmount) > maxPurchaseAmount || maxPurchaseAmount <= 0}
              className="bg-blue-500 hover:bg-blue-600"
            >
              {t('settings.topUp.purchase')} ¥{topUpAmount || '0'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}