import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // Served by the FastAPI backend which mounts /assets and falls back
  // to index.html for all other paths, so keep default base "/".
  server: {
    host: "127.0.0.1",
    port: 11121,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:11120",
        changeOrigin: true,
      },
    },
  },
});
