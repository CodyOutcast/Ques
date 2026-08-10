import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';

export default function LowerNarrative({ children }) {
  const narrativeRef = useRef(null);
  const reduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: narrativeRef,
    offset: ['start end', 'end start'],
  });

  const atmosphereOpacity = useTransform(
    scrollYProgress,
    [0, 0.07, 0.9, 1],
    [0, 0.98, 0.96, 0],
  );
  const violetY = useTransform(scrollYProgress, [0, 1], [-120, 250]);
  const violetX = useTransform(scrollYProgress, [0, 1], [-60, 90]);
  const violetOpacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 0.9, 0.58]);
  const cyanY = useTransform(scrollYProgress, [0, 1], [180, -160]);
  const cyanX = useTransform(scrollYProgress, [0, 0.62, 1], [120, -35, -90]);
  const cyanScale = useTransform(scrollYProgress, [0, 0.58, 1], [0.78, 1.08, 0.92]);
  const resolvedOpacity = useTransform(scrollYProgress, [0, 0.48, 0.84, 1], [0, 0.36, 0.96, 0.7]);
  const resolvedScale = useTransform(scrollYProgress, [0, 0.78, 1], [0.58, 1.08, 0.88]);
  const ribbonRotate = useTransform(scrollYProgress, [0, 1], [-8, 13]);
  const ribbonY = useTransform(scrollYProgress, [0, 1], [80, -90]);

  return (
    <div ref={narrativeRef} className="lower-narrative">
      <motion.div
        className="lower-atmosphere"
        style={{ opacity: atmosphereOpacity }}
        aria-hidden="true"
      >
        <motion.div
          className="lower-atmosphere__field lower-atmosphere__field--violet"
          style={{
            opacity: violetOpacity,
            x: reduceMotion ? 0 : violetX,
            y: reduceMotion ? 0 : violetY,
          }}
        />
        <motion.div
          className="lower-atmosphere__field lower-atmosphere__field--cyan"
          style={{
            x: reduceMotion ? 0 : cyanX,
            y: reduceMotion ? 0 : cyanY,
            scale: reduceMotion ? 1 : cyanScale,
          }}
        />
        <motion.div
          className="lower-atmosphere__ribbon"
          style={{
            rotate: reduceMotion ? 0 : ribbonRotate,
            y: reduceMotion ? 0 : ribbonY,
          }}
        />
        <motion.div
          className="lower-atmosphere__resolution"
          style={{
            opacity: resolvedOpacity,
            scale: reduceMotion ? 1 : resolvedScale,
          }}
        />
      </motion.div>

      {children}
    </div>
  );
}
