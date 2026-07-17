"use client";

import { useEffect, useState, useRef } from "react";
import { fetchCharacters } from "../../lib/api";
import { useHistoryStore } from "../../lib/store";
import type { Character } from "../../types";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";

const CharacterIntro = dynamic(
  () => import("../../components/CharacterIntro").then((mod) => mod.CharacterIntro),
  { ssr: false }
);

const QuangTrungCinematicIntro = dynamic(
  () => import("../../components/QuangTrungCinematicIntro").then((mod) => mod.QuangTrungCinematicIntro),
  { ssr: false }
);


// Local image maps to static local assets or dynamic assets from backend
const CHARACTER_IMAGE_MAP: Record<string, string> = {
  quang_trung: "/assets/quang_trung/idle.png",
  tran_hung_dao: "/assets/tran_hung_dao/idle.png",
  nguyen_trai: "/assets/nguyen_trai/idle.png",
  ho_chi_minh: "/assets/ho_chi_minh/idle.png",
  vo_nguyen_giap: "/assets/vo_nguyen_giap/idle.png",
};

export default function CharacterSelectPage() {
  const router = useRouter();
  const [characterList, setCharacterList] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [playIntro, setPlayIntro] = useState(false);
  const [playCinematicIntro, setPlayCinematicIntro] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  
  const selectCharacter = useHistoryStore((state) => state.selectCharacter);

  useEffect(() => {
    fetchCharacters()
      .then((payload) => {
        setCharacterList(payload.characters);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Không tải được danh sách nhân vật.");
        setLoading(false);
      });
  }, []);

  // Background Canvas particles
  useEffect(() => {
    if (playIntro) return; // disable background canvas if intro is playing
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let particles: Array<{
      x: number;
      y: number;
      size: number;
      speedY: number;
      speedX: number;
      opacity: number;
    }> = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Populate particles
    for (let i = 0; i < 40; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 1,
        speedY: -(Math.random() * 0.4 + 0.1),
        speedX: (Math.random() - 0.5) * 0.2,
        opacity: Math.random() * 0.4 + 0.1,
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#e5bd3b";
      
      particles.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.globalAlpha = p.opacity;
        ctx.fill();

        p.y += p.speedY;
        p.x += p.speedX;

        if (p.y < -10) {
          p.y = canvas.height + 10;
          p.x = Math.random() * canvas.width;
        }
      });
      animId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, [playIntro, loading]);

  const handleSelect = (character: Character) => {
    setSelectedCharacter(character);
    if (character.character_id === "quang_trung") {
      setPlayCinematicIntro(true);
    } else {
      selectCharacter(character.character_id);
      localStorage.setItem("history_simulation_active_char", character.character_id);
      router.push(`/?character=${character.character_id}`);
    }
  };

  const handleIntroComplete = () => {
    if (selectedCharacter) {
      // Save chosen character ID to store and localStorage
      selectCharacter(selectedCharacter.character_id);
      localStorage.setItem("history_simulation_active_char", selectedCharacter.character_id);
      router.push(`/?character=${selectedCharacter.character_id}`);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-[#0c0a07] flex flex-col items-center justify-center text-[#e5bd3b]">
        <div className="text-xl font-display tracking-[0.2em] animate-pulse">Đang mở phủ dụ nhân vật...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-[#0c0a07] flex flex-col items-center justify-center text-[#ff4d4d] p-6 text-center">
        <h2 className="text-2xl font-bold font-display mb-4">Lỗi Hệ Thống</h2>
        <p className="max-w-md">{error}</p>
        <button onClick={() => window.location.reload()} className="mt-6 border border-[#ff4d4d] px-4 py-2 rounded-md hover:bg-[#ff4d4d]/10 transition">
          Thử lại
        </button>
      </div>
    );
  }

  if (playCinematicIntro && selectedCharacter) {
    return <QuangTrungCinematicIntro onComplete={handleIntroComplete} />;
  }

  if (playIntro && selectedCharacter) {
    return <CharacterIntro character={selectedCharacter} onComplete={handleIntroComplete} />;
  }

  return (
    <main className="select-page">
      <div className="select-bg" />
      <canvas ref={canvasRef} className="select-canvas" />
      
      <div className="select-content">
        <header className="select-header">
          <div className="select-header-ornament">
            <span className="select-header-line" />
            <span className="select-header-diamond" />
            <span className="select-header-line" />
          </div>
          <h1 className="select-title">ĐỐI THOẠI LỊCH SỬ</h1>
          <p className="select-subtitle">Chọn nhân vật để bước vào không gian nhập vai</p>
        </header>

        <section className="character-cards-grid">
          {characterList.map((char) => {
            const imgSrc = CHARACTER_IMAGE_MAP[char.character_id] || char.portrait_url;
            return (
              <article key={char.character_id} className="character-card">
                <div className="character-card-badge">{char.death_year ? `Tại thế ${char.death_year}` : "Danh nhân"}</div>
                
                {imgSrc ? (
                  <img 
                    src={imgSrc} 
                    alt={char.display_name} 
                    className="character-card-portrait"
                    onError={(e) => {
                      // Fallback if image fails to load
                      (e.target as HTMLImageElement).style.display = 'none';
                      const placeholder = (e.target as HTMLImageElement).nextElementSibling;
                      if (placeholder) {
                        (placeholder as HTMLElement).style.display = 'flex';
                      }
                    }}
                  />
                ) : null}
                
                <div 
                  className="character-card-portrait-placeholder" 
                  style={{ display: imgSrc ? 'none' : 'flex' }}
                >
                  {char.display_name.slice(0, 2)}
                </div>

                <div className="character-card-info">
                  <h2 className="character-card-name">{char.display_name}</h2>
                  <p className="character-card-era">{char.era}</p>
                </div>

                <button 
                  onClick={() => handleSelect(char)}
                  className="character-card-btn"
                  aria-label={`Chọn nhân vật ${char.display_name}`}
                />
              </article>
            );
          })}
        </section>
      </div>
    </main>
  );
}
