export function Curtain({ isOpen }: { isOpen: boolean }) {
  // Velvet fold pattern
  const velvetFolds = "repeating-linear-gradient(to right, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 5%, rgba(0,0,0,0.3) 10%)";
  
  return (
    <div
      className="absolute inset-0 pointer-events-none z-50 flex overflow-hidden"
      aria-hidden="true"
    >
      {/* Top Drape / Valance (Yếm rèm) */}
      <svg 
        className="absolute top-0 left-0 w-full h-[15vh] transition-transform duration-[3000ms] ease-[cubic-bezier(0.4,0,0.2,1)] z-20 drop-shadow-[0_15px_15px_rgba(0,0,0,0.9)]"
        style={{ transform: isOpen ? "translateY(-100%)" : "translateY(0)" }}
        preserveAspectRatio="none"
        viewBox="0 0 100 100"
      >
        <defs>
          <linearGradient id="valance-folds" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="rgba(0,0,0,0.6)" />
            <stop offset="12.5%" stopColor="rgba(0,0,0,0)" />
            <stop offset="25%" stopColor="rgba(0,0,0,0.6)" />
            <stop offset="37.5%" stopColor="rgba(0,0,0,0)" />
            <stop offset="50%" stopColor="rgba(0,0,0,0.6)" />
            <stop offset="62.5%" stopColor="rgba(0,0,0,0)" />
            <stop offset="75%" stopColor="rgba(0,0,0,0.6)" />
            <stop offset="87.5%" stopColor="rgba(0,0,0,0)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.6)" />
          </linearGradient>
        </defs>
        <path d="M0,0 L100,0 L100,60 Q87.5,100 75,60 Q62.5,20 50,60 Q37.5,100 25,60 Q12.5,20 0,60 Z" fill="#9d3127" />
        <path d="M0,0 L100,0 L100,60 Q87.5,100 75,60 Q62.5,20 50,60 Q37.5,100 25,60 Q12.5,20 0,60 Z" fill="url(#valance-folds)" />
        {/* Gold trim */}
        <path d="M0,60 Q12.5,20 25,60 Q37.5,100 50,60 Q62.5,20 75,60 Q87.5,100 100,60" stroke="#d4af37" strokeWidth="3" fill="none" />
      </svg>

      <div
        className="w-1/2 h-full origin-left transition-transform duration-[3000ms] ease-[cubic-bezier(0.4,0,0.2,1)] z-10"
        style={{
          transform: isOpen ? "scaleX(0)" : "scaleX(1)",
          background: "#9d3127",
          backgroundImage: `linear-gradient(90deg, transparent 85%, rgba(0,0,0,0.8) 100%), ${velvetFolds}`,
          boxShadow: isOpen ? "none" : "15px 0 30px rgba(0,0,0,0.9)"
        }}
      >
        {/* Tassel (Tua rua) */}
        <div className="absolute top-0 right-0 h-full w-[25px] bg-gradient-to-r from-[#805e11] via-[#d4af37] to-[#805e11]">
           <div className="w-full h-full opacity-40" style={{ backgroundImage: "repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, rgba(0,0,0,1) 3px, rgba(0,0,0,1) 4px)" }} />
        </div>
      </div>

      <div
        className="w-1/2 h-full origin-right transition-transform duration-[3000ms] ease-[cubic-bezier(0.4,0,0.2,1)] z-10"
        style={{
          transform: isOpen ? "scaleX(0)" : "scaleX(1)",
          background: "#9d3127",
          backgroundImage: `linear-gradient(270deg, transparent 85%, rgba(0,0,0,0.8) 100%), ${velvetFolds}`,
          boxShadow: isOpen ? "none" : "-15px 0 30px rgba(0,0,0,0.9)"
        }}
      >
        {/* Tassel (Tua rua) */}
        <div className="absolute top-0 left-0 h-full w-[25px] bg-gradient-to-r from-[#805e11] via-[#d4af37] to-[#805e11]">
           <div className="w-full h-full opacity-40" style={{ backgroundImage: "repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, rgba(0,0,0,1) 3px, rgba(0,0,0,1) 4px)" }} />
        </div>
      </div>
    </div>
  );
}
