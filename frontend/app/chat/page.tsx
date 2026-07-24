"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, Bot, Pause, Play, RotateCcw, ShieldCheck, Sparkles, UserRound } from "lucide-react";
import { CharacterViewer } from "../../components/CharacterViewer";
import { IntroSequence } from "../../components/IntroSequence";
import { TranQuocTuanIntro } from "../../components/TranQuocTuanIntro";
import dynamic from "next/dynamic";

const QuangTrungCinematicIntro = dynamic(
  () => import("../../components/QuangTrungCinematicIntro").then((mod) => mod.QuangTrungCinematicIntro),
  { ssr: false }
);
import { citationKey, fetchCharacters, sendFeedback, streamChat, synthesizeAudio } from "../../lib/api";
import { activeCharacter, summarizeCitations, useHistoryStore } from "../../lib/store";
import type { ChatMessage, Citation, StreamDiagnostics } from "../../types";

/* ── Helpers ── */

function newId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function confidenceLabel(value?: number) {
  if (value === undefined) return "Chưa đo";
  if (value >= 85) return "Rất cao";
  if (value >= 65) return "Cao";
  if (value >= 45) return "Trung bình";
  return "Cần kiểm chứng";
}

function citationQuality(citation: Citation) {
  const tier = citation.source_tier ?? 3;
  const score = citation.source_quality_score ?? ({ 1: 1, 2: 0.78, 3: 0.55, 4: 0.25 }[tier] ?? 0.55);
  if (tier <= 1 || score >= 0.9) return { label: "Nguồn mạnh", tone: "excellent", note: "Sử liệu gốc / nguồn chính thống; khi trích báo cáo vẫn nên mở nguồn và đối chiếu bản in hoặc bản học thuật." };
  if (tier === 2 || score >= 0.72) return { label: "Nguồn tốt", tone: "strong", note: "Nguồn học thuật, sách hoặc bản số hóa có giá trị; vẫn cần đọc trong bối cảnh." };
  if (tier === 3 || score >= 0.48) return { label: "Nguồn phụ trợ", tone: "medium", note: "Nguồn có biên tập nhưng không nên dùng một mình cho kết luận học thuật." };
  return { label: "Cần kiểm chứng", tone: "weak", note: "Nguồn yếu hoặc cần đối chiếu thêm" };
}

function tierLabel(tier?: number) {
  return {
    1: "Tier 1 · Chính thống",
    2: "Tier 2 · Học thuật",
    3: "Tier 3 · Phổ thông",
    4: "Tier 4 · Cần đối chiếu",
  }[tier || 3];
}

function isNonRag(diagnostics?: StreamDiagnostics) {
  return diagnostics?.variant === "non_rag" || diagnostics?.route_source === "non_rag";
}

function evidenceMessage(diagnostics?: StreamDiagnostics, citations?: Citation[]) {
  if (isNonRag(diagnostics)) {
    return "Không có citation/grounding vì đây là baseline không truy xuất tư liệu. Chỉ dùng để so sánh với RAG, không dùng làm căn cứ học thuật.";
  }
  const count = citations?.length || 0;
  const strongRatio = diagnostics?.source_summary?.strong_source_ratio ?? 0;
  if (!count) return "Chưa có citation để đối chiếu. Không nên dùng làm căn cứ báo cáo nếu chưa kiểm chứng thủ công.";
  if (strongRatio >= 0.66) return "Có nhiều citation từ nguồn mạnh. Có thể dùng làm điểm bắt đầu để đối chiếu, nhưng khi viết báo cáo vẫn phải mở nguồn và kiểm chứng thủ công.";
  if (strongRatio >= 0.34) return "Có citation nhưng tỷ lệ nguồn mạnh chưa đủ cao. Nên đọc thêm và bổ sung tư liệu mạnh hơn trước khi trích báo cáo.";
  return "Citation chủ yếu là nguồn phụ trợ hoặc cần kiểm chứng. Không nên dùng làm căn cứ học thuật nếu chưa bổ sung nguồn mạnh.";
}

/* ── Ambient Particles ── */

function AmbientParticles() {
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, overflow: 'hidden' }}>
      {Array.from({ length: 15 }).map((_, i) => (
        <span
          key={i}
          className="ambient-particle"
          style={{
            left: `${5 + Math.random() * 90}%`,
            top: `${100 + Math.random() * 20}%`,
            width: `${1.5 + Math.random() * 2}px`,
            height: `${1.5 + Math.random() * 2}px`,
            animationDelay: `${Math.random() * 8}s`,
            animationDuration: `${6 + Math.random() * 6}s`,
            background: i % 3 === 0
              ? 'rgba(37, 183, 166, 0.25)'
              : 'rgba(229, 189, 59, 0.25)',
          }}
        />
      ))}
    </div>
  );
}

/* ── Evidence Quality Panel ── */

function EvidenceQualityPanel({ diagnostics, citations }: { diagnostics?: StreamDiagnostics; citations?: Citation[] }) {
  if (!diagnostics && !citations?.length) return null;
  const nonRag = isNonRag(diagnostics);
  const confidence = nonRag ? undefined : diagnostics?.grounding_confidence;
  const sourceSummary = diagnostics?.source_summary;
  const latency = diagnostics?.timings_ms?.total_ms;
  const strongRatio = nonRag ? 0 : Math.round((sourceSummary?.strong_source_ratio || 0) * 100);
  const level = nonRag ? "Không áp dụng" : confidenceLabel(confidence);

  return (
    <div className={`mt-4 rounded-xl border p-4 ${nonRag ? "border-[rgba(196,82,58,.25)] bg-[rgba(196,82,58,.05)]" : "border-[rgba(37,183,166,.2)] bg-[rgba(37,183,166,.05)]"}`}
      style={{ backdropFilter: 'blur(8px)' }}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 label-uppercase" style={{ color: 'var(--patina)' }}>
            <ShieldCheck size={14} /> Evidence Quality
          </div>
          <div className="mt-2 text-2xl font-black" style={{ color: 'var(--rice)', fontFamily: 'var(--font-display)' }}>{level}</div>
        </div>
        <span className="rounded-full border px-3 py-1 label-uppercase"
          style={{ borderColor: 'var(--border-gold)', color: 'var(--kinpaku)' }}>
          {nonRag ? "Non-RAG baseline" : "RAG + citation"}
        </span>
      </div>

      <p className="mt-3 text-sm leading-6" style={{ color: 'var(--rice-80)' }}>{evidenceMessage(diagnostics, citations)}</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {[
          { label: "Grounding", value: nonRag ? "—" : `${confidence ?? "?"}%` },
          { label: "Nguồn mạnh", value: nonRag ? "—" : `${strongRatio}%` },
          { label: "Độ trễ", value: latency ? `${latency}ms` : "đang đo" },
        ].map((item) => (
          <div key={item.label} className="rounded-lg p-3" style={{ background: 'var(--rice-08)' }}>
            <div className="label-uppercase" style={{ color: 'var(--rice-40)', fontSize: '0.65rem' }}>{item.label}</div>
            <div className="mt-1 text-xl font-black" style={{ color: 'var(--rice)', fontFamily: 'var(--font-mono)' }}>{item.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Citation List ── */

function CitationList({ citations }: { citations?: Citation[] }) {
  if (!citations?.length) return null;
  return (
    <details className="mt-4 rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border-gold)', background: 'var(--raised)' }}>
      <summary className="cursor-pointer px-5 py-3 text-sm font-semibold" style={{ color: 'var(--rice-80)' }}>
        Tư liệu đối chiếu · {citations.length}
      </summary>
      <div className="space-y-3 px-5 pb-5">
        {citations.map((citation, index) => {
          const quality = citationQuality(citation);
          return (
            <article
              key={citationKey(citation, index)}
              className="rounded-lg border-l-4 px-4 py-3"
              style={{ borderLeftColor: 'var(--vermillion)', background: '#faf5ea', color: 'var(--ink)' }}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="font-semibold">
                  {index + 1}. {citation.source_title}
                </div>
                <span className={`quality-badge quality-badge-${quality.tone}`}>{quality.label}</span>
              </div>
              <div className="mt-2 label-uppercase" style={{ color: '#6b4c2a', fontSize: '0.65rem' }}>
                {tierLabel(citation.source_tier)}
              </div>
              <div className="mt-1 text-sm">Niên đại tài liệu: {citation.source_year || "không rõ"}</div>
              <div className="text-sm">Mức độ nhận định: {citation.claim_status}</div>
              <div className="text-sm">Đoạn tư liệu: {citation.chunk_id}</div>
              <div className="mt-1 text-xs" style={{ color: '#6b4c2a' }}>{quality.note}</div>
              {citation.fact ? <p className="mt-2 text-sm leading-relaxed">{citation.fact}</p> : null}
              {citation.source_url ? (
                <a
                  href={citation.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 inline-block text-sm font-semibold underline"
                  style={{ color: '#075ca8' }}
                >
                  Mở tư liệu
                </a>
              ) : null}
            </article>
          );
        })}
      </div>
    </details>
  );
}

/* ── Audio Player ── */

function AudioPlayer({
  audioBase64,
  onAudioPlay,
  onAudioStop,
}: {
  audioBase64: string;
  onAudioPlay?: () => void;
  onAudioStop?: () => void;
}) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const toggle = async () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      await audio.play();
    } else {
      audio.pause();
    }
  };

  const elapsed = duration ? Math.min(duration, progress) : progress;
  const pct = duration ? Math.min(100, (elapsed / duration) * 100) : 0;

  return (
    <div className="mt-4 surface p-4">
      <audio
        ref={audioRef}
        src={`data:audio/mpeg;base64,${audioBase64}`}
        preload="metadata"
        onPlay={() => setPlaying(true)}
        onPause={() => {
          setPlaying(false);
          onAudioStop?.();
        }}
        onEnded={() => {
          setPlaying(false);
          onAudioStop?.();
        }}
        onPlaying={onAudioPlay}
        onLoadedMetadata={(event) => setDuration(event.currentTarget.duration || 0)}
        onTimeUpdate={(event) => setProgress(event.currentTarget.currentTime || 0)}
        autoPlay
      />
      <div className="flex items-center gap-4">
        <button
          onClick={toggle}
          className="btn-gold flex h-11 w-14 items-center justify-center rounded-lg"
          aria-label={playing ? "Dừng âm thanh" : "Phát âm thanh"}
        >
          {playing ? <Pause size={18} /> : <Play size={18} />}
        </button>
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 label-uppercase" style={{ color: 'var(--kinpaku)', fontSize: '0.65rem' }}>
              <span className="pulse-dot" style={{ width: 6, height: 6 }} />
              Âm thanh nhập vai
            </div>
            <div className="text-mono text-xs" style={{ color: 'var(--rice-60)' }}>
              {Math.floor(elapsed).toString().padStart(2, "0")}s
            </div>
          </div>
          <div className="h-2 overflow-hidden rounded-full" style={{ background: 'var(--rice-08)' }}>
            <div className="audio-progress h-full rounded-full" style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Message Bubble ── */

function MessageBubble({
  message,
  onAudioPlay,
  onAudioStop,
  onFeedback,
}: {
  message: ChatMessage;
  onAudioPlay?: () => void;
  onAudioStop?: () => void;
  onFeedback?: (messageId: string, rating: string) => void;
}) {
  const isUser = message.role === "user";
  const feedbackOptions = [
    ["faithful", "Nguồn phù hợp"],
    ["missing-citation", "Nguồn chưa thuyết phục"],
    ["hallucination", "Có dấu hiệu sai"],
  ] as const;
  return (
    <div className="message-enter flex gap-4 items-start">
      <div
        className="mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
        style={{
          background: isUser
            ? 'linear-gradient(135deg, var(--vermillion), #a83e2e)'
            : 'linear-gradient(135deg, var(--kinpaku), var(--kinpaku-soft))',
          boxShadow: isUser
            ? '0 4px 16px rgba(196, 82, 58, 0.3)'
            : '0 4px 16px rgba(229, 189, 59, 0.3)',
        }}
      >
        {isUser ? <UserRound size={18} color="#fff" /> : <Bot size={18} color="#0a0806" />}
      </div>
      <div className="min-w-0 flex-1">
        <div
          className="rounded-xl px-5 py-4 leading-8"
          style={{
            background: isUser ? 'var(--rice-08)' : 'transparent',
            color: isUser ? 'var(--rice)' : 'var(--rice-80)',
            border: isUser ? '1px solid var(--border-subtle)' : 'none',
          }}
        >
          {message.content || <span className="text-muted">Đang thành lời...</span>}
        </div>
        {message.audioPending ? (
          <div className="mt-4 rounded-xl border px-4 py-3 text-sm text-muted loading-shimmer"
            style={{ borderColor: 'var(--border-gold)', minHeight: 48 }}>
            Đang tạo âm thanh nhập vai...
          </div>
        ) : null}
        {message.audioReady && message.audioBase64 ? (
          <AudioPlayer audioBase64={message.audioBase64} onAudioPlay={onAudioPlay} onAudioStop={onAudioStop} />
        ) : null}
        {!isUser ? (
          <>
            <EvidenceQualityPanel diagnostics={message.diagnostics} citations={message.citations} />
            <CitationList citations={message.citations} />
            {message.content ? (
              <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-muted">
                <span className="mr-1 label-uppercase" style={{ fontSize: '0.6rem' }}>Phản hồi</span>
                {feedbackOptions.map(([rating, label]) => (
                  <button
                    key={rating}
                    type="button"
                    disabled={Boolean(message.feedbackSent)}
                    onClick={() => onFeedback?.(message.id, rating)}
                    className="btn-ghost rounded-full px-3 py-1 text-xs"
                    style={{ fontSize: '0.72rem' }}
                  >
                    {message.feedbackSent === rating ? "Đã ghi nhận" : label}
                  </button>
                ))}
              </div>
            ) : null}
          </>
        ) : null}
      </div>
    </div>
  );
}

import { useSearchParams } from "next/navigation";

/* ═══════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════ */

import { Suspense } from "react";

function ChatContent() {
  const searchParams = useSearchParams();
  const characterParam = searchParams.get("character");

  const {
    characters,
    selectedCharacterId,
    messages,
    status,
    statusText,
    isSending,
    visual,
    setCharacters,
    selectCharacter,
    addMessage,
    updateAssistant,
    appendAssistantText,
    setStatus,
    setSending,
    setVisual,
    completeVisualMotion,
    beginSpeaking,
    endSpeaking,
    clearChat,
  } = useHistoryStore();
  const [input, setInput] = useState("");
  const [playingIntro, setPlayingIntro] = useState<string | null>(null);
  const [variant, setVariant] = useState<"rag" | "non_rag">("rag");
  const [loadError, setLoadError] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetchCharacters()
      .then((payload) => {
        setCharacters(payload.characters, payload.default_character_id);
        if (characterParam && payload.characters.some((c: any) => c.character_id === characterParam)) {
          selectCharacter(characterParam);
        }
      })
      .catch((error: Error) => setLoadError(error.message));
  }, [setCharacters, characterParam, selectCharacter]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const selected = useMemo(
    () => activeCharacter(characters, selectedCharacterId),
    [characters, selectedCharacterId],
  );
  const latestAssistantId = useMemo(
    () => [...messages].reverse().find((message) => message.role === "assistant")?.id,
    [messages],
  );

  const handleSelectCharacter = (characterId: string) => {
    abortRef.current?.abort();
    abortRef.current = null;
    selectCharacter(characterId);
    setInput("");

    if (characterId === "quang_trung" || characterId === "tran_hung_dao" || characterId === "nguyen_trai") {
      setPlayingIntro(characterId);
    } else {
      setPlayingIntro(null);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const query = input.trim();
    const characterId = selected?.character_id || selectedCharacterId;
    if (!query || !characterId || isSending) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setInput("");
    setSending(true);
    setStatus("thinking", "Đang gợi ký ức");

    const userMessage: ChatMessage = { id: newId(), role: "user", content: query };
    const assistantId = newId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      citations: [],
      audioPending: false,
      audioReady: false,
    };
    addMessage(userMessage);
    addMessage(assistantMessage);

    const history = useHistoryStore
      .getState()
      .messages.slice(-8)
      .map((message) => ({ role: message.role, content: message.content }));

    try {
      await streamChat(
        characterId,
        query,
        history,
        {
          onStart: (data) => {
            if (useHistoryStore.getState().selectedCharacterId === data.character_id) {
              setStatus("thinking", data.status);
              if (data.visual) setVisual(data.visual);
            }
          },
          onRetrieval: (data) => {
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, {
              citations: data.citations,
              mode: data.mode,
              state: data.state,
              diagnostics: data,
            });
            setStatus("answering", summarizeCitations(data.citations));
          },
          onStreamStart: (data) => {
            if (useHistoryStore.getState().selectedCharacterId === characterId) {
              setVisual(data.visual);
            }
          },
          onToken: (text) => {
            if (useHistoryStore.getState().selectedCharacterId === characterId) {
              appendAssistantText(assistantId, text);
            }
          },
          onFinal: (data) => {
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, {
              content: data.answer,
              citations: data.citations,
              mode: data.mode,
              state: data.state,
              diagnostics: data,
              audioPending: true,
            });
            const currentVisual = useHistoryStore.getState().visual;
            if (data.visual && currentVisual.motion !== "attack") {
              setVisual(data.visual);
            }
            setSending(false);
            setStatus("idle", "Sẵn sàng đối thoại");
            void synthesizeAudio(characterId, data.answer)
              .then((audio) => {
                if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
                updateAssistant(assistantId, {
                  audioPending: false,
                  audioReady: audio.ok,
                  audioBase64: audio.audio_base64,
                });
              })
              .catch(() => {
                if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
                updateAssistant(assistantId, {
                  audioPending: false,
                  audioReady: false,
                  audioBase64: null,
                });
              });
          },
          onError: (message) => {
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, { content: message });
            setStatus("error", message);
            setSending(false);
          },
        },
        controller.signal,
        variant,
      );
    } catch (error) {
      if (controller.signal.aborted) return;
      const message = error instanceof Error ? error.message : "Có lỗi khi đối thoại.";
      updateAssistant(assistantId, { content: message });
      setStatus("error", message);
      setSending(false);
    }
  };

  const handleFeedback = async (messageId: string, rating: string) => {
    const characterId = selected?.character_id || selectedCharacterId;
    updateAssistant(messageId, { feedbackSent: rating });
    try {
      await sendFeedback({ message_id: messageId, character_id: characterId, rating });
    } catch {
      updateAssistant(messageId, { feedbackSent: undefined });
    }
  };

  /* ── Main Application ── */
  return (
    <>
      {playingIntro === "quang_trung" && (
        <QuangTrungCinematicIntro onComplete={() => setPlayingIntro(null)} />
      )}
      {playingIntro === "tran_hung_dao" && (
        <TranQuocTuanIntro onComplete={() => setPlayingIntro(null)} />
      )}
      {playingIntro === "nguyen_trai" && (
        <IntroSequence onComplete={() => setPlayingIntro(null)} />
      )}
      <AmbientParticles />
      <main className="shell-grid" style={{ position: 'relative', zIndex: 1 }}>

        {/* ─── LEFT SIDEBAR ─── */}
        <aside className="left-rail panel flex min-h-[calc(100vh-2.5rem)] flex-col gap-5 p-5">
          <div>
            <div className="mb-2 label-uppercase" style={{ color: 'var(--kinpaku)' }}>Nhân vật</div>
            <select
              className="w-full rounded-lg border px-4 py-3 text-sm font-semibold outline-none transition-all"
              style={{
                borderColor: 'var(--border-gold-strong)',
                background: 'var(--raised-2)',
                color: 'var(--rice)',
              }}
              value={selectedCharacterId}
              onChange={(event) => handleSelectCharacter(event.target.value)}
              disabled={!characters.length}
            >
              {characters.map((character) => (
                <option key={character.character_id} value={character.character_id}>
                  {character.display_name}
                </option>
              ))}
            </select>
          </div>

          <section className="rounded-xl border p-4" style={{ borderColor: 'var(--border-gold)', background: 'var(--rice-08)' }}>
            <div className="mb-3 label-uppercase" style={{ color: 'var(--kinpaku)' }}>Chế độ kiểm thử</div>
            <div className="grid gap-2">
              {[
                ["rag", "RAG có trích dẫn", "Truy xuất tư liệu rồi trả lời."],
                ["non_rag", "Non-RAG baseline", "Không truy xuất, dùng để so sánh."],
              ].map(([value, label, description]) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setVariant(value as "rag" | "non_rag")}
                  className="rounded-lg border px-3 py-3 text-left transition-all"
                  style={{
                    borderColor: variant === value ? 'var(--kinpaku)' : 'var(--border-gold)',
                    background: variant === value ? 'rgba(229, 189, 59, 0.1)' : 'var(--rice-08)',
                    boxShadow: variant === value ? '0 0 20px rgba(229, 189, 59, 0.1)' : 'none',
                  }}
                >
                  <div className="text-sm font-bold" style={{ color: 'var(--rice)' }}>{label}</div>
                  <div className="mt-1 text-xs leading-5 text-muted">{description}</div>
                </button>
              ))}
            </div>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-bold" style={{ color: 'var(--rice)', fontFamily: 'var(--font-display)' }}>
              <Sparkles size={16} className="inline mr-2" style={{ color: 'var(--kinpaku)' }} />
              Kịch bản gài bẫy
            </h2>
            <div className="space-y-2">
              {(selected?.edge_cases || []).map((caseText) => (
                <button
                  key={caseText}
                  type="button"
                  onClick={() => setInput(caseText)}
                  className="btn-ghost w-full text-left text-sm leading-6 rounded-lg px-3 py-3"
                >
                  {caseText}
                </button>
              ))}
            </div>
          </section>

          <button
            type="button"
            onClick={clearChat}
            className="btn-ghost mt-auto flex items-center justify-center gap-2 rounded-lg"
          >
            <RotateCcw size={15} />
            Xóa hội thoại
          </button>
        </aside>

        {/* ─── MAIN CHAT ─── */}
        <section className="flex min-h-[calc(100vh-2.5rem)] flex-col">
          <header className="mb-6">
            <div className="section-divider mb-3" />
            <h1 className="text-3xl font-black text-display" style={{ color: 'var(--rice)' }}>
              Đối thoại lịch sử với nhân vật
            </h1>
            <p className="mt-2 text-muted text-sm">
              Nhân vật trả lời nhập vai dựa trên sử liệu thực · Phần đối chiếu học thuật nằm riêng bên dưới
            </p>
          </header>

          <div className="chat-scroll flex-1 overflow-y-auto pr-2">
            {loadError ? (
              <div className="surface p-6" style={{ color: '#f09080' }}>
                <strong>Lỗi kết nối:</strong> {loadError}
              </div>
            ) : messages.length ? (
              <div className="space-y-8">
                {messages.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    onAudioPlay={message.role === "assistant" && message.id === latestAssistantId ? beginSpeaking : undefined}
                    onAudioStop={message.role === "assistant" && message.id === latestAssistantId ? endSpeaking : undefined}
                    onFeedback={handleFeedback}
                  />
                ))}
              </div>
            ) : (
              <div className="surface flex min-h-[52vh] items-center justify-center p-10 text-center" style={{ borderColor: 'var(--border-gold)' }}>
                <div>
                  <div className="section-divider mx-auto mb-4" style={{ width: 80 }} />
                  <h2 className="text-2xl font-bold text-display" style={{ color: 'var(--kinpaku)' }}>
                    {selected?.display_name || "Simulacra"}
                  </h2>
                  <p className="mt-4 max-w-xl text-muted leading-7">
                    Khung đối thoại đã sẵn sàng. Hãy hỏi thẳng vào thân thế, tư tưởng, trận đánh, lựa chọn chính trị hoặc
                    câu gài bẫy để kiểm tra mô phỏng.
                  </p>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="mt-5">
            <div className="flex items-center gap-3 rounded-xl border p-3"
              style={{
                borderColor: 'var(--border-gold)',
                background: 'var(--rice-08)',
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.2)',
              }}>
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder={`Hỏi ${selected?.display_name || "nhân vật"} về thân thế, sự nghiệp, tư tưởng...`}
                className="min-w-0 flex-1 bg-transparent px-3 py-3 outline-none"
                style={{ color: 'var(--rice)', fontSize: '0.95rem' }}
                disabled={!selected || isSending}
              />
              <button
                type="submit"
                disabled={!input.trim() || !selected || isSending}
                className="btn-gold flex h-12 w-12 items-center justify-center rounded-xl"
                aria-label="Gửi câu hỏi"
              >
                <ArrowUp size={20} />
              </button>
            </div>
          </form>
        </section>

        {/* ─── RIGHT SIDEBAR ─── */}
        <aside className="right-rail">
          <div className="sticky top-5 flex h-[calc(100vh-2.5rem)] flex-col gap-4 overflow-y-auto pr-1">
            <div className="panel overflow-hidden glow-gold">
              <CharacterViewer character={selected} visual={visual} onMotionComplete={completeVisualMotion} />
            </div>
            <div className="panel p-5">
              <h2 className="text-lg font-bold text-display" style={{ color: 'var(--kinpaku)' }}>Nhân vật đang chọn</h2>
              <div className="section-divider mt-2 mb-3" />
              <p className="text-sm leading-7" style={{ color: 'var(--rice-80)' }}>
                <span className="label-uppercase" style={{ color: 'var(--rice-40)', fontSize: '0.6rem' }}>Tên</span><br />
                {selected?.display_name}
              </p>
              <p className="text-sm leading-7 mt-2" style={{ color: 'var(--rice-80)' }}>
                <span className="label-uppercase" style={{ color: 'var(--rice-40)', fontSize: '0.6rem' }}>Triều đại</span><br />
                {selected?.era || "đang nạp"}
              </p>
              <div className="mt-4 rounded-lg border px-3 py-2.5 text-sm flex items-center gap-2"
                style={{
                  borderColor: 'rgba(37, 183, 166, 0.2)',
                  background: 'rgba(37, 183, 166, 0.05)',
                  color: 'var(--rice-80)',
                }}>
                <span className="pulse-dot" />
                {status === "idle" ? "Sẵn sàng" : statusText}
              </div>
            </div>
          </div>
        </aside>
      </main>
    </>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center text-[var(--kinpaku)]">Đang tải giao diện...</div>}>
      <ChatContent />
    </Suspense>
  );
}
