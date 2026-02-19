import { useEffect, useRef, useState } from "react";
import { ExternalLink } from "lucide-react";

import { cn } from "@/lib/utils";
import { FormattedDate } from "@/components/commit-layout/formatted-date";

function ContentWrapper({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  return (
    <div className="mx-auto max-w-7xl px-6 lg:flex lg:px-8">
      <div className="lg:ml-96 lg:flex lg:w-full lg:justify-end lg:pl-32">
        <div
          className={cn(
            "mx-auto max-w-lg lg:mx-0 lg:w-0 lg:max-w-xl lg:flex-auto",
            className,
          )}
          {...props}
        />
      </div>
    </div>
  );
}

function ArticleHeader({ id, date }: { id: string; date: string | Date }) {
  return (
    <header className="relative mb-10 xl:mb-0">
      <div className="pointer-events-none absolute top-0 left-[max(-0.5rem,calc(50%-18.625rem))] z-50 flex h-4 items-center justify-end gap-x-2 lg:right-[calc(max(2rem,50%-38rem)+40rem)] lg:left-0 lg:min-w-lg xl:h-8">
        <a href={`#${id}`} className="inline-flex">
          <FormattedDate
            date={date}
            className="hidden xl:pointer-events-auto xl:block xl:text-2xs/4 xl:font-medium xl:text-white/50"
          />
        </a>
        <div className="h-0.25 w-3.5 bg-gray-400 lg:-mr-3.5 xl:mr-0 xl:bg-gray-300" />
      </div>
      <ContentWrapper>
        <div className="flex">
          <a href={`#${id}`} className="inline-flex">
            <FormattedDate
              date={date}
              className="text-2xs/4 font-medium text-gray-500 xl:hidden dark:text-white/50"
            />
          </a>
        </div>
      </ContentWrapper>
    </header>
  );
}

interface ChangelogArticleProps {
  id: string;
  date: string | Date;
  title: string;
  githubRelease?: string;
  children: React.ReactNode;
}

export function ChangelogArticle({
  id,
  date,
  title,
  githubRelease,
  children,
}: ChangelogArticleProps) {
  const heightRef = useRef<HTMLDivElement>(null);
  const [heightAdjustment, setHeightAdjustment] = useState(0);

  useEffect(() => {
    if (!heightRef.current) {
      return;
    }

    const observer = new ResizeObserver(() => {
      if (!heightRef.current) {
        return;
      }
      const { height } = heightRef.current.getBoundingClientRect();
      const nextMultipleOf8 = 8 * Math.ceil(height / 8);
      setHeightAdjustment(nextMultipleOf8 - height);
    });

    observer.observe(heightRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <article
      id={id}
      className="scroll-mt-16"
      style={{ paddingBottom: `${heightAdjustment}px` }}
    >
      <div ref={heightRef}>
        <ArticleHeader id={id} date={date} />
        <ContentWrapper>
          <div className="mb-6 flex flex-wrap items-center gap-3">
            <h2 className="text-xl font-semibold text-fd-foreground">
              {title}
            </h2>
            {githubRelease && (
              <a
                href={githubRelease}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-fd-primary transition-colors hover:text-fd-primary/80"
              >
                <ExternalLink className="size-3.5" />
                View on GitHub
              </a>
            )}
          </div>
        </ContentWrapper>
        <ContentWrapper className="prose prose-fd max-w-none" data-mdx-content>
          {children}
        </ContentWrapper>
      </div>
    </article>
  );
}
