import { useRef } from 'react';
import { motion, useInView, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const signalNodes = [
  ['12%', '28%', 0.2],
  ['25%', '12%', 1.1],
  ['41%', '22%', 0.7],
  ['66%', '10%', 1.5],
  ['86%', '31%', 0.4],
  ['74%', '47%', 1.9],
  ['91%', '68%', 1.2],
  ['67%', '82%', 0.6],
  ['45%', '73%', 1.6],
  ['20%', '86%', 0.9],
  ['9%', '61%', 1.4],
  ['31%', '49%', 0.1],
];

const HomeSection = () => {
  const { t } = useTranslation();
  const heroRef = useRef(null);
  const reduceMotion = useReducedMotion();
  const isHeroInView = useInView(heroRef, { amount: 0.08 });
  const shouldAnimate = isHeroInView && !reduceMotion;
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  const orbY = useTransform(scrollYProgress, [0, 1], [0, 74]);
  const copyY = useTransform(scrollYProgress, [0, 0.78], [0, 30]);
  const copyOpacity = useTransform(scrollYProgress, [0, 0.72], [1, 0.42]);

  return (
    <section ref={heroRef} id="home" data-section="home" className="hero-section">
      <motion.div
        className={`hero-signal${shouldAnimate ? ' is-active' : ''}`}
        style={{ y: reduceMotion ? 0 : orbY }}
        aria-hidden="true"
      >
        <div className="hero-signal__plane" />
        <div className="hero-signal__ring hero-signal__ring--one" />
        <div className="hero-signal__ring hero-signal__ring--two" />
        <div className="hero-signal__ring hero-signal__ring--three" />
        <div className="hero-signal__scan" />
        <div className="hero-signal__axis hero-signal__axis--horizontal" />
        <div className="hero-signal__axis hero-signal__axis--vertical" />

        {signalNodes.map(([left, top, delay], index) => (
          <motion.span
            key={`${left}-${top}`}
            className={`hero-signal__node hero-signal__node--${(index % 3) + 1}`}
            style={{ left, top }}
            animate={shouldAnimate
              ? { opacity: [0.3, 1, 0.3], scale: [0.8, 1.25, 0.8] }
              : { opacity: 0.48, scale: 1 }}
            transition={shouldAnimate
              ? { duration: 3.2, delay, repeat: Infinity, ease: 'easeInOut' }
              : { duration: 0.2 }}
          />
        ))}

        <motion.div
          className="hero-signal__core"
          animate={shouldAnimate
            ? { rotate: [0, 3, -2, 0], y: [0, -8, 0] }
            : { rotate: 0, y: 0 }}
          transition={shouldAnimate
            ? { duration: 8, repeat: Infinity, ease: 'easeInOut' }
            : { duration: 0.2 }}
        >
          <span className="hero-signal__core-glow" />
          <img src="/brand/mark.ico" alt="" width="256" height="256" />
        </motion.div>
      </motion.div>

      <motion.div
        className="hero-copy"
        style={{ y: reduceMotion ? 0 : copyY, opacity: reduceMotion ? 1 : copyOpacity }}
        initial={false}
      >
        <p className="hero-copy__company">{t('home_section.company_name')}</p>
        <h1>{t('home_section.tagline')}</h1>
      </motion.div>

      <motion.div
        className="hero-scroll-indicator"
        aria-hidden="true"
        initial={false}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <span />
      </motion.div>
    </section>
  );
};

export default HomeSection;
