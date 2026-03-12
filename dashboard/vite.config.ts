import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Inside Docker: backend resolves via Docker DNS
// Local dev: falls back to localhost:8000
const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://localhost:8000'
const BACKEND_WS = BACKEND_URL.replace(/^http/, 'ws')

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/health': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/ws': {
        target: BACKEND_WS,
        ws: true,
      },
    },
  },
})
