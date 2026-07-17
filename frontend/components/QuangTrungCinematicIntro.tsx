"use client";

import { useEffect, useRef, useState } from "react";

// ─── Audio files per scene ─────────────────────────────────────────────────
const SCENE_AUDIOS = [
  "/scene1.mp3",
  "/scene2.mp3",
  "/scene3.mp3",
  "/scene4.mp3",
  "/scene5.mp3",
  "/scene6.mp3",
];

// ─── Types ─────────────────────────────────────────────────────────────────
interface TextLine {
  text: string;
  startFrac: number; // [0,1] fraction of THIS scene's audio duration
  endFrac: number;
  style?: "normal" | "title" | "epic" | "heroic" | "hardship";
}

interface Scene {
  id: number;
  background: string | null;
  bgPosition?: string;     // CSS object-position for background image
  backgroundEffect: "kenburns-right" | "kenburns-left" | "kenburns-up" | "kenburns-victory" | "still";
  overlayClass: string;
  lines: TextLine[];
  particleMode: "dust" | "embers" | "sakura" | "sparks";
  chapterLabel: string;
}

// ─── Scene data ────────────────────────────────────────────────────────────
const SCENES: Scene[] = [
  {
    id: 0,
    background: null,
    backgroundEffect: "still",
    overlayClass: "overlay-dark",
    particleMode: "dust",
    chapterLabel: "Lời Mở Đầu",
    lines: [
      { text: "Trong lịch sử hàng nghìn năm của dân tộc Việt Nam...", startFrac: 0.04, endFrac: 0.50 },
      { text: "có một người đã làm rung chuyển cả thiên hạ.", startFrac: 0.54, endFrac: 0.96 },
    ],
  },
  {
    id: 1,
    background: "/images/quang_trung_coronation.png",
    backgroundEffect: "kenburns-right",
    overlayClass: "overlay-dawn",
    particleMode: "dust",
    chapterLabel: "Xuất Thân & Khởi Nghĩa",
    lines: [
      { text: "Nguyễn Huệ — sinh năm 1753 tại Phú Xuân, Bình Định.", startFrac: 0.02, endFrac: 0.34 },
      { text: "Từ tầng lớp bình dân, ông cùng anh em nhà Tây Sơn", startFrac: 0.36, endFrac: 0.65 },
      { text: "thắp ngọn lửa nổi dậy, lật đổ chúa Nguyễn,", startFrac: 0.67, endFrac: 0.96 },
    ],
  },
  {
    id: 2,
    background: "/images/quang_trung_coronation.png",
    backgroundEffect: "kenburns-left",
    overlayClass: "overlay-gold",
    particleMode: "dust",
    chapterLabel: "Đăng Quang Núi Bân · 1788",
    lines: [
      { text: "Tháng 12 năm Mậu Thân — 1788 —", startFrac: 0.02, endFrac: 0.28 },
      { text: "giữa mùa đông lạnh giá ở núi Bân, Huế,", startFrac: 0.30, endFrac: 0.58 },
      { text: "Nguyễn Huệ lên ngôi Hoàng đế, lấy hiệu là...", startFrac: 0.60, endFrac: 0.79 },
      { text: "QUANG TRUNG", startFrac: 0.81, endFrac: 0.97, style: "epic" },
    ],
  },
  {
    id: 3,
    background: "/images/quang_trung_march.png",
    backgroundEffect: "kenburns-up",
    overlayClass: "overlay-fire",
    particleMode: "embers",
    chapterLabel: "Hành Quân Thần Tốc",
    lines: [
      { text: "29 vạn quân Thanh kéo vào Thăng Long — nghênh ngang ăn Tết.", startFrac: 0.02, endFrac: 0.32 },
      { text: "Quang Trung hạ lệnh:", startFrac: 0.33, endFrac: 0.44 },
      { text: "XUẤT BINH", startFrac: 0.46, endFrac: 0.56, style: "heroic" },
      { text: "100.000 đại quân Tây Sơn — hành quân thần tốc xuyên đêm —", startFrac: 0.58, endFrac: 0.80 },
      { text: "500 cây số trong vòng 7 ngày", startFrac: 0.82, endFrac: 0.97, style: "hardship" },
    ],
  },
  {
    id: 4,
    background: "/images/quang_trung_battle.png",
    backgroundEffect: "kenburns-left",
    overlayClass: "overlay-battle",
    particleMode: "sparks",
    chapterLabel: "Đại Chiến Ngọc Hồi · 1789",
    lines: [
      { text: "Mùng 5 Tết Kỷ Dậu — 1789 —", startFrac: 0.02, endFrac: 0.22 },
      { text: "Voi chiến Tây Sơn phá tan đồn Ngọc Hồi.", startFrac: 0.24, endFrac: 0.48 },
      { text: "Đống Đa thất thủ — Sầm Nghi Đống tự vẫn.", startFrac: 0.50, endFrac: 0.74 },
      { text: "Tôn Sĩ Nghị bỏ ấn kiếm tháo chạy về Trung Quốc.", startFrac: 0.76, endFrac: 0.97 },
    ],
  },
  {
    id: 5,
    background: "/images/quang_trung_victory.png",
    bgPosition: "50% 0%",   // ← Unambiguous top-center: shows face clearly
    backgroundEffect: "kenburns-victory",
    overlayClass: "overlay-victory",
    particleMode: "sakura",
    chapterLabel: "Di Sản Bất Tử",
    lines: [
      { text: "Thăng Long giải phóng — chỉ trong 5 ngày.", startFrac: 0.02, endFrac: 0.26, style: "title" },
      { text: "Quang Trung — người anh hùng áo vải —", startFrac: 0.28, endFrac: 0.52 },
      { text: "mất năm 1792, chỉ 39 tuổi.", startFrac: 0.54, endFrac: 0.70 },
      { text: "Nhưng tinh thần của Ngài sẽ còn mãi mãi.", startFrac: 0.72, endFrac: 0.97 },
    ],
  },
];

// ─── Particle ──────────────────────────────────────────────────────────────
interface Particle {
  x: number; y: number;
  vx: number; vy: number;
  life: number; maxLife: number;
  size: number; color: string;
  rotation: number; rotSpeed: number;
  isPetal: boolean;
}

// ─── React state for renders (minimal surface) ────────────────────────────
interface RenderState {
  sceneIdx: number;
  exitingSceneIdx: number | null;
  activeLineIdx: number;
  passedLines: number[];   // array so React equality checks work
  globalFrac: number;
  transitionOut: boolean;
  epicFlash: boolean;
  showSceneFlash: boolean;
}

// ─── Component ─────────────────────────────────────────────────────────────
export function QuangTrungCinematicIntro({ onComplete }: { onComplete: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete; // keep latest ref without re-mounting

  const [rs, setRs] = useState<RenderState>({
    sceneIdx: 0,
    exitingSceneIdx: null,
    activeLineIdx: -1,
    passedLines: [],
    globalFrac: 0,
    transitionOut: false,
    epicFlash: false,
    showSceneFlash: false,
  });

  // Skip button ref so it can call skip from inside useEffect without stale closure
  const skipRef = useRef<() => void>(() => {});

  // ── All animation logic lives inside this one useEffect ───────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // ─ Canvas resize ─
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize, { passive: true });

    // ─ Mutable loop state ─
    let dead = false;          // set true on cleanup / skip
    let rafId = 0;
    const advanced = new Set<number>(); // guard against double-advance per scene
    const particles: Particle[] = [];

    // ─ Pre-load all audio ─
    const audioEls: HTMLAudioElement[] = SCENE_AUDIOS.map(src => {
      const a = new Audio(src);
      a.preload = "auto";
      return a;
    });

    // ─ Skip exposes teardown ─
    skipRef.current = () => {
      dead = true;
      cancelAnimationFrame(rafId);
      audioEls.forEach(a => { try { a.pause(); } catch (_) {} });
      onCompleteRef.current();
    };

    // ─ Particle helpers ───────────────────────────────────────────────────
    function spawnParticles(mode: Scene["particleMode"]) {
      // Always add some gold dust regardless of mode
      if (Math.random() < 0.28) {
        particles.push({
          x: Math.random() * canvas!.width,
          y: -8,
          vx: (Math.random() - 0.5) * 0.9,
          vy: Math.random() * 0.7 + 0.25,
          life: 0,
          maxLife: Math.random() * 220 + 130,
          size: Math.random() * 2.2 + 0.5,
          color: "rgba(229,189,59,",
          rotation: 0, rotSpeed: 0,
          isPetal: false,
        });
      }
      // Mode-specific particles
      const chance = mode === "sparks" ? 0.72 : mode === "sakura" ? 0.55 : 0.16;
      const count  = mode === "sparks" ? 4 : mode === "sakura" ? 3 : 1;
      for (let i = 0; i < count; i++) {
        if (Math.random() > chance) continue;
        const rising = mode === "embers" || mode === "sparks";
        let color: string;
        let isPetal = false;
        if (mode === "embers") color = `rgba(255,${Math.floor(Math.random() * 80 + 80)},20,`;
        else if (mode === "sakura") { color = `rgba(255,${Math.floor(Math.random() * 60 + 160)},180,`; isPetal = true; }
        else if (mode === "sparks") color = `rgba(255,${Math.floor(Math.random() * 120 + 100)},30,`;
        else color = "rgba(229,189,59,";   // dust
        particles.push({
          x: Math.random() * canvas!.width,
          y: rising ? canvas!.height + 10 : -10,
          vx: (Math.random() - 0.5) * (mode === "sparks" ? 5 : 1.2),
          vy: rising ? -(Math.random() * 3 + 1.5) : Math.random() * 1.1 + 0.35,
          life: 0,
          maxLife: Math.random() * 150 + 90,
          size: isPetal ? Math.random() * 18 + 9   // bigger dramatic petals
              : mode === "sparks" ? Math.random() * 3 + 1.5 : Math.random() * 2.5 + 0.8,
          color,
          rotation: isPetal ? Math.random() * Math.PI * 2 : 0,
          rotSpeed: isPetal ? (Math.random() - 0.5) * 0.06 : 0,
          isPetal,
        });
      }
    }

    function drawParticles(mode: Scene["particleMode"]) {
      const ctx = canvas!.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, canvas!.width, canvas!.height);

      spawnParticles(mode);

      // Filter dead
      let i = particles.length;
      while (i--) if (particles[i].life >= particles[i].maxLife) particles.splice(i, 1);

      for (const p of particles) {
        p.life++;
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.99;
        if (p.isPetal) p.rotation += p.rotSpeed;
        const alpha = Math.sin((p.life / p.maxLife) * Math.PI) * 0.82;
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.fillStyle = `${p.color}${alpha})`;
        if (p.isPetal) {
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rotation);
          ctx.beginPath();
          ctx.ellipse(0, 0, p.size * 0.45, p.size, 0, 0, Math.PI * 2);
          ctx.fill();
        } else {
          if (mode === "embers" || mode === "sparks") {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.x - p.vx * 3, p.y - p.vy * 3);
            ctx.strokeStyle = `${p.color}${alpha})`;
            ctx.lineWidth = Math.max(0.1, p.size * 0.4);
            ctx.stroke();
          }
          ctx.beginPath();
          ctx.arc(p.x, p.y, Math.max(0.1, p.size * 0.5), 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      }
    }

    // ─ Advance scene guard ────────────────────────────────────────────────
    function advanceScene(fromIdx: number) {
      if (dead || advanced.has(fromIdx)) return;
      advanced.add(fromIdx);
      cancelAnimationFrame(rafId);
      const next = fromIdx + 1;
      if (next >= SCENES.length) {
        dead = true;
        setRs(prev => ({ ...prev, globalFrac: 1 }));
        setTimeout(() => onCompleteRef.current(), 1000);
      } else {
        startScene(next);
      }
    }

    // ─ Core: start a scene ────────────────────────────────────────────────
    function startScene(idx: number) {
      if (dead) return;
      cancelAnimationFrame(rafId);
      particles.length = 0;

      const scene = SCENES[idx];
      const audio = audioEls[idx];

      // Silence other audios
      audioEls.forEach((a, i) => {
        if (i !== idx) { try { a.pause(); a.currentTime = 0; } catch (_) {} }
      });

      const prevIdx = idx > 0 ? idx - 1 : null;

      // Initial React state
      setRs({
        sceneIdx: idx,
        exitingSceneIdx: prevIdx,
        activeLineIdx: -1,
        passedLines: [],
        globalFrac: idx / SCENES.length,
        transitionOut: false,
        epicFlash: false,
        showSceneFlash: prevIdx !== null,
      });

      // Clear transition states after animation finishes
      setTimeout(() => {
        if (!dead) {
          setRs(prev => {
            if (prev.sceneIdx === idx) {
              return { ...prev, exitingSceneIdx: null, showSceneFlash: false };
            }
            return prev;
          });
        }
      }, 760);

      let epicFlashed = false;
      // Track elapsed TIME (seconds since scene started) for text sync
      // We use elapsed because audio.duration may be NaN at first
      let sceneStart = performance.now();
      // Once audio.duration loads, we switch to audio-time-based frac
      // For advancing: ONLY audio.ended / timeout, NOT frac >= 1
      let safetyTimeout: ReturnType<typeof setTimeout> | null = null;

      function tick() {
        if (dead) return;
        drawParticles(scene.particleMode);

        const elapsed = (performance.now() - sceneStart) / 1000;

        // Compute frac:
        // - If audio has valid duration: use audio.currentTime / duration (precise sync)
        // - Else: use elapsed / 6 (fallback estimate)
        let frac: number;
        const dur = audio.duration;
        const validDur = !!(dur && isFinite(dur) && dur > 0);
        if (validDur) {
          frac = Math.min(0.98, audio.currentTime / dur);
        } else {
          frac = Math.min(0.60, elapsed / 6); // won't advance, just shows text
        }

        // Karaoke: active line = first line whose range contains frac
        let activeLineIdx = -1;
        const passedLines: number[] = [];
        for (let i = 0; i < scene.lines.length; i++) {
          const line = scene.lines[i];
          if (frac >= line.startFrac && frac <= line.endFrac) {
            activeLineIdx = i;
          } else if (frac > line.endFrac) {
            passedLines.push(i);
          }
        }

        // Epic flash (scene 2 only)
        if (idx === 2 && !epicFlashed) {
          const epicLine = scene.lines.find(l => l.style === "epic");
          if (epicLine && frac >= epicLine.startFrac) {
            epicFlashed = true;
            setRs(prev => ({ ...prev, epicFlash: true }));
            setTimeout(() => setRs(prev => ({ ...prev, epicFlash: false })), 480);
          }
        }

        const transitionOut = validDur && (dur - audio.currentTime) < 0.85;
        const globalFrac = (idx + frac) / SCENES.length;

        setRs(prev => ({
          ...prev,
          activeLineIdx,
          passedLines,
          globalFrac,
          transitionOut,
        }));

        rafId = requestAnimationFrame(tick);
      }

      // Setup safety-net timeout BEFORE play (uses estimated duration from file size)
      // The "ended" event is primary; this is only a fallback
      const setupSafetyTimeout = (estimatedDur: number) => {
        if (safetyTimeout) clearTimeout(safetyTimeout);
        safetyTimeout = setTimeout(() => advanceScene(idx), (estimatedDur + 1.5) * 1000);
      };

      audio.currentTime = 0;
      audio.volume = 1;

      // When duration becomes known, set up the safety timeout
      audio.addEventListener("loadedmetadata", () => {
        setupSafetyTimeout(audio.duration || 8);
      }, { once: true });

      // If metadata already loaded, set safety timeout now
      if (audio.duration && isFinite(audio.duration)) {
        setupSafetyTimeout(audio.duration);
      } else {
        setupSafetyTimeout(10); // generic fallback
      }

      // PRIMARY advance trigger: ended event
      audio.addEventListener("ended", () => {
        if (safetyTimeout) clearTimeout(safetyTimeout);
        advanceScene(idx);
      }, { once: true });

      // Start playback + RAF loop
      audio.play()
        .then(() => {
          sceneStart = performance.now();
          rafId = requestAnimationFrame(tick);
        })
        .catch(() => {
          // Autoplay blocked: run entirely on elapsed time
          sceneStart = performance.now();
          rafId = requestAnimationFrame(tick);
          // Use a timed advance since audio.ended won't fire
          if (safetyTimeout) clearTimeout(safetyTimeout);
          setupSafetyTimeout(6);
        });
    }

    // ── Kick off ──
    startScene(0);

    return () => {
      dead = true;
      cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      audioEls.forEach(a => { try { a.pause(); } catch (_) {} });
    };
  }, []); // ← mount-only; onComplete accessed via ref

  const currentScene = SCENES[rs.sceneIdx] ?? SCENES[0];

  return (
    <div className={`cineintro-root ${rs.epicFlash ? "cineintro-flash" : ""}`}>
      {/* Particle canvas */}
      <canvas ref={canvasRef} className="cineintro-canvas" />

      {/* Background slides */}
      <div className="cineintro-bg-layer">
        {SCENES.map((scene, idx) => {
          const isActive = rs.sceneIdx === idx;
          const isExiting = rs.exitingSceneIdx === idx;
          return (
            <div
              key={scene.id}
              className={`cineintro-slide ${isActive ? "cineintro-slide-active" : ""} ${isExiting ? "cineintro-slide-exiting" : ""}`}
            >
              {scene.background ? (
                <img
                  src={scene.background}
                  alt=""
                  style={{ objectPosition: scene.bgPosition ?? "center center" }}
                  className={`cineintro-bg-img ${rs.sceneIdx === idx ? `cineintro-bg-${scene.backgroundEffect}` : ""}`}
                />
              ) : (
                <div className="cineintro-bg-dark" />
              )}
              {/* Per-slide vignette for cinematic depth */}
              <div className="cineintro-vignette" />
              <div className={`cineintro-overlay ${scene.overlayClass}`} />
            </div>
          );
        })}
      </div>

      {/* Scanline film texture — always present, very subtle */}
      <div className="cineintro-scanlines" />

      {/* Victory light rays — only on final scene */}
      {rs.sceneIdx === 5 && <div className="cineintro-light-rays" />}

      {/* Victory warm amber sunset glow — pulses at bottom of final scene */}
      {rs.sceneIdx === 5 && <div className="cineintro-victory-warmglow" />}

      {/* Golden scene transition flash overlay */}
      {rs.showSceneFlash && <div className="cineintro-scene-flash" />}

      {/* Skip */}
      <button
        onClick={() => skipRef.current()}
        className="cineintro-skip-btn"
        aria-label="Bỏ qua Intro"
      >
        Bỏ qua ▶
      </button>

      {/* Chapter label */}
      <div className="cineintro-chapter-label">{currentScene.chapterLabel}</div>

      {/* Scene dots */}
      <div className="cineintro-scene-dots">
        {SCENES.map((s, idx) => (
          <div
            key={s.id}
            className={`cineintro-dot ${idx === rs.sceneIdx ? "cineintro-dot-active" : idx < rs.sceneIdx ? "cineintro-dot-passed" : ""}`}
          />
        ))}
      </div>

      {/* Progress bar (bottom) */}
      <div className="cineintro-progress">
        <div className="cineintro-progress-fill" style={{ width: `${rs.globalFrac * 100}%` }} />
      </div>

      {/* ── Karaoke subtitle block ── */}
      <div className={`cineintro-subtitle-wrapper ${rs.transitionOut ? "cineintro-subtitle-fade" : ""}`}>
        {currentScene.lines.map((line, idx) => {
          const isActive  = rs.activeLineIdx === idx;
          const isPassed  = rs.passedLines.includes(idx);
          const isPending = !isActive && !isPassed;

          return (
            <div
              key={`${rs.sceneIdx}-${idx}`}
              className={[
                "cineintro-text-line",
                isActive  ? "cineintro-line-active"  : "",
                isPassed  ? "cineintro-line-passed"  : "",
                isPending ? "cineintro-line-pending" : "",
                line.style === "epic"  ? "cineintro-line-epic"  : "",
                line.style === "title" ? "cineintro-line-title" : "",
                line.style === "heroic" ? "cineintro-line-heroic" : "",
                line.style === "hardship" ? "cineintro-line-hardship" : "",
              ].filter(Boolean).join(" ")}
            >
              {line.text}
            </div>
          );
        })}
      </div>
    </div>
  );
}
