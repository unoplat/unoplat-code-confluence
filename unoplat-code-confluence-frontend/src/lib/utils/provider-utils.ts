import { ProviderKey } from "@/types/credential-enums";
import {
  Github,
  GitlabIcon,
  type LucideIcon,
  Cloud,
  Building2,
} from "lucide-react";

/**
 * Get user-friendly display name for a provider key
 */
export function getProviderDisplayName(provider_key: ProviderKey): string {
  const displayNames: Record<ProviderKey, string> = {
    [ProviderKey.GITHUB_OPEN]: "GitHub",
    [ProviderKey.GITHUB_ENTERPRISE]: "GitHub Enterprise",
    [ProviderKey.GITLAB_CE]: "GitLab",
    [ProviderKey.GITLAB_ENTERPRISE]: "GitLab Enterprise",
    [ProviderKey.GOOGLE_AUTH]: "Google OAuth",
    [ProviderKey.GITHUB_AUTH]: "GitHub OAuth",
    [ProviderKey.MODEL_PROVIDER_AUTH]: "Model Provider",
  };

  return displayNames[provider_key] || provider_key;
}

/**
 * Get icon component for a provider key
 */
export function getProviderIcon(provider_key: ProviderKey): LucideIcon {
  const iconMap: Record<ProviderKey, LucideIcon> = {
    [ProviderKey.GITHUB_OPEN]: Github,
    [ProviderKey.GITHUB_ENTERPRISE]: Building2,
    [ProviderKey.GITLAB_CE]: GitlabIcon,
    [ProviderKey.GITLAB_ENTERPRISE]: Building2,
    [ProviderKey.GOOGLE_AUTH]: Cloud,
    [ProviderKey.GITHUB_AUTH]: Github,
    [ProviderKey.MODEL_PROVIDER_AUTH]: Cloud,
  };

  return iconMap[provider_key] || Cloud;
}

/**
 * Check if a provider is an enterprise/self-hosted provider
 */
export function isEnterpriseProvider(provider_key: ProviderKey): boolean {
  return [ProviderKey.GITHUB_ENTERPRISE, ProviderKey.GITLAB_ENTERPRISE].includes(
    provider_key,
  );
}

/**
 * Get repository URL based on provider and repository details
 */
export function getRepositoryUrl(
  provider_key: ProviderKey,
  owner: string,
  repo: string,
  enterpriseUrl?: string,
): string {
  switch (provider_key) {
    case ProviderKey.GITHUB_OPEN:
      return `https://github.com/${owner}/${repo}`;

    case ProviderKey.GITHUB_ENTERPRISE: {
      if (!enterpriseUrl) {
        console.warn(
          "Enterprise URL not provided for GitHub Enterprise repository",
        );
        return `https://github.com/${owner}/${repo}`; // Fallback
      }
      // Remove trailing slash if present
      const githubBaseUrl = enterpriseUrl.replace(/\/$/, "");
      return `${githubBaseUrl}/${owner}/${repo}`;
    }

    case ProviderKey.GITLAB_CE:
      return `https://gitlab.com/${owner}/${repo}`;

    case ProviderKey.GITLAB_ENTERPRISE: {
      if (!enterpriseUrl) {
        console.warn(
          "Enterprise URL not provided for GitLab Enterprise repository",
        );
        return `https://gitlab.com/${owner}/${repo}`; // Fallback
      }
      // Remove trailing slash if present
      const gitlabBaseUrl = enterpriseUrl.replace(/\/$/, "");
      return `${gitlabBaseUrl}/${owner}/${repo}`;
    }

    default:
      // Fallback for unknown providers
      return `https://github.com/${owner}/${repo}`;
  }
}

/**
 * Get short provider code (for display in compact spaces)
 */
export function getProviderShortCode(provider_key: ProviderKey): string {
  const shortCodes: Record<ProviderKey, string> = {
    [ProviderKey.GITHUB_OPEN]: "GH",
    [ProviderKey.GITHUB_ENTERPRISE]: "GHE",
    [ProviderKey.GITLAB_CE]: "GL",
    [ProviderKey.GITLAB_ENTERPRISE]: "GLE",
    [ProviderKey.GOOGLE_AUTH]: "GOO",
    [ProviderKey.GITHUB_AUTH]: "GHA",
    [ProviderKey.MODEL_PROVIDER_AUTH]: "MOD",
  };

  return shortCodes[provider_key] || provider_key.substring(0, 3).toUpperCase();
}

/**
 * Get provider color class for badges/pills
 */
export function getProviderColorClass(provider_key: ProviderKey): string {
  const colorClasses: Record<ProviderKey, string> = {
    [ProviderKey.GITHUB_OPEN]: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
    [ProviderKey.GITHUB_ENTERPRISE]: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100",
    [ProviderKey.GITLAB_CE]: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100",
    [ProviderKey.GITLAB_ENTERPRISE]: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100",
    [ProviderKey.GOOGLE_AUTH]: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100",
    [ProviderKey.GITHUB_AUTH]: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
    [ProviderKey.MODEL_PROVIDER_AUTH]: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
  };

  return (
    colorClasses[provider_key] ||
    "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100"
  );
}

/**
 * Get provider options for select dropdowns
 */
export interface ProviderOption {
  label: string;
  value: ProviderKey;
  icon: LucideIcon;
  isEnterprise: boolean;
}

export function getRepositoryProviderOptions(): ProviderOption[] {
  return [
    {
      label: "GitHub",
      value: ProviderKey.GITHUB_OPEN,
      icon: Github,
      isEnterprise: false,
    },
    {
      label: "GitHub Enterprise",
      value: ProviderKey.GITHUB_ENTERPRISE,
      icon: Building2,
      isEnterprise: true,
    },
    {
      label: "GitLab CE",
      value: ProviderKey.GITLAB_CE,
      icon: GitlabIcon,
      isEnterprise: false,
    },
    {
      label: "GitLab Enterprise",
      value: ProviderKey.GITLAB_ENTERPRISE,
      icon: Building2,
      isEnterprise: true,
    },
  ];
}
