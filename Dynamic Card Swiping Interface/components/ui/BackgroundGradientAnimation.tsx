import React, { useEffect } from 'react';
import './background-gradient-animation.css';

interface BackgroundGradientAnimationProps {
  gradientBackgroundStart?: string;
  gradientBackgroundEnd?: string;
  firstColor?: string;   // r, g, b string without rgb()
  secondColor?: string;  // r, g, b
  thirdColor?: string;   // r, g, b
  size?: string;         // e.g., '80%'
  blendingValue?: string; // CSS mix-blend-mode value
  className?: string;
  containerClassName?: string;
  children?: React.ReactNode;
}

export function BackgroundGradientAnimation({
  gradientBackgroundStart = 'rgb(30, 144, 255)',     // blue
  gradientBackgroundEnd = 'rgb(0, 200, 150)',        // green
  firstColor = '30, 144, 255',
  secondColor = '0, 200, 150',
  thirdColor = '50, 220, 190',
  size = '80%',
  blendingValue = 'soft-light',
  className,
  containerClassName,
  children,
}: BackgroundGradientAnimationProps) {
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--gradient-background-start', gradientBackgroundStart);
    root.style.setProperty('--gradient-background-end', gradientBackgroundEnd);
    root.style.setProperty('--first-color', firstColor);
    root.style.setProperty('--second-color', secondColor);
    root.style.setProperty('--third-color', thirdColor);
    root.style.setProperty('--size', size);
    root.style.setProperty('--blending-value', blendingValue);
  }, [
    gradientBackgroundStart,
    gradientBackgroundEnd,
    firstColor,
    secondColor,
    thirdColor,
    size,
    blendingValue,
  ]);

  return (
    <div
      className={[
        'bgga-container',
        containerClassName || '',
      ].join(' ').trim()}
    >
      {/* animated gradient blobs layer (behind) */}
      <div className="bgga-gradients">
        <div className="bgga-blob bgga-anim-first" />
        <div className="bgga-blob bgga-anim-second" />
        <div className="bgga-blob bgga-anim-third" />
      </div>
      {/* foreground content */}
      <div className={['bgga-content', className || ''].join(' ').trim()}>
        {children}
      </div>
    </div>
  );
}

export default BackgroundGradientAnimation; 