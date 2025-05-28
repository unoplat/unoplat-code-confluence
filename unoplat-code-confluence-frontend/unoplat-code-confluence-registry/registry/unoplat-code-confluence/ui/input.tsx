import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground border-input flex h-9 w-full min-w-0 rounded-md border bg-background px-3 py-2 text-sm shadow-sm transition-all duration-200 outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted",
        "hover:border-input/60 focus:border-primary focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
        "aria-invalid:border-destructive aria-invalid:focus:ring-destructive",
        className
      )}
      {...props}
    />
  )
}

export { Input }
