/**
 * Banner Configuration
 *
 * Edit this file to update the banner message shown across the documentation site.
 * The banner appears at the top of every page and can be dismissed by users.
 *
 * To hide the banner completely, set `enabled` to false.
 * When updating the message for a new release, change the `id` to reset
 * the dismissed state for all users.
 */

export interface BannerConfig {
  /** Whether to show the banner */
  enabled: boolean;
  /** Unique ID - change this to reset dismissed state for all users */
  id: string;
  /** The message to display in the banner */
  message: string;
  /** Optional link URL */
  linkUrl?: string;
  /** Optional link text (defaults to "Learn more") */
  linkText?: string;
  /** Visual variant: "normal" or "rainbow" */
  variant?: "normal" | "rainbow";
}

export const bannerConfig: BannerConfig = {
  enabled: true,
  id: "v0.20.0",
  message: "Reliable auditable agents are here. ",
  linkUrl: "/changelog/v0.20.0",
  linkText: " See what's new!",
  variant: "rainbow",
};
