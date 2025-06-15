import axios from 'axios'
import { ElMessage } from 'element-plus'
import tokenManager from './tokenManager'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage直接获取token（避免循环依赖）
    try {
      const authData = localStorage.getItem('auth-store')
      if (authData) {
        const parsedData = JSON.parse(authData)
        const token = parsedData.token
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
          console.log('✅ Token已添加到请求头')
        } else {
          console.warn('⚠️ 未找到token')
        }
      } else {
        console.warn('⚠️ 未找到认证数据')
      }
    } catch (error) {
      console.error('❌ 获取token失败:', error)
    }

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API请求错误:', error)

    // 网络错误
    if (!error.response) {
      if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        ElMessage.error('网络连接失败，请检查网络连接')
      } else if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请稍后重试')
      } else {
        ElMessage.error('网络错误，请检查网络连接')
      }
      return Promise.reject(error)
    }

    const { status, data } = error.response
    const currentPath = window.location.pathname

    // 处理不同状态码
    switch (status) {
      case 400:
        // 请求参数错误，显示具体错误信息
        if (data?.detail) {
          // 登录页面的错误不在这里处理，让登录页面自己处理
          if (!currentPath.includes('/login')) {
            ElMessage.error(data.detail)
          }
        } else {
          if (!currentPath.includes('/login')) {
            ElMessage.error('请求参数错误')
          }
        }
        break

      case 401:
        // 未授权，token无效或过期
        if (data?.detail) {
          if (!currentPath.includes('/login')) {
            ElMessage.error(data.detail)
            // 清除token并跳转到登录页
            localStorage.removeItem('auth-store')
            setTimeout(() => {
              window.location.href = '/login'
            }, 1500)
          }
        } else {
          if (!currentPath.includes('/login')) {
            ElMessage.error('登录已过期，请重新登录')
            // 清除token并跳转到登录页
            localStorage.removeItem('auth-store')
            setTimeout(() => {
              window.location.href = '/login'
            }, 1500)
          }
        }
        break

      case 403:
        // 权限不足
        if (data?.detail) {
          ElMessage.error(data.detail)
        } else {
          ElMessage.error('权限不足，无法执行此操作')
        }
        break

      case 404:
        ElMessage.error('请求的资源不存在')
        break

      case 422:
        // 数据验证错误
        if (data?.detail) {
          if (Array.isArray(data.detail)) {
            // FastAPI验证错误格式
            const errors = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('; ')
            ElMessage.error(`数据验证失败: ${errors}`)
          } else {
            ElMessage.error(data.detail)
          }
        } else {
          ElMessage.error('数据验证失败')
        }
        break

      case 500:
        ElMessage.error('服务器内部错误，请稍后重试')
        break

      case 502:
        ElMessage.error('网关错误，请稍后重试')
        break

      case 503:
        ElMessage.error('服务暂时不可用，请稍后重试')
        break

      default:
        if (data?.detail) {
          ElMessage.error(data.detail)
        } else {
          ElMessage.error(`请求失败 (${status})`)
        }
    }

    return Promise.reject(error)
  }
)

export default api
