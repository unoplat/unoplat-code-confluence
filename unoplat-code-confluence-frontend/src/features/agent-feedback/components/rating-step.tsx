import { useMemo } from "react";
import { SiGithub } from "react-icons/si";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAppForm, useFieldContext } from "@/forms";
import type { ParentWorkflowJobResponse } from "@/types";
import type { RepositoryAgentCodebaseState } from "@/features/repository-agent-snapshots/transformers";

import type {
  AgentId,
  AgentRatingValue,
  AgentSentimentRating,
  SentimentRating,
} from "../schema";
import { AGENT_IDS, AGENT_ID_LABELS } from "../schema";
import { useAgentFeedbackStore } from "../store";
import { ThumbsRatingSelector } from "./thumbs-rating-selector";

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
 * Uses context-based field access for nested components (CodebaseAccordionItem, AgentRatingRow).
 */
export function RatingStep({
  codebases,
  job,
  onCancel,
  onContinue,
}: RatingStepProps): React.ReactElement {
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
      <ScrollArea className="flex-1">
        {/* Repository Info Card */}
        <Card className="border-muted/50 mx-7 mt-6">
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

        {/* Overall Rating Section */}
        <div className="flex flex-col gap-2.5 px-7 pt-4">
          <Label className="text-base font-medium">
            How was your experience with the generated agents?
          </Label>
          <form.AppField name="overallRating">
            {(field) => <field.EmojiRatingField />}
          </form.AppField>
        </div>

        {/* Per-Agent Ratings Accordion */}
        <div className="flex flex-col px-7 pt-4 pb-4">
          <Label className="text-muted-foreground text-sm font-medium">
            Rate individual agents (optional)
          </Label>
          <form.AppField name="agentRatings">
            {() => (
              <Accordion
                type="multiple"
                defaultValue={codebases[0] ? [codebases[0].codebaseName] : []}
              >
                {codebases.map((codebase) => (
                  <CodebaseAccordionItem
                    key={codebase.codebaseName}
                    codebase={codebase}
                  />
                ))}
              </Accordion>
            )}
          </form.AppField>
        </div>
      </ScrollArea>

      <DialogFooter variant="sticky">
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
      </DialogFooter>
    </>
  );
}

// ─────────────────────────────────────────────────
// Sub-component: CodebaseAccordionItem
// ─────────────────────────────────────────────────

interface CodebaseAccordionItemProps {
  codebase: RepositoryAgentCodebaseState;
}

/**
 * Accordion item showing agent ratings for a single codebase.
 *
 * Reads the agentRatings array via useFieldContext to compute
 * the progress badge count (rated / total agents).
 */
function CodebaseAccordionItem({
  codebase,
}: CodebaseAccordionItemProps): React.ReactElement {
  const field = useFieldContext<AgentRatingValue[]>();

  // Count non-null ratings for this codebase
  const ratedCount = field.state.value.filter(
    (ar) => ar.codebase_name === codebase.codebaseName && ar.rating !== null,
  ).length;

  return (
    <AccordionItem value={codebase.codebaseName}>
      <AccordionTrigger className="text-sm hover:no-underline">
        <div className="flex items-center gap-2">
          <span className="font-medium">{codebase.codebaseName}</span>
          <Badge variant="secondary">
            {ratedCount}/{AGENT_IDS.length}
          </Badge>
        </div>
      </AccordionTrigger>
      <AccordionContent className="space-y-3">
        {AGENT_IDS.map((agentId) => (
          <AgentRatingRow
            key={`${codebase.codebaseName}-${agentId}`}
            codebaseName={codebase.codebaseName}
            agentId={agentId}
          />
        ))}
      </AccordionContent>
    </AccordionItem>
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
 * Single row for rating one agent with thumbs up/down.
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
  const currentRating =
    index >= 0 ? (field.state.value[index]?.rating ?? null) : null;

  const handleChange = (rating: AgentSentimentRating | null): void => {
    if (index >= 0) {
      const updated = [...field.state.value];
      updated[index] = { ...updated[index], rating };
      field.handleChange(updated);
    }
  };

  return (
    <div className="flex items-center justify-between gap-3">
      <Label className="text-muted-foreground min-w-0 text-sm">
        {AGENT_ID_LABELS[agentId]}
      </Label>
      <ThumbsRatingSelector value={currentRating} onChange={handleChange} />
    </div>
  );
}
