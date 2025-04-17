# How to Enable the Delete (Trash) Button in CodebaseForm

This guide explains how to re-enable the delete (trash) button for each codebase entry in the `CodebaseForm` component.

## Steps to Enable Delete Functionality

1. **Restore the `onRemove` prop in the `CodebaseFormProps` interface:**

```ts
export interface CodebaseFormProps {
  index: number;
  parentForm: any; // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onRemove?: () => void;
}
```

2. **Accept the `onRemove` prop in the `CodebaseForm` function signature:**

```ts
export function CodebaseForm({
  index,
  parentForm,
  onRemove,
}: CodebaseFormProps): React.ReactElement {
  // ...
```

3. **Re-add the Trash (delete) button JSX inside the main return block, just after the opening `<div>`:**

```tsx
{onRemove && (
  <Button
    variant="ghost"
    size="icon"
    className="absolute top-2 right-2"
    onClick={onRemove}
    type="button"
  >
    <TrashIcon className="h-4 w-4 text-destructive" />
  </Button>
)}
```

4. **Restore the following imports at the top of the file:**

```ts
import { TrashIcon, InfoIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
```

## Summary
- Uncomment or re-add the code above in `src/components/custom/CodebaseForm.tsx`.
- The delete button will appear for each codebase form, and will call the `onRemove` callback when clicked.

**Type hints are included for all TypeScript code.** 