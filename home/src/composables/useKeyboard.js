/**
 * 键盘快捷键组合式函数
 */
import { onMounted, onUnmounted } from 'vue'

export function useKeyboard() {
  const keyHandlers = new Map()

  /**
   * 注册键盘快捷键
   * @param {string} key - 按键组合，如 'ctrl+s', 'escape', 'space'
   * @param {Function} handler - 处理函数
   * @param {Object} options - 选项
   */
  const registerKey = (key, handler, options = {}) => {
    const {
      preventDefault = true,
      stopPropagation = true,
      target = document
    } = options

    const normalizedKey = normalizeKey(key)
    
    if (!keyHandlers.has(normalizedKey)) {
      keyHandlers.set(normalizedKey, [])
    }
    
    keyHandlers.get(normalizedKey).push({
      handler,
      preventDefault,
      stopPropagation,
      target
    })
  }

  /**
   * 注销键盘快捷键
   * @param {string} key - 按键组合
   * @param {Function} handler - 处理函数（可选）
   */
  const unregisterKey = (key, handler = null) => {
    const normalizedKey = normalizeKey(key)
    
    if (!keyHandlers.has(normalizedKey)) return
    
    if (handler) {
      const handlers = keyHandlers.get(normalizedKey)
      const index = handlers.findIndex(h => h.handler === handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
      if (handlers.length === 0) {
        keyHandlers.delete(normalizedKey)
      }
    } else {
      keyHandlers.delete(normalizedKey)
    }
  }

  /**
   * 标准化按键名称
   * @param {string} key - 按键组合
   */
  const normalizeKey = (key) => {
    return key.toLowerCase()
      .replace(/\s+/g, '')
      .split('+')
      .sort()
      .join('+')
  }

  /**
   * 处理键盘事件
   * @param {KeyboardEvent} event - 键盘事件
   */
  const handleKeyDown = (event) => {
    const keys = []
    
    if (event.ctrlKey) keys.push('ctrl')
    if (event.altKey) keys.push('alt')
    if (event.shiftKey) keys.push('shift')
    if (event.metaKey) keys.push('meta')
    
    // 特殊按键映射
    const specialKeys = {
      ' ': 'space',
      'Escape': 'escape',
      'Enter': 'enter',
      'Tab': 'tab',
      'Backspace': 'backspace',
      'Delete': 'delete',
      'ArrowUp': 'up',
      'ArrowDown': 'down',
      'ArrowLeft': 'left',
      'ArrowRight': 'right',
      'Home': 'home',
      'End': 'end',
      'PageUp': 'pageup',
      'PageDown': 'pagedown'
    }
    
    const keyName = specialKeys[event.key] || event.key.toLowerCase()
    keys.push(keyName)
    
    const keyCombo = keys.sort().join('+')
    
    if (keyHandlers.has(keyCombo)) {
      const handlers = keyHandlers.get(keyCombo)
      
      handlers.forEach(({ handler, preventDefault, stopPropagation }) => {
        if (preventDefault) event.preventDefault()
        if (stopPropagation) event.stopPropagation()
        
        handler(event)
      })
    }
  }

  // 生命周期管理
  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
    keyHandlers.clear()
  })

  return {
    registerKey,
    unregisterKey
  }
}

/**
 * 常用快捷键预设
 */
export const commonKeys = {
  ESCAPE: 'escape',
  ENTER: 'enter',
  SPACE: 'space',
  CTRL_S: 'ctrl+s',
  CTRL_Z: 'ctrl+z',
  CTRL_Y: 'ctrl+y',
  CTRL_A: 'ctrl+a',
  CTRL_C: 'ctrl+c',
  CTRL_V: 'ctrl+v',
  CTRL_X: 'ctrl+x',
  F1: 'f1',
  F5: 'f5',
  UP: 'up',
  DOWN: 'down',
  LEFT: 'left',
  RIGHT: 'right'
}

/**
 * 快捷键提示组合式函数
 */
export function useKeyboardHints() {
  const hints = new Map()

  /**
   * 添加快捷键提示
   * @param {string} key - 按键组合
   * @param {string} description - 描述
   * @param {string} category - 分类
   */
  const addHint = (key, description, category = 'general') => {
    if (!hints.has(category)) {
      hints.set(category, [])
    }
    
    hints.get(category).push({
      key,
      description,
      displayKey: formatKeyDisplay(key)
    })
  }

  /**
   * 获取所有提示
   */
  const getAllHints = () => {
    const result = {}
    hints.forEach((value, key) => {
      result[key] = value
    })
    return result
  }

  /**
   * 格式化按键显示
   * @param {string} key - 按键组合
   */
  const formatKeyDisplay = (key) => {
    return key
      .split('+')
      .map(k => {
        const keyMap = {
          'ctrl': 'Ctrl',
          'alt': 'Alt',
          'shift': 'Shift',
          'meta': 'Cmd',
          'escape': 'Esc',
          'enter': 'Enter',
          'space': 'Space',
          'up': '↑',
          'down': '↓',
          'left': '←',
          'right': '→'
        }
        return keyMap[k] || k.toUpperCase()
      })
      .join(' + ')
  }

  return {
    addHint,
    getAllHints,
    formatKeyDisplay
  }
}

/**
 * 检测是否为Mac系统
 */
export const isMac = () => {
  return /Mac|iPod|iPhone|iPad/.test(navigator.platform)
}

/**
 * 获取修饰键名称（根据系统）
 */
export const getModifierKey = () => {
  return isMac() ? 'Cmd' : 'Ctrl'
}
