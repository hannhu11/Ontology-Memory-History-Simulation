"use client";

export function WaterStage({ sceneId, progress }: { sceneId: string; progress: number }) {
  const isScene1 = sceneId === "scene_1";
  const isScene2 = sceneId === "scene_2";
  const isScene3 = sceneId === "scene_3";
  const isScene4 = sceneId === "scene_4";

  if (!isScene1 && !isScene2 && !isScene3 && !isScene4) return null;

  let bgGradient = "";
  if (isScene1) {
    // Trời đang xanh trong thì bị mây đen và sắc đỏ máu từ phương Bắc tràn xuống
    bgGradient = "linear-gradient(180deg, #1a0000 0%, #3a1c11 40%, #112230 80%, #050403 100%)";
  } else if (isScene2) {
    bgGradient = "radial-gradient(circle at 50% 85%, #ffe600 0%, #ff5500 40%, #990000 75%, #110000 100%)";
  } else if (isScene3) {
    bgGradient = "radial-gradient(circle at 50% 85%, #ff2a00 0%, #990000 40%, #330000 75%, #050403 100%)";
  } else if (isScene4) {
    // Bình minh rực rỡ, non sông gấm vóc
    bgGradient = "linear-gradient(0deg, #ff8c00 0%, #ffc03a 30%, #4da6ff 80%, #004488 100%)";
  }

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-end overflow-hidden pointer-events-none">
      {/* Dynamic Background */}
      <div 
        className="absolute inset-0 transition-all duration-[3000ms] ease-in-out"
        style={{
          background: bgGradient,
          animation: isScene2 || isScene3 ? "firePulse 4s infinite alternate ease-in-out" : "none",
          opacity: progress < 0.05 ? progress * 20 : progress > 0.95 ? (1 - progress) * 20 : 1
        }}
      />

      {/* Common Ground */}
      <div className="absolute bottom-0 left-0 w-full h-[35%] bg-gradient-to-t from-[#050403] via-[rgba(5,4,3,0.9)] to-transparent z-0 transition-opacity duration-1000" />

      <svg width="0" height="0">
        <defs>
          <filter id="flag-wind">
            <feTurbulence type="fractalNoise" baseFrequency="0.015 0.08" numOctaves="3" result="noise">
              <animate attributeName="baseFrequency" values="0.015 0.08; 0.03 0.12; 0.015 0.08" dur="2s" repeatCount="indefinite" />
            </feTurbulence>
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="20" />
          </filter>
        </defs>
      </svg>

      {/* SCENE 1: Họa Xâm Lăng (Mongol Threat over Dai Viet) */}
      {isScene1 && (
        <div className="absolute inset-0 flex items-end justify-center z-10">
           
           {/* Bầu trời vần vũ mây đen sấm chớp từ phía Bắc */}
           <div className="absolute top-0 left-0 w-full h-[60%] z-0" style={{ animation: "stormClouds 20s linear infinite" }}>
             <svg viewBox="0 0 800 300" fill="#000" className="w-[150%] h-full opacity-60">
               <path d="M0,100 Q100,50 200,120 T400,100 T600,150 T800,80 L800,0 L0,0 Z" />
               <path d="M-100,150 Q100,80 200,180 T500,150 T800,200 T1000,120 L1000,0 L-100,0 Z" opacity="0.5" />
             </svg>
           </div>
           {/* Tia chớp */}
           <div className="absolute top-[20%] right-[30%] w-[100px] h-[200px] opacity-0 z-0" style={{ animation: "lightning 6s infinite" }}>
              <svg viewBox="0 0 50 100" fill="#fff" className="drop-shadow-[0_0_10px_#fff]">
                 <path d="M30,0 L0,50 L20,50 L10,100 L50,40 L30,40 Z" />
              </svg>
           </div>

           {/* Bóng dáng kỵ binh Nguyên Mông tràn xuống từ đồi cao */}
           <div className="absolute bottom-[20%] right-[-10%] w-[80%] h-[40%] opacity-80 z-10" style={{ transform: `translateX(-${progress*10}%)` }}>
             <svg viewBox="0 0 800 300" fill="#050403" className="w-full h-full drop-shadow-[0_0_15px_rgba(255,0,0,0.3)]">
                {/* Đồi núi Bắc */}
                <path d="M100,300 L900,300 L900,150 Q700,100 400,180 Q200,220 0,300 Z" />
                {/* Đạo quân Kỵ binh */}
                {[...Array(8)].map((_, i) => (
                  <g key={`mongol-${i}`} transform={`translate(${600 - i*70}, ${110 + i*12}) scale(${0.8 + Math.random()*0.4})`}>
                    <path d="M0,50 L10,30 Q20,20 40,30 L50,50 Z" /> {/* Thân ngựa */}
                    <circle cx="5" cy="40" r="10" /> {/* Đầu ngựa */}
                    <path d="M25,30 L20,10 L30,5 L35,25 Z" /> {/* Kỵ sĩ */}
                    <path d="M25,15 Q35,-10 50,-20 M25,15 Q30,-10 40,-20" stroke="#050403" strokeWidth="2" fill="none" /> {/* Mũ lông / cờ tuế */}
                    <path d="M25,20 C10,0 50,0 35,20" stroke="#050403" strokeWidth="3" fill="none" /> {/* Cung sừng */}
                  </g>
                ))}
                {/* Cờ xí giặc */}
                <path d="M700,100 L705,30 L650,40 L690,60 L640,70 L700,90" stroke="#050403" strokeWidth="2" />
                <path d="M500,150 L505,80 L450,90 L490,110 L440,120 L500,140" stroke="#050403" strokeWidth="2" />
             </svg>
           </div>

           {/* Làng quê Đại Việt ở tiền cảnh, mong manh dưới bóng tối */}
           <div className="absolute bottom-[0%] left-[-5%] w-[60%] h-[30%] opacity-95 z-20">
             <svg viewBox="0 0 600 200" fill="#050403" className="w-full h-full">
                {/* Lũy tre ngà gập mình trong gió */}
                {[...Array(12)].map((_, i) => (
                  <path key={`bamboo-${i}`} d={`M${50 + i*40},200 Q${100 + i*45},100 ${150 + i*50},0`} stroke="#050403" strokeWidth={5 + Math.random()*5} fill="none" style={{ animation: "bambooSway 3s infinite alternate ease-in-out", transformOrigin: `${50+i*40}px 200px` }} />
                ))}
                {/* Cổng làng cổ kính */}
                <rect x="250" y="100" width="20" height="100" />
                <rect x="350" y="100" width="20" height="100" />
                <path d="M230,100 L390,100 L310,50 Z" />
                <path d="M240,110 L380,110 L310,65 Z" fill="#2a4b5c" opacity="0.3" />
                {/* Mái tranh nhỏ */}
                <path d="M50,150 L150,150 L100,100 Z" />
                <path d="M120,160 L220,160 L170,110 Z" />
             </svg>
           </div>
        </div>
      )}

      {/* SCENE 2: The Army (Vạn Kiếp) */}
      {isScene2 && (
        <div className="absolute bottom-0 left-0 w-full h-[70%] flex items-end justify-center z-10">
          <div className="absolute bottom-[20%] w-[120%] flex justify-between items-end z-10" style={{ filter: "url(#flag-wind)" }}>
             {[...Array(6)].map((_, i) => {
               const height = 150 + Math.random() * 200;
               return (
                 <div key={`fg-flag-${i}`} className="relative flex flex-col items-center origin-bottom drop-shadow-[0_0_15px_rgba(255,100,0,0.5)]" style={{ transform: `scale(${1 + Math.random()*0.5})` }}>
                    <div className="w-[6px] bg-[#050403]" style={{ height: `${height + 50}px` }} />
                    <svg className="absolute top-0 left-1 w-32 h-64" viewBox="0 0 100 200" fill="#050403">
                      {/* Chữ Hán/Nôm "Trần" hoặc "Sát Thát" trên cờ */}
                      <path d="M0,0 Q50,20 90,10 Q80,40 95,50 Q60,70 85,80 Q50,110 75,130 Q30,150 50,190 Q20,180 0,200 Z" />
                      <path d="M30,50 L70,50 M50,30 L50,150 M40,80 L60,80" stroke="#ffaa00" strokeWidth="4" opacity="0.6" fill="none" />
                    </svg>
                 </div>
               );
             })}
          </div>
          <div className="absolute bottom-0 w-full flex justify-between px-2 items-end z-10 opacity-80" style={{ animation: "marchBob 1.5s infinite alternate ease-in-out" }}>
            {[...Array(35)].map((_, i) => (
               <div key={`spear-${i}`} className="w-[3px] bg-[#050403]" style={{ height: `${Math.random()*150 + 150}px`, transform: `rotate(${(Math.random()-0.5)*20}deg)` }} />
            ))}
          </div>
          <div className="absolute bottom-[-5%] w-[110%] h-[50%] flex justify-between items-end z-20">
             {[...Array(10)].map((_, i) => (
               <div key={`horse-${i}`} className="relative h-full" style={{ width: '12%', transform: `scale(${0.9 + Math.random()*0.4}) translateY(${Math.random()*30}px)`, animation: `marchBob ${1 + Math.random()*0.5}s infinite alternate ease-in-out`, animationDelay: `${Math.random()}s` }}>
                 <svg viewBox="0 0 100 150" fill="#050403" preserveAspectRatio="xMidYMax meet" className="w-full h-full drop-shadow-[0_0_20px_rgba(255,50,0,0.6)]">
                    <rect x="75" y="10" width="3" height="140" />
                    <path d="M72,10 L76,0 L79,10 Z" />
                    <path d="M20,150 L30,90 Q40,65 60,90 L70,150 Z" />
                    <circle cx="45" cy="55" r="14" />
                    <path d="M25,50 Q45,20 65,50 L70,60 L20,60 Z" />
                    <ellipse cx="40" cy="110" rx="25" ry="35" />
                 </svg>
               </div>
             ))}
          </div>
        </div>
      )}

      {/* SCENE 3: Bạch Đằng (Spikes, Boats, Arrows) */}
      {isScene3 && (
        <div className="absolute bottom-0 left-0 w-full h-[70%] z-10">
          <div className="absolute inset-0 overflow-hidden z-0">
             {[...Array(40)].map((_, i) => (
               <div key={`arrow-${i}`} className="absolute bg-[#050403]"
                    style={{
                      width: '50px', height: '2px', left: '-50px', top: `${Math.random() * 60}%`,
                      transform: 'rotate(15deg)', animation: `arrowFly ${0.8 + Math.random()}s linear infinite`,
                      animationDelay: `${Math.random() * 4}s`, opacity: progress > 0.1 && progress < 0.85 ? 0.8 : 0
                    }} />
             ))}
          </div>
          <div className="absolute bottom-0 w-full flex justify-between px-[5%] items-end z-10">
            {[...Array(25)].map((_, i) => {
              let ty = 100;
              if (progress > 0.3) {
                const phaseProgress = Math.min(1, (progress - 0.3) / 0.2);
                const stagger = (i % 5) * 0.05;
                const adjustedProgress = Math.max(0, Math.min(1, (phaseProgress - stagger) / 0.5));
                ty = 100 - adjustedProgress * 100;
              }
              const height = 200 + (i % 4) * 60;
              return (
                 <div key={`spike-${i}`} className="relative flex justify-center items-end"
                      style={{ transform: `translateY(${ty}%) rotate(${(i%5 - 2)*12}deg)` }}>
                    <svg width="40" height={height} viewBox={`0 0 30 ${height}`} fill="#050403" className="drop-shadow-[0_0_20px_rgba(255,0,0,0.8)]">
                      <path d={`M5,${height} L25,${height} L20,40 L15,0 L10,40 Z`} />
                      <path d="M10,40 L15,0 L20,40 Z" fill="#4a0000" />
                    </svg>
                 </div>
              );
            })}
          </div>
          <div className="absolute bottom-[5%] w-full flex justify-center items-end z-20 transition-all duration-[2000ms] ease-in-out"
               style={{
                 transform: progress < 0.2 ? `translateX(${progress*100 - 50}vw)` : 
                            progress < 0.5 ? `translateX(${10 + (progress-0.2)*30}vw)` : 
                            `translateX(25vw) rotate(${progress > 0.5 ? 20 : 0}deg) translateY(${progress > 0.5 ? 120 : 0}px)`,
                 opacity: progress > 0.8 ? 1 - (progress-0.8)*5 : 1
               }}>
            {[1, 2].map(i => (
               <svg key={`big-boat-${i}`} width="500" height="350" viewBox="0 0 400 300" fill="#050403" 
                    className="drop-shadow-[0_0_40px_rgba(255,0,0,0.9)]"
                    style={{ transform: `scale(${i === 1 ? 1 : 0.6}) translateX(${i === 2 ? '-300px' : '0'}) rotate(${i === 1 ? 10 : -5}deg)` }}>
                  <path d="M20,200 L380,200 L320,280 L80,280 Z" />
                  <rect x="200" y="40" width="12" height="160" transform="rotate(15 200 200)" />
                  <rect x="100" y="80" width="10" height="120" transform="rotate(-20 100 200)" />
                  <path d="M170,50 Q250,100 190,150 Q160,120 170,50 Z" opacity="0.8" />
                  <path d="M80,80 Q130,120 90,160 Q60,140 80,80 Z" opacity="0.6" />
                  <path d="M140,160 L280,160 L270,120 L150,120 Z" />
                  <path d="M150,120 L270,120 L260,80 L160,80 Z" />
                  <path d="M130,120 L290,120 L280,100 L140,100 Z" />
                  <path d="M140,80 L280,80 L270,60 L150,60 Z" />
                  <rect x="350" y="210" width="40" height="8" transform="rotate(45)" fill="#050403" />
                  <rect x="40" y="180" width="50" height="10" transform="rotate(-30)" fill="#050403" />
                  <rect x="280" y="240" width="30" height="6" transform="rotate(15)" fill="#050403" />
                  <path d="M30,180 L360,180" stroke="#ff0000" strokeWidth="4" opacity="0.7" />
               </svg>
            ))}
          </div>
        </div>
      )}

      {/* SCENE 4: Di Sản (Hào Khí Đông A - Tran Hung Dao Silhouette & Binh Thu Yeu Luoc) */}
      {isScene4 && (
        <div className="absolute inset-0 z-10 flex items-end justify-center">
           
           {/* Non sông gấm vóc (Vịnh Hạ Long / Núi non hùng vĩ) ở Hậu cảnh */}
           <div className="absolute bottom-[20%] w-[120%] h-[40%] z-0 opacity-40">
             <svg viewBox="0 0 1000 300" fill="#002244" className="w-full h-full drop-shadow-[0_0_20px_rgba(0,100,255,0.4)]">
                <path d="M0,300 L200,100 L300,200 L450,50 L600,250 L800,80 L1000,300 Z" />
                <path d="M-100,300 L150,150 L250,250 L350,100 L550,280 L750,120 L1100,300 Z" opacity="0.6" fill="#001122" />
             </svg>
           </div>

           {/* Ánh sáng bình minh (Sunrise rays) rọi từ sau núi */}
           <div className="absolute top-[20%] left-1/2 -translate-x-1/2 w-[100%] h-[100%] pointer-events-none mix-blend-screen z-0"
                style={{
                  background: "conic-gradient(from 180deg at 50% 100%, rgba(255,200,50,0) 0deg, rgba(255,220,100,0.2) 20deg, rgba(255,200,50,0) 40deg, rgba(255,220,100,0.2) 60deg, rgba(255,200,50,0) 80deg)",
                  animation: "rayRotate 15s infinite alternate ease-in-out"
                }} />

           {/* Cuộn giấy cổ "Binh Thư Yếu Lược / Hịch Tướng Sĩ" bung mở trên bầu trời */}
           <div className="absolute top-[10%] w-[60%] h-[50%] z-10 opacity-70 drop-shadow-[0_0_15px_rgba(255,200,50,0.6)]" style={{ transform: `scale(${0.8 + progress*0.2}) translateY(-${progress*20}px)` }}>
              <svg viewBox="0 0 500 400" className="w-full h-full">
                 {/* Cuộn giấy bay */}
                 <path d="M100,350 Q150,200 300,150 T450,50" stroke="#ffaa00" strokeWidth="60" fill="none" opacity="0.3" strokeLinecap="round" />
                 <path d="M100,350 Q150,200 300,150 T450,50" stroke="#ffea00" strokeWidth="58" fill="none" opacity="0.4" strokeLinecap="round" />
                 {/* Chữ Hán/Nôm phát sáng trên cuộn giấy */}
                 <path d="M150,270 L170,270 M160,260 L160,280 M220,220 L240,210 M320,130 L340,120" stroke="#050403" strokeWidth="4" opacity="0.8" />
                 <path d="M180,250 L200,240 M260,190 L280,180 M380,90 L400,80" stroke="#050403" strokeWidth="4" opacity="0.8" />
              </svg>
           </div>
           
           {/* Hào khí Đông A - Tượng đài Trần Hưng Đạo kiêu hãnh */}
           <div className="absolute bottom-[5%] z-20 w-[60%] md:w-[40%] h-[80%] flex items-end justify-center drop-shadow-[0_0_30px_rgba(255,150,0,0.5)]">
             <svg viewBox="0 0 400 600" fill="#050403" className="w-full h-full max-h-[90vh]">
               {/* Bệ đá vững chãi */}
               <path d="M100,600 L300,600 L280,500 L120,500 Z" />
               <path d="M80,500 L320,500 L300,450 L100,450 Z" />
               {/* Áo choàng bay trong gió (Cape) */}
               <path d="M160,200 Q50,300 20,500 Q150,480 200,450 Z" style={{ animation: "capeFlutter 3s infinite alternate ease-in-out" }} />
               {/* Thân người vạm vỡ, bọc giáp */}
               <path d="M150,450 L250,450 L260,250 L140,250 Z" />
               {/* Chân / thế đứng uy nghi */}
               <path d="M150,450 L120,600 L160,600 L190,450 Z" />
               <path d="M250,450 L280,600 L240,600 L210,450 Z" />
               {/* Vai và Mũ trụ (Helmet) */}
               <path d="M120,250 L280,250 L250,180 L150,180 Z" />
               <path d="M180,180 L220,180 L200,130 Z" /> {/* Chóp mũ */}
               {/* Tay trái cầm Binh thư (Scroll) */}
               <path d="M140,250 Q100,300 120,350 L140,360 L160,250 Z" />
               <rect x="90" y="340" width="40" height="80" transform="rotate(15 90 340)" />
               {/* Tay phải chỉ gươm xuống biển / Về phía chân trời */}
               <path d="M260,250 Q320,280 340,320 L320,340 L250,280 Z" />
               <path d="M330,320 L400,420" stroke="#050403" strokeWidth="8" strokeLinecap="round" /> {/* Thanh gươm dài */}
             </svg>
           </div>

           {/* Hạt linh khí (Glowing Spirit Particles) bay lên từ mặt đất */}
           <div className="absolute inset-0 pointer-events-none z-30">
             {[...Array(30)].map((_, i) => {
               const left = 20 + Math.random()*60;
               return (
                 <div key={`spirit-${i}`} className="absolute w-2 h-2 bg-[#ffea00] rounded-full"
                      style={{
                        left: `${left}%`, bottom: '0%',
                        animation: `spiritRise ${3 + Math.random()*4}s infinite linear`,
                        animationDelay: `${Math.random()*5}s`,
                        boxShadow: "0 0 15px 4px rgba(255,234,0,0.8)"
                      }} />
               );
             })}
           </div>

        </div>
      )}

      <style jsx>{`
        @keyframes firePulse {
          0% { filter: brightness(1); transform: scale(1); }
          100% { filter: brightness(1.1); transform: scale(1.02); }
        }
        @keyframes marchBob {
          0% { transform: translateY(0); }
          100% { transform: translateY(12px); }
        }
        @keyframes arrowFly {
          0% { transform: translate(0, 0) rotate(15deg); }
          100% { transform: translate(120vw, 30vh) rotate(15deg); }
        }
        @keyframes stormClouds {
          0% { transform: translateX(0); }
          100% { transform: translateX(-20%); }
        }
        @keyframes lightning {
          0%, 95%, 98%, 100% { opacity: 0; }
          96%, 99% { opacity: 1; transform: scale(1.1); }
        }
        @keyframes bambooSway {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(-15deg); }
        }
        @keyframes rayRotate {
          0% { transform: rotate(-10deg); opacity: 0.5; }
          100% { transform: rotate(10deg); opacity: 1; }
        }
        @keyframes capeFlutter {
          0% { transform: scaleX(1) skewX(0deg); }
          100% { transform: scaleX(1.1) skewX(-5deg); }
        }
        @keyframes spiritRise {
          0% { transform: translateY(0) scale(1); opacity: 1; }
          100% { transform: translateY(-80vh) scale(0); opacity: 0; }
        }
      `}</style>
    </div>
  );
}
