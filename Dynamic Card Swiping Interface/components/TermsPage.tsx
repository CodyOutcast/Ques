import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, FileText } from 'lucide-react';

export function TermsPage({ onBack }: { onBack: () => void }) {
  return (
    <motion.div className="absolute left-0 right-0 mx-auto w-[393px] h-[852px] bg-white">
      <div className="h-[90px] px-[19px] z-0 relative bg-[#FAFAFA] border-b border-[#E8EDF2] flex items-center">
        <div className="flex items-center justify-between w-[354px]">
          <button onClick={onBack} className="p-2"><ArrowLeft className="w-6 h-6 text-[#0055F7]" /></button>
          <h1 className="text-lg font-bold">服务条款</h1>
          <div className="w-10" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6" style={{ height: 'calc(100% - 90px - 96px)' }}>
        <div className="py-6 space-y-4 text-sm text-gray-700">
          <h2 className="text-lg font-semibold flex items-center gap-2"><FileText className="w-5 h-5" /> 使用须知</h2>
          <p>欢迎使用本产品。使用本产品即表示您同意遵守以下条款…（这里可替换为正式条款内容）。</p>
          <p>1. 用户应遵守当地法律法规，不得利用本平台从事违法违规行为。</p>
          <p>2. 本平台会尽力保障服务稳定，但不对因不可抗力导致的服务中断承担责任。</p>
          <p>3. 如涉及付费服务，请以应用内显示为准。</p>
          <p>更多细节请联系管理员。</p>
        </div>
      </div>
    </motion.div>
  );
} 