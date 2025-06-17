/**
 * 日志管理工具
 * 在生产环境中禁用console.log，只保留必要的错误信息
 */

class Logger {
  constructor() {
    this.isDev = import.meta.env.DEV
    this.isDebug = import.meta.env.VITE_DEBUG === 'true'
  }

  /**
   * 普通日志 - 只在开发环境显示
   */
  log(...args) {
    if (this.isDev) {
      console.log(...args)
    }
  }

  /**
   * 信息日志 - 只在开发环境显示
   */
  info(...args) {
    if (this.isDev) {
      console.info(...args)
    }
  }

  /**
   * 警告日志 - 开发环境和调试模式显示
   */
  warn(...args) {
    if (this.isDev || this.isDebug) {
      console.warn(...args)
    }
  }

  /**
   * 错误日志 - 始终显示
   */
  error(...args) {
    console.error(...args)
  }

  /**
   * 调试日志 - 只在调试模式显示
   */
  debug(...args) {
    if (this.isDebug) {
      console.log('[DEBUG]', ...args)
    }
  }

  /**
   * 分组日志 - 只在开发环境显示
   */
  group(label) {
    if (this.isDev) {
      console.group(label)
    }
  }

  /**
   * 结束分组 - 只在开发环境显示
   */
  groupEnd() {
    if (this.isDev) {
      console.groupEnd()
    }
  }

  /**
   * 表格日志 - 只在开发环境显示
   */
  table(data) {
    if (this.isDev) {
      console.table(data)
    }
  }

  /**
   * 时间日志 - 只在开发环境显示
   */
  time(label) {
    if (this.isDev) {
      console.time(label)
    }
  }

  /**
   * 结束时间日志 - 只在开发环境显示
   */
  timeEnd(label) {
    if (this.isDev) {
      console.timeEnd(label)
    }
  }
}

// 创建全局日志实例
const logger = new Logger()

export default logger
