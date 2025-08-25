import React from 'react';
import { BrandBlock } from './BrandBlock';

interface HeaderBarProps {
  rightContent?: React.ReactNode;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ rightContent }) => {
  return (
    <div className="h-[90px] px-[19px] z-0 relative bg-[#FAFAFA] border-b border-[#E8EDF2] flex items-center">
      <div className="flex items-center justify-between w-[354px]">
        <BrandBlock />
        <div className="flex gap-2">
          {rightContent}
        </div>
      </div>
    </div>
  );
}; 