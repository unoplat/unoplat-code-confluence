/**
 * Centralized Form Infrastructure
 *
 * This module provides TanStack Form integration with:
 * - Context-based field access via useFieldContext/useFormContext
 * - Pre-bound field components accessible via form.AppField
 * - Utility functions for error handling
 *
 * @example Basic usage with useAppForm
 * ```tsx
 * import { useAppForm } from '@/forms'
 *
 * function MyForm() {
 *   const form = useAppForm({
 *     defaultValues: { rating: undefined, comments: '' },
 *     validators: { onChange: mySchema },
 *   })
 *
 *   return (
 *     <form onSubmit={(e) => { e.preventDefault(); form.handleSubmit() }}>
 *       <form.AppField
 *         name="rating"
 *         children={(field) => <field.EmojiRatingField />}
 *       />
 *       <form.AppField
 *         name="comments"
 *         children={(field) => <field.TextareaField placeholder="..." />}
 *       />
 *     </form>
 *   )
 * }
 * ```
 *
 * @example Using useFieldContext in nested components
 * ```tsx
 * import { useFieldContext } from '@/forms'
 *
 * function NestedComponent() {
 *   // Access field state without prop drilling
 *   const field = useFieldContext<string[]>()
 *   return <div>{field.state.value.length} items selected</div>
 * }
 * ```
 */

// Contexts and hooks
export {
  fieldContext,
  formContext,
  useFieldContext,
  useFormContext,
} from "./form-context";

// Form hook factory
export { useAppForm, withForm } from "./form-hook";

// Pre-bound field components (also accessible via form.AppField)
export {
  CategoryChipsField,
  EmojiRatingField,
  MiniEmojiField,
  TextareaField,
} from "./fields";

// Types and utilities
export type { BaseFieldProps, FieldErrors } from "./types";
export { getFieldErrorMessages } from "./utils";
