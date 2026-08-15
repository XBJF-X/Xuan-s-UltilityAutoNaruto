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
  build: {
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          // vue/pinia 等运行时单例库必须保持单实例：
          // 若被重复打包（如 pinia 同时被入口与 store 异步 chunk 各自内联一份），
          // 会因 piniaSymbol 不一致导致 useStore 拿不到 activePinia，报
          // "Cannot read properties of undefined (reading '_s')"。
          if (
            id.includes('node_modules/pinia') ||
            id.includes('node_modules/vue') ||
            id.includes('node_modules/vue-router') ||
            id.includes('node_modules/@vue')
          ) {
            return 'vue-vendor'
          }
          return undefined
        },
      },
    },
  },
})
