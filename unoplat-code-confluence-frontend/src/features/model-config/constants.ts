/**
 * Constants for model configuration feature
 * Standardizes field names and keys across components
 */

export const MODEL_NAME_FIELD = 'model_name';

export const PROVIDER_KEY_FIELD = 'provider_key';

export const FIELD_TYPES = {
  TEXT: 'text',
  PASSWORD: 'password',
  URL: 'url',
  SELECT: 'select',
  TEXTAREA: 'textarea',
  NUMBER: 'number',
  BOOLEAN: 'boolean',
} as const;

export type FieldType = typeof FIELD_TYPES[keyof typeof FIELD_TYPES];