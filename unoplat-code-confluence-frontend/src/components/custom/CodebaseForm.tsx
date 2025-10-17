"use client";

import { z } from "zod";
import { InfoIcon, TrashIcon } from "lucide-react";
import React from "react";
import { useStore } from '@tanstack/react-store';

import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { LANGUAGE_PACKAGE_MANAGERS } from "../../types";

// Extend the Zod schema to include nested structures if needed
export const CodebaseSchema = z.object({
  codebase_folder: z.string().min(1, "Codebase folder is required"),
  root_packages: z.array(z.string().min(1, "Root package path cannot be empty")).nullable().optional(),
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
  onRemove?: () => void;
}

export function CodebaseForm({
  index,
  parentForm,
  disabled = false,
  onRemove,
}: CodebaseFormProps): React.ReactElement {
  
  // Subscribe to form store for reactive data
  const codebaseFolder: string = useStore(
    parentForm.store,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (state: any) => state.values?.codebases?.[index]?.codebase_folder ?? "",
  );

  // Direct access to store state for arrays (not using useStore to avoid rendering issues)
  const getRootPackages = (): string[] => {
    const state = parentForm.store.state;
    return state.values?.codebases?.[index]?.root_packages ?? [];
  };

  const isRootRepo: boolean = codebaseFolder === ".";
  const isRootRepoLocked: boolean = isRootRepo;

  // Debug logs to examine reactive values
  console.debug('[CodebaseForm]', { index, codebaseFolder, rootPackages: getRootPackages() });

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

  // Handle root repository checkbox change
  function handleRootRepoChange(checked: boolean, field: FieldState): void {
    if (checked) {
      field.handleChange(".");
    } else {
      field.handleChange("");
    }
  }

  // Helper functions for managing root packages array
  const addRootPackage = () => {
    const currentPackages = getRootPackages();
    const newPackages = [...currentPackages, ""];
    parentForm.setFieldValue(getFieldName("root_packages"), newPackages);
  };

  const removeRootPackage = (indexToRemove: number) => {
    const currentPackages = getRootPackages();
    const newPackages = currentPackages.filter((_, i) => i !== indexToRemove);
    parentForm.setFieldValue(
      getFieldName("root_packages"),
      newPackages.length > 0 ? newPackages : null
    );
  };

  const updateRootPackage = (packageIndex: number, value: string) => {
    const currentPackages = getRootPackages();
    const newPackages = [...currentPackages];
    newPackages[packageIndex] = value;
    parentForm.setFieldValue(getFieldName("root_packages"), newPackages);
  };

  return (
    <div className="space-y-4 p-4 border rounded-md relative">
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

      <parentForm.Field
        name={getFieldName("codebase_folder")}
        validators={{
          onChange: ({ value }: { value: string }) => !value ? "Codebase folder is required" : undefined
        }}
      >
        {(field: FieldState) => (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox 
                id={`is_root_repo_${index}`}
                checked={isRootRepo}
                onCheckedChange={(checked) => handleRootRepoChange(checked as boolean, field)}
                disabled={disabled || isRootRepoLocked}
              />
              <Label 
                htmlFor={`is_root_repo_${index}`}
                className="cursor-pointer text-sm font-medium"
              >
                No subdirectory: Codebase lives in the repository root.
              </Label>
            </div>
            
            {!isRootRepo && !isRootRepoLocked && renderField(
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
            
            {isRootRepo && (
              <div className="text-sm text-muted-foreground italic">
                Using repository root as codebase folder (".")
              </div>
            )}
          </div>
        )}
      </parentForm.Field>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Root Packages</label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="inline-flex">
                    <InfoIcon className="h-4 w-4 text-muted-foreground cursor-pointer" />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="right" align="start" className="max-w-[260px] text-sm">
                  <p>The paths to root packages within the codebase folder. Leave empty for non-monorepo projects.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          {!disabled && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addRootPackage}
            >
              Add Root Package
            </Button>
          )}
        </div>
        
        {getRootPackages().length === 0 ? (
          <div className="text-sm text-muted-foreground italic">
            No root packages specified. For non-monorepo projects, this is normal.
          </div>
        ) : (
          <div className="space-y-2">
            {getRootPackages().map((pkg, pkgIndex) => (
              <div key={pkgIndex} className="flex items-center gap-2">
                <Input
                  placeholder="e.g., src/code_confluence_flow_bridge"
                  value={pkg}
                  onChange={(e) => updateRootPackage(pkgIndex, e.target.value)}
                  disabled={disabled}
                  readOnly={disabled}
                />
                {!disabled && getRootPackages().length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeRootPackage(pkgIndex)}
                  >
                    <TrashIcon className="h-4 w-4 text-destructive" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

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
            onValueChange={(value) => {
              field.handleChange(value);
              const packageFieldName = `${getFieldName('programming_language_metadata')}.package_manager`;
              const availableManagers = LANGUAGE_PACKAGE_MANAGERS[value] ?? [];
              const currentManager = parentForm.store.state.values?.codebases?.[index]?.programming_language_metadata?.package_manager;

              if (!currentManager || !availableManagers.includes(currentManager)) {
                parentForm.setFieldValue(
                  packageFieldName,
                  availableManagers[0] ?? ""
                );
              }
            }}
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
              {Object.keys(LANGUAGE_PACKAGE_MANAGERS).map((langKey) => {
                const label = langKey.charAt(0).toUpperCase() + langKey.slice(1);
                return (
                  <SelectItem key={langKey} value={langKey}>
                    {label}
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        )}
      </parentForm.Field>

      <parentForm.Field
        name={getFieldName('programming_language_metadata') + '.package_manager'}
        validators={{
          onChange: ({ value }: { value: string }) => (!value ? "Package manager is required" : undefined),
        }}
      >
        {(field: FieldState) => {
          return renderField(
            field,
            'Package Manager',
            'The package manager used for managing dependencies',
            `package_manager_${index}`,
            <Select
              value={field.state.value}
              onValueChange={(value) => {
                field.handleChange(value);
              }}
              disabled={disabled}
            >
              <SelectTrigger
                id={`package_manager_${index}`}
                className={field.state.meta.errors.length > 0 ? 'border-destructive' : ''}
                disabled={disabled}
              >
                <SelectValue placeholder="Select package manager" />
              </SelectTrigger>
              <SelectContent>
                {(() => {
                  const state = parentForm.store.state;
                  const lang = state.values?.codebases?.[index]?.programming_language_metadata?.language;
                  
                  return lang && LANGUAGE_PACKAGE_MANAGERS[lang]
                    ? LANGUAGE_PACKAGE_MANAGERS[lang].map((pm) => (
                        <SelectItem key={pm} value={pm}>{pm}</SelectItem>
                      ))
                    : null;
                })()}
              </SelectContent>
            </Select>,
          );
        }}
      </parentForm.Field>
    </div>
  );
} 