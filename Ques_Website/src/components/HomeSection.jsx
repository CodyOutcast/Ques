import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const HomeSection = () => {
  const { t } = useTranslation();
  const heroRef = useRef(null);
  const reduceMotion = useReducedMotion();
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
        className="hero-signal"
        style={{ y: reduceMotion ? 0 : orbY }}
        aria-hidden="true"
      >
        <div className="hero-signal__plane" />
        <span className="hero-signal__veil hero-signal__veil--one" />
        <span className="hero-signal__veil hero-signal__veil--two" />
        <span className="hero-signal__veil hero-signal__veil--three" />

        <div className="hero-signal__core">
          <span className="hero-signal__core-glow" />
          <img src="/brand/mark.ico" alt="" width="256" height="256" />
        </div>
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
