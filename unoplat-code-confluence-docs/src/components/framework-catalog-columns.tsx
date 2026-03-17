import { type ColumnDef } from "@tanstack/react-table";
import { Code, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { createColumnConfigHelper } from "@/components/data-table-filter/core/filters";
import type { FrameworkCatalogRow } from "@/types/framework-catalog";

const dtf = createColumnConfigHelper<FrameworkCatalogRow>();

export const catalogFilterConfig = [
  dtf
    .text()
    .id("library")
    .accessor((row) => row.library)
    .displayName("Library")
    .icon(Search)
    .build(),
  dtf
    .option()
    .id("language")
    .accessor((row) => row.language)
    .displayName("Language")
    .icon(Code)
    .options([
      { value: "python", label: "Python" },
      { value: "typescript", label: "TypeScript" },
    ])
    .build(),
] as const;

export const catalogColumnDefs: ColumnDef<FrameworkCatalogRow>[] = [
  {
    id: "language",
    accessorKey: "language",
    header: "Language",
    // Fixed narrow width: badge content is at most ~90px
    // Ref: https://tanstack.com/table/latest/docs/api/features/column-sizing
    size: 100,
    minSize: 80,
    maxSize: 120,
    cell: ({ row }) => (
      <Badge variant="secondary">{row.original.language}</Badge>
    ),
  },
  {
    id: "library",
    accessorKey: "library",
    header: "Library",
    // Fixed narrow width: library names are short identifiers
    // Ref: https://tanstack.com/table/latest/docs/api/features/column-sizing
    size: 160,
    minSize: 120,
    maxSize: 200,
    cell: ({ row }) => (
      <a
        className="inline-flex items-center rounded-full border border-fd-border bg-fd-card px-2.5 py-1 font-mono text-xs hover:bg-fd-accent"
        href={row.original.catalogPath}
      >
        {row.original.library}
      </a>
    ),
  },
  {
    id: "description",
    accessorKey: "description",
    header: "Description",
    // No fixed size — let this column fill all remaining space
    // Ref: https://tanstack.com/table/latest/docs/guide/column-sizing
    size: Number.MAX_SAFE_INTEGER,
    minSize: 200,
    cell: ({ row }) => (
      <span className="text-xs text-fd-muted-foreground">
        {row.original.description}
      </span>
    ),
  },
];
