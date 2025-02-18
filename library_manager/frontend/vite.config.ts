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
  test: { // Add this test configuration
    globals: true, // Important for using Jest-like globals (describe, it, expect)
    environment: 'jsdom', // Simulate a browser environment for React testing
    include: ['tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'], // Include test files
    setupFiles: [], // Optional: Add setup files if needed (e.g., for global mocks)
  },
})
