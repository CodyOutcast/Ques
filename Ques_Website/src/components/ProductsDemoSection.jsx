import { useEffect, useRef, useState } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import { FiAlertCircle, FiPause, FiPlay } from 'react-icons/fi';

const ProductsDemoSection = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [shouldLoad, setShouldLoad] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isUserPaused, setIsUserPaused] = useState(false);
  const stageRef = useRef(null);
  const videoRef = useRef(null);
  const isInView = useInView(stageRef, { margin: '-20% 0px -20% 0px' });
  const isNearView = useInView(stageRef, { margin: '300px 0px 300px 0px' });
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (isNearView) setShouldLoad(true);
  }, [isNearView]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !shouldLoad) return;

    if (isInView && !reduceMotion && !isUserPaused) {
      const playPromise = video.play();
      playPromise?.catch?.(() => {});
    } else {
      video.pause();
    }
  }, [isInView, isUserPaused, reduceMotion, shouldLoad]);

  const togglePlayback = () => {
    const video = videoRef.current;
    if (!video) return;

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
        <div className="demo-stage__chrome" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        {!isLoaded && !hasError && <div className="demo-stage__loading" />}

        {hasError && (
          <div className="demo-stage__error">
            <FiAlertCircle />
            <p>Failed to load demo video</p>
            <span>Please check the video file</span>
          </div>
        )}

        <video
          ref={videoRef}
          loop
          muted
          playsInline
          preload="metadata"
          poster={shouldLoad ? '/products/geoseer/screenshots/analysis.png' : undefined}
          src={shouldLoad ? '/products/geoseer/demo.mp4' : undefined}
          onLoadedMetadata={() => setIsLoaded(true)}
          onError={() => {
            setHasError(true);
            setIsLoaded(true);
          }}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          className={isLoaded && !hasError ? 'is-loaded' : ''}
        />

        {isLoaded && !hasError && (
          <button
            type="button"
            className="demo-stage__playback"
            onClick={togglePlayback}
            aria-label={isPlaying ? 'Pause demo video' : 'Play demo video'}
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
