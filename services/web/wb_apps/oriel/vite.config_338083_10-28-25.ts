import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import glsl from "vite-plugin-glsl";

// 🧠 oriel Vite configuration
export default defineConfig({
  plugins: [
    react(),
    glsl()
  ],
  resolve: {
    alias: {
      "@": "/src",
    },
  },
  server: {
    host: true,
    open: false,
    port: 5173,
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
  optimizeDeps: {
    include: ["react", "react-dom", "three", "framer-motion"],
  },
});
