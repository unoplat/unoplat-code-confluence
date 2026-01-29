import React from "react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ExaConfigCard } from "./ExaConfigCard";

/**
 * Main container component for tool/MCP provider configuration
 * Displays all available tool configurations (currently Exa)
 */
export function ToolConfigurationSection(): React.ReactElement {
  return (
    <div className="space-y-6">
      <Card className="border-border bg-card shadow-md">
        <CardHeader className="mx-auto max-w-4xl px-8 py-6">
          <div className="space-y-2">
            <CardTitle className="text-xl font-semibold tracking-tight">
              Tool Configuration
            </CardTitle>
            <CardDescription className="text-muted-foreground text-base leading-relaxed">
              Configure external tools and MCP providers for enhanced code
              intelligence features.
            </CardDescription>
          </div>
        </CardHeader>
      </Card>

      <div className="mx-auto grid max-w-4xl gap-4">
        <ExaConfigCard />
      </div>
    </div>
  );
}
