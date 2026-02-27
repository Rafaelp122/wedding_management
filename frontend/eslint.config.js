import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  // Arquivos e pastas ignorados globalmente
  globalIgnores(["dist", "node_modules", "src/api/generated/**/*"]),

  // 2. Configuração Global
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      "@typescript-eslint/no-empty-object-type": [
        "error",
        { allowInterfaces: "with-single-extends" },
      ],
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  },

  // Exceção específica para o shadcn/ui
  {
    // Aplica-se apenas aos arquivos dentro da pasta ui
    files: ["src/components/ui/**/*.{ts,tsx}"],
    rules: {
      // Desativa o aviso que o shadcn causa propositalmente
      "react-refresh/only-export-components": "off",
    },
  },
]);
