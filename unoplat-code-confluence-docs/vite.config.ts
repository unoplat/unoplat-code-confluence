import react from "@vitejs/plugin-react";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import { defineConfig } from "vite";
import tsConfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import mdx from "fumadocs-mdx/vite";

export default defineConfig({
  server: {
    port: 3000,
  },
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress Fumadocs MDX architecture warnings
        // Fumadocs intentionally uses both static imports (for SSR) and dynamic imports (for client-side code-splitting)
        // This is expected behavior, not a bug. See: https://github.com/vitejs/vite/issues/13848
        if (
          warning.code === "PLUGIN_WARNING" &&
          warning.message.includes(
            "dynamic import will not move module into another chunk",
          ) &&
          warning.message.includes(".source/")
        ) {
          return;
        }
        warn(warning);
      },
    },
  },
  plugins: [
    mdx(await import("./source.config")),
    tailwindcss(),
    tsConfigPaths({
      projects: ["./tsconfig.json"],
    }),
    tanstackStart({
      // Use full static prerendering instead of SPA mode
      prerender: {
        enabled: true,
        autoSubfolderIndex: true,
        autoStaticPathsDiscovery: true,
        crawlLinks: true,
      },
      // Pre-render the search API route for static search index
      pages: [
        {
          path: "/api/search",
          prerender: { enabled: true, outputPath: "/api/search" },
        },
      ],
      // Sitemap configuration for SEO
      sitemap: {
        enabled: true,
        host: "https://docs.unoplat.io",
        outputPath: "sitemap.xml",
      },
    }),
    react(),
  ],
});
