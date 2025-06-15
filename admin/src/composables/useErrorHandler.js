/**
 * 全局错误处理和用户体验优化
 */
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'

export function useErrorHandler() {
  /**
   * 处理API错误
   * @param {Error} error - 错误对象
   * @param {string} defaultMessage - 默认错误消息
   * @param {Object} options - 配置选项
   */
  const handleApiError = (error, defaultMessage = '操作失败', options = {}) => {
    console.error('API错误:', error)
    
    const {
      showNotification = false,
      showRetry = false,
      onRetry = null,
      duration = 3000
    } = options

    let errorMessage = defaultMessage
    let errorType = 'error'

    // 解析错误信息
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = data.detail || '请求参数错误'
          break
        case 401:
          errorMessage = '登录已过期，请重新登录'
          errorType = 'warning'
          // 可以在这里触发重新登录逻辑
          break
        case 403:
          errorMessage = '权限不足，无法执行此操作'
          errorType = 'warning'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 422:
          errorMessage = data.detail || '数据验证失败'
          break
        case 429:
          errorMessage = '请求过于频繁，请稍后再试'
          break
        case 500:
          errorMessage = '服务器内部错误，请联系管理员'
          break
        case 502:
        case 503:
        case 504:
          errorMessage = '服务暂时不可用，请稍后重试'
          break
        default:
          errorMessage = data.detail || data.message || defaultMessage
      }
    } else if (error.request) {
      errorMessage = '网络连接失败，请检查网络设置'
      errorType = 'warning'
    } else {
      errorMessage = error.message || defaultMessage
    }

    // 显示错误消息
    if (showNotification) {
      ElNotification({
        title: '操作失败',
        message: errorMessage,
        type: errorType,
        duration: duration,
        showClose: true
      })
    } else {
      ElMessage({
        message: errorMessage,
        type: errorType,
        duration: duration,
        showClose: true
      })
    }

    // 显示重试按钮
    if (showRetry && onRetry) {
      setTimeout(() => {
        ElMessageBox.confirm(
          '操作失败，是否重试？',
          '重试确认',
          {
            confirmButtonText: '重试',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          onRetry()
        }).catch(() => {
          // 用户取消重试
        })
      }, 1000)
    }

    return {
      message: errorMessage,
      type: errorType,
      status: error.response?.status
    }
  }

  /**
   * 处理成功消息
   * @param {string} message - 成功消息
   * @param {Object} options - 配置选项
   */
  const handleSuccess = (message = '操作成功', options = {}) => {
    const {
      showNotification = false,
      duration = 2000
    } = options

    if (showNotification) {
      ElNotification({
        title: '操作成功',
        message: message,
        type: 'success',
        duration: duration
      })
    } else {
      ElMessage({
        message: message,
        type: 'success',
        duration: duration
      })
    }
  }

  /**
   * 显示加载消息
   * @param {string} message - 加载消息
   * @returns {Object} 消息实例，可调用close()关闭
   */
  const showLoading = (message = '正在处理...') => {
    return ElMessage({
      message: message,
      type: 'info',
      duration: 0,
      showClose: false
    })
  }

  /**
   * 确认对话框
   * @param {string} message - 确认消息
   * @param {string} title - 对话框标题
   * @param {Object} options - 配置选项
   */
  const confirmAction = async (message, title = '确认操作', options = {}) => {
    const {
      confirmButtonText = '确认',
      cancelButtonText = '取消',
      type = 'warning',
      dangerouslyUseHTMLString = false
    } = options

    try {
      await ElMessageBox.confirm(
        message,
        title,
        {
          confirmButtonText,
          cancelButtonText,
          type,
          dangerouslyUseHTMLString
        }
      )
      return true
    } catch {
      return false
    }
  }

  /**
   * 网络状态检查
   */
  const checkNetworkStatus = () => {
    if (!navigator.onLine) {
      ElMessage({
        message: '网络连接已断开，请检查网络设置',
        type: 'warning',
        duration: 0,
        showClose: true
      })
      return false
    }
    return true
  }

  return {
    handleApiError,
    handleSuccess,
    showLoading,
    confirmAction,
    checkNetworkStatus
  }
}

/**
 * 全局错误处理器
 */
export function setupGlobalErrorHandler() {
  const { handleApiError } = useErrorHandler()

  // 监听未捕获的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise错误:', event.reason)
    
    if (event.reason?.response) {
      handleApiError(event.reason, '系统错误')
    }
    
    event.preventDefault()
  })

  // 监听全局错误
  window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error)
    
    ElMessage({
      message: '系统发生错误，请刷新页面重试',
      type: 'error',
      duration: 5000,
      showClose: true
    })
  })
}

/**
 * 网络状态监听
 */
export function setupNetworkMonitor() {
  window.addEventListener('online', () => {
    ElMessage({
      message: '网络连接已恢复',
      type: 'success',
      duration: 2000
    })
  })

  window.addEventListener('offline', () => {
    ElMessage({
      message: '网络连接已断开',
      type: 'warning',
      duration: 0,
      showClose: true
    })
  })
}
