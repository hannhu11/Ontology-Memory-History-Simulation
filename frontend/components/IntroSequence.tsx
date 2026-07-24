"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

/* ─────────────────────────── Types ─────────────────────────── */

interface IntroSequenceProps {
  onComplete: () => void;
}

interface Scene {
  id: number;
  background: string | null;
  title?: string;
  subtitle?: string;
  narration: string;
  isFinal?: boolean;
}

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
  drift: number;
  opacity: number;
}

/* ────────────────────────── Constants ──────────────────────── */

const SCENE_DURATION_MS = 12_000;
const TOTAL_DURATION_MS = 60_000;
const TYPING_SPEED_MS = 55;
const PARTICLE_COUNT = 42;

const GOLD = "#e5bd3b";
const GOLD_DARK = "#d4a937";
const GOLD_DIM = "rgba(229, 189, 59, 0.35)";
const LACQUER = "#0a0806";
const TEXT_PRIMARY = "#f6f0e4";

const SCENES: Scene[] = [
  {
    id: 0,
    background: "/intro/scene1_youth.png",
    title: "NGUYỄN TRÃI",
    subtitle: "Ức Trai · 1380–1442",
    narration:
      "Sinh ra trong thời loạn lạc, lớn lên giữa nỗi đau mất nước...",
  },
  {
    id: 1,
    background: "/intro/scene2_lamson.png",
    narration:
      "Theo Lê Lợi dựng cờ khởi nghĩa Lam Sơn, dùng mưu phạt tâm công — lấy nhân nghĩa thắng hung tàn, đem chí nhân thay cường bạo.",
  },
  {
    id: 2,
    background: "/intro/scene3_proclamation.png",
    narration:
      "Viết nên Bình Ngô đại cáo — bản tuyên ngôn độc lập thứ hai của dân tộc, khẳng định chủ quyền và nền văn hiến ngàn năm.",
  },
  {
    id: 3,
    background: "/intro/scene4_legacy.png",
    narration:
      "Bi kịch Lệ Chi Viên — người anh hùng bị oan khuất, nhưng tư tưởng nhân nghĩa sáng mãi ngàn thu.",
  },
  {
    id: 4,
    background: null,
    narration: "Hãy đối thoại cùng Nguyễn Trãi",
    isFinal: true,
  },
];

/* ──────────────────── Particle Generator ───────────────────── */

function generateParticles(count: number): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    particles.push({
      id: i,
      x: Math.random() * 100,
      y: 80 + Math.random() * 30,
      size: 1.5 + Math.random() * 3,
      duration: 8 + Math.random() * 14,
      delay: Math.random() * 12,
      drift: -20 + Math.random() * 40,
      opacity: 0.15 + Math.random() * 0.55,
    });
  }
  return particles;
}

/* ──────────────────── Typewriter Hook ──────────────────────── */

function useTypewriter(text: string, active: boolean, speed: number): string {
  const [displayed, setDisplayed] = useState("");
  const indexRef = useRef(0);

  useEffect(() => {
    if (!active) {
      setDisplayed("");
      indexRef.current = 0;
      return;
    }

    const intervalRef: { current: number | null } = {
      current: null,
    };

    /* Small delay before typing begins so the scene bg settles */
    const startDelay = window.setTimeout(() => {
      const interval = window.setInterval(() => {
        indexRef.current += 1;
        if (indexRef.current >= text.length) {
          setDisplayed(text);
          window.clearInterval(interval);
        } else {
          setDisplayed(text.slice(0, indexRef.current));
        }
      }, speed);

      /* Store interval handle so the outer cleanup can clear it */
      intervalRef.current = interval;
    }, 800);

    return () => {
      window.clearTimeout(startDelay);
      if (intervalRef.current !== null) window.clearInterval(intervalRef.current);
      indexRef.current = 0;
      setDisplayed("");
    };
  }, [text, active, speed]);

  return displayed;
}

/* ───────────────────── Keyframe Styles ─────────────────────── */

const KEYFRAMES = `
@keyframes introParticleRise {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: var(--p-opacity, 0.4);
  }
  90% {
    opacity: var(--p-opacity, 0.4);
  }
  100% {
    transform: translateY(-110vh) translateX(var(--p-drift, 0px));
    opacity: 0;
  }
}

@keyframes introKenBurns1 {
  0%   { transform: scale(1.0)  translate(0%, 0%); }
  100% { transform: scale(1.15) translate(-2%, -1.5%); }
}

@keyframes introKenBurns2 {
  0%   { transform: scale(1.05) translate(1%, 0%); }
  100% { transform: scale(1.18) translate(-1%, -2%); }
}

@keyframes introKenBurns3 {
  0%   { transform: scale(1.0)  translate(-1%, 1%); }
  100% { transform: scale(1.14) translate(1%, -1%); }
}

@keyframes introKenBurns4 {
  0%   { transform: scale(1.08) translate(0%, 0%); }
  100% { transform: scale(1.2)  translate(-2%, -2%); }
}

@keyframes introTitleGlow {
  0%, 100% { text-shadow: 0 0 40px rgba(229,189,59,0.3), 0 0 80px rgba(229,189,59,0.1); }
  50%      { text-shadow: 0 0 60px rgba(229,189,59,0.6), 0 0 120px rgba(229,189,59,0.2); }
}

@keyframes introPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(229,189,59,0.4);
  }
  50% {
    box-shadow: 0 0 0 14px rgba(229,189,59,0);
  }
}

@keyframes introCursorBlink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

@keyframes introFadeInUp {
  0%   { opacity: 0; transform: translateY(24px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes introStarTwinkle {
  0%, 100% { opacity: 0.15; transform: scale(0.8); }
  50%      { opacity: 0.7;  transform: scale(1.2); }
}

@keyframes introProgressShine {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}
`;

const KEN_BURNS_ANIMATIONS = [
  "introKenBurns1",
  "introKenBurns2",
  "introKenBurns3",
  "introKenBurns4",
];

/* ═══════════════════════ Main Component ════════════════════════ */

export function IntroSequence({ onComplete }: IntroSequenceProps) {
  /* ── State ── */
  const [currentScene, setCurrentScene] = useState(0);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [sceneOpacity, setSceneOpacity] = useState(1);
  const [sceneScale, setSceneScale] = useState(1);
  const [titleVisible, setTitleVisible] = useState(false);
  const [subtitleVisible, setSubtitleVisible] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const startTimeRef = useRef(Date.now());
  const rafRef = useRef<number | null>(null);
  const sceneTimerRef = useRef<number | null>(null);
  const unmountedRef = useRef(false);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.play().catch((err) => console.log("Audio autoplay blocked", err));
    }
  }, []);

  const handleFinish = () => {
    if (audioRef.current) {
      try { audioRef.current.pause(); } catch (_) {}
    }
    onComplete();
  };

  const particles = useMemo(() => generateParticles(PARTICLE_COUNT), []);
  const scene = SCENES[currentScene];

  /* ── Typewriter for narration ── */
  const typedText = useTypewriter(
    scene.narration,
    sceneOpacity > 0.5,
    TYPING_SPEED_MS
  );

  /* ── Title / subtitle staggered entrance (scene 0 only) ── */
  useEffect(() => {
    if (currentScene !== 0) {
      setTitleVisible(false);
      setSubtitleVisible(false);
      return;
    }
    const t1 = window.setTimeout(() => setTitleVisible(true), 600);
    const t2 = window.setTimeout(() => setSubtitleVisible(true), 1800);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, [currentScene]);

  /* ── Elapsed‑time animation frame ── */
  useEffect(() => {
    unmountedRef.current = false;
    startTimeRef.current = Date.now();

    function tick() {
      if (unmountedRef.current) return;
      const now = Date.now();
      const elapsed = now - startTimeRef.current;
      setElapsedMs(Math.min(elapsed, TOTAL_DURATION_MS));
      if (elapsed < TOTAL_DURATION_MS) {
        rafRef.current = requestAnimationFrame(tick);
      }
    }

    rafRef.current = requestAnimationFrame(tick);

    return () => {
      unmountedRef.current = true;
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  /* ── Scene transitions ── */
  const transitionToScene = useCallback(
    (nextIndex: number) => {
      if (nextIndex >= SCENES.length) {
        onComplete();
        return;
      }
      /* Fade out current scene */
      setSceneOpacity(0);
      setSceneScale(0.97);

      sceneTimerRef.current = window.setTimeout(() => {
        if (unmountedRef.current) return;
        setCurrentScene(nextIndex);
        /* Fade in new scene */
        setSceneOpacity(0);
        setSceneScale(1.03);

        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            if (unmountedRef.current) return;
            setSceneOpacity(1);
            setSceneScale(1);
          });
        });
      }, 800);
    },
    [onComplete]
  );

  /* Auto-advance scenes */
  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (unmountedRef.current) return;
      if (scene.isFinal) return; /* scene 5 stays until button click */
      transitionToScene(currentScene + 1);
    }, SCENE_DURATION_MS);

    return () => window.clearTimeout(timer);
  }, [currentScene, scene.isFinal, transitionToScene]);

  /* ── Cleanup ── */
  useEffect(() => {
    return () => {
      unmountedRef.current = true;
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      if (sceneTimerRef.current !== null)
        window.clearTimeout(sceneTimerRef.current);
    };
  }, []);

  /* ── Derived ── */
  const progressPct = Math.min(100, (elapsedMs / TOTAL_DURATION_MS) * 100);
  const kenBurnsAnim =
    KEN_BURNS_ANIMATIONS[currentScene % KEN_BURNS_ANIMATIONS.length];

  /* ══════════════════════════ Render ═══════════════════════════ */

  return (
    <>
      {/* Inject keyframes */}
      <style dangerouslySetInnerHTML={{ __html: KEYFRAMES }} />

      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 9999,
          backgroundColor: LACQUER,
          overflow: "hidden",
          fontFamily:
            "'Noto Serif', 'Source Serif 4', 'Georgia', serif",
        }}
      >
        <audio ref={audioRef} src="/speech_intro_nguyen_trai.mp3" preload="auto" />
        {/* ─── Background layer ─── */}
        {scene.background ? (
          <div
            key={`bg-${scene.id}`}
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: `url("${scene.background}")`,
              backgroundSize: "cover",
              backgroundPosition: "center",
              animation: `${kenBurnsAnim} ${SCENE_DURATION_MS}ms ease-out forwards`,
              opacity: sceneOpacity * 0.55,
              transition: "opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
              willChange: "transform, opacity",
            }}
            aria-hidden="true"
          />
        ) : null}

        {/* ─── Dark vignette overlay ─── */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `
              radial-gradient(ellipse 80% 70% at 50% 50%, transparent 0%, ${LACQUER} 100%),
              linear-gradient(to bottom, rgba(10,8,6,0.4) 0%, transparent 30%, transparent 70%, rgba(10,8,6,0.85) 100%)
            `,
            pointerEvents: "none",
          }}
          aria-hidden="true"
        />

        {/* ─── Ambient golden particles ─── */}
        <div
          style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
          aria-hidden="true"
        >
          {particles.map((p) => (
            <div
              key={p.id}
              style={{
                position: "absolute",
                left: `${p.x}%`,
                top: `${p.y}%`,
                width: p.size,
                height: p.size,
                borderRadius: "50%",
                backgroundColor: GOLD,
                opacity: 0,
                animation: `introParticleRise ${p.duration}s linear ${p.delay}s infinite`,
                ["--p-drift" as string]: `${p.drift}px`,
                ["--p-opacity" as string]: p.opacity,
                willChange: "transform, opacity",
              }}
            />
          ))}
        </div>

        {/* ─── Scene 5 star field ─── */}
        {scene.isFinal ? (
          <div
            style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
            aria-hidden="true"
          >
            {Array.from({ length: 60 }).map((_, i) => (
              <div
                key={`star-${i}`}
                style={{
                  position: "absolute",
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  width: 1.5 + Math.random() * 2,
                  height: 1.5 + Math.random() * 2,
                  borderRadius: "50%",
                  backgroundColor:
                    i % 3 === 0 ? GOLD : "rgba(246, 240, 228, 0.6)",
                  animation: `introStarTwinkle ${2 + Math.random() * 4}s ease-in-out ${Math.random() * 3}s infinite`,
                }}
              />
            ))}
          </div>
        ) : null}

        {/* ─── Content layer ─── */}
        <div
          style={{
            position: "relative",
            zIndex: 2,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            padding: "2rem 1.5rem",
            opacity: sceneOpacity,
            transform: `scale(${sceneScale})`,
            transition:
              "opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
        >
          {/* Scene 1 – Title card */}
          {scene.title ? (
            <div
              style={{
                textAlign: "center",
                marginBottom: 24,
                opacity: titleVisible ? 1 : 0,
                transform: titleVisible
                  ? "translateY(0)"
                  : "translateY(30px)",
                transition:
                  "opacity 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94), transform 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
              }}
            >
              <h1
                style={{
                  fontSize: "clamp(2.5rem, 6vw, 5rem)",
                  fontWeight: 900,
                  letterSpacing: "0.14em",
                  color: GOLD,
                  margin: 0,
                  lineHeight: 1.1,
                  animation: "introTitleGlow 3s ease-in-out infinite",
                }}
              >
                {scene.title}
              </h1>
              {scene.subtitle ? (
                <div
                  style={{
                    marginTop: 16,
                    fontSize: "clamp(0.9rem, 2vw, 1.25rem)",
                    fontWeight: 700,
                    letterSpacing: "0.22em",
                    textTransform: "uppercase",
                    color: GOLD_DARK,
                    opacity: subtitleVisible ? 0.85 : 0,
                    transform: subtitleVisible
                      ? "translateY(0)"
                      : "translateY(16px)",
                    transition:
                      "opacity 1s ease 0.2s, transform 1s ease 0.2s",
                  }}
                >
                  {scene.subtitle}
                </div>
              ) : null}
            </div>
          ) : null}

          {/* Scene 5 – Final heading */}
          {scene.isFinal ? (
            <h2
              style={{
                fontSize: "clamp(1.6rem, 4vw, 2.8rem)",
                fontWeight: 900,
                color: GOLD,
                textAlign: "center",
                lineHeight: 1.3,
                margin: 0,
                marginBottom: 40,
                animation: "introTitleGlow 3s ease-in-out infinite",
              }}
            >
              {scene.narration}
            </h2>
          ) : null}

          {/* Narration text (typewriter) — non-final scenes */}
          {!scene.isFinal ? (
            <div
              style={{
                maxWidth: 680,
                textAlign: "center",
                position: "relative",
              }}
            >
              {/* Decorative line above text */}
              <div
                style={{
                  width: 48,
                  height: 2,
                  background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
                  margin: "0 auto 24px",
                  borderRadius: 1,
                  opacity: typedText.length > 0 ? 0.7 : 0,
                  transition: "opacity 0.6s ease",
                }}
                aria-hidden="true"
              />

              <p
                style={{
                  fontSize: "clamp(1rem, 2.2vw, 1.35rem)",
                  lineHeight: 2,
                  color: TEXT_PRIMARY,
                  margin: 0,
                  fontWeight: 500,
                  textShadow: "0 2px 20px rgba(0,0,0,0.7)",
                }}
              >
                {typedText}
                {typedText.length < scene.narration.length ? (
                  <span
                    style={{
                      display: "inline-block",
                      width: 2,
                      height: "1.1em",
                      backgroundColor: GOLD,
                      marginLeft: 2,
                      verticalAlign: "text-bottom",
                      animation: "introCursorBlink 0.8s step-end infinite",
                    }}
                    aria-hidden="true"
                  />
                ) : null}
              </p>

              {/* Decorative line below text */}
              <div
                style={{
                  width: 48,
                  height: 2,
                  background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
                  margin: "24px auto 0",
                  borderRadius: 1,
                  opacity:
                    typedText.length >= scene.narration.length ? 0.7 : 0,
                  transition: "opacity 1s ease",
                }}
                aria-hidden="true"
              />
            </div>
          ) : null}

          {/* Scene 5 – CTA Button */}
          {scene.isFinal ? (
            <button
              onClick={handleFinish}
              style={{
                marginTop: 8,
                padding: "18px 48px",
                fontSize: "1.05rem",
                fontWeight: 800,
                fontFamily: "inherit",
                letterSpacing: "0.08em",
                color: LACQUER,
                backgroundColor: GOLD,
                border: "none",
                borderRadius: 8,
                cursor: "pointer",
                animation:
                  "introPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite, introFadeInUp 1s ease-out both",
                animationDelay: "0s, 0.4s",
                transition:
                  "background-color 0.3s ease, transform 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "#f0cc58";
                e.currentTarget.style.transform = "scale(1.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = GOLD;
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              Bắt đầu trải nghiệm
            </button>
          ) : null}
        </div>

        {/* ─── Skip button ─── */}
        <button
          onClick={handleFinish}
          style={{
            position: "absolute",
            top: 28,
            right: 32,
            zIndex: 10,
            padding: "10px 22px",
            fontSize: "0.8rem",
            fontWeight: 700,
            fontFamily: "inherit",
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: "rgba(246, 240, 228, 0.6)",
            backgroundColor: "rgba(246, 240, 228, 0.06)",
            border: `1px solid rgba(246, 240, 228, 0.12)`,
            borderRadius: 6,
            cursor: "pointer",
            backdropFilter: "blur(8px)",
            transition:
              "color 0.3s ease, border-color 0.3s ease, background-color 0.3s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = TEXT_PRIMARY;
            e.currentTarget.style.borderColor = GOLD_DIM;
            e.currentTarget.style.backgroundColor =
              "rgba(229, 189, 59, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "rgba(246, 240, 228, 0.6)";
            e.currentTarget.style.borderColor =
              "rgba(246, 240, 228, 0.12)";
            e.currentTarget.style.backgroundColor =
              "rgba(246, 240, 228, 0.06)";
          }}
          aria-label="Bỏ qua phần giới thiệu"
        >
          Bỏ qua
        </button>

        {/* ─── Scene indicator dots ─── */}
        <div
          style={{
            position: "absolute",
            bottom: 56,
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 10,
            display: "flex",
            gap: 10,
          }}
          aria-hidden="true"
        >
          {SCENES.map((s) => (
            <div
              key={s.id}
              style={{
                width: s.id === currentScene ? 24 : 8,
                height: 8,
                borderRadius: 4,
                backgroundColor:
                  s.id === currentScene ? GOLD : "rgba(246, 240, 228, 0.2)",
                transition:
                  "width 0.5s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.5s ease",
              }}
            />
          ))}
        </div>

        {/* ─── Progress bar ─── */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 3,
            backgroundColor: "rgba(246, 240, 228, 0.06)",
            zIndex: 10,
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${progressPct}%`,
              background: `linear-gradient(90deg, ${GOLD_DARK}, ${GOLD}, ${GOLD_DARK})`,
              backgroundSize: "200% 100%",
              animation: "introProgressShine 2s linear infinite",
              borderRadius: "0 2px 2px 0",
              transition: "width 0.25s linear",
              boxShadow: `0 0 12px ${GOLD_DIM}`,
            }}
          />
        </div>

        {/* ─── Elapsed time indicator ─── */}
        <div
          style={{
            position: "absolute",
            bottom: 14,
            right: 32,
            zIndex: 10,
            fontSize: "0.7rem",
            fontWeight: 700,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            letterSpacing: "0.08em",
            color: "rgba(246, 240, 228, 0.3)",
          }}
          aria-hidden="true"
        >
          {Math.floor(elapsedMs / 1000)
            .toString()
            .padStart(2, "0")}
          s / 60s
        </div>
      </div>
    </>
  );
}

export default IntroSequence;
