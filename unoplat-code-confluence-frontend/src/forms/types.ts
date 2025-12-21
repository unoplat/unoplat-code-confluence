import type { FieldApi } from "@tanstack/react-form";

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
 * TanStack Form returns errors as an array of unknown types.
 * This type captures the shape for use in error extraction utilities.
 */
export type FieldErrors = FieldApi<
  unknown,
  string,
  undefined,
  undefined,
  unknown
>["state"]["meta"]["errors"];
