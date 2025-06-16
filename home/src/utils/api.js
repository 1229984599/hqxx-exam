import axios from 'axios'
import cacheManager from './cache.js'

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
    // 前台页面暂时不需要认证token
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API请求错误:', error)
    if (error.response?.data?.detail) {
      console.error('错误详情:', error.response.data.detail)
    }
    return Promise.reject(error)
  }
)

// 带缓存的API调用函数
const cachedApiCall = (endpoint, params = {}, ttl = 5 * 60 * 1000) => {
  // 检查是否有强制刷新标识
  const forceRefresh = params._t !== undefined
  const cacheKey = cacheManager.generateKey(endpoint, params)

  // 如果不是强制刷新，尝试从缓存获取
  if (!forceRefresh) {
    const cached = cacheManager.get(cacheKey)
    if (cached) {
      console.log(`Cache hit for ${endpoint}`)
      return Promise.resolve(cached)
    }
  } else {
    console.log(`Force refresh for ${endpoint}, bypassing cache`)
    // 强制刷新时清除相关缓存
    cacheManager.delete(cacheKey)
  }

  // 调用API
  return api.get(endpoint, { params }).then(response => {
    // 缓存响应数据
    cacheManager.set(cacheKey, response, ttl)
    console.log(`${forceRefresh ? 'Force refreshed and cached' : 'Cache set'} for ${endpoint}`)
    return response
  })
}

// API方法 - 使用公开接口和缓存
export const apiService = {
  // 获取学期列表（缓存5分钟）
  getSemesters: (params = {}) => cachedApiCall('/public/semesters/', { only_active_time: true, ...params }, 5 * 60 * 1000),

  // 获取年级列表（缓存5分钟）
  getGrades: (params = {}) => cachedApiCall('/public/grades/', params, 5 * 60 * 1000),

  // 获取学科列表（缓存5分钟）
  getSubjects: (params = {}) => cachedApiCall('/public/subjects/', params, 5 * 60 * 1000),

  // 获取分类列表（缓存3分钟，因为可能根据学科变化）
  getCategories: (params = {}) => cachedApiCall('/public/categories/', params, 3 * 60 * 1000),

  // 获取试题列表（缓存2分钟）
  getQuestions: (params = {}) => cachedApiCall('/public/questions/', params, 2 * 60 * 1000),

  // 随机获取试题（不缓存，保证随机性）
  getRandomQuestion: (params = {}) => api.get('/public/questions/random', { params }),

  // 获取试题详情（暂时保留原路径，如需要可以添加到公开接口）
  getQuestion: (id) => api.get(`/questions/${id}`),

  // 检查学期状态（不缓存，确保实时性）
  checkSemesterStatus: (semesterId) => api.get(`/public/semesters/${semesterId}/status`)
}

// 缓存管理工具
export const cacheUtils = {
  // 清除所有缓存
  clearAll: () => cacheManager.clear(),

  // 清除特定模式的缓存
  clearPattern: (pattern) => {
    const keys = Array.from(cacheManager.cache.keys())
    keys.forEach(key => {
      if (key.includes(pattern)) {
        cacheManager.delete(key)
      }
    })
  },

  // 获取缓存统计
  getStats: () => cacheManager.getStats(),

  // 手动设置缓存
  set: (key, data, ttl) => cacheManager.set(key, data, ttl),

  // 手动获取缓存
  get: (key) => cacheManager.get(key)
}

export default api
