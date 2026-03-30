---
id: doc-2
title: Firebase TypeScript SDK Feature Discovery
type: other
created_date: '2026-03-29 04:42'
updated_date: '2026-03-30 04:59'
---
# Firebase TypeScript SDK Feature Discovery

## Purpose
Define the initial Firebase support plan for `framework-definitions/schema.json` using schema-compatible, high-confidence TypeScript feature signatures.

## Scope
Phase 1 focuses on the modular Firebase web SDK only:
- `firebase/*`

Out of scope for this phase:
- `firebase-admin`
- `firebase-functions`
- compat APIs

These should be modeled as separate follow-up library entries because they use different package roots and have different semantics.

## Key Architectural Conclusion
The main issue is no longer just Firebase feature curation.

The current framework-feature model is mixing together three different concerns:
1. precise detector identity
2. architectural capability
3. operation-level intent

That is why raw library-oriented names such as `get_auth` feel wrong even when the detection is technically correct.

### What we can do today
The current schema can group related APIs only in a limited way:
- one feature may list multiple `absolute_paths`
- one feature has a single `concept`
- one feature has a single `target_level`
- one feature has a single `base_confidence`
- one feature has one shared description/notes block

So today we can safely group sibling APIs that represent the same operation and share the same concept/target level.

Examples that are possible today:
- `app_initialize` -> `firebase/app.initializeApp`
- `authentication_initialize` -> `firebase/auth.getAuth`, `firebase/auth.initializeAuth`
- `authentication_sign_in` -> `firebase/auth.signInWithEmailAndPassword`, `firebase/auth.signInWithPopup`, `firebase/auth.signInWithRedirect`
- `authentication_sign_out` -> `firebase/auth.signOut`
- `authentication_state_observe` -> `firebase/auth.onAuthStateChanged`
- `document_db_initialize` -> `firebase/firestore.getFirestore`
- `document_db_read` -> `firebase/firestore.getDoc`, `firebase/firestore.getDocs`
- `document_db_write` -> `firebase/firestore.addDoc`, `firebase/firestore.setDoc`, `firebase/firestore.updateDoc`
- `file_storage_initialize` -> `firebase/storage.getStorage`
- `file_storage_upload` -> `firebase/storage.uploadBytes`
- `file_storage_download` -> `firebase/storage.getDownloadURL`

### What we cannot do today
The current schema cannot represent a higher-order architectural grouping such as `authentication` as a first-class concept separate from individual feature keys.

That means the schema cannot currently express all of the following at the same time:
- exact detector identity
- operation-level grouping
- parent architectural capability

This is the core limitation.

## Schema Constraints
Feature definitions must follow the schema in:
- `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json`

Important constraints for this work:
- Prefer `concept: "CallExpression"`
- `CallExpression` requires `target_level: "function"`
- `CallExpression` requires `base_confidence`
- Use canonical `absolute_paths` values such as `firebase/app.initializeApp`
- Prefer high-confidence, low-ambiguity modular APIs for the initial cut
- For `CallExpression`, schema entries with `base_confidence < 0.70` must include `notes`

## Why Current Schema Is Insufficient
In `schema.json`, a feature definition currently contains only fields such as:
- `description`
- `docs_url`
- `absolute_paths`
- `target_level`
- `concept`
- `construct_query`
- `base_confidence`
- `startpoint`
- `notes`

There is no first-class field for:
- architectural capability
- capability family
- operation kind
- downstream architectural mapping

As a result, the contributor-chosen feature key becomes the only semantic label.

That makes the feature key do too much work.

## Output-Model Gap
The limitation is not only in the schema.

The query-engine output models and mapper are also feature-key driven today.

### Current behavior
- `app_interfaces_mapper.py` maps exact raw `feature_key` strings into inbound and outbound enums.
- Anything not explicitly mapped falls through into `InternalConstruct.kind = feature_key`.
- `agent_md_output.py` has many outbound kinds, but no clear auth/identity capability enum today.

This means even if we improve Firebase naming, authentication-like features still do not have a clean architectural home in downstream outputs.

### Important implication
Auth should not be forced into a database bucket.
If we add an outbound architectural enum for this area, it should be something like identity/authentication rather than a `DB_*` category.

## Recommended Schema Direction
Do not rely only on raw feature-key renaming.

### Recommended model
Keep precise detection, but add first-class architectural metadata.

Recommended new feature fields:
- `architectural_kind`
- `operation_kind`

### Why this is better
This lets us keep a precise detector-level feature while also exposing the software-engineering fundamental behind it.

Example shape:
```json
{
  "authentication_sign_in": {
    "description": "Authenticates a user with the application's identity provider.",
    "absolute_paths": [
      "firebase/auth.signInWithEmailAndPassword",
      "firebase/auth.signInWithPopup",
      "firebase/auth.signInWithRedirect"
    ],
    "target_level": "function",
    "concept": "CallExpression",
    "architectural_kind": "authentication",
    "operation_kind": "sign_in",
    "base_confidence": 0.82
  }
}
```

This preserves:
- exact matching paths
- operation-level grouping
- architectural rollup

## Recommended Enum Strategy
### Architectural capability examples
A cross-library capability enum should be based on software-engineering fundamentals, not vendor APIs.

Examples:
- `app_bootstrap`
- `authentication`
- `authorization`
- `document_db`
- `realtime_data`
- `file_storage`
- `serverless_invocation`
- `telemetry`
- `messaging`
- `configuration`
- `routing`

### Operation examples
A separate operation enum can stay fundamental as well.

Examples:
- `initialize`
- `sign_in`
- `sign_up`
- `sign_out`
- `observe_state`
- `read`
- `write`
- `update`
- `upload`
- `download`
- `invoke`
- `emit`

## Existing Validation Pipeline
The query engine already has a dedicated Temporal validator for low-confidence `CallExpression` matches.

### Relevant implementation references
- `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_agents.py`
- `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/temporal_workflows.py`
- `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/models/repository/framework_feature_validation_models.py`
- `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/temporal/activities/app_interfaces_activity.py`
- `unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/db/postgres/code_confluence_framework_repository.py`

### What the validator does
The `call_expression_validator` agent is designed for one low-confidence `CallExpression` candidate at a time. It:
1. checks official docs first
2. reads local file context
3. expands nearby symbol and alias evidence across the codebase
4. compares docs against detector evidence and local code
5. persists evidence with `upsert_framework_feature_validation_evidence`
6. persists the final status with `set_framework_feature_validation_status`

### Important threshold alignment
The DB currently routes low-confidence `CallExpression` rows to the validator when:
- `match_confidence < 0.70`

This aligns well with the schema rule that `CallExpression` features below `0.70` require contributor notes.

## Firebase Naming Recommendation Right Now
Until the schema is extended, use the most architecture-grounded operation names we can express safely today.

### Prefer these kinds of names
- `app_initialize`
- `authentication_initialize`
- `authentication_sign_in`
- `authentication_sign_up`
- `authentication_sign_out`
- `authentication_state_observe`
- `document_db_initialize`
- `document_db_read`
- `document_db_write`
- `file_storage_initialize`
- `file_storage_upload`
- `file_storage_download`

### Avoid these kinds of names
- `get_auth`
- `state_change_auth`
- `get_firestore`
- `upload_bytes`
- `get_download_url`

Those are implementation-level API labels, not architecture-level software concepts.

## Practical Rollout Guidance
### Lane A: direct high-confidence capability-oriented features
These can ship immediately even before schema extension, because they can be grouped safely at the operation level.

1. `app_initialize`
2. `authentication_initialize`
3. `authentication_sign_in`
4. `authentication_sign_up`
5. `authentication_sign_out`
6. `authentication_state_observe`
7. `document_db_initialize`
8. `document_db_read`
9. `document_db_write`
10. `file_storage_initialize`
11. `file_storage_upload`
12. `file_storage_download`

### Lane B: validator-backed expansion candidates
These are useful, but more likely to require disambiguation around aliasing, builder/reference semantics, overloads, or weaker behavioral signals.

1. `document_db_query`
2. `document_db_realtime_observe`
3. `authentication_interactive_sign_in`
4. `serverless_invocation`
5. `telemetry_emit`
6. `realtime_db_reference`
7. `realtime_db_observe`

## Follow-up Work Needed
This direction requires changes in more than one place.

### Schema work
Add first-class capability metadata to framework feature definitions.

### Query-engine work
Add architectural capability support to downstream mapping and outputs.
In particular, auth/identity needs a first-class architectural destination rather than falling back to `InternalConstruct.kind`.

### Firebase work
Rework Firebase TypeScript definitions so they use capability-oriented naming and grouping.

## Backlog Tracking
This architectural direction is now tracked in:
- `TASK-24` Introduce architecture-level capability grouping for framework features
- `TASK-24.1` Extend framework feature schema for capability metadata
- `TASK-24.2` Rework Firebase TypeScript definitions around architectural capabilities
- `TASK-24.3` Align query-engine outputs with architectural capability grouping

## Suggested Next Steps
1. Extend the schema with architectural capability metadata.
2. Add or revise output-model enums so auth/identity has a clean architectural representation.
3. Update Firebase definitions to use architecture-level operation names instead of raw API names.
4. Add tests for grouped capability definitions and validator-backed low-confidence cases.
