# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the documentation website for Unoplat Code Confluence, built with Docusaurus 3.8.1. Code Confluence is a universal code context engine that extracts, understands, and provides precise code context across repositories using Tree-sitter and LLM pipelines. The site is configured in docs-only mode, meaning visitors land directly on the documentation rather than a separate homepage.

## Development Commands

```bash
# Install dependencies
yarn install

# Start development server (http://localhost:3000)
yarn start

# Build for production
yarn build

# Serve production build locally
yarn serve

# Clear Docusaurus cache
yarn clear
```

## Architecture Overview

### Technology Stack
- **Docusaurus 3.8.1** - Static site generator optimized for documentation
- **React 18** - Component framework
- **SWC Compiler** - Rust-based compiler for 20x faster builds (replaces Babel)
- **MDX** - Markdown with JSX for rich content
- **EmailJS** - Contact form integration
- **@visx** - Data visualization components for technical diagrams

### Project Structure
```
docs/                    # Documentation content (MDX files)
├── quickstart/         # Getting started guides
├── deep-dive/          # Technical architecture and vision
├── contribution/       # Contributor guidelines
└── unoplat-oss-atlas/  # OSS Atlas documentation

src/
├── components/         # Custom React components
├── css/               # Custom styling and themes
└── pages/             # Custom pages (contact-us.js, index.js)

static/                # Static assets (images, icons, SVGs)
```

### Key Features
- **Docs-Only Mode** - Site serves documentation directly at root URL
- **Dark Mode Support** - Toggle between light and dark themes with system preference detection
- **Auto-generated Navigation** - File-system based sidebar generation
- **Interactive SVG Diagrams** - Custom modal functionality for architecture diagrams
- **Image Zoom Plugin** - Hover-to-zoom functionality for screenshots
- **External Contact Link** - Contact Us navbar item links to main Unoplat site
- **Mobile Responsive** - Fully responsive design
- **SEO Optimized** - Proper meta tags and semantic HTML

## Content Management

### Adding Documentation
- Create `.md` or `.mdx` files in appropriate `docs/` subdirectories
- Use `_category_.json` files to configure sidebar sections
- Follow existing naming conventions for consistency
- Images should be placed in `static/` directory

### Custom Components
- React components in `src/components/` can be used in MDX files
- Follow existing patterns for styling with CSS modules
- Use `@visx` components for data visualizations and technical diagrams

### Configuration Files
- **`docusaurus.config.js`** - Main site configuration, theming, plugins, navbar/footer
- **`sidebars.js`** - Navigation structure (currently using auto-generated mode)
- **`package.json`** - Dependencies, scripts, and Node.js version requirements

## Relationship to Code Confluence Ecosystem

This documentation site is part of the larger Unoplat Code Confluence monorepo:

- **Backend Services** (`unoplat-code-confluence-ingestion`) - Python-based code parsing and ingestion
- **Frontend Application** (`unoplat-code-confluence-frontend`) - React-based web interface
- **Infrastructure** - Neo4j graph database, PostgreSQL, Temporal workflows
- **This Documentation Site** - User guides, technical docs, and developer resources

The documentation covers the entire platform architecture, from quick 5-minute Docker setup to deep technical architecture explanations.

## Development Notes

### Performance Optimizations
- Uses SWC compiler instead of Babel for significantly faster builds
- Image optimization with WebP support
- Automatic code splitting via Docusaurus

### Content Guidelines
- Keep documentation focused on practical implementation
- Use interactive diagrams for complex architecture explanations
- Maintain consistent tone between technical depth and accessibility
- Update `CHANGELOG.md` for significant documentation changes

### Environment Requirements
- Node.js 18+ (specified in package.json engines)
- Yarn package manager preferred over npm