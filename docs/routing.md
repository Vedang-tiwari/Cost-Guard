# Cost Guard Model Routing & Optimization Architecture

Cost Guard's Intelligent Optimization Engine (Phase 2) intercepts requests to minimize token expenditure and overall cost while ensuring task-appropriate reasoning capabilities.

---

## 1. Request Analysis & Complexity Scoring

Each incoming prompt undergoes multi-factor heuristic complexity evaluation producing a score between `0` and `100`:

| Complexity Score | Tier | Target Model Class | Example Models |
|---|---|---|---|
| **0 – 30** | Low | Economical, fast models | `gemini-1.5-flash`, `gpt-4o-mini`, `claude-3-5-haiku` |
| **31 – 65** | Medium | Balanced capability models | `gpt-4o`, `gemini-1.5-pro` |
| **66 – 100** | High | Premium reasoning models | `gpt-4o`, `claude-3-5-sonnet` |

### Complexity Scoring Signals
1. **Task Type Baseline**: classification (`15`), extraction (`35`), summarization (`40`), code (`70`), reasoning (`75`).
2. **Context & Token Volume**: Length penalties scaled up to 20 points for prompts exceeding 200, 500, 1000, and 2000 tokens.
3. **Instruction Density**: Detection of numbered lists, multi-step subtasks, and bulleted constraints.
4. **Negative Constraints & Output Formatting**: Structural schema requirements ("must not", "only in valid JSON").
5. **Reasoning Markers**: Presence of chain-of-thought phrases ("step-by-step", "trade-offs", "implications").

---

## 2. Semantic Caching

- **Tenant Isolation**: Deterministic composite cache keys scoped to `application_id` and `organization_id`.
- **Topical Vector Embeddings**: 256-dimensional dense normalized embeddings with TF-IDF style stop-word suppression and n-gram subword hashing.
- **Similarity Threshold**: Configurable threshold (default `0.88`). High similarity matches return instantly with **100% cost savings** and **zero provider API overhead**.

---

## 3. Prompt Optimization

- Normalizes excessive whitespace and redundant consecutive line breaks (`\n{3,}` -> `\n\n`).
- Strips non-instructional polite filler prefixes ("Please answer the following question:", "Could you kindly explain...").
- Measures original tokens vs optimized tokens and logs `methods_applied` and `tokens_saved`.

---

## 4. Cost Accounting Formula

```text
Actual Cost = (Input Tokens / 1,000,000 × Input Price) + (Output Tokens / 1,000,000 × Output Price)
Baseline Cost = (Input Tokens / 1,000,000 × Reference Price) + (Output Tokens / 1,000,000 × Reference Price)
Savings ($) = max(0, Baseline Cost - Actual Cost)
Savings (%) = (Savings / Baseline Cost) × 100
```
- Reference baseline model: `gpt-4o` ($2.50 / 1M input, $10.00 / 1M output).
