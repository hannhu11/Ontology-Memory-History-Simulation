export type Character = {
  character_id: string;
  display_name: string;
  era: string;
  death_year?: number;
  edge_cases: string[];
  portrait_url: string | null;
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
};

export type StreamEvent =
  | { event: "start"; data: { character_id: string; status: string } }
  | { event: "retrieval"; data: { mode: string; state: string; citations: Citation[] } }
  | { event: "token"; data: { text: string } }
  | { event: "final"; data: { answer: string; mode: string; state: string; citations: Citation[] } }
  | { event: "error"; data: { message: string; detail?: string } };
