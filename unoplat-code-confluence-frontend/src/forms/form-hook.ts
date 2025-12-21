import { createFormHook } from "@tanstack/react-form";

import {
  CategoryChipsField,
  EmojiRatingField,
  MiniEmojiField,
  TextareaField,
} from "./fields";
import { fieldContext, formContext } from "./form-context";

/**
 * Application-wide form hook factory created via TanStack Form's createFormHook
 *
 * This provides:
 * - `useAppForm`: Drop-in replacement for `useForm` that automatically provides contexts
 * - `withForm`: HOC wrapper for form components (alternative pattern)
 *
 * Pre-registered field components:
 * - `EmojiRatingField` - Large emoji rating selector for overall ratings
 * - `MiniEmojiField` - Compact emoji selector for per-item ratings
 * - `CategoryChipsField` - Multi-select chip toggles for categories
 * - `TextareaField` - Textarea with character counter and error display
 *
 * @example
 * ```tsx
 * const form = useAppForm({
 *   defaultValues: { rating: undefined, comments: '' },
 *   validators: { onChange: mySchema },
 * })
 *
 * return (
 *   <form.AppField
 *     name="rating"
 *     children={(field) => <field.EmojiRatingField />}
 *   />
 * )
 * ```
 *
 * @see https://tanstack.com/form/latest/docs/framework/react/guides/form-composition
 */
export const { useAppForm, withForm } = createFormHook({
  fieldContext,
  formContext,
  fieldComponents: {
    CategoryChipsField,
    EmojiRatingField,
    MiniEmojiField,
    TextareaField,
  },
  formComponents: {},
});
