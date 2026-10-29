import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    host: '127.0.0.1',
    fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/.local/**', '**/.cache/**', '**/.handoff-backups/**', '**/.releases/**', '**/backend/**'] },
    watch: { ignored: ['**/.cache/**', '**/.local/**', '**/backend/**', '**/.handoff-backups/**'] },
    proxy: { '/api': { target: process.env.CAMPUSLINK_BACKEND_URL || 'http://127.0.0.1:8000', changeOrigin: true } }
  },
  preview: {
    host: '127.0.0.1',
    proxy: { '/api': { target: process.env.CAMPUSLINK_BACKEND_URL || 'http://127.0.0.1:8000', changeOrigin: true } }
  }
})
