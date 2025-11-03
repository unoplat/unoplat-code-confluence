import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const skeletonVariants = cva(
  "animate-pulse bg-muted",
  {
    variants: {
      radius: {
        none: "rounded-none",
        sm: "rounded-sm",
        default: "rounded-md",
        lg: "rounded-lg",
        xl: "rounded-xl",
        full: "rounded-full",
      },
      height: {
        xs: "h-2",
        sm: "h-4",
        default: "h-6",
        lg: "h-8",
        xl: "h-12",
      },
    },
    defaultVariants: {
      radius: "default",
      height: "default",
    },
  }
)

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

function Skeleton({
  className,
  radius,
  height,
  ...props
}: SkeletonProps) {
  return (
    <div
      className={cn(skeletonVariants({ radius, height }), className)}
      {...props}
    />
  )
}

export { Skeleton }
