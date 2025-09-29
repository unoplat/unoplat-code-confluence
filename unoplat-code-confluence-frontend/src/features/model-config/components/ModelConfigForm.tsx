import React from 'react';
import { useForm } from '@tanstack/react-form';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Loader2, Save, X } from 'lucide-react';
import { ConfigField } from './ConfigField';
import { generateProviderConfigSchema, getProviderConfigDefaults } from '../schema-generator';
import { useSaveProviderConfig } from '@/hooks/useSaveModelConfig';
import type { ModelProviderDefinition } from '../types';
import type { ModelConfigResponse } from '@/lib/api';
import { MODEL_NAME_FIELD } from '../constants';

interface ModelConfigFormProps {
  provider: ModelProviderDefinition;
  existingConfig?: ModelConfigResponse | null;
  onCancel: () => void;
  onSuccess?: () => void;
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
  className
}: ModelConfigFormProps): React.ReactElement {
  const saveConfigMutation = useSaveProviderConfig(provider.provider_key!);

  // Generate schema and defaults for this provider
  const schema = React.useMemo(() => generateProviderConfigSchema(provider), [provider]);

  // Merge existing config with defaults
  const defaultValues = React.useMemo(() => {
    const defaults = getProviderConfigDefaults(provider);

    // If we have existing config for this provider, merge it with defaults
    if (existingConfig && existingConfig.provider_key === provider.provider_key) {
      return {
        ...defaults,
        [MODEL_NAME_FIELD]: existingConfig.model_name || defaults[MODEL_NAME_FIELD],
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
        'You have unsaved changes. Are you sure you want to discard them?'
      );
      if (!confirmDiscard) return;
    }
    onCancel();
  };

  return (
    <div className={className}>
      <div className="mb-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">
              {existingConfig ? 'Update' : 'Configure'} {provider.display_name}
            </h3>
            <p className="text-sm text-muted-foreground">
              {existingConfig
                ? `Update your ${provider.display_name} provider configuration`
                : `Set up your ${provider.display_name} provider configuration`}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCancel}
            disabled={saveConfigMutation.isPending}
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
                    const result = schema.shape[MODEL_NAME_FIELD].safeParse(value);
                    return result.success ? undefined : result.error.errors[0]?.message;
                  },
                }}
              >
                {(field) => (
                  <ConfigField
                    field={{
                      key: MODEL_NAME_FIELD,
                      type: 'text',
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
                    error={field.state.meta.errors?.[0] ? String(field.state.meta.errors[0]) : undefined}
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
                          const result = schema.shape[fieldDef.key].safeParse(value);
                          return result.success ? undefined : result.error.errors[0]?.message;
                        },
                      }}
                    >
                      {(field) => (
                        <ConfigField
                          field={fieldDef}
                          value={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          error={field.state.meta.errors?.[0] ? String(field.state.meta.errors[0]) : undefined}
                        />
                      )}
                    </form.Field>
                  ))}
                </div>
              </div>
            </>
          )}

          <Separator />

          {/* Form Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
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
                disabled={saveConfigMutation.isPending}
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
                    disabled={!canSubmit || saveConfigMutation.isPending}
                  >
                    {saveConfigMutation.isPending || isSubmitting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        {existingConfig ? 'Updating...' : 'Saving...'}
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        {existingConfig ? 'Update Configuration' : 'Save Configuration'}
                      </>
                    )}
                  </Button>
                )}
              </form.Subscribe>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
