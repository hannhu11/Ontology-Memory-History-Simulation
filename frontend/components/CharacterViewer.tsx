"use client";

import { useEffect, useMemo, useState } from "react";
import type { Character, CharacterVisual, VisualEmotion } from "../types";

const QUANG_TRUNG_ASSETS: Record<string, string> = {
  idle: "idle.png",
  talking: "talking.png",
  thinking: "thinking.png",
  confused: "confused.png",
  happy: "happy.png",
  angry: "angry.png",
  angry_2: "angry_2.png",
  sad: "sad.png",
  thinkingSheet: "Quang Trung-hero_thinking.png",
  attackSheet: "Quang Trung-attack.png",
};

function assetUrl(characterId: string, filename: string) {
  return `/assets/${characterId}/${encodeURIComponent(filename)}`;
}

function staticAssetFor(visual: CharacterVisual) {
  if (visual.asset) return visual.asset;
  if (visual.emotion === "angry" && visual.intent === "battle_detail") return QUANG_TRUNG_ASSETS.angry_2;
  return QUANG_TRUNG_ASSETS[visual.emotion] || QUANG_TRUNG_ASSETS.idle;
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
            window.setTimeout(() => onComplete?.(), 120);
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
      className="h-full w-full bg-no-repeat"
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
  characterId,
  visual,
}: {
  characterId: string;
  visual: CharacterVisual;
}) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const baseEmotion = safeBaseEmotion(visual.baseEmotion || visual.emotion);
  const currentAsset = useMemo(() => {
    if (visual.emotion !== "talking") return staticAssetFor(visual);
    return mouthOpen ? QUANG_TRUNG_ASSETS.talking : QUANG_TRUNG_ASSETS[baseEmotion] || QUANG_TRUNG_ASSETS.idle;
  }, [baseEmotion, mouthOpen, visual]);

  useEffect(() => {
    if (visual.emotion !== "talking") {
      setMouthOpen(false);
      return;
    }
    const interval = window.setInterval(() => setMouthOpen((value) => !value), 180);
    return () => window.clearInterval(interval);
  }, [visual.emotion]);

  return (
    <img
      src={assetUrl(characterId, currentAsset)}
      alt=""
      className="h-full w-full object-contain transition-opacity duration-300"
      draggable={false}
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
          <StaticPortrait characterId={character.character_id} visual={visual} />
        ) : null}
        {!isQuangTrung && character.portrait_url ? (
          <img src={character.portrait_url} alt="" className="h-full w-full object-contain" draggable={false} />
        ) : null}
        {!isQuangTrung && !character.portrait_url ? (
          <div className="flex h-full items-center justify-center text-center">
            <div>
              <div className="text-xl font-black uppercase text-[#e5bd3b]">{character.display_name}</div>
              <div className="mt-2 text-sm font-bold uppercase tracking-[.12em] text-[#e5bd3b]">Simulacra</div>
            </div>
          </div>
        ) : null}
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
