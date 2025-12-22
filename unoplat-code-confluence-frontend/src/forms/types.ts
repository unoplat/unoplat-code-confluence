import type { AnyFieldApi } from "@tanstack/react-form";

/**
 * Common base props for pre-bound field components
 */
export interface BaseFieldProps {
  /** Optional label to display above the field */
  label?: string;
  /** Optional description text below the label */
  description?: string;
  /** Additional className for the field container */
  className?: string;
}

/**
 * Type alias for TanStack Form field errors array
 *
 * TanStack Form returns errors as an array of mixed types (string, object, etc.).
 * Uses the official AnyFieldApi alias to avoid enumerating all FieldApi generics.
 * @see https://github.com/tanstack/form/blob/v1.11.0/docs/reference/type-aliases/anyfieldapi.md
 */
export type FieldErrors = AnyFieldApi["state"]["meta"]["errors"];

/**
 * Type alias for a single field error element
 */
export type FieldError = FieldErrors[number];
