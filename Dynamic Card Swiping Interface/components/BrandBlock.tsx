import React, { useEffect, useState } from 'react';
import logo from '../auth-imports/no_bg.PNG';

export const BrandBlock: React.FC = () => {
  const [logoAspect, setLogoAspect] = useState<number | null>(null);
  useEffect(() => {
    const img = new Image();
    img.onload = () => setLogoAspect((img.naturalWidth && img.naturalHeight) ? (img.naturalWidth / img.naturalHeight) : 1);
    img.src = logo as any;
  }, []);

  return (
    <div
      className="flex flex-row items-end justify-center gap-0 leading-[0] px-0 py-[13px] relative"
    >
      <div
        aria-label="Ques"
        className="inline-block"
        style={{
          height: '36px',
          width: logoAspect ? `${Math.round(36 * (logoAspect as number))}px` : 'auto',
          backgroundColor: '#0055F7',
          WebkitMaskImage: `url(${logo})`,
          maskImage: `url(${logo})`,
          WebkitMaskRepeat: 'no-repeat',
          maskRepeat: 'no-repeat',
          WebkitMaskPosition: 'left center',
          maskPosition: 'left center',
          WebkitMaskSize: 'contain',
          maskSize: 'contain'
        } as React.CSSProperties}
      />
      <p
        className="block text-nowrap whitespace-pre"
        style={{
          marginLeft: '4px',
          color: '#0055F7',
          fontFeatureSettings: "'liga' off, 'clig' off",
          fontFamily: '"Instrument Sans"',
          fontSize: '42px',
          fontStyle: 'italic',
          fontWeight: '700',
          lineHeight: '36px',
          transform: 'translateY(4px)'
        }}
      >
        Ques
      </p>
    </div>
  );
}; 