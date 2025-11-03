import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const inputVariants = cva(
  "flex w-full border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
  {
    variants: {
      size: {
        sm: "h-8 rounded-(--radius-sm) px-3 py-1 text-sm",
        default: "h-10 rounded-(--radius-md) px-3 py-2 text-base md:text-sm",
        lg: "h-12 rounded-(--radius-lg) px-4 py-3 text-lg",
      },
      state: {
        default: "",
        error: "border-destructive focus-visible:ring-destructive",
        success:
          "border-green-500 focus-visible:ring-green-500 dark:border-green-400 dark:focus-visible:ring-green-400",
      },
    },
    defaultVariants: {
      size: "default",
      state: "default",
    },
  },
);

export interface InputProps
  extends Omit<React.ComponentProps<"input">, "size">,
    VariantProps<typeof inputVariants> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, size, state, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(inputVariants({ size, state }), className)}
        ref={ref}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";

export { Input, inputVariants };
