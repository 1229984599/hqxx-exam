import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const sidebarCollapsed = ref(false)
  const theme = ref('light')
  const language = ref('zh-CN')
  const pageSize = ref(20)
  const autoSave = ref(true)
  const showTokenStatus = ref(import.meta.env.DEV) // 开发模式默认显示
  const notifications = ref(true)
  const soundEnabled = ref(true)
  
  // 页面状态
  const currentPage = ref('')
  const breadcrumbs = ref([])
  const pageLoading = ref(false)
  
  // 用户偏好设置
  const preferences = ref({
    editor: {
      fontSize: 14,
      theme: 'default',
      autoSave: true,
      autoSaveInterval: 30000 // 30秒
    },
    table: {
      pageSize: 20,
      showBorder: true,
      stripe: true,
      size: 'default'
    },
    form: {
      labelWidth: '120px',
      size: 'default',
      validateOnRuleChange: true
    }
  })

  // 计算属性
  const isDark = computed(() => theme.value === 'dark')
  const isCollapsed = computed(() => sidebarCollapsed.value)
  const currentLanguage = computed(() => language.value)
  
  // 方法
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed) {
    sidebarCollapsed.value = collapsed
  }

  function setTheme(newTheme) {
    theme.value = newTheme
    // 应用主题到document
    document.documentElement.setAttribute('data-theme', newTheme)
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function setLanguage(lang) {
    language.value = lang
    // 这里可以集成i18n
    console.log('语言切换到:', lang)
  }

  function setPageSize(size) {
    pageSize.value = size
  }

  function setCurrentPage(page) {
    currentPage.value = page
  }

  function setBreadcrumbs(crumbs) {
    breadcrumbs.value = crumbs
  }

  function setPageLoading(loading) {
    pageLoading.value = loading
  }

  function toggleTokenStatus() {
    showTokenStatus.value = !showTokenStatus.value
  }

  function setTokenStatusVisible(visible) {
    showTokenStatus.value = visible
  }

  function updatePreference(category, key, value) {
    if (preferences.value[category]) {
      preferences.value[category][key] = value
    }
  }

  function resetPreferences() {
    preferences.value = {
      editor: {
        fontSize: 14,
        theme: 'default',
        autoSave: true,
        autoSaveInterval: 30000
      },
      table: {
        pageSize: 20,
        showBorder: true,
        stripe: true,
        size: 'default'
      },
      form: {
        labelWidth: '120px',
        size: 'default',
        validateOnRuleChange: true
      }
    }
  }

  // 导出配置
  function exportSettings() {
    return {
      theme: theme.value,
      language: language.value,
      pageSize: pageSize.value,
      autoSave: autoSave.value,
      notifications: notifications.value,
      soundEnabled: soundEnabled.value,
      preferences: preferences.value
    }
  }

  // 导入配置
  function importSettings(settings) {
    if (settings.theme) setTheme(settings.theme)
    if (settings.language) setLanguage(settings.language)
    if (settings.pageSize) setPageSize(settings.pageSize)
    if (typeof settings.autoSave === 'boolean') autoSave.value = settings.autoSave
    if (typeof settings.notifications === 'boolean') notifications.value = settings.notifications
    if (typeof settings.soundEnabled === 'boolean') soundEnabled.value = settings.soundEnabled
    if (settings.preferences) preferences.value = { ...preferences.value, ...settings.preferences }
  }

  // 初始化主题
  function initializeTheme() {
    setTheme(theme.value)
  }

  return {
    // 状态
    sidebarCollapsed,
    theme,
    language,
    pageSize,
    autoSave,
    showTokenStatus,
    notifications,
    soundEnabled,
    currentPage,
    breadcrumbs,
    pageLoading,
    preferences,
    
    // 计算属性
    isDark,
    isCollapsed,
    currentLanguage,
    
    // 方法
    toggleSidebar,
    setSidebarCollapsed,
    setTheme,
    setLanguage,
    setPageSize,
    setCurrentPage,
    setBreadcrumbs,
    setPageLoading,
    toggleTokenStatus,
    setTokenStatusVisible,
    updatePreference,
    resetPreferences,
    exportSettings,
    importSettings,
    initializeTheme
  }
}, {
  // 配置持久化
  persist: {
    key: 'app-store',
    storage: localStorage,
    paths: [
      'sidebarCollapsed',
      'theme', 
      'language',
      'pageSize',
      'autoSave',
      'showTokenStatus',
      'notifications',
      'soundEnabled',
      'preferences'
    ],
    beforeRestore: () => {
      console.log('🔄 恢复应用配置...')
    },
    afterRestore: (context) => {
      console.log('✅ 应用配置已恢复')
      // 恢复后初始化主题
      context.store.initializeTheme()
    }
  }
})
