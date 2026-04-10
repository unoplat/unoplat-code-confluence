---
id: TASK-27
title: >-
  Align DIDS contribution docs/schema with operation-level ingestion contract
  and refresh Firebase example
status: In Progress
assignee:
  - pi
created_date: '2026-04-09 06:41'
updated_date: '2026-04-10 06:48'
labels:
  - docs
  - schema
  - firebase
dependencies: []
references:
  - >-
    unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx
  - >-
    unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json
  - unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json
  - >-
    unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/processor/db/postgres/framework_loader.py
  - >-
    unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py
  - >-
    /Users/jayghiya/Documents/unoplat/unoplat-code-confluence.add-firebase-discovery/backlog/docs/doc-2
    - Firebase-TypeScript-SDK-Feature-Discovery.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review and fix documentation/schema drift in `unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx` and the published docs schema assets. Current docs still describe nested detector records per operation and stale migration wording, but ingestion/runtime in this branch consume a capability -> operation model where each operation is a single executable detection contract. Also refresh the Firebase TypeScript SDK example using vetted capability/operation research from official docs/backlog notes before finalizing the example set.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Contribution docs describe the same capability -> operation contract currently enforced by ingestion/runtime, with stale migration wording removed.
- [x] #2 Published docs schema assets match the supported operation-level structure and do not advertise unsupported nested multi-detector operations.
- [x] #3 Firebase example and surrounding guidance use a vetted set of major Firebase TypeScript SDK capabilities and operations informed by official docs/research.
- [x] #4 Relevant docs validation is rerun and documented after the updates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Validate current enforced contract from ingestion/runtime and identify every place the contribution page and published docs schema still imply unsupported nested multi-detector operations.
2. Research the Firebase TypeScript SDK capability surface from official/current docs and derive a vetted capability -> operation inventory suitable for the contribution-page example.
3. Revise the review-feedback plan using the researched Firebase inventory and the confirmed runtime contract, then present the detailed update for approval before implementation.
4. After approval, update the docs page and published schema assets, then rerun targeted docs validation and capture results in the task notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Validated that ingestion/runtime currently support capability -> operation, with each operation normalized into a single FrameworkFeature payload; no nested multi-detector operation model is present in ingestion schema or commons payload models.

Launched background subagent `Firebase SDK Research` to survey official Firebase TypeScript/Web SDK docs and return a major capability -> operation inventory for the docs example and review-feedback planning.

Read research artifact `research/firebase-typescript-sdk-capabilities.md`. Official Firebase JS SDK survey covered 12 packages and identified broad capability families beyond auth/storage, including Firestore, Realtime Database, analytics/telemetry, messaging, remote config, app check, performance monitoring, callable functions, and AI inference.

Research recommends a docs-friendly Firebase subset of 4 capabilities / 11 operations. For this repo we still need to normalize those findings into the branch vocabulary and schema constraints (for example `document_database` vs `document_db`, `analytics` vs `telemetry`, listener-style names vs architectural operation verbs).

## Firebase Capability Analysis — HopperTribe-Partner

**Repository**: https://github.com/Entropy1-ai/HopperTribe-Partner
**Packages**: `firebase` ^12.8.0 (client), `firebase-admin` ^13.0.0 + `firebase-functions` ^6.3.0 (server), `@capacitor-firebase/authentication` ^8.1.0 (native)

### Firebase Services Actually Used

1. **Firebase Auth** (client): `initializeAuth`, `onAuthStateChanged`, `signInWithEmailAndPassword`, `createUserWithEmailAndPassword`, `signInWithPopup` (Google), `signInWithPhoneNumber`, `signInWithCustomToken`, `signInWithCredential`, `RecaptchaVerifier`, `PhoneAuthProvider`, `EmailAuthProvider`, `linkWithCredential`, `updateProfile`, `updateEmail`, `verifyBeforeUpdateEmail`, `updatePassword`, `sendPasswordResetEmail`, `fetchSignInMethodsForEmail`, `deleteUser`, `GoogleAuthProvider`
2. **Firebase Auth** (server/admin): `getAuth`, `getUserByEmail`, `createCustomToken`, `updateUser`
3. **Cloud Firestore** (client): `getFirestore`, `collection`, `addDoc`, `query`, `where`, `getDocs`, `doc`, `updateDoc`, `getDoc`, `setDoc`, `collectionGroup`, `deleteDoc`, `deleteField`, `limit`
4. **Cloud Firestore** (server/admin): `getFirestore`, `FieldValue`, `collectionGroup`, collection/doc CRUD
5. **Cloud Storage** (client): `getStorage`, `ref`, `uploadBytes`, `getDownloadURL`
6. **Cloud Functions** (client invocation): `getFunctions`, `httpsCallable` — calls `sendEmailOTP`, `verifyEmailOTP`, `verifyEmailOTPAndLogin`, `disableUserAccount`, `manualGenerateCatalogs`
7. **Cloud Functions** (server definitions): `onCall` (5 callable functions), `onSchedule` (1 weekly cron)
8. **App Check** (client, currently disabled): `initializeAppCheck`, `ReCaptchaV3Provider`

### Capability Mapping to schema.json

#### Capabilities that map to existing families (3 families)

**`http_endpoint`** — Server-side callable Cloud Functions (firebase-functions v2)
- Operation: `callable_function`
- absolute_paths: `firebase-functions/v2/https.onCall`
- concept: CallExpression, target_level: function, base_confidence: 0.95, startpoint: true
- 5 instances in repo: sendEmailOTP, verifyEmailOTP, verifyEmailOTPAndLogin, disableUserAccount, manualGenerateCatalogs

**`scheduled_task`** — Server-side scheduled Cloud Functions
- Operation: `scheduled_function`
- absolute_paths: `firebase-functions/v2/scheduler.onSchedule`
- concept: CallExpression, target_level: function, base_confidence: 0.95, startpoint: true
- 1 instance in repo: generateExperienceCatalogs (weekly Sunday 2:00 AM IST)

**`http_client`** — Client-side invocation of callable Cloud Functions
- Operation: `callable_invoke`
- absolute_paths: `firebase/functions.httpsCallable`
- concept: CallExpression, target_level: function, base_confidence: 0.85, startpoint: false
- 5 instances in repo: matching the 5 onCall functions above
- Note: lower confidence because httpsCallable is often wrapped in helper functions

#### Capabilities with NO matching schema family (gaps)

| Firebase Service | Suggested Family | Key Operations Used |
|---|---|---|
| Firestore (client) | `document_database` | `addDoc`, `getDoc`, `getDocs`, `setDoc`, `updateDoc`, `deleteDoc`, `query`, `where`, `collectionGroup`, `limit` — heaviest usage (~25 service functions) |
| Firestore (admin) | `document_database` | `getFirestore`, `FieldValue`, `collectionGroup` — server-side via Admin SDK |
| Auth (client) | `authentication` | `initializeAuth`, `onAuthStateChanged`, `signInWithEmailAndPassword`, `signInWithPopup`, `signInWithPhoneNumber`, `signInWithCustomToken`, `createUserWithEmailAndPassword` — 6+ sign-in strategies |
| Auth (admin) | `authentication` | `getAuth`, `getUserByEmail`, `createCustomToken`, `updateUser` — server-side auth management |
| Storage (client) | `object_storage` | `getStorage`, `uploadBytes`, `getDownloadURL` — single `uploadFile` helper for homestay images |
| App Check (client) | `security` / `app_check` | `initializeAppCheck`, `ReCaptchaV3Provider` — currently disabled in this repo |

### Detector JSON for Existing Capabilities

All detectors use `concept: CallExpression` — Firebase SDK uses factory function patterns throughout.

```json
{
  "http_endpoint": {
    "operations": {
      "callable_function": {
        "description": "Defines an HTTPS callable Cloud Function.",
        "docs_url": "https://firebase.google.com/docs/functions/callable",
        "absolute_paths": ["firebase-functions/v2/https.onCall"],
        "target_level": "function",
        "concept": "CallExpression",
        "base_confidence": 0.95,
        "startpoint": true,
        "notes": "Variable name becomes the deployed function name."
      }
    }
  },
  "scheduled_task": {
    "operations": {
      "scheduled_function": {
        "description": "Defines a scheduled Cloud Function on a cron schedule.",
        "docs_url": "https://firebase.google.com/docs/functions/schedule-functions",
        "absolute_paths": ["firebase-functions/v2/scheduler.onSchedule"],
        "target_level": "function",
        "concept": "CallExpression",
        "base_confidence": 0.95,
        "startpoint": true,
        "notes": "Config object has schedule (cron), timeZone, and resource fields."
      }
    }
  },
  "http_client": {
    "operations": {
      "callable_invoke": {
        "description": "Creates a callable ref to invoke a Cloud Function over HTTPS.",
        "docs_url": "https://firebase.google.com/docs/functions/callable#call_the_function",
        "absolute_paths": ["firebase/functions.httpsCallable"],
        "target_level": "function",
        "concept": "CallExpression",
        "base_confidence": 0.85,
        "startpoint": false,
        "notes": "Returns a wrapper; often wrapped in helper functions hence lower confidence."
      }
    }
  }
}
```

AC #2 update (2026-04-10): Synced published docs schema assets to ingestion contract by replacing `unoplat-code-confluence-docs/public/schemas/custom-framework-lib-schema-v4.json` and `custom-framework-lib-schema.json` with the canonical operation-level schema from `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/schema.json`.

Resulting published schemas now use capability -> operation with operation-level `absolute_paths`, `target_level`, `concept` directly, and no nested `detectors` object.

Removed unsupported/legacy constructs from published docs assets: `detectorDef`, `detectorKeyDef`, and `operationKindEnum`.

Validation checks run:
- `diff -u ingestion/schema.json docs/public/schemas/custom-framework-lib-schema-v4.json` -> no diff
- `diff -u ingestion/schema.json docs/public/schemas/custom-framework-lib-schema.json` -> no diff
- grep for `detectors|detectorDef|detectorKeyDef|operationKindEnum` in `docs/public/schemas` -> no matches
- `jq empty` parse check for both docs schema files -> pass

Firebase implementation update (2026-04-10): added `unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions/typescript/firebase.json` with operation-level capability coverage including Cloud Functions families (`rpc_server`, `rest_api`, `rpc_client`, `http_client`, `scheduler`, `change_data_capture`, `job_queue`) plus core Firebase (`authentication`, `document_database`, `object_storage`, `telemetry`). Operation names follow intuitive action naming (`call`, `request`, `invoke`, `schedule`, etc.) and use multiple operations where needed.

Updated ingestion integration expectations in `tests/integration/test_framework_definitions_ingestion.py` after adding Firebase: frameworks 12, features 58, absolute paths 128 (from parser output via `FrameworkDefinitionLoader.parse_json_data`).

Updated contribution docs Firebase example only (compact operation-level example + vetted capability/operation map callout) in `unoplat-code-confluence-docs/content/docs/contribution/custom-framework-schema/index.mdx`, keeping broader guidance untouched.

Docs sync run: `cd unoplat-code-confluence-docs && bun run sync:framework-definitions` generated Firebase artifacts/pages including `public/framework-definitions/typescript/firebase.json`, `public/framework-definitions/language-index.json`, `content/docs/supported-frameworks/typescript/meta.json`, and `content/docs/supported-frameworks/typescript/firebase.mdx`.

Validation run results for AC #4: `task validate-single-framework FILE=framework-definitions/typescript/firebase.json` ✅, `task validate-framework-definitions` ✅, `uv run pytest tests/integration/test_framework_definitions_ingestion.py` ✅ (14 passed), `bun run types:check` ✅, `bun run build` ✅ (prerender included `/docs/supported-frameworks/typescript/firebase` and `/framework-definitions/typescript/firebase.json`).
<!-- SECTION:NOTES:END -->
