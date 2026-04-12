# Requirements Document

## Introduction

The Unoplat Code Confluence Context Engine exists to enable **sustainable and reliable use of AI for maximum engineering productivity**. Rather than AI agents burning context windows on exploration and guessing at codebase conventions, the Context Engine provides them with verified, structured, and actionable knowledge — turning every AI interaction into a productive one.

The system is built around four pillars:

1. **Accurate context** — Generates AGENTS.md files containing engineering workflow commands, dependency guides, business logic domain analysis, and application construct identification
2. **Trusted commands** — Engineering commands validated through sandbox execution with auto-generated task runner configuration files
3. **Right skills** — Agent Skills recommendations from the open ecosystem ([agentskills.io](https://agentskills.io)) matched to codebase context
4. **Self-hostable, reliable, and auditable** — Fully self-hostable with durable workflows, retry policies, structured audit logs, and complete traceability across all operations

The Context Engine operates in two phases. The **Ingestion Phase** parses source code into structural signatures, detects framework-specific patterns using declarative definitions, and stores code structure in a database for downstream analysis. The **Generation Phase** uses LLM-based agents to analyze ingested data and produce AGENTS.md sections, with each agent scoped to a single section. Updates are applied through section-scoped updaters and delivered via pull requests.

The system builds trust progressively through a pipeline: **Extraction** → **Confidence Scoring** → **Sandbox Validation** → **Taskfile Generation** → **Skill Recommendation**. Each stage adds a layer of verification — from LLM-extracted commands with confidence scores, to sandbox-validated commands that are proven to work, to auto-generated task runner configurations, to recommended agent skills matched to the codebase context.

## Glossary

- **Context_Engine**: The system that analyzes codebases and generates AGENTS.md files across two phases (ingestion + generation)
- **AGENTS_MD_File**: A machine-readable file containing structured context about a codebase
- **Structural_Signature_Extractor**: Component that parses source code into syntax trees and extracts structural signatures (functions, classes, imports, types)
- **Framework_Detection_Service**: Component that recognizes framework-specific patterns based on declarative framework definitions
- **Workflow_Orchestrator**: Durable workflow engine that manages scalable, auditable, and reliable task processing with retry policies
- **Repository**: A code repository to be analyzed
- **Domain_Entity**: Business logic objects representing core application concepts
- **Database_Entity**: Data models representing database structures
- **Engineering_Workflow**: Canonical commands for install, build, dev, test, lint, and type checking
- **Context_Metadata**: Structured information about dependencies, interfaces, domain models, and data store models
- **Application_Construct**: Any inbound or outbound interface through which an application communicates with the external world. Detected by extending the existing Custom Framework/Library Schema ([docs.unoplat.io/docs/contribution/custom-framework-schema](https://docs.unoplat.io/docs/contribution/custom-framework-schema)) with construct direction and type classification:
  - **Inbound constructs**: REST endpoints, GraphQL resolvers, gRPC service methods, message consumers, WebSocket handlers, CLI commands, event handlers, scheduled job handlers, webhook receivers
  - **Outbound constructs**: HTTP client calls, gRPC client calls, message producers, database queries, external API calls, notification senders
- **Construct_Specification**: An extension of the existing open-source Custom Framework/Library Schema that adds construct direction (inbound/outbound) and construct type classification to the current `startpoint` boolean field. The existing schema already supports import-gated, regex-based detection using concept types (AnnotationLike, CallExpression, Inheritance) across Python, TypeScript, JavaScript, Java, and Go — this extension expands it from marking entry points (`startpoint: true`) to classifying ALL application boundary constructs with direction and type metadata
- **LLM_Agent**: An AI agent powered by a large language model, used as the primary extraction mechanism in the generation phase. Each agent is scoped to a specific AGENTS.md section
- **Section_Updater**: An LLM_Agent that updates a single section heading in AGENTS.md without modifying content outside its section boundary
- **Confidence_Score**: A numerical score (0.0–1.0) assigned to extracted information, indicating the level of evidence behind it. Used to filter low-confidence results before inclusion in AGENTS.md
- **Sandbox_Validator** [Future]: An isolated execution environment for validating engineering workflow commands against the actual codebase
- **Taskfile_Generator** [Future]: Component that produces a task runner configuration file from sandbox-validated commands
- **Agent_Skill**: A reusable capability package following the Agent Skills open spec ([agentskills.io](https://agentskills.io)). A directory with a SKILL.md file containing metadata and instructions, installable from the [skills.sh](https://skills.sh) marketplace. Supported by 20+ AI coding tools
- **Skill_Recommendation_Engine** [Future]: Component that matches codebase context (frameworks, dependencies, commands) to Agent_Skills from the open ecosystem
- **Framework_Definition**: A declarative specification following the Custom Framework/Library Schema ([docs.unoplat.io/docs/contribution/custom-framework-schema](https://docs.unoplat.io/docs/contribution/custom-framework-schema)) describing framework-specific patterns using concept types (AnnotationLike, CallExpression, Inheritance), import-gated detection, and regex-based pattern matching
- **Language_Processor**: A pluggable module for language-specific structural extraction, following the strategy pattern
- **Sync_Engine**: Component that detects codebase changes and triggers incremental re-analysis to keep AGENTS.md current
- **User_Instructions**: Custom per-repository instructions provided by the developer to guide how the Context Engine analyzes and generates AGENTS.md for that specific codebase, covering preferences for engineering workflow conventions, dependency categorization, business domain terminology, and construct identification priorities

## Requirements

### Requirement 1: Structural Signature Extraction

**User Story:** As a system architect, I want the ingestion phase to parse source code into structural signatures, so that code structure is extracted consistently and accurately across programming languages.

#### Acceptance Criteria

1. THE Structural_Signature_Extractor SHALL parse source code files into concrete syntax trees
2. WHEN extracting structural signatures, THE Structural_Signature_Extractor SHALL identify function definitions (name, parameters, return type, docstring, decorators, positions), class definitions (name, base classes, methods, attributes), import statements, and type definitions
3. WHEN parsing fails for a file, THE Structural_Signature_Extractor SHALL log the error and continue processing other files
4. THE ingestion phase SHALL store extracted structural signatures in a database for downstream consumption by LLM_Agents

### Requirement 2: Framework-Aware Detection

**User Story:** As a developer working with frameworks, I want the ingestion phase to detect framework-specific patterns using the Custom Framework/Library Schema, so that framework usage is accurately captured.

#### Acceptance Criteria

1. THE Framework_Detection_Service SHALL load Framework_Definitions following the Custom Framework/Library Schema ([docs.unoplat.io/docs/contribution/custom-framework-schema](https://docs.unoplat.io/docs/contribution/custom-framework-schema)) from a configurable directory at startup
2. WHEN framework dependencies are detected in package manager files, THE Framework_Detection_Service SHALL apply import-gated, regex-based detection using concept types: AnnotationLike, CallExpression, and Inheritance
3. THE Framework_Detection_Service SHALL support extensible framework definitions — adding a new framework SHALL require only adding a new definition file following the schema, not modifying core code
4. WHEN a Framework_Definition specifies a construct as an entry point (via `startpoint` or extended construct metadata), THE detection SHALL mark it as an Application_Construct
5. THE Framework_Detection_Service SHALL store detection results in the database alongside structural signatures

### Requirement 3: Multi-Language Ingestion Support

**User Story:** As a developer working with polyglot codebases, I want the ingestion phase to support multiple programming languages via pluggable Language_Processors, so that all supported languages in my repository are analyzed.

#### Acceptance Criteria

1. THE ingestion pipeline SHALL support Python source code analysis with full structural signatures, import extraction, framework detection, and data model detection
2. THE ingestion pipeline SHALL support TypeScript source code analysis (partial: data model detection in v1, full structural signatures in v2)
3. THE ingestion pipeline SHALL use a strategy-pattern Language_Processor, where each language implements its own extraction logic
4. WHEN analyzing a Repository with multiple languages, THE ingestion pipeline SHALL process all supported language files using the appropriate Language_Processor
5. WHEN encountering an unsupported language file, THE ingestion pipeline SHALL skip the file and log a warning

### Requirement 4: Ingestion Discovery and File Processing

**User Story:** As a developer, I want the ingestion phase to efficiently discover and process source files, so that analysis completes in reasonable time even for large codebases.

#### Acceptance Criteria

1. WHEN analyzing a Repository, THE ingestion pipeline SHALL use efficient file discovery to detect codebases and their languages
2. WHEN processing source files, THE Language_Processor SHALL support configurable concurrency for parallel file processing
3. WHEN analyzing a Repository, THE ingestion pipeline SHALL skip binary files, generated code, and files matching ignore patterns
4. THE ingestion pipeline SHALL calculate file checksums for change tracking
5. THE ingestion pipeline SHALL store processed file data in the database with structural signatures, imports, framework detections, and data model metadata

### Requirement 5: AGENTS.md Generation via LLM Agents

**User Story:** As a developer, I want the Context Engine to generate and update AGENTS.md files per codebase using LLM_Agents, so that AI coding agents have accurate, structured context about my codebase.

#### Acceptance Criteria

1. WHEN a Repository is provided to the Context_Engine, THE generation phase SHALL produce a codebase-local AGENTS_MD_File containing structured sections for: Engineering Workflow, Dependency Guide, Business Logic Domain, and Application Constructs
2. WHEN generating an AGENTS_MD_File, THE Context_Engine SHALL use specialized LLM_Agents, each scoped to a specific section
3. WHEN an LLM_Agent runs for a section, IT SHALL use the Section_Updater pattern where each run is scoped to a single section heading and SHALL NOT modify content outside that section boundary
4. WHEN updating AGENTS.md, THE Section_Updater SHALL enforce path safety — only modifying files within the codebase root
5. WHEN an AGENTS_MD_File is generated, THE output SHALL be machine-readable, structured markdown parseable by AI coding agents

### Requirement 6: Engineering Workflow Extraction

**User Story:** As a developer, I want the Context Engine to identify canonical engineering commands with evidence-based confidence, so that AI agents know how to build, test, and run my application.

#### Acceptance Criteria

1. WHEN analyzing a Repository, THE engineering workflow LLM_Agent SHALL inspect configuration files to extract commands for stages: install, build, dev, test, lint, and type_check
2. EACH extracted command SHALL include a Confidence_Score (0.0–1.0) validated against official documentation via web search
3. THE Context_Engine SHALL filter out commands below a configurable confidence threshold
4. THE Context_Engine SHALL deduplicate commands by (stage, command), retaining the highest Confidence_Score
5. THE Context_Engine SHALL normalize configuration file paths to repository-relative format
6. THE LLM_Agent SHALL receive language-specific instructions supporting Python, TypeScript, and additional languages as they are added

### Requirement 7: Dependency Guide Generation

**User Story:** As a developer, I want the Context Engine to document external dependencies with purpose and usage from official documentation, so that AI agents understand how third-party libraries are used.

#### Acceptance Criteria

1. WHEN analyzing a Repository, THE generation phase SHALL extract dependency names from the ingested metadata
2. THE dependency guide LLM_Agent SHALL process each dependency, producing a description with purpose (from official docs) and usage (how it's used in this codebase)
3. WHEN web search returns no official documentation for a dependency, THE LLM_Agent SHALL mark it as an internal dependency and skip documentation
4. WHEN a single dependency fails to document, THE workflow SHALL continue processing remaining dependencies
5. THE generation phase SHALL aggregate all dependency entries into a structured Dependency Guide section

### Requirement 8: Business Logic Domain Analysis

**User Story:** As a developer, I want the Context Engine to analyze data models and describe the business logic domain, so that AI agents understand the core domain of my codebase.

#### Acceptance Criteria

1. THE business domain LLM_Agent SHALL retrieve all data model file paths and line spans from the ingested metadata
2. THE LLM_Agent SHALL inspect ALL data model files to synthesize a domain summary
3. THE LLM_Agent SHALL return a concise plain text description summarizing the dominant business logic domain
4. THE output validator SHALL reject empty outputs and structured formats (JSON, markdown) — only plain text is accepted
5. THE workflow SHALL enrich the business logic output with data model file references from the ingested metadata

### Requirement 9: Application Construct Identification

**User Story:** As a developer, I want the Context Engine to identify ALL inbound and outbound application constructs by extending the existing Custom Framework/Library Schema, so that AI agents understand the complete application boundary.

#### Acceptance Criteria

1. THE Context_Engine SHALL extend the existing Custom Framework/Library Schema ([docs.unoplat.io/docs/contribution/custom-framework-schema](https://docs.unoplat.io/docs/contribution/custom-framework-schema)) to support construct direction and type classification — evolving the current `startpoint` boolean into a richer construct metadata model
2. THE extended schema SHALL categorize **inbound constructs**: REST endpoints, GraphQL resolvers, gRPC service methods, message consumers, WebSocket handlers, CLI commands, event handlers, scheduled job handlers, and webhook receivers
3. THE extended schema SHALL categorize **outbound constructs**: HTTP client calls, gRPC client calls, message producers, database queries, external API calls, and notification senders
4. THE construct identification SHALL leverage the existing import-gated, regex-based detection mechanism (concept types: AnnotationLike, CallExpression, Inheritance) already in Framework_Definitions
5. THE identified constructs SHALL be written to the Application Constructs section of AGENTS.md with construct type, protocol, path/topic, handler reference, and direction (inbound/outbound)
6. THE Construct_Specification SHALL remain extensible — adding detection for a new construct type SHALL require only updating Framework_Definition files, not modifying core detection logic

### Requirement 10: Durable Workflow Orchestration

**User Story:** As a system administrator, I want the Context Engine to use a durable workflow orchestrator, so that ALL processing is reliable, auditable, and scalable.

#### Acceptance Criteria

1. THE Context_Engine SHALL use a Workflow_Orchestrator to manage ALL processing pipelines (ingestion and generation) with reliability and auditability guarantees
2. THE Workflow_Orchestrator SHALL support parent-child workflow patterns: a parent workflow per repository orchestrating parallel child workflows per codebase
3. WHEN processing a codebase, THE child workflow SHALL execute LLM_Agents in a defined sequence, with each agent followed by its Section_Updater
4. WHEN an LLM_Agent fails within a child workflow, THE workflow SHALL collect the error and continue processing subsequent agents (continue-and-collect strategy)
5. WHEN a processing task fails with a transient error, THE Workflow_Orchestrator SHALL retry according to configured retry policies
6. WHEN processing completes, THE Workflow_Orchestrator SHALL log audit information including start time, end time, status, errors, and usage statistics — ensuring every workflow run is fully traceable
7. THE Workflow_Orchestrator SHALL persist results before propagating errors, ensuring partial output is never lost
8. ALL workflow executions SHALL be durable — surviving process restarts, network failures, and infrastructure interruptions without losing progress

### Requirement 11: Usage Statistics Tracking

**User Story:** As a system administrator, I want the Context Engine to track LLM usage statistics per agent and per codebase, so that I can monitor costs and resource consumption.

#### Acceptance Criteria

1. THE system SHALL track per-agent usage statistics including: requests, input tokens, output tokens, cache tokens, and estimated cost
2. THE child workflow SHALL aggregate statistics from all agents in a codebase
3. THE parent workflow SHALL build repository-level statistics with totals and per-codebase breakdown
4. WHEN an agent fails, THE workflow SHALL contribute zero statistics for that agent
5. THE usage statistics SHALL be persisted as part of the workflow output

### Requirement 12: Real-Time Progress Streaming

**User Story:** As a developer using the frontend, I want real-time progress updates during agent execution, so that I can see what is happening without polling.

#### Acceptance Criteria

1. THE Context_Engine SHALL stream agent execution events to the frontend in real-time using server-sent events
2. THE event stream SHALL include named events identifying: codebase, agent, and execution phase (tool calls, tool results, final results)
3. THE Context_Engine SHALL compute per-codebase progress as a percentage based on completed agents
4. THE Context_Engine SHALL compute overall repository progress as the average of all codebase progress values
5. WHEN event persistence fails, THE system SHALL log the error but NOT interrupt agent execution (non-critical path)

### Requirement 13: Pull Request Creation for AGENTS.md

**User Story:** As a developer, I want the Context Engine to create a pull request with the generated AGENTS.md files, so that changes are reviewed before merging into the repository.

#### Acceptance Criteria

1. THE PR creation SHALL implement one-shot semantics: the first successful publish creates the PR; all subsequent calls for the same workflow run return the existing PR
2. THE system SHALL create a feature branch from the default branch for each workflow run
3. BEFORE creating a PR, THE system SHALL check for an existing open PR on the branch
4. THE system SHALL compare local file content with remote content and skip unchanged files
5. THE system SHALL only publish files that were actually changed by Section_Updaters, with deduplication for files touched by multiple sections
6. THE PR metadata persistence SHALL use row-level locking to prevent concurrent publish races

### Requirement 14: Modular and Extensible Architecture

**User Story:** As a system architect, I want the Context Engine to have a modular architecture, so that new languages, frameworks, and construct types can be added without modifying core components.

#### Acceptance Criteria

1. THE ingestion phase SHALL separate language-specific parsing into pluggable Language_Processor modules with a defined interface
2. THE ingestion phase SHALL separate framework-specific detection into declarative Framework_Definition files loaded at startup
3. WHEN adding support for a new language, a developer SHALL create a new Language_Processor without modifying the generic parser
4. WHEN adding support for a new framework, a developer SHALL create a new Framework_Definition file and it SHALL be loaded automatically at startup
5. THE generation phase agents SHALL be registry-based, allowing agents to be enabled or disabled without code changes
6. THE Construct_Specification SHALL be extensible — new construct types SHALL require only definition updates, not core code changes

### Requirement 15: Error Handling and Logging

**User Story:** As a system administrator, I want the Context Engine to handle errors gracefully with continue-and-collect strategy, so that partial failures do not prevent generation of available context.

#### Acceptance Criteria

1. WHEN a parsing error occurs for a file in the ingestion phase, THE Language_Processor SHALL log the error and continue processing other files
2. WHEN an LLM_Agent fails within the generation workflow, THE workflow SHALL collect the error and continue with subsequent agents
3. WHEN a single dependency fails to document, THE workflow SHALL log the warning and continue with remaining dependencies
4. THE system SHALL use structured logging with trace context propagated across workflow steps
5. WHEN all agents in a codebase have completed with errors, THE workflow SHALL persist partial results BEFORE raising errors

### Requirement 16: Configuration Management

**User Story:** As a developer, I want to configure Context Engine behavior including model providers, tool credentials, and analysis options, so that the system adapts to different environments.

#### Acceptance Criteria

1. THE system SHALL support AI model configuration with provider and model settings
2. THE system SHALL support tool credential configuration for web search and other external tools
3. THE system SHALL resolve search capabilities dynamically based on configured providers
4. THE system SHALL support configurable usage limits for agent execution
5. THE ingestion phase SHALL support configurable framework definition loading

### Requirement 17: TypeScript Framework Parsing

**User Story:** As a TypeScript developer, I want the ingestion phase to detect TypeScript framework patterns, so that my TypeScript codebases get framework-aware analysis.

#### Acceptance Criteria

1. THE ingestion pipeline SHALL add Framework_Definitions for TypeScript frameworks (e.g., Express, NestJS, Next.js, Prisma)
2. THE Framework_Detection_Service SHALL apply TypeScript-specific concept detection using the same concept types as other languages
3. THE TypeScript Language_Processor SHALL support both .ts and .tsx files
4. It should also be able to identify programming constructs that help in identifying business entities. 

### Requirement 18: Go Language and Framework Support
**User Story:** As a Go developer, I want the ingestion phase to parse Go code and detect Go framework patterns, so that my Go codebases get full analysis.

#### Acceptance Criteria

1. THE ingestion pipeline SHALL create a Go Language_Processor
3. THE ingestion pipeline SHALL add Framework_Definitions for Go frameworks (e.g., Gin, Echo, GORM)
3. It should also be able to identify programming constructs that help in identifying business entities. 

### Requirement 19: Java Language and Framework Support
**User Story:** As a Java developer, I want the ingestion phase to parse Java code and detect Java framework patterns, so that my Java codebases get full analysis.

#### Acceptance Criteria

1. THE ingestion pipeline SHALL create a Java Language_Processor
2. THE ingestion pipeline SHALL add Framework_Definitions for Java frameworks (e.g., Spring Boot, Hibernate, Jakarta EE)
3. THE ingestion pipeline SHALL add a Java codebase detector
4. It should also be able to identify programming constructs that help in identifying business entities. 

### Requirement 20: Extended Engineering Workflow for All Languages
**User Story:** As a Go or Java developer, I want the engineering workflow agent to extract build, test, and run commands specific to my language ecosystem, so that my AGENTS.md has accurate workflow guidance.

#### Acceptance Criteria

1. THE engineering workflow LLM_Agent SHALL include Go-specific command discovery patterns (Makefile, task runner, Go toolchain conventions)
2. THE engineering workflow LLM_Agent SHALL include Java-specific command discovery patterns (Maven, Gradle, wrapper scripts)
3. THE agent SHALL include language-specific examples for each supported language
4. THE engineering workflow stages (install, build, dev, test, lint, type_check) SHALL remain language-agnostic

### Requirement 21: Sandbox Command Validation
**User Story:** As a developer, I want engineering workflow commands to be validated through sandbox execution, so that the commands in my AGENTS.md are TRUSTED and verified to actually work.

#### Acceptance Criteria

1. THE system SHALL provide a Sandbox_Validator capable of executing engineering workflow commands in an isolated environment
2. AFTER the engineering workflow LLM_Agent produces commands with Confidence_Scores, THE Sandbox_Validator SHALL execute each command against the actual codebase
3. THE Sandbox_Validator SHALL record execution results: exit code, stdout/stderr (truncated), execution time, and resource usage
4. WHEN a command succeeds in the sandbox (exit code 0), ITS status SHALL be upgraded to "sandbox_validated", which is authoritative and replaces LLM-only confidence scoring
5. WHEN a command fails in the sandbox, THE system SHALL record the failure and either exclude the command or mark it with "sandbox_failed" status
6. THE sandbox environment SHALL support language-specific toolchains for all supported languages

### Requirement 22: Taskfile Generation
**User Story:** As a developer, I want a task runner configuration file auto-generated from sandbox-validated commands, so that I have a ready-to-use, trusted configuration for local development.

#### Acceptance Criteria

1. AFTER sandbox validation completes, THE Taskfile_Generator SHALL produce a task runner configuration containing only sandbox-validated commands
2. THE generated configuration SHALL organize tasks by engineering workflow stage (install, build, dev, test, lint, type_check)
3. EACH task SHALL include: task name, command, description, and optional dependencies (e.g., install before build)
4. THE Taskfile_Generator SHALL NOT include commands that failed sandbox validation
5. THE generated file SHALL be included in the PR alongside AGENTS.md and companion artifact files

### Requirement 23: Codebase Skill Analysis & Matching
**User Story:** As a developer, I want the Context Engine to recommend which Agent_Skills from the open ecosystem are most relevant for my codebase, so that AI agents working on my code have the right capabilities installed.

#### Acceptance Criteria

1. THE Skill_Recommendation_Engine SHALL query the skills ecosystem to discover available Agent_Skills
2. THE engine SHALL match codebase context signals (detected frameworks, dependency categories, language, validated commands) to skill descriptions and metadata
3. THE engine SHALL rank skills by relevance using codebase-specific signals
4. THE engine SHALL filter out skills incompatible with the codebase's language or environment
5. THE engine SHALL support both automatic matching (framework to skill) and user-curated skill lists

### Requirement 24: Skill Recommendations Output
**User Story:** As a developer, I want AGENTS.md to include recommended Agent_Skills so that AI agents can self-discover and install relevant capabilities for my codebase.

#### Acceptance Criteria

1. THE Context_Engine SHALL generate a Recommended Skills section in AGENTS.md
2. EACH recommendation SHALL include: skill name, description, install command, why it's recommended (mapping to detected context), and confidence level
3. THE recommendations SHALL enable AI agents to self-discover and install relevant skills — closing the loop from codebase analysis to actionable agent capabilities
4. THE Skill_Recommendation_Engine SHALL NOT generate skills — it SHALL only recommend existing skills from the open ecosystem

### Requirement 25: Continuous AGENTS.md Synchronization
**User Story:** As a developer, I want AGENTS.md to stay in sync with my codebase as it evolves, so that AI agents always have current, accurate context — not stale information from the last full generation run.

#### Acceptance Criteria

1. THE Sync_Engine SHALL detect codebase changes (new files, modified files, deleted files, dependency changes) since the last generation run
2. WHEN changes are detected, THE Sync_Engine SHALL trigger incremental re-analysis of only the affected sections rather than full regeneration
3. THE Sync_Engine SHALL support event-driven triggers (e.g., post-commit hooks, CI pipeline integration, scheduled runs)
4. WHEN incremental re-analysis produces changes, THE system SHALL create a new PR with only the updated sections

### Requirement 26: Self-Hostable Deployment

**User Story:** As an organization, I want to self-host the Context Engine on my own infrastructure, so that I have full control over data, security, and operational costs.

#### Acceptance Criteria

1. THE Context_Engine SHALL be self-hostable — all components SHALL be deployable on the organization's own infrastructure without dependency on external hosted services (except for configured LLM providers and optional web search)
2. THE system SHALL provide containerized deployment artifacts for all components
3. THE system SHALL support configurable external dependencies (database, workflow orchestrator) that the organization provisions
4. THE system SHALL NOT require any proprietary SaaS dependencies for core functionality
5. ALL workflows across ingestion and generation phases SHALL provide reliability guarantees: durable execution, configurable retry policies, and graceful degradation on partial failures
6. ALL workflows SHALL provide auditability guarantees: structured logging, workflow state tracking, execution history, and per-run statistics persisted for post-hoc analysis

### Requirement 27: User-Specific Repository Instructions

**User Story:** As a developer, I want to provide custom instructions for my repository, so that the Context Engine tailors its analysis and generation to my team's specific conventions and preferences.

#### Acceptance Criteria

1. THE Context_Engine SHALL support User_Instructions per repository that guide how the system analyzes and generates AGENTS.md for that specific codebase
2. WHEN User_Instructions are provided, THE LLM_Agents SHALL incorporate them into their analysis and generation process alongside default behavior
3. THE User_Instructions SHALL be able to specify preferences for: engineering workflow conventions, dependency categorization, business domain terminology, and construct identification priorities
4. WHEN no User_Instructions are provided, THE Context_Engine SHALL use default behavior without requiring any user configuration
5. THE User_Instructions SHALL be stored alongside repository configuration and persisted across generation runs