import React from "react";
import { useForm } from "@tanstack/react-form";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Loader2, Save, Trash2, X } from "lucide-react";
import { toast } from "sonner";
import { ConfigField } from "./ConfigField";
import {
  generateProviderConfigSchema,
  getProviderConfigDefaults,
} from "../schema-generator";
import {
  useDeleteModelConfig,
  useSaveProviderConfig,
} from "@/hooks/useSaveModelConfig";
import { useCodexOauth } from "@/hooks/useCodexOauth";
import type { ModelProviderDefinition } from "../types";
import type { ModelConfigResponse } from "@/lib/api";
import { MODEL_NAME_FIELD } from "../constants";

interface ModelConfigFormProps {
  provider: ModelProviderDefinition;
  existingConfig?: ModelConfigResponse | null;
  onCancel: () => void;
  onSuccess?: () => void;
  onDeleted?: () => void;
  className?: string;
}

/**
 * Form component for configuring a model provider using TanStack Form
 * Dynamically generates form fields based on provider metadata
 */
export function ModelConfigForm({
  provider,
  existingConfig,
  onCancel,
  onSuccess,
  onDeleted,
  className,
}: ModelConfigFormProps): React.ReactElement {
  const providerKey = provider.provider_key!;
  const saveConfigMutation = useSaveProviderConfig(providerKey);
  const deleteConfigMutation = useDeleteModelConfig();
  const isCodexProvider = provider.provider_key === "codex_openai";
  const codexOauth = useCodexOauth(isCodexProvider);
  const isActiveProviderConfig =
    existingConfig?.provider_key === provider.provider_key;

  // Generate schema and defaults for this provider
  const schema = React.useMemo(
    () => generateProviderConfigSchema(provider),
    [provider],
  );

  // Merge existing config with defaults
  const defaultValues = React.useMemo(() => {
    const defaults = getProviderConfigDefaults(provider);

    // If we have existing config for this provider, merge it with defaults
    if (
      existingConfig &&
      existingConfig.provider_key === provider.provider_key
    ) {
      return {
        ...defaults,
        [MODEL_NAME_FIELD]:
          existingConfig.model_name || defaults[MODEL_NAME_FIELD],
        // Merge extra_config fields if they exist
        ...(existingConfig.extra_config || {}),
      };
    }

    return defaults;
  }, [provider, existingConfig]);

  const form = useForm({
    defaultValues,
    onSubmit: async ({ value }) => {
      // Transform form values to match API expectations
      const configData = {
        [MODEL_NAME_FIELD]: value[MODEL_NAME_FIELD],
        provider_key: provider.provider_key,
        ...value,
      };

      saveConfigMutation.mutate(configData, {
        onSuccess: () => {
          // Reset form state with current values to clear isDirty flag
          form.reset(form.state.values);
          onSuccess?.();
        },
      });
    },
  });

  const handleCancel = () => {
    if (form.state.isDirty) {
      const confirmDiscard = window.confirm(
        "You have unsaved changes. Are you sure you want to discard them?",
      );
      if (!confirmDiscard) return;
    }
    onCancel();
  };

  const handleConnectChatGpt = async () => {
    const popup = window.open(
      "about:blank",
      "codex-oauth-login",
      "popup=yes,width=560,height=760",
    );
    if (!popup) {
      toast.error("Popup blocked", {
        description: "Please allow popups and retry ChatGPT login.",
      });
      return;
    }

    let oauthConnected = false;

    try {
      const auth = await codexOauth.authorizeMutation.mutateAsync({
        frontend_origin: window.location.origin,
      });
      const authorizeUrl = new URL(auth.authorization_url);
      const redirectUri = authorizeUrl.searchParams.get("redirect_uri");
      const expectedOrigin = redirectUri
        ? new URL(redirectUri).origin
        : "http://localhost:1455";

      popup.location.href = auth.authorization_url;
      const result = await codexOauth.waitForPopupResult(popup, expectedOrigin);

      if (result.status === "success") {
        oauthConnected = true;
        const formValue = form.state.values;

        // Fall back to provider placeholder if model name is empty
        const modelName =
          formValue[MODEL_NAME_FIELD] ||
          provider.model_field?.placeholder ||
          "";

        const configData = {
          provider_key: providerKey,
          ...formValue,
          [MODEL_NAME_FIELD]: modelName,
        };

        // Update the form field so it reflects the chosen model
        form.setFieldValue(MODEL_NAME_FIELD, modelName);

        await saveConfigMutation.mutateAsync(configData, true);
        form.reset(form.state.values);
        codexOauth.invalidateModelQueries();
        toast.success("ChatGPT connected and configuration saved");
        onSuccess?.();
      } else {
        toast.error("ChatGPT connection failed", {
          description: result.error || "OAuth flow failed.",
        });
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unexpected OAuth error";
      toast.error(
        oauthConnected
          ? "ChatGPT connected but failed to save configuration"
          : "Failed to connect ChatGPT",
        { description: message },
      );
    } finally {
      if (!popup.closed) {
        popup.close();
      }
    }
  };

  const handleDisconnectChatGpt = async () => {
    await codexOauth.disconnectMutation.mutateAsync();
    onSuccess?.();
  };

  const handleDeleteConfiguration = () => {
    deleteConfigMutation.mutate(undefined, {
      onSuccess: () => {
        form.reset();
        onDeleted?.();
      },
    });
  };

  const isCodexConnected =
    isCodexProvider &&
    (codexOauth.statusQuery.data?.connected ??
      (existingConfig?.provider_key === "codex_openai"
        ? existingConfig.has_api_key
        : false));

  return (
    <div className={className}>
      <div className="mb-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">
              {existingConfig ? "Update" : "Configure"} {provider.display_name}
            </h3>
            <p className="text-muted-foreground text-sm">
              {existingConfig
                ? `Update your ${provider.display_name} provider configuration`
                : `Set up your ${provider.display_name} provider configuration`}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCancel}
            disabled={
              saveConfigMutation.isPending || deleteConfigMutation.isPending
            }
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="space-y-6"
        >
          {/* Model Field */}
          {provider.model_field && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Model Configuration</h3>

              <form.Field
                name={MODEL_NAME_FIELD}
                validators={{
                  onChange: ({ value }) => {
                    const result =
                      schema.shape[MODEL_NAME_FIELD].safeParse(value);
                    return result.success
                      ? undefined
                      : result.error.errors[0]?.message;
                  },
                }}
              >
                {(field) => (
                  <ConfigField
                    field={{
                      key: MODEL_NAME_FIELD,
                      type: "text",
                      label: provider.model_field.label,
                      placeholder: provider.model_field.placeholder || null,
                      help: provider.model_field.help || null,
                      required: provider.model_field.required,
                      default: null,
                      enum: null,
                    }}
                    value={field.state.value}
                    onChange={field.handleChange}
                    onBlur={field.handleBlur}
                    error={
                      field.state.meta.errors?.[0]
                        ? String(field.state.meta.errors[0])
                        : undefined
                    }
                  />
                )}
              </form.Field>
            </div>
          )}

          {/* Provider-specific Fields */}
          {provider.fields.length > 0 && (
            <>
              {provider.model_field && <Separator />}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Provider Settings</h3>

                <div className="grid gap-4">
                  {provider.fields.map((fieldDef) => (
                    <form.Field
                      key={fieldDef.key}
                      name={fieldDef.key}
                      validators={{
                        onChange: ({ value }) => {
                          const result =
                            schema.shape[fieldDef.key].safeParse(value);
                          return result.success
                            ? undefined
                            : result.error.errors[0]?.message;
                        },
                      }}
                    >
                      {(field) => (
                        <ConfigField
                          field={fieldDef}
                          value={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          error={
                            field.state.meta.errors?.[0]
                              ? String(field.state.meta.errors[0])
                              : undefined
                          }
                        />
                      )}
                    </form.Field>
                  ))}
                </div>
              </div>
            </>
          )}

          {isCodexProvider && (
            <>
              <Separator />
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">ChatGPT OAuth</h3>
                <div className="rounded-md border p-4">
                  <div className="mb-3 flex items-center justify-between gap-4">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">
                        Status:{" "}
                        {isCodexConnected ? "Connected" : "Not connected"}
                      </p>
                      {codexOauth.statusQuery.data?.account_id && (
                        <p className="text-muted-foreground text-xs">
                          Account: {codexOauth.statusQuery.data.account_id}
                        </p>
                      )}
                    </div>
                    {codexOauth.statusQuery.isFetching && (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      onClick={handleConnectChatGpt}
                      disabled={
                        codexOauth.authorizeMutation.isPending ||
                        saveConfigMutation.isPending
                      }
                    >
                      {codexOauth.authorizeMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Starting OAuth...
                        </>
                      ) : isCodexConnected ? (
                        "Reconnect ChatGPT"
                      ) : (
                        "Connect ChatGPT"
                      )}
                    </Button>

                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleDisconnectChatGpt}
                      disabled={
                        !isCodexConnected ||
                        codexOauth.disconnectMutation.isPending
                      }
                    >
                      {codexOauth.disconnectMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Disconnecting...
                        </>
                      ) : (
                        "Disconnect"
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </>
          )}

          <Separator />

          {/* Form Actions */}
          <div className="flex items-center justify-between">
            <div className="text-muted-foreground flex items-center gap-2 text-sm">
              {form.state.errors.length > 0 && (
                <span className="text-red-600">
                  Please fix the errors above
                </span>
              )}
              {form.state.isDirty && !saveConfigMutation.isPending && (
                <span>You have unsaved changes</span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleCancel}
                disabled={
                  saveConfigMutation.isPending || deleteConfigMutation.isPending
                }
              >
                Cancel
              </Button>

              <form.Subscribe
                selector={(state) => ({
                  canSubmit: state.canSubmit,
                  isSubmitting: state.isSubmitting,
                })}
              >
                {({ canSubmit, isSubmitting }) => (
                  <Button
                    type="submit"
                    disabled={
                      !canSubmit ||
                      saveConfigMutation.isPending ||
                      deleteConfigMutation.isPending
                    }
                  >
                    {saveConfigMutation.isPending || isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {isActiveProviderConfig ? "Updating..." : "Saving..."}
                      </>
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        {isActiveProviderConfig
                          ? "Update Configuration"
                          : "Save Configuration"}
                      </>
                    )}
                  </Button>
                )}
              </form.Subscribe>

              {isActiveProviderConfig && (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      type="button"
                      variant="outline"
                      className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                      disabled={
                        saveConfigMutation.isPending ||
                        deleteConfigMutation.isPending
                      }
                    >
                      {deleteConfigMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete Configuration
                        </>
                      )}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        Delete model configuration?
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently delete the active model provider
                        configuration and stored model credentials.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel
                        disabled={deleteConfigMutation.isPending}
                      >
                        Cancel
                      </AlertDialogCancel>
                      <AlertDialogAction
                        onClick={handleDeleteConfiguration}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        disabled={deleteConfigMutation.isPending}
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
