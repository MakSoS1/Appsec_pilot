// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - tanstackStart, viteReact, tailwindcss, tsConfigPaths, cloudflare (build-only),
//     componentTagger (dev-only), VITE_* env injection, @ path alias, React/TanStack dedupe,
//     error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... } }) if needed.
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

const basePath = process.env.VITE_BASE_PATH ?? "/";
const routerBasePath =
  basePath.endsWith("/") && basePath.length > 1 ? basePath.slice(0, -1) : basePath;
const pagesBuild = process.env.VITE_PAGES_BUILD === "true";

const tanstackStartConfig = pagesBuild
  ? {
      router: { basepath: routerBasePath },
      prerender: {
        enabled: true,
        autoSubfolderIndex: true,
        crawlLinks: true,
      },
      pages: [
        {
          path: "/",
          prerender: {
            enabled: true,
            outputPath: "/",
            autoSubfolderIndex: true,
            crawlLinks: true,
          },
        },
      ],
    }
  : {
      server: { entry: "server" },
      router: { basepath: routerBasePath },
    };

// Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
// @cloudflare/vite-plugin builds from this — wrangler.jsonc main alone is insufficient.
export default defineConfig({
  cloudflare: pagesBuild ? false : undefined,
  vite: {
    base: basePath,
  },
  tanstackStart: tanstackStartConfig,
});
