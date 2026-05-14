import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      environmentOptions: {
        jsdom: {
          url: "http://localhost:5173",
        },
      },
      setupFiles: ["./src/test-setup.ts"],
      include: ["src/**/*.{test,spec}.{ts,tsx}"],
      exclude: ["node_modules", "dist"],
      css: true,
      clearMocks: true,
      restoreMocks: true,
      coverage: {
        provider: "v8",
        enabled: false,
        include: ["src/**/*.{ts,tsx}"],
        exclude: [
          "src/api/generated/**",
          "src/components/ui/**",
          "**/*.test.*",
          "**/*.spec.*",
          "src/types/**",
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
