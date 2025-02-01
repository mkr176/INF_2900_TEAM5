import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // generate .vite/manifest.json in outDir
    manifest: true,
    rollupOptions: {
      // overwrite default .html entry
      // input: '/path/to/main.js',
      output: {
        assetFileNames: 'assets/css/index.min.css',
        entryFileNames: 'assets/js/[name].min.js',
      },
    },
  },
})
