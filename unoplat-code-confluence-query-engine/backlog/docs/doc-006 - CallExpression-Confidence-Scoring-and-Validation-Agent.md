---
id: doc-006
title: CallExpression Confidence Scoring and Low-Confidence Validation Agent
type: architecture
created_date: '2026-02-25 10:20'
updated_date: '2026-02-25 10:20'
---
# CallExpression Confidence Scoring and Low-Confidence Validation Agent

> **Purpose**: Introduce a practical hybrid detection pipeline for framework `CallExpression` features by combining fast import/call heuristics with confidence scoring and an LLM validation pass for uncertain matches.

---

## Executive Summary

### Problem

Current framework feature detection is deterministic and fast, but practical precision gaps exist for `CallExpression`-heavy patterns:

1. False positives from shared method names (`create`, `findMany`, `update`) across non-framework objects.
2. False negatives for wrapper/indirection patterns where framework usage is not directly visible in one call expression.
3. Limited downstream evidence for disambiguation (`match_text` + line span only in persisted usage rows).

### Proposed Approach

1. Keep existing deterministic detection as baseline.
2. Add confidence scoring to feature definition and per-match evidence.
3. Validate only low-confidence `CallExpression` detections using a dedicated validator agent that reads focused source context.
4. Use validator result to confirm, reject, or correct the classified interface construct before AGENTS/app_interfaces rendering.

### Why this is pragmatic

1. Preserves speed for high-confidence paths.
2. Avoids costly full symbolic analysis for complex alias/wrapper flows.
3. Leverages LLM strengths (local code understanding with context windows) where heuristics are weakest.

---

## Current-State Constraints

## 1. Framework feature model and schema constraints

1. Feature schema currently allows only fixed fields and does not include confidence metadata.
2. `construct_query` is constrained to existing keys and has no confidence-related controls.
3. Current ingestion schema still enforces concept-level constraints around `CallExpression`.

## 2. Detection payload and persistence constraints

1. In-memory `CallExpression` detections contain richer fields (`callee`, `args_text`) but downstream persistence primarily keeps line span + `match_text`.
2. Query-engine app interface aggregation currently maps from feature rows without confidence semantics.

## 3. Query-engine workflow constraints

1. `app_interfaces_agent` exists today as deterministic DB-to-model transformation.
2. It does not run an LLM adjudication step for uncertain features.

---

## Design Goals

1. Improve precision for `CallExpression`-derived interface classification without regressing throughput.
2. Introduce confidence in a contract-safe, auditable way across ingestion and query-engine.
3. Keep rollout incremental with a clear cutover plan.
4. Restrict LLM validation scope to uncertain records to control latency and token cost.
5. Enforce mandatory validation for low-confidence records before interface aggregation.

---

## Non-Goals

1. Full static analysis / interprocedural dataflow for all language features.
2. Replacing Tree-sitter baseline detection.
3. Applying LLM validation to all concepts from day one.
4. Breaking existing AGENTS.md generation format in a single release.

---

## Proposed Data Model Extensions

## 1. Framework definition schema (spec-time confidence)

Add one field to `featureDef`:

1. `base_confidence` (number, `0.0` to `1.0`, default `0.85`)

Usage guidance:

1. High-precision patterns (e.g., strict decorator + method regex) can use higher `base_confidence`.
2. Broad call patterns (e.g., generic CRUD verbs) should set lower `base_confidence`.
3. If `base_confidence < 0.70`, contributors should provide disambiguation guidance in existing feature `notes` for validator context.

## 2. Framework feature metadata (definition table)

Extend `framework_feature` model/table:

1. `base_confidence` (float)

## 3. Detected usage metadata (usage table)

Extend `code_confluence_file_framework_feature` model/table:

1. `match_confidence` (float)
2. `validation_status` (enum/string: `pending`, `completed`, `needs_review`)
3. `evidence_json` (JSONB; optional rich evidence such as `callee`, `args_text`, normalized object chain, validator decision, rationale, and line references)

This is required so low-confidence decisioning is queryable and reproducible.

---

## Confidence Scoring Model (CallExpression Phase)

## 1. Inputs

1. `base_confidence` from feature definition.
2. Import evidence strength (exact absolute path vs module-level partial).
3. Callee shape signals:
   - exact constructor/function match
   - member-chain depth
   - verb ambiguity (`create` more ambiguous than `findFirstOrThrow`)
4. Optional construct query specificity:
   - tighter regex increases confidence
   - broad regex decreases confidence

## 2. Example scoring formula (initial heuristic)

```
score = base_confidence
score += import_exact_bonus
score += callee_exact_bonus
score -= ambiguous_verb_penalty
score -= broad_regex_penalty
score = clamp(score, 0.0, 1.0)
```

Initial defaults:

1. `GLOBAL_CALL_EXPRESSION_VALIDATION_THRESHOLD = 0.70`
2. `auto-accept threshold = 0.90`
3. `reject-by-heuristic` not enabled initially (avoid premature false negatives)

---

## Validation Agent Design

## 1. Triggering

Run only when:

1. `concept == CallExpression`
2. `match_confidence < GLOBAL_CALL_EXPRESSION_VALIDATION_THRESHOLD` (`0.70`)
3. Feature is relevant to interface mapping stage (inbound/outbound/internal classification paths)

## 2. Validator inputs

Per candidate:

1. Codebase path
2. File path
3. Start/end line
4. Matched text
5. Feature metadata (`library`, `feature_key`, `absolute_paths`, `construct_query`, `base_confidence`, `notes`)
6. Parsed evidence (`callee`, `args_text`, and any alias/object hints)

## 3. Validator tools

Use existing query-engine tools:

1. `read_file_content` for targeted line windows
2. `search_across_codebase` for related symbol/object usage
3. Optional narrow context expansion around assignment/constructor points

## 4. Validator outputs

Structured result per candidate:

1. `decision`: `confirm | reject | correct`
2. `updated_feature_key` (only for `correct`)
3. `final_confidence` (`0.0..1.0`)
4. `evidence_json` (structured evidence payload containing rationale and file + line references)

## 5. Write-back behavior

1. Update usage row fields (`validation_status`, `match_confidence`, `evidence_json`).
2. Set `validation_status = completed` when validator output is written; set `validation_status = needs_review` when validator cannot produce a reliable decision.
3. Rows with `evidence_json.decision in {confirm, correct}` proceed to interface mapper.
4. Rows with `evidence_json.decision = reject` are excluded from final interfaces and can be logged for audit.

---

## Workflow Integration

## 1. Existing flow

1. Ingestion writes framework feature usage rows.
2. Query-engine `app_interfaces_activity` fetches rows and maps directly to interfaces.

## 2. Proposed flow

1. Fetch feature usage rows.
2. Partition into:
   - high-confidence accepted
   - low-confidence validation-required
3. Run validator on low-confidence partition.
4. Merge accepted + validator-`completed` rows with decision `confirm`/`correct`.
5. Build interfaces from merged set.
6. Persist validator outcomes for observability/debuggability.

---

## Incremental Rollout Plan

## Phase 1: Contracts and storage

1. Add schema field (`base_confidence`).
2. Extend commons models and DB tables for confidence + validation fields.
3. Add migrations with explicit backfill and strict constraints.

## Phase 2: Scoring in ingestion

1. Implement initial `CallExpression` scorer.
2. Persist `match_confidence` and evidence.
3. Keep deterministic interface mapper unchanged (no validator yet).

## Phase 3: Validator integration

1. Add new query-engine validator agent and workflow step.
2. Enable for Python `CallExpression` rows first.
3. Enforce validator execution for all rows below global threshold (`0.70`).

## Phase 4: Expansion

1. Extend to TypeScript once TS framework feature detection path is wired.
2. Evaluate extending validator to other concepts if ROI is proven.

---

## Acceptance Criteria

## 1. Functional

1. Feature definitions accept and persist confidence metadata.
2. Usage rows contain `match_confidence` for `CallExpression`.
3. Low-confidence rows are validated and receive explicit status (`pending`, `completed`, `needs_review`).
4. App interfaces output excludes rows whose validator decision is `reject`.

## 2. Quality

1. Precision improves materially on representative mixed-service repos.
2. High-confidence throughput remains near current baseline.
3. Validator token/latency impact remains bounded by global-threshold gating (`0.70`).

## 3. Observability

1. Metrics emitted:
   - low-confidence candidate count
   - validation `completed`/`needs_review` rates
   - validator decision (`confirm`/`reject`/`correct`) rates
   - average confidence before/after validation
   - validator latency and token cost

---

## Practical Example: Why this is needed

```ts
import { PrismaClient } from "@prisma/client";
import Stripe from "stripe";

const prisma = new PrismaClient();
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function createCustomer(email: string) {
  return stripe.customers.create({ email });
}
```

Heuristic-only risk:

1. Import gate passes due to Prisma presence.
2. Generic `create` call can be misclassified as Prisma usage.

Confidence+validator behavior:

1. Heuristic assigns low/medium confidence due to ambiguous verb and object mismatch.
2. Validator inspects local code and confirms `create` belongs to Stripe client, not Prisma.
3. Detection is rejected/corrected before interface aggregation.

---

## Risks and Mitigations

1. Risk: Added schema/model complexity.
   - Mitigation: explicit migration/backfill plan + phased rollout.
2. Risk: Validator cost spikes on large repos.
   - Mitigation: strict threshold gating + per-run caps + batching.
3. Risk: LLM validator introduces non-determinism.
   - Mitigation: constrained output schema + evidence line requirements + strict retry/error policy.
4. Risk: Missing evidence fields reduce validator quality.
   - Mitigation: persist richer `CallExpression` evidence (`callee`, args, object hints) in usage metadata.

---

## Open Questions

1. Is global threshold `0.70` correct, or should it be tuned after benchmark runs?
2. Should corrected decisions create alternate feature rows or mutate in place?
3. Do we expose confidence in final `AgentMdOutput`, or keep it internal for now?
4. Should validator run before or inside `app_interfaces_activity`?
5. What is the first benchmark corpus for precision/cost comparison?

---

## Implementation Checklist

1. Schema: add `base_confidence` field to `featureDef`.
2. Commons: update `FrameworkFeature` + typed models.
3. DB: add confidence/validation columns + migration.
4. Ingestion: compute/persist `match_confidence` for `CallExpression`.
5. Query-engine DB repo: fetch confidence + validation fields.
6. Query-engine workflow: add low-confidence validation step.
7. Agent layer: add validator agent definition and strict output model.
8. Mapper: consume only accepted records and validator-`completed` records with decision `confirm`/`correct`.
9. Tests: contract, migration, scorer unit tests, validator integration tests.
10. Metrics: add counters/histograms for validation outcomes and cost.
