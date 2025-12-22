import { useMemo, useState } from "react";
import { ChevronDown } from "lucide-react";
import { SiGithub } from "react-icons/si";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { SheetFooter } from "@/components/ui/sheet";
import { useAppForm, useFieldContext } from "@/forms";
import { cn } from "@/lib/utils";
import type { ParentWorkflowJobResponse } from "@/types";
import type { RepositoryAgentCodebaseState } from "@/features/repository-agent-snapshots/transformers";

import type { AgentId, AgentRatingValue, SentimentRating } from "../schema";
import { AGENT_IDS, AGENT_ID_LABELS } from "../schema";
import { useAgentFeedbackStore } from "../store";
import { MiniEmojiSelector } from "./mini-emoji-selector";

interface RatingStepProps {
  /** Codebases from Electric SQL snapshot */
  codebases: RepositoryAgentCodebaseState[];
  /** Job data for repository info display */
  job: ParentWorkflowJobResponse;
  /** Callback when user cancels */
  onCancel: () => void;
  /** Callback when user continues to next step */
  onContinue: () => void;
}

/**
 * Rating step - First step of feedback flow
 *
 * Owns its form via `useAppForm` and syncs values to Zustand store on navigation.
 * Uses context-based field access for nested components (CodebaseRatingCard, AgentRatingRow).
 */
export function RatingStep({
  codebases,
  job,
  onCancel,
  onContinue,
}: RatingStepProps): React.ReactElement {
  const [agentRatingsOpen, setAgentRatingsOpen] = useState(true);
  const { draft, setDraft } = useAgentFeedbackStore();

  // Build initial agent ratings array from codebases + stored draft
  const initialAgentRatings = useMemo((): AgentRatingValue[] => {
    const ratings: AgentRatingValue[] = [];
    for (const codebase of codebases) {
      for (const agentId of AGENT_IDS) {
        const storedRating = draft.agentRatings.find(
          (ar) =>
            ar.codebase_name === codebase.codebaseName &&
            ar.agent_id === agentId,
        );
        ratings.push({
          codebase_name: codebase.codebaseName,
          agent_id: agentId,
          rating: storedRating?.rating ?? null,
        });
      }
    }
    return ratings;
  }, [codebases, draft.agentRatings]);

  // Create form with useAppForm - provides context for nested components
  const form = useAppForm({
    defaultValues: {
      overallRating: draft.overallRating as SentimentRating | undefined,
      agentRatings: initialAgentRatings,
    },
  });

  // Sync form values to store before navigating to next step
  const handleContinue = (): void => {
    setDraft({
      overallRating: form.state.values.overallRating,
      agentRatings: form.state.values.agentRatings,
    });
    onContinue();
  };

  return (
    <>
      <ScrollArea className="flex-1 px-6">
        <div className="space-y-8 py-6">
          {/* Repository Info Card */}
          <Card className="border-muted/50">
            <CardContent className="flex items-center gap-4 p-4">
              <div className="bg-muted flex h-10 w-10 items-center justify-center rounded-full">
                <SiGithub className="text-muted-foreground h-5 w-5" />
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-medium">
                  {job.repository_owner_name}/{job.repository_name}
                </span>
                <span className="text-muted-foreground text-xs">
                  {codebases.length} codebase{codebases.length !== 1 ? "s" : ""}{" "}
                  analyzed
                </span>
              </div>
            </CardContent>
          </Card>

          <Separator />

          {/* Overall Rating Section */}
          <div className="space-y-2">
            <Label className="text-base font-medium">
              How was your experience with the generated agents?
            </Label>
            <form.AppField name="overallRating">
              {(field) => <field.EmojiRatingField />}
            </form.AppField>
          </div>

          <Separator />

          {/* Per-Agent Ratings Collapsible */}
          <Collapsible
            open={agentRatingsOpen}
            onOpenChange={setAgentRatingsOpen}
          >
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className="flex h-auto w-full justify-between px-0 py-2 hover:bg-transparent"
              >
                <span className="text-muted-foreground text-sm font-medium">
                  Rate individual agents (optional)
                </span>
                <ChevronDown
                  className={cn(
                    "text-muted-foreground h-4 w-4 transition-transform",
                    agentRatingsOpen && "rotate-180",
                  )}
                />
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-4 pt-4">
              {/* Wrap with agentRatings field context for nested components */}
              <form.AppField name="agentRatings">
                {() => (
                  <>
                    {codebases.map((codebase) => (
                      <CodebaseRatingCard
                        key={codebase.codebaseName}
                        codebase={codebase}
                      />
                    ))}
                  </>
                )}
              </form.AppField>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </ScrollArea>

      <SheetFooter className="flex-row justify-end gap-2 border-t px-6 py-4">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <form.Subscribe selector={(state) => state.values.overallRating}>
          {(overallRating) => (
            <Button onClick={handleContinue} disabled={!overallRating}>
              Continue
            </Button>
          )}
        </form.Subscribe>
      </SheetFooter>
    </>
  );
}

// ─────────────────────────────────────────────────
// Sub-component: CodebaseRatingCard
// ─────────────────────────────────────────────────

interface CodebaseRatingCardProps {
  codebase: RepositoryAgentCodebaseState;
}

/**
 * Card showing agent ratings for a single codebase
 *
 * No form prop needed - nested AgentRatingRow components access
 * field state via useFieldContext (context set by parent form.AppField).
 */
function CodebaseRatingCard({
  codebase,
}: CodebaseRatingCardProps): React.ReactElement {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Badge variant="section">CODEBASE</Badge>
          <span className="text-sm font-medium">{codebase.codebaseName}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {AGENT_IDS.map((agentId) => (
          <AgentRatingRow
            key={`${codebase.codebaseName}-${agentId}`}
            codebaseName={codebase.codebaseName}
            agentId={agentId}
          />
        ))}
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────
// Sub-component: AgentRatingRow
// ─────────────────────────────────────────────────

interface AgentRatingRowProps {
  codebaseName: string;
  agentId: AgentId;
}

/**
 * Single row for rating one agent
 *
 * Uses `useFieldContext` to access the agentRatings array field
 * without requiring form prop drilling. Must be rendered inside
 * a form.AppField wrapper for "agentRatings".
 */
function AgentRatingRow({
  codebaseName,
  agentId,
}: AgentRatingRowProps): React.ReactElement {
  // Access the agentRatings field via context (set by parent form.AppField)
  const field = useFieldContext<AgentRatingValue[]>();

  // Find the index of this agent rating in the array
  const index = field.state.value.findIndex(
    (ar) => ar.codebase_name === codebaseName && ar.agent_id === agentId,
  );
  const currentRating = index >= 0 ? field.state.value[index]?.rating : null;

  const handleChange = (rating: SentimentRating | null): void => {
    if (index >= 0) {
      const updated = [...field.state.value];
      updated[index] = { ...updated[index], rating };
      field.handleChange(updated);
    }
  };

  return (
    <div className="flex items-center justify-between">
      <Label className="text-muted-foreground text-sm">
        {AGENT_ID_LABELS[agentId]}
      </Label>
      <MiniEmojiSelector value={currentRating} onChange={handleChange} />
    </div>
  );
}
