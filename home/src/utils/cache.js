/**
 * 前端缓存工具
 */

class CacheManager {
  constructor() {
    this.cache = new Map()
    this.ttl = new Map()
    this.defaultTTL = 5 * 60 * 1000 // 5分钟默认过期时间
  }

  /**
   * 生成缓存键
   * @param {string} key 
   * @param {object} params 
   * @returns {string}
   */
  generateKey(key, params = {}) {
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((result, key) => {
        result[key] = params[key]
        return result
      }, {})
    
    return `${key}:${JSON.stringify(sortedParams)}`
  }

  /**
   * 设置缓存
   * @param {string} key 
   * @param {any} data 
   * @param {number} ttl 过期时间（毫秒）
   */
  set(key, data, ttl = this.defaultTTL) {
    const cacheKey = typeof key === 'string' ? key : this.generateKey(key.endpoint, key.params)
    const expireTime = Date.now() + ttl
    
    this.cache.set(cacheKey, data)
    this.ttl.set(cacheKey, expireTime)
    
    // 清理过期缓存
    this.cleanup()
  }

  /**
   * 获取缓存
   * @param {string|object} key 
   * @returns {any|null}
   */
  get(key) {
    const cacheKey = typeof key === 'string' ? key : this.generateKey(key.endpoint, key.params)
    
    if (!this.cache.has(cacheKey)) {
      return null
    }

    const expireTime = this.ttl.get(cacheKey)
    if (Date.now() > expireTime) {
      // 缓存已过期
      this.cache.delete(cacheKey)
      this.ttl.delete(cacheKey)
      return null
    }

    return this.cache.get(cacheKey)
  }

  /**
   * 删除缓存
   * @param {string|object} key
   */
  delete(key) {
    const cacheKey = typeof key === 'string' ? key : this.generateKey(key.endpoint, key.params)
    this.cache.delete(cacheKey)
    this.ttl.delete(cacheKey)
  }

  /**
   * 删除匹配模式的缓存
   * @param {string} pattern 匹配模式
   */
  deleteByPattern(pattern) {
    const keys = Array.from(this.cache.keys())
    let deletedCount = 0

    keys.forEach(key => {
      if (key.includes(pattern)) {
        this.cache.delete(key)
        this.ttl.delete(key)
        deletedCount++
      }
    })

    console.log(`Deleted ${deletedCount} cache entries matching pattern: ${pattern}`)
    return deletedCount
  }

  /**
   * 清空所有缓存
   */
  clear() {
    this.cache.clear()
    this.ttl.clear()
  }

  /**
   * 清理过期缓存
   */
  cleanup() {
    const now = Date.now()
    for (const [key, expireTime] of this.ttl.entries()) {
      if (now > expireTime) {
        this.cache.delete(key)
        this.ttl.delete(key)
      }
    }
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    }
  }

  /**
   * 缓存装饰器 - 用于API调用
   * @param {Function} apiFunction 
   * @param {string} cacheKey 
   * @param {number} ttl 
   * @returns {Function}
   */
  withCache(apiFunction, cacheKey, ttl = this.defaultTTL) {
    return async (...args) => {
      const key = this.generateKey(cacheKey, args[0] || {})
      
      // 尝试从缓存获取
      const cached = this.get(key)
      if (cached) {
        console.log(`Cache hit for ${key}`)
        return cached
      }

      // 调用API
      try {
        const result = await apiFunction(...args)
        this.set(key, result, ttl)
        console.log(`Cache set for ${key}`)
        return result
      } catch (error) {
        console.error(`API call failed for ${key}:`, error)
        throw error
      }
    }
  }
}

// 创建全局缓存实例
const cacheManager = new CacheManager()

// 定期清理过期缓存（每分钟）
setInterval(() => {
  cacheManager.cleanup()
}, 60 * 1000)

export default cacheManager

/**
 * 缓存装饰器函数
 * @param {string} key 缓存键
 * @param {number} ttl 过期时间（毫秒）
 */
export function cached(key, ttl = 5 * 60 * 1000) {
  return function(target, propertyName, descriptor) {
    const method = descriptor.value
    descriptor.value = cacheManager.withCache(method, key, ttl)
    return descriptor
  }
}

/**
 * 清除指定模式的缓存
 * @param {string} pattern 缓存键模式
 */
export function clearCacheByPattern(pattern) {
  const keys = Array.from(cacheManager.cache.keys())
  keys.forEach(key => {
    if (key.includes(pattern)) {
      cacheManager.delete(key)
    }
  })
}
