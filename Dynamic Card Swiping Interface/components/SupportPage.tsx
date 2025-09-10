import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Heart } from 'lucide-react';

export function SupportPage({ onBack }: { onBack: () => void }) {
  return (
    <motion.div className="absolute left-0 right-0 mx-auto w-[393px] h-[852px] bg-white">
      <div className="h-[90px] px-[19px] z-0 relative bg-[#FAFAFA] border-b border-[#E8EDF2] flex items-center">
        <div className="flex items-center justify-between w-[354px]">
          <button onClick={onBack} className="p-2"><ArrowLeft className="w-6 h-6 text-[#0055F7]" /></button>
          <h1 className="text-lg font-bold">支持创作者</h1>
          <div className="w-10" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6" style={{ height: 'calc(100% - 90px - 96px)' }}>
        <div className="py-8 text-center space-y-4">
          <Heart className="w-12 h-12 text-pink-500 mx-auto" />
          <h2 className="text-xl font-bold">a little support</h2>
          <p className="text-gray-600">你的支持将帮助我们继续打磨更好的产品体验。</p>
          <div className="grid grid-cols-3 gap-3 mt-6">
            {["¥6", "¥18", "¥66"].map((amt) => (
              <button key={amt} className="py-3 rounded-lg border hover:bg-pink-50 text-pink-600 border-pink-200 font-semibold">{amt}</button>
            ))}
          </div>
          <button className="mt-6 w-full py-3 rounded-lg bg-pink-500 text-white font-bold hover:bg-pink-600">自定义金额</button>
        </div>
      </div>
    </motion.div>
  );
} 