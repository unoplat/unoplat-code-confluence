# Shadcn Registry Guide for Developers

## Overview

This guide explains how to properly structure and maintain a custom shadcn/ui registry, based on our implementation of the Unoplat Code Confluence design system and official shadcn documentation.

## Key Concepts

### Registry Types

There are two main registry item types for design systems:

1. **`registry:style`** - Complete design system foundation
   - Extends or replaces the default shadcn style
   - Contains typography, spacing, shadows, and base design tokens
   - Includes dependencies and component configurations
   - Applied once at project initialization (cannot be changed later)

2. **`registry:theme`** - Pure color schemes
   - Only contains color-related CSS variables
   - No dependencies or extends field
   - Can be added or changed after initialization
   - Provides light/dark mode color definitions

### Architecture Principles

#### 1. Inline Definitions (REQUIRED)

Per official documentation, themes and styles MUST use inline definitions:

```json
{
  "name": "my-theme",
  "type": "registry:theme",
  "cssVars": {
    "light": { /* colors */ },
    "dark": { /* colors */ }
  }
}
```

**NEVER use file references for themes/styles:**
```json
// ❌ WRONG - Don't do this
{
  "name": "my-theme",
  "type": "registry:theme",  
  "files": [{
    "path": "path/to/theme.json",
    "type": "registry:theme"
  }]
}
```

The `files[]` array is only for code assets (components, pages, utils), not for theme/style definitions.

#### 2. Separation of Concerns

**Style** contains:
- Font families (`font-sans`, `font-mono`, etc.)
- Border radius
- Shadows
- Spacing scales
- Any non-color design tokens

**Theme** contains ONLY colors:
- Background/foreground colors
- Semantic colors (primary, secondary, etc.)
- Component-specific colors (card, popover, etc.)
- Chart colors

## Implementation Examples

### 1. Theme Definition (Official Pattern)
```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "custom-theme",
  "type": "registry:theme",
  "cssVars": {
    "light": {
      "background": "oklch(1 0 0)",
      "foreground": "oklch(0.141 0.005 285.823)",
      "primary": "oklch(0.546 0.245 262.881)",
      "primary-foreground": "oklch(0.97 0.014 254.604)",
      "ring": "oklch(0.746 0.16 232.661)",
      "sidebar-primary": "oklch(0.546 0.245 262.881)",
      "sidebar-primary-foreground": "oklch(0.97 0.014 254.604)",
      "sidebar-ring": "oklch(0.746 0.16 232.661)"
    },
    "dark": {
      "background": "oklch(0.141 0.005 285.823)",
      "foreground": "oklch(0.985 0 0)",
      "primary": "oklch(0.707 0.165 254.624)",
      "primary-foreground": "oklch(0.97 0.014 254.604)",
      "ring": "oklch(0.707 0.165 254.624)",
      "sidebar-primary": "oklch(0.707 0.165 254.624)",
      "sidebar-primary-foreground": "oklch(0.97 0.014 254.604)",
      "sidebar-ring": "oklch(0.707 0.165 254.624)"
    }
  }
}
```

### 2. Style Definition - Extending Default
```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "example-style",
  "type": "registry:style",
  "dependencies": ["@tabler/icons-react"],
  "registryDependencies": [
    "login-01",
    "calendar",
    "https://example.com/r/editor.json"
  ],
  "cssVars": {
    "theme": {
      "font-sans": "Inter, sans-serif"
    },
    "light": {
      "brand": "20 14.3% 4.1%"
    },
    "dark": {
      "brand": "20 14.3% 4.1%"
    }
  }
}
```

### 3. Style Definition - From Scratch
```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "extends": "none",
  "name": "new-style",
  "type": "registry:style",
  "dependencies": ["tailwind-merge", "clsx"],
  "registryDependencies": [
    "utils",
    "https://example.com/r/button.json"
  ],
  "cssVars": {
    "theme": {
      "font-sans": "Inter, sans-serif"
    },
    "light": {
      "main": "#88aaee",
      "bg": "#dfe5f2",
      "border": "#000",
      "text": "#000",
      "ring": "#000"
    },
    "dark": {
      "main": "#88aaee",
      "bg": "#272933",
      "border": "#000",
      "text": "#e6e6e6",
      "ring": "#fff"
    }
  }
}
```

## cssVars Structure

The `cssVars` object can have at most three top-level keys:

1. **`theme`** - Global tokens that apply regardless of light/dark mode
   - Fonts, animations, spacing, etc.
   - Variables that don't change with color scheme

2. **`light`** - Light mode specific values
   - Color values for light theme
   - Can include mode-specific shadows or other tokens

3. **`dark`** - Dark mode specific values
   - Color values for dark theme
   - Parallels the light mode structure

## Color Format Best Practices

Use **OKLCH** color space (recommended by shadcn):
```
oklch(lightness chroma hue)
- lightness: 0-1 (0 = black, 1 = white)
- chroma: 0-0.5 (0 = gray, higher = more colorful)
- hue: 0-360 (color wheel angle)
```

Examples from official themes:
```json
"primary": "oklch(0.546 0.245 262.881)",
"background": "oklch(1 0 0)",
"destructive": "oklch(0.577 0.245 27.325)"
```

## Required CSS Variables

Ensure these variables are defined for shadcn components to work properly:

### Core Colors (Required)
- `background`, `foreground`
- `card`, `card-foreground`
- `popover`, `popover-foreground`
- `primary`, `primary-foreground`
- `secondary`, `secondary-foreground`
- `muted`, `muted-foreground`
- `accent`, `accent-foreground`
- `destructive`, `destructive-foreground`
- `border`, `input`, `ring`

### Chart Colors
- `chart-1` through `chart-5`

### Sidebar Colors (if using sidebar)
- `sidebar`, `sidebar-foreground`
- `sidebar-primary`, `sidebar-primary-foreground`
- `sidebar-accent`, `sidebar-accent-foreground`
- `sidebar-border`, `sidebar-ring`

## Extending vs Starting Fresh

### Extending Default Style (Recommended)
Simply omit the `extends` field - this inherits from the default "new-york" style:
```json
{
  "name": "my-style",
  "type": "registry:style"
  // No "extends" field = inherits from default
}
```

### Starting from Scratch
Use `"extends": "none"` and provide ALL required tokens:
```json
{
  "name": "my-style",
  "type": "registry:style",
  "extends": "none",
  "dependencies": ["tailwind-merge", "clsx"],
  "registryDependencies": ["utils"],
  "cssVars": {
    // Must define ALL variables!
  }
}
```

## Common Mistakes to Avoid

### 1. Schema Validation Errors
Always include the schema reference:
```json
"$schema": "https://ui.shadcn.com/schema/registry-item.json"
```

Use exact type strings:
- ✅ `"type": "registry:style"`
- ✅ `"type": "registry:theme"`
- ❌ `"type": "style"` (missing prefix)
- ❌ `"type": "registry:styles"` (wrong plural)

### 2. Mixing Concerns
```json
// ❌ WRONG - Theme with non-color variables
{
  "type": "registry:theme",
  "cssVars": {
    "light": {
      "primary": "...",
      "font-sans": "Inter" // Should be in style!
    }
  }
}
```

### 3. Invalid extends Values
```json
// ✅ CORRECT - Valid extends values
"extends": "none"  // Start from scratch
// OR omit the field to extend default

// ❌ WRONG - Invalid extends values
"extends": "my-custom-style"
"extends": "default"
```

## Testing Your Registry

1. **Build the registry:**
   ```bash
   pnpm registry:build
   ```

2. **Check output in `public/r/`:**
   - Verify JSON files are generated
   - Built files will wrap content in a files array (this is normal)

3. **Test installation:**
   ```bash
   pnpm dlx shadcn@latest add http://localhost:3000/r/[item-name].json
   ```

## Integration with components.json

Set your style in `components.json` before initialization:
```json
{
  "style": "unoplat-style", // Your custom style name
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  }
}
```

Remember: **"The style for your components… cannot be changed after initialization."**

## CLI Usage

- **Initialize with style**: Set in components.json, then `shadcn init`
- **Add theme later**: `shadcn add custom-theme`
- **Add components**: `shadcn add button` (uses your style)

## Key Takeaways

1. **Always use inline definitions** for themes and styles (no file references)
2. **Themes contain only colors**, styles contain everything else
3. **Include schema references** for validation
4. **Omit extends to inherit** from default style
5. **Choose style at init time** - it cannot be changed later
6. **Use OKLCH colors** for better color manipulation
7. **Test locally** before deploying your registry

This approach ensures your registry follows official shadcn patterns and provides a maintainable design system for your projects.