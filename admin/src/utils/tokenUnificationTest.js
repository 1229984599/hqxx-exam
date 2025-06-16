/**
 * Token统一管理测试工具
 * 用于验证token管理的统一性和自动刷新功能
 */

export function testTokenUnification() {
  console.log('🧪 开始Token统一管理测试...')
  
  try {
    // 1. 检查auth store是否正常工作
    const { useAuthStore } = require('../stores/auth')
    const authStore = useAuthStore()
    
    console.log('📊 Auth Store状态:')
    console.log('- 是否已认证:', authStore.isAuthenticated)
    console.log('- Token存在:', !!authStore.token)
    console.log('- 用户信息:', authStore.user?.username || 'N/A')
    
    // 2. 检查localStorage中的数据
    const authData = localStorage.getItem('auth-store')
    if (authData) {
      const parsedData = JSON.parse(authData)
      console.log('💾 localStorage数据:')
      console.log('- Token存在:', !!parsedData.token)
      console.log('- 用户信息:', parsedData.user?.username || 'N/A')
      
      // 3. 验证两者是否一致
      const storeToken = authStore.token
      const localToken = parsedData.token
      
      if (storeToken === localToken) {
        console.log('✅ Auth Store和localStorage中的token一致')
      } else {
        console.warn('⚠️ Auth Store和localStorage中的token不一致')
        console.log('Store token:', storeToken?.substring(0, 20) + '...')
        console.log('Local token:', localToken?.substring(0, 20) + '...')
      }
    } else {
      console.warn('⚠️ localStorage中没有认证数据')
    }
    
    // 4. 检查token管理器状态
    const tokenManager = require('./tokenManager').default
    if (authStore.token) {
      const tokenInfo = tokenManager.getTokenInfo(authStore.token)
      console.log('🔑 Token信息:')
      console.log('- 有效性:', tokenInfo.valid)
      console.log('- 过期时间:', tokenInfo.expiresAt)
      console.log('- 剩余时间:', tokenInfo.timeUntilExpiry)
    }
    
    // 5. 测试API请求中的token使用
    console.log('🌐 测试API token使用...')
    testApiTokenUsage()
    
    console.log('✅ Token统一管理测试完成')
    
  } catch (error) {
    console.error('❌ Token统一管理测试失败:', error)
  }
}

function testApiTokenUsage() {
  console.log('🧪 测试API token使用...')

  try {
    // 检查API模块是否正确设置了auth store
    const api = require('./api')

    // 模拟一个API请求来测试token获取
    const mockConfig = {
      headers: {},
      url: '/test',
      method: 'GET'
    }

    // 获取请求拦截器
    const interceptors = api.default.interceptors.request.handlers
    if (interceptors && interceptors.length > 0) {
      const requestInterceptor = interceptors[0].fulfilled

      // 执行拦截器
      const result = requestInterceptor(mockConfig)

      if (result.headers.Authorization) {
        console.log('✅ API请求中正确添加了Authorization头')
        console.log('- Authorization:', result.headers.Authorization.substring(0, 30) + '...')

        // 检查控制台输出来确定token来源
        console.log('📝 请查看上方日志确认token来源（应该显示"从auth-store获取token"）')
      } else {
        console.warn('⚠️ API请求中没有Authorization头')
      }
    } else {
      console.warn('⚠️ 未找到请求拦截器')
    }
  } catch (error) {
    console.error('❌ 测试API token使用失败:', error)
  }
}

/**
 * 测试token自动刷新功能
 */
export function testTokenAutoRefresh() {
  console.log('🔄 测试Token自动刷新功能...')
  
  try {
    const { useAuthStore } = require('../stores/auth')
    const authStore = useAuthStore()
    
    if (!authStore.isAuthenticated) {
      console.warn('⚠️ 用户未登录，无法测试token刷新')
      return
    }
    
    console.log('🧪 手动触发token刷新测试...')
    authStore.refreshToken()
      .then(() => {
        console.log('✅ Token刷新成功')
        // 再次检查token统一性
        setTimeout(() => {
          testTokenUnification()
        }, 1000)
      })
      .catch(error => {
        console.error('❌ Token刷新失败:', error)
      })
      
  } catch (error) {
    console.error('❌ Token自动刷新测试失败:', error)
  }
}

/**
 * 清理测试环境
 */
export function cleanupTokenTest() {
  console.log('🧹 清理Token测试环境...')
  
  // 这里可以添加清理逻辑，比如重置某些状态
  console.log('✅ 清理完成')
}

// 在开发环境下自动运行测试
if (process.env.NODE_ENV === 'development') {
  // 延迟执行，确保应用已初始化
  setTimeout(() => {
    if (window.location.pathname !== '/login') {
      testTokenUnification()
    }
  }, 2000)
}
