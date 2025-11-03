import * as React from "react"
import * as SeparatorPrimitive from "@radix-ui/react-separator"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const separatorVariants = cva("shrink-0 bg-border transition-colors", {
  variants: {
    size: {
      default: "",
      sm: "",
      lg: "",
    },
    variant: {
      default: "bg-border",
      muted: "bg-muted",
      accent: "bg-accent",
    },
  },
  defaultVariants: {
    size: "default",
    variant: "default",
  },
})

export interface SeparatorProps
  extends React.ComponentPropsWithoutRef<typeof SeparatorPrimitive.Root>,
    VariantProps<typeof separatorVariants> {}

const Separator = React.forwardRef<
  React.ElementRef<typeof SeparatorPrimitive.Root>,
  SeparatorProps
>(
  (
    { className, orientation = "horizontal", decorative = true, size, variant, ...props },
    ref
  ) => {
    const orientationClass = orientation === "horizontal" 
      ? size === "sm" ? "h-[0.5px] w-full" 
        : size === "lg" ? "h-[2px] w-full" 
        : "h-[1px] w-full"
      : size === "sm" ? "h-full w-[0.5px]" 
        : size === "lg" ? "h-full w-[2px]" 
        : "h-full w-[1px]"
    
    return (
      <SeparatorPrimitive.Root
        ref={ref}
        decorative={decorative}
        orientation={orientation}
        className={cn(separatorVariants({ size, variant }), orientationClass, className)}
        {...props}
      />
    )
  }
)
Separator.displayName = SeparatorPrimitive.Root.displayName

export { Separator, separatorVariants }
