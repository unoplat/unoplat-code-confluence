// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";

// React Compiler configuration (disabled for now)
// See: https://react.dev/reference/react-compiler/configuration
// const ReactCompilerConfig = {
//   // Add any compiler options here if needed
// };

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    tanstackRouter({
      target: "react",
      routesDirectory: "./src/routes",
      generatedRouteTree: "./src/routeTree.gen.ts",
      autoCodeSplitting: false,
    }),
    react({
      // DISABLED: React Compiler breaks TanStack Table functionality
      // Issue: https://github.com/facebook/react/issues/33057
      // TanStack Table uses mutable state internally, incompatible with React Compiler's memoization
      // TODO: Re-enable when TanStack Table v9 or React Compiler adds compatibility
      // babel: {
      //   plugins: [["babel-plugin-react-compiler", ReactCompilerConfig]],
      // },
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
