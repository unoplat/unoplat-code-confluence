import { ProviderKey } from "@/types/credential-enums";

/**
 * Provider metadata for route rendering
 */
export interface ProviderMetadata {
  title: string;
  description: string;
  routeSlug: string;
}

/**
 * Map repository provider keys to their route slugs for dynamic routing
 * Slug format: lowercase with hyphens (e.g., "github-enterprise")
 *
 * Currently supports: GitHub, GitHub Enterprise
 * Extensible for: GitLab CE, GitLab Enterprise (future)
 */
const REPOSITORY_PROVIDER_ROUTE_SLUGS: Record<ProviderKey, string | null> = {
  // Active repository providers
  [ProviderKey.GITHUB_OPEN]: "github",
  [ProviderKey.GITHUB_ENTERPRISE]: "github-enterprise",

  // Future repository providers (not yet implemented)
  [ProviderKey.GITLAB_CE]: null, // Will be "gitlab"
  [ProviderKey.GITLAB_ENTERPRISE]: null, // Will be "gitlab-enterprise"

  // Non-repository providers (not used in onboarding routes)
  [ProviderKey.GOOGLE_AUTH]: null,
  [ProviderKey.GITHUB_AUTH]: null,
  [ProviderKey.MODEL_PROVIDER_AUTH]: null,
};

/**
 * Provider metadata for UI display
 * Only includes active repository providers
 */
const REPOSITORY_PROVIDER_METADATA: Partial<
  Record<ProviderKey, Omit<ProviderMetadata, "routeSlug">>
> = {
  [ProviderKey.GITHUB_OPEN]: {
    title: "GitHub Repositories",
    description:
      "Connect your GitHub repositories to ingest them into Unoplat Code Confluence.",
  },
  [ProviderKey.GITHUB_ENTERPRISE]: {
    title: "GitHub Enterprise Repositories",
    description:
      "Connect your GitHub Enterprise account. For Enterprise Cloud on github.com you can leave the Base URL empty. For data residency (ghe.com) or self-hosted Enterprise Server, supply the instance URL and a PAT.",
  },
  // Future providers will be added here
};

/**
 * Get the route slug for a provider key
 *
 * @param providerKey - The provider key
 * @returns Route slug (e.g., "github-enterprise") or null if not supported
 *
 * @example
 * ```tsx
 * getProviderRouteSlug(ProviderKey.GITHUB_ENTERPRISE) // "github-enterprise"
 * getProviderRouteSlug(ProviderKey.GITHUB_OPEN) // "github"
 * getProviderRouteSlug(ProviderKey.GITLAB_CE) // null (not yet supported)
 * ```
 */
export function getProviderRouteSlug(providerKey: ProviderKey): string | null {
  return REPOSITORY_PROVIDER_ROUTE_SLUGS[providerKey];
}

/**
 * Get complete metadata for a provider including route slug
 *
 * @param providerKey - The provider key
 * @returns Provider metadata (title, description, routeSlug) or null if not supported
 *
 * @example
 * ```tsx
 * const metadata = getProviderMetadata(ProviderKey.GITHUB_OPEN);
 * // { title: "GitHub Repositories", description: "...", routeSlug: "github" }
 * ```
 */
export function getProviderMetadata(
  providerKey: ProviderKey,
): ProviderMetadata | null {
  const slug = REPOSITORY_PROVIDER_ROUTE_SLUGS[providerKey];
  const metadata = REPOSITORY_PROVIDER_METADATA[providerKey];

  if (!slug || !metadata) {
    return null;
  }

  return {
    ...metadata,
    routeSlug: slug,
  };
}

/**
 * Get provider key from route slug (reverse lookup)
 *
 * @param slug - The route slug (e.g., "github-enterprise")
 * @returns Provider key or null if not found
 *
 * @example
 * ```tsx
 * getProviderFromSlug("github-enterprise") // ProviderKey.GITHUB_ENTERPRISE
 * getProviderFromSlug("github") // ProviderKey.GITHUB_OPEN
 * getProviderFromSlug("invalid") // null
 * ```
 */
export function getProviderFromSlug(slug: string): ProviderKey | null {
  const entry = Object.entries(REPOSITORY_PROVIDER_ROUTE_SLUGS).find(
    ([, routeSlug]) => routeSlug === slug,
  );
  return entry ? (entry[0] as ProviderKey) : null;
}

/**
 * Derive the selected provider from the current route pathname
 *
 * Replaces the need for storing `selectedProvider` in Zustand by using
 * the route as the single source of truth.
 *
 * @param pathname - Current route pathname from router
 * @returns Provider key derived from the route, or null if no provider route
 *
 * @example
 * ```tsx
 * const pathname = usePathname();
 * const selectedProvider = getProviderFromPathname(pathname);
 * // pathname="/onboarding/github-enterprise" -> ProviderKey.GITHUB_ENTERPRISE
 * // pathname="/onboarding/github" -> ProviderKey.GITHUB_OPEN
 * // pathname="/settings" -> null
 * ```
 */
export function getProviderFromPathname(pathname: string): ProviderKey | null {
  // Extract the last segment from the pathname
  const segments = pathname.split("/").filter(Boolean);
  const lastSegment = segments[segments.length - 1];

  if (!lastSegment) return null;

  return getProviderFromSlug(lastSegment);
}
