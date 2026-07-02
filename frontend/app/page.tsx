"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, Bot, Pause, Play, RotateCcw, ShieldCheck, UserRound } from "lucide-react";
import { CharacterViewer } from "../components/CharacterViewer";
import { citationKey, fetchCharacters, sendFeedback, streamChat, synthesizeAudio } from "../lib/api";
import { activeCharacter, summarizeCitations, useHistoryStore } from "../lib/store";
import type { ChatMessage, Citation, StreamDiagnostics } from "../types";

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

function EvidenceQualityPanel({ diagnostics, citations }: { diagnostics?: StreamDiagnostics; citations?: Citation[] }) {
  if (!diagnostics && !citations?.length) return null;
  const nonRag = isNonRag(diagnostics);
  const confidence = nonRag ? undefined : diagnostics?.grounding_confidence;
  const sourceSummary = diagnostics?.source_summary;
  const latency = diagnostics?.timings_ms?.total_ms;
  const strongRatio = nonRag ? 0 : Math.round((sourceSummary?.strong_source_ratio || 0) * 100);
  const level = nonRag ? "Không áp dụng" : confidenceLabel(confidence);

  return (
    <div className={`mt-4 rounded-xl border p-4 ${nonRag ? "border-[rgba(255,184,107,.35)] bg-[rgba(255,184,107,.08)]" : "border-[rgba(37,183,166,.28)] bg-[rgba(37,183,166,.07)]"}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-xs font-black uppercase tracking-[.14em] text-[#25b7a6]">
            <ShieldCheck size={15} /> Evidence Quality
          </div>
          <div className="mt-2 text-2xl font-black text-[#f6f0e4]">{level}</div>
        </div>
        <span className="rounded-full border border-[rgba(246,240,228,.14)] px-3 py-1 text-xs font-black uppercase tracking-[.12em] text-[#e5bd3b]">
          {nonRag ? "Non-RAG baseline" : "RAG + citation"}
        </span>
      </div>

      <p className="mt-3 text-sm leading-6 text-[rgba(246,240,228,.78)]">{evidenceMessage(diagnostics, citations)}</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg bg-[rgba(246,240,228,.05)] p-3">
          <div className="text-xs font-bold uppercase tracking-[.12em] text-muted">Grounding</div>
          <div className="mt-1 text-xl font-black text-[#f6f0e4]">{nonRag ? "—" : `${confidence ?? "?"}%`}</div>
        </div>
        <div className="rounded-lg bg-[rgba(246,240,228,.05)] p-3">
          <div className="text-xs font-bold uppercase tracking-[.12em] text-muted">Nguồn mạnh</div>
          <div className="mt-1 text-xl font-black text-[#f6f0e4]">{nonRag ? "—" : `${strongRatio}%`}</div>
        </div>
        <div className="rounded-lg bg-[rgba(246,240,228,.05)] p-3">
          <div className="text-xs font-bold uppercase tracking-[.12em] text-muted">Độ trễ</div>
          <div className="mt-1 text-xl font-black text-[#f6f0e4]">{latency ? `${latency}ms` : "đang đo"}</div>
        </div>
      </div>
    </div>
  );
}

function CitationList({ citations }: { citations?: Citation[] }) {
  if (!citations?.length) return null;
  return (
    <details className="mt-4 rounded-lg border border-[rgba(229,189,59,.18)] bg-[#15120f]">
      <summary className="cursor-pointer px-4 py-3 text-sm text-[rgba(246,240,228,.8)]">
        Tư liệu đối chiếu · {citations.length}
      </summary>
      <div className="space-y-3 px-4 pb-4">
        {citations.map((citation, index) => {
          const quality = citationQuality(citation);
          return (
            <article
              key={citationKey(citation, index)}
              className="rounded-md border-l-4 border-[#9d3127] bg-[#fbf3df] px-4 py-3 text-[#2b2119]"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="font-semibold">
                  {index + 1}. {citation.source_title}
                </div>
                <span className={`quality-badge quality-badge-${quality.tone}`}>{quality.label}</span>
              </div>
              <div className="mt-2 text-xs font-bold uppercase tracking-[.1em] text-[#6b4c2a]">
                {tierLabel(citation.source_tier)}
              </div>
              <div className="mt-1 text-sm">Niên đại tài liệu: {citation.source_year || "không rõ"}</div>
              <div className="text-sm">Mức độ nhận định: {citation.claim_status}</div>
              <div className="text-sm">Đoạn tư liệu: {citation.chunk_id}</div>
              <div className="mt-1 text-xs text-[#6b4c2a]">{quality.note}</div>
              {citation.fact ? <p className="mt-2 text-sm leading-relaxed">{citation.fact}</p> : null}
              {citation.source_url ? (
                <a
                  href={citation.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 inline-block text-sm font-semibold text-[#075ca8] underline"
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
          className="flex h-11 w-14 items-center justify-center rounded-md bg-[#e5bd3b] text-[#1d160e] transition hover:bg-[#f0cc58]"
          aria-label={playing ? "Dừng âm thanh" : "Phát âm thanh"}
        >
          {playing ? <Pause size={20} /> : <Play size={20} />}
        </button>
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.12em] text-[#e5bd3b]">
              <span className="h-2 w-2 rounded-full bg-[#25b7a6]" />
              Âm thanh nhập vai
            </div>
            <div className="font-mono text-xs text-[rgba(246,240,228,.72)]">
              {Math.floor(elapsed).toString().padStart(2, "0")}s
            </div>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[rgba(246,240,228,.08)]">
            <div className="audio-progress h-full rounded-full" style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}

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
    <div className={`flex gap-3 ${isUser ? "items-start" : "items-start"}`}>
      <div
        className={`mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-md ${
          isUser ? "bg-[#ff4b4b]" : "bg-[#ff9f19]"
        }`}
      >
        {isUser ? <UserRound size={20} /> : <Bot size={20} />}
      </div>
      <div className="min-w-0 flex-1">
        <div
          className={`rounded-lg px-5 py-4 leading-8 ${
            isUser
              ? "bg-[rgba(246,240,228,.08)] text-[#f6f0e4]"
              : "bg-transparent text-[rgba(246,240,228,.92)]"
          }`}
        >
          {message.content || <span className="text-muted">Đang thành lời...</span>}
        </div>
        {message.audioPending ? (
          <div className="mt-4 rounded-lg border border-[rgba(229,189,59,.16)] bg-[#15120f] px-4 py-3 text-sm text-muted">
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
                <span className="mr-1 font-bold uppercase tracking-[.12em]">Phản hồi</span>
                {feedbackOptions.map(([rating, label]) => (
                  <button
                    key={rating}
                    type="button"
                    disabled={Boolean(message.feedbackSent)}
                    onClick={() => onFeedback?.(message.id, rating)}
                    className="rounded-full border border-[rgba(229,189,59,.18)] px-3 py-1 text-[rgba(246,240,228,.82)] transition hover:border-[#e5bd3b] hover:bg-[rgba(229,189,59,.08)] disabled:cursor-not-allowed disabled:opacity-45"
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

export default function Home() {
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
  const [variant, setVariant] = useState<"rag" | "non_rag">("rag");
  const [loadError, setLoadError] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetchCharacters()
      .then((payload) => setCharacters(payload.characters, payload.default_character_id))
      .catch((error: Error) => setLoadError(error.message));
  }, [setCharacters]);

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

  return (
    <main className="shell-grid">
      <aside className="left-rail panel flex min-h-[calc(100vh-2rem)] flex-col gap-5 p-5">
        <div>
          <div className="mb-2 text-xs uppercase tracking-[.14em] text-[#d7b458]">Nhân vật</div>
          <select
            className="w-full rounded-md border border-[rgba(229,189,59,.22)] bg-[#f6f0e4] px-4 py-3 text-[#2b2119] outline-none"
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

        <section className="rounded-lg border border-[rgba(229,189,59,.18)] bg-[rgba(246,240,228,.05)] p-4">
          <div className="mb-3 text-xs font-bold uppercase tracking-[.14em] text-[#d7b458]">Chế độ kiểm thử</div>
          <div className="grid gap-2">
            {[
              ["rag", "RAG có trích dẫn", "Truy xuất tư liệu rồi trả lời."],
              ["non_rag", "Non-RAG baseline", "Không truy xuất, dùng để so sánh."],
            ].map(([value, label, description]) => (
              <button
                key={value}
                type="button"
                onClick={() => setVariant(value as "rag" | "non_rag")}
                className={`rounded-md border px-3 py-3 text-left transition ${
                  variant === value
                    ? "border-[#e5bd3b] bg-[rgba(229,189,59,.14)]"
                    : "border-[rgba(229,189,59,.14)] bg-[rgba(246,240,228,.04)] hover:border-[rgba(229,189,59,.36)]"
                }`}
              >
                <div className="text-sm font-bold text-[#f6f0e4]">{label}</div>
                <div className="mt-1 text-xs leading-5 text-muted">{description}</div>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold text-[#f6f0e4]">Kịch bản gài bẫy</h2>
          <div className="space-y-3">
            {(selected?.edge_cases || []).map((caseText) => (
              <button
                key={caseText}
                type="button"
                onClick={() => setInput(caseText)}
                className="w-full rounded-md border border-[rgba(229,189,59,.18)] bg-[rgba(246,240,228,.06)] px-3 py-3 text-sm leading-6 text-[rgba(246,240,228,.88)] transition hover:border-[#e5bd3b] hover:bg-[rgba(229,189,59,.1)]"
              >
                {caseText}
              </button>
            ))}
          </div>
        </section>

        <button
          type="button"
          onClick={clearChat}
          className="mt-auto flex items-center justify-center gap-2 rounded-md border border-[rgba(229,189,59,.22)] px-4 py-3 text-sm text-[rgba(246,240,228,.9)] hover:bg-[rgba(229,189,59,.1)]"
        >
          <RotateCcw size={16} />
          Xóa hội thoại
        </button>
      </aside>

      <section className="flex min-h-[calc(100vh-2rem)] flex-col">
        <header className="mb-5">
          <h1 className="text-3xl font-black text-[#f6f0e4]">Đối thoại lịch sử với nhân vật</h1>
          <p className="mt-2 text-muted">Nhân vật trả lời nhập vai; phần đối chiếu học thuật nằm riêng bên dưới.</p>
        </header>

        <div className="chat-scroll flex-1 overflow-y-auto pr-2">
          {loadError ? (
            <div className="surface p-5 text-[#ffb7a8]">{loadError}</div>
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
            <div className="surface flex min-h-[48vh] items-center justify-center p-8 text-center">
              <div>
                <div className="mx-auto mb-4 h-2 w-24 rounded-full bg-[#e5bd3b]" />
                <h2 className="text-2xl font-bold text-[#e5bd3b]">{selected?.display_name || "Simulacra"}</h2>
                <p className="mt-3 max-w-xl text-muted">
                  Khung đối thoại đã sẵn sàng. Hãy hỏi thẳng vào thân thế, tư tưởng, trận đánh, lựa chọn chính trị hoặc
                  câu gài bẫy để kiểm tra mô phỏng.
                </p>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="mt-5">
          <div className="flex items-center gap-3 rounded-lg border border-[rgba(229,189,59,.16)] bg-[rgba(246,240,228,.08)] p-3">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={`Hỏi ${selected?.display_name || "nhân vật"} về thân thế, sự nghiệp, tư tưởng...`}
              className="min-w-0 flex-1 bg-transparent px-2 py-3 text-[#f6f0e4] outline-none placeholder:text-[rgba(246,240,228,.42)]"
              disabled={!selected || isSending}
            />
            <button
              type="submit"
              disabled={!input.trim() || !selected || isSending}
              className="flex h-12 w-12 items-center justify-center rounded-md bg-[#e5bd3b] text-[#1c150d] disabled:cursor-not-allowed disabled:opacity-45"
              aria-label="Gửi câu hỏi"
            >
              <ArrowUp size={21} />
            </button>
          </div>
        </form>
      </section>

      <aside className="right-rail">
        <div className="sticky top-8 flex h-[calc(100vh-4rem)] flex-col gap-4 overflow-y-auto pr-1">
          <div className="panel overflow-hidden">
            <CharacterViewer character={selected} visual={visual} onMotionComplete={completeVisualMotion} />
          </div>
          <div className="panel p-5">
            <h2 className="text-lg font-bold text-[#e5bd3b]">Nhân vật đang chọn</h2>
            <p className="mt-3 text-sm leading-7 text-[rgba(246,240,228,.84)]">
              Tên hiển thị: {selected?.display_name}
            </p>
            <p className="text-sm leading-7 text-[rgba(246,240,228,.84)]">
              Triều đại: {selected?.era || "đang nạp"}
            </p>
            <div className="mt-4 rounded-md border border-[rgba(37,183,166,.28)] bg-[rgba(37,183,166,.07)] px-3 py-2 text-sm text-[rgba(246,240,228,.84)]">
              <span className="mr-2 inline-block h-2 w-2 rounded-full bg-[#25b7a6]" />
              {status === "idle" ? "Sẵn sàng" : statusText}
            </div>
          </div>
        </div>
      </aside>
    </main>
  );
}
