---
id: TASK-5
title: Support multiple saved model-provider configurations
status: To Do
assignee: []
created_date: '2026-03-02 12:09'
updated_date: '2026-03-19 09:57'
labels:
  - feature
  - model-config
  - backend
  - frontend
dependencies: []
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design and implement per-provider (or named-profile) model configuration + credential persistence so users can keep multiple provider setups and switch without overwriting credentials/config. Replace current single-record `ai_model_config` + shared model credential behavior with explicit selection of active config.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Users can save configurations for at least two different providers without overwriting each other.
- [ ] #2 Switching active provider does not require re-entering credentials if already saved for that provider.
- [ ] #3 API exposes list/get/save/select/delete operations for multiple model configs.
- [ ] #4 Frontend allows selecting among saved provider configs and indicates which is active.
- [ ] #5 Worker/model runtime uses credentials tied to the selected active config only.
- [ ] #6 Migration path preserves existing single active config as one saved config entry.
<!-- AC:END -->
