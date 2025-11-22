import React, { useState } from "react";
import { useForm } from "@tanstack/react-form";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Eye, EyeOff } from "lucide-react";
import { toast } from "sonner";
import {
  CredentialNamespace,
  ProviderKey,
  SecretKind,
} from "@/types/credential-enums";
import { getProviderDisplayName } from "@/lib/utils/provider-utils";
import { useProviderMutations } from "@/hooks/use-provider-mutations";
import { DEFAULT_REPOSITORY_CREDENTIAL_PARAMS } from "@/lib/constants/credentials";
import { buildGitHubPatLink } from "@/lib/github-token-utils";
import { z } from "zod";

function buildGitHubPatLinkForHost(host: string): string {
  const sanitizedHost = host.replace(/\/$/, "");
  const base = `${sanitizedHost}/settings/tokens/new`;
  const defaultLink = buildGitHubPatLink();
  const [, query = ""] = defaultLink.split("?");
  return query ? `${base}?${query}` : base;
}

interface RepositoryProviderFormProps {
  trigger?: React.ReactNode;
  inline?: boolean;
  isUpdate?: boolean;
  existingProvider?: ProviderKey;
}

const repositoryProviderSchema = z
  .object({
    provider_key: z.nativeEnum(ProviderKey, {
      required_error: "Please select a provider",
    }),
    patToken: z.string().trim().min(1, "PAT token is required"),
    url: z.string().trim(),
  })
  .superRefine((data, ctx) => {
    if (data.provider_key === ProviderKey.GITHUB_ENTERPRISE) {
      if (data.url && !/^https?:\/\//i.test(data.url)) {
        ctx.addIssue({
          path: ["url"],
          code: z.ZodIssueCode.custom,
          message: "Enter a valid URL including http(s)://",
        });
      }
    }
  });

export function RepositoryProviderForm({
  trigger,
  inline = false,
  isUpdate = false,
  existingProvider,
}: RepositoryProviderFormProps): React.ReactElement {
  const [open, setOpen] = useState(inline);
  const [showToken, setShowToken] = useState(false);
  const { submitToken, updateToken } = useProviderMutations();
  const navigate = useNavigate();

  const form = useForm({
    defaultValues: {
      provider_key:
        isUpdate && existingProvider
          ? (existingProvider as ProviderKey)
          : (ProviderKey.GITHUB_OPEN as ProviderKey),
      patToken: "",
      url: "",
    },
    validators: {
      onBlur: repositoryProviderSchema,
    },
    onSubmit: async ({ value }) => {
      const providerKey = value.provider_key;
      const trimmedToken = value.patToken.trim();
      const trimmedUrl = value.url.trim();

      const credentialParams = {
        ...DEFAULT_REPOSITORY_CREDENTIAL_PARAMS,
        namespace: CredentialNamespace.REPOSITORY,
        secret_kind: SecretKind.PAT,
        provider_key: providerKey,
        ...(trimmedUrl ? { url: trimmedUrl } : {}),
      };

      const mutation = isUpdate ? updateToken : submitToken;

      mutation.mutate(
        { token: trimmedToken, params: credentialParams },
        {
          onSuccess: () => {
            toast.success(
              isUpdate
                ? "Provider token updated successfully"
                : "Provider connected",
            );

            if (!isUpdate) {
              navigate({
                to: "/onboarding/$provider",
                params: {
                  provider:
                    providerKey === ProviderKey.GITHUB_ENTERPRISE
                      ? "github-enterprise"
                      : "github",
                },
              });
            }

            form.reset();
            setOpen(false);
          },
          onError: (error: Error) => {
            toast.error(
              error.message ||
                `Failed to ${isUpdate ? "update" : "connect"} provider`,
            );
          },
        },
      );
    },
  });

  const formBody = (
    <form
      className="space-y-4"
      onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit();
      }}
    >
      <form.Field name="provider_key">
        {(field) => (
          <div className="space-y-2 text-left">
            <Label htmlFor="provider_key" className="block text-left">
              Provider
            </Label>
            <Select
              value={field.state.value}
              onValueChange={(value) =>
                field.handleChange(value as ProviderKey)
              }
              disabled={isUpdate}
            >
              <SelectTrigger id="provider_key">
                <SelectValue placeholder="Choose a provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ProviderKey.GITHUB_OPEN}>GitHub</SelectItem>
                <SelectItem value={ProviderKey.GITHUB_ENTERPRISE}>
                  GitHub Enterprise
                </SelectItem>
              </SelectContent>
            </Select>
            {field.state.meta.isTouched &&
              field.state.meta.errors.length > 0 && (
                <p className="text-destructive text-sm">
                  {(() => {
                    const error = field.state.meta.errors[0] as
                      | string
                      | { message: string }
                      | undefined;
                    return typeof error === "string"
                      ? error
                      : (error?.message ?? "");
                  })()}
                </p>
              )}
          </div>
        )}
      </form.Field>

      <form.Subscribe selector={(state) => state.values.provider_key}>
        {(provider_key) =>
          provider_key === ProviderKey.GITHUB_ENTERPRISE && (
            <form.Field name="url">
              {(field) => (
                <div className="space-y-2 text-left">
                  <Label htmlFor="url" className="block text-left">
                    Base URL (optional)
                  </Label>
                  <Input
                    id="url"
                    type="url"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    placeholder="https://yourcompany.ghe.com or https://github.mycompany.com"
                  />
                  {field.state.meta.isTouched &&
                    field.state.meta.errors.length > 0 && (
                      <p className="text-destructive text-sm">
                        {(() => {
                          const error = field.state.meta.errors[0] as
                            | string
                            | { message: string }
                            | undefined;
                          return typeof error === "string"
                            ? error
                            : (error?.message ?? "");
                        })()}
                      </p>
                    )}
                </div>
              )}
            </form.Field>
          )
        }
      </form.Subscribe>

      <form.Field name="patToken">
        {(field) => (
          <div className="space-y-2 text-left">
            <Label htmlFor="patToken" className="block text-left">
              Personal Access Token
            </Label>
            <div className="relative">
              <Input
                id="patToken"
                type={showToken ? "text" : "password"}
                value={field.state.value}
                onChange={(e) => field.handleChange(e.target.value)}
                onBlur={field.handleBlur}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute top-0 right-0 h-full px-3 hover:bg-transparent"
                onClick={() => setShowToken((v) => !v)}
              >
                {showToken ? (
                  <EyeOff className="text-muted-foreground h-4 w-4" />
                ) : (
                  <Eye className="text-muted-foreground h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-muted-foreground text-xs">
              Personal Access Token for the selected provider.
            </p>
            {field.state.meta.isTouched &&
              field.state.meta.errors.length > 0 && (
                <p className="text-destructive text-sm">
                  {(() => {
                    const error = field.state.meta.errors[0] as
                      | string
                      | { message: string }
                      | undefined;
                    return typeof error === "string"
                      ? error
                      : (error?.message ?? "");
                  })()}
                </p>
              )}
          </div>
        )}
      </form.Field>

      <div className="flex items-center justify-between">
        <form.Subscribe
          selector={(state) => [state.values.provider_key, state.values.url]}
        >
          {([provider_key, url]) => (
            <a
              className="text-primary text-sm font-medium underline underline-offset-4"
              href={
                provider_key === ProviderKey.GITHUB_ENTERPRISE && url
                  ? buildGitHubPatLinkForHost(url)
                  : buildGitHubPatLink()
              }
              target="_blank"
              rel="noreferrer"
            >
              Generate token on{" "}
              {getProviderDisplayName(provider_key as ProviderKey)}
            </a>
          )}
        </form.Subscribe>
        <div className="flex gap-2">
          {!inline && (
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
          )}
          <form.Subscribe
            selector={(state) => [state.canSubmit, state.isSubmitting]}
          >
            {([canSubmit, isSubmitting]) => (
              <Button type="submit" disabled={!canSubmit}>
                {isSubmitting
                  ? isUpdate
                    ? "Updating..."
                    : "Connecting..."
                  : isUpdate
                    ? "Update Token"
                    : "Connect"}
              </Button>
            )}
          </form.Subscribe>
        </div>
      </div>
    </form>
  );

  if (inline) {
    return (
      <div className="bg-card w-full max-w-xl rounded-lg border p-6 shadow-sm">
        <h3 className="text-lg font-semibold">
          {isUpdate ? "Update provider token" : "Add repository provider"}
        </h3>
        <p className="text-muted-foreground text-sm">
          {isUpdate
            ? "Update your Personal Access Token for the selected provider."
            : "Choose GitHub or GitHub Enterprise and paste a PAT."}
        </p>
        <div className="mt-4">{formBody}</div>
      </div>
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {isUpdate ? "Update provider token" : "Add repository provider"}
          </DialogTitle>
          <DialogDescription>
            {isUpdate
              ? "Update your Personal Access Token for the selected provider."
              : "Connect another provider to manage its repositories."}
          </DialogDescription>
        </DialogHeader>
        {formBody}
      </DialogContent>
    </Dialog>
  );
}
