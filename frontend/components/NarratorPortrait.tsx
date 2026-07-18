"use client";

import { useEffect, useState } from "react";

export function NarratorPortrait({ isTalking, opacity }: { isTalking: boolean; opacity: number }) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [imgFailed, setImgFailed] = useState(false);

  useEffect(() => {
    if (!isTalking) {
      setMouthOpen(false);
      return;
    }
    const interval = window.setInterval(() => setMouthOpen((v) => !v), 190);
    return () => window.clearInterval(interval);
  }, [isTalking]);

  const src = mouthOpen ? "/assets/tran_hung_dao/talking.png" : "/assets/tran_hung_dao/idle.png";

  return (
    <div 
      className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[500px] h-[75vh] flex items-end justify-center pointer-events-none transition-opacity duration-1000 z-30"
      style={{ opacity: imgFailed ? 0 : opacity }}
    >
      <img
        src={src}
        alt=""
        // Make the image darker (silhouette-like) but with intense orange drop shadow (rim light)
        className="h-full object-contain origin-bottom brightness-[0.2] contrast-[1.5] saturate-0 drop-shadow-[0_0_40px_rgba(255,85,0,0.8)]"
        style={{ animation: "epicBreath 6s ease-in-out infinite alternate" }}
        onError={() => setImgFailed(true)}
      />
      <style jsx>{`
        @keyframes epicBreath {
          0% { transform: scale(1) translateY(0); }
          100% { transform: scale(1.02) translateY(-10px); }
        }
      `}</style>
    </div>
  );
}
