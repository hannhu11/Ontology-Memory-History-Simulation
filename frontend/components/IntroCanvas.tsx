"use client";

import { useEffect, useRef, useCallback } from "react";

// ─── Particle Types ────────────────────────────────────────────────
interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  life: number;
  maxLife: number;
  color: string;
  type: "ember" | "mist" | "splash" | "blossom" | "dust" | "lantern" | "confetti";
  rotation?: number;
  rotSpeed?: number;
}

interface WavePoint {
  x: number;
  y: number;
  baseY: number;
  speed: number;
  amplitude: number;
  phase: number;
}

// ─── Canvas Manager Hook ───────────────────────────────────────────
export function useIntroCanvas(
  canvasRef: React.RefObject<HTMLCanvasElement | null>,
  activeChapter: number,
  scrollProgress: number,
  mousePos: { x: number; y: number }
) {
  const particlesRef = useRef<Particle[]>([]);
  const wavePointsRef = useRef<WavePoint[]>([]);
  const frameRef = useRef<number>(0);
  const timeRef = useRef<number>(0);
  const initedRef = useRef(false);

  // ─── Initialize wave points ──────────────────────────────────────
  const initWaves = useCallback((width: number) => {
    const points: WavePoint[] = [];
    const count = Math.ceil(width / 20) + 1;
    for (let i = 0; i < count; i++) {
      points.push({
        x: (i / (count - 1)) * width,
        y: 0,
        baseY: 0,
        speed: 0.02 + Math.random() * 0.02,
        amplitude: 6 + Math.random() * 8,
        phase: Math.random() * Math.PI * 2,
      });
    }
    wavePointsRef.current = points;
  }, []);

  // ─── Spawn particles based on chapter ────────────────────────────
  const spawnParticles = useCallback(
    (width: number, height: number, chapter: number, dt: number) => {
      const particles = particlesRef.current;

      // Lanterns (ch 0) — floating golden dots like river lanterns
      if (chapter === 0) {
        if (particles.filter((p) => p.type === "lantern").length < 15 && Math.random() < 0.03) {
          particles.push({
            x: Math.random() * width,
            y: height * 0.55 + Math.random() * height * 0.15,
            vx: 0.15 + Math.random() * 0.3,
            vy: -0.05 + Math.random() * 0.05,
            size: 3 + Math.random() * 4,
            opacity: 0.6 + Math.random() * 0.4,
            life: 0,
            maxLife: 600 + Math.random() * 400,
            color: `hsl(${40 + Math.random() * 20}, 90%, ${60 + Math.random() * 20}%)`,
            type: "lantern",
          });
        }
      }

      // Mist (ch 0, 1, 2)
      if (chapter <= 2) {
        if (particles.filter((p) => p.type === "mist").length < 8 && Math.random() < 0.01) {
          particles.push({
            x: -100 + Math.random() * (width + 200),
            y: height * 0.3 + Math.random() * height * 0.4,
            vx: 0.2 + Math.random() * 0.4,
            vy: -0.05 + Math.random() * 0.1,
            size: 120 + Math.random() * 200,
            opacity: 0.04 + Math.random() * 0.06,
            life: 0,
            maxLife: 800 + Math.random() * 600,
            color: "rgba(200,220,210,1)",
            type: "mist",
          });
        }
      }

      // Splash (ch 1) — water droplets when puppet rises
      if (chapter === 1) {
        if (particles.filter((p) => p.type === "splash").length < 30 && Math.random() < 0.08) {
          const cx = width / 2;
          particles.push({
            x: cx + (Math.random() - 0.5) * 200,
            y: height * 0.65,
            vx: (Math.random() - 0.5) * 3,
            vy: -(2 + Math.random() * 4),
            size: 2 + Math.random() * 3,
            opacity: 0.8,
            life: 0,
            maxLife: 60 + Math.random() * 40,
            color: `hsl(${170 + Math.random() * 30}, 60%, ${60 + Math.random() * 20}%)`,
            type: "splash",
          });
        }
      }

      // Embers (ch 3, 4) — fire particles
      if (chapter === 3 || chapter === 4) {
        const maxEmbers = chapter === 4 ? 60 : 25;
        const spawnRate = chapter === 4 ? 0.15 : 0.06;
        if (particles.filter((p) => p.type === "ember").length < maxEmbers && Math.random() < spawnRate) {
          particles.push({
            x: Math.random() * width,
            y: height + 10,
            vx: (Math.random() - 0.5) * 1.5,
            vy: -(1 + Math.random() * 2.5),
            size: 1.5 + Math.random() * 3,
            opacity: 0.8 + Math.random() * 0.2,
            life: 0,
            maxLife: 120 + Math.random() * 180,
            color: `hsl(${15 + Math.random() * 25}, 100%, ${50 + Math.random() * 20}%)`,
            type: "ember",
          });
        }
      }

      // Dust (ch 4, 5) — battle dust
      if (chapter === 4) {
        if (particles.filter((p) => p.type === "dust").length < 40 && Math.random() < 0.1) {
          particles.push({
            x: -20,
            y: height * 0.4 + Math.random() * height * 0.4,
            vx: 2 + Math.random() * 3,
            vy: (Math.random() - 0.5) * 0.5,
            size: 40 + Math.random() * 60,
            opacity: 0.03 + Math.random() * 0.04,
            life: 0,
            maxLife: 200 + Math.random() * 200,
            color: "rgba(180,150,100,1)",
            type: "dust",
          });
        }
      }

      // Blossoms (ch 5, 6) — cherry blossoms falling
      if (chapter >= 5) {
        if (particles.filter((p) => p.type === "blossom").length < 25 && Math.random() < 0.04) {
          particles.push({
            x: Math.random() * width,
            y: -20,
            vx: 0.3 + Math.random() * 0.5,
            vy: 0.5 + Math.random() * 1,
            size: 6 + Math.random() * 8,
            opacity: 0.5 + Math.random() * 0.5,
            life: 0,
            maxLife: 400 + Math.random() * 300,
            color: `hsl(${340 + Math.random() * 20}, ${60 + Math.random() * 30}%, ${75 + Math.random() * 15}%)`,
            type: "blossom",
            rotation: Math.random() * 360,
            rotSpeed: (Math.random() - 0.5) * 3,
          });
        }
      }

      // Confetti (ch 6) — golden victory confetti
      if (chapter === 6) {
        if (particles.filter((p) => p.type === "confetti").length < 30 && Math.random() < 0.05) {
          particles.push({
            x: Math.random() * width,
            y: -10,
            vx: (Math.random() - 0.5) * 2,
            vy: 1 + Math.random() * 2,
            size: 4 + Math.random() * 6,
            opacity: 0.8 + Math.random() * 0.2,
            life: 0,
            maxLife: 300 + Math.random() * 200,
            color: `hsl(${40 + Math.random() * 15}, 90%, ${55 + Math.random() * 20}%)`,
            type: "confetti",
            rotation: Math.random() * 360,
            rotSpeed: (Math.random() - 0.5) * 8,
          });
        }
      }
    },
    []
  );

  // ─── Update & draw loop ──────────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      if (!initedRef.current) {
        initWaves(canvas.width);
        initedRef.current = true;
      }
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = () => {
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);
      timeRef.current++;
      const t = timeRef.current;

      // ── Draw water surface (chapters 0-2) ─────────────────
      if (activeChapter <= 2) {
        const waterY = height * (0.65 - activeChapter * 0.02);
        const wavePoints = wavePointsRef.current;

        // Update waves
        for (const wp of wavePoints) {
          wp.y = waterY + Math.sin(t * wp.speed + wp.phase) * wp.amplitude;
          // Mouse influence
          const dx = (wp.x / width - 0.5) - mousePos.x * 0.5;
          wp.y += dx * 3;
        }

        // Draw water body
        ctx.beginPath();
        ctx.moveTo(0, height);
        for (let i = 0; i < wavePoints.length; i++) {
          const p = wavePoints[i];
          if (i === 0) {
            ctx.lineTo(p.x, p.y);
          } else {
            const prev = wavePoints[i - 1];
            const cpx = (prev.x + p.x) / 2;
            ctx.quadraticCurveTo(prev.x, prev.y, cpx, (prev.y + p.y) / 2);
          }
        }
        ctx.lineTo(width, height);
        ctx.closePath();

        const waterGrad = ctx.createLinearGradient(0, waterY, 0, height);
        waterGrad.addColorStop(0, "rgba(5,46,33,0.6)");
        waterGrad.addColorStop(0.3, "rgba(3,26,18,0.85)");
        waterGrad.addColorStop(1, "rgba(3,10,7,0.95)");
        ctx.fillStyle = waterGrad;
        ctx.fill();

        // Water glow line
        ctx.beginPath();
        for (let i = 0; i < wavePoints.length; i++) {
          const p = wavePoints[i];
          if (i === 0) ctx.moveTo(p.x, p.y);
          else {
            const prev = wavePoints[i - 1];
            const cpx = (prev.x + p.x) / 2;
            ctx.quadraticCurveTo(prev.x, prev.y, cpx, (prev.y + p.y) / 2);
          }
        }
        ctx.strokeStyle = `rgba(229,189,59,${0.15 + Math.sin(t * 0.03) * 0.08})`;
        ctx.lineWidth = 2;
        ctx.shadowColor = "rgba(229,189,59,0.4)";
        ctx.shadowBlur = 12;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Moon reflection (ch 0)
        if (activeChapter === 0) {
          const moonX = width * 0.7 + mousePos.x * 15;
          const moonY = height * 0.15 + mousePos.y * 8;
          const moonGrad = ctx.createRadialGradient(moonX, moonY, 5, moonX, moonY, 80);
          moonGrad.addColorStop(0, "rgba(220,230,240,0.25)");
          moonGrad.addColorStop(0.4, "rgba(200,215,230,0.08)");
          moonGrad.addColorStop(1, "transparent");
          ctx.fillStyle = moonGrad;
          ctx.fillRect(0, 0, width, height);

          // Moon reflection on water
          const refY = waterY + 30 + mousePos.y * 5;
          for (let i = 0; i < 8; i++) {
            const ry = refY + i * 12;
            const rw = 30 - i * 3;
            ctx.fillStyle = `rgba(200,215,230,${0.05 - i * 0.005})`;
            ctx.fillRect(moonX - rw / 2 + Math.sin(t * 0.05 + i) * 5, ry, rw, 3);
          }
        }
      }

      // ── Spawn & update particles ──────────────────────────
      spawnParticles(width, height, activeChapter, 1);

      const particles = particlesRef.current;
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.life++;
        p.x += p.vx;
        p.y += p.vy;

        const lifeRatio = p.life / p.maxLife;

        // Physics by type
        if (p.type === "splash") {
          p.vy += 0.15; // gravity
          p.opacity = 0.8 * (1 - lifeRatio);
        } else if (p.type === "ember") {
          p.vx += (Math.random() - 0.5) * 0.1;
          p.vy -= 0.005;
          p.opacity = p.life < 20 ? p.life / 20 : (1 - lifeRatio) * 0.9;
        } else if (p.type === "blossom") {
          p.vx += Math.sin(t * 0.02 + p.x * 0.01) * 0.02;
          p.rotation = (p.rotation || 0) + (p.rotSpeed || 1);
          p.opacity = Math.min(1, p.life / 30) * (1 - Math.max(0, lifeRatio - 0.7) / 0.3);
        } else if (p.type === "confetti") {
          p.vx += Math.sin(t * 0.03 + p.y * 0.02) * 0.03;
          p.rotation = (p.rotation || 0) + (p.rotSpeed || 2);
          p.opacity = (1 - lifeRatio) * 0.9;
        } else if (p.type === "mist") {
          p.x += mousePos.x * 0.3;
          p.y += mousePos.y * 0.15;
          p.opacity = Math.min(p.opacity, (1 - lifeRatio) * 0.06);
        } else if (p.type === "dust") {
          p.opacity = Math.min(p.opacity, (1 - lifeRatio) * 0.05);
        } else if (p.type === "lantern") {
          p.vy = Math.sin(t * 0.02 + p.x * 0.005) * 0.15;
          p.opacity = 0.5 + Math.sin(t * 0.05 + p.x) * 0.2;
          if (lifeRatio > 0.8) p.opacity *= (1 - lifeRatio) / 0.2;
        }

        // Draw
        ctx.save();
        ctx.globalAlpha = Math.max(0, p.opacity);

        if (p.type === "mist" || p.type === "dust") {
          const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
          grad.addColorStop(0, p.color);
          grad.addColorStop(1, "transparent");
          ctx.fillStyle = grad;
          ctx.fillRect(p.x - p.size, p.y - p.size, p.size * 2, p.size * 2);
        } else if (p.type === "blossom") {
          ctx.translate(p.x, p.y);
          ctx.rotate(((p.rotation || 0) * Math.PI) / 180);
          ctx.fillStyle = p.color;
          // Petal shape
          for (let petal = 0; petal < 5; petal++) {
            ctx.beginPath();
            ctx.ellipse(0, -p.size * 0.4, p.size * 0.25, p.size * 0.45, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.rotate((Math.PI * 2) / 5);
          }
        } else if (p.type === "confetti") {
          ctx.translate(p.x, p.y);
          ctx.rotate(((p.rotation || 0) * Math.PI) / 180);
          ctx.fillStyle = p.color;
          ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
        } else if (p.type === "lantern") {
          // Glow
          const glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4);
          glow.addColorStop(0, p.color);
          glow.addColorStop(1, "transparent");
          ctx.fillStyle = glow;
          ctx.fillRect(p.x - p.size * 4, p.y - p.size * 4, p.size * 8, p.size * 8);
          // Core
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // ember, splash — simple circle
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
          // Glow for embers
          if (p.type === "ember") {
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 8;
            ctx.fill();
            ctx.shadowBlur = 0;
          }
        }

        ctx.restore();

        // Remove dead particles
        if (p.life >= p.maxLife || p.x < -200 || p.x > width + 200 || p.y < -200 || p.y > height + 200) {
          particles.splice(i, 1);
        }
      }

      frameRef.current = requestAnimationFrame(draw);
    };

    frameRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", resize);
    };
  }, [canvasRef, activeChapter, mousePos, initWaves, spawnParticles]);

  // Expose method to trigger burst effects
  const triggerSplashBurst = useCallback(
    (cx: number, cy: number, count = 20) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 2 + Math.random() * 4;
        particlesRef.current.push({
          x: cx,
          y: cy,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 2,
          size: 2 + Math.random() * 3,
          opacity: 0.9,
          life: 0,
          maxLife: 40 + Math.random() * 30,
          color: `hsl(${45 + Math.random() * 15}, 85%, ${55 + Math.random() * 20}%)`,
          type: "splash",
        });
      }
    },
    [canvasRef]
  );

  return { triggerSplashBurst };
}
