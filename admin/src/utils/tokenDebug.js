/**
 * Token调试工具
 * 用于检查token的存储和传输状态
 */

export function debugTokenStatus() {
  console.log('🔍 Token状态调试:')
  
  try {
    // 检查localStorage中的认证数据
    const authData = localStorage.getItem('auth-store')
    if (authData) {
      const parsedData = JSON.parse(authData)
      console.log('📦 localStorage中的认证数据:', {
        hasToken: !!parsedData.token,
        tokenLength: parsedData.token?.length || 0,
        hasUser: !!parsedData.user,
        username: parsedData.user?.username || 'N/A'
      })
      
      if (parsedData.token) {
        // 解析token
        try {
          const parts = parsedData.token.split('.')
          if (parts.length === 3) {
            const payload = JSON.parse(atob(parts[1]))
            const now = Math.floor(Date.now() / 1000)
            console.log('🔑 Token信息:', {
              username: payload.sub,
              issuedAt: new Date(payload.iat * 1000).toLocaleString(),
              expiresAt: new Date(payload.exp * 1000).toLocaleString(),
              isExpired: payload.exp < now,
              timeUntilExpiry: payload.exp - now + ' 秒'
            })
          } else {
            console.error('❌ Token格式错误')
          }
        } catch (error) {
          console.error('❌ Token解析失败:', error)
        }
      } else {
        console.warn('⚠️ 未找到token')
      }
    } else {
      console.warn('⚠️ localStorage中没有认证数据')
    }
    
    // 检查pinia store状态
    try {
      const { useAuthStore } = require('../stores/auth')
      const authStore = useAuthStore()
      console.log('🏪 Pinia Store状态:', {
        hasToken: !!authStore.token,
        hasUser: !!authStore.user,
        isAuthenticated: authStore.isAuthenticated
      })
    } catch (error) {
      console.warn('⚠️ 无法访问Pinia Store:', error.message)
    }
    
  } catch (error) {
    console.error('❌ Token状态检查失败:', error)
  }
}

export function testApiRequest() {
  console.log('🧪 测试API请求...')
  
  import('../utils/api').then(({ default: api }) => {
    api.get('/auth/me')
      .then(response => {
        console.log('✅ API请求成功:', response.data)
      })
      .catch(error => {
        console.error('❌ API请求失败:', error.response?.data || error.message)
        
        // 检查请求头
        if (error.config?.headers?.Authorization) {
          console.log('🔑 请求携带的Authorization头:', error.config.headers.Authorization)
        } else {
          console.error('❌ 请求未携带Authorization头')
        }
      })
  })
}

// 在控制台中可以调用的调试函数
window.debugToken = debugTokenStatus
window.testApi = testApiRequest
