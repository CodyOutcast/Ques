import { useEffect, useRef } from 'react';

const vertexShader = /* glsl */ `
  attribute vec2 position;
  attribute vec2 uv;
  varying vec2 vUv;

  void main() {
    vUv = uv;
    gl_Position = vec4(position, 0.0, 1.0);
  }
`;

const fragmentShader = /* glsl */ `
  precision highp float;

  uniform float uTime;
  uniform float uScroll;
  uniform vec2 uResolution;
  uniform vec2 uPointer;
  varying vec2 vUv;

  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
      f.y
    );
  }

  float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    mat2 rotation = mat2(0.84, -0.54, 0.54, 0.84);

    for (int i = 0; i < 3; i++) {
      value += amplitude * noise(p);
      p = rotation * p * 2.02 + 7.13;
      amplitude *= 0.5;
    }

    return value;
  }

  void main() {
    vec2 p = vUv - 0.5;
    p.x *= uResolution.x / max(uResolution.y, 1.0);

    float time = uTime * 0.075;
    float coherence = smoothstep(0.06, 0.92, uScroll);
    float fieldA = fbm(p * 1.18 + vec2(time, -time * 0.62));
    float fieldB = fbm(p * 1.82 + vec2(-time * 0.54, time * 0.38));
    vec2 warp = vec2(fieldA - 0.5, fieldB - 0.5);
    float latent = fbm(p * 1.42 + warp * (1.25 - coherence * 0.35));

    float centralCurve = sin(p.x * 1.72 + time * 1.4) * 0.10;
    centralCurve += (latent - 0.5) * mix(0.34, 0.12, coherence);
    float primaryRibbon = exp(-abs(p.y - centralCurve) * 15.0);

    float branchCurve = -0.19 + sin(p.x * 2.1 - time) * 0.13;
    branchCurve += (fieldB - 0.5) * 0.24;
    float branchRibbon = exp(-abs(p.y - branchCurve) * 11.5) * (1.0 - coherence * 0.64);

    float filament = 1.0 - abs(sin((latent + p.x * 0.16 - uScroll * 0.3) * 17.0));
    filament = pow(max(filament, 0.0), 12.0) * (0.32 + fieldA * 0.68);

    vec2 pointer = uPointer - 0.5;
    pointer.x *= uResolution.x / max(uResolution.y, 1.0);
    float response = exp(-length(p - pointer * 0.28) * 3.9);

    vec3 indigo = vec3(0.18, 0.18, 0.78);
    vec3 violet = vec3(0.58, 0.24, 0.92);
    vec3 aqua = vec3(0.16, 0.82, 0.88);
    vec3 rose = vec3(0.86, 0.34, 0.60);

    vec3 color = mix(indigo, violet, fieldA);
    color *= filament * 0.27;
    color += mix(violet, aqua, coherence) * primaryRibbon * (0.08 + coherence * 0.13);
    color += mix(rose, indigo, fieldB) * branchRibbon * 0.075;
    color += aqua * response * primaryRibbon * 0.07;

    float haze = smoothstep(0.38, 0.82, latent) * 0.032;
    color += mix(indigo, aqua, coherence) * haze;

    float vignette = smoothstep(0.92, 0.12, length(vUv - 0.5));
    float alpha = filament * 0.12 + primaryRibbon * 0.08 + branchRibbon * 0.045 + haze;
    alpha *= 0.4 + vignette * 0.6;

    gl_FragColor = vec4(color, clamp(alpha, 0.0, 0.24));
  }
`;

export default function GenerativeField() {
  const mountRef = useRef(null);

  useEffect(() => {
    const mountNode = mountRef.current;
    if (!mountNode) return undefined;

    let disposed = false;
    let frameId = 0;
    let renderer;
    let gl;
    let program;
    let mesh;
    let reducedMotionQuery;
    let documentResizeObserver;
    let isReducedMotion = false;
    let isStaticMode = false;
    let isHeroActive = true;
    let frameInterval = 1000 / 30;
    let lastRenderTime = 0;
    let scrollRange = 1;
    const pointerTarget = { x: 0.5, y: 0.48 };
    const pointerCurrent = { x: 0.5, y: 0.48 };

    const initialise = async () => {
      const { Mesh, Program, Renderer, Triangle } = await import('ogl');
      if (disposed) return;

      reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      isReducedMotion = reducedMotionQuery.matches;
      const finePointerQuery = window.matchMedia('(pointer: fine)');
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      const deviceMemory = Number(navigator.deviceMemory) || Infinity;
      const logicalCores = Number(navigator.hardwareConcurrency) || Infinity;
      const isLowEndDevice = deviceMemory <= 2
        || logicalCores <= 2
        || (deviceMemory <= 4 && logicalCores <= 4);
      const prefersStaticField = Boolean(connection?.saveData)
        || isLowEndDevice;
      const shouldTrackPointer = finePointerQuery.matches && !prefersStaticField;
      isStaticMode = isReducedMotion || prefersStaticField;
      isHeroActive = window.scrollY < window.innerHeight * 0.95;

      renderer = new Renderer({
        alpha: true,
        antialias: false,
        dpr: 1,
        powerPreference: 'high-performance',
      });
      gl = renderer.gl;
      gl.clearColor(0, 0, 0, 0);
      gl.canvas.className = 'generative-field__canvas';
      gl.canvas.setAttribute('aria-hidden', 'true');
      mountNode.replaceChildren(gl.canvas);

      program = new Program(gl, {
        vertex: vertexShader,
        fragment: fragmentShader,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        uniforms: {
          uTime: { value: 0 },
          uScroll: { value: 0 },
          uResolution: { value: [window.innerWidth, window.innerHeight] },
          uPointer: { value: [0.5, 0.48] },
        },
      });
      mesh = new Mesh(gl, { geometry: new Triangle(gl), program });

      const updateScroll = () => {
        if (!program) return;
        program.uniforms.uScroll.value = window.scrollY / scrollRange;
        const nextHeroActive = window.scrollY < window.innerHeight * 0.95;
        if (nextHeroActive !== isHeroActive) {
          isHeroActive = nextHeroActive;
          restartAnimation();
        }
      };

      const updateDocumentMetrics = () => {
        scrollRange = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
        updateScroll();
      };

      const resize = () => {
        if (!renderer || !program) return;
        const isMobile = window.innerWidth <= 760;
        const pixelBudget = isMobile ? 650_000 : 1_250_000;
        const budgetDpr = Math.sqrt(pixelBudget / Math.max(window.innerWidth * window.innerHeight, 1));
        const dprCap = isMobile ? 1 : 1.15;
        renderer.dpr = Math.max(0.5, Math.min(window.devicePixelRatio || 1, dprCap, budgetDpr));
        renderer.setSize(window.innerWidth, window.innerHeight);
        program.uniforms.uResolution.value = [gl.canvas.width, gl.canvas.height];
        frameInterval = isMobile ? 1000 / 24 : 1000 / 30;
        updateDocumentMetrics();
        if (isStaticMode || !isHeroActive) restartAnimation();
      };

      const updatePointer = (event) => {
        pointerTarget.x = event.clientX / Math.max(window.innerWidth, 1);
        pointerTarget.y = 1 - event.clientY / Math.max(window.innerHeight, 1);
      };

      const render = (time = 0) => {
        if (!renderer || !program || !mesh || document.hidden) return;

        const shouldAnimate = !isStaticMode && isHeroActive;
        if (shouldAnimate && time - lastRenderTime < frameInterval) {
          frameId = window.requestAnimationFrame(render);
          return;
        }
        lastRenderTime = time;
        pointerCurrent.x += (pointerTarget.x - pointerCurrent.x) * 0.03;
        pointerCurrent.y += (pointerTarget.y - pointerCurrent.y) * 0.03;
        program.uniforms.uPointer.value = [pointerCurrent.x, pointerCurrent.y];
        program.uniforms.uTime.value = isStaticMode ? 2 : time * 0.001;
        renderer.render({ scene: mesh });
        if (shouldAnimate) frameId = window.requestAnimationFrame(render);
      };

      const restartAnimation = () => {
        window.cancelAnimationFrame(frameId);
        lastRenderTime = 0;
        if (!document.hidden) render(performance.now());
      };

      const handleMotionPreference = (event) => {
        isReducedMotion = event.matches;
        isStaticMode = isReducedMotion || prefersStaticField;
        restartAnimation();
      };

      const removeListeners = () => {
        window.removeEventListener('resize', resize);
        window.removeEventListener('scroll', updateScroll);
        if (shouldTrackPointer) {
          window.removeEventListener('pointermove', updatePointer);
        }
        documentResizeObserver?.disconnect();
        document.removeEventListener('visibilitychange', restartAnimation);
        reducedMotionQuery?.removeEventListener('change', handleMotionPreference);
      };

      resize();
      render(performance.now());
      window.addEventListener('resize', resize, { passive: true });
      window.addEventListener('scroll', updateScroll, { passive: true });
      if (shouldTrackPointer) {
        window.addEventListener('pointermove', updatePointer, { passive: true });
      }
      documentResizeObserver = new ResizeObserver(updateDocumentMetrics);
      documentResizeObserver.observe(document.body);
      document.addEventListener('visibilitychange', restartAnimation);
      reducedMotionQuery.addEventListener('change', handleMotionPreference);
      mountNode.cleanupGenerativeField = removeListeners;
    };

    initialise().catch(() => mountNode.classList.add('is-fallback'));

    return () => {
      disposed = true;
      window.cancelAnimationFrame(frameId);
      mountNode.cleanupGenerativeField?.();
      if (gl?.canvas?.parentNode) gl.canvas.parentNode.removeChild(gl.canvas);
    };
  }, []);

  return <div ref={mountRef} className="generative-field" aria-hidden="true" />;
}
