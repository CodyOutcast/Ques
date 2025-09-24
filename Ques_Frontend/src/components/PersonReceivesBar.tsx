import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Gift } from 'lucide-react';

interface PersonReceivesBarProps {
  personName: string;
  currentPlan: 'basic' | 'pro';
  receivesLeft: number;
  onGiftReceives?: (recipientName: string, amount: number) => void;
}

export function PersonReceivesBar({ 
  personName,
  currentPlan, 
  receivesLeft, 
  onGiftReceives
}: PersonReceivesBarProps) {
  // Calculate receives needed for this person (mock logic - could be dynamic)
  const receivesNeeded = Math.floor(Math.random() * 3) + 1; // 1-3 receives
  const hasEnoughReceives = currentPlan === 'pro' || receivesLeft >= receivesNeeded;

  const handleGiftToPerson = () => {
    onGiftReceives?.(personName, 1);
  };

  return (
    <div className="bg-blue-50/80 backdrop-blur-sm border-b border-blue-200 p-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <span className="text-sm">Receives:</span>
          
          {/* Extended Progress bar */}
          <div className="flex items-center gap-2 flex-1 max-w-32">
            <div className="flex-1 bg-gray-200 rounded-full h-1.5">
              <div 
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  hasEnoughReceives ? 'bg-green-500' : 'bg-orange-500'
                }`}
                style={{ width: `${Math.min((receivesLeft / 5) * 100, 100)}%` }}
              />
            </div>
            
            <span className="text-sm font-medium text-blue-600">
              {currentPlan === 'pro' ? '∞' : receivesLeft}
            </span>
            
            {currentPlan === 'basic' && receivesLeft <= 2 && (
              <Badge variant="destructive" className="text-xs h-4">Low</Badge>
            )}
          </div>
        </div>

        {/* Gift button - icon only */}
        <Button
          variant="outline"
          size="sm"
          className="h-6 w-6 p-0 flex-shrink-0"
          onClick={handleGiftToPerson}
        >
          <Gift size={12} />
        </Button>
      </div>
    </div>
  );
}