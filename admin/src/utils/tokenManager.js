/**
 * Token管理工具
 * 提供token的存储、验证、刷新等功能
 */

import { ElMessage } from 'element-plus'

class TokenManager {
  constructor() {
    this.refreshPromise = null // 防止并发刷新
    this.isRefreshing = false
    this.refreshThreshold = 5 * 60 * 1000 // 5分钟（毫秒）
    this.getTokenCallback = null // token获取回调函数
  }

  /**
   * 获取token（通过回调函数）
   */
  getToken() {
    return this.getTokenCallback ? this.getTokenCallback() : null
  }

  /**
   * 解析JWT token
   */
  parseJWT(token) {
    try {
      if (!token) return null
      
      const parts = (token || '').split('.')
      if (parts.length !== 3) return null
      
      const payload = parts[1]
      const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
      return decoded
    } catch (error) {
      console.error('解析JWT失败:', error)
      return null
    }
  }

  /**
   * 获取token过期时间
   */
  getTokenExpiry(token = null) {
    const targetToken = token || this.getToken()
    if (!targetToken) return null

    const payload = this.parseJWT(targetToken)
    if (!payload || !payload.exp) return null

    return new Date(payload.exp * 1000)
  }

  /**
   * 检查token是否有效
   */
  isTokenValid(token = null) {
    const targetToken = token || this.getToken()
    if (!targetToken) return false

    const expiry = this.getTokenExpiry(targetToken)
    if (!expiry) return false

    return expiry > new Date()
  }

  /**
   * 检查token是否即将过期
   */
  isTokenExpiringSoon(token = null, thresholdMs = null) {
    const targetToken = token || this.getToken()
    if (!targetToken) return true

    const expiry = this.getTokenExpiry(targetToken)
    if (!expiry) return true

    const threshold = thresholdMs || this.refreshThreshold
    const timeUntilExpiry = expiry.getTime() - Date.now()

    return timeUntilExpiry <= threshold
  }

  /**
   * 获取token剩余有效时间（毫秒）
   */
  getTokenRemainingTime(token = null) {
    const targetToken = token || this.getToken()
    if (!targetToken) return 0

    const expiry = this.getTokenExpiry(targetToken)
    if (!expiry) return 0

    const remaining = expiry.getTime() - Date.now()
    return Math.max(0, remaining)
  }

  /**
   * 刷新token
   */
  async refreshToken(api, currentToken) {
    // 防止并发刷新
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise
    }

    this.isRefreshing = true
    this.refreshPromise = this._doRefreshToken(api, currentToken)

    try {
      const result = await this.refreshPromise
      return result
    } finally {
      this.isRefreshing = false
      this.refreshPromise = null
    }
  }

  /**
   * 执行token刷新
   */
  async _doRefreshToken(api, currentToken) {
    try {
      console.log('🔄 开始刷新token...')

      const response = await api.post('/auth/refresh')
      const { access_token } = response.data

      if (!access_token) {
        throw new Error('服务器返回的新token无效')
      }

      console.log('✅ Token刷新成功')
      return access_token
    } catch (error) {
      console.error('❌ Token刷新失败:', error)

      // 根据错误类型给出不同提示
      if (error.response?.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        setTimeout(() => {
          window.location.href = '/login'
        }, 1500)
      } else if (error.response?.status === 403) {
        ElMessage.error('账户已被禁用，请联系管理员')
        setTimeout(() => {
          window.location.href = '/login'
        }, 1500)
      } else {
        ElMessage.error('自动续期失败，请重新登录')
        setTimeout(() => {
          window.location.href = '/login'
        }, 1500)
      }

      throw error
    }
  }

  /**
   * 检查并自动刷新token
   */
  async checkAndRefreshToken(api, currentToken) {
    if (!currentToken) {
      return false
    }

    // 如果token无效，直接返回false
    if (!this.isTokenValid(currentToken)) {
      console.log('Token已过期，需要重新登录')
      return false
    }

    // 如果token即将过期，尝试刷新
    if (this.isTokenExpiringSoon(currentToken)) {
      try {
        const newToken = await this.refreshToken(api, currentToken)
        return newToken
      } catch (error) {
        return false
      }
    }

    return true
  }

  /**
   * 启动定时检查
   */
  startPeriodicCheck(api, getTokenCallback, updateTokenCallback, intervalMs = 60000) { // 默认每分钟检查一次
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
    }

    // 保存token获取回调
    this.getTokenCallback = getTokenCallback

    this.checkInterval = setInterval(async () => {
      try {
        const currentToken = getTokenCallback()
        const result = await this.checkAndRefreshToken(api, currentToken)

        // 如果返回了新token，通知外部更新
        if (typeof result === 'string') {
          console.log('🔄 Token已自动刷新，更新到store中')
          if (updateTokenCallback && typeof updateTokenCallback === 'function') {
            updateTokenCallback(result)
          }
        }
      } catch (error) {
        console.error('定时token检查失败:', error)
      }
    }, intervalMs)

    console.log('🕐 启动token定时检查，间隔:', intervalMs / 1000, '秒')
  }

  /**
   * 停止定时检查
   */
  stopPeriodicCheck() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
      this.getTokenCallback = null
      console.log('⏹️ 停止token定时检查')
    }
  }

  /**
   * 获取token信息（用于调试）
   */
  getTokenInfo(token = null) {
    const targetToken = token || this.getToken()
    if (!targetToken) {
      return { valid: false, message: 'No token found' }
    }

    const payload = this.parseJWT(targetToken)
    if (!payload) {
      return { valid: false, message: 'Invalid token format' }
    }

    const expiry = this.getTokenExpiry(targetToken)
    const isValid = this.isTokenValid(targetToken)
    const isExpiringSoon = this.isTokenExpiringSoon(targetToken)
    const remainingTime = this.getTokenRemainingTime(targetToken)

    return {
      valid: isValid,
      expiry: expiry,
      isExpiringSoon: isExpiringSoon,
      remainingTime: remainingTime,
      remainingTimeFormatted: this.formatTime(remainingTime),
      username: payload.sub,
      payload: payload
    }
  }

  /**
   * 格式化时间
   */
  formatTime(ms) {
    if (ms <= 0) return '已过期'
    
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (days > 0) return `${days}天${hours % 24}小时`
    if (hours > 0) return `${hours}小时${minutes % 60}分钟`
    if (minutes > 0) return `${minutes}分钟${seconds % 60}秒`
    return `${seconds}秒`
  }
}

// 创建单例实例
const tokenManager = new TokenManager()

export default tokenManager
