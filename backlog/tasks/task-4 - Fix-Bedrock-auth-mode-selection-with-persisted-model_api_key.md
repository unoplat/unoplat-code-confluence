---
id: TASK-4
title: Fix Bedrock auth mode selection with persisted model_api_key
status: Done
assignee: []
created_date: '2026-03-02 07:40'
updated_date: '2026-03-02 12:09'
labels:
  - bugfix
  - bedrock
  - auth
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure Bedrock provider construction does not force bearer-token auth when a stale/non-Bedrock global model_api_key exists. Preserve IAM/profile/default credential chain flows unless user explicitly provides Bedrock bearer token for this provider.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Scoped persisted `model_api_key` metadata by provider at write time (`provider_key` in credential metadata).

Updated Bedrock build logic to only use persisted `model_api_key` when scoped to `bedrock`; otherwise ignore and fall back to IAM/profile/env chain.

Kept AWS access-key mode strict: when `aws_access_key_id` is set, requires a Bedrock-scoped secret value.

Updated Bedrock provider help text to clarify that keys saved for other providers are ignored.

Validation run: `uv run basedpyright` and `uv run ruff check` on modified backend files passed.
<!-- SECTION:FINAL_SUMMARY:END -->
