import { useRef } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import { FiCompass, FiCpu, FiDatabase, FiRefreshCw, FiShield } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
import InferenceField from './InferenceField';

const revealEase = [0.16, 1, 0.3, 1];

const stageDetails = [
  {
    className: 'workflow-stage--observe',
    icon: FiCompass,
    index: '01',
    labelKey: 'workflow_interpret',
    delay: 0.08,
  },
  {
    className: 'workflow-stage--reason',
    icon: FiCpu,
    index: '02',
    labelKey: 'workflow_execute',
    delay: 0.42,
  },
  {
    className: 'workflow-stage--act',
    icon: FiShield,
    index: '03',
    labelKey: 'workflow_audit',
    delay: 0.76,
  },
  {
    className: 'workflow-stage--verify',
    icon: FiRefreshCw,
    index: '04',
    labelKey: 'workflow_learn',
    delay: 1.1,
  },
];

export default function WorkflowField() {
  const fieldRef = useRef(null);
  const reduceMotion = useReducedMotion();
  const isInView = useInView(fieldRef, {
    amount: 0.35,
    margin: '0px 0px -10% 0px',
  });
  const { t } = useTranslation();
  const isActive = Boolean(isInView && !reduceMotion);

  const stageMotion = (delay) => ({
    initial: reduceMotion ? false : { opacity: 0, scale: 0.88, y: 10 },
    animate: isActive || reduceMotion
      ? { opacity: 1, scale: 1, y: 0 }
      : { opacity: 0, scale: 0.88, y: 10 },
    transition: { duration: 0.58, delay: isActive ? delay : 0, ease: revealEase },
  });

  return (
    <div
      ref={fieldRef}
      className={`workflow-field${isActive ? ' is-active' : ''}${reduceMotion ? ' is-reduced-motion' : ''}`}
    >
      <InferenceField />

      <span
        className="workflow-field__focus"
      />

      <div className="workflow-field__hud">
        <div className="workflow-field__identity">
          <span className="workflow-field__identity-mark"><i /><i /></span>
          <span className="workflow-field__identity-copy">
            <small>{t('about_section.workflow_kicker')}</small>
            <strong>{t('about_section.workflow_label')}</strong>
          </span>
        </div>
      </div>

      {['one', 'two', 'three'].map((link, index) => (
        <span key={link} className={`workflow-link workflow-link--${link}`}>
          <motion.span
            initial={false}
            animate={{ scaleX: isActive || reduceMotion ? 1 : 0 }}
            transition={{
              duration: 0.5,
              delay: isActive ? 0.25 + (index * 0.34) : 0,
              ease: revealEase,
            }}
          />
        </span>
      ))}

      {[0, 1].map((packetIndex) => (
        <span
          key={packetIndex}
          className={`workflow-packet workflow-packet--${packetIndex + 1}`}
        />
      ))}

      {stageDetails.map((stage) => {
        const StageIcon = stage.icon;

        return (
          <motion.div
            key={stage.index}
            className={`workflow-stage ${stage.className}`}
            {...stageMotion(stage.delay)}
          >
            <span className="workflow-stage__asset"><StageIcon /></span>
            <span className="workflow-stage__copy">
              <small>{stage.index}</small>
              <strong>{t(`about_section.${stage.labelKey}`)}</strong>
            </span>
            <span className="workflow-stage__port workflow-stage__port--in" />
            <span className="workflow-stage__port workflow-stage__port--out" />
            <span className="workflow-stage__trace"><i /></span>
          </motion.div>
        );
      })}

      <motion.div
        className="workflow-field__result"
        initial={reduceMotion ? false : { opacity: 0, y: 14 }}
        animate={isActive || reduceMotion
          ? { opacity: 1, y: 0 }
          : { opacity: 0, y: 14 }}
        transition={{ duration: 0.58, delay: isActive ? 1.35 : 0, ease: revealEase }}
      >
        <span className="workflow-field__result-asset"><FiDatabase /></span>
        <span className="workflow-field__result-copy">
          <strong>{t('about_section.workflow_feedback_title')}</strong>
          <small>{t('about_section.workflow_feedback')}</small>
        </span>
      </motion.div>
    </div>
  );
}
