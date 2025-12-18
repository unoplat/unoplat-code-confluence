import type { UiErrorReport } from "@/types";

/**
 * Formats aggregated error content from multiple error sources into a single markdown string.
 * Used when submitting feedback for all errors (repository + codebases) in a single GitHub issue.
 *
 * @param repositoryError - The repository-level error report (if any)
 * @param codebaseErrors - Array of codebase errors with their folder identifiers
 * @returns Formatted markdown string combining all errors
 */
export function formatAggregatedErrorReportContent(
  repositoryError: UiErrorReport | null,
  codebaseErrors: Array<{ folder: string; error: UiErrorReport }>,
): string {
  const sections: string[] = [];

  // Repository-level error section
  if (repositoryError) {
    const repoStackTrace =
      repositoryError.error_traceback || repositoryError.stack_trace;

    let repoMetadataSection = "";
    if (repositoryError.metadata) {
      try {
        repoMetadataSection = `\n#### Metadata\n\`\`\`json\n${JSON.stringify(repositoryError.metadata, null, 2)}\n\`\`\`\n`;
      } catch {
        repoMetadataSection = "\n#### Metadata\nCould not format metadata.\n";
      }
    }

    sections.push(`## Repository Error

**Type:** ${repositoryError.error_type}
**Message:** ${repositoryError.error_message}

${repoStackTrace ? `### Stack Trace\n\`\`\`\n${repoStackTrace}\n\`\`\`` : ""}${repoMetadataSection}`);
  }

  // Codebase-level errors section
  if (codebaseErrors.length > 0) {
    sections.push(`## Codebase Errors (${codebaseErrors.length} failed)`);

    for (const { folder, error } of codebaseErrors) {
      const codebaseStackTrace = error.error_traceback || error.stack_trace;

      let codebaseMetadataSection = "";
      if (error.metadata) {
        try {
          codebaseMetadataSection = `\n#### Metadata\n\`\`\`json\n${JSON.stringify(error.metadata, null, 2)}\n\`\`\`\n`;
        } catch {
          codebaseMetadataSection =
            "\n#### Metadata\nCould not format metadata.\n";
        }
      }

      sections.push(`### \`${folder}\`

**Message:** ${error.error_message}

${codebaseStackTrace ? `\`\`\`\n${codebaseStackTrace}\n\`\`\`` : ""}${codebaseMetadataSection}`);
    }
  }

  sections.push(`## Additional Information
<!-- Please add any additional information that might help resolve this issue -->
`);

  return sections.join("\n\n");
}
