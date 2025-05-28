import React from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useDevModeStore } from "@/stores/useDevModeStore"
import { Workflow, Network, ExternalLink } from "lucide-react"
import { env } from "@/lib/env"

export default function DeveloperModePage(): React.ReactElement {
  const { isDevMode, setDevMode } = useDevModeStore()
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6">
        <Card className="shadow-md border-border bg-card">
          <CardHeader className="max-w-4xl mx-auto px-8 py-6">
            <div className="flex items-center justify-between space-x-6">
              <div className="space-y-2">
                <CardTitle className="text-xl font-semibold tracking-tight">Developer Mode</CardTitle>
                <CardDescription className="text-base text-muted-foreground leading-relaxed">
                  Toggle Developer Mode to access code confluence's infrastructure tooling.
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={isDevMode}
                  onCheckedChange={(checked: boolean): void => { setDevMode(checked) }}
                  aria-label="Toggle developer mode"
                />
              </div>
            </div>
          </CardHeader>
          {isDevMode && (
            <CardContent className="px-8 pt-0 pb-6 max-w-4xl mx-auto">
              <div className="mt-6 space-y-6">
                <div className="grid grid-cols-[1fr_auto] gap-6 items-center">
                  <div className="min-w-0">
                    <h3 className="text-base font-semibold mb-2">Workflow Orchestrator</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed break-words">
                      Access and manage automated workflows, view execution logs, and debug orchestration issues.
                    </p>
                  </div>
                  <div className="flex justify-end">
                    <Button 
                      asChild 
                      variant="outline" 
                      size="default" 
                      className="min-w-[160px] hover:bg-accent hover:text-accent-foreground"
                    >
                      <a
                        href={env.workflowOrchestratorUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2"
                        aria-label="Open Workflow Orchestrator in new tab"
                      >
                        <Workflow className="h-4 w-4" />
                        <span>Workflow Orchestrator</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </Button>
                  </div>
                </div>
                
                <Separator />
                
                <div className="grid grid-cols-[1fr_auto] gap-6 items-center">
                  <div className="min-w-0">
                    <h3 className="text-base font-semibold mb-2">Knowledge Graph</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed break-words">
                      Explore the knowledge graph, inspect entities and relationships, and debug data connections.
                    </p>
                  </div>
                  <div className="flex justify-end">
                    <Button 
                      asChild 
                      variant="outline" 
                      size="default" 
                      className="min-w-[160px] hover:bg-accent hover:text-accent-foreground"
                    >
                      <a
                        href={env.knowledgeGraphUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2"
                        aria-label="Open Knowledge Graph in new tab"
                      >
                        <Network className="h-4 w-4" />
                        <span>Knowledge Graph</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  )
}