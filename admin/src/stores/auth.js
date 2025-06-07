import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('admin_token') || null)
  const user = ref(null)
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  
  // 方法
  async function login(credentials) {
    try {
      const response = await api.post('/auth/login/json', credentials)
      const { access_token } = response.data
      
      token.value = access_token
      localStorage.setItem('admin_token', access_token)
      
      // 获取用户信息
      await fetchUser()
      
      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }
  
  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
    }
  }
  
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('admin_token')
  }
  
  // 初始化时获取用户信息
  if (token.value) {
    fetchUser()
  }
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    fetchUser,
    logout
  }
})
