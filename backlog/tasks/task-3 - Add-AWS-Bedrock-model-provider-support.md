---
id: TASK-3
title: Add AWS Bedrock model provider support
status: In Progress
assignee: []
created_date: '2026-03-02 06:46'
labels:
  - ai-model-config
  - backend
  - frontend
dependencies: []
references:
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/provider_catalog.py
  - >-
    unoplat-code-confluence-query-engine/src/unoplat_code_confluence_query_engine/services/config/model_factory.py
  - >-
    unoplat-code-confluence-frontend/src/features/model-config/components/ModelConfigurationSection.tsx
documentation:
  - 'https://ai.pydantic.dev/models/bedrock/'
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expose AWS Bedrock as a selectable model provider in model configuration and wire backend model factory creation for Bedrock models with automatic Anthropic prompt caching defaults.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bedrock appears in /v1/providers with required model and credential-related fields for frontend rendering.
- [ ] #2 ModelFactory can build a BedrockConverseModel when provider_key is bedrock using supported BedrockProvider authentication options.
- [ ] #3 For Bedrock Anthropic model IDs, model settings automatically enable comprehensive Bedrock caching (instructions, tool definitions, messages).
- [ ] #4 Existing providers and model configuration flows continue to work without regression.
<!-- AC:END -->
