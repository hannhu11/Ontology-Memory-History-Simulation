"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import { TRAN_HUNG_DAO_INTRO } from "./tranHungDaoScript";
import { Curtain } from "./Curtain";
import { WaterStage } from "./WaterStage";
import { NarratorPortrait } from "./NarratorPortrait";
import { CinematicOverlay } from "./CinematicOverlay";

export function TranQuocTuanIntro({ onComplete }: { onComplete: () => void }) {
  const [sceneIndex, setSceneIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const requestRef = useRef<number | null>(null);
  
  const [stage, setStage] = useState<'IDLE' | 'OPENING' | 'PLAYING' | 'FINISHED'>('IDLE');
  const [showStartButton, setShowStartButton] = useState(false);
  const [audioDuration, setAudioDuration] = useState<number>(60);

  // Tự động chia thời lượng cảnh dựa trên số lượng từ (word count)
  const dynamicScenes = useMemo(() => {
    const D = audioDuration;
    return [
      { ...TRAN_HUNG_DAO_INTRO[0], startTime: -3, duration: 3 }, // Rèm mở
      { ...TRAN_HUNG_DAO_INTRO[1], startTime: 0, duration: D * 0.20 },
      { ...TRAN_HUNG_DAO_INTRO[2], startTime: D * 0.20, duration: D * 0.16 },
      { ...TRAN_HUNG_DAO_INTRO[3], startTime: D * 0.36, duration: D * 0.39 },
      { ...TRAN_HUNG_DAO_INTRO[4], startTime: D * 0.75, duration: D * 0.25 },
      { ...TRAN_HUNG_DAO_INTRO[5], startTime: D, duration: 4 }
    ];
  }, [audioDuration]);

  // Lấy thời lượng thực tế của file Audio
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const handleLoadedMetadata = () => {
      if (audio.duration && audio.duration !== Infinity) {
        setAudioDuration(audio.duration);
      }
    };
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    if (audio.readyState >= 1) handleLoadedMetadata();
    return () => audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
  }, []);

  // Bước 1: Kiểm tra Autoplay khi mới vào
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    // Thử play để xem trình duyệt có chặn không
    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        // Trình duyệt cho phép -> Tạm dừng, reset về 0 và bắt đầu mở rèm
        audio.pause();
        audio.currentTime = 0;
        setStage('OPENING');
      }).catch(error => {
        // Trình duyệt chặn -> Hiện nút Bắt đầu
        console.log("Autoplay blocked, showing button", error);
        setShowStartButton(true);
      });
    }
  }, []);

  // Hàm xử lý khi bấm nút "Bắt đầu"
  const handleStart = () => {
    setShowStartButton(false);
    const audio = audioRef.current;
    if (audio) {
       // Phát audio để "mở khóa" quyền phát của trình duyệt, sau đó dừng lại ngay
       audio.play().then(() => {
         audio.pause();
         audio.currentTime = 0;
         setStage('OPENING');
       }).catch(e => {
         console.error(e);
         setStage('OPENING'); // Cứ tiếp tục dù lỗi
       });
    } else {
       setStage('OPENING');
    }
  };

  // Bước 2: Quá trình mở rèm (3 giây)
  useEffect(() => {
    if (stage === 'OPENING') {
      const timer = setTimeout(() => {
        setStage('PLAYING');
      }, 3000); // Đợi 3 giây cho rèm mở xong
      return () => clearTimeout(timer);
    }
  }, [stage]);

  // Bước 3: Vòng lặp Animation đồng bộ với Audio
  useEffect(() => {
    if (stage !== 'PLAYING') return;
    
    const audio = audioRef.current;
    if (!audio) return;

    audio.play().catch(e => console.log("Play prevented in PLAYING stage", e));

    const animate = () => {
      const time = audio.currentTime;
      
      let currentIdx = dynamicScenes.findIndex(s => time >= s.startTime && time < (s.startTime + s.duration));
      
      if (currentIdx === -1) {
        if (time >= dynamicScenes[dynamicScenes.length - 1].startTime) {
           if (audio.ended || time >= audioDuration) {
             setStage('FINISHED');
             setTimeout(() => onComplete(), 1000);
             return;
           }
           currentIdx = dynamicScenes.length - 1;
        } else {
           currentIdx = 1; // Mặc định về cảnh 1 vì cảnh 0 đã qua
        }
      }

      // Không bao giờ lùi về cảnh 0 (Rèm mở) khi đang PLAYING
      if (currentIdx === 0) currentIdx = 1;

      setSceneIndex(currentIdx);
      
      const currentScene = dynamicScenes[currentIdx];
      const elapsed = time - currentScene.startTime;
      setProgress(Math.min(1, Math.max(0, elapsed / currentScene.duration)));

      requestRef.current = requestAnimationFrame(animate);
    };

    requestRef.current = requestAnimationFrame(animate);

    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
      audio.pause();
    };
  }, [stage, onComplete, dynamicScenes, audioDuration]);

  // Render logic
  const isCurtainOpen = stage === 'OPENING' || stage === 'PLAYING';
  
  // Chỉ khi vào PLAYING (rèm đã mở xong) mới lấy cảnh hiện tại, nếu đang OPENING thì chưa có text
  const currentScene = stage === 'PLAYING' ? (dynamicScenes[sceneIndex] || dynamicScenes[1]) : dynamicScenes[0];
  
  const isNarratorVisible = stage === 'PLAYING' && (sceneIndex === 1 || sceneIndex === 2 || sceneIndex === 4);
  const isTalking = stage === 'PLAYING' && progress > 0.05 && progress < 0.95 && currentScene.line.length > 0;
  
  const showCaption = stage === 'PLAYING' && sceneIndex > 0 && sceneIndex < dynamicScenes.length - 1;

  return (
    <div className="relative w-full h-full bg-[#050403] overflow-hidden text-white select-none">
      <audio ref={audioRef} src="/speech_intro_tran_quoc_tuan.mp3" preload="auto" />
      <CinematicOverlay sceneIndex={sceneIndex} />
      <Curtain isOpen={isCurtainOpen} />
      <WaterStage sceneId={currentScene.id} progress={progress} />
      <NarratorPortrait isTalking={isTalking} opacity={isNarratorVisible ? 1 : 0} />
      
      {showStartButton && stage === 'IDLE' && (
        <div className="absolute inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <button 
            onClick={handleStart}
            className="px-10 py-4 border-2 border-[#d4af37] text-[#d4af37] font-bold text-2xl uppercase tracking-widest hover:bg-[#d4af37] hover:text-[#050403] transition-all duration-300 shadow-[0_0_20px_rgba(212,175,55,0.4)] hover:shadow-[0_0_40px_rgba(212,175,55,0.8)] rounded-sm"
          >
            Bắt đầu trải nghiệm
          </button>
        </div>
      )}

      {/* Caption container */}
      <div className="absolute bottom-[8%] left-1/2 -translate-x-1/2 w-[90%] max-w-4xl text-center z-50 pointer-events-none">
        {showCaption && (
          <>
            <h2 className="text-2xl md:text-3xl font-black uppercase tracking-[0.2em] text-[#ffea00] mb-6 drop-shadow-[0_0_15px_rgba(255,85,0,0.9)]"
                style={{ textShadow: "0 5px 15px #050403, 0 0 20px #ff5500" }}>
              {currentScene.label.normalize('NFC')}
            </h2>
            <p className="text-xl md:text-3xl font-sans font-semibold text-white leading-relaxed transition-all duration-[1500ms]"
               style={{ 
                 opacity: isTalking ? 1 : 0,
                 transform: isTalking ? "translateY(0) scale(1)" : "translateY(20px) scale(0.95)",
                 textShadow: "0 4px 20px rgba(5,4,3,1), 0 2px 5px rgba(5,4,3,1), 0 0 30px rgba(255,85,0,0.6)"
               }}>
              {currentScene.line.normalize('NFC')}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
