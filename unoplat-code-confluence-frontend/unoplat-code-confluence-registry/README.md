# Unoplat Code Confluence shadcn Registry

This is the official component registry for Unoplat Code Confluence, implementing our design system as a self-hosted shadcn registry.

## Overview

The Unoplat Code Confluence registry provides a collection of React components built with our design system principles:
- Clean, minimalistic interfaces
- Developer-focused design
- Accessibility-first approach
- Consistent typography and color system
- Full dark mode support

## Design System

Our design system is built using tweakcn and is available via:

```bash
pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/cmb66bxi6000104l41iyf32wb
```
and access it on [web](https://tweakcn.com/r/themes/cmb66bxi6000104l41iyf32wb)
## Available Components

### UI Components
- `alert` - Alert messages with different severity levels
- `alert-dialog` - Modal dialogs for important alerts and confirmations
- `avatar` - User avatar display with fallback support
- `badge` - Small count and labeling components
- `breadcrumb` - Navigation breadcrumbs for hierarchy display
- `button` - Buttons with multiple variants (primary, secondary, outline, ghost, link)
- `calendar` - Date picker calendar component
- `card` - Content containers with header, body, and footer sections
- `checkbox` - Checkbox inputs with label support
- `collapsible` - Expandable/collapsible content sections
- `command` - Command palette interface component
- `dialog` - Modal dialog boxes for user interactions
- `drawer` - Slide-out drawer panels
- `dropdown-menu` - Dropdown menu with keyboard navigation
- `form` - Form components with validation support
- `input` - Form inputs with hover and focus states
- `label` - Form labels with proper accessibility
- `popover` - Floating popovers for additional content
- `select` - Select dropdown components
- `separator` - Visual separator lines
- `sheet` - Slide-out sheet components
- `sidebar` - Navigation sidebar component
- `skeleton` - Loading skeleton placeholders
- `slider` - Range slider input component
- `switch` - Toggle switch components
- `table` - Data table with sorting and filtering
- `tabs` - Tabbed interface components
- `textarea` - Multi-line text inputs
- `toast` - Toast notifications system
- `toaster` - Toast notification container
- `tooltip` - Hover tooltips for additional information
- `use-toast` - Toast notification hook

### Blocks
- `feedback-form` - Complete feedback form component with validation

### Showcase
- `unoplat-showcase` - Complete demonstration of all components and design patterns

## Using the Registry

### With shadcn CLI

```bash
# Add components to application consuming from registry
npx shadcn@latest add http://localhost:3000/r/button.json

### Building the Registry

```bash
task launch-registry
```