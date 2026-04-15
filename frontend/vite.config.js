import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,      // ✅ THIS is the key fix
    port: 5173,
    watch: {
      usePolling: true,   // ✅ THIS fixes hot reload in Docker
    }
  }
})