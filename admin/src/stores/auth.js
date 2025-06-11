import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'
import tokenManager from '../utils/tokenManager'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(null)
  const user = ref(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && tokenManager.isTokenValid(token.value))
  
  // 方法
  async function login(credentials) {
    try {
      // 验证输入
      if (!credentials.username?.trim()) {
        throw new Error('用户名不能为空')
      }
      if (!credentials.password) {
        throw new Error('密码不能为空')
      }

      const response = await api.post('/auth/login/json', {
        username: credentials.username.trim(),
        password: credentials.password
      })

      const { access_token } = response.data

      if (!access_token) {
        throw new Error('服务器返回的令牌无效')
      }

      // 设置token（pinia会自动持久化）
      token.value = access_token
      tokenManager.setToken(access_token)

      // 获取用户信息
      await fetchUser()

      // 启动token定时检查
      tokenManager.startPeriodicCheck(api)

      return true
    } catch (error) {
      console.error('登录失败:', error)

      // 清理可能的无效token
      if (token.value) {
        logout()
      }

      throw error
    }
  }
  
  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)

      // 根据错误类型决定是否登出
      if (error.response?.status === 401) {
        // token无效或过期，自动登出
        console.log('Token无效，自动登出')
        logout()
      } else if (error.response?.status === 403) {
        // 账户被禁用
        console.log('账户被禁用，自动登出')
        logout()
      } else {
        // 其他错误，可能是网络问题，不自动登出
        console.log('网络错误，保持登录状态')
      }

      throw error
    }
  }
  
  function logout() {
    token.value = null
    user.value = null
    tokenManager.clearToken()
    tokenManager.stopPeriodicCheck()
  }

  // 刷新token
  async function refreshToken() {
    try {
      const newToken = await tokenManager.refreshToken(api)
      token.value = newToken
      return newToken
    } catch (error) {
      console.error('刷新token失败:', error)
      logout()
      throw error
    }
  }

  // 获取token信息
  function getTokenInfo() {
    return tokenManager.getTokenInfo()
  }
  
  // 初始化函数（由持久化插件的afterRestore调用）
  async function initialize() {
    if (token.value && tokenManager.isTokenValid(token.value)) {
      try {
        await fetchUser()
        console.log('✅ 用户信息获取成功')
      } catch (error) {
        console.log('❌ 获取用户信息失败，清理状态')
        logout()
      }
    }
  }
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    fetchUser,
    logout,
    refreshToken,
    getTokenInfo,
    initialize
  }
}, {
  // 配置持久化
  persist: {
    key: 'auth-store',
    storage: localStorage,
    paths: ['token', 'user'], // 只持久化token和user
    beforeRestore: (context) => {
      console.log('🔄 恢复认证状态...')
    },
    afterRestore: async (context) => {
      console.log('✅ 认证状态已恢复')
      // 恢复后同步token到tokenManager
      if (context.store.token) {
        tokenManager.setToken(context.store.token)
        // 验证token有效性
        if (tokenManager.isTokenValid(context.store.token)) {
          console.log('✅ Token有效，启动定时检查')
          // 启动定时检查
          tokenManager.startPeriodicCheck(api)
          // 初始化用户信息
          await context.store.initialize()
        } else {
          console.log('❌ Token已过期，清理状态')
          // token无效，清理状态
          context.store.token = null
          context.store.user = null
          tokenManager.clearToken()
        }
      }
    }
  }
})
