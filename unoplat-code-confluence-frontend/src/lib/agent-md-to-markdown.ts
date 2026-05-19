import json2md from "json2md";
import type {
  AgentMdAppInterfaces,
  AgentMdCodebaseOutput,
  AgentMdInterfaceConstruct,
} from "@/features/repository-agent-snapshots/schema";

interface AgentMdToMarkdownOptions {
  title?: string;
}

function formatEngineeringWorkflowCommand(command: {
  command: string;
  config_file: string;
  working_directory?: string | null;
}): string {
  const metadata = [command.config_file];

  if (command.working_directory) {
    metadata.push(`cwd: ${command.working_directory}`);
  }

  return `\`${command.command}\` (${metadata.join(", ")})`;
}

function buildMatchPatternLines(
  matchPattern: Record<string, string[]>,
): string[] {
  const lines: string[] = [];
  for (const [filePath, matches] of Object.entries(matchPattern)) {
    if (!matches.length) {
      lines.push(filePath);
      continue;
    }
    for (const match of matches) {
      const trimmed = match.trim();
      lines.push(trimmed ? `${filePath}: ${trimmed}` : filePath);
    }
  }
  return lines;
}

function pushInterfacesSectionEntries(
  entries: unknown[],
  appInterfaces: AgentMdAppInterfaces | null | undefined,
  headingLevel: "h2" | "h3",
  subHeadingLevel: "h3" | "h4",
): void {
  entries.push({ [headingLevel]: "App Interfaces" });
  entries.push({
    p: "Format: `path: L<line>: <match_text>` where path is codebase-relative.",
  });

  if (!appInterfaces) {
    entries.push({ p: "No app interfaces detected." });
    return;
  }

  entries.push({ [subHeadingLevel]: "Inbound Constructs" });
  if (appInterfaces.inbound_constructs.length) {
    pushInterfaceConstructEntries(
      entries,
      appInterfaces.inbound_constructs,
      subHeadingLevel,
    );
  } else {
    entries.push({ p: "No inbound constructs detected." });
  }

  entries.push({ [subHeadingLevel]: "Outbound Constructs" });
  if (appInterfaces.outbound_constructs.length) {
    pushInterfaceConstructEntries(
      entries,
      appInterfaces.outbound_constructs,
      subHeadingLevel,
    );
  } else {
    entries.push({ p: "No outbound constructs detected." });
  }

  entries.push({ [subHeadingLevel]: "Internal Constructs" });
  if (appInterfaces.internal_constructs.length) {
    pushInterfaceConstructEntries(
      entries,
      appInterfaces.internal_constructs,
      subHeadingLevel,
    );
  } else {
    entries.push({ p: "No internal constructs detected." });
  }
}

function pushInterfaceConstructEntries(
  entries: unknown[],
  constructs: AgentMdInterfaceConstruct[],
  subHeadingLevel: "h3" | "h4",
): void {
  const constructHeadingLevel = subHeadingLevel === "h3" ? "h4" : "h4";
  for (const construct of constructs) {
    const libraryLabel = construct.library || "unknown";
    entries.push({
      [constructHeadingLevel]: `${construct.kind} (${libraryLabel})`,
    });

    const matchLines = buildMatchPatternLines(construct.match_pattern);
    if (matchLines.length) {
      entries.push({ ul: matchLines });
    } else {
      entries.push({ p: "No matches detected." });
    }
  }
}

export function agentMdOutputToMarkdown(
  agent: AgentMdCodebaseOutput,
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

  // Development Workflow Guide
  entries.push({ h2: "Development Workflow Guide" });
  entries.push({ h3: "Commands" });
  const byStage: Record<
    string,
    {
      stage: string;
      command: string;
      config_file: string;
      working_directory?: string | null;
    }[]
  > = {};
  for (const cmd of agent?.engineering_workflow?.commands ?? []) {
    (byStage[cmd.stage] ||= []).push(cmd);
  }
  const stageOrder = ["install", "build", "dev", "test", "lint", "type_check"];
  for (const stage of stageOrder.filter((value) => byStage[value]?.length)) {
    entries.push({ h3: stage.replace(/_/g, " ").toUpperCase() });
    entries.push({
      ol: byStage[stage].map((c) => formatEngineeringWorkflowCommand(c)),
    });
  }

  // Dependency Guide section
  entries.push({ h2: "Dependency Guide" });
  if (agent?.dependency_guide?.dependencies?.length) {
    entries.push({
      ul: agent.dependency_guide.dependencies.map(
        (d) => `**${d.name}** — ${d.purpose}`,
      ),
    });
  } else {
    entries.push({ p: "No dependency guide entries available." });
  }

  // Business Domain Guide
  entries.push({ h2: "Business Domain Guide" });
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

  pushInterfacesSectionEntries(entries, agent?.app_interfaces, "h2", "h3");

  return json2md(entries as any);
}

export function codebasesToMarkdown(
  codebases: Record<string, AgentMdCodebaseOutput>,
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

    // Development Workflow Guide
    entries.push({ h3: "Development Workflow Guide" });
    entries.push({ h4: "Commands" });
    const byStage: Record<
      string,
      {
        stage: string;
        command: string;
        config_file: string;
        working_directory?: string | null;
      }[]
    > = {};
    for (const cmd of agent?.engineering_workflow?.commands ?? []) {
      (byStage[cmd.stage] ||= []).push(cmd);
    }
    const stageOrder = [
      "install",
      "build",
      "dev",
      "test",
      "lint",
      "type_check",
    ];
    for (const stage of stageOrder.filter((value) => byStage[value]?.length)) {
      entries.push({ h4: stage.replace(/_/g, " ").toUpperCase() });
      entries.push({
        ol: byStage[stage].map((c) => formatEngineeringWorkflowCommand(c)),
      });
    }

    // Dependency Guide section (per codebase)
    entries.push({ h3: "Dependency Guide" });
    if (agent?.dependency_guide?.dependencies?.length) {
      entries.push({
        ul: agent.dependency_guide.dependencies.map(
          (d) => `**${d.name}** — ${d.purpose}`,
        ),
      });
    } else {
      entries.push({ p: "No dependency guide entries available." });
    }

    // Business Domain Guide
    entries.push({ h3: "Business Domain Guide" });
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

    pushInterfacesSectionEntries(entries, agent?.app_interfaces, "h3", "h4");

    // Add separator between codebases (except for the last one)
    const codebaseNames = Object.keys(codebases);
    if (codebaseName !== codebaseNames[codebaseNames.length - 1]) {
      entries.push({ hr: "" });
    }
  }

  return json2md(entries as any);
}
