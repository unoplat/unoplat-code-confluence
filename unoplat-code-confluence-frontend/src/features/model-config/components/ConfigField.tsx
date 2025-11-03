import React from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import type { ProviderConfigFieldDefinition } from "../types";
import { FIELD_TYPES } from "../constants";

interface ConfigFieldProps {
  field: ProviderConfigFieldDefinition;
  value: unknown;
  onChange: (value: unknown) => void;
  onBlur?: () => void;
  error?: string;
  className?: string;
}

/**
 * Dynamic field renderer component that renders different input types
 * based on the field definition metadata
 */
export function ConfigField({
  field,
  value,
  onChange,
  onBlur,
  error,
  className,
}: ConfigFieldProps): React.ReactElement {
  const fieldId = `field-${field.key}`;

  const handleInputChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    onChange(event.target.value);
  };

  const handleSelectChange = (newValue: string) => {
    onChange(newValue);
  };

  const handleCheckboxChange = (checked: boolean) => {
    onChange(checked);
  };

  const renderField = () => {
    const commonProps = {
      id: fieldId,
      onBlur,
      "aria-describedby": error
        ? `${fieldId}-error`
        : field.help
          ? `${fieldId}-help`
          : undefined,
      "aria-invalid": !!error,
    };

    switch (field.type) {
      case FIELD_TYPES.PASSWORD:
        return (
          <Input
            {...commonProps}
            type="password"
            value={String(value || "")}
            onChange={handleInputChange}
            placeholder={field.placeholder || undefined}
          />
        );

      case FIELD_TYPES.URL:
        return (
          <Input
            {...commonProps}
            type="url"
            value={String(value || "")}
            onChange={handleInputChange}
            placeholder={field.placeholder || "https://..."}
          />
        );

      case FIELD_TYPES.NUMBER:
        return (
          <Input
            {...commonProps}
            type="number"
            value={String(value || "")}
            onChange={handleInputChange}
            placeholder={field.placeholder || "0"}
          />
        );

      case FIELD_TYPES.TEXTAREA:
        return (
          <Textarea
            {...commonProps}
            value={String(value || "")}
            onChange={handleInputChange}
            placeholder={field.placeholder || undefined}
            rows={4}
          />
        );

      case FIELD_TYPES.SELECT:
        return (
          <Select
            value={String(value || "")}
            onValueChange={handleSelectChange}
          >
            <SelectTrigger {...commonProps}>
              <SelectValue
                placeholder={field.placeholder || "Select an option..."}
              />
            </SelectTrigger>
            <SelectContent>
              {field.enum?.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case FIELD_TYPES.BOOLEAN:
        return (
          <div className="flex items-center space-x-2">
            <Checkbox
              {...commonProps}
              checked={Boolean(value)}
              onCheckedChange={handleCheckboxChange}
            />
            <Label htmlFor={fieldId} className="text-sm font-normal">
              {field.placeholder || "Enable this option"}
            </Label>
          </div>
        );

      case FIELD_TYPES.TEXT:
      default:
        return (
          <Input
            {...commonProps}
            type="text"
            value={String(value || "")}
            onChange={handleInputChange}
            placeholder={field.placeholder || undefined}
          />
        );
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label - skip for boolean fields as they have inline labels */}
      {field.type !== FIELD_TYPES.BOOLEAN && (
        <Label htmlFor={fieldId} className="text-sm font-medium">
          {field.label}
          {field.required && <span className="ml-1 text-red-500">*</span>}
        </Label>
      )}

      {/* Field input */}
      {renderField()}

      {/* Help text */}
      {field.help && (
        <p id={`${fieldId}-help`} className="text-muted-foreground text-xs">
          {field.help}
        </p>
      )}

      {/* Error message */}
      {error && (
        <p id={`${fieldId}-error`} className="text-xs text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
