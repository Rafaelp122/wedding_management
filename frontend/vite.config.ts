import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
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
