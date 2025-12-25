import { Link } from "@tanstack/react-router";
import { CalendarDays, ExternalLink } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardAction,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { ChangelogEntry } from "@/lib/changelog-utils";
import { formatReleaseDate } from "@/lib/changelog-utils";

interface ChangelogCardProps {
  release: ChangelogEntry;
}

export function ChangelogCard({ release }: ChangelogCardProps) {
  const formattedDate = formatReleaseDate(release.releaseDate);

  return (
    <Card className="group relative transition-colors hover:bg-fd-accent/50">
      <Link
        to="/changelog/$slug"
        params={{ slug: release.slug }}
        className="absolute inset-0 z-0"
        aria-label={`View ${release.title} changelog`}
      />
      <CardHeader>
        <CardTitle className="group-hover:text-fd-primary transition-colors">
          {release.title}
        </CardTitle>
        <CardDescription>{release.description}</CardDescription>
        <CardAction>
          <Badge variant="outline" className="font-mono">
            v{release.version}
          </Badge>
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3 text-sm text-fd-muted-foreground">
          <div className="flex items-center gap-1.5">
            <CalendarDays className="size-4" />
            {formattedDate ? (
              <time dateTime={release.releaseDate}>{formattedDate}</time>
            ) : (
              <span>Unknown date</span>
            )}
          </div>
          {release.githubRelease && (
            <>
              <Separator orientation="vertical" className="h-4" />
              <a
                href={release.githubRelease}
                target="_blank"
                rel="noopener noreferrer"
                className="relative z-10 inline-flex items-center gap-1 hover:text-fd-foreground transition-colors"
              >
                <ExternalLink className="size-3.5" />
                GitHub
              </a>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
