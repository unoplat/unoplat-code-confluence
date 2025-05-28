import * as React from "react"
import { FeedbackForm } from "@/registry/unoplat-code-confluence/blocks/feedback-form"
import { Button } from "@/registry/unoplat-code-confluence/ui/button"
import { ModeToggle } from "@/components/mode-toggle"

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto flex flex-col min-h-svh px-4 py-8 gap-8">
      <header className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Unoplat Code Confluence Registry</h1>
            <p className="text-muted-foreground">
              A custom registry for distributing Unoplat design system components.
            </p>
          </div>
          <ModeToggle />
        </div>
      </header>
      <main className="flex flex-col flex-1 gap-8">
        <div className="flex flex-col gap-4 border rounded-lg p-4 min-h-[450px] relative">
          <div className="flex items-center justify-between">
            <h2 className="text-sm text-muted-foreground sm:pl-3">
              A feedback form with validation using Unoplat UI components
            </h2>
            <Button size="sm" variant="outline">
              View Component
            </Button>
          </div>
          <div className="flex items-center justify-center min-h-[500px] relative">
            <FeedbackForm />
          </div>
        </div>
      </main>
    </div>
  )
}
