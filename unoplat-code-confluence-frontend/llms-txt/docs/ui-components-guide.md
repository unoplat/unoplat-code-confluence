# UI Components Guide

## Using Shadcn UI Components

This project uses [Shadcn UI](https://ui.shadcn.com/) components, which are built on top of Radix UI primitives. Shadcn UI provides a consistent set of accessible, customizable components that follow best practices for modern web applications.

### Key Principles

1. **Always use Shadcn UI components** instead of direct Radix UI components when possible
2. **Never import directly from Radix UI** in application components
3. **Follow the established patterns** for component usage to maintain consistency

### Available Components

The following Shadcn UI components are available in the project:

- Alert (`./ui/alert`)
- Button (`./ui/button`)
- Card (`./ui/card`)
- Checkbox (`./ui/checkbox`)
- Dialog (`./ui/dialog`)
- Dropdown Menu (`./ui/dropdown-menu`)
- Form components (`./ui/form/form`)
- Input (`./ui/input`)
- Label (`./ui/label`)
- Popover (`./ui/popover`)
- Separator (`./ui/separator`)
- Table (`./ui/table`)
- Toast (`./ui/toast`)
- Tooltip (`./ui/tooltip`)

### Example: Using Dialog Components

❌ **Incorrect** (importing directly from Radix UI):
```tsx
import * as Dialog from '@radix-ui/react-dialog';

function MyComponent() {
  return (
    <Dialog.Root>
      <Dialog.Trigger>Open</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay />
        <Dialog.Content>
          <Dialog.Title>Title</Dialog.Title>
          <Dialog.Description>Description</Dialog.Description>
          <Dialog.Close>Close</Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

✅ **Correct** (using Shadcn UI components):
```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';

function MyComponent() {
  return (
    <Dialog>
      <DialogTrigger>Open</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Title</DialogTitle>
          <DialogDescription>Description</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

### Adding New Components

When new UI components are needed:

1. Check if a Shadcn UI component already exists
2. If not, create a new component following the Shadcn UI patterns
3. Place the component in the `src/components/ui` directory
4. Export the component with proper TypeScript types and appropriate naming

### Benefits of Using Shadcn UI

- **Consistency** in styling and behavior
- **Accessibility** built-in
- **Type safety** with proper TypeScript definitions
- **Customizability** with Tailwind CSS
- **Better developer experience**

### Common Issues

- Background not hiding behind modals/dialogs: Make sure to use the Shadcn Dialog component which includes the proper overlay handling
- Styling inconsistencies: Use the provided Tailwind classes and avoid custom styling when possible
- Accessibility issues: Shadcn components include built-in accessibility features that may be missing in custom implementations

By following these guidelines, we can maintain a consistent, accessible, and maintainable UI across the application. 