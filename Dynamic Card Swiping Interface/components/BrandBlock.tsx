import React, { useEffect, useState, useRef } from 'react';
import logo from '../auth-imports/no_bg.PNG';

// 全局缓存图片宽高比，避免重复加载
let globalLogoAspect: number | null = null;
let isLoadingGlobal = false;
const loadingCallbacks: ((aspect: number) => void)[] = [];

const loadLogoAspect = (): Promise<number> => {
  return new Promise((resolve) => {
    // 如果已经有缓存的宽高比，直接返回
    if (globalLogoAspect !== null) {
      resolve(globalLogoAspect);
      return;
    }
    
    // 如果正在加载中，添加到回调队列
    if (isLoadingGlobal) {
      loadingCallbacks.push(resolve);
      return;
    }
    
    // 开始加载图片
    isLoadingGlobal = true;
    const img = new Image();
    img.onload = () => {
      const aspect = (img.naturalWidth && img.naturalHeight) ? (img.naturalWidth / img.naturalHeight) : 1;
      globalLogoAspect = aspect;
      isLoadingGlobal = false;
      
      // 调用所有等待的回调
      resolve(aspect);
      loadingCallbacks.forEach(callback => callback(aspect));
      loadingCallbacks.length = 0; // 清空回调数组
    };
    img.onerror = () => {
      globalLogoAspect = 1; // 默认宽高比
      isLoadingGlobal = false;
      resolve(1);
      loadingCallbacks.forEach(callback => callback(1));
      loadingCallbacks.length = 0;
    };
    img.src = logo as any;
  });
};

export const BrandBlock: React.FC = React.memo(() => {
  const [logoAspect, setLogoAspect] = useState<number | null>(globalLogoAspect);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    
    loadLogoAspect().then((aspect) => {
      if (mountedRef.current) {
        setLogoAspect(aspect);
      }
    });

    return () => {
      mountedRef.current = false;
    };
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
          width: logoAspect ? `${Math.round(36 * logoAspect)}px` : 'auto',
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
}); 