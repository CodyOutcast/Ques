import React from 'react';
import { motion } from 'motion/react';

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
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8, type: "spring" }}
        className="absolute flex flex-col font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold h-[75px] italic justify-center leading-[0] left-[200.5px] text-[#0055f7] text-[128px] text-center top-[333.5px] tracking-[-2px] translate-x-[-50%] translate-y-[-50%] w-[349px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[95px]">Ques</p>
      </motion.div>
      
      <div className="absolute bottom-[42.91%] font-['Rubik:Bold',_sans-serif] font-bold leading-[normal] left-[14.93%] right-[32.59%] text-[#0055f7] text-[24px] text-left top-[47.48%]">
        <motion.p
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6, ease: "easeOut" }}
          className="block mb-0"
        >
          Match.
        </motion.p>
        <motion.p
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.0, duration: 0.6, ease: "easeOut" }}
          className="block mb-0"
        >
          Connect.
        </motion.p>
        <motion.p
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.6, ease: "easeOut" }}
          className="block"
        >
          Collab.
        </motion.p>
      </div>
    </motion.div>
  );
}