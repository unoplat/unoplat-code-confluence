import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';
import { ProviderSelector } from './ProviderSelector';
import { ModelConfigForm } from './ModelConfigForm';
import { useModelProviders } from '@/hooks/useModelProviders';
import { useModelConfig } from '@/hooks/useModelConfig';
import type { ModelProviderDefinition } from '../types';

/**
 * Main container component for model provider configuration
 * Handles provider selection, configuration forms, and state management
 */
export function ModelConfigurationSection(): React.ReactElement {
  const [selectedProviderKey, setSelectedProviderKey] = React.useState<string | undefined>();

  const {
    data: providers = [],
    isLoading,
    error,
    refetch
  } = useModelProviders();

  const { data: existingConfig } = useModelConfig();

  // Auto-select provider when existing config loads
  React.useEffect(() => {
    if (existingConfig?.provider_key && !selectedProviderKey && providers.length > 0) {
      setSelectedProviderKey(existingConfig.provider_key);
    }
  }, [existingConfig, selectedProviderKey, providers]);

  const errorMessage = error
    ? error instanceof Error
      ? error.message
      : 'Unexpected error occurred while loading providers.'
    : null;

  const selectedProvider = React.useMemo<ModelProviderDefinition | undefined>(() => {
    return providers.find((provider) => provider.provider_key === selectedProviderKey);
  }, [providers, selectedProviderKey]);

  const handleProviderChange = (providerKey: string) => {
    setSelectedProviderKey(providerKey || undefined);
  };

  const handleFormCancel = () => {
    setSelectedProviderKey(undefined);
  };

  const handleFormSuccess = () => {
    refetch(); // Refresh providers list to update configuration status
  };

  const handleRetry = () => {
    refetch();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6">
        <Card className="shadow-md border-border bg-card">
          <CardHeader className="max-w-4xl mx-auto px-8 py-6">
            <div className="flex items-center justify-between space-x-6">
              <div className="space-y-2">
                <CardTitle className="text-xl font-semibold tracking-tight">Model Provider Configuration</CardTitle>
                <CardDescription className="text-base text-muted-foreground leading-relaxed">
                  Configure AI model providers for code intelligence features and set up API credentials.
                </CardDescription>
              </div>
              <div className="min-w-[240px]">
                {/* Error State */}
                {errorMessage ? (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="flex items-center justify-between">
                      <span className="text-xs">Failed to load providers</span>
                      <Button variant="outline" size="sm" onClick={handleRetry}>
                        Retry
                      </Button>
                    </AlertDescription>
                  </Alert>
                ) : providers.length > 0 ? (
                  <ProviderSelector
                    providers={providers}
                    selectedProvider={selectedProviderKey}
                    onProviderChange={handleProviderChange}
                    isLoading={isLoading}
                    error={errorMessage}
                    label="Provider"
                    placeholder="Select a provider"
                  />
                ) : (
                  !isLoading && (
                    <div className="flex flex-col items-center gap-2 rounded-md border border-dashed border-muted p-4 text-xs text-muted-foreground">
                      <AlertCircle className="h-4 w-4" />
                      <span>No providers available</span>
                      <Button variant="outline" size="sm" onClick={handleRetry}>
                        Refresh
                      </Button>
                    </div>
                  )
                )}

                {isLoading && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <div className="h-3 w-3 animate-spin rounded-full border-2 border-muted border-t-transparent" />
                    Loading providers...
                  </div>
                )}
              </div>
            </div>
          </CardHeader>

          {selectedProvider && (
            <CardContent className="px-8 pt-0 pb-6 max-w-4xl mx-auto">
              <ModelConfigForm
                key={selectedProvider.provider_key}
                provider={selectedProvider}
                existingConfig={existingConfig}
                onCancel={handleFormCancel}
                onSuccess={handleFormSuccess}
                className="border-0 shadow-none bg-transparent p-0"
              />
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
}
