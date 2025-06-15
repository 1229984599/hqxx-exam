/**
 * 加载状态管理
 */
import { ref, computed } from 'vue'
import { ElLoading } from 'element-plus'

// 全局加载状态
const globalLoadingStates = ref(new Map())
const globalLoadingInstance = ref(null)

export function useLoading(key = 'default') {
  // 局部加载状态
  const loading = ref(false)
  const loadingText = ref('加载中...')
  
  // 设置加载状态
  const setLoading = (state, text = '加载中...') => {
    loading.value = state
    loadingText.value = text
    
    // 更新全局状态
    if (state) {
      globalLoadingStates.value.set(key, { loading: true, text })
    } else {
      globalLoadingStates.value.delete(key)
    }
  }

  // 异步操作包装器
  const withLoading = async (asyncFn, text = '处理中...') => {
    setLoading(true, text)
    try {
      const result = await asyncFn()
      return result
    } finally {
      setLoading(false)
    }
  }

  // 全屏加载
  const showFullScreenLoading = (text = '加载中...') => {
    if (globalLoadingInstance.value) {
      globalLoadingInstance.value.close()
    }
    
    globalLoadingInstance.value = ElLoading.service({
      lock: true,
      text: text,
      background: 'rgba(0, 0, 0, 0.7)',
      customClass: 'global-loading'
    })
  }

  const hideFullScreenLoading = () => {
    if (globalLoadingInstance.value) {
      globalLoadingInstance.value.close()
      globalLoadingInstance.value = null
    }
  }

  // 计算全局加载状态
  const isGlobalLoading = computed(() => {
    return globalLoadingStates.value.size > 0
  })

  const globalLoadingText = computed(() => {
    const states = Array.from(globalLoadingStates.value.values())
    return states.length > 0 ? states[0].text : ''
  })

  return {
    loading,
    loadingText,
    setLoading,
    withLoading,
    showFullScreenLoading,
    hideFullScreenLoading,
    isGlobalLoading,
    globalLoadingText
  }
}

/**
 * 批量操作加载状态管理
 */
export function useBatchLoading() {
  const batchLoading = ref(false)
  const batchProgress = ref(0)
  const batchTotal = ref(0)
  const batchCurrent = ref(0)
  const batchErrors = ref([])

  const startBatch = (total, description = '批量处理') => {
    batchLoading.value = true
    batchTotal.value = total
    batchCurrent.value = 0
    batchProgress.value = 0
    batchErrors.value = []
  }

  const updateProgress = (current, errors = []) => {
    batchCurrent.value = current
    batchProgress.value = Math.round((current / batchTotal.value) * 100)
    batchErrors.value = errors
  }

  const finishBatch = () => {
    batchLoading.value = false
    batchProgress.value = 100
  }

  const batchProgressText = computed(() => {
    if (!batchLoading.value) return ''
    return `${batchCurrent.value}/${batchTotal.value} (${batchProgress.value}%)`
  })

  return {
    batchLoading,
    batchProgress,
    batchTotal,
    batchCurrent,
    batchErrors,
    batchProgressText,
    startBatch,
    updateProgress,
    finishBatch
  }
}

/**
 * 页面加载状态管理
 */
export function usePageLoading() {
  const pageLoading = ref(true)
  const pageError = ref(null)
  const retryCount = ref(0)
  const maxRetries = ref(3)

  const setPageLoading = (loading) => {
    pageLoading.value = loading
  }

  const setPageError = (error) => {
    pageError.value = error
    pageLoading.value = false
  }

  const clearPageError = () => {
    pageError.value = null
  }

  const retryPageLoad = async (loadFn) => {
    if (retryCount.value >= maxRetries.value) {
      setPageError('重试次数已达上限，请刷新页面')
      return false
    }

    retryCount.value++
    pageLoading.value = true
    clearPageError()

    try {
      await loadFn()
      retryCount.value = 0
      return true
    } catch (error) {
      setPageError(error.message || '页面加载失败')
      return false
    }
  }

  const canRetry = computed(() => {
    return retryCount.value < maxRetries.value
  })

  return {
    pageLoading,
    pageError,
    retryCount,
    maxRetries,
    canRetry,
    setPageLoading,
    setPageError,
    clearPageError,
    retryPageLoad
  }
}

/**
 * 智能加载状态
 * 根据操作类型自动选择合适的加载提示
 */
export function useSmartLoading() {
  const { setLoading, withLoading } = useLoading()

  const loadingMessages = {
    fetch: '正在加载数据...',
    create: '正在创建...',
    update: '正在更新...',
    delete: '正在删除...',
    upload: '正在上传...',
    download: '正在下载...',
    export: '正在导出...',
    import: '正在导入...',
    backup: '正在备份...',
    restore: '正在恢复...',
    test: '正在测试连接...',
    save: '正在保存...',
    submit: '正在提交...',
    process: '正在处理...'
  }

  const smartLoading = async (operation, asyncFn, customText = null) => {
    const text = customText || loadingMessages[operation] || '处理中...'
    return await withLoading(asyncFn, text)
  }

  return {
    smartLoading,
    loadingMessages
  }
}

/**
 * 防抖加载
 * 防止快速重复操作
 */
export function useDebounceLoading(delay = 300) {
  const { setLoading, withLoading } = useLoading()
  let debounceTimer = null

  const debounceLoading = async (asyncFn, text = '处理中...') => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    return new Promise((resolve, reject) => {
      debounceTimer = setTimeout(async () => {
        try {
          const result = await withLoading(asyncFn, text)
          resolve(result)
        } catch (error) {
          reject(error)
        }
      }, delay)
    })
  }

  return {
    debounceLoading
  }
}
