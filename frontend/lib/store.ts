import { create } from "zustand";
import type { Character, CharacterVisual, ChatMessage, Citation } from "../types";

export const DEFAULT_VISUAL: CharacterVisual = {
  phase: "idle",
  emotion: "idle",
  baseEmotion: "idle",
  motion: "none",
  action: "none",
};

type HistoryState = {
  characters: Character[];
  selectedCharacterId: string;
  messages: ChatMessage[];
  status: "idle" | "thinking" | "answering" | "audio" | "error";
  statusText: string;
  isSending: boolean;
  visual: CharacterVisual;
  setCharacters: (characters: Character[], defaultId: string) => void;
  selectCharacter: (characterId: string) => void;
  addMessage: (message: ChatMessage) => void;
  updateAssistant: (id: string, patch: Partial<ChatMessage>) => void;
  appendAssistantText: (id: string, text: string) => void;
  setStatus: (status: HistoryState["status"], statusText: string) => void;
  setSending: (value: boolean) => void;
  setVisual: (visual: CharacterVisual) => void;
  completeVisualMotion: () => void;
  beginSpeaking: () => void;
  endSpeaking: () => void;
  clearChat: () => void;
};

export const useHistoryStore = create<HistoryState>((set) => ({
  characters: [],
  selectedCharacterId: "",
  messages: [],
  status: "idle",
  statusText: "Sẵn sàng đối thoại",
  isSending: false,
  visual: DEFAULT_VISUAL,
  setCharacters: (characters, defaultId) =>
    set({
      characters,
      selectedCharacterId: defaultId || characters[0]?.character_id || "",
      messages: [],
      status: "idle",
      statusText: "Sẵn sàng đối thoại",
      visual: DEFAULT_VISUAL,
    }),
  selectCharacter: (characterId) =>
    set({
      selectedCharacterId: characterId,
      messages: [],
      status: "idle",
      statusText: "Đã đổi nhân vật",
      isSending: false,
      visual: DEFAULT_VISUAL,
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
  setVisual: (visual) =>
    set((state) => ({
      visual: {
        ...visual,
        baseEmotion:
          visual.baseEmotion ||
          (visual.emotion === "talking" ? state.visual.baseEmotion || "idle" : visual.emotion),
      },
    })),
  completeVisualMotion: () =>
    set((state) => ({
      visual: {
        ...state.visual,
        motion: "none",
        action: "none",
      },
    })),
  beginSpeaking: () =>
    set((state) => ({
      visual: {
        ...state.visual,
        phase: "speaking",
        emotion: "talking",
        baseEmotion:
          state.visual.emotion === "talking" ? state.visual.baseEmotion || "idle" : state.visual.emotion,
        motion: state.visual.motion === "attack" ? "attack" : "none",
        action: state.visual.motion === "attack" ? state.visual.action : "none",
      },
    })),
  endSpeaking: () =>
    set((state) => ({
      visual: {
        ...state.visual,
        phase: "idle",
        emotion: state.visual.baseEmotion || "idle",
        motion: "none",
        action: "none",
      },
    })),
  clearChat: () =>
    set({
      messages: [],
      status: "idle",
      statusText: "Đã xóa hội thoại",
      isSending: false,
      visual: DEFAULT_VISUAL,
    }),
}));

export function activeCharacter(characters: Character[], selectedCharacterId: string): Character | undefined {
  return characters.find((character) => character.character_id === selectedCharacterId) || characters[0];
}

export function summarizeCitations(citations: Citation[] | undefined) {
  if (!citations?.length) return "Chưa có tư liệu đối chiếu.";
  return `${citations.length} ký ức đối chiếu đã được gợi lại.`;
}
