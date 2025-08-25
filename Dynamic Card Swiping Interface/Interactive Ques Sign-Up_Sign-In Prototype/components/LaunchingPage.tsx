import React from 'react';
import { motion } from 'framer-motion';
import logoUrl from '../../auth-imports/no_bg.PNG?url';

export function LaunchingPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.25 }}
      className="relative size-full bg-gradient-to-br from-[#1e90ff] via-[#1ec8b1] to-[#00c896]"
      data-name="launching-page"
    >
      {/* Centered logo */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.img
          src={logoUrl}
          alt="Ques"
          initial={{ scale: 0.94, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
          style={{ width: 100, height: 'auto' }}
        />
      </div>
    </motion.div>
  );
}