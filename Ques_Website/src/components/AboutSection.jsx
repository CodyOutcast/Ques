import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import WorkflowField from './WorkflowField';

const reveal = {
  initial: { opacity: 0, y: 36 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-12%' },
  transition: { duration: 0.85, ease: [0.16, 1, 0.3, 1] },
};

const AboutSection = () => {
  const { t } = useTranslation();

  return (
    <section id="about" data-section="about" className="about-section section-shell">
      <div className="section-grid about-intro">
        <motion.div {...reveal}>
          <h2 className="section-title">{t('about_section.title')}</h2>
        </motion.div>

        <motion.p
          className="section-lead"
          {...reveal}
          transition={{ ...reveal.transition, delay: 0.08 }}
        >
          {t('about_section.description')}
        </motion.p>
      </div>

      <div className="about-composition">
        <motion.div
          className="about-visual"
          initial={{ opacity: 0, scale: 0.92 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: '-14%' }}
          transition={{ duration: 1.05, ease: [0.16, 1, 0.3, 1] }}
          aria-hidden="true"
        >
          <div className="about-visual__frame about-visual__frame--front">
            <WorkflowField />
          </div>
        </motion.div>

        <div className="about-principles">
          <motion.article
            className="principle-block principle-block--autonomy"
            {...reveal}
            transition={{ ...reveal.transition, delay: 0.08 }}
          >
            <h3>{t('about_section.mission_title')}</h3>
            <p>{t('about_section.mission_description')}</p>
          </motion.article>

          <motion.article
            className="principle-block principle-block--learning"
            {...reveal}
            transition={{ ...reveal.transition, delay: 0.16 }}
          >
            <h3>{t('about_section.vision_title')}</h3>
            <p>{t('about_section.vision_description')}</p>
          </motion.article>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
