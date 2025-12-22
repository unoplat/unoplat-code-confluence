import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

import { useFieldContext } from "../form-context";
import { getFieldErrorMessages } from "../utils";

interface CategoryChipOption<T extends string> {
  /** The value to store when selected */
  value: T;
  /** Display label for the chip */
  label: string;
}

interface CategoryChipsFieldProps<T extends string> {
  /** Array of options to display as selectable chips */
  options: CategoryChipOption<T>[];
  /** Additional className for the chips container */
  className?: string;
}

/**
 * Pre-bound multi-select chip field for category/tag selection
 *
 * Uses `useFieldContext` to access form field state automatically.
 * Renders as a flex-wrap container of selectable pill-shaped chips.
 * Supports selecting multiple options (stored as array).
 *
 * @typeParam T - The string literal type for option values
 *
 * @example
 * ```tsx
 * const CATEGORY_OPTIONS = [
 *   { value: 'accuracy', label: 'Accuracy Issues' },
 *   { value: 'clarity', label: 'Clarity Issues' },
 * ]
 *
 * <form.AppField
 *   name="categories"
 *   children={(field) => (
 *     <field.CategoryChipsField options={CATEGORY_OPTIONS} />
 *   )}
 * />
 * ```
 */
export function CategoryChipsField<T extends string>({
  options,
  className,
}: CategoryChipsFieldProps<T>): React.ReactElement {
  const field = useFieldContext<T[]>();
  const errors = getFieldErrorMessages(field.state.meta.errors);

  return (
    <div className="space-y-2">
      <div className={cn("flex flex-wrap gap-2", className)}>
        {options.map(({ value, label }) => {
          const isSelected = field.state.value.includes(value);
          return (
            <Label
              key={value}
              className={cn(
                "flex cursor-pointer items-center gap-2 rounded-full border px-4 py-2 transition-colors",
                isSelected
                  ? "border-primary bg-primary/10"
                  : "border-input hover:bg-muted",
              )}
            >
              <Checkbox
                checked={isSelected}
                onCheckedChange={(checked) => {
                  const current = field.state.value;
                  field.handleChange(
                    checked === true
                      ? [...current, value]
                      : current.filter((v) => v !== value),
                  );
                }}
                className="sr-only"
              />
              <span className="text-sm">{label}</span>
            </Label>
          );
        })}
      </div>
      {errors.length > 0 && (
        <p className="text-destructive text-sm">{errors[0]}</p>
      )}
    </div>
  );
}
