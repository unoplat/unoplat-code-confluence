# Business Domain References

## Domain Summary
This frontend supports a code-analysis and repository-operations platform that onboards GitHub/GitLab repositories, captures codebase metadata, runs ingestion and AI-agent workflows, and tracks repository/codebase job status, events, errors, and generated Agent MD snapshots. It also manages provider credentials, OAuth, model and tool configuration, while collecting application and per-agent feedback that can be submitted as GitHub issues.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/api.ts#L17-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/api.ts#L27-L35`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts#L13-L14`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts#L26-L27`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/schema.ts#L48-L49`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/store.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/store.ts#L15-L20`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/agent-feedback/store.ts#L25-L36`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/api.ts#L12-L19`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/api.ts#L25-L28`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/schema.ts#L18-L19`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/store.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/app-feedback/store.ts#L3-L8`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/provider-schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/provider-schema.ts#L65-L67`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/provider-schema.ts#L69-L71`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/schema-generator.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/schema-generator.ts#L167-L169`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/types.ts#L20-L28`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/model-config/types.ts#L36-L39`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L16-L20`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L22-L25`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L140-L142`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L143-L145`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/collection.ts#L146-L148`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts#L26-L34`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts#L36-L44`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/hooks.ts#L46-L56`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L36-L38`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L49-L51`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L57-L59`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L77-L79`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L86-L88`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L94-L96`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L104-L106`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L121-L123`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/schema.ts#L199-L201`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/transformers.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/transformers.ts#L10-L13`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/repository-agent-snapshots/transformers.ts#L17-L26`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/tool-config/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/features/tool-config/types.ts#L35-L37`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/forms/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/forms/types.ts#L6-L13`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/use-data-table.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/use-data-table.ts#L45-L68`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useCodexOauth.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useCodexOauth.ts#L10-L14`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveModelConfig.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveModelConfig.ts#L9-L12`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveModelConfig.ts#L14-L17`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveToolConfig.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveToolConfig.ts#L9-L12`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/hooks/useSaveToolConfig.ts#L14-L16`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-events-utils.ts#L313-L318`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-md-to-markdown.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/agent-md-to-markdown.ts#L8-L10`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L55-L58`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L61-L63`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L69-L74`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L189-L194`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L419-L425`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L503-L513`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L518-L524`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L626-L628`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L630-L634`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L636-L640`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L642-L649`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L651-L654`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L731-L737`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L742-L746`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L788-L805`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L807-L810`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L812-L817`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L819-L821`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L823-L826`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L828-L833`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L835-L838`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api.ts#L843-L848`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repositories-api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repositories-api.ts#L5-L10`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repository-provider-api.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repository-provider-api.ts#L31-L33`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/api/repository-provider-api.ts#L35-L38`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/env.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/env.ts#L7-L32`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/github-token-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/github-token-utils.ts#L10-L13`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-route-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-route-utils.ts#L6-L10`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/utils/provider-utils.ts#L147-L152`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/validation/credential-schemas.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/lib/validation/credential-schemas.ts#L101-L103`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L85-L97`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L98-L109`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L110-L124`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L125-L166`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L167-L172`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L175-L260`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L263-L266`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/routeTree.gen.ts#L277-L284`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useAuthStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useAuthStore.ts#L5-L9`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useCommandPaletteStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useCommandPaletteStore.ts#L3-L8`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useDevModeStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useDevModeStore.ts#L4-L7`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useThemeStore.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/stores/useThemeStore.ts#L6-L9`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L4-L10`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L13-L19`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L22-L27`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L30-L33`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L36-L41`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L43-L51`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L53-L56`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L58-L63`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L65-L68`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L71-L78`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L80-L88`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L91-L93`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L96-L99`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L101-L104`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L106-L113`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L119-L128`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L130-L135`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L137-L139`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L146-L149`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L152-L156`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L162-L170`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L173-L176`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L179-L191`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L194-L196`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L201-L207`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L218-L222`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L227-L243`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L246-L253`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L256-L264`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L267-L270`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L273-L276`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L279-L281`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L284-L295`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L311-L315`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L317-L319`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types.ts#L322-L327`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L6-L12`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L17-L20`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L25-L28`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L33-L37`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L43-L47`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L49-L54`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L56-L58`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L63-L66`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-events.ts#L71-L73`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L21-L25`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L30-L39`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L49-L54`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/agent-feedback.ts#L83-L86`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/credential-enums.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/credential-enums.ts#L49-L55`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/credential-enums.ts#L60-L62`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L7-L9`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L12-L21`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L24-L30`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L32-L37`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L43-L45`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L47-L49`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/data-table.ts#L51-L54`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L1-L13`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L17-L19`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L21-L26`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L28-L31`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L33-L38`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/index.ts#L40-L48`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts#L6-L8`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts#L13-L17`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-frontend/src/types/repository-provider.ts#L22-L26`
