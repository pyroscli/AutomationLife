import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Proxy API + OAuth routes to the FastAPI backend so the browser only ever
// sees one origin (localhost:5173) and session cookies stay same-origin.
const backend = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: backend, changeOrigin: false },
      '/login': { target: backend, changeOrigin: false },
      '/auth': { target: backend, changeOrigin: false },
    },
  },
})
