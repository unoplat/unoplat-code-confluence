import React from "react";
import { Card } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";
import type {
  WorkflowStatistics,
  UsageStatistics,
} from "@/features/repository-agent-snapshots/schema";

interface AgentStatisticsDisplayProps {
  statistics: WorkflowStatistics | null;
}

function formatNumber(num: number): string {
  return num.toLocaleString();
}

function formatCost(cost: number | null | undefined): string {
  if (cost === null || cost === undefined) {
    return "N/A";
  }
  return `$${cost.toFixed(4)}`;
}

function UsageStatsGrid({
  stats,
}: {
  stats: UsageStatistics;
}): React.ReactElement {
  return (
    <div className="grid grid-cols-2 gap-3 text-sm">
      <div>
        <div className="text-muted-foreground text-xs">Requests</div>
        <div className="font-medium">{formatNumber(stats.requests)}</div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Tool Calls</div>
        <div className="font-medium">{formatNumber(stats.tool_calls)}</div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Input Tokens</div>
        <div className="font-medium">{formatNumber(stats.input_tokens)}</div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Output Tokens</div>
        <div className="font-medium">{formatNumber(stats.output_tokens)}</div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Cache Read</div>
        <div className="font-medium">
          {formatNumber(stats.cache_read_tokens)}
        </div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Cache Write</div>
        <div className="font-medium">
          {formatNumber(stats.cache_write_tokens)}
        </div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Total Tokens</div>
        <div className="font-medium">{formatNumber(stats.total_tokens)}</div>
      </div>
      <div>
        <div className="text-muted-foreground text-xs">Est. Cost</div>
        <div className="font-medium">
          {formatCost(stats.estimated_cost_usd)}
        </div>
      </div>
    </div>
  );
}

export function AgentStatisticsDisplay({
  statistics,
}: AgentStatisticsDisplayProps): React.ReactElement {
  if (!statistics) {
    return (
      <Card className="p-4">
        <div className="text-muted-foreground text-sm">
          No statistics available yet.
        </div>
      </Card>
    );
  }

  const overallStats: UsageStatistics = {
    requests: statistics.total_requests,
    tool_calls: statistics.total_tool_calls,
    input_tokens: statistics.total_input_tokens,
    output_tokens: statistics.total_output_tokens,
    cache_write_tokens: statistics.total_cache_write_tokens,
    cache_read_tokens: statistics.total_cache_read_tokens,
    total_tokens: statistics.total_tokens,
    estimated_cost_usd: statistics.total_estimated_cost_usd,
  };

  const hasCodebaseBreakdown =
    statistics.by_codebase && Object.keys(statistics.by_codebase).length > 0;

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <h3 className="mb-3 text-sm font-semibold">
          Overall Workflow Statistics
        </h3>
        <UsageStatsGrid stats={overallStats} />
      </Card>

      {hasCodebaseBreakdown && (
        <Card className="p-4">
          <h3 className="mb-3 text-sm font-semibold">Per-Codebase Breakdown</h3>
          <div className="space-y-2">
            {Object.entries(statistics.by_codebase).map(
              ([codebaseName, stats]) => (
                <Collapsible key={codebaseName}>
                  <CollapsibleTrigger className="hover:bg-accent flex w-full items-center justify-between rounded-md border p-2 text-sm">
                    <span className="font-medium">{codebaseName}</span>
                    <ChevronDown className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180" />
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-2 rounded-md border p-3">
                    <UsageStatsGrid stats={stats} />
                  </CollapsibleContent>
                </Collapsible>
              ),
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
