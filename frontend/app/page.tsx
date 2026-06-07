"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, Bot, Pause, Play, RotateCcw, UserRound } from "lucide-react";
import { citationKey, fetchCharacters, streamChat, synthesizeAudio } from "../lib/api";
import { activeCharacter, summarizeCitations, useHistoryStore } from "../lib/store";
import type { ChatMessage, Citation } from "../types";

function newId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function CitationList({ citations }: { citations?: Citation[] }) {
  if (!citations?.length) return null;
  return (
    <details className="mt-4 rounded-lg border border-[rgba(229,189,59,.18)] bg-[#15120f]">
      <summary className="cursor-pointer px-4 py-3 text-sm text-[rgba(246,240,228,.8)]">
        Tư liệu đối chiếu · {citations.length}
      </summary>
      <div className="space-y-3 px-4 pb-4">
        {citations.map((citation, index) => (
          <article
            key={citationKey(citation, index)}
            className="rounded-md border-l-4 border-[#9d3127] bg-[#fbf3df] px-4 py-3 text-[#2b2119]"
          >
            <div className="font-semibold">
              {index + 1}. {citation.source_title}
            </div>
            <div className="mt-1 text-sm">Niên đại tài liệu: {citation.source_year || "không rõ"}</div>
            <div className="text-sm">Mức độ nhận định: {citation.claim_status}</div>
            <div className="text-sm">Đoạn tư liệu: {citation.chunk_id}</div>
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
        ))}
      </div>
    </details>
  );
}

function AudioPlayer({ audioBase64 }: { audioBase64: string }) {
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
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
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

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
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
        {message.audioReady && message.audioBase64 ? <AudioPlayer audioBase64={message.audioBase64} /> : null}
        {!isUser ? <CitationList citations={message.citations} /> : null}
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
    setCharacters,
    selectCharacter,
    addMessage,
    updateAssistant,
    appendAssistantText,
    setStatus,
    setSending,
    clearChat,
  } = useHistoryStore();
  const [input, setInput] = useState("");
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
            }
          },
          onRetrieval: (data) => {
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, {
              citations: data.citations,
              mode: data.mode,
              state: data.state,
            });
            setStatus("answering", summarizeCitations(data.citations));
          },
          onToken: (text) => {
            if (useHistoryStore.getState().selectedCharacterId === characterId) {
              appendAssistantText(assistantId, text);
            }
          },
          onFinal: async (data) => {
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, {
              content: data.answer,
              citations: data.citations,
              mode: data.mode,
              state: data.state,
              audioPending: true,
            });
            setStatus("audio", "Đang tạo âm thanh nhập vai");
            setSending(false);
            const audio = await synthesizeAudio(characterId, data.answer);
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, {
              audioPending: false,
              audioReady: audio.ok,
              audioBase64: audio.audio_base64,
            });
            setStatus("idle", "Sẵn sàng đối thoại");
          },
          onError: (message) => {
            if (useHistoryStore.getState().selectedCharacterId !== characterId) return;
            updateAssistant(assistantId, { content: message });
            setStatus("error", message);
            setSending(false);
          },
        },
        controller.signal,
      );
    } catch (error) {
      if (controller.signal.aborted) return;
      const message = error instanceof Error ? error.message : "Có lỗi khi đối thoại.";
      updateAssistant(assistantId, { content: message });
      setStatus("error", message);
      setSending(false);
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
                <MessageBubble key={message.id} message={message} />
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

      <aside className="right-rail flex flex-col gap-4">
        <div className="panel overflow-hidden">
          {selected?.portrait_url ? (
            <img src={selected.portrait_url} alt={selected.display_name} className="h-auto w-full" />
          ) : (
            <div className="flex aspect-[4/3] items-center justify-center bg-[#1d1915] text-center">
              <div>
                <div className="text-xl font-black uppercase text-[#e5bd3b]">{selected?.display_name || "Nhân vật"}</div>
                <div className="mt-2 text-sm font-bold uppercase tracking-[.12em] text-[#e5bd3b]">Simulacra</div>
              </div>
            </div>
          )}
        </div>
        <div className="panel p-5">
          <h2 className="text-lg font-bold text-[#e5bd3b]">Nhân vật đang chọn</h2>
          <p className="mt-3 text-sm leading-7 text-[rgba(246,240,228,.84)]">Tên hiển thị: {selected?.display_name}</p>
          <p className="text-sm leading-7 text-[rgba(246,240,228,.84)]">Triều đại: {selected?.era || "đang nạp"}</p>
          <div className="mt-4 rounded-md border border-[rgba(37,183,166,.28)] bg-[rgba(37,183,166,.07)] px-3 py-2 text-sm text-[rgba(246,240,228,.84)]">
            <span className="mr-2 inline-block h-2 w-2 rounded-full bg-[#25b7a6]" />
            {status === "idle" ? "Sẵn sàng" : statusText}
          </div>
        </div>
      </aside>
    </main>
  );
}
