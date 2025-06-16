import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/global.css'
import { permissionDirective, roleDirective } from './composables/usePermissions'
import { setAuthStore } from './utils/api'

const app = createApp(App)
const pinia = createPinia()

// 配置pinia持久化插件
pinia.use(piniaPluginPersistedstate)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
// 开发环境下引入调试工具
if (import.meta.env.DEV) {
  import('./utils/permissionTest.js')
  import('./utils/permissionSystemTest.js')
  import('./utils/finalPermissionValidation.js')
  // import('./utils/tokenDebug.js')
}
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 注册权限和角色指令
app.directive('permission', permissionDirective)
app.directive('role', roleDirective)

// 设置auth store到API模块（在pinia初始化后）
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
setAuthStore(authStore)

app.mount('#app')
