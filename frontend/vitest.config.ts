import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "happy-dom",
      environmentOptions: {
        happyDom: {
          url: "http://localhost:5173",
        },
      },
      setupFiles: ["./src/test-setup.ts"],
      isolate: false,
      include: ["src/**/*.{test,spec}.{ts,tsx}"],
      exclude: ["node_modules", "dist"],
      css: false,
      deps: {
        optimizer: {
          web: {
            enabled: true,
            include: [
              "react",
              "react-dom",
              "react-router-dom",
              "lucide-react",
              "recharts",
              "date-fns",
              "@tanstack/react-query",
              "zustand",
              "axios",
              "class-variance-authority",
              "clsx",
              "tailwind-merge",
              "zod",
              "sonner"
            ],
          },
        },
      },
      clearMocks: true,
      restoreMocks: true,
      coverage: {
        provider: "v8",
        enabled: false,
        reporter: ["text", "lcov"],
        include: ["src/**/*.{ts,tsx}"],
        exclude: [
          "src/api/generated/**",
          "src/components/ui/**",
          "**/*.test.*",
          "**/*.spec.*",
          "src/test-data.ts",
          "src/main.tsx",
          "src/router/**",
          "src/components/layouts/**",
          "src/components/app-sidebar/**",
          "src/features/landing/**",
          "src/features/auth/pages/LoginPage.tsx",
        ],
      },
    },
  }),
);
