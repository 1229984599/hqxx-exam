/**
 * 性能监控工具
 */

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.observers = []
    this.isEnabled = import.meta.env.DEV || localStorage.getItem('performance-monitor') === 'true'
  }

  /**
   * 启用性能监控
   */
  enable() {
    this.isEnabled = true
    localStorage.setItem('performance-monitor', 'true')
    this.startObserving()
  }

  /**
   * 禁用性能监控
   */
  disable() {
    this.isEnabled = false
    localStorage.removeItem('performance-monitor')
    this.stopObserving()
  }

  /**
   * 开始性能计时
   */
  startTiming(name) {
    if (!this.isEnabled) return

    this.metrics.set(name, {
      startTime: performance.now(),
      endTime: null,
      duration: null
    })
  }

  /**
   * 结束性能计时
   */
  endTiming(name) {
    if (!this.isEnabled) return

    const metric = this.metrics.get(name)
    if (metric) {
      metric.endTime = performance.now()
      metric.duration = metric.endTime - metric.startTime
      
      if (import.meta.env.DEV) {
        console.log(`⏱️ ${name}: ${metric.duration.toFixed(2)}ms`)
      }
    }
  }

  /**
   * 测量函数执行时间
   */
  async measureFunction(name, fn) {
    if (!this.isEnabled) return await fn()

    this.startTiming(name)
    try {
      const result = await fn()
      this.endTiming(name)
      return result
    } catch (error) {
      this.endTiming(name)
      throw error
    }
  }

  /**
   * 测量API请求时间
   */
  measureApiRequest(url, method = 'GET') {
    if (!this.isEnabled) return

    const name = `API ${method} ${url}`
    this.startTiming(name)
    
    return {
      end: () => this.endTiming(name)
    }
  }

  /**
   * 获取性能指标
   */
  getMetrics() {
    const result = {}
    for (const [name, metric] of this.metrics) {
      if (metric.duration !== null) {
        result[name] = {
          duration: metric.duration,
          startTime: metric.startTime,
          endTime: metric.endTime
        }
      }
    }
    return result
  }

  /**
   * 清除性能指标
   */
  clearMetrics() {
    this.metrics.clear()
  }

  /**
   * 获取页面性能信息
   */
  getPagePerformance() {
    if (!window.performance || !window.performance.timing) {
      return null
    }

    const timing = window.performance.timing
    const navigation = window.performance.navigation

    return {
      // 页面加载时间
      pageLoadTime: timing.loadEventEnd - timing.navigationStart,
      // DNS查询时间
      dnsTime: timing.domainLookupEnd - timing.domainLookupStart,
      // TCP连接时间
      tcpTime: timing.connectEnd - timing.connectStart,
      // 请求时间
      requestTime: timing.responseEnd - timing.requestStart,
      // 解析DOM树时间
      domParseTime: timing.domComplete - timing.domLoading,
      // 白屏时间
      whiteScreenTime: timing.responseStart - timing.navigationStart,
      // 首屏时间
      firstScreenTime: timing.loadEventEnd - timing.navigationStart,
      // 导航类型
      navigationType: navigation.type,
      // 重定向次数
      redirectCount: navigation.redirectCount
    }
  }

  /**
   * 监控资源加载性能
   */
  getResourcePerformance() {
    if (!window.performance || !window.performance.getEntriesByType) {
      return []
    }

    const resources = window.performance.getEntriesByType('resource')
    return resources.map(resource => ({
      name: resource.name,
      type: resource.initiatorType,
      size: resource.transferSize,
      duration: resource.duration,
      startTime: resource.startTime,
      endTime: resource.responseEnd
    }))
  }

  /**
   * 开始观察性能
   */
  startObserving() {
    if (!this.isEnabled) return

    // 观察长任务
    if ('PerformanceObserver' in window) {
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) { // 超过50ms的任务
              console.warn(`🐌 Long task detected: ${entry.duration.toFixed(2)}ms`)
            }
          }
        })
        longTaskObserver.observe({ entryTypes: ['longtask'] })
        this.observers.push(longTaskObserver)
      } catch (error) {
        console.warn('Long task observer not supported')
      }

      // 观察导航性能
      try {
        const navigationObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            console.log('📊 Navigation performance:', {
              domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
              loadComplete: entry.loadEventEnd - entry.loadEventStart,
              totalTime: entry.loadEventEnd - entry.fetchStart
            })
          }
        })
        navigationObserver.observe({ entryTypes: ['navigation'] })
        this.observers.push(navigationObserver)
      } catch (error) {
        console.warn('Navigation observer not supported')
      }

      // 观察资源加载
      try {
        const resourceObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 1000) { // 超过1秒的资源加载
              console.warn(`🐌 Slow resource: ${entry.name} (${entry.duration.toFixed(2)}ms)`)
            }
          }
        })
        resourceObserver.observe({ entryTypes: ['resource'] })
        this.observers.push(resourceObserver)
      } catch (error) {
        console.warn('Resource observer not supported')
      }
    }
  }

  /**
   * 停止观察性能
   */
  stopObserving() {
    this.observers.forEach(observer => {
      try {
        observer.disconnect()
      } catch (error) {
        console.warn('Error disconnecting observer:', error)
      }
    })
    this.observers = []
  }

  /**
   * 生成性能报告
   */
  generateReport() {
    const metrics = this.getMetrics()
    const pagePerf = this.getPagePerformance()
    const resources = this.getResourcePerformance()

    return {
      timestamp: new Date().toISOString(),
      customMetrics: metrics,
      pagePerformance: pagePerf,
      resourcePerformance: resources,
      memoryUsage: this.getMemoryUsage(),
      userAgent: navigator.userAgent
    }
  }

  /**
   * 获取内存使用情况
   */
  getMemoryUsage() {
    if (window.performance && window.performance.memory) {
      return {
        usedJSHeapSize: window.performance.memory.usedJSHeapSize,
        totalJSHeapSize: window.performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit
      }
    }
    return null
  }

  /**
   * 导出性能数据
   */
  exportData() {
    const report = this.generateReport()
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `performance-report-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
}

// 创建全局实例
const performanceMonitor = new PerformanceMonitor()

// 自动启动（仅在开发环境或手动启用时）
if (import.meta.env.DEV || localStorage.getItem('performance-monitor') === 'true') {
  performanceMonitor.enable()
}

/**
 * 性能装饰器
 */
export function measurePerformance(name) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value

    descriptor.value = async function(...args) {
      const measureName = name || `${target.constructor.name}.${propertyKey}`
      return await performanceMonitor.measureFunction(measureName, () => {
        return originalMethod.apply(this, args)
      })
    }

    return descriptor
  }
}

/**
 * Vue组件性能监控混入
 */
export const performanceMixin = {
  beforeCreate() {
    if (performanceMonitor.isEnabled) {
      const componentName = this.$options.name || 'Anonymous'
      performanceMonitor.startTiming(`Component ${componentName} create`)
    }
  },
  
  created() {
    if (performanceMonitor.isEnabled) {
      const componentName = this.$options.name || 'Anonymous'
      performanceMonitor.endTiming(`Component ${componentName} create`)
      performanceMonitor.startTiming(`Component ${componentName} mount`)
    }
  },
  
  mounted() {
    if (performanceMonitor.isEnabled) {
      const componentName = this.$options.name || 'Anonymous'
      performanceMonitor.endTiming(`Component ${componentName} mount`)
    }
  }
}

export default performanceMonitor
