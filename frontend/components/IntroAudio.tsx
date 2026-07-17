"use client";

import { useEffect, useRef, useCallback } from "react";

// ─── Audio Engine Hook ─────────────────────────────────────────────
export function useIntroAudio() {
  const ctxRef = useRef<AudioContext | null>(null);
  const masterGainRef = useRef<GainNode | null>(null);
  const droneRef = useRef<OscillatorNode | null>(null);
  const drumIntervalRef = useRef<number | null>(null);
  const activeChapterRef = useRef(0);

  const voiceoverRef = useRef<HTMLAudioElement | null>(null);

  // ─── Initialize audio context ────────────────────────────────────
  const initAudio = useCallback(() => {
    if (ctxRef.current) return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      ctxRef.current = ctx;

      // Initialize voiceover Audio element
      if (typeof window !== "undefined" && !voiceoverRef.current) {
        voiceoverRef.current = new Audio("/vua_quang_trung.mp3");
        voiceoverRef.current.volume = 0.95;
      }

      // Master gain
      const masterGain = ctx.createGain();
      masterGain.gain.setValueAtTime(0.01, ctx.currentTime);
      masterGain.gain.linearRampToValueAtTime(0.6, ctx.currentTime + 2);
      masterGain.connect(ctx.destination);
      masterGainRef.current = masterGain;

      // ── Deep drone pad (ambient) ────────────────────────
      const drone = ctx.createOscillator();
      const droneGain = ctx.createGain();
      const droneFilter = ctx.createBiquadFilter();
      drone.type = "sawtooth";
      drone.frequency.setValueAtTime(48.99, ctx.currentTime);
      droneFilter.type = "lowpass";
      droneFilter.frequency.setValueAtTime(80, ctx.currentTime);
      drone.connect(droneFilter);
      droneFilter.connect(droneGain);
      droneGain.gain.setValueAtTime(0.15, ctx.currentTime);
      droneGain.connect(masterGain);
      drone.start();
      droneRef.current = drone;

      // ── Đàn bầu (monochord) — higher sine oscillator ───
      const danBau = ctx.createOscillator();
      const danBauGain = ctx.createGain();
      const danBauFilter = ctx.createBiquadFilter();
      danBau.type = "sine";
      danBau.frequency.setValueAtTime(220, ctx.currentTime);
      danBauFilter.type = "lowpass";
      danBauFilter.frequency.setValueAtTime(400, ctx.currentTime);
      danBauGain.gain.setValueAtTime(0, ctx.currentTime);
      danBau.connect(danBauFilter);
      danBauFilter.connect(danBauGain);
      danBauGain.connect(masterGain);
      danBau.start();

      // Đàn bầu melody — vibrato on random intervals
      const melodyLoop = () => {
        const ch = activeChapterRef.current;
        if (ch <= 2) {
          const notes = [220, 261.6, 293.7, 329.6, 392, 440];
          const note = notes[Math.floor(Math.random() * notes.length)];
          const now = ctx.currentTime;
          danBau.frequency.setValueAtTime(note, now);
          danBau.frequency.linearRampToValueAtTime(note * (1 + Math.random() * 0.05), now + 0.8);
          danBauGain.gain.setValueAtTime(0.06, now);
          danBauGain.gain.linearRampToValueAtTime(0, now + 2.5);
        }
        setTimeout(melodyLoop, 3000 + Math.random() * 4000);
      };
      setTimeout(melodyLoop, 2000);

      // ── War drums loop (intensity scales with chapter) ──
      const drumLoop = () => {
        const ch = activeChapterRef.current;
        const intensity = ch <= 1 ? 0.15 : ch <= 3 ? 0.3 : ch === 4 ? 0.5 : 0.2;
        const tempo = ch === 4 ? 800 : ch >= 3 ? 1100 : 1600;

        const playDrum = (freq: number, vol: number, decay: number) => {
          try {
            const osc = ctx.createOscillator();
            const g = ctx.createGain();
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(0.01, ctx.currentTime + decay);
            g.gain.setValueAtTime(vol * intensity, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + decay);
            osc.connect(g);
            g.connect(masterGain);
            osc.start();
            osc.stop(ctx.currentTime + decay);
          } catch (e) {}
        };

        if (Math.random() > 0.3) {
          playDrum(65, 0.5, 0.5);
          setTimeout(() => playDrum(55, 0.4, 0.4), 180);
        } else {
          playDrum(75, 0.55, 0.6);
          setTimeout(() => playDrum(60, 0.35, 0.3), 130);
          setTimeout(() => playDrum(50, 0.3, 0.3), 260);
        }

        drumIntervalRef.current = window.setTimeout(drumLoop, tempo);
      };
      setTimeout(drumLoop, 1000);
    } catch (e) {
      console.warn("IntroAudio init error:", e);
    }
  }, []);

  // ─── Play ElevenLabs Voiceover Segments ──────────────────────────
  const playVoiceSegment = useCallback((chapterId: number) => {
    const audioObj = voiceoverRef.current;
    if (!audioObj) return;

    const segments: Record<number, { start: number; end: number }> = {
      0: { start: 0, end: 3.8 },
      2: { start: 3.8, end: 11.5 },
      3: { start: 11.5, end: 19.5 },
      4: { start: 19.5, end: 29.8 },
      6: { start: 29.8, end: 42.2 }
    };

    const seg = segments[chapterId];
    if (seg) {
      audioObj.pause();
      audioObj.currentTime = seg.start;
      
      const onTimeUpdate = () => {
        if (audioObj.currentTime >= seg.end) {
          audioObj.pause();
        }
      };
      audioObj.ontimeupdate = onTimeUpdate;
      
      audioObj.play().catch(e => console.warn("Voiceover play blocked:", e));
    } else {
      audioObj.pause();
    }
  }, []);

  // ─── Sound Effects ───────────────────────────────────────────────
  const playWaterSplash = useCallback(() => {
    const ctx = ctxRef.current;
    const master = masterGainRef.current;
    if (!ctx || !master) return;
    try {
      const len = ctx.sampleRate * 0.6;
      const buf = ctx.createBuffer(1, len, ctx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      const src = ctx.createBufferSource();
      src.buffer = buf;
      const filt = ctx.createBiquadFilter();
      filt.type = "bandpass";
      filt.frequency.setValueAtTime(180, ctx.currentTime);
      filt.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.3);
      filt.Q.setValueAtTime(1.5, ctx.currentTime);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.2, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
      src.connect(filt);
      filt.connect(g);
      g.connect(master);
      src.start();
    } catch (e) {}
  }, []);

  const playCannonBoom = useCallback(() => {
    const ctx = ctxRef.current;
    const master = masterGainRef.current;
    if (!ctx || !master) return;
    try {
      const len = ctx.sampleRate * 1.5;
      const buf = ctx.createBuffer(1, len, ctx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      const src = ctx.createBufferSource();
      src.buffer = buf;
      const filt = ctx.createBiquadFilter();
      filt.type = "lowpass";
      filt.frequency.setValueAtTime(1000, ctx.currentTime);
      filt.frequency.exponentialRampToValueAtTime(8, ctx.currentTime + 1.2);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.5, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.3);
      src.connect(filt);
      filt.connect(g);
      g.connect(master);
      src.start();
    } catch (e) {}
  }, []);

  const playSwordClash = useCallback(() => {
    const ctx = ctxRef.current;
    const master = masterGainRef.current;
    if (!ctx || !master) return;
    try {
      const o1 = ctx.createOscillator();
      const o2 = ctx.createOscillator();
      const g = ctx.createGain();
      o1.type = "triangle";
      o1.frequency.setValueAtTime(1400, ctx.currentTime);
      o1.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.12);
      o2.type = "square";
      o2.frequency.setValueAtTime(1800, ctx.currentTime);
      o2.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.1);
      g.gain.setValueAtTime(0.18, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
      o1.connect(g);
      o2.connect(g);
      g.connect(master);
      o1.start();
      o2.start();
      o1.stop(ctx.currentTime + 0.15);
      o2.stop(ctx.currentTime + 0.15);
    } catch (e) {}
  }, []);

  const playElephantRoar = useCallback(() => {
    const ctx = ctxRef.current;
    const master = masterGainRef.current;
    if (!ctx || !master) return;
    try {
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(120, ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(300, ctx.currentTime + 0.3);
      osc.frequency.linearRampToValueAtTime(80, ctx.currentTime + 1.2);
      g.gain.setValueAtTime(0.3, ctx.currentTime);
      g.gain.linearRampToValueAtTime(0.4, ctx.currentTime + 0.3);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
      const filt = ctx.createBiquadFilter();
      filt.type = "lowpass";
      filt.frequency.setValueAtTime(500, ctx.currentTime);
      osc.connect(filt);
      filt.connect(g);
      g.connect(master);
      osc.start();
      osc.stop(ctx.currentTime + 1.5);
    } catch (e) {}
  }, []);

  const playVictoryDrum = useCallback(() => {
    const ctx = ctxRef.current;
    const master = masterGainRef.current;
    if (!ctx || !master) return;
    try {
      for (let i = 0; i < 6; i++) {
        setTimeout(() => {
          const osc = ctx.createOscillator();
          const g = ctx.createGain();
          osc.frequency.setValueAtTime(80 + i * 10, ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
          g.gain.setValueAtTime(0.4, ctx.currentTime);
          g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
          osc.connect(g);
          g.connect(master);
          osc.start();
          osc.stop(ctx.currentTime + 0.4);
        }, i * 150);
      }
    } catch (e) {}
  }, []);

  // ─── Update chapter for dynamic audio intensity ──────────────────
  const setChapter = useCallback((ch: number) => {
    activeChapterRef.current = ch;
  }, []);

  // ─── Cleanup ─────────────────────────────────────────────────────
  const cleanup = useCallback(() => {
    if (drumIntervalRef.current) clearTimeout(drumIntervalRef.current);
    if (droneRef.current) {
      try { droneRef.current.stop(); } catch (e) {}
    }
    if (ctxRef.current) {
      try { ctxRef.current.close(); } catch (e) {}
    }
    ctxRef.current = null;

    if (voiceoverRef.current) {
      try { voiceoverRef.current.pause(); } catch (e) {}
      voiceoverRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined" && !voiceoverRef.current) {
      voiceoverRef.current = new Audio("/vua_quang_trung.mp3");
      voiceoverRef.current.volume = 0.95;
    }
    return () => cleanup();
  }, [cleanup]);

  return {
    initAudio,
    setChapter,
    playVoiceSegment,
    playWaterSplash,
    playGroup: null, // placeholder
    playCannonBoom,
    playSwordClash,
    playElephantRoar,
    playVictoryDrum,
    cleanup,
  };
}
