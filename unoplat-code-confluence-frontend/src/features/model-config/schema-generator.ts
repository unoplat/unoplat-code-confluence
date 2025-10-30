import { z } from "zod";
import type {
  ModelProviderDefinition,
  ProviderConfigFieldDefinition,
} from "./types";
import { MODEL_NAME_FIELD, FIELD_TYPES } from "./constants";

/**
 * Creates a base Zod schema for a field type, handling TanStack Form's string inputs
 * Uses z.coerce for numbers to handle HTML form string inputs properly
 *
 * @param fieldType - The type of field
 * @param enumOptions - For select fields, the available options
 * @returns Base Zod schema for the field type
 */
const getBaseSchema = (
  fieldType: string,
  enumOptions?: string[] | null,
): z.ZodTypeAny => {
  switch (fieldType) {
    case FIELD_TYPES.NUMBER:
      // Use coerce to handle string inputs from HTML forms
      return z.coerce.number();

    case FIELD_TYPES.BOOLEAN:
      return z.boolean();

    case FIELD_TYPES.URL:
      return z.string().url("Please enter a valid URL");

    case FIELD_TYPES.SELECT:
      if (enumOptions && enumOptions.length > 0) {
        return z.enum(enumOptions as [string, ...string[]]);
      }
      return z.string();

    case FIELD_TYPES.TEXT:
    case FIELD_TYPES.PASSWORD:
    case FIELD_TYPES.TEXTAREA:
    default:
      return z.string();
  }
};

/**
 * Creates a Zod schema for an individual field based on its configuration
 * Properly handles required/optional fields and defaults
 *
 * @param field - The field definition from provider metadata
 * @returns Complete Zod schema for the field
 */
const isStringSchema = (schema: z.ZodTypeAny): schema is z.ZodString =>
  schema instanceof z.ZodString;

const createFieldSchema = (
  field: ProviderConfigFieldDefinition,
): z.ZodTypeAny => {
  // Start with base schema for the field type
  let schema = getBaseSchema(field.type, field.enum);

  // Handle required vs optional fields
  if (field.required) {
    // Apply minimum validations for required fields
    if (
      isStringSchema(schema) &&
      (field.type === FIELD_TYPES.TEXT ||
        field.type === FIELD_TYPES.PASSWORD ||
        field.type === FIELD_TYPES.URL ||
        field.type === FIELD_TYPES.TEXTAREA)
    ) {
      schema = schema.min(1, `${field.label} is required`);
    } else if (field.type === FIELD_TYPES.NUMBER) {
      // For numbers, we just ensure it's not NaN after coercion
      schema = (schema as z.ZodNumber).refine((val) => !isNaN(val), {
        message: `${field.label} must be a valid number`,
      });
    }
    // Boolean and select fields are inherently valid when required
  } else {
    // Make field optional first
    schema = schema.optional();

    // Only apply default after making optional
    if (field.default !== null && field.default !== undefined) {
      schema = schema.default(field.default);
    }
  }

  return schema;
};

/**
 * Generates a dynamic Zod schema based on provider field definitions
 * Handles the model field and all provider-specific configuration fields
 *
 * @param provider - The provider definition containing field metadata
 * @returns Complete Zod schema for validating provider configuration
 */
export const generateProviderConfigSchema = (
  provider: ModelProviderDefinition,
) => {
  const schemaFields: Record<string, z.ZodTypeAny> = {};

  // Add model field validation (model_field is BaseFieldDefinition, no default property)
  if (provider.model_field) {
    const modelField = provider.model_field;
    const baseModelSchema = z.string();
    const modelSchema = modelField.required
      ? baseModelSchema.min(1, `${modelField.label} is required`)
      : baseModelSchema.optional();

    schemaFields[MODEL_NAME_FIELD] = modelSchema;
  }

  // Add provider-specific field validations
  provider.fields.forEach((field) => {
    schemaFields[field.key] = createFieldSchema(field);
  });

  return z.object(schemaFields);
};

/**
 * Gets the default values for a provider configuration form
 * Only uses defaults from ProviderConfigFieldDefinition, not BaseFieldDefinition
 *
 * @param provider - The provider definition
 * @returns Object with default values for form initialization
 */
export const getProviderConfigDefaults = (
  provider: ModelProviderDefinition,
): Record<string, unknown> => {
  const defaults: Record<string, unknown> = {};

  // Set model field default (BaseFieldDefinition doesn't have default, use empty string)
  if (provider.model_field?.required) {
    defaults[MODEL_NAME_FIELD] = "";
  }

  // Set provider field defaults (ProviderConfigFieldDefinition has default property)
  provider.fields.forEach((field) => {
    if (field.default !== null && field.default !== undefined) {
      defaults[field.key] = field.default;
    } else if (field.required) {
      // Set appropriate empty defaults for required fields based on type
      switch (field.type) {
        case FIELD_TYPES.BOOLEAN:
          defaults[field.key] = false;
          break;
        case FIELD_TYPES.NUMBER:
          defaults[field.key] = ""; // Empty string, will be coerced to number
          break;
        default:
          defaults[field.key] = "";
          break;
      }
    }
  });

  return defaults;
};

/**
 * Type helper to infer the schema type from a provider definition
 * Provides TypeScript type safety for form values
 */
export type ProviderConfigInput = z.infer<
  ReturnType<typeof generateProviderConfigSchema>
>;
