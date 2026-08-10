import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'framer-motion';

const columns = 88;
const rows = 64;

const attractors = [
  { x: 0.12, y: 0.24 },
  { x: 0.22, y: 0.76 },
  { x: 0.46, y: 0.44 },
  { x: 0.72, y: 0.22 },
  { x: 0.84, y: 0.72 },
];

const branches = [
  [[0.04, 0.18], [0.18, 0.24], [0.31, 0.36], [0.49, 0.48], [0.69, 0.46], [0.94, 0.62]],
  [[0.02, 0.78], [0.20, 0.72], [0.34, 0.58], [0.49, 0.48], [0.69, 0.46], [0.94, 0.62]],
  [[0.12, 0.48], [0.27, 0.43], [0.37, 0.40], [0.49, 0.48], [0.69, 0.46], [0.94, 0.62]],
];

const contourPalette = [
  'rgba(55, 54, 164, 0.022)',
  'rgba(78, 60, 195, 0.026)',
  'rgba(101, 68, 206, 0.032)',
  'rgba(62, 130, 197, 0.038)',
  'rgba(55, 183, 199, 0.048)',
  'rgba(105, 226, 207, 0.058)',
];

const canvasLayerStyle = {
  position: 'absolute',
  inset: 0,
  display: 'block',
  width: '100%',
  height: '100%',
};

const traceCurve = (context, points) => {
  context.beginPath();
  context.moveTo(points[0][0], points[0][1]);
  for (let index = 0; index < points.length - 1; index += 1) {
    const current = points[index];
    const next = points[index + 1];
    const midpointX = (current[0] + next[0]) / 2;
    context.quadraticCurveTo(current[0], current[1], midpointX, (current[1] + next[1]) / 2);
  }
  const last = points.at(-1);
  context.lineTo(last[0], last[1]);
};

const clearCanvas = (context, canvas) => {
  context.save();
  context.setTransform(1, 0, 0, 1, 0, 0);
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.restore();
};

export default function InferenceField() {
  const containerRef = useRef(null);
  const baseCanvasRef = useRef(null);
  const dynamicCanvasRef = useRef(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    const container = containerRef.current;
    const baseCanvas = baseCanvasRef.current;
    const dynamicCanvas = dynamicCanvasRef.current;
    if (!container || !baseCanvas || !dynamicCanvas) return undefined;

    let disposed = false;
    let initialised = false;
    let initialisePromise;
    let width = 0;
    let height = 0;
    let dpr = 1;
    let isVisible = false;
    let baseContext;
    let dynamicContext;
    let contourData = [];
    let scaledBranches = [];
    let branchGradients = [];

    const drawBase = () => {
      if (!baseContext) return;
      clearCanvas(baseContext, baseCanvas);
      baseContext.setTransform(dpr, 0, 0, dpr, 0, 0);

      const glow = baseContext.createRadialGradient(
        width * 0.48, height * 0.5, 0,
        width * 0.48, height * 0.5, Math.max(width, height) * 0.58,
      );
      glow.addColorStop(0, 'rgba(84, 72, 219, 0.13)');
      glow.addColorStop(0.48, 'rgba(31, 124, 174, 0.06)');
      glow.addColorStop(1, 'rgba(4, 8, 15, 0)');
      baseContext.fillStyle = glow;
      baseContext.fillRect(0, 0, width, height);

      baseContext.save();
      baseContext.scale(width / columns, height / rows);
      baseContext.globalCompositeOperation = 'screen';
      contourData.forEach((contour, index) => {
        baseContext.fillStyle = contourPalette[index];
        baseContext.fill(contour);
      });
      baseContext.restore();

      baseContext.save();
      attractors.forEach((attractor, index) => {
        const radius = 2 + (index % 2) * 0.8;
        baseContext.beginPath();
        baseContext.arc(attractor.x * width, attractor.y * height, radius, 0, Math.PI * 2);
        baseContext.fillStyle = index < 2
          ? 'rgba(158, 105, 218, 0.42)'
          : 'rgba(111, 221, 216, 0.68)';
        baseContext.shadowBlur = 12;
        baseContext.shadowColor = baseContext.fillStyle;
        baseContext.fill();
      });
      baseContext.restore();
    };

    const prepareDynamicLayer = () => {
      if (!dynamicContext) return;
      scaledBranches = branches.map((branch) => (
        branch.map(([x, y]) => [x * width, y * height])
      ));

      dynamicContext.setTransform(1, 0, 0, 1, 0, 0);
      branchGradients = branches.map((_, index) => {
        const gradient = dynamicContext.createLinearGradient(
          0,
          0,
          dynamicCanvas.width,
          dynamicCanvas.height,
        );
        gradient.addColorStop(0, index === 1 ? 'rgba(173, 82, 205, 0.04)' : 'rgba(81, 104, 225, 0.04)');
        gradient.addColorStop(0.5, 'rgba(103, 166, 235, 0.22)');
        gradient.addColorStop(1, 'rgba(105, 233, 213, 0.62)');
        return gradient;
      });
    };

    const drawDynamic = () => {
      if (!dynamicContext) return;
      clearCanvas(dynamicContext, dynamicCanvas);
      dynamicContext.setTransform(dpr, 0, 0, dpr, 0, 0);

      scaledBranches.forEach((points, index) => {
        dynamicContext.save();
        dynamicContext.lineCap = 'round';
        dynamicContext.lineJoin = 'round';
        dynamicContext.strokeStyle = branchGradients[index];
        traceCurve(dynamicContext, points);
        dynamicContext.lineWidth = index === 2 ? 4.2 : 3;
        dynamicContext.globalAlpha = index === 2 ? 0.12 : 0.07;
        dynamicContext.stroke();
        dynamicContext.lineWidth = index === 2 ? 1.45 : 0.9;
        dynamicContext.globalAlpha = index === 2 ? 0.9 : 0.62;
        dynamicContext.stroke();
        dynamicContext.restore();
      });
    };

    const updateAnimationState = () => {
      container.classList.toggle('is-active', isVisible && !reduceMotion);
      container.classList.toggle('is-reduced-motion', Boolean(reduceMotion));
    };

    const resize = () => {
      if (!initialised || disposed) return;
      const bounds = container.getBoundingClientRect();
      const nextWidth = Math.max(1, bounds.width);
      const nextHeight = Math.max(1, bounds.height);
      const isMobile = nextWidth <= 760;
      const nextDpr = Math.min(window.devicePixelRatio || 1, isMobile ? 1 : 1.25);

      if (nextWidth === width && nextHeight === height && nextDpr === dpr) return;
      width = nextWidth;
      height = nextHeight;
      dpr = nextDpr;

      [baseCanvas, dynamicCanvas].forEach((canvas) => {
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
      });

      drawBase();
      prepareDynamicLayer();
      drawDynamic();
    };

    const initialise = () => {
      if (initialised || disposed) return Promise.resolve();
      if (initialisePromise) return initialisePromise;

      initialisePromise = import('../inferenceContours')
        .then(({ default: contourPaths }) => {
          if (disposed) return;
          contourData = contourPaths.map((path) => new Path2D(path));
          baseContext = baseCanvas.getContext('2d');
          dynamicContext = dynamicCanvas.getContext('2d');
          if (!baseContext || !dynamicContext) return;
          initialised = true;
          resize();
        })
        .catch(() => container.classList.add('is-fallback'));

      return initialisePromise;
    };

    const visibilityObserver = new IntersectionObserver(([entry]) => {
      isVisible = entry.isIntersecting;
      updateAnimationState();
      if (isVisible && !initialised) initialise();
    }, { rootMargin: '200px' });

    const resizeObserver = new ResizeObserver(resize);

    resizeObserver.observe(container);
    visibilityObserver.observe(container);
    updateAnimationState();

    return () => {
      disposed = true;
      resizeObserver.disconnect();
      visibilityObserver.disconnect();
    };
  }, [reduceMotion]);

  return (
    <div ref={containerRef} className="inference-field" aria-hidden="true">
      <canvas ref={baseCanvasRef} style={canvasLayerStyle} />
      <canvas
        ref={dynamicCanvasRef}
        className="inference-field__dynamic"
        style={canvasLayerStyle}
      />
    </div>
  );
}
