export type Character = {
  character_id: string;
  display_name: string;
  era: string;
  death_year?: number;
  edge_cases: string[];
  portrait_url: string | null;
};

export type VisualEmotion = "idle" | "thinking" | "talking" | "happy" | "angry" | "sad" | "confused";

export type VisualMotion = "none" | "thinking" | "attack";

export type CharacterVisual = {
  phase: "idle" | "thinking" | "answering" | "speaking";
  intent?: string;
  emotion: VisualEmotion;
  baseEmotion?: Exclude<VisualEmotion, "talking">;
  motion: VisualMotion;
  asset?: string;
  action?: "none" | "loop" | "play_once";
};

export type Citation = {
  chunk_id: string;
  source_title: string;
  source_url: string;
  source_year?: string | number;
  claim_status: string;
  source_tier?: number;
  source_quality_score?: number;
  answer_intents?: string[];
  tags?: string[];
  fact: string;
};

export type RouteInfo = {
  intent: string;
  needs_rag: boolean;
  optimized_search_query?: string;
  confidence?: number;
  source?: string;
};

export type SourceSummary = {
  citation_count: number;
  tiers: number[];
  strong_source_count: number;
  strong_source_ratio: number;
};

export type StreamDiagnostics = {
  route?: RouteInfo;
  route_source?: string;
  llm_status?: string;
  fallback_used?: boolean;
  timings_ms?: Record<string, number>;
  source_summary?: SourceSummary;
  grounding_confidence?: number;
  variant?: "rag" | "non_rag";
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  mode?: string;
  state?: string;
  audioBase64?: string | null;
  audioReady?: boolean;
  audioPending?: boolean;
  diagnostics?: StreamDiagnostics;
  feedbackSent?: string;
};

export type StreamEvent =
  | { event: "start"; data: { character_id: string; status: string; visual?: CharacterVisual } }
  | { event: "retrieval"; data: { mode: string; state: string; citations: Citation[] } & StreamDiagnostics }
  | { event: "stream_start"; data: { intent: string; emotion: VisualEmotion; visual: CharacterVisual } }
  | { event: "token"; data: { text: string } }
  | {
      event: "final";
      data: { answer: string; mode: string; state: string; citations: Citation[]; visual?: CharacterVisual } & StreamDiagnostics;
    }
  | { event: "error"; data: { message: string; detail?: string } };
