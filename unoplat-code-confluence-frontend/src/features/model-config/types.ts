// Re-export the Zod-inferred types to maintain compatibility
// This follows the Zod v3.24.2 best practice of using schema inference as the source of truth
export type {
  ProviderFieldPrimitive,
  BaseFieldDefinition,
  ProviderConfigFieldDefinition,
  ModelProviderDefinition,
  ProviderCatalogRecord,
} from "./provider-schema";

// Import for use in additional types
import type {
  ModelProviderDefinition,
  ProviderFieldPrimitive,
} from "./provider-schema";

// Additional utility types for the UI layer
export type ModelProviderKind = "native" | "openai_compat" | (string & {});

export type ProviderFieldType =
  | "text"
  | "password"
  | "select"
  | "url"
  | "textarea"
  | "number"
  | "boolean"
  | (string & {});

export type ModelProviderDefinitions = readonly ModelProviderDefinition[];

export type ProviderFieldValue = ProviderFieldPrimitive | null;

export type ProviderFieldValuesMap = Record<string, ProviderFieldValue>;

export interface ProviderFormValues {
  readonly model: string;
  readonly fields: ProviderFieldValuesMap;
}

export type ProviderFormValueRecord = Record<string, ProviderFormValues>;
