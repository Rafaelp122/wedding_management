import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { sentryVitePlugin } from "@sentry/vite-plugin";

export default defineConfig({
  envDir: "../",
  build: {
    sourcemap: true,
  },
  plugins: [
    react(),
    tailwindcss(),
    ...(process.env.SENTRY_AUTH_TOKEN
      ? [
          sentryVitePlugin({
            org: "rafael-pereira",
            project: "react-frontend",
            authToken: process.env.SENTRY_AUTH_TOKEN,
          }),
        ]
      : []),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true, // Necessário para o Docker expor a rede
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true, // Garante detecção de mudanças no Windows/WSL2
      interval: 100,
    },
    hmr: {
      clientPort: 5173, // Garante que o HMR conecte na porta do Host
    },
  },
});
