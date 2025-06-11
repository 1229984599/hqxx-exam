import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useApiStore = defineStore('api', () => {
  // 状态
  const loading = ref(false)
  const requestCount = ref(0)
  const errorCount = ref(0)
  const lastError = ref(null)
  const requestHistory = ref([])

  // 计算属性
  const isLoading = computed(() => loading.value)
  const hasErrors = computed(() => errorCount.value > 0)
  const successRate = computed(() => {
    if (requestCount.value === 0) return 100
    return ((requestCount.value - errorCount.value) / requestCount.value * 100).toFixed(2)
  })

  // 方法
  function startRequest(config) {
    loading.value = true
    requestCount.value++
    
    // 记录请求历史
    const requestInfo = {
      id: Date.now(),
      method: config.method?.toUpperCase() || 'GET',
      url: config.url,
      timestamp: new Date(),
      status: 'pending'
    }
    
    requestHistory.value.unshift(requestInfo)
    
    // 只保留最近50条记录
    if (requestHistory.value.length > 50) {
      requestHistory.value = requestHistory.value.slice(0, 50)
    }
    
    return requestInfo.id
  }

  function finishRequest(requestId, success = true, error = null) {
    loading.value = false
    
    if (!success) {
      errorCount.value++
      lastError.value = {
        message: error?.message || '未知错误',
        timestamp: new Date(),
        details: error
      }
    }
    
    // 更新请求历史
    const request = requestHistory.value.find(r => r.id === requestId)
    if (request) {
      request.status = success ? 'success' : 'error'
      request.error = error
      request.duration = Date.now() - request.timestamp.getTime()
    }
  }

  function clearHistory() {
    requestHistory.value = []
    errorCount.value = 0
    lastError.value = null
  }

  function clearError() {
    lastError.value = null
  }

  // API方法封装
  async function get(url, config = {}) {
    const requestId = startRequest({ method: 'GET', url, ...config })
    try {
      const response = await api.get(url, config)
      finishRequest(requestId, true)
      return response
    } catch (error) {
      finishRequest(requestId, false, error)
      throw error
    }
  }

  async function post(url, data, config = {}) {
    const requestId = startRequest({ method: 'POST', url, ...config })
    try {
      const response = await api.post(url, data, config)
      finishRequest(requestId, true)
      return response
    } catch (error) {
      finishRequest(requestId, false, error)
      throw error
    }
  }

  async function put(url, data, config = {}) {
    const requestId = startRequest({ method: 'PUT', url, ...config })
    try {
      const response = await api.put(url, data, config)
      finishRequest(requestId, true)
      return response
    } catch (error) {
      finishRequest(requestId, false, error)
      throw error
    }
  }

  async function del(url, config = {}) {
    const requestId = startRequest({ method: 'DELETE', url, ...config })
    try {
      const response = await api.delete(url, config)
      finishRequest(requestId, true)
      return response
    } catch (error) {
      finishRequest(requestId, false, error)
      throw error
    }
  }

  async function patch(url, data, config = {}) {
    const requestId = startRequest({ method: 'PATCH', url, ...config })
    try {
      const response = await api.patch(url, data, config)
      finishRequest(requestId, true)
      return response
    } catch (error) {
      finishRequest(requestId, false, error)
      throw error
    }
  }

  // 批量请求
  async function batch(requests) {
    const promises = requests.map(req => {
      const { method, url, data, config } = req
      switch (method.toLowerCase()) {
        case 'get':
          return get(url, config)
        case 'post':
          return post(url, data, config)
        case 'put':
          return put(url, data, config)
        case 'delete':
          return del(url, config)
        case 'patch':
          return patch(url, data, config)
        default:
          throw new Error(`不支持的请求方法: ${method}`)
      }
    })

    try {
      const results = await Promise.allSettled(promises)
      return results
    } catch (error) {
      console.error('批量请求失败:', error)
      throw error
    }
  }

  // 重试请求
  async function retry(requestId) {
    const request = requestHistory.value.find(r => r.id === requestId)
    if (!request) {
      throw new Error('请求记录不存在')
    }

    // 重新发起请求
    return get(request.url)
  }

  return {
    // 状态
    loading,
    requestCount,
    errorCount,
    lastError,
    requestHistory,
    
    // 计算属性
    isLoading,
    hasErrors,
    successRate,
    
    // 方法
    startRequest,
    finishRequest,
    clearHistory,
    clearError,
    
    // API方法
    get,
    post,
    put,
    delete: del,
    patch,
    batch,
    retry,
    
    // 原始api实例（用于特殊情况）
    api
  }
}, {
  // 配置持久化
  persist: {
    key: 'api-store',
    storage: sessionStorage, // 使用sessionStorage，关闭浏览器后清除
    paths: ['requestCount', 'errorCount'], // 只持久化统计数据
    beforeRestore: () => {
      console.log('🔄 恢复API状态...')
    },
    afterRestore: () => {
      console.log('✅ API状态已恢复')
    }
  }
})
