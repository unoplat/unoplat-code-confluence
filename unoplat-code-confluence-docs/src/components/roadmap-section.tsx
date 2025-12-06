import type { ReactNode } from 'react';

interface RoadmapSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function RoadmapSection({
  title,
  description,
  children,
}: RoadmapSectionProps) {
  return (
    <section className="mb-8">
      <h2 className="mb-2 text-xl font-bold">{title}</h2>
      {description && (
        <p className="mb-4 text-muted-foreground">{description}</p>
      )}
      <div className="grid gap-4 md:grid-cols-2">{children}</div>
    </section>
  );
}
