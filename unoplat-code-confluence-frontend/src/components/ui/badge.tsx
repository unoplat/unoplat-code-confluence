import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border border-border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        success: "border-transparent bg-primary/10 text-primary",
        warning: "border-transparent bg-destructive/10 text-destructive",
        info: "border-transparent bg-primary/10 text-primary",
        pending: "border-transparent bg-muted text-muted-foreground",
        running: "border-transparent bg-primary/10 text-primary",
        completed: "border-transparent bg-primary/10 text-primary",
        failed: "border-transparent bg-destructive/10 text-destructive",
        cancelled: "border-transparent bg-muted text-muted-foreground",
        alpha:
          "border-amber-200 bg-amber-100 text-amber-800 dark:border-amber-400 dark:bg-amber-950/40 dark:text-amber-200",
        beta: "border-blue-200 bg-blue-100 text-blue-800 dark:border-blue-400 dark:bg-blue-950/40 dark:text-blue-200",
      },
      size: {
        default: "px-2.5 py-0.5 text-xs",
        sm: "px-2 py-0.5 text-xs",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
