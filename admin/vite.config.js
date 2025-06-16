import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  base: '/admin',
  publicDir: 'public', // 确保public目录被复制到构建输出
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // 优化模板编译
          hoistStatic: true,
          cacheHandlers: true
        }
      }
    }),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      // 自动导入 Vue 相关函数
      imports: ['vue', 'vue-router'],
      dts: true
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: true
    }),
  ],
  server: {
    port: 3001,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        followRedirects: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 确保保持原始请求方法
            proxyReq.method = req.method
          })
        }
      }
    }
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'element-plus',
      'axios',
      '@element-plus/icons-vue'
    ]
  }
})
