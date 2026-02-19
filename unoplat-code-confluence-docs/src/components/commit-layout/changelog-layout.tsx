import { useId } from "react";

import {
  ChangelogIntro,
  ChangelogIntroFooter,
} from "@/components/commit-layout/changelog-intro";
import { StarField } from "@/components/commit-layout/star-field";

function Timeline() {
  const id = useId();

  return (
    <div className="pointer-events-none absolute inset-0 z-50 overflow-hidden lg:right-[calc(max(2rem,50%-38rem)+40rem)] lg:min-w-lg lg:overflow-visible">
      <svg
        className="absolute top-0 left-[max(0px,calc(50%-18.125rem))] h-full w-1.5 lg:left-full lg:ml-1 xl:right-1 xl:left-auto xl:ml-0"
        aria-hidden="true"
      >
        <defs>
          <pattern
            id={id}
            width="6"
            height="8"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M0 0H6M0 8H6"
              className="stroke-gray-400/15 dark:stroke-white/10"
              fill="none"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#${id})`} />
      </svg>
    </div>
  );
}

function Glow() {
  const id = useId();

  return (
    <div className="absolute inset-0 -z-10 overflow-hidden bg-gray-950 lg:right-[calc(max(2rem,50%-38rem)+40rem)] lg:min-w-lg">
      <svg
        className="absolute -bottom-48 left-[-40%] h-320 w-[180%] lg:top-[-40%] lg:-right-40 lg:bottom-auto lg:left-auto lg:h-[180%] lg:w-7xl"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id={`${id}-desktop`} cx="100%">
            <stop offset="0%" stopColor="rgba(120, 120, 140, 0.25)" />
            <stop offset="53.95%" stopColor="rgba(60, 60, 80, 0.09)" />
            <stop offset="100%" stopColor="rgba(10, 14, 23, 0)" />
          </radialGradient>
          <radialGradient id={`${id}-mobile`} cy="100%">
            <stop offset="0%" stopColor="rgba(120, 120, 140, 0.25)" />
            <stop offset="53.95%" stopColor="rgba(60, 60, 80, 0.09)" />
            <stop offset="100%" stopColor="rgba(10, 14, 23, 0)" />
          </radialGradient>
        </defs>
        <rect
          width="100%"
          height="100%"
          fill={`url(#${id}-desktop)`}
          className="hidden lg:block"
        />
        <rect
          width="100%"
          height="100%"
          fill={`url(#${id}-mobile)`}
          className="lg:hidden"
        />
      </svg>
      <div className="absolute inset-x-0 right-0 bottom-0 h-px bg-white mix-blend-overlay lg:top-0 lg:left-auto lg:h-auto lg:w-px" />
    </div>
  );
}

function FixedSidebar({
  main,
  footer,
}: {
  main: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="relative flex-none overflow-hidden px-6 lg:pointer-events-none lg:fixed lg:top-[var(--fd-banner-height)] lg:bottom-0 lg:left-0 lg:right-0 lg:z-30 lg:flex lg:px-0">
      <Glow />
      <div className="relative flex w-full lg:pointer-events-auto lg:mr-[calc(max(2rem,50%-38rem)+40rem)] lg:min-w-lg lg:overflow-x-hidden lg:overflow-y-auto lg:pl-[max(4rem,calc(50%-38rem))]">
        <div className="mx-auto max-w-lg lg:mx-0 lg:flex lg:w-96 lg:max-w-none lg:flex-col lg:before:flex-1 lg:before:pt-6">
          <div className="pt-20 pb-16 sm:pt-32 sm:pb-20 lg:py-20">
            <div className="relative">
              <StarField className="top-14 -right-44" />
              {main}
            </div>
          </div>
          <div className="flex flex-1 items-end justify-center pb-4 lg:justify-start lg:pb-6">
            {footer}
          </div>
        </div>
      </div>
    </div>
  );
}

export function ChangelogLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <FixedSidebar
        main={<ChangelogIntro />}
        footer={<ChangelogIntroFooter />}
      />
      <div className="relative flex-auto">
        <Timeline />
        <main className="space-y-20 py-20 sm:space-y-32 sm:py-32">
          {children}
        </main>
      </div>
    </>
  );
}
