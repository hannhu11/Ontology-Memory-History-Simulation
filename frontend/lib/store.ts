import { create } from "zustand";
import type { Character, ChatMessage, Citation } from "../types";

type HistoryState = {
  characters: Character[];
  selectedCharacterId: string;
  messages: ChatMessage[];
  status: "idle" | "thinking" | "answering" | "audio" | "error";
  statusText: string;
  isSending: boolean;
  setCharacters: (characters: Character[], defaultId: string) => void;
  selectCharacter: (characterId: string) => void;
  addMessage: (message: ChatMessage) => void;
  updateAssistant: (id: string, patch: Partial<ChatMessage>) => void;
  appendAssistantText: (id: string, text: string) => void;
  setStatus: (status: HistoryState["status"], statusText: string) => void;
  setSending: (value: boolean) => void;
  clearChat: () => void;
};

export const useHistoryStore = create<HistoryState>((set) => ({
  characters: [],
  selectedCharacterId: "",
  messages: [],
  status: "idle",
  statusText: "Sẵn sàng đối thoại",
  isSending: false,
  setCharacters: (characters, defaultId) =>
    set({
      characters,
      selectedCharacterId: defaultId || characters[0]?.character_id || "",
      messages: [],
      status: "idle",
      statusText: "Sẵn sàng đối thoại",
    }),
  selectCharacter: (characterId) =>
    set({
      selectedCharacterId: characterId,
      messages: [],
      status: "idle",
      statusText: "Đã đổi nhân vật",
      isSending: false,
    }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  updateAssistant: (id, patch) =>
    set((state) => ({
      messages: state.messages.map((message) => (message.id === id ? { ...message, ...patch } : message)),
    })),
  appendAssistantText: (id, text) =>
    set((state) => ({
      messages: state.messages.map((message) =>
        message.id === id ? { ...message, content: `${message.content}${text}` } : message,
      ),
    })),
  setStatus: (status, statusText) => set({ status, statusText }),
  setSending: (value) => set({ isSending: value }),
  clearChat: () => set({ messages: [], status: "idle", statusText: "Đã xóa hội thoại", isSending: false }),
}));

export function activeCharacter(characters: Character[], selectedCharacterId: string): Character | undefined {
  return characters.find((character) => character.character_id === selectedCharacterId) || characters[0];
}

export function summarizeCitations(citations: Citation[] | undefined) {
  if (!citations?.length) return "Chưa có tư liệu đối chiếu.";
  return `${citations.length} ký ức đối chiếu đã được gợi lại.`;
}
