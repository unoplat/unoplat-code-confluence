import logoDark from "@/assets/code-confluence-logo-dark.svg";
import { IconLink } from "@/components/commit-layout/icon-link";

function GitHubIcon(props: React.ComponentPropsWithoutRef<"svg">) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor" {...props}>
      <path d="M8 .198a8 8 0 0 0-8 8 7.999 7.999 0 0 0 5.47 7.59c.4.076.547-.172.547-.384 0-.19-.007-.694-.01-1.36-2.226.482-2.695-1.074-2.695-1.074-.364-.923-.89-1.17-.89-1.17-.725-.496.056-.486.056-.486.803.056 1.225.824 1.225.824.714 1.224 1.873.87 2.33.666.072-.518.278-.87.507-1.07-1.777-.2-3.644-.888-3.644-3.954 0-.873.31-1.586.823-2.146-.09-.202-.36-1.016.07-2.118 0 0 .67-.214 2.2.82a7.67 7.67 0 0 1 2-.27 7.67 7.67 0 0 1 2 .27c1.52-1.034 2.19-.82 2.19-.82.43 1.102.16 1.916.08 2.118.51.56.82 1.273.82 2.146 0 3.074-1.87 3.75-3.65 3.947.28.24.54.73.54 1.48 0 1.07-.01 1.93-.01 2.19 0 .21.14.46.55.38A7.972 7.972 0 0 0 16 8.199a8 8 0 0 0-8-8Z" />
    </svg>
  );
}

function DiscordIcon(props: React.ComponentPropsWithoutRef<"svg">) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor" {...props}>
      <path d="M13.545 2.907a13.2 13.2 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406.833a12.2 12.2 0 0 0-3.658 0 8 8 0 0 0-.412-.833.05.05 0 0 0-.052-.025c-1.125.194-2.22.534-3.257 1.011a.04.04 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032q.003.022.021.037a13.3 13.3 0 0 0 3.996 2.02.05.05 0 0 0 .056-.019c.308-.42.582-.863.818-1.329a.05.05 0 0 0-.01-.059.05.05 0 0 0-.018-.011 8.8 8.8 0 0 1-1.248-.595.05.05 0 0 1-.005-.084q.125-.093.248-.19a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.05.05 0 0 1 .053.007q.121.097.248.19a.05.05 0 0 1-.004.084 8.3 8.3 0 0 1-1.249.594.05.05 0 0 0-.03.07c.24.467.514.91.818 1.33a.05.05 0 0 0 .056.018 13.2 13.2 0 0 0 4-2.02.05.05 0 0 0 .021-.036c.334-3.451-.559-6.449-2.366-9.106a.03.03 0 0 0-.02-.019M5.196 10.404c-.789 0-1.438-.724-1.438-1.612s.637-1.613 1.438-1.613c.807 0 1.45.73 1.438 1.613 0 .888-.637 1.612-1.438 1.612m5.316 0c-.788 0-1.438-.724-1.438-1.612s.637-1.613 1.438-1.613c.807 0 1.451.73 1.438 1.613 0 .888-.631 1.612-1.438 1.612" />
    </svg>
  );
}

function LinkedInIcon(props: React.ComponentPropsWithoutRef<"svg">) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor" {...props}>
      <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854zm4.943 12.248V6.169H2.542v7.225zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248S2.4 3.226 2.4 3.934c0 .694.521 1.248 1.327 1.248zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016l.016-.025V6.169H6.29c.032.682 0 7.225 0 7.225z" />
    </svg>
  );
}

function XIcon(props: React.ComponentPropsWithoutRef<"svg">) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor" {...props}>
      <path d="M9.51762 6.77491L15.3459 0H13.9648L8.90409 5.88256L4.86212 0H0.200195L6.31244 8.89547L0.200195 16H1.58139L6.92562 9.78782L11.1942 16H15.8562L9.51728 6.77491H9.51762ZM7.62588 8.97384L7.00658 8.08805L2.07905 1.03974H4.20049L8.17706 6.72795L8.79636 7.61374L13.9654 15.0075H11.844L7.62588 8.97418V8.97384Z" />
    </svg>
  );
}

function FeedIcon(props: React.ComponentPropsWithoutRef<"svg">) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor" {...props}>
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M2.5 3a.5.5 0 0 1 .5-.5h.5c5.523 0 10 4.477 10 10v.5a.5.5 0 0 1-.5.5h-.5a.5.5 0 0 1-.5-.5v-.5A8.5 8.5 0 0 0 3.5 4H3a.5.5 0 0 1-.5-.5V3Zm0 4.5A.5.5 0 0 1 3 7h.5A5.5 5.5 0 0 1 9 12.5v.5a.5.5 0 0 1-.5.5H8a.5.5 0 0 1-.5-.5v-.5a4 4 0 0 0-4-4H3a.5.5 0 0 1-.5-.5v-.5Zm0 5a1 1 0 1 1 2 0 1 1 0 0 1-2 0Z"
      />
    </svg>
  );
}

export function ChangelogIntro() {
  return (
    <>
      <div>
        <a href="https://www.unoplat.io" target="_blank" rel="noopener noreferrer">
          <img
            src={logoDark}
            alt="Unoplat Code Confluence"
            className="inline-block h-8 w-auto"
          />
        </a>
      </div>
      <h1 className="mt-14 font-display text-4xl/tight font-light text-white">
        Code Confluence{" "}
        <span className="text-gray-300">Changelog & Releases</span>
      </h1>
      <p className="mt-4 text-sm/6 text-gray-300">
        Track every release, improvement, and fix to Unoplat Code Confluence.
        Stay up to date with the latest features and changes.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-x-1 gap-y-3 sm:gap-x-2 lg:justify-start">
        <IconLink
          href="https://github.com/unoplat/unoplat-code-confluence"
          icon={GitHubIcon}
          className="flex-none"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub
        </IconLink>
        <IconLink
          href="https://discord.gg/qe2nbQMnWB"
          icon={DiscordIcon}
          className="flex-none"
          target="_blank"
          rel="noopener noreferrer"
        >
          Discord
        </IconLink>
        <IconLink
          href="https://www.linkedin.com/company/unoplat/"
          icon={LinkedInIcon}
          className="flex-none"
          target="_blank"
          rel="noopener noreferrer"
        >
          LinkedIn
        </IconLink>
        <IconLink
          href="https://x.com/unoplatio"
          icon={XIcon}
          className="flex-none"
          target="_blank"
          rel="noopener noreferrer"
        >
          X
        </IconLink>
        <IconLink
          href="/changelog/feed/xml"
          icon={FeedIcon}
          className="flex-none"
          target="_blank"
          rel="noopener noreferrer"
        >
          RSS
        </IconLink>
      </div>
    </>
  );
}

export function ChangelogIntroFooter() {
  return (
    <p className="flex items-baseline gap-x-2 text-[0.8125rem]/6 text-gray-500">
      Built by{" "}
      <a
        href="https://www.unoplat.io"
        target="_blank"
        rel="noopener noreferrer"
        className="text-gray-300 underline decoration-gray-500/50 underline-offset-2 transition-colors hover:text-white hover:decoration-white/50"
      >
        Unoplat
      </a>
    </p>
  );
}
