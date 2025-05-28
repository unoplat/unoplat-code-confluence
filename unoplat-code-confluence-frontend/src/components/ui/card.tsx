import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "../../lib/utils"

const cardVariants = cva(
  "bg-card text-card-foreground transition-colors",
  {
    variants: {
      variant: {
        default: "border bg-card shadow-[--shadow-sm]",
        elevated: "border-0 bg-card shadow-[--shadow-md]",
        outline: "border-2 bg-card shadow-none",
        ghost: "border-0 bg-transparent shadow-none",
      },
      padding: {
        none: "",
        sm: "[&_[data-card-header]]:p-4 [&_[data-card-content]]:p-4 [&_[data-card-content]]:pt-0 [&_[data-card-footer]]:p-4 [&_[data-card-footer]]:pt-0",
        default: "[&_[data-card-header]]:p-6 [&_[data-card-content]]:p-6 [&_[data-card-content]]:pt-0 [&_[data-card-footer]]:p-6 [&_[data-card-footer]]:pt-0",
        lg: "[&_[data-card-header]]:p-8 [&_[data-card-content]]:p-8 [&_[data-card-content]]:pt-0 [&_[data-card-footer]]:p-8 [&_[data-card-footer]]:pt-0",
      },
      radius: {
        default: "rounded-[--radius-lg]",
        sm: "rounded-[--radius-sm]",
        md: "rounded-[--radius-md]",
        lg: "rounded-[--radius-lg]",
        xl: "rounded-[--radius-xl]",
        none: "rounded-none",
      },
    },
    defaultVariants: {
      variant: "default",
      padding: "default",
      radius: "default",
    },
  }
)

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, radius, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, padding, radius }), className)}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-card-header
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-card-content
    className={cn("p-6 pt-0", className)}
    {...props}
  />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-card-footer
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, cardVariants } 