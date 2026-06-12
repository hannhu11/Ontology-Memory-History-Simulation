"use client";

import { useEffect, useMemo, useState } from "react";
import type { Character, CharacterVisual, VisualEmotion } from "../types";

const STATIC_ASSETS: Record<VisualEmotion | "angry_2", string> = {
  idle: "idle.png",
  talking: "talking.png",
  thinking: "thinking.png",
  confused: "confused.png",
  happy: "happy.png",
  angry: "angry.png",
  angry_2: "angry_2.png",
  sad: "sad.png",
};

const QUANG_TRUNG_ASSETS: Record<string, string> = {
  ...STATIC_ASSETS,
  thinkingSheet: "Quang Trung-hero_thinking.png",
  attackSheet: "Quang Trung-attack.png",
};

const PRELOAD_ASSETS = Object.values(STATIC_ASSETS);

function assetUrl(characterId: string, filename: string) {
  return `/assets/${characterId}/${encodeURIComponent(filename)}`;
}

function staticAssetFor(visual: CharacterVisual) {
  if (visual.asset) return visual.asset;
  if (visual.emotion === "angry" && visual.intent === "battle_detail") return STATIC_ASSETS.angry_2;
  return STATIC_ASSETS[visual.emotion] || STATIC_ASSETS.idle;
}

function safeBaseEmotion(emotion: CharacterVisual["baseEmotion"] | VisualEmotion | undefined) {
  if (!emotion || emotion === "talking") return "idle";
  return emotion;
}

function SpriteSheet({
  src,
  loop,
  onComplete,
}: {
  src: string;
  loop: boolean;
  onComplete?: () => void;
}) {
  const columns: number = 5;
  const rows: number = 5;
  const frameCount = columns * rows;
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    setFrame(0);
    const interval = window.setInterval(() => {
      setFrame((current) => {
        const next = current + 1;
        if (next >= frameCount) {
          if (!loop) {
            window.clearInterval(interval);
            window.setTimeout(() => onComplete?.(), 560);
            return frameCount - 1;
          }
          return 0;
        }
        return next;
      });
    }, loop ? 95 : 70);
    return () => window.clearInterval(interval);
  }, [frameCount, loop, onComplete]);

  const column = frame % columns;
  const row = Math.floor(frame / columns);
  const x = columns === 1 ? 0 : (column / (columns - 1)) * 100;
  const y = rows === 1 ? 0 : (row / (rows - 1)) * 100;

  return (
    <div
      className="h-full w-full bg-no-repeat transition-opacity duration-300 ease-out"
      style={{
        backgroundImage: `url("${src}")`,
        backgroundSize: `${columns * 100}% ${rows * 100}%`,
        backgroundPosition: `${x}% ${y}%`,
      }}
      aria-hidden="true"
    />
  );
}

function StaticPortrait({
  character,
  visual,
}: {
  character: Character;
  visual: CharacterVisual;
}) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [fallbackSrc, setFallbackSrc] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const baseEmotion = safeBaseEmotion(visual.baseEmotion || visual.emotion);
  const currentAsset = useMemo(() => {
    if (visual.emotion !== "talking") return staticAssetFor(visual);
    return mouthOpen ? STATIC_ASSETS.talking : STATIC_ASSETS[baseEmotion] || STATIC_ASSETS.idle;
  }, [baseEmotion, mouthOpen, visual]);
  const primarySrc = assetUrl(character.character_id, currentAsset);

  useEffect(() => {
    if (visual.emotion !== "talking") {
      setMouthOpen(false);
      return;
    }
    const interval = window.setInterval(() => setMouthOpen((value) => !value), 180);
    return () => window.clearInterval(interval);
  }, [visual.emotion]);

  useEffect(() => {
    setFallbackSrc(null);
    setFailed(false);
  }, [primarySrc]);

  const src = fallbackSrc || primarySrc;

  if (failed) {
    return (
      <div className="flex h-full items-center justify-center text-center">
        <div>
          <div className="text-xl font-black uppercase text-[#e5bd3b]">{character.display_name}</div>
          <div className="mt-2 text-sm font-bold uppercase tracking-[.12em] text-[#e5bd3b]">Simulacra</div>
        </div>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt=""
      className="h-full w-full object-contain transition-opacity duration-300"
      draggable={false}
      onError={() => {
        const idleSrc = assetUrl(character.character_id, STATIC_ASSETS.idle);
        if (src !== idleSrc) {
          setFallbackSrc(idleSrc);
          return;
        }
        if (character.portrait_url && src !== character.portrait_url) {
          setFallbackSrc(character.portrait_url);
          return;
        }
        setFailed(true);
      }}
    />
  );
}

export function CharacterViewer({
  character,
  visual,
  onMotionComplete,
}: {
  character?: Character;
  visual: CharacterVisual;
  onMotionComplete?: () => void;
}) {
  const preloadCharacterId = character?.character_id;

  useEffect(() => {
    if (!preloadCharacterId) return;
    const images = PRELOAD_ASSETS.map((filename) => {
      const image = new Image();
      image.src = assetUrl(preloadCharacterId, filename);
      return image;
    });
    return () => images.forEach((image) => (image.src = ""));
  }, [preloadCharacterId]);

  if (!character) {
    return (
      <div className="character-frame flex items-center justify-center text-center">
        <div className="text-sm uppercase tracking-[.16em] text-[#e5bd3b]">Đang nạp nhân vật</div>
      </div>
    );
  }

  const isQuangTrung = character.character_id === "quang_trung";
  const motion = visual.motion;

  return (
    <div className="character-frame">
      <div className="character-stage">
        {isQuangTrung && motion === "thinking" ? (
          <SpriteSheet src={assetUrl(character.character_id, QUANG_TRUNG_ASSETS.thinkingSheet)} loop />
        ) : null}
        {isQuangTrung && motion === "attack" ? (
          <SpriteSheet
            src={assetUrl(character.character_id, QUANG_TRUNG_ASSETS.attackSheet)}
            loop={false}
            onComplete={onMotionComplete}
          />
        ) : null}
        {isQuangTrung && motion === "none" ? (
          <StaticPortrait character={character} visual={visual} />
        ) : null}
        {!isQuangTrung ? <StaticPortrait character={character} visual={visual} /> : null}
      </div>
      <div className="character-visual-caption">
        {visual.motion === "thinking"
          ? "Đang gợi ký ức"
          : visual.motion === "attack"
            ? "Khí thế xung trận"
            : visual.emotion === "talking"
              ? "Đang đối thoại"
              : "Trạng thái nhập vai"}
      </div>
    </div>
  );
}
