import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-content shadow-sm hover:bg-primary-focus",
        secondary:
          "border-transparent bg-secondary text-secondary-content shadow-sm hover:bg-secondary-focus",
        destructive:
          "border-transparent bg-error text-white shadow-sm hover:bg-error-600",
        success:
          "border-transparent bg-success text-white shadow-sm hover:bg-success-600",
        warning:
          "border-transparent bg-warning text-white shadow-sm hover:bg-warning-600",
        info:
          "border-transparent bg-info text-info-content shadow-sm hover:bg-info-600",
        outline: 
          "text-foreground border-border hover:bg-muted",
        ghost:
          "text-foreground hover:bg-muted border-transparent",
      },
      size: {
        default: "px-2.5 py-0.5 text-xs",
        sm: "px-2 py-0.25 text-[0.625rem]",
        lg: "px-3 py-1 text-sm",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge, badgeVariants }