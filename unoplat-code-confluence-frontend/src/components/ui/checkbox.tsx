import * as React from "react";
import * as CheckboxPrimitive from "@radix-ui/react-checkbox";
import { cva, type VariantProps } from "class-variance-authority";
import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

const checkboxVariants = cva(
  "peer shrink-0 border border-border ring-offset-background focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
  {
    variants: {
      size: {
        sm: "h-3 w-3",
        default: "h-4 w-4",
        lg: "h-5 w-5",
      },
      variant: {
        default: "border-primary",
        secondary: "border-secondary",
        muted: "border-muted-foreground",
      },
      radius: {
        none: "rounded-none",
        sm: "rounded-xs",
        default: "rounded-xs",
        md: "rounded-md",
        full: "rounded-full",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
      radius: "default",
    },
  },
);

const checkboxIndicatorVariants = cva(
  "flex items-center justify-center text-current",
  {
    variants: {
      size: {
        sm: "[&>svg]:h-2.5 [&>svg]:w-2.5",
        default: "[&>svg]:h-4 [&>svg]:w-4",
        lg: "[&>svg]:h-4 [&>svg]:w-4",
      },
    },
    defaultVariants: {
      size: "default",
    },
  },
);

export interface CheckboxProps
  extends React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>,
    VariantProps<typeof checkboxVariants> {}

const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  CheckboxProps
>(({ className, size, variant, radius, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(checkboxVariants({ size, variant, radius }), className)}
    {...props}
  >
    <CheckboxPrimitive.Indicator
      className={cn(checkboxIndicatorVariants({ size }))}
    >
      <Check />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
));
Checkbox.displayName = CheckboxPrimitive.Root.displayName;

export { Checkbox };
