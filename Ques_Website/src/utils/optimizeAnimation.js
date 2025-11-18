// 性能优化配置
export const optimizeAnimation = {
  // GPU 加速
  gpuAcceleration: {
    transform: 'translateZ(0)',
    willChange: 'transform, opacity',
    backfaceVisibility: 'hidden'
  },
  
  // 优化的弹簧动画配置
  optimizedSpring: {
    type: 'spring',
    stiffness: 100,
    damping: 15,
    mass: 0.5
  },
  
  // 简化的过渡动画
  simplifiedTransition: {
    duration: 0.3,
    ease: 'easeInOut'
  }
};
