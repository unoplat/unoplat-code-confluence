import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const textareaVariants = cva(
  "flex w-full border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none transition-colors",
  {
    variants: {
      size: {
        sm: "min-h-[60px] rounded-(--radius-sm) px-3 py-2 text-sm",
        default:
          "min-h-[80px] rounded-(--radius-md) px-3 py-2 text-base md:text-sm",
        lg: "min-h-[120px] rounded-(--radius-lg) px-4 py-3 text-lg",
      },
      state: {
        default: "",
        error: "border-destructive focus-visible:ring-destructive",
        success:
          "border-green-500 focus-visible:ring-green-500 dark:border-green-400 dark:focus-visible:ring-green-400",
      },
      resize: {
        none: "resize-none",
        both: "resize",
        horizontal: "resize-x",
        vertical: "resize-y",
      },
      wrap: {
        normal: "",
        code: "whitespace-pre-wrap break-all",
        prose: "whitespace-pre-wrap break-words",
      },
    },
    defaultVariants: {
      size: "default",
      state: "default",
      resize: "vertical",
      wrap: "normal",
    },
  },
);

export interface TextareaProps
  extends React.ComponentProps<"textarea">,
    VariantProps<typeof textareaVariants> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, size, state, resize, wrap, ...props }, ref) => {
    return (
      <textarea
        className={cn(textareaVariants({ size, state, resize, wrap }), className)}
        ref={ref}
        {...props}
      />
    );
  },
);
Textarea.displayName = "Textarea";

export { Textarea, textareaVariants };
