import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'
import tokenManager from '../utils/tokenManager'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(null)
  const user = ref(null)
  const permissions = ref([])
  const roles = ref([])

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && tokenManager.isTokenValid(token.value))
  const isSuperuser = computed(() => user.value?.is_superuser || false)
  
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

      // 设置token（只通过pinia管理，移除重复设置）
      token.value = access_token

      // 获取用户信息
      await fetchUser()

      // 获取用户权限
      await fetchPermissions()

      // 启动token定时检查（传入token获取函数）
      tokenManager.startPeriodicCheck(api, () => token.value)

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

  async function fetchPermissions() {
    try {
      const response = await api.get('/auth/permissions')
      permissions.value = response.data.permissions || []
      roles.value = response.data.roles || []
      console.log('✅ 权限信息已获取:', { permissions: permissions.value, roles: roles.value })
    } catch (error) {
      console.error('获取权限信息失败:', error)
      permissions.value = []
      roles.value = []

      // 权限获取失败不影响登录状态，但需要记录错误
      if (error.response?.status === 401) {
        console.log('Token无效，自动登出')
        logout()
      }
    }
  }
  
  function logout() {
    token.value = null
    user.value = null
    permissions.value = []
    roles.value = []
    tokenManager.stopPeriodicCheck()
  }

  // 刷新token
  async function refreshToken() {
    try {
      const newToken = await tokenManager.refreshToken(api, token.value)
      token.value = newToken
      return newToken
    } catch (error) {
      console.error('刷新token失败:', error)
      logout()
      throw error
    }
  }

  // 更新用户信息
  function updateUser(userData) {
    if (user.value) {
      Object.assign(user.value, userData)
    }
  }

  // 基于角色的权限检查方法（RBAC核心）
  function hasRole(roleCode) {
    if (!roleCode) return true
    if (isSuperuser.value) return true
    return roles.value.some(role => role.code === roleCode)
  }

  function hasAnyRole(roleCodes) {
    if (!roleCodes || roleCodes.length === 0) return true
    if (isSuperuser.value) return true
    return roleCodes.some(roleCode => hasRole(roleCode))
  }

  function hasAllRoles(roleCodes) {
    if (!roleCodes || roleCodes.length === 0) return true
    if (isSuperuser.value) return true
    return roleCodes.every(roleCode => hasRole(roleCode))
  }

  // 基于权限的检查方法（细粒度权限控制）
  function hasPermission(permission) {
    if (!permission) return true
    if (isSuperuser.value) return true
    if (permissions.value.includes('*')) return true
    return permissions.value.includes(permission)
  }

  function hasAnyPermission(permissionList) {
    if (!permissionList || permissionList.length === 0) return true
    if (isSuperuser.value) return true
    if (permissions.value.includes('*')) return true
    return permissionList.some(permission => permissions.value.includes(permission))
  }

  function hasAllPermissions(permissionList) {
    if (!permissionList || permissionList.length === 0) return true
    if (isSuperuser.value) return true
    if (permissions.value.includes('*')) return true
    return permissionList.every(permission => permissions.value.includes(permission))
  }

  // 获取token信息
  function getTokenInfo() {
    return tokenManager.getTokenInfo(token.value)
  }

  // 初始化函数（由持久化插件的afterRestore调用）
  async function initialize() {
    if (token.value && tokenManager.isTokenValid(token.value)) {
      try {
        await fetchUser()
        await fetchPermissions()
        console.log('✅ 用户信息和权限获取成功')
      } catch (error) {
        console.log('❌ 获取用户信息失败，清理状态')
        logout()
      }
    }
  }
  
  return {
    // 状态
    token,
    user,
    permissions,
    roles,
    // 计算属性
    isAuthenticated,
    isSuperuser,
    // 方法
    login,
    fetchUser,
    fetchPermissions,
    logout,
    refreshToken,
    updateUser,
    getTokenInfo,
    initialize,
    // 角色检查方法（RBAC核心）
    hasRole,
    hasAnyRole,
    hasAllRoles,
    // 权限检查方法（细粒度控制）
    hasPermission,
    hasAnyPermission,
    hasAllPermissions
  }
}, {
  // 配置持久化
  persist: {
    key: 'auth-store',
    storage: localStorage,
    paths: ['token', 'user', 'permissions', 'roles'], // 持久化认证和权限信息
    beforeRestore: (context) => {
      console.log('🔄 恢复认证状态...')
    },
    afterRestore: async (context) => {
      console.log('✅ 认证状态已恢复')
      // 验证token有效性
      if (context.store.token) {
        if (tokenManager.isTokenValid(context.store.token)) {
          console.log('✅ Token有效，启动定时检查')
          // 启动定时检查（传入token获取函数）
          tokenManager.startPeriodicCheck(api, () => context.store.token)
          // 初始化用户信息
          await context.store.initialize()
        } else {
          console.log('❌ Token已过期，清理状态')
          // token无效，清理状态
          context.store.token = null
          context.store.user = null
          context.store.permissions = []
          context.store.roles = []
        }
      }
    }
  }
})
