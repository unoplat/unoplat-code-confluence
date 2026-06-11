import react from "@vitejs/plugin-react";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import { defineConfig } from "vite-plus";
// NOTE: createRunnableDevEnvironment MUST come from "vite" (the running engine,
// @voidzero-dev/vite-plus-core via the override), not "vite-plus". The vite-plus
// CLI bundles its own copy of this class; an env built from it fails the engine's
// isRunnableDevEnvironment brand check at runtime and SSR silently 404s.
// eslint-disable-next-line vite-plus/prefer-vite-plus-imports -- engine identity required for TanStack Start's runnable SSR env.
import { createRunnableDevEnvironment } from "vite";
import mdx from "fumadocs-mdx/vite";
import svgr from "vite-plugin-svgr";
import { ViteImageOptimizer } from "vite-plugin-image-optimizer";

export default defineConfig({
  fmt: {},
  lint: {
    jsPlugins: [{ name: "vite-plus", specifier: "vite-plus/oxlint-plugin" }],
    rules: { "vite-plus/prefer-vite-plus-imports": "error" },
    options: { typeAware: true, typeCheck: true },
  },
  server: {
    port: 3000,
  },
  // Native tsconfig `paths` resolution (e.g. `@/*` -> `./src/*`), replacing the
  // vite-tsconfig-paths plugin which vite-plus now supersedes.
  resolve: {
    tsconfigPaths: true,
  },
  // TanStack Start's dev SSR requires a RunnableDevEnvironment (it calls
  // serverEnv.runner.import() to execute the SSR entry in-process). Under
  // vite-plus (Vite 8) the default `ssr` dev environment is non-runnable, so
  // Start silently skips installing its middleware and every route 404s
  // ("Cannot GET /"). Explicitly create the ssr env as runnable to restore SSR.
  environments: {
    ssr: {
      dev: {
        createEnvironment(name, config) {
          return createRunnableDevEnvironment(name, config);
        },
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Use fixed filename for CSS to prevent SSR/client hash mismatch
        // This ensures pre-rendered HTML references the same CSS file that exists after build
        assetFileNames: (assetInfo) => {
          if (assetInfo.names?.some((name) => name.endsWith(".css"))) {
            return "assets/app.css";
          }
          return "assets/[name]-[hash][extname]";
        },
      },
      onwarn(warning, warn) {
        // Suppress Fumadocs MDX architecture warnings
        // Fumadocs intentionally uses both static imports (for SSR) and dynamic imports (for client-side code-splitting)
        // This is expected behavior, not a bug. See: https://github.com/vitejs/vite/issues/13848
        if (
          warning.code === "PLUGIN_WARNING" &&
          warning.message.includes("dynamic import will not move module into another chunk") &&
          warning.message.includes(".source/")
        ) {
          return;
        }
        warn(warning);
      },
    },
  },
  plugins: [
    svgr({
      svgrOptions: {
        // Replace hardcoded colors with currentColor for theme compatibility
        plugins: ["@svgr/plugin-svgo", "@svgr/plugin-jsx"],
        svgoConfig: {
          plugins: [
            {
              name: "preset-default",
              params: {
                overrides: {
                  removeViewBox: false,
                },
              },
            },
            {
              name: "convertColors",
              params: {
                currentColor: true,
              },
            },
          ],
        },
      },
    }),
    mdx(await import("./source.config")),
    tanstackStart({
      // Use full static prerendering instead of SPA mode
      prerender: {
        enabled: true,
        autoSubfolderIndex: true,
        autoStaticPathsDiscovery: true,
        crawlLinks: true,
        // Skip API routes except the static search index export.
        filter: ({ path }) => !path.startsWith("/api/") || path === "/api/search",
      },
      // Sitemap configuration for SEO
      sitemap: {
        enabled: true,
        host: "https://docs.unoplat.io",
        outputPath: "sitemap.xml",
      },
    }),
    react(),
    ViteImageOptimizer({
      test: /\.(jpe?g|png|tiff|webp|avif)$/i,
      includePublic: true,
      logStats: true,
      cache: true,
      // SVGs excluded from test regex — already optimized by vite-plugin-svgr
      png: {
        quality: 82,
        compressionLevel: 9,
      },
      jpeg: {
        quality: 82,
        progressive: true,
        mozjpeg: true,
      },
      webp: {
        lossless: false,
        quality: 82,
        smartSubsample: true,
      },
      avif: {
        lossless: false,
        quality: 75,
      },
    }),
  ],
});
