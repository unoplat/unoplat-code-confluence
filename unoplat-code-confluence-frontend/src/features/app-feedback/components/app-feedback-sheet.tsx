import { useRef } from "react";
import confetti from "canvas-confetti";
import { ExternalLink, Loader2, Sparkles } from "lucide-react";
import { useRouterState } from "@tanstack/react-router";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { getFieldErrorMessages, useAppForm, useFieldContext } from "@/forms";
import { cn } from "@/lib/utils";

import { type AppFeedbackResponse, submitAppFeedback } from "../api";
import type { AppFeedbackCategory } from "../schema";
import { useAppFeedbackSheetStore } from "../store";
import { FeedbackCategorySelector } from "./feedback-category-selector";

const FORM_SECTION_CLASS_NAME = "flex flex-col gap-[8px]";
const FORM_LABEL_CLASS_NAME = "text-[13px] leading-[16px] font-medium";
const FORM_META_CLASS_NAME = "text-[11px] leading-[14px]";

/**
 * Inner component for category field using useFieldContext
 * Wires FeedbackCategorySelector to TanStack Form field state
 */
function CategoryFieldInner(): React.ReactElement {
  const field = useFieldContext<AppFeedbackCategory>();

  return (
    <FeedbackCategorySelector
      value={field.state.value || undefined}
      onChange={(cat) => field.handleChange(cat)}
    />
  );
}

/**
 * Inner component for subject field using useFieldContext
 * Wires shadcn Input to TanStack Form field state
 */
function SubjectFieldInner(): React.ReactElement {
  const field = useFieldContext<string>();
  const errors = getFieldErrorMessages(field.state.meta.errors);
  const hasErrors = errors.length > 0;

  return (
    <div className="space-y-[4px]">
      <Input
        value={field.state.value ?? ""}
        onChange={(e) => field.handleChange(e.target.value)}
        onBlur={field.handleBlur}
        placeholder="Brief summary of your feedback"
        maxLength={100}
        className={cn(
          "h-[38px] px-[12px] py-[8px] text-[13px] leading-[20px] shadow-none md:text-[13px]",
          hasErrors && "border-destructive",
        )}
      />
      {hasErrors && (
        <p className="text-destructive text-[12px] leading-[16px]">
          {errors[0]}
        </p>
      )}
    </div>
  );
}

function DescriptionFieldInner(): React.ReactElement {
  const field = useFieldContext<string>();
  const errors = getFieldErrorMessages(field.state.meta.errors);
  const hasErrors = errors.length > 0;
  const charCount = field.state.value.length;

  return (
    <div className="space-y-[8px]">
      <div className="flex items-center justify-between gap-[12px]">
        <Label className={FORM_LABEL_CLASS_NAME}>Description</Label>
        <span
          className={cn(
            FORM_META_CLASS_NAME,
            hasErrors ? "text-destructive" : "text-muted-foreground",
          )}
        >
          {charCount}/2000
        </span>
      </div>
      <Textarea
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
        onBlur={field.handleBlur}
        placeholder="Tell us more..."
        maxLength={2000}
        rows={5}
        state={hasErrors ? "error" : "default"}
        className="min-h-[120px] px-[12px] py-[8px] text-[13px] leading-[20px] shadow-none md:text-[13px]"
      />
      {hasErrors && (
        <p className="text-destructive text-[12px] leading-[16px]">
          {errors[0]}
        </p>
      )}
    </div>
  );
}

export function AppFeedbackSheet(): React.ReactElement {
  const { isOpen, close } = useAppFeedbackSheetStore();
  const submittedIssueRef = useRef<AppFeedbackResponse | null>(null);

  const pathname = useRouterState({
    select: (s) => s.location.pathname,
  });

  const form = useAppForm({
    defaultValues: {
      category: "" as AppFeedbackCategory,
      sentiment: "" as "happy" | "neutral" | "unhappy",
      subject: "",
      description: "",
    },
    onSubmit: async ({ value }) => {
      const result = await submitAppFeedback({
        ...value,
        current_route: pathname,
      });
      submittedIssueRef.current = result;

      // Fire confetti directly after successful submission
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    },
  });

  const handleClose = (): void => {
    close();
    // Delay reset so sheet animation completes before clearing
    setTimeout(() => {
      form.reset();
      submittedIssueRef.current = null;
    }, 300);
  };

  const handleTrackFeedback = (): void => {
    if (submittedIssueRef.current?.issue_url) {
      window.open(
        submittedIssueRef.current.issue_url,
        "_blank",
        "noopener,noreferrer",
      );
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={(v) => !v && handleClose()}>
      <SheetContent
        side="right"
        size="lg"
        className="flex flex-col gap-0 p-0 [&>button]:top-[24px] [&>button]:right-[24px]"
      >
        <SheetHeader className="border-border space-y-[4px] border-b px-[24px] py-[16px]">
          <SheetTitle className="text-[16px] leading-[24px] font-semibold">
            Send Feedback
          </SheetTitle>
          <SheetDescription className="text-[13px] leading-[18px]">
            Help us improve Unoplat Code Confluence
          </SheetDescription>
        </SheetHeader>

        <form.Subscribe selector={(state) => state.isSubmitSuccessful}>
          {(isSubmitSuccessful) =>
            isSubmitSuccessful ? (
              <div className="flex flex-1 flex-col items-center justify-center px-6 py-8">
                <Card className="w-full max-w-sm border-0 shadow-none">
                  <CardHeader className="items-center pb-4 text-center">
                    <div className="bg-primary/10 mb-4 flex h-16 w-16 items-center justify-center rounded-full">
                      <Sparkles className="text-primary h-8 w-8" />
                    </div>
                    <CardTitle className="text-xl">Got it!</CardTitle>
                    <CardDescription>
                      Your feedback is now a GitHub issue. We&apos;ll take it
                      from here.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col items-center gap-6">
                    {submittedIssueRef.current?.issue_number && (
                      <Badge variant="secondary" className="text-sm">
                        Issue #{submittedIssueRef.current.issue_number}
                      </Badge>
                    )}
                    <div className="flex flex-col gap-3 sm:flex-row">
                      {submittedIssueRef.current?.issue_url && (
                        <Button variant="default" onClick={handleTrackFeedback}>
                          <ExternalLink className="mr-2 h-4 w-4" />
                          Track Feedback
                        </Button>
                      )}
                      <Button variant="outline" onClick={handleClose}>
                        Close
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <>
                <ScrollArea className="flex-1">
                  <form
                    id="feedback-form"
                    onSubmit={(e) => {
                      e.preventDefault();
                      form.handleSubmit();
                    }}
                    className="flex flex-col gap-[24px] px-[24px] py-[24px]"
                  >
                    {/* Category */}
                    <div className={FORM_SECTION_CLASS_NAME}>
                      <Label className={FORM_LABEL_CLASS_NAME}>Category</Label>
                      <form.AppField name="category">
                        {() => <CategoryFieldInner />}
                      </form.AppField>
                    </div>

                    {/* Sentiment */}
                    <div className={FORM_SECTION_CLASS_NAME}>
                      <Label className={FORM_LABEL_CLASS_NAME}>
                        How are you feeling?
                      </Label>
                      <form.AppField name="sentiment">
                        {(field) => <field.EmojiRatingField />}
                      </form.AppField>
                    </div>

                    {/* Subject */}
                    <div className={FORM_SECTION_CLASS_NAME}>
                      <Label className={FORM_LABEL_CLASS_NAME}>Subject</Label>
                      <form.AppField name="subject">
                        {() => <SubjectFieldInner />}
                      </form.AppField>
                    </div>

                    {/* Description */}
                    <div className={FORM_SECTION_CLASS_NAME}>
                      <form.AppField name="description">
                        {() => <DescriptionFieldInner />}
                      </form.AppField>
                    </div>
                  </form>
                </ScrollArea>

                {/* Footer */}
                <div className="border-border flex shrink-0 items-center justify-between border-t px-[24px] py-[16px]">
                  <Button
                    variant="outline"
                    className="h-[34px] px-[16px] py-[8px] text-[13px] leading-[16px]"
                    onClick={handleClose}
                  >
                    Cancel
                  </Button>
                  <form.Subscribe
                    selector={(state) => [state.canSubmit, state.isSubmitting]}
                  >
                    {([canSubmit, isSubmitting]) => (
                      <Button
                        type="submit"
                        form="feedback-form"
                        disabled={!canSubmit || isSubmitting}
                        className="h-[32px] px-[16px] py-[8px] text-[13px] leading-[16px]"
                      >
                        {isSubmitting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Submitting...
                          </>
                        ) : (
                          "Submit"
                        )}
                      </Button>
                    )}
                  </form.Subscribe>
                </div>
              </>
            )
          }
        </form.Subscribe>
      </SheetContent>
    </Sheet>
  );
}
