import type { ReactNode } from 'react';

import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardAction,
} from '@/components/ui/card';

type Status = 'shipped' | 'in-progress' | 'planned';
type SubStatus = 'stable' | 'beta' | 'alpha';

interface RoadmapCardProps {
  title: string;
  description: string;
  status: Status;
  subStatus?: SubStatus;
  href?: string;
  icon?: ReactNode;
}

const statusLabels: Record<Status, string> = {
  shipped: 'Shipped',
  'in-progress': 'In Progress',
  planned: 'Planned',
};

const subStatusLabels: Record<SubStatus, string> = {
  stable: 'Stable',
  beta: 'Beta',
  alpha: 'Alpha',
};

export function RoadmapCard({
  title,
  description,
  status,
  subStatus,
  href,
  icon,
}: RoadmapCardProps) {
  return (
    <Card className="transition-colors hover:bg-accent/50">
      <CardHeader>
        {icon && <div className="mb-2">{icon}</div>}
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
        <CardAction>
          <div className="flex gap-2">
            <Badge variant={status}>{statusLabels[status]}</Badge>
            {subStatus && (
              <Badge variant={subStatus}>{subStatusLabels[subStatus]}</Badge>
            )}
          </div>
        </CardAction>
      </CardHeader>
      {href && (
        <CardContent>
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline"
          >
            View on GitHub →
          </a>
        </CardContent>
      )}
    </Card>
  );
}
