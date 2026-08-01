import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  root: resolve(__dirname),
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:4199',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:4199',
        ws: true,
      },
    },
  },
  base: './',
})
