export function CinematicOverlay({ sceneIndex }: { sceneIndex: number }) {
  return (
    <div className="absolute inset-0 pointer-events-none z-40 overflow-hidden mix-blend-overlay">
      {/* Heavy Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,rgba(5,4,3,0.95)_100%)]" />
      
      {/* Film grain noise */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.15]">
        <filter id="noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="4" stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter="url(#noise)" />
      </svg>
      
      {/* Rolling Smoke Overlay */}
      <svg className="absolute inset-0 w-full h-full opacity-30 mix-blend-color-dodge">
        <filter id="smoke">
          <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="3" result="noise">
            <animate attributeName="baseFrequency" values="0.01; 0.015; 0.01" dur="20s" repeatCount="indefinite" />
          </feTurbulence>
          <feColorMatrix type="matrix" values="1 0 0 0 0  0 0.5 0 0 0  0 0 0 0 0  0 0 0 3 -1" />
        </filter>
        <rect width="100%" height="100%" filter="url(#smoke)" fill="#ffaa00" />
      </svg>

      {/* Epic Flying Embers */}
      <div className="absolute inset-0 overflow-hidden mix-blend-screen opacity-100">
         {[...Array(40)].map((_, i) => {
            const size = Math.random() * 6 + 2;
            const duration = Math.random() * 5 + 3;
            const delay = -(Math.random() * 5);
            return (
              <div 
                key={i} 
                className="absolute rounded-full bg-[#ffea00]"
                style={{
                  width: `${size}px`,
                  height: `${size}px`,
                  left: `${Math.random() * 100}%`,
                  bottom: `-10px`,
                  boxShadow: `0 0 ${size * 3}px #ff5500, 0 0 ${size * 6}px #ff0000`,
                  animation: `emberRise ${duration}s ease-in infinite`,
                  animationDelay: `${delay}s`
                }}
              />
            );
         })}
      </div>

      <style jsx>{`
        @keyframes emberRise {
          0% { transform: translate(0, 0) scale(1); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; transform: translate(${Math.random() > 0.5 ? '' : '-'}${Math.random() * 200 + 50}px, -80vh) scale(0.5); }
          100% { transform: translate(${Math.random() > 0.5 ? '' : '-'}${Math.random() * 300 + 100}px, -100vh) scale(0); opacity: 0; }
        }
      `}</style>
    </div>
  );
}
