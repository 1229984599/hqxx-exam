/**
 * 消息提示工具
 */
import { createApp } from 'vue'
import MessageToast from '../components/MessageToast.vue'

class MessageManager {
  constructor() {
    this.instances = []
    this.zIndex = 9999
  }

  /**
   * 显示消息
   * @param {Object} options 消息选项
   */
  show(options) {
    const {
      type = 'info',
      message = '',
      description = '',
      duration = 3000,
      showProgress = true
    } = options

    // 创建消息实例
    const instance = this.createInstance({
      type,
      message,
      description,
      duration,
      showProgress
    })

    // 添加到实例列表
    this.instances.push(instance)

    return instance
  }

  /**
   * 创建消息实例
   * @param {Object} props 组件属性
   */
  createInstance(props) {
    // 创建容器元素
    const container = document.createElement('div')

    // 先创建实例对象的引用
    let instance = null

    // 创建Vue应用实例
    const app = createApp(MessageToast, {
      ...props,
      onClose: () => {
        if (instance) {
          this.removeInstance(instance)
        }
      }
    })

    // 挂载组件
    const vm = app.mount(container)

    // 将容器添加到body
    document.body.appendChild(container)

    // 创建实例对象
    instance = {
      app,
      vm,
      container,
      close: () => {
        if (vm && typeof vm.close === 'function') {
          vm.close()
        }
      }
    }

    return instance
  }

  /**
   * 移除消息实例
   * @param {Object} instance 实例对象
   */
  removeInstance(instance) {
    const index = this.instances.indexOf(instance)
    if (index > -1) {
      this.instances.splice(index, 1)
      
      // 销毁Vue应用实例
      if (instance.app) {
        instance.app.unmount()
      }
      
      // 移除DOM元素
      if (instance.container && instance.container.parentNode) {
        instance.container.parentNode.removeChild(instance.container)
      }
    }
  }

  /**
   * 成功消息
   * @param {String|Object} message 消息内容或选项对象
   * @param {Object} options 额外选项
   */
  success(message, options = {}) {
    if (typeof message === 'string') {
      return this.show({
        type: 'success',
        message,
        ...options
      })
    } else {
      return this.show({
        type: 'success',
        ...message
      })
    }
  }

  /**
   * 错误消息
   * @param {String|Object} message 消息内容或选项对象
   * @param {Object} options 额外选项
   */
  error(message, options = {}) {
    if (typeof message === 'string') {
      return this.show({
        type: 'error',
        message,
        duration: 5000, // 错误消息显示时间更长
        ...options
      })
    } else {
      return this.show({
        type: 'error',
        duration: 5000,
        ...message
      })
    }
  }

  /**
   * 警告消息
   * @param {String|Object} message 消息内容或选项对象
   * @param {Object} options 额外选项
   */
  warning(message, options = {}) {
    if (typeof message === 'string') {
      return this.show({
        type: 'warning',
        message,
        duration: 4000,
        ...options
      })
    } else {
      return this.show({
        type: 'warning',
        duration: 4000,
        ...message
      })
    }
  }

  /**
   * 信息消息
   * @param {String|Object} message 消息内容或选项对象
   * @param {Object} options 额外选项
   */
  info(message, options = {}) {
    if (typeof message === 'string') {
      return this.show({
        type: 'info',
        message,
        ...options
      })
    } else {
      return this.show({
        type: 'info',
        ...message
      })
    }
  }

  /**
   * 清除所有消息
   */
  clear() {
    this.instances.forEach(instance => {
      if (instance.close) {
        instance.close()
      }
    })
    this.instances = []
  }
}

// 创建全局实例
const messageManager = new MessageManager()

// 导出便捷方法
export const message = {
  success: (msg, options) => messageManager.success(msg, options),
  error: (msg, options) => messageManager.error(msg, options),
  warning: (msg, options) => messageManager.warning(msg, options),
  info: (msg, options) => messageManager.info(msg, options),
  show: (options) => messageManager.show(options),
  clear: () => messageManager.clear()
}

export default message

// 全局安装方法
export function install(app) {
  app.config.globalProperties.$message = message
  app.provide('message', message)
}
