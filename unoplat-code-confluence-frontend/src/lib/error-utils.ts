import {
  ApiErrorReport,
  UiErrorReport,
  IssueType,
  IssueTracking,
} from "../types";

/**
 * Converts an API error report to a UI error report by adding the necessary UI-specific fields
 *
 * @param apiError - The error report from the API
 * @param context - The context data needed to create a complete UI error report
 * @returns A UI error report with all required fields
 */
export function apiToUiErrorReport(
  apiError: ApiErrorReport,
  context: {
    error_type: IssueType;
    repository_name: string;
    repository_owner_name: string;
    parent_workflow_run_id: string;
    workflow_id?: string;
    workflow_run_id?: string;
    activity_id?: string;
    activity_name?: string;
  },
): UiErrorReport {
  // Extract any issue tracking data from metadata if it exists
  const issueTracking = apiError.metadata?.issue_tracking as
    | IssueTracking
    | undefined;

  // Handle stack_trace which could be string | null | undefined
  // Convert null to undefined to satisfy error_traceback type
  const errorTraceback =
    apiError.stack_trace === null ? undefined : apiError.stack_trace;

  return {
    // Include all API error fields
    ...apiError,

    // Add UI-specific properties
    error_type: context.error_type,
    error_traceback: errorTraceback, // Map stack_trace to error_traceback for backward compatibility

    // Add repository context
    repository_name: context.repository_name,
    repository_owner_name: context.repository_owner_name,
    parent_workflow_run_id: context.parent_workflow_run_id,

    // Add optional workflow context if provided
    ...(context.workflow_id && { workflow_id: context.workflow_id }),
    ...(context.workflow_run_id && {
      workflow_run_id: context.workflow_run_id,
    }),
    ...(context.activity_id && { activity_id: context.activity_id }),
    ...(context.activity_name && { activity_name: context.activity_name }),

    // Add issue tracking if it exists in metadata
    ...(issueTracking && { issue_tracking: issueTracking }),
  };
}

/**
 * Formats error report content for display in the feedback dialog
 *
 * @param errorReport - The UI error report
 * @returns Formatted markdown string for display
 */
export function formatErrorReportContent(errorReport: UiErrorReport): string {
  const title =
    errorReport.error_type === "CODEBASE"
      ? "Codebase Error Details"
      : "Repository Error Details";

  // Use error_traceback if available, fallback to stack_trace
  const stackTrace = errorReport.error_traceback || errorReport.stack_trace;

  // Format metadata if available
  let metadataSection = "";
  if (errorReport.metadata) {
    try {
      metadataSection = `\n### Metadata\n\`\`\`json\n${JSON.stringify(errorReport.metadata, null, 2)}\n\`\`\`\n`;
    } catch {
      metadataSection = "\n### Metadata\nCould not format metadata.\n";
    }
  }

  return `## ${title}

**Type:** ${errorReport.error_type}
**Message:** ${errorReport.error_message}

${stackTrace ? `### Stack Trace\n\`\`\`\n${stackTrace}\n\`\`\`` : ""}
${metadataSection}

## Additional Information
<!-- Please add any additional information that might help resolve this issue -->

`;
}
