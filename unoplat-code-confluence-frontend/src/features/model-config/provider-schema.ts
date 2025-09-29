import { z } from 'zod';

// Avoid importing types only used for explicit type annotations
// Rely on Zod's type inference instead - official Zod v3.24.2 pattern

// 1. Define primitive schema without explicit type annotation
// Using z.union for better type inference than ZodType<Interface>
const providerFieldPrimitiveSchema = z.union([
  z.string(),
  z.number(),
  z.boolean(),
]);

// 2. Base field schema with proper null/undefined handling
const baseFieldSchema = z
  .object({
    label: z.string().min(1, 'Field label is required'),
    // Use .nullable() for explicit null values
    placeholder: z.string().nullable(),
    // Use .nullish() for fields that can be null OR undefined
    help: z.string().nullish(),
    required: z.boolean().default(false),
  })
  .passthrough();

export const providerModelFieldSchema = baseFieldSchema;

// 3. Provider config field schema using .extend() on actual schema (not ZodType)
export const providerConfigFieldSchema = baseFieldSchema
  .extend({
    key: z.string().min(1, 'Field key is required'),
    type: z.string().min(1, 'Field type is required'),
    default: providerFieldPrimitiveSchema.nullable().default(null),
    enum: z.array(z.string().min(1)).nullable().default(null),
  })
  .superRefine((field, ctx) => {
    // 4. Proper typing for superRefine - field is inferred, ctx is RefinementCtx
    if (field.type === 'select' && (!field.enum || field.enum.length === 0)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Select fields must provide at least one option.',
        path: ['enum'],
      });
    }
  });

// 5. Model provider schema using inferred types
// Note: provider_key is optional here because the backend returns it as the record key
// We'll backfill it when transforming the response
export const modelProviderSchema = z
  .object({
    provider_key: z.string().min(1, 'Provider key is required').optional(),
    display_name: z.string().min(1, 'Display name is required'),
    kind: z.string().min(1, 'Provider kind is required'),
    model_field: providerModelFieldSchema,
    fields: z.array(providerConfigFieldSchema).default([]),
  })
  .passthrough();

// 6. Catalog schemas using Zod inference
export const providerCatalogSchema = z.record(modelProviderSchema);
export const providerCatalogArraySchema = z.array(modelProviderSchema);

// 7. Export inferred types - this is the recommended Zod v3.24.2 pattern
export type ProviderFieldPrimitive = z.infer<typeof providerFieldPrimitiveSchema>;
export type BaseFieldDefinition = z.infer<typeof baseFieldSchema>;
export type ProviderConfigFieldDefinition = z.infer<typeof providerConfigFieldSchema>;
export type ModelProviderDefinition = z.infer<typeof modelProviderSchema>;
export type ProviderCatalogRecord = z.infer<typeof providerCatalogSchema>;
export type ProviderCatalogInput = z.infer<typeof providerCatalogSchema>;
export type ModelProviderSchemaInput = z.infer<typeof modelProviderSchema>;
