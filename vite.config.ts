import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],

    // Tauri development configuration
    clearScreen: false,
    server: {
        port: 1420,
        strictPort: true,
        host: true,
        watch: {
            // Tell vite to ignore watching src-tauri
            ignored: ["**/src-tauri/**"]
        }
    },

    // Environment variables
    envPrefix: ['VITE_', 'TAURI_'],

    // Build configuration
    build: {
        // Output to dist directory (Tauri will look here)
        outDir: 'dist',
        sourcemap: !!process.env.TAURI_DEBUG,
        // Don't minify in debug builds
        minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
        // Don't clear dist in watch mode
        emptyOutDir: !process.env.TAURI_DEBUG,
    }
})