import type { Character, Citation, StreamEvent } from "../types";

export async function fetchCharacters(): Promise<{ characters: Character[]; default_character_id: string }> {
  const response = await fetch("/api/characters", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Không tải được danh sách nhân vật.");
  }
  return response.json();
}

type StreamHandlers = {
  onStart?: (data: Extract<StreamEvent, { event: "start" }>["data"]) => void;
  onRetrieval?: (data: Extract<StreamEvent, { event: "retrieval" }>["data"]) => void;
  onToken?: (text: string) => void;
  onFinal?: (data: Extract<StreamEvent, { event: "final" }>["data"]) => void;
  onError?: (message: string) => void;
};

function dispatchEventBlock(block: string, handlers: StreamHandlers) {
  const eventLine = block.split("\n").find((line) => line.startsWith("event:"));
  const dataLine = block.split("\n").find((line) => line.startsWith("data:"));
  if (!eventLine || !dataLine) return;
  const event = eventLine.slice(6).trim();
  const rawData = dataLine.slice(5).trim();
  const data = JSON.parse(rawData);
  if (event === "start") handlers.onStart?.(data);
  if (event === "retrieval") handlers.onRetrieval?.(data);
  if (event === "token") handlers.onToken?.(data.text || "");
  if (event === "final") handlers.onFinal?.(data);
  if (event === "error") handlers.onError?.(data.message || "Có lỗi khi tạo câu trả lời.");
}

export async function streamChat(
  characterId: string,
  message: string,
  history: { role: string; content: string }[],
  handlers: StreamHandlers,
  signal?: AbortSignal,
) {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ character_id: characterId, message, history }),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new Error("Không kết nối được luồng đối thoại.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() || "";
    for (const block of blocks) {
      if (block.trim()) {
        dispatchEventBlock(block, handlers);
      }
    }
  }
  if (buffer.trim()) {
    dispatchEventBlock(buffer, handlers);
  }
}

export async function synthesizeAudio(characterId: string, text: string): Promise<{
  ok: boolean;
  audio_base64: string | null;
  mime_type: string;
  message: string;
}> {
  const response = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ character_id: characterId, text }),
  });
  if (!response.ok) {
    return { ok: false, audio_base64: null, mime_type: "audio/mpeg", message: "Âm thanh chưa sẵn sàng." };
  }
  return response.json();
}

export function citationKey(citation: Citation, index: number) {
  return `${citation.chunk_id || citation.source_title}-${index}`;
}
