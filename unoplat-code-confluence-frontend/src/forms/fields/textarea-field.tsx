import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

import { useFieldContext } from "../form-context";
import { getFieldErrorMessages } from "../utils";

interface TextareaFieldProps {
  /** Placeholder text for the textarea */
  placeholder?: string;
  /** Maximum character limit (default: 1000) */
  maxLength?: number;
  /** Number of visible rows (default: 4) */
  rows?: number;
  /** Additional className for the textarea */
  className?: string;
}

/**
 * Pre-bound textarea field with character counter and error display
 *
 * Uses `useFieldContext` to access form field state automatically.
 * Includes a character counter that updates as the user types.
 *
 * @example
 * ```tsx
 * <form.AppField
 *   name="comments"
 *   children={(field) => (
 *     <field.TextareaField
 *       placeholder="Tell us more..."
 *       maxLength={500}
 *     />
 *   )}
 * />
 * ```
 */
export function TextareaField({
  placeholder,
  maxLength = 1000,
  rows = 4,
  className,
}: TextareaFieldProps): React.ReactElement {
  const field = useFieldContext<string>();
  const errors = getFieldErrorMessages(field.state.meta.errors);
  const charCount = field.state.value?.length ?? 0;
  const hasErrors = errors.length > 0;

  return (
    <div className="space-y-2">
      <Textarea
        value={field.state.value ?? ""}
        onChange={(e) => field.handleChange(e.target.value)}
        onBlur={field.handleBlur}
        placeholder={placeholder}
        maxLength={maxLength}
        rows={rows}
        state={hasErrors ? "error" : "default"}
        className={cn(className)}
      />
      <div className="text-muted-foreground flex justify-between text-xs">
        <span>
          {hasErrors ? (
            <span className="text-destructive">{errors[0]}</span>
          ) : null}
        </span>
        <span>
          {charCount}/{maxLength}
        </span>
      </div>
    </div>
  );
}
