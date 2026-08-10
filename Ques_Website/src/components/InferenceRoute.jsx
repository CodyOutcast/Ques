import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'framer-motion';

const routeStages = [
  { selector: '#home', position: 0.38, x: 0.59 },
  { selector: '#about', position: 0.23, x: 0.34 },
  { selector: '.about-composition', position: 0.58, x: 0.43 },
  { selector: '#products', position: 0.34, x: 0.67 },
  { selector: '#team', position: 0.42, x: 0.38 },
  { selector: '#contact', position: 0.52, x: 0.61 },
];

const pointOnCurve = (start, controlA, controlB, end, amount) => {
  const inverse = 1 - amount;
  const inverseSquared = inverse * inverse;
  const amountSquared = amount * amount;

  return {
    x: inverseSquared * inverse * start.x
      + 3 * inverseSquared * amount * controlA.x
      + 3 * inverse * amountSquared * controlB.x
      + amountSquared * amount * end.x,
    y: inverseSquared * inverse * start.y
      + 3 * inverseSquared * amount * controlA.y
      + 3 * inverse * amountSquared * controlB.y
      + amountSquared * amount * end.y,
  };
};

const sampleRoute = (points) => {
  if (points.length < 2) return { samples: [], totalLength: 0 };

  const samples = [{ ...points[0], distance: 0 }];
  let previous = points[0];
  let totalLength = 0;

  for (let index = 0; index < points.length - 1; index += 1) {
    const p0 = points[index - 1] ?? points[index];
    const p1 = points[index];
    const p2 = points[index + 1];
    const p3 = points[index + 2] ?? p2;
    const tension = 0.18;
    const controlA = {
      x: p1.x + (p2.x - p0.x) * tension,
      y: p1.y + (p2.y - p0.y) * tension,
    };
    const controlB = {
      x: p2.x - (p3.x - p1.x) * tension,
      y: p2.y - (p3.y - p1.y) * tension,
    };

    for (let step = 1; step <= 28; step += 1) {
      const point = pointOnCurve(p1, controlA, controlB, p2, step / 28);
      totalLength += Math.hypot(point.x - previous.x, point.y - previous.y);
      samples.push({ ...point, distance: totalLength });
      previous = point;
    }
  }

  return { samples, totalLength };
};

const traceVisibleRoute = (context, samples, visibleDistance, scrollTop, endpoint) => {
  if (samples.length < 2) return false;

  context.beginPath();
  context.moveTo(samples[0].x, samples[0].y - scrollTop);

  for (let index = 1; index < samples.length; index += 1) {
    const point = samples[index];
    if (point.distance <= visibleDistance) {
      endpoint.x = point.x;
      endpoint.y = point.y - scrollTop;
      context.lineTo(endpoint.x, endpoint.y);
      continue;
    }

    const previous = samples[index - 1];
    const segmentLength = point.distance - previous.distance;
    const amount = segmentLength > 0
      ? Math.max(0, (visibleDistance - previous.distance) / segmentLength)
      : 0;
    endpoint.x = previous.x + (point.x - previous.x) * amount;
    endpoint.y = previous.y + (point.y - previous.y) * amount - scrollTop;
    context.lineTo(endpoint.x, endpoint.y);
    break;
  }

  return true;
};

const drawRouteDot = (context, point, radius, color, alpha) => {
  context.save();
  context.fillStyle = color;
  context.globalAlpha = alpha * 0.2;
  context.beginPath();
  context.arc(point.x, point.y, radius * 3.4, 0, Math.PI * 2);
  context.fill();

  context.globalAlpha = alpha;
  context.beginPath();
  context.arc(point.x, point.y, radius, 0, Math.PI * 2);
  context.fill();
  context.restore();
};

export default function InferenceRoute() {
  const canvasRef = useRef(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const context = canvas.getContext('2d');
    if (!context) return undefined;

    let frameId = 0;
    let width = 0;
    let height = 0;
    let dpr = 1;
    let disposed = false;
    let anchors = [];
    let routeSamples = [];
    let routeLength = 0;
    let renderedProgress = 0;
    let scrollRange = 1;
    let scrollTop = Math.max(0, window.scrollY);
    let endThreshold = 2;
    const routeStart = { x: 0, y: 0 };
    const routeEnd = { x: 0, y: 0 };

    const draw = () => {
      frameId = 0;

      context.setTransform(1, 0, 0, 1, 0, 0);
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.setTransform(dpr, 0, 0, dpr, 0, 0);

      const isAtPageEnd = scrollTop > 0 && scrollRange - scrollTop <= endThreshold;
      const targetProgress = isAtPageEnd ? 1 : Math.min(1, scrollTop / scrollRange);
      const progressDifference = targetProgress - renderedProgress;
      if (reduceMotion || isAtPageEnd || Math.abs(progressDifference) < 0.0001) {
        renderedProgress = targetProgress;
      } else {
        renderedProgress += progressDifference * 0.2;
      }

      if (renderedProgress <= 0 || routeLength <= 0) return;

      routeStart.x = routeSamples[0].x;
      routeStart.y = routeSamples[0].y - scrollTop;

      const revealAlpha = Math.min(1, (renderedProgress * scrollRange) / 96);
      const mobile = width <= 760;

      context.save();
      context.lineCap = 'round';
      context.lineJoin = 'round';
      const gradient = context.createLinearGradient(0, 0, width, height);
      gradient.addColorStop(0, 'rgba(139, 85, 220, 0.08)');
      gradient.addColorStop(Math.max(0.12, renderedProgress * 0.72), 'rgba(92, 147, 232, 0.42)');
      gradient.addColorStop(1, 'rgba(94, 225, 210, 0.52)');
      context.strokeStyle = gradient;
      context.globalAlpha = revealAlpha * (mobile ? 0.12 : 0.16);
      context.lineWidth = mobile ? 3 : 4.5;
      if (!traceVisibleRoute(
        context,
        routeSamples,
        routeLength * renderedProgress,
        scrollTop,
        routeEnd,
      )) return;
      context.stroke();

      context.globalAlpha = revealAlpha;
      context.lineWidth = mobile ? 1 : 1.3;
      traceVisibleRoute(
        context,
        routeSamples,
        routeLength * renderedProgress,
        scrollTop,
        routeEnd,
      );
      context.stroke();
      context.restore();

      const dotRadius = mobile ? 1.9 : 2.4;
      drawRouteDot(
        context,
        routeStart,
        dotRadius,
        'rgba(150, 103, 229, 0.95)',
        revealAlpha * 0.78,
      );
      if (isAtPageEnd && renderedProgress >= 1) {
        drawRouteDot(
          context,
          routeEnd,
          dotRadius * 1.12,
          'rgba(101, 216, 226, 0.98)',
          revealAlpha,
        );
      }

      if (!reduceMotion && Math.abs(targetProgress - renderedProgress) >= 0.0001) {
        requestDraw();
      }
    };

    const requestDraw = () => {
      if (disposed || frameId) return;
      frameId = window.requestAnimationFrame(draw);
    };

    const measure = () => {
      if (disposed) return;
      const canvasBounds = canvas.getBoundingClientRect();
      const nextWidth = Math.max(1, canvasBounds.width);
      const nextHeight = Math.max(1, canvasBounds.height);
      const mobile = nextWidth <= 760;
      const nextDpr = Math.min(window.devicePixelRatio || 1, mobile ? 1.25 : 1.5);
      const pixelWidth = Math.round(nextWidth * nextDpr);
      const pixelHeight = Math.round(nextHeight * nextDpr);

      width = nextWidth;
      height = nextHeight;
      dpr = nextDpr;
      endThreshold = Math.max(2, dpr * 2);
      if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
        canvas.width = pixelWidth;
        canvas.height = pixelHeight;
      }

      anchors = routeStages
        .map((stage) => {
          const element = document.querySelector(stage.selector);
          if (!element) return null;
          const bounds = element.getBoundingClientRect();
          return {
            x: mobile ? width * 0.88 : width * stage.x,
            y: bounds.top + window.scrollY + bounds.height * stage.position,
          };
        })
        .filter(Boolean);

      const sampledRoute = sampleRoute(anchors);
      routeSamples = sampledRoute.samples;
      routeLength = sampledRoute.totalLength;

      const scrollingElement = document.scrollingElement ?? document.documentElement;
      scrollRange = Math.max(scrollingElement.scrollHeight - scrollingElement.clientHeight, 1);
      scrollTop = Math.max(0, scrollingElement.scrollTop);
      requestDraw();
    };

    const handleScroll = () => {
      scrollTop = Math.max(0, window.scrollY);
      requestDraw();
    };

    measure();

    const resizeObserver = new ResizeObserver(measure);
    routeStages.forEach(({ selector }) => {
      const element = document.querySelector(selector);
      if (element) resizeObserver.observe(element);
    });

    window.addEventListener('resize', measure, { passive: true });
    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('load', measure, { once: true });
    document.fonts?.ready?.then(() => {
      if (!disposed) measure();
    });

    return () => {
      disposed = true;
      window.cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      window.removeEventListener('resize', measure);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('load', measure);
    };
  }, [reduceMotion]);

  return <canvas ref={canvasRef} className="inference-route" aria-hidden="true" />;
}
