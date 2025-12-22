import { createFormHookContexts } from "@tanstack/react-form";

/**
 * Centralized form contexts created via TanStack Form's createFormHookContexts
 *
 * These contexts enable:
 * - `useFieldContext()` for nested components to access field state without prop drilling
 * - `useFormContext()` for accessing the parent form instance
 *
 * @see https://tanstack.com/form/latest/docs/framework/react/guides/form-composition
 */
export const { fieldContext, formContext, useFieldContext, useFormContext } =
  createFormHookContexts();
