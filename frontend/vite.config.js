// Owner: Member 2
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // In development, /api calls go to the FastAPI server. No CORS setup needed.
    proxy: { '/api': 'http://localhost:8000' },
  },
  test: { environment: 'node' },
})
