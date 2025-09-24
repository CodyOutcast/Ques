import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';

import { 
  Bell, 
  MessageCircle,
  CreditCard, 
  FileText,
  LogOut, 
  Trash2,
  Crown,
  Plus,
  Gift
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
  const [notifications, setNotifications] = useState({
    whisperRequests: true,
  });

  const [wechatId, setWechatId] = useState('your_wechat_id');
  const [whisperCount, setWhisperCount] = useState(3); // Remaining whispers for basic plan
  const [customWhisperMessage, setCustomWhisperMessage] = useState('Hi! I found your profile through Ques and would love to connect. Looking forward to chatting!');
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('');

  const handleTopUpConfirm = () => {
    const amount = parseInt(topUpAmount);
    if (amount && amount > 0 && amount <= 100) {
      onTopUpReceives?.(amount);
      setShowTopUpModal(false);
      setTopUpAmount('');
    }
  };

  const settingSections = [
    {
      title: 'Whispers',
      icon: MessageCircle,
      description: 'Manage your whisper settings and WeChat contact',
      content: (
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">WeChat ID for Whispers</h4>
            <p className="text-xs text-gray-500 mb-3">
              This WeChat ID will be shared when someone whispers back to you
            </p>
            <Input
              placeholder="Enter your WeChat ID"
              value={wechatId}
              onChange={(e) => setWechatId(e.target.value)}
            />
          </div>

          {currentPlan === 'pro' && (
            <div>
              <h4 className="text-sm font-medium mb-2">Custom Whisper Message</h4>
              <p className="text-xs text-gray-500 mb-3">
                Personalize your whisper message that gets sent with your contact info
              </p>
              <Textarea
                placeholder="Enter your custom whisper message..."
                value={customWhisperMessage}
                onChange={(e) => {
                  const newValue = e.target.value;
                  if (newValue.length <= 200) {
                    setCustomWhisperMessage(newValue);
                  }
                }}
                rows={3}
                maxLength={200}
                className="resize-none"
              />
              <p className="text-xs text-gray-400 mt-1">
                {customWhisperMessage.length}/200 characters
              </p>
            </div>
          )}
          
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">Whisper Usage</span>
              <Badge variant={currentPlan === 'pro' ? 'default' : 'secondary'}>
                {currentPlan === 'pro' ? 'Pro Plan' : 'Basic Plan'}
              </Badge>
            </div>
            <p className="text-xs text-gray-600">
              {currentPlan === 'pro' 
                ? 'Unlimited whispers available' 
                : `${whisperCount} whispers remaining this month`
              }
            </p>
            {currentPlan === 'basic' && (
              <p className="text-xs text-gray-500 mt-1">
                Upgrade to Pro for custom whisper messages
              </p>
            )}
          </div>
        </div>
      )
    },
    {
      title: 'Payment Plan',
      icon: CreditCard,
      description: 'Manage your subscription and billing',
      content: (
        <div className="space-y-4">
          {/* Receives Status */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Receives Left:</span>
                  <span className="text-sm font-medium text-blue-600">
                    {currentPlan === 'pro' ? '∞' : receivesLeft}
                  </span>
                  {currentPlan === 'basic' && receivesLeft <= 2 && (
                    <Badge variant="destructive" className="text-xs">Low</Badge>
                  )}
                </div>

                {currentPlan === 'basic' && (
                  <div className="w-16 bg-gray-200 rounded-full h-1.5">
                    <div 
                      className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${(receivesLeft / 5) * 100}%` }}
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
                <h4 className="font-medium">Basic Plan</h4>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Free</span>
                  {currentPlan === 'basic' && (
                    <Badge variant="default" className="text-xs">Current</Badge>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-600 mb-1">• 5 whispers per month</p>
              <p className="text-xs text-gray-600 mb-2">• 5 receives per month</p>
              <p className="text-xs text-gray-500">Perfect for casual networking</p>
            </div>

            {/* Pro Plan */}
            <div className={`p-4 rounded-lg border-2 ${currentPlan === 'pro' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">Pro Plan</h4>
                  <Crown size={16} className="text-yellow-500" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">¥10/month</span>
                  {currentPlan === 'pro' && (
                    <Badge variant="default" className="text-xs">Current</Badge>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-600 mb-1">• Unlimited whispers</p>
              <p className="text-xs text-gray-600 mb-1">• Unlimited receives</p>
              <p className="text-xs text-gray-600 mb-2">• Custom whisper messages</p>
              <p className="text-xs text-gray-500">For active networkers and professionals</p>
            </div>
          </div>

          {currentPlan === 'basic' && (
            <Button 
              className="w-full" 
              onClick={() => onPlanChange?.('pro')}
            >
              Upgrade to Pro - ¥10/month
            </Button>
          )}

          {currentPlan === 'pro' && (
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => onPlanChange?.('basic')}
            >
              Downgrade to Basic Plan
            </Button>
          )}
        </div>
      )
    },
    {
      title: 'Notifications',
      icon: Bell,
      description: 'Control what notifications you receive',
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Whisper requests</span>
              <p className="text-xs text-gray-500">New whisper back requests from others</p>
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
      title: 'Terms & Privacy',
      icon: FileText,
      description: 'Legal documents and privacy information',
      content: (
        <div className="space-y-3">
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">Terms of Service</p>
              <p className="text-xs text-gray-500">Read our terms and conditions</p>
            </div>
          </Button>
          
          <Separator />
          
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">Privacy Policy</p>
              <p className="text-xs text-gray-500">How we handle your data</p>
            </div>
          </Button>
          
          <Separator />
          
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">Data Protection</p>
              <p className="text-xs text-gray-500">GDPR and data rights information</p>
            </div>
          </Button>
          
          <Separator />
          
          <Button variant="ghost" className="w-full justify-start p-0 h-auto">
            <div className="text-left">
              <p className="text-sm font-medium">Community Guidelines</p>
              <p className="text-xs text-gray-500">Rules for safe networking</p>
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
        <h1 className="text-xl font-medium">Settings</h1>
        <p className="text-sm text-gray-500">Manage your preferences and privacy</p>
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
          <h3 className="font-medium mb-3">Account</h3>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-center gap-2">
              <LogOut size={16} />
              Sign Out
            </Button>
            
            <Button variant="destructive" className="w-full justify-center gap-2">
              <Trash2 size={16} />
              Delete Account
            </Button>
          </div>
          
          <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
            <p className="text-xs text-yellow-700">
              <strong>Data Notice:</strong> Ques is designed for professional networking. 
              Please do not share personal identifying information or sensitive data.
            </p>
          </div>
        </Card>

        {/* Safe area for bottom navigation */}
        <div className="h-20"></div>
      </div>

      {/* Top-up Modal */}
      <Dialog open={showTopUpModal} onOpenChange={setShowTopUpModal}>
        <DialogContent className="sm:max-w-md mx-4">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus size={18} className="text-blue-500" />
              Top Up Receives
            </DialogTitle>
            <DialogDescription>
              Enter the number of receives you want to purchase (¥1 per receive)
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Amount</label>
              <Input
                type="number"
                placeholder="Enter amount (1-100)"
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                min="1"
                max="100"
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum 100 receives per transaction
              </p>
            </div>
            
            {topUpAmount && parseInt(topUpAmount) > 0 && (
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="flex justify-between text-sm">
                  <span>Receives:</span>
                  <span>{topUpAmount}</span>
                </div>
                <div className="flex justify-between text-sm font-medium">
                  <span>Total Cost:</span>
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
              Cancel
            </Button>
            <Button 
              onClick={handleTopUpConfirm}
              disabled={!topUpAmount || parseInt(topUpAmount) <= 0 || parseInt(topUpAmount) > 100}
              className="bg-blue-500 hover:bg-blue-600"
            >
              Purchase ¥{topUpAmount || '0'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}