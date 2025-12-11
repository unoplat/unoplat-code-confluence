import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-full border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
        destructive:
          "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        // Job status variants
        completed:
          "border-transparent bg-success/10 text-success [a&]:hover:bg-success/20",
        failed:
          "border-transparent bg-destructive/10 text-destructive [a&]:hover:bg-destructive/20",
        pending:
          "border-transparent bg-muted text-muted-foreground [a&]:hover:bg-muted/80",
        running:
          "border-transparent bg-info/10 text-info [a&]:hover:bg-info/20",
        cancelled:
          "border-transparent bg-muted text-muted-foreground [a&]:hover:bg-muted/80",
        // Feature status variants
        alpha:
          "border-transparent bg-purple-500 text-white [a&]:hover:bg-purple-600",
        beta: "border-transparent bg-indigo-500 text-white [a&]:hover:bg-indigo-600",
        stable:
          "border-transparent bg-green-500 text-white [a&]:hover:bg-green-600",
        // Operation type variants
        ingestion:
          "border-transparent bg-info/10 text-info [a&]:hover:bg-info/20",
        agents_generation:
          "border-transparent bg-purple-500/10 text-purple-600 dark:text-purple-400 [a&]:hover:bg-purple-500/20",
        agent_md_update:
          "border-transparent bg-amber-500/10 text-amber-600 dark:text-amber-400 [a&]:hover:bg-amber-500/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span";

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  );
}

export { Badge, badgeVariants };
