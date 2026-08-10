import { useEffect, useRef, useState } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import { FiAlertCircle, FiPause, FiPlay } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const ProductsDemoSection = () => {
  const { t } = useTranslation();
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [shouldLoad, setShouldLoad] = useState(false);
  const [canAutoLoad, setCanAutoLoad] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isUserPaused, setIsUserPaused] = useState(false);
  const stageRef = useRef(null);
  const videoRef = useRef(null);
  const isInView = useInView(stageRef, { margin: '-20% 0px -20% 0px' });
  const isNearView = useInView(stageRef, { margin: '300px 0px 300px 0px' });
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    const connection = navigator.connection
      ?? navigator.mozConnection
      ?? navigator.webkitConnection;
    const isSlowConnection = ['slow-2g', '2g'].includes(connection?.effectiveType);
    const isTouchFirst = window.matchMedia('(pointer: coarse)').matches;
    setCanAutoLoad(!connection?.saveData && !isSlowConnection && !isTouchFirst);
  }, []);

  useEffect(() => {
    if (!isNearView || !canAutoLoad || shouldLoad) return undefined;

    const startLoading = () => setShouldLoad(true);
    let timeoutId = 0;
    const queueLoading = () => {
      window.clearTimeout(timeoutId);
      timeoutId = window.setTimeout(startLoading, 180);
    };

    queueLoading();
    window.addEventListener('scroll', queueLoading, { passive: true });
    return () => {
      window.clearTimeout(timeoutId);
      window.removeEventListener('scroll', queueLoading);
    };
  }, [canAutoLoad, isNearView, shouldLoad]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !shouldLoad) return;

    if (!isInView || reduceMotion || isUserPaused) {
      video.pause();
      return undefined;
    }

    video.play()?.catch?.(() => {});
    return undefined;
  }, [isInView, isUserPaused, reduceMotion, shouldLoad]);

  const togglePlayback = () => {
    const video = videoRef.current;
    if (!video) return;

    if (!shouldLoad) {
      setIsUserPaused(false);
      setShouldLoad(true);
      return;
    }

    if (video.paused) {
      setIsUserPaused(false);
      setShouldLoad(true);
      video.play()?.catch?.(() => {});
    } else {
      setIsUserPaused(true);
      video.pause();
    }
  };

  return (
    <div className="demo-section section-shell">
      <motion.div
        ref={stageRef}
        className="demo-stage"
        initial={{ opacity: 0, y: 48, scale: 0.98 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, margin: '-10%' }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="demo-stage__halo" aria-hidden="true" />

        {shouldLoad && !isLoaded && !hasError && <div className="demo-stage__loading" />}

        {hasError && (
          <div className="demo-stage__error">
            <FiAlertCircle aria-hidden="true" />
            <p>{t('products_section.demo_error_title')}</p>
            <span>{t('products_section.demo_error_hint')}</span>
          </div>
        )}

        <video
          ref={videoRef}
          loop
          muted
          playsInline
          preload={shouldLoad ? 'metadata' : 'none'}
          width="1280"
          height="720"
          poster="/products/geoseer/screenshots/analysis-1440.webp"
          src={shouldLoad ? '/products/geoseer/demo-720.mp4' : undefined}
          onLoadedData={() => setIsLoaded(true)}
          onError={() => {
            setHasError(true);
            setIsLoaded(true);
          }}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          className={!shouldLoad || (isLoaded && !hasError) ? 'is-loaded' : ''}
        />

        {(!shouldLoad || isLoaded) && !hasError && (
          <button
            type="button"
            className={`demo-stage__playback${!shouldLoad ? ' is-prompt' : ''}`}
            onClick={togglePlayback}
            aria-label={t(isPlaying ? 'products_section.demo_pause' : 'products_section.demo_play')}
          >
            {isPlaying ? <FiPause aria-hidden="true" /> : <FiPlay aria-hidden="true" />}
          </button>
        )}

        <div className="demo-stage__edge demo-stage__edge--left" aria-hidden="true" />
        <div className="demo-stage__edge demo-stage__edge--right" aria-hidden="true" />
      </motion.div>
    </div>
  );
};

export default ProductsDemoSection;
