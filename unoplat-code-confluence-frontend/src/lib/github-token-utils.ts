// GitHub Classic PAT scopes required for Unoplat Code Confluence
export const GITHUB_CLASSIC_SCOPES = [
  // Core repo access
  'repo',            // includes repo:status, repo_deployment, public_repo, repo:invite
  'security_events', // add Code-Scanning / Dependabot API rights
  'user',            // read & write profile, emails
  'user:follow',     // follow / unfollow users
] as const;

export interface BuildPatLinkOptions {
  note?: string;
  expirationDays?: 'none' | '30' | '90' | '365';
}

/**
 * Builds a deep link to GitHub's token generation page with pre-filled scopes
 * @param options - Configuration for the token generation link
 * @returns The complete URL to redirect users to GitHub token generation
 */
export function buildGitHubPatLink(options: BuildPatLinkOptions = {}): string {
  const {
    note = 'Unoplat Code Confluence Access Token',
    expirationDays = 'none'
  } = options;

  const base = 'https://github.com/settings/tokens/new';
  const scopes = encodeURIComponent(GITHUB_CLASSIC_SCOPES.join(','));
  const description = encodeURIComponent(note);
  
  return `${base}?description=${description}&scopes=${scopes}&default_expires_at=${expirationDays}`;
}

/**
 * Get human-readable scope descriptions
 */
export const SCOPE_DESCRIPTIONS = {
  repo: 'Full read/write access to repositories, deployments, and invitations',
  security_events: 'Read/write access to Code Scanning and Dependabot alerts',
  user: 'Read and update your GitHub profile and email addresses',
  'user:follow': 'Ability to follow and unfollow users'
} as const;