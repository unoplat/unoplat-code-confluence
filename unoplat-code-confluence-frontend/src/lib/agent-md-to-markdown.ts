import json2md from "json2md";
import type { AgentMdOutput } from "@/types/sse";

interface AgentMdToMarkdownOptions {
  title?: string;
}

export function agentMdOutputToMarkdown(
  agent: AgentMdOutput,
  options?: AgentMdToMarkdownOptions,
): string {
  const title: string = options?.title ?? "Agents Documentation";

  const entries: unknown[] = [];

  entries.push({ h1: title });

  // Programming language metadata
  entries.push({ h2: "Programming Language Metadata" });
  entries.push({
    ul: [
      `Primary Language: ${agent?.programming_language_metadata?.primary_language ?? "Unknown"}`,
      `Package Manager: ${agent?.programming_language_metadata?.package_manager ?? "Unknown"}`,
    ],
  });

  // Project configuration
  entries.push({ h2: "Project Configuration" });
  if (agent?.project_configuration?.config_files?.length) {
    entries.push({
      ul: agent.project_configuration.config_files.map(
        (f) => `${f.path} — ${f.purpose}`,
      ),
    });
  } else {
    entries.push({ p: "No configuration files detected." });
  }

  // Development workflow (group by kind)
  entries.push({ h2: "Development Workflow" });
  const byKind: Record<
    string,
    {
      kind: string;
      command: string;
      description?: string;
      config_files: string[];
    }[]
  > = {};
  for (const cmd of agent?.development_workflow?.commands ?? []) {
    (byKind[cmd.kind] ||= []).push(cmd);
  }
  for (const kind of Object.keys(byKind)) {
    entries.push({ h3: kind.replace(/_/g, " ").toUpperCase() });
    entries.push({
      ol: byKind[kind].map(
        (c) => `${c.command}${c.description ? ` — ${c.description}` : ""}`,
      ),
    });
  }

  // Business logic domain
  entries.push({ h2: "Business Logic Domain" });
  if (agent?.business_logic?.description) {
    entries.push({ p: agent.business_logic.description });
  }
  if (agent?.business_logic?.data_models?.length) {
    entries.push({ h3: "Core Files" });
    entries.push({
      ul: agent.business_logic.data_models.map(
        (m) => `${m.path}${m.responsibility ? ` — ${m.responsibility}` : ""}`,
      ),
    });
  }

  return json2md(entries as any);
}

export function codebasesToMarkdown(
  codebases: Record<string, AgentMdOutput>,
  options?: AgentMdToMarkdownOptions,
): string {
  const title: string = options?.title ?? "Agents Documentation";
  const entries: unknown[] = [];

  entries.push({ h1: title });

  for (const [codebaseName, agent] of Object.entries(codebases)) {
    // Codebase section
    entries.push({ h2: `Codebase: ${codebaseName}` });

    // Programming language metadata
    entries.push({ h3: "Programming Language Metadata" });
    entries.push({
      ul: [
        `Primary Language: ${agent?.programming_language_metadata?.primary_language ?? "Unknown"}`,
        `Package Manager: ${agent?.programming_language_metadata?.package_manager ?? "Unknown"}`,
      ],
    });

    // Project configuration
    entries.push({ h3: "Project Configuration" });
    if (agent?.project_configuration?.config_files?.length) {
      entries.push({
        ul: agent.project_configuration.config_files.map(
          (f) => `${f.path} — ${f.purpose}`,
        ),
      });
    } else {
      entries.push({ p: "No configuration files detected." });
    }

    // Development workflow (group by kind)
    entries.push({ h3: "Development Workflow" });
    const byKind: Record<
      string,
      {
        kind: string;
        command: string;
        description?: string;
        config_files: string[];
      }[]
    > = {};
    for (const cmd of agent?.development_workflow?.commands ?? []) {
      (byKind[cmd.kind] ||= []).push(cmd);
    }
    for (const kind of Object.keys(byKind)) {
      entries.push({ h4: kind.replace(/_/g, " ").toUpperCase() });
      entries.push({
        ol: byKind[kind].map(
          (c) => `${c.command}${c.description ? ` — ${c.description}` : ""}`,
        ),
      });
    }

    // Business logic domain
    entries.push({ h3: "Business Logic Domain" });
    if (agent?.business_logic?.description) {
      entries.push({ p: agent.business_logic.description });
    }
    if (agent?.business_logic?.data_models?.length) {
      entries.push({ h4: "Core Files" });
      entries.push({
        ul: agent.business_logic.data_models.map(
          (m) => `${m.path}${m.responsibility ? ` — ${m.responsibility}` : ""}`,
        ),
      });
    }

    // Add separator between codebases (except for the last one)
    const codebaseNames = Object.keys(codebases);
    if (codebaseName !== codebaseNames[codebaseNames.length - 1]) {
      entries.push({ hr: "" });
    }
  }

  return json2md(entries as any);
}
