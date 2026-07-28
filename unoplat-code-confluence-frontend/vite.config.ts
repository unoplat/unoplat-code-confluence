// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// React Compiler configuration
// See: https://react.dev/reference/react-compiler/configuration
// Note: Default behavior already excludes node_modules (verified in babel-plugin-react-compiler source)
// TanStack Table compatibility: Use "use no memo" directive in components using useReactTable()
// Issue: https://github.com/facebook/react/issues/33057
// const ReactCompilerConfig = {
//   panicThreshold: 'none', // Skip problematic components instead of failing build
// };

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    tanstackRouter({
      target: "react",
      routesDirectory: "./src/routes",
      generatedRouteTree: "./src/routeTree.gen.ts",
      autoCodeSplitting: false,
    }),
    // react({
    //   babel: {
    //     plugins: [['babel-plugin-react-compiler', ReactCompilerConfig]],
    //   },
  // }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    // Browser uses same-origin /electric/*; proxy to Electric so host port
    // 3001 and CORS are not required. In Tilt/Compose, ELECTRIC_PROXY_TARGET
    // points at the Compose service DNS name (http://electric:3000).
    proxy: {
      "/electric": {
        target: process.env.ELECTRIC_PROXY_TARGET ?? "http://127.0.0.1:3001",
        changeOrigin: true,
        rewrite: (requestPath) => requestPath.replace(/^\/electric/, ""),
      },
    },
  },
  build: {
    rollupOptions: {
      // Customize Rollup behavior during production builds
      // See: https://rollupjs.org/configuration-options/
      onwarn(warning, defaultHandler) {
        // Suppress "use client" directive warnings in SPA builds
        // These directives are for Next.js Server Components and are meaningless in client-only apps
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE') {
          return;
        }
        // Suppress sourcemap errors (can't resolve original location)
        if (warning.code === 'SOURCEMAP_ERROR') {
          return;
        }
        // Pass all other warnings through (THIS_IS_UNDEFINED, CIRCULAR_DEPENDENCY, etc.)
        defaultHandler(warning);
      },
    },
  },
});
