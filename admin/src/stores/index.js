/**
 * Store 统一导出文件
 * 提供所有store的统一入口
 */

// 导出所有store
export { useAuthStore } from './auth'
export { useApiStore } from './api'
export { useAppStore } from './app'

// 导出store工具函数
export function useStores() {
  return {
    auth: useAuthStore(),
    api: useApiStore(),
    app: useAppStore()
  }
}

// 重置所有store
export function resetAllStores() {
  const stores = useStores()
  
  // 重置认证状态
  stores.auth.logout()
  
  // 清除API历史
  stores.api.clearHistory()
  
  // 重置应用偏好（可选）
  // stores.app.resetPreferences()
  
  console.log('🔄 所有store已重置')
}

// 导出store状态（用于调试）
export function getStoreStates() {
  const stores = useStores()
  
  return {
    auth: {
      isAuthenticated: stores.auth.isAuthenticated,
      user: stores.auth.user,
      hasToken: !!stores.auth.token
    },
    api: {
      requestCount: stores.api.requestCount,
      errorCount: stores.api.errorCount,
      successRate: stores.api.successRate,
      isLoading: stores.api.isLoading
    },
    app: {
      theme: stores.app.theme,
      language: stores.app.language,
      sidebarCollapsed: stores.app.sidebarCollapsed,
      showTokenStatus: stores.app.showTokenStatus
    }
  }
}

// 导出配置（用于备份/恢复）
export function exportAllSettings() {
  const stores = useStores()
  
  return {
    app: stores.app.exportSettings(),
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  }
}

// 导入配置
export function importAllSettings(settings) {
  const stores = useStores()
  
  if (settings.app) {
    stores.app.importSettings(settings.app)
  }
  
  console.log('✅ 配置导入完成')
}
