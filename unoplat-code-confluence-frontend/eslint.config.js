import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import react from 'eslint-plugin-react'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import tseslint from 'typescript-eslint'
import prettierConfig from 'eslint-config-prettier'
import reactCompiler from 'eslint-plugin-react-compiler'
import useNoMemo from 'eslint-plugin-use-no-memo'

export default tseslint.config(
  // Ignore patterns
  {
    ignores: ['dist', 'node_modules', '.yarn', 'routeTree.gen.ts']
  },

  // Main configuration for all TypeScript/TSX files
  {
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommended,
      prettierConfig,
    ],
    files: ['src/**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: {
        ...globals.browser,
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    settings: {
      react: {
        version: 'detect', // Auto-detect React version
      },
      // Map shadcn/ui custom components to HTML elements for a11y rules
      'jsx-a11y': {
        components: {
          // Example mappings - adjust based on your custom components
          Button: 'button',
          Input: 'input',
          Select: 'select',
          Textarea: 'textarea',
          Link: 'a',
        },
      },
    },
    plugins: {
      'react': react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      'jsx-a11y': jsxA11y,
      'react-compiler': reactCompiler,
      'use-no-memo': useNoMemo,
    },
    rules: {
      // ==========================================
      // REACT HOOKS RULES (React Compiler compatible)
      // ==========================================
      // Updated to recommended-latest for React Compiler support
      ...reactHooks.configs['recommended-latest'].rules,

      // ==========================================
      // REACT RULES
      // ==========================================
      // Core React recommended rules
      ...react.configs.recommended.rules,
      // JSX runtime rules (React 17+, no need to import React)
      ...react.configs['jsx-runtime'].rules,

      // Performance rules
      // Note: jsx-no-bind relaxed to 'warn' because React Compiler auto-memoizes inline functions
      'react/jsx-no-bind': ['warn', {
        allowArrowFunctions: true,  // React Compiler handles this
        allowBind: false,
        ignoreRefs: true,
        ignoreDOMComponents: true,
      }],
      'react/jsx-no-constructed-context-values': 'error',
      'react/no-unstable-nested-components': 'error',
      'react/no-array-index-key': 'warn',

      // Best practices
      'react/self-closing-comp': 'error',
      'react/jsx-boolean-value': ['error', 'never'],
      'react/jsx-curly-brace-presence': ['error', {
        props: 'never',
        children: 'never',
        propElementValues: 'always'  // Recommended for consistency
      }],
      'react/jsx-fragments': ['error', 'syntax'], // Use <> instead of <Fragment>
      'react/jsx-no-useless-fragment': 'error',

      // React 19 specific
      'react/no-deprecated': 'error',
      'react/no-unknown-property': ['error', {
        ignore: ['css', 'cmdk-input', 'cmdk-list', 'cmdk-item', 'cmdk-group', 'cmdk-dialog', 'cmdk-separator']
      }],

      // ==========================================
      // ACCESSIBILITY RULES
      // ==========================================
      ...jsxA11y.flatConfigs.recommended.rules,

      // Additional strict a11y rules
      'jsx-a11y/anchor-ambiguous-text': 'warn',
      'jsx-a11y/no-aria-hidden-on-focusable': 'error',
      'jsx-a11y/prefer-tag-over-role': 'warn',

      // ==========================================
      // REACT REFRESH (Vite HMR)
      // ==========================================
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],

      // ==========================================
      // TYPESCRIPT OVERRIDES
      // ==========================================
      // Relax some TS rules that conflict with React patterns
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
      '@typescript-eslint/ban-ts-comment': ['error', {
        'ts-expect-error': 'allow-with-description',
      }],

      // ==========================================
      // REACT COMPILER
      // ==========================================
      // Enabled with "use no memo" directives for TanStack Table components
      // See: https://github.com/facebook/react/issues/33057
      // 'react-compiler/react-compiler': 'error',
    },
  },
)
