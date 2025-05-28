import * as React from "react";
import * as LabelPrimitive from "@radix-ui/react-label";
import { Slot } from "@radix-ui/react-slot";
import { useForm as useTanstackForm, type AnyFieldApi } from "@tanstack/react-form";

import { cn } from "@/lib/utils";
import { Label } from "@/registry/unoplat-code-confluence/ui/label";

// Form component
interface FormProps extends React.HTMLAttributes<HTMLFormElement> {
  // Using any for FormApi to avoid complex generic type issues
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any;
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void;
}

const Form = React.forwardRef<HTMLFormElement, FormProps>(
  ({ form, children, className, onSubmit, ...props }, ref): React.ReactElement => {
    return (
      <form
        ref={ref}
        onSubmit={(e): void => {
          if (onSubmit) {
            onSubmit(e);
          } else {
            e.preventDefault();
            form.handleSubmit();
          }
        }}
        className={className}
        {...props}
      >
        {children}
      </form>
    );
  }
);
Form.displayName = "Form";

// Type for form field context
type FormFieldContextValue = {
  name: string;
  fieldApi: AnyFieldApi;
};

// Form field context
const FormFieldContext = React.createContext<FormFieldContextValue | undefined>(
  undefined
);

// Field component
interface FormFieldProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "children"> {
  name: string;
  // Using any for FormApi to avoid complex generic type issues
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any;
  children: (field: AnyFieldApi) => React.ReactNode;
}

const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ name, form, children, ...props }, ref): React.ReactElement => {
    return (
      <div ref={ref} {...props}>
        {form.Field({
          name,
          children: (field: AnyFieldApi): React.ReactNode => (
            <FormFieldContext.Provider value={{ name, fieldApi: field }}>
              {children(field)}
            </FormFieldContext.Provider>
          ),
        })}
      </div>
    );
  }
);
FormField.displayName = "FormField";

// Hook to use form field
const useFormField = (): FormFieldContextValue => {
  const fieldContext = React.useContext(FormFieldContext);
  
  if (!fieldContext) {
    throw new Error("useFormField should be used within <FormField>");
  }
  
  return fieldContext;
};

// Form item context
type FormItemContextValue = {
  id: string;
};

const FormItemContext = React.createContext<FormItemContextValue>(
  {} as FormItemContextValue
);

// Form item component
const FormItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref): React.ReactElement => {
  const id = React.useId();

  return (
    <FormItemContext.Provider value={{ id }}>
      <div ref={ref} className={cn("space-y-2", className)} {...props} />
    </FormItemContext.Provider>
  );
});
FormItem.displayName = "FormItem";

// Form label component
const FormLabel = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>
>(({ className, ...props }, ref): React.ReactElement => {
  const { fieldApi } = useFormField();
  const { id } = React.useContext(FormItemContext);
  const formItemId = `${id}-form-item`;
  const hasError = fieldApi.state.meta.errors.length > 0;

  return (
    <Label
      ref={ref}
      className={cn(hasError && "text-destructive", className)}
      htmlFor={formItemId}
      {...props}
    />
  );
});
FormLabel.displayName = "FormLabel";

// Form control component
const FormControl = React.forwardRef<
  React.ElementRef<typeof Slot>,
  React.ComponentPropsWithoutRef<typeof Slot>
>(({ ...props }, ref): React.ReactElement => {
  const { fieldApi } = useFormField();
  const { id } = React.useContext(FormItemContext);
  const formItemId = `${id}-form-item`;
  const formDescriptionId = `${id}-form-item-description`;
  const formMessageId = `${id}-form-item-message`;
  const hasError = fieldApi.state.meta.errors.length > 0;

  return (
    <Slot
      ref={ref}
      id={formItemId}
      aria-describedby={
        !hasError
          ? `${formDescriptionId}`
          : `${formDescriptionId} ${formMessageId}`
      }
      aria-invalid={hasError}
      {...props}
    />
  );
});
FormControl.displayName = "FormControl";

// Form description component
const FormDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref): React.ReactElement => {
  const { id } = React.useContext(FormItemContext);
  const formDescriptionId = `${id}-form-item-description`;

  return (
    <p
      ref={ref}
      id={formDescriptionId}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  );
});
FormDescription.displayName = "FormDescription";

// Form message component
const FormMessage = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, children, ...props }, ref): React.ReactElement => {
  const { fieldApi } = useFormField();
  const { id } = React.useContext(FormItemContext);
  const formMessageId = `${id}-form-item-message`;
  
  const errors = fieldApi.state.meta.errors;
  const body = errors.length > 0 ? errors[0] : children;

  if (!body) {
    return <></>;
  }

  return (
    <p
      ref={ref}
      id={formMessageId}
      className={cn("text-sm font-medium text-destructive", className)}
      {...props}
    >
      {body}
    </p>
  );
});
FormMessage.displayName = "FormMessage";

// Export components
export {
  useFormField,
  Form,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  FormField,
  useTanstackForm,
};