import React from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useDevModeStore } from "@/stores/useDevModeStore"
import { Workflow, Network } from "lucide-react"
import { env } from "@/lib/env"

export default function DeveloperModePage(): React.ReactElement {
  const { isDevMode, setDevMode } = useDevModeStore()
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6">
        <Card className="shadow-sm rounded-none border-x-0">
          <CardHeader className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between space-x-4">
              <div className="space-y-1">
                <CardTitle>Developer Mode</CardTitle>
                <CardDescription className="text-base font-normal leading-normal">
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
            <CardContent className="px-6 pt-0 pb-6 max-w-4xl mx-auto">
              <div className="mt-4 space-y-4">
                <div className="grid grid-cols-[1fr_auto] gap-4 items-center">
                  <div className="min-w-0">
                    <h3 className="text-sm font-medium mb-1">Workflow Orchestrator</h3>
                    <p className="text-muted-foreground text-xs leading-normal break-words">
                      Access and manage automated workflows, view execution logs, and debug orchestration issues.                    </p>
                  </div>
                  <div className="flex justify-end">
                    <Button 
                      asChild 
                      variant="outline" 
                      size="default" 
                      className="w-auto max-w-xs hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 dark:hover:bg-blue-900/20 dark:hover:text-blue-400"
                    >
                      <a
                        href={env.workflowOrchestratorUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2"
                      >
                        <Workflow className="h-4 w-4" />
                        Workflow Orchestrator
                      </a>
                    </Button>
                  </div>
                </div>
                
                <Separator />
                
                <div className="grid grid-cols-[1fr_auto] gap-4 items-center">
                  <div className="min-w-0">
                    <h3 className="text-sm font-medium mb-1">Knowledge Graph</h3>
                    <p className="text-muted-foreground text-xs leading-normal break-words">
                      Explore the knowledge graph, inspect entities and relationships, and debug data connections.
                    </p>
                  </div>
                  <div className="flex justify-end">
                    <Button 
                      asChild 
                      variant="outline" 
                      size="default" 
                      className="w-auto max-w-xs hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 dark:hover:bg-blue-900/20 dark:hover:text-blue-400"
                    >
                      <a
                        href={env.knowledgeGraphUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2"
                      >
                        <Network className="h-4 w-4" />
                        Knowledge Graph
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