/**
 * UI工具函数
 */

/**
 * 平滑滚动到顶部
 */
export function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

/**
 * 平滑滚动到元素
 * @param {string|Element} element - 元素选择器或元素对象
 * @param {Object} options - 滚动选项
 */
export function scrollToElement(element, options = {}) {
  const {
    behavior = 'smooth',
    block = 'start',
    inline = 'nearest'
  } = options

  let targetElement
  if (typeof element === 'string') {
    targetElement = document.querySelector(element)
  } else {
    targetElement = element
  }

  if (targetElement) {
    targetElement.scrollIntoView({
      behavior,
      block,
      inline
    })
  }
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @param {boolean} immediate - 是否立即执行
 */
export function debounce(func, wait, immediate = false) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func(...args)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 限制时间（毫秒）
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    try {
      document.execCommand('copy')
      document.body.removeChild(textArea)
      return true
    } catch (err) {
      document.body.removeChild(textArea)
      return false
    }
  }
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * 格式化数字
 * @param {number} num - 数字
 * @param {Object} options - 格式化选项
 */
export function formatNumber(num, options = {}) {
  const {
    locale = 'zh-CN',
    minimumFractionDigits = 0,
    maximumFractionDigits = 2
  } = options

  return new Intl.NumberFormat(locale, {
    minimumFractionDigits,
    maximumFractionDigits
  }).format(num)
}

/**
 * 获取随机颜色
 * @param {string} type - 颜色类型 ('hex', 'rgb', 'hsl')
 */
export function getRandomColor(type = 'hex') {
  switch (type) {
    case 'hex':
      return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')
    case 'rgb':
      const r = Math.floor(Math.random() * 256)
      const g = Math.floor(Math.random() * 256)
      const b = Math.floor(Math.random() * 256)
      return `rgb(${r}, ${g}, ${b})`
    case 'hsl':
      const h = Math.floor(Math.random() * 360)
      const s = Math.floor(Math.random() * 100)
      const l = Math.floor(Math.random() * 100)
      return `hsl(${h}, ${s}%, ${l}%)`
    default:
      return getRandomColor('hex')
  }
}

/**
 * 检测设备类型
 */
export function getDeviceType() {
  const userAgent = navigator.userAgent.toLowerCase()
  const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)
  const isTablet = /ipad|android(?!.*mobile)/i.test(userAgent)
  
  if (isMobile && !isTablet) {
    return 'mobile'
  } else if (isTablet) {
    return 'tablet'
  } else {
    return 'desktop'
  }
}

/**
 * 检测是否支持触摸
 */
export function isTouchDevice() {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

/**
 * 获取浏览器信息
 */
export function getBrowserInfo() {
  const userAgent = navigator.userAgent
  let browserName = 'Unknown'
  let browserVersion = 'Unknown'

  if (userAgent.indexOf('Chrome') > -1) {
    browserName = 'Chrome'
    browserVersion = userAgent.match(/Chrome\/(\d+)/)?.[1] || 'Unknown'
  } else if (userAgent.indexOf('Firefox') > -1) {
    browserName = 'Firefox'
    browserVersion = userAgent.match(/Firefox\/(\d+)/)?.[1] || 'Unknown'
  } else if (userAgent.indexOf('Safari') > -1) {
    browserName = 'Safari'
    browserVersion = userAgent.match(/Version\/(\d+)/)?.[1] || 'Unknown'
  } else if (userAgent.indexOf('Edge') > -1) {
    browserName = 'Edge'
    browserVersion = userAgent.match(/Edge\/(\d+)/)?.[1] || 'Unknown'
  }

  return {
    name: browserName,
    version: browserVersion,
    userAgent
  }
}

/**
 * 生成唯一ID
 * @param {number} length - ID长度
 */
export function generateId(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 深度克隆对象
 * @param {any} obj - 要克隆的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime())
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item))
  }

  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}
