import * as React from "react"

import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "border-input placeholder:text-muted-foreground flex field-sizing-content min-h-20 w-full rounded-md border bg-background px-3 py-2 text-sm shadow-sm transition-all duration-200 outline-none disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted resize-y",
        "hover:border-input/60 focus:border-primary focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
        "aria-invalid:border-destructive aria-invalid:focus:ring-destructive",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
