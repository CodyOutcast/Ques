import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Gift, X } from 'lucide-react';

interface ReceivesBarProps {
  currentPlan: 'basic' | 'pro';
  receivesLeft: number;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
}

export function ReceivesBar({ 
  currentPlan, 
  receivesLeft, 
  onTopUpReceives, 
  onGiftReceives 
}: ReceivesBarProps) {
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [giftAmount, setGiftAmount] = useState(1);
  const [recipientName, setRecipientName] = useState('');

  const handleGift = () => {
    if (recipientName.trim() && giftAmount > 0) {
      onGiftReceives?.(recipientName, giftAmount);
      setShowGiftModal(false);
      setRecipientName('');
      setGiftAmount(1);
    }
  };

  return (
    <>
      <div className="bg-white/95 backdrop-blur-sm border-b border-gray-200 p-3">
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
                className="text-xs h-6 px-2"
                onClick={() => onTopUpReceives?.(1)}
              >
                +1 (¥1)
              </Button>
            )}

            <Button
              variant="outline"
              size="sm"
              className="text-xs h-6 px-2 gap-1"
              onClick={() => setShowGiftModal(true)}
            >
              <Gift size={12} />
              Gift
            </Button>
          </div>
        </div>
      </div>

      {/* Gift Modal */}
      <AnimatePresence>
        {showGiftModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 z-50"
              onClick={() => setShowGiftModal(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-4 z-50 bg-white rounded-2xl p-6 flex flex-col max-w-sm mx-auto my-auto h-fit"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                    <Gift size={20} className="text-white" />
                  </div>
                  <h3 className="text-lg font-medium">Gift Receives</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowGiftModal(false)}
                  className="w-8 h-8 p-0"
                >
                  <X size={16} />
                </Button>
              </div>
              
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Send receives to help someone connect with more people. Each receive costs ¥1.
                </p>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Recipient Name</label>
                  <Input
                    placeholder="Enter WeChat ID or name"
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Amount to Gift</label>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => setGiftAmount(Math.max(1, giftAmount - 1))}
                    >
                      -
                    </Button>
                    <span className="w-12 text-center text-sm font-medium">{giftAmount}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => setGiftAmount(giftAmount + 1)}
                    >
                      +
                    </Button>
                    <span className="text-xs text-gray-500 ml-2">
                      Total: ¥{giftAmount}
                    </span>
                  </div>
                </div>

                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-xs text-purple-700">
                    💝 Your gift will help {recipientName || 'someone'} receive {giftAmount} more whisper{giftAmount !== 1 ? 's' : ''} this month!
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowGiftModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-purple-500 hover:bg-purple-600"
                  onClick={handleGift}
                  disabled={!recipientName.trim()}
                >
                  Send Gift ¥{giftAmount}
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}