import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import type { ModelProviderDefinition } from '../types';

interface ProviderSelectorProps {
  providers: ModelProviderDefinition[];
  selectedProvider?: string;
  onProviderChange: (providerKey: string) => void;
  isLoading?: boolean;
  error?: string | null;
  label?: string;
  placeholder?: string;
  className?: string;
}

/**
 * Select dropdown component for choosing a model provider
 * Displays providers using their configured display names
 */
export function ProviderSelector({
  providers,
  selectedProvider,
  onProviderChange,
  isLoading = false,
  error = null,
  label = 'Provider',
  placeholder = 'Select a provider...',
  className
}: ProviderSelectorProps): React.ReactElement {
  const handleValueChange = (value: string) => {
    onProviderChange(value);
  };

  const selectedProviderData = providers.find(
    (provider) => provider.provider_key === selectedProvider
  );

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <Label htmlFor="provider-select" className="text-sm font-medium">
          {label}
        </Label>
      )}

      <Select
        value={selectedProvider || ''}
        onValueChange={handleValueChange}
        disabled={isLoading || !!error}
      >
        <SelectTrigger id="provider-select" className="w-full">
          {isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Loading providers...</span>
            </div>
          ) : (
            <SelectValue placeholder={placeholder}>
              {selectedProviderData?.display_name}
            </SelectValue>
          )}
        </SelectTrigger>

        <SelectContent>
          {providers.map((provider) => (
            <SelectItem
              key={provider.provider_key}
              value={provider.provider_key || ''}
            >
              <span className="font-medium">{provider.display_name}</span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {selectedProviderData?.model_field?.help && (
        <p className="text-xs text-muted-foreground">
          {selectedProviderData.model_field.help}
        </p>
      )}
    </div>
  );
}
