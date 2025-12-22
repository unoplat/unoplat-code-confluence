import type { FieldErrors } from "./types";

/**
 * Extract string error messages from TanStack Form field errors
 *
 * TanStack Form validation returns errors as an array of mixed types:
 * - String messages directly from validators
 * - Objects with { message: string } from Zod or other schema validators
 *
 * This utility normalizes these into a string array for display.
 *
 * @param errors - Array of error values from field.state.meta.errors
 * @returns Array of extracted string messages
 *
 * @example
 * ```tsx
 * const field = useFieldContext<string>()
 * const messages = getFieldErrorMessages(field.state.meta.errors)
 * // messages: ["Field is required", "Must be at least 3 characters"]
 * ```
 */
export function getFieldErrorMessages(errors: FieldErrors): string[] {
  return errors
    .map((err) => {
      if (typeof err === "string") return err;
      if (typeof err === "object" && err !== null && "message" in err) {
        return (err as { message?: string }).message;
      }
      return undefined;
    })
    .filter((msg): msg is string => Boolean(msg));
}
