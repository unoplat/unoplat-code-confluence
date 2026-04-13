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
  /** Unique ID - change this to reset dismissed state for all users.
   *  IMPORTANT: Use dashes, not dots (e.g., "v0-24-0" not "v0.24.0").
   *  Dots create invalid CSS class selectors that break sidebar layout. */
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
  id: "v0-34-0",
  message: "Release v0.34.0 adds capability-operation schema v4, FastMCP client support, and Firebase detection.",
  linkUrl: "/changelog#v0.34.0",
  linkText: "Read release notes",
  variant: "rainbow",
};
