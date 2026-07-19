import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "happy-dom",
      env: {
        TZ: "UTC",
      },
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

      coverage: {
        provider: "v8",
        enabled: false,
        reporter: ["text", "lcov"],
        include: ["src/**/*.{ts,tsx}"],
        exclude: [
          "src/instrument.ts",
          "src/api/types/**",
          "src/features/logistics/types.ts",
          "src/api/generated/**",
          "**/*.test.*",
          "**/*.spec.*",
          "src/test-data.ts",
          "src/test-utils/**",
          "src/main.tsx",
          "src/router/**",
          "src/components/layouts/**",
          "src/features/landing/**",
          "src/features/auth/pages/LoginPage.tsx",
          "src/components/app-sidebar/index.tsx",
          "src/components/app-sidebar/nav-user.tsx",
          "src/components/ui/alert.tsx",
          "src/components/ui/badge.tsx",
          "src/components/ui/breadcrumb.tsx",
          "src/components/ui/button.tsx",
          "src/components/ui/card.tsx",
          "src/components/ui/chart.tsx",
          "src/components/ui/checkbox.tsx",
          "src/components/ui/dialog.tsx",
          "src/components/ui/dropdown-menu.tsx",
          "src/components/ui/form.tsx",
          "src/components/ui/input.tsx",
          "src/components/ui/label.tsx",
          "src/components/ui/progress.tsx",
          "src/components/ui/select.tsx",
          "src/components/ui/separator.tsx",
          "src/components/ui/sheet.tsx",
          "src/components/ui/sidebar.tsx",
          "src/components/ui/skeleton.tsx",
          "src/components/ui/sonner.tsx",
          "src/components/ui/table.tsx",
          "src/components/ui/tabs.tsx",
          "src/components/ui/textarea.tsx",
          "src/components/ui/tooltip.tsx",
        ],
      },
    },
  }),
);
