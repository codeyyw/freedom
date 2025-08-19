import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      '@views': fileURLToPath(new URL('./src/views', import.meta.url)),
      '@utils': fileURLToPath(new URL('./src/utils', import.meta.url)),
      '@assets': fileURLToPath(new URL('./src/assets', import.meta.url))
    },
  },
  server: {
    port: 3000,
    open: true, // 自动打开浏览器
    cors: true, // 允许跨域
    proxy: {
      // 代理配置，用于开发时的API请求
      '/api': {
        target: 'http://localhost:8000', // 后端服务地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // 生产环境不生成sourcemap
    minify: 'terser', // 使用terser压缩
    rollupOptions: {
      output: {
        // 分包策略
        manualChunks: {
          vendor: ['vue'],
          utils: ['lodash', 'axios'] // 如果使用这些库的话
        }
      }
    },
    chunkSizeWarningLimit: 1000 // 调整chunk大小警告限制
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";` // 全局SCSS变量
      }
    }
  },
  optimizeDeps: {
    include: ['vue'] // 预构建依赖
  }
})
