import React from 'react';
import { motion } from 'framer-motion';

// Positioning and sizing constants (px) — adjust here if you want to fine-tune
const TITLE_LEFT_PX = 20;      // Ques 左边距（不再使用水平定位，可作为偏移备用）
const TITLE_TOP_PX = 320;       // Ques 顶部位置
const TITLE_SIZE_PX = 128;      // Ques 字号
const LINES_LEFT_PX = 60;       // 三行左边距
const LINES_TOP_PX = 440;       // 三行顶部位置（保证与 Ques 有足够间距）
const LINES_GAP_PX = (typeof document !== 'undefined' && document.documentElement.lang?.startsWith('zh')) ? 4 : -10; // 仅中文时增大行距

export function LaunchingPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-[#ffffff] relative size-full"
      data-name="luanching page"
    >
      {/* Center wrapper to avoid framer-motion overriding transform */}
      <div className="absolute" style={{ left: '50%', transform: 'translateX(-50%)', top: TITLE_TOP_PX }}>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8, type: "spring" }}
          style={{ fontVariationSettings: "'wdth' 100" }}
        >
          <p
            className="adjustLetterSpacing block text-left font-['Instrument Sans',_sans-serif] font-bold italic text-[#0055f7] leading-[95px] tracking-[-2px]"
            style={{
              fontFamily: 'Instrument Sans, system-ui, sans-serif',
              fontStyle: 'italic',
              fontWeight: 700,
              color: '#0055f7',
              fontSize: `${TITLE_SIZE_PX}px`,
              lineHeight: '95px',
              letterSpacing: '-2px',
              textAlign: 'left'
            }}
          >
            Ques
          </p>
        </motion.div>
      </div>
      
      <div
        className="absolute"
        style={{ left: LINES_LEFT_PX, top: LINES_TOP_PX }}
      >
        <motion.p
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6, ease: "easeOut" }}
          className="block font-['Rubik',_sans-serif] font-bold text-[#0055f7] text-[24px]"
        >
          匹配
        </motion.p>
        <motion.p
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.0, duration: 0.6, ease: "easeOut" }}
          className="block font-['Rubik',_sans-serif] font-bold text-[#0055f7] text-[24px]"
          style={{ marginTop: LINES_GAP_PX }}
        >
          连接
        </motion.p>
        <motion.p
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.6, ease: "easeOut" }}
          className="block font-['Rubik',_sans-serif] font-bold text-[#0055f7] text-[24px]"
          style={{ marginTop: LINES_GAP_PX }}
        >
          协作
        </motion.p>
      </div>
    </motion.div>
  );
}