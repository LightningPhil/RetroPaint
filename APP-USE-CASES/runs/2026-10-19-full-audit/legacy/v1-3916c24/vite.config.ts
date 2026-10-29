import { defineConfig } from 'vite';

// Relative asset URLs so the same build works on GitHub project pages
// (https://<user>.github.io/RetroPaint/) and under `vite preview`.
export default defineConfig({
  base: './',
  server: {
    port: 8080,
    strictPort: true,
  },
  preview: {
    port: 8080,
    strictPort: true,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
  },
});
