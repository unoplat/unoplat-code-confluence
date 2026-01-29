import React from "react";
import { useForm } from "@tanstack/react-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ExternalLink, Loader2, Eye, EyeOff } from "lucide-react";
import { exaApiKeySchema } from "../schema";
import { TOOL_PROVIDER_HELP_URLS } from "../constants";
import { useSaveToolConfig } from "@/hooks/useSaveToolConfig";
import { cn } from "@/lib/utils";

interface ExaConfigFormProps {
  onCancel: () => void;
  onSuccess: () => void;
  className?: string;
}

/**
 * Form component for configuring Exa API key
 * Uses TanStack Form with Zod validation
 */
export function ExaConfigForm({
  onCancel,
  onSuccess,
  className,
}: ExaConfigFormProps): React.ReactElement {
  const [showApiKey, setShowApiKey] = React.useState(false);
  const saveConfigMutation = useSaveToolConfig();

  const form = useForm({
    defaultValues: {
      api_key: "",
    },
    onSubmit: async ({ value }) => {
      saveConfigMutation.mutate(
        { provider: "exa", apiKey: value.api_key },
        {
          onSuccess: () => {
            form.reset();
            onSuccess();
          },
        },
      );
    },
  });

  const toggleShowApiKey = () => {
    setShowApiKey((prev) => !prev);
  };

  return (
    <form
      className={cn("space-y-4", className)}
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="api_key" className="text-sm font-medium">
            API Key
          </Label>
          <a
            href={TOOL_PROVIDER_HELP_URLS.exa}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-xs transition-colors"
          >
            Get API Key
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>

        <form.Field
          name="api_key"
          validators={{
            onChange: ({ value }) => {
              const result = exaApiKeySchema.shape.api_key.safeParse(value);
              return result.success
                ? undefined
                : result.error.errors[0]?.message;
            },
          }}
        >
          {(field) => (
            <div className="space-y-1">
              <div className="relative">
                <Input
                  id="api_key"
                  type={showApiKey ? "text" : "password"}
                  autoComplete="off"
                  placeholder="Enter your Exa API key"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  aria-invalid={
                    field.state.meta.errors?.length ? "true" : undefined
                  }
                  aria-describedby={
                    field.state.meta.errors?.length
                      ? "api_key-error"
                      : "api_key-help"
                  }
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute top-1/2 right-1 h-7 w-7 -translate-y-1/2 p-0"
                  onClick={toggleShowApiKey}
                  aria-label={showApiKey ? "Hide API key" : "Show API key"}
                >
                  {showApiKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {field.state.meta.errors?.length ? (
                <p id="api_key-error" className="text-destructive text-xs">
                  {String(field.state.meta.errors[0])}
                </p>
              ) : (
                <p id="api_key-help" className="text-muted-foreground text-xs">
                  Your API key is encrypted before storage
                </p>
              )}
            </div>
          )}
        </form.Field>
      </div>

      <div className="flex items-center justify-end gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onCancel}
          disabled={saveConfigMutation.isPending}
        >
          Cancel
        </Button>
        <form.Subscribe
          selector={(state) => ({
            canSubmit: state.canSubmit,
            isDirty: state.isDirty,
            isSubmitting: state.isSubmitting,
          })}
        >
          {({ canSubmit, isDirty, isSubmitting }) => (
            <Button
              type="submit"
              size="sm"
              disabled={!canSubmit || !isDirty || saveConfigMutation.isPending}
            >
              {saveConfigMutation.isPending || isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save"
              )}
            </Button>
          )}
        </form.Subscribe>
      </div>
    </form>
  );
}
