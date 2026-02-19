export const SITE_URL =
  import.meta.env.PUBLIC_SITE_URL ?? "https://docs.unoplat.io";

export const SITE_NAME = "Unoplat Code Confluence";

export const DEFAULT_DESCRIPTION =
  "Unoplat Code Confluence — the universal code context engine for AI agents. Auto-generate AGENTS.md for Python and TypeScript codebases with code parsing, dependency tracking, and agentic planning to ship features 2x faster.";

const KEYWORDS =
  "code context, agents-md, agentic-ai, agentic-planning, agent-skills, code-parsing, code-understanding, dependency-track, python, typescript, llm, gen-ai, hallucination-mitigation, workflow";

interface SeoOptions {
  title: string;
  description?: string;
  path?: string;
  type?: "website" | "article";
}

/**
 * Generate meta tag objects for TanStack Start head().
 * Follows the same pattern used in TanStack Start's official examples.
 */
export function seo({
  title,
  description = DEFAULT_DESCRIPTION,
  path = "/",
  type = "website",
}: SeoOptions): Array<Record<string, string>> {
  const pageTitle =
    title === SITE_NAME ? title : `${title} - ${SITE_NAME}`;
  const url = `${SITE_URL}${path}`;

  return [
    { title: pageTitle },
    { name: "description", content: description },
    { name: "keywords", content: KEYWORDS },
    { property: "og:title", content: pageTitle },
    { property: "og:description", content: description },
    { property: "og:url", content: url },
    { property: "og:type", content: type },
    { property: "og:site_name", content: SITE_NAME },
    { name: "twitter:card", content: "summary" },
    { name: "twitter:title", content: pageTitle },
    { name: "twitter:description", content: description },
  ];
}

/** Generate a canonical link object for TanStack Start head(). */
export function canonicalLink(path: string): { rel: string; href: string } {
  return { rel: "canonical", href: `${SITE_URL}${path}` };
}
