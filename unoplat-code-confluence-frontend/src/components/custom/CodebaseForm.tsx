"use client";

import { z } from "zod";
import { InfoIcon } from "lucide-react";
import React from "react";

import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Extend the Zod schema to include nested structures if needed
export const CodebaseSchema = z.object({
  codebase_folder: z.string().min(1, "Codebase folder is required"),
  root_package: z.string().min(1, "Root package is required"),
  programming_language_metadata: z.object({
    language: z.string().min(1, "Language is required"),
    package_manager: z.string().min(1, "Package manager is required"),
  })
});

// TypeScript type inference from the Zod schema
export type Codebase = z.infer<typeof CodebaseSchema>;

// Type for repository config form data
export interface RepositoryConfig {
  repositoryName: string;
  codebases: Codebase[];
}

// Define a type for TanStack Form field state
interface FieldState<T = string> {
  state: { 
    value: T; 
    meta: { errors: string[] } 
  }; 
  handleBlur: () => void;
  handleChange: (value: T) => void;
}

export interface CodebaseFormProps {
  index: number;
  // Use an `any` type for the form to avoid complex generic types
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parentForm: any;
  disabled?: boolean;
}

export function CodebaseForm({
  index,
  parentForm,
  disabled = false,
}: CodebaseFormProps): React.ReactElement {
  // Helper to create field name with proper type
  const getFieldName = <K extends keyof Codebase>(fieldName: K): string => 
    `codebases[${index}].${fieldName}`;

  // Function to render a field with common components
  const renderField = (
    field: FieldState,
    label: string,
    tooltip: string,
    id: string,
    children: React.ReactNode
  ) => (
    <div className="grid gap-2">
      <div className="flex items-center gap-2">
        <label htmlFor={id} className="text-sm font-medium">
          {label}
        </label>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="inline-flex">
                <InfoIcon className="h-4 w-4 text-muted-foreground cursor-pointer" />
              </span>
            </TooltipTrigger>
            <TooltipContent side="right" align="start" className="max-w-[260px] text-sm">
              <p>{tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {children}

      {field.state.meta.errors && field.state.meta.errors.length > 0 && (
        <p className="text-sm text-destructive">{field.state.meta.errors.join(", ")}</p>
      )}
    </div>
  );

  return (
    <div className="space-y-4 p-4 border rounded-md relative">
      {/* Delete button is currently disabled and hidden as per requirements */}
      {/*
      {onRemove && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2"
          onClick={onRemove}
          type="button"
        >
          <TrashIcon className="h-4 w-4 text-destructive" />
        </Button>
      )}
      */}

      <parentForm.Field
        name={getFieldName("codebase_folder")}
        validators={{
          onChange: ({ value }: { value: string }) => !value ? "Codebase folder is required" : undefined
        }}
      >
        {(field: FieldState) => renderField(
          field,
          "Codebase Folder",
          "The relative path to the codebase folder within the repository",
          `codebase_folder_${index}`,
          <Input
            id={`codebase_folder_${index}`}
            placeholder="e.g., unoplat-code-confluence-ingestion/code-confluence-flow-bridge"
            value={field.state.value}
            onBlur={field.handleBlur}
            onChange={(e) => field.handleChange(e.target.value)}
            className={field.state.meta.errors.length > 0 ? "border-destructive" : ""}
            disabled={disabled}
            readOnly={disabled}
          />
        )}
      </parentForm.Field>

      <parentForm.Field
        name={getFieldName("root_package")}
        validators={{
          onChange: ({ value }: { value: string }) => !value ? "Root package is required" : undefined
        }}
      >
        {(field: FieldState) => renderField(
          field,
          "Root Package",
          "The path to the root package within the codebase folder",
          `root_package_${index}`,
          <Input
            id={`root_package_${index}`}
            placeholder="e.g., src/code_confluence_flow_bridge"
            value={field.state.value}
            onBlur={field.handleBlur}
            onChange={(e) => field.handleChange(e.target.value)}
            className={field.state.meta.errors.length > 0 ? "border-destructive" : ""}
            disabled={disabled}
            readOnly={disabled}
          />
        )}
      </parentForm.Field>

      <parentForm.Field
        name={getFieldName('programming_language_metadata') + '.language'}
        validators={{
          onChange: ({ value }: { value: string }) => !value ? "Language is required" : undefined
        }}
      >
        {(field: FieldState) => renderField(
          field,
          "Language",
          "The programming language used in the codebase",
          `language_${index}`,
          <Select
            value={field.state.value}
            onValueChange={(value) => field.handleChange(value)}
            disabled={disabled}
          >
            <SelectTrigger 
              id={`language_${index}`} 
              className={field.state.meta.errors.length > 0 ? "border-destructive" : ""}
              disabled={disabled}
            >
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="python">Python</SelectItem>
            </SelectContent>
          </Select>
        )}
      </parentForm.Field>

      <parentForm.Field
        name={getFieldName('programming_language_metadata') + '.package_manager'}
        validators={{
          onChange: ({ value }: { value: string }) => !value ? "Package manager is required" : undefined
        }}
      >
        {(field: FieldState) => renderField(
          field,
          "Package Manager",
          "The package manager used for managing dependencies",
          `package_manager_${index}`,
          <Select
            value={field.state.value}
            onValueChange={(value) => field.handleChange(value)}
            disabled={disabled}
          >
            <SelectTrigger 
              id={`package_manager_${index}`} 
              className={field.state.meta.errors.length > 0 ? "border-destructive" : ""}
              disabled={disabled}
            >
              <SelectValue placeholder="Select package manager" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="uv">uv</SelectItem>
              <SelectItem value="pip">pip</SelectItem>
              <SelectItem value="poetry">poetry</SelectItem>
            </SelectContent>
          </Select>
        )}
      </parentForm.Field>
    </div>
  );
} 