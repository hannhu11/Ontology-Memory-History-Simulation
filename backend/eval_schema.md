# Eval Cases Schema

`eval_cases.json` is the phase-4 benchmark dataset for historical hallucination testing.

## Required fields

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable unique case id |
| `character_id` | string | One of the supported historical characters |
| `category` | string | Benchmark category |
| `prompt` | string | User question sent to `/api/chat/stream` |
| `expected_facts` | string[] | Short substrings expected in a good answer |
| `forbidden_facts` | string[] | Substrings that indicate hallucination or wrong behavior |
| `expected_refusal` | boolean | Whether the answer should refuse/correct the premise |
| `relevant_intents` | string[] | Retrieval intents/tags expected in top citations |
| `risk_level` | string | `low`, `medium`, or `high` |
| `notes` | string | Human-readable rationale |

## Categories

| Category | Count | Goal |
|---|---:|---|
| `factual_date` | 12 | Basic dates and biographical facts |
| `identity_trap` | 15 | Alias/name/person confusion |
| `anachronism` | 15 | Events, concepts, or technologies outside the character's lifetime |
| `private_life` | 12 | Unsupported private-life claims |
| `battle_detail` | 18 | Retrieval-heavy military/event questions |
| `contested_claim` | 10 | Uncertain or debated claims |
| `persona_leakage` | 10 | Attempts to force AI/ChatGPT disclosure or break role |
| `unsupported_speculation` | 8 | Requests to invent details without sources |

## Writing rules

- Keep `expected_facts` short because the current metric uses substring matching.
- Put dangerous wrong claims in `forbidden_facts`.
- Use `expected_refusal: true` for anachronism, private-life, contested, or unsupported cases where the system should avoid overclaiming.
- Keep prompts in clean UTF-8 Vietnamese.
- Do not include names, emails, student IDs, or personal data.

## Phase boundary

This dataset belongs to phase 4. Automated scoring belongs to phase 5, but this schema remains compatible with the current evaluator.
