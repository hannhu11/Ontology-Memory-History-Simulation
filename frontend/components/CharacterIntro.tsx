"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";
import type { Character } from "../types";
import { useIntroCanvas } from "./IntroCanvas";
import { useIntroAudio } from "./IntroAudio";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}


interface CharacterIntroProps {
  character: Character;
  onComplete: () => void;
}

export function CharacterIntro({ character, onComplete }: CharacterIntroProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const lenisRef = useRef<Lenis | null>(null);
  
  // States for general flow
  const [activeChapter, setActiveChapter] = useState(0);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [audioStarted, setAudioStarted] = useState(false);
  const [showTooltip, setShowTooltip] = useState<string | null>(null);
  const chapterTriggeredRef = useRef<Set<number>>(new Set());

  // Interactive 1: Drag puppet stick
  const [stickProgress, setStickProgress] = useState(0);
  const [isDraggingStick, setIsDraggingStick] = useState(false);
  const stickStartRef = useRef<number | null>(null);
  const [puppetRevealed, setPuppetRevealed] = useState(false);

  // Interactive 2: Tactical Battle Matchmaking Map
  // Available Tây Sơn Tokens
  const TOKENS = [
    { id: "voi_chien", label: "Quang Trung (Voi chiến)", target: "ngoc_hoi", icon: "🐘" },
    { id: "ky_binh", label: "Đô đốc Long (Kỵ binh)", target: "khuong_thuong", icon: "🐎" },
    { id: "bo_binh", label: "Đô đốc Tuyết (Bộ binh)", target: "dam_muc", icon: "⚔" }
  ];
  // Target Fort Slots
  const TARGETS = [
    { id: "ngoc_hoi", label: "Đồn Ngọc Hồi", desc: "Chính diện phía Nam Thăng Long" },
    { id: "khuong_thuong", label: "Đồn Khương Thượng", desc: "Tập kích hiểm yếu phía Tây" },
    { id: "dam_muc", label: "Đầm Mực", desc: "Vây bắt chặn đường giặc tháo lui" }
  ];
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const [assignedSlots, setAssignedSlots] = useState<Record<string, string>>({}); // TargetId -> TokenId
  const [battleCompleted, setBattleCompleted] = useState(false);
  const [screenShake, setScreenShake] = useState(false);

  const audio = useIntroAudio();
  const { triggerSplashBurst } = useIntroCanvas(canvasRef, activeChapter, scrollProgress, mousePos);

  const TOTAL_CHAPTERS = 7;

  // ─── Start audio on first interaction ────────────────────────────
  const handleFirstInteraction = useCallback(() => {
    if (!audioStarted) {
      audio.initAudio();
      setAudioStarted(true);
      audio.playVoiceSegment(activeChapter);
    }
  }, [audioStarted, audio, activeChapter]);

  // ─── Mouse parallax tracking ─────────────────────────────────────
  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setMousePos({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      });
    };
    window.addEventListener("mousemove", handleMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMove);
  }, []);

  // ─── Lenis Smooth Scroll + GSAP ScrollTrigger ────────────────────
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Initialize Lenis
    const lenis = new Lenis({
      wrapper: container,
      content: container.firstElementChild as HTMLElement,
      lerp: 0.06,
      smoothWheel: true,
    });
    lenisRef.current = lenis;

    // Connect Lenis → GSAP ScrollTrigger
    lenis.on("scroll", (e: any) => {
      ScrollTrigger.update();
      const progress = e.progress || 0;
      setScrollProgress(progress);
    });

    // RAF loop for Lenis
    const raf = (time: number) => {
      lenis.raf(time);
      requestAnimationFrame(raf);
    };
    requestAnimationFrame(raf);

    // Configure ScrollTrigger to use our container
    ScrollTrigger.defaults({
      scroller: container,
    });

    // ── Per-chapter ScrollTriggers ──────────────────────────
    for (let i = 0; i < TOTAL_CHAPTERS; i++) {
      const section = container.querySelector(`[data-chapter="${i}"]`);
      if (!section) continue;

      // Puppet rise animation (Only apply scroll animation if puppet is revealed in Chapter 1)
      const puppetContent = section.querySelector(".puppet-content");
      if (puppetContent && i !== 1) {
        gsap.fromTo(
          puppetContent,
          { y: 100, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 1,
            ease: "power3.out",
            scrollTrigger: {
              trigger: section,
              start: "top 80%",
              end: "top 30%",
              scrub: 1,
            },
          }
        );
      }

      // Staggered text elements
      const staggerEls = section.querySelectorAll(".stagger-in");
      if (staggerEls.length) {
        gsap.fromTo(
          staggerEls,
          { y: 40, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            stagger: 0.15,
            duration: 0.8,
            ease: "power2.out",
            scrollTrigger: {
              trigger: section,
              start: "top 60%",
              toggleActions: "play none none reverse",
            },
          }
        );
      }

      // Chapter activation
      ScrollTrigger.create({
        trigger: section,
        start: "top 50%",
        end: "bottom 50%",
        onEnter: () => {
          setActiveChapter(i);
          audio.setChapter(i);
          audio.playVoiceSegment(i);
          // Trigger chapter-specific sounds (once)
          if (!chapterTriggeredRef.current.has(i)) {
            chapterTriggeredRef.current.add(i);
            if (i === 1) {
              audio.playWaterSplash();
              setTimeout(() => {
                const canvas = canvasRef.current;
                if (canvas) triggerSplashBurst(canvas.width / 2, canvas.height * 0.65, 10);
              }, 200);
            }
            if (i === 3) {
              // Crisis wind/fire
              setTimeout(() => audio.playCannonBoom(), 800);
            }
            if (i === 4) {
              audio.playVictoryDrum();
            }
          }
        },
        onEnterBack: () => {
          setActiveChapter(i);
          audio.setChapter(i);
          audio.playVoiceSegment(i);
        },
      });
    }

    // ── Parallax background images ─────────────────────────
    container.querySelectorAll(".parallax-img").forEach((img) => {
      gsap.fromTo(
        img,
        { yPercent: -15 },
        {
          yPercent: 15,
          ease: "none",
          scrollTrigger: {
            trigger: img.closest("section"),
            start: "top bottom",
            end: "bottom top",
            scrub: true,
          },
        }
      );
    });

    return () => {
      lenis.destroy();
      ScrollTrigger.getAll().forEach((st) => st.kill());
      audio.cleanup();
    };
  }, [puppetRevealed]); // Re-init scrolltriggers once puppet state completes to ensure height calculations align

  const handleSkip = useCallback(() => {
    audio.cleanup();
    onComplete();
  }, [audio, onComplete]);

  // ─── Drag Puppet Stick Logic ────────────────────────────────────
  const onStickMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    handleFirstInteraction();
    setIsDraggingStick(true);
    stickStartRef.current = e.clientY;
  };

  const onStickTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    handleFirstInteraction();
    if (e.touches.length > 0) {
      setIsDraggingStick(true);
      stickStartRef.current = e.touches[0].clientY;
    }
  };

  useEffect(() => {
    if (!isDraggingStick) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (stickStartRef.current === null) return;
      const diffY = stickStartRef.current - e.clientY; // drag up is positive
      const maxDragDistance = 250; // pixels to drag up
      const progress = Math.min(100, Math.max(0, (diffY / maxDragDistance) * 100));
      setStickProgress(progress);

      // Splash water periodically
      if (Math.random() < 0.25) {
        audio.playWaterSplash();
        const canvas = canvasRef.current;
        if (canvas) {
          triggerSplashBurst(
            canvas.width / 2 + (Math.random() - 0.5) * 120,
            canvas.height * (0.65 - (progress / 100) * 0.1),
            6
          );
        }
      }

      if (progress >= 100) {
        setIsDraggingStick(false);
        setPuppetRevealed(true);
        audio.playElephantRoar();
        const canvas = canvasRef.current;
        if (canvas) {
          triggerSplashBurst(canvas.width / 2, canvas.height * 0.55, 40);
        }
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (stickStartRef.current === null || e.touches.length === 0) return;
      const diffY = stickStartRef.current - e.touches[0].clientY;
      const maxDragDistance = 220;
      const progress = Math.min(100, Math.max(0, (diffY / maxDragDistance) * 100));
      setStickProgress(progress);

      if (Math.random() < 0.2) {
        audio.playWaterSplash();
      }

      if (progress >= 100) {
        setIsDraggingStick(false);
        setPuppetRevealed(true);
        audio.playElephantRoar();
      }
    };

    const handleMouseUp = () => {
      setIsDraggingStick(false);
      stickStartRef.current = null;
      // Spring back if not fully pulled
      if (stickProgress < 100) {
        gsap.to({ val: stickProgress }, {
          val: 0,
          duration: 0.5,
          ease: "power2.out",
          onUpdate: function() {
            setStickProgress((this.targets()[0] as any).val);
          }
        });
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("touchmove", handleTouchMove, { passive: false });
    window.addEventListener("touchend", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleMouseUp);
    };
  }, [isDraggingStick, stickProgress, triggerSplashBurst, audio]);

  // ─── Tactical Battle Matchmaking Logic ─────────────────────────
  const selectTokenForMatch = (tokenId: string) => {
    handleFirstInteraction();
    setSelectedToken(tokenId === selectedToken ? null : tokenId);
  };

  const assignToSlot = (targetId: string) => {
    if (!selectedToken) return;

    // Verify if it is correct target matching
    const matchingToken = TOKENS.find(t => t.id === selectedToken);
    if (matchingToken && matchingToken.target === targetId) {
      // Place successfully
      setAssignedSlots(prev => ({
        ...prev,
        [targetId]: selectedToken
      }));
      audio.playSwordClash();
      
      const canvas = canvasRef.current;
      if (canvas) {
        triggerSplashBurst(canvas.width * (0.3 + Math.random() * 0.4), canvas.height * 0.5, 15);
      }

      // Check if all placed correctly
      const nextSlots = { ...assignedSlots, [targetId]: selectedToken };
      if (Object.keys(nextSlots).length === TOKENS.length) {
        setBattleCompleted(true);
        setScreenShake(true);
        // Battle finale firework bursts
        setTimeout(() => audio.playCannonBoom(), 200);
        setTimeout(() => audio.playCannonBoom(), 800);
        setTimeout(() => {
          audio.playElephantRoar();
          setScreenShake(false);
        }, 1500);
      }
    } else {
      // Wrong slot feedback
      audio.playWaterSplash();
      // Jiggle element effect
      const element = document.getElementById(`target-${targetId}`);
      if (element) {
        gsap.fromTo(element, { x: -10 }, { x: 10, duration: 0.1, repeat: 3, yoyo: true, onComplete: () => { gsap.set(element, { x: 0 }); } });
      }
    }
    setSelectedToken(null);
  };

  // Reset tactical matchmaking board
  const resetBattleMap = () => {
    setAssignedSlots({});
    setBattleCompleted(false);
    setSelectedToken(null);
  };

  return (
    <div
      ref={containerRef}
      className={`story-scroll-container ${screenShake ? "camera-shake-active" : ""}`}
      onClick={handleFirstInteraction}
      onScroll={handleFirstInteraction}
    >
      {/* Lenis needs a content wrapper */}
      <div className="story-content-wrapper">
        {/* ── Canvas Layer (particles, water, effects) ── */}
        <canvas
          ref={canvasRef}
          className="story-canvas"
        />

        {/* ── Skip Button ── */}
        <button onClick={handleSkip} className="story-skip-btn">
          Bỏ qua Intro
        </button>

        {/* ── Scroll Progress ── */}
        <div
          className="story-progress-bar"
          style={{ width: `${scrollProgress * 100}%` }}
        />

        {/* ── Scroll Indicator (chapter 0 & revealed only) ── */}
        {activeChapter === 0 && (
          <div className="story-scroll-hint">
            <span>Cuộn để mở đầu</span>
            <div className="story-scroll-arrow" />
          </div>
        )}

        {/* ── Chapter Navigation Dots ── */}
        <div className="story-chapter-dots">
          {Array.from({ length: TOTAL_CHAPTERS }).map((_, i) => (
            <div
              key={i}
              className={`story-dot ${activeChapter === i ? "active" : ""} ${i <= activeChapter ? "visited" : ""}`}
            />
          ))}
        </div>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 0 — MỞ MÀN: Đêm trên sông cổ
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="0" className="story-section story-ch-opening">
          <div
            className="puppet-content story-center-col"
            style={{
              transform: `translate(${mousePos.x * -8}px, ${mousePos.y * -5}px)`,
            }}
          >
            <p className="stagger-in story-narrator-text">
              &ldquo;Mùa xuân năm Kỷ Dậu 1789...&rdquo;
            </p>
            <div className="stagger-in story-narrator-subtitle">
              Đêm giao thừa thay đổi vận mệnh giang sơn
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 1 — CON RỐI TRỒI LÊN (Drag wood handle)
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="1" className="story-section story-ch-reveal">
          <div className="puppet-content story-center-col">
            
            {/* Control Puppet Image Container */}
            <div className="story-puppet-frame stagger-in">
              <div className="story-puppet-glow" />
              <img
                src="/images/quang_trung_battle_elephant_king.png"
                alt="Quang Trung cưỡi voi chiến"
                className="story-puppet-image"
                style={{
                  transform: `scale(1.1) translateY(${puppetRevealed ? 0 : (100 - stickProgress) * 1.5}px)`,
                  filter: puppetRevealed ? "brightness(1.15) contrast(1.05) drop-shadow(0 0 25px rgba(229,189,59,0.55))" : `brightness(${0.25 + (stickProgress / 100) * 0.75})`
                }}
              />
            </div>

            {/* Drag Interaction Interface */}
            {!puppetRevealed ? (
              <div className="story-drag-stick-container stagger-in">
                <span className="story-drag-stick-label">
                  KÉO GẬY GỖ ĐỂ ĐIỀU KHIỂN CON RỐI
                </span>
                <div className="story-stick-slot">
                  <div 
                    className="story-stick-fill"
                    style={{ height: `${stickProgress}%` }}
                  />
                  <div
                    className={`story-stick-handle ${isDraggingStick ? "active" : ""}`}
                    style={{ bottom: `calc(${stickProgress}% - 22px)` }}
                    onMouseDown={onStickMouseDown}
                    onTouchStart={onStickTouchStart}
                  >
                    <div className="story-stick-wood-textures" />
                    <span>✥</span>
                  </div>
                </div>
                <p className="story-drag-sub">Nhấp giữ và kéo tay cầm gỗ hướng lên trên</p>
              </div>
            ) : (
              <div className="animate-pulse flex flex-col items-center">
                <h2 className="story-reveal-title text-gold-glow">
                  QUANG TRUNG XUẤT THẾ
                </h2>
                <p className="story-reveal-subtitle">
                  HOÀNG ĐẾ ÁO VẢI CỜ ĐÀO
                </p>
                <div className="mt-6 flex gap-2 items-center text-xs text-[var(--patina)] font-bold tracking-widest uppercase">
                  <span>Con rối đã khớp vị trí · Hãy cuộn tiếp tục</span>
                  <span className="animate-bounce">↓</span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 2 — GIỚI THIỆU NHÂN VẬT
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="2" className="story-section story-ch-intro">
          <div className="puppet-content story-center-col">
            <div className="stagger-in story-calligraphy text-red-neon">
              光中
            </div>
            <div className="story-info-cards">
              <div className="stagger-in story-info-card card-neon-gold">
                <div className="story-info-card-label">Tên húy</div>
                <div className="story-info-card-value">Nguyễn Huệ</div>
              </div>
              <div className="stagger-in story-info-card card-neon-gold">
                <div className="story-info-card-label">Niên hiệu</div>
                <div className="story-info-card-value">Quang Trung</div>
              </div>
              <div className="stagger-in story-info-card card-neon-gold">
                <div className="story-info-card-label">Triều đại</div>
                <div className="story-info-card-value">Tây Sơn</div>
              </div>
              <div className="stagger-in story-info-card card-neon-gold">
                <div className="story-info-card-label">Đăng quang</div>
                <div className="story-info-card-value">1788</div>
              </div>
            </div>
            <p className="stagger-in story-bio-text">
              Từ nông dân áo vải Bình Định, Nguyễn Huệ dựng cờ Tây Sơn diệt giặc ngoại xâm, dẹp loạn căn cứ, lên ngôi Hoàng đế, thiết lập kỷ nguyên mới cho dân tộc.
            </p>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 3 — GIANG SƠN LÂM NGUY
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="3" className="story-section story-ch-crisis">
          <div className="story-crisis-overlay" />
          <div className="puppet-content story-center-col">
            <span className="stagger-in story-chapter-label story-label-red">
              CHƯƠNG I — GIANG SƠN LÂM NGUY
            </span>
            <h3 className="stagger-in story-crisis-title">
              29 VẠN QUÂN THANH<br />XÂM LĂNG BẮC HÀ
            </h3>
            <p className="stagger-in story-crisis-text">
              Tôn Sĩ Nghị kiêu ngạo kéo đại quân chiếm đóng kinh thành Thăng Long. Lê Chiêu Thống bán nước cầu vinh, nhân dân lầm than trong ách áp bức hiểm nguy.
            </p>
            <div className="story-crisis-stats stagger-in">
              <div className="story-crisis-stat">
                <div className="story-stat-num text-red-glow text-orange-neon">290,000</div>
                <div className="story-stat-label">Giặc ngoại bang</div>
              </div>
              <div className="story-crisis-stat">
                <div className="story-stat-num text-orange-neon">1788</div>
                <div className="story-stat-label">Thăng Long thất thủ</div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 4 — HỊCH TƯỚNG SĨ & THỀ TRƯỚC TRẬN
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="4" className="story-section story-ch-oath">
          <div
            className="puppet-content story-center-col"
            style={{ transform: `translate(${mousePos.x * -5}px, 0)` }}
          >
            <span className="stagger-in story-chapter-label text-gold-glow">
              CHƯƠNG II — LỜI THỀ HẠ KỲ THỆ SƯ
            </span>
            <div className="stagger-in story-oath-scroll">
              <div className="story-oath-text text-gold-reflection">
                <p>&ldquo;Đánh cho để tóc dài,</p>
                <p>Đánh cho để răng đen,</p>
                <p>Đánh cho nó chích luân bất phản,</p>
                <p>Đánh cho nó phiến giáp bất hoàn,</p>
                <p>Đánh cho sử tri Nam quốc anh hùng chi hữu chủ!&rdquo;</p>
              </div>
            </div>
            <div className="stagger-in story-oath-source">
              — Lời tuyên dụ hùng tráng của Quang Trung tại Phượng Hoàng Trung Đô
            </div>
            <div className="stagger-in story-march-stats">
              <div className="story-march-stat">
                <span className="story-march-num text-gold-glow">200km</span>
                <span className="story-march-label">Hành quân thần tốc</span>
              </div>
              <div className="story-march-stat">
                <span className="story-march-num text-gold-glow">5 ngày</span>
                <span className="story-march-label">Tốc lực Phú Xuân → Tam Điệp</span>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 5 — ĐẠI CHIẾN NGỌC HỒI - ĐỐNG ĐA (Drag match minigame)
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="5" className="story-section story-ch-battle">
          {/* Background battle image */}
          <div className="story-battle-bg">
            <img
              src="/images/quang_trung_battle_elephant_king.png"
              alt="Đại phá quân Thanh"
              className="story-battle-bg-img parallax-img"
            />
            <div className="story-battle-bg-overlay" />
          </div>

          <div className="puppet-content story-center-col story-z-top w-full">
            <span className="stagger-in story-chapter-label story-label-red">
              CHƯƠNG III — CHIẾN DỊCH KỶ DẬU 1789
            </span>
            <h3 className="stagger-in story-battle-title text-gold-glow">
              SA BÀN DÀN TRẬN CHIẾN THUẬT
            </h3>
            
            {/* Tactical Battle Interactive Map Game */}
            <div className="story-tactical-map-container stagger-in w-full max-w-4xl">
              
              {/* Token Bank */}
              <div className="story-token-bank">
                <p className="story-bank-title">CHỌN CÁNH QUÂN TÂY SƠN:</p>
                <div className="story-tokens-list">
                  {TOKENS.map(token => {
                    const isPlaced = Object.values(assignedSlots).includes(token.id);
                    return (
                      <button
                        key={token.id}
                        onClick={() => !isPlaced && selectTokenForMatch(token.id)}
                        disabled={isPlaced}
                        className={`story-draggable-token ${selectedToken === token.id ? "selected" : ""} ${isPlaced ? "placed" : ""}`}
                      >
                        <span className="token-icon">{token.icon}</span>
                        <span className="token-label">{token.label}</span>
                        {isPlaced && <span className="token-check">✓ Đang công đồn</span>}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Target Map Slots */}
              <div className="story-tactical-map">
                <div className="story-map-bg-lines" />
                <p className="story-map-heading">KHOẢNG CÁCH THĂNG LONG CẬN KỀ — KÉO BÀI VÀO CỨ ĐIỂM:</p>
                <div className="story-map-targets">
                  {TARGETS.map(target => {
                    const slotTokenId = assignedSlots[target.id];
                    const slotToken = TOKENS.find(t => t.id === slotTokenId);
                    
                    return (
                      <div
                        key={target.id}
                        id={`target-${target.id}`}
                        onClick={() => selectedToken && assignToSlot(target.id)}
                        className={`story-drop-slot ${slotTokenId ? "occupied" : ""} ${selectedToken ? "waiting-pulse" : ""}`}
                      >
                        <div className="slot-glow" />
                        <div className="slot-meta">
                          <span className="slot-title">{target.label}</span>
                          <span className="slot-desc">{target.desc}</span>
                        </div>
                        <div className="slot-dropzone">
                          {slotToken ? (
                            <div className="slot-filled-token animate-[scaleIn_0.3s_ease]">
                              <span>{slotToken.icon}</span>
                              <strong>{slotToken.label}</strong>
                            </div>
                          ) : (
                            <span className="slot-placeholder">✥ Đợi điều binh</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Minigame status message */}
              <div className="story-game-actions">
                {battleCompleted ? (
                  <div className="story-battle-success-banner animate-[scaleIn_0.5s_ease_both]">
                    <span className="victory-badge">⚔ HOẢ LỰC ĐÃ CHÂM NGÒI</span>
                    <p className="victory-desc">
                      Quang Trung ngự voi chỉ huy công đồn chính diện Ngọc Hồi. Đô đốc Long cưỡi ngựa tập kích sườn Khương Thượng khiến giặc mất vía tự vẫn. Bộ binh Đô đốc Tuyết siết chặt gọng kìm tại Đầm Mực chặn đường tháo chạy của kẻ địch!
                    </p>
                  </div>
                ) : (
                  <p className="story-instructions-text">
                    {selectedToken 
                      ? "👉 Chọn một cứ điểm màu xanh trên bản đồ sa bàn để tiến đánh." 
                      : "🎯 Hãy chọn một quân bài Tây Sơn bên trên để tiến hành chỉ huy trận chiến."}
                  </p>
                )}
                
                {(Object.keys(assignedSlots).length > 0) && (
                  <button onClick={resetBattleMap} className="story-reset-btn">
                    Tái lập trận địa
                  </button>
                )}
              </div>
            </div>

            {/* Explanatory strategy hotspots (Only visible once game is completed to avoid clutter) */}
            {battleCompleted && (
              <div className="story-hotspots stagger-in mt-8">
                <button
                  className="story-hotspot"
                  onMouseEnter={() => setShowTooltip("strategy_summary")}
                  onMouseLeave={() => setShowTooltip(null)}
                >
                  ⚔ Chiến dịch Ngọc Hồi - Đống Đa
                  {showTooltip === "strategy_summary" && (
                    <div className="story-tooltip">
                      Tấn công chiến lược phối hợp hiệp đồng quân binh chủng cực cao: Hỏa lực voi chiến Tây Sơn xé toạc phòng tuyến, bộ binh và kỵ binh đánh thọc sâu tạo thế vây bắt nghẹt thở phá tan 29 vạn quân Thanh trong vòng 5 ngày xuân.
                    </div>
                  )}
                </button>
              </div>
            )}
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════
            CHAPTER 6 — CHIẾN THẮNG & VÀO DIỆN KIẾN
            ═══════════════════════════════════════════════════ */}
        <section data-chapter="6" className="story-section story-ch-victory">
          <div className="story-victory-sunrise" />
          <div className="puppet-content story-center-col story-z-top">
            <span className="stagger-in story-chapter-label story-label-gold">
              KHẢI HOÀN KỶ DẬU 1789
            </span>
            <h3 className="stagger-in story-victory-title text-gold-glow">
              QUYẾT ĐOÁN · TÁO BẠO · PHI THƯỜNG
            </h3>
            <p className="stagger-in story-victory-text">
              Mặc dù triều đại trị vì ngắn ngủi chỉ 4 năm trước khi băng hà đột ngột, vị vua áo vải anh hùng Quang Trung - Nguyễn Huệ đã khắc sâu vào trang sử Việt Nam tinh thần hành động quật cường, táo bạo và quả cảm vô song.
            </p>
            <div className="stagger-in story-victory-stats">
              <div className="story-v-stat">
                <div className="story-v-num text-gold-glow">5 ngày</div>
                <div className="story-v-label">Đại phá quân Thanh</div>
              </div>
              <div className="story-v-stat">
                <div className="story-v-num text-gold-glow">100%</div>
                <div className="story-v-label">Giải phóng bờ cõi Thăng Long</div>
              </div>
              <div className="story-v-stat">
                <div className="story-v-num text-gold-glow">Bất tử</div>
                <div className="story-v-label">Trong sử sách nước Nam</div>
              </div>
            </div>
            <button onClick={handleSkip} className="stagger-in story-cta-btn">
              ⚔ Bước Vào Diện Kiến Hoàng Đế
            </button>
          </div>
        </section>

        {/* Bottom padding for scroll clearance */}
        <div style={{ height: "30vh" }} />
      </div>
    </div>
  );
}
