/**
 * 拼音处理工具函数
 */

import { pinyin } from 'pinyin-pro'

/**
 * 获取字符的所有拼音选项
 * @param {string} char - 中文字符
 * @returns {Array} 拼音选项数组
 */
export function getAllPinyinOptions(char) {
  if (!char || !/[\u4e00-\u9fff]/.test(char)) {
    return [char]
  }

  try {
    // 获取多音字的所有读音
    const pinyinResult = pinyin(char, {
      toneType: 'symbol',
      type: 'array',
      multiple: true
    })

    if (Array.isArray(pinyinResult) && pinyinResult.length > 0) {
      // 如果是多音字，返回所有读音
      if (Array.isArray(pinyinResult[0])) {
        return pinyinResult[0]
      }
      // 如果是单音字，返回单个读音
      return pinyinResult
    }

    // 回退方案：使用默认拼音
    const defaultPinyin = pinyin(char, { toneType: 'symbol' })
    return [defaultPinyin || char]
  } catch (error) {
    console.warn('获取拼音失败:', error)
    return [char]
  }
}

/**
 * 处理拼音导航
 * @param {Event} e - 键盘事件
 * @param {Object} editor - TinyMCE编辑器实例
 */
export function handlePinyinNavigation(e, editor) {
  if (!editor) return

  const selection = editor.selection
  const range = selection.getRng()
  const currentNode = selection.getNode()

  // 检查是否在拼音注音中
  const rubyElement = currentNode.closest ? currentNode.closest('ruby.pinyin-ruby') : null

  if (rubyElement) {
    // 在拼音注音中的导航处理
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault()
      navigateBetweenPinyinElements(editor, rubyElement, e.key === 'ArrowRight')
    } else if (e.key === 'Delete' || e.key === 'Backspace') {
      e.preventDefault()
      removePinyinElement(editor, rubyElement)
    }
  }
}

/**
 * 在拼音元素之间导航
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {Element} currentRuby - 当前拼音元素
 * @param {boolean} forward - 是否向前导航
 */
function navigateBetweenPinyinElements(editor, currentRuby, forward) {
  const body = editor.getBody()
  const allRubies = body.querySelectorAll('ruby.pinyin-ruby')
  const currentIndex = Array.from(allRubies).indexOf(currentRuby)

  let targetIndex
  if (forward) {
    targetIndex = currentIndex + 1
    if (targetIndex >= allRubies.length) {
      // 移动到最后一个拼音元素后面
      const range = editor.dom.createRng()
      const nextSibling = currentRuby.nextSibling
      if (nextSibling) {
        range.setStart(nextSibling, 0)
      } else {
        range.setStartAfter(currentRuby)
      }
      range.collapse(true)
      editor.selection.setRng(range)
      return
    }
  } else {
    targetIndex = currentIndex - 1
    if (targetIndex < 0) {
      // 移动到第一个拼音元素前面
      const range = editor.dom.createRng()
      range.setStartBefore(currentRuby)
      range.collapse(true)
      editor.selection.setRng(range)
      return
    }
  }

  // 移动到目标拼音元素
  const targetRuby = allRubies[targetIndex]
  if (targetRuby) {
    const range = editor.dom.createRng()
    range.selectNode(targetRuby)
    editor.selection.setRng(range)
  }
}

/**
 * 移除拼音元素
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {Element} rubyElement - 要移除的拼音元素
 */
function removePinyinElement(editor, rubyElement) {
  const rbElement = rubyElement.querySelector('rb')
  const char = rbElement ? rbElement.textContent : rubyElement.getAttribute('data-char')

  // 用原始字符替换拼音元素
  const textNode = editor.getDoc().createTextNode(char)
  rubyElement.parentNode.replaceChild(textNode, rubyElement)

  // 将光标移动到字符后
  const range = editor.dom.createRng()
  range.setStart(textNode, char.length)
  range.collapse(true)
  editor.selection.setRng(range)
}

// 存储编辑器的拼音编辑函数引用
let editorPinyinEditFunction = null

/**
 * 设置编辑器的拼音编辑函数
 * @param {Function} openPinyinEditDialog - 打开拼音编辑对话框的函数
 */
export function setEditorPinyinEditFunction(openPinyinEditDialog) {
  editorPinyinEditFunction = openPinyinEditDialog
}

/**
 * 处理拼音编辑
 * @param {Element} rubyElement - 拼音元素
 * @param {Object} editor - TinyMCE编辑器实例
 */
export function handlePinyinEdit(rubyElement, editor) {
  const char = rubyElement.getAttribute('data-char')
  const currentPinyin = rubyElement.getAttribute('data-pinyin')
  const pinyinOptionsStr = rubyElement.getAttribute('data-pinyin-options')

  let pinyinOptions = []
  try {
    pinyinOptions = JSON.parse(pinyinOptionsStr || '[]')
  } catch (error) {
    pinyinOptions = getAllPinyinOptions(char)
  }

  if (pinyinOptions.length <= 1) {
    // 只有一个读音，无需编辑
    if (window.ElMessage) {
      window.ElMessage.info(`"${char}" 只有一个读音：${currentPinyin}`)
    }
    return
  }

  // 使用编辑器的拼音编辑函数
  if (editorPinyinEditFunction) {
    editorPinyinEditFunction(
      char,
      currentPinyin,
      pinyinOptions,
      (selectedPinyin) => {
        updatePinyinElement(rubyElement, selectedPinyin)
      },
      () => {
        removePinyinElement(editor, rubyElement)
      }
    )
  }
}

/**
 * 显示拼音上下文菜单
 * @param {Element} rubyElement - 拼音元素
 * @param {Event} event - 右键事件
 * @param {Object} editor - TinyMCE编辑器实例
 */
export function showPinyinContextMenu(rubyElement, event, editor) {
  // 阻止默认右键菜单
  event.preventDefault()
  event.stopPropagation()

  // 清除之前的菜单
  const existingMenus = document.querySelectorAll('.pinyin-context-menu')
  existingMenus.forEach(menu => menu.remove())

  const char = rubyElement.getAttribute('data-char')
  const currentPinyin = rubyElement.getAttribute('data-pinyin')
  const pinyinOptionsStr = rubyElement.getAttribute('data-pinyin-options')

  let pinyinOptions = []
  try {
    pinyinOptions = JSON.parse(pinyinOptionsStr || '[]')
  } catch (error) {
    pinyinOptions = getAllPinyinOptions(char)
  }

  // 获取更精确的鼠标位置
  const mouseX = event.pageX || event.clientX + window.scrollX
  const mouseY = event.pageY || event.clientY + window.scrollY

  // 创建上下文菜单
  const menu = document.createElement('div')
  menu.className = 'pinyin-context-menu'
  menu.style.cssText = `
    position: absolute;
    left: ${mouseX}px;
    top: ${mouseY}px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 10000;
    min-width: 140px;
    padding: 8px 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `

  // 添加拼音选项
  pinyinOptions.forEach((option, index) => {
    const item = document.createElement('div')
    item.className = 'pinyin-menu-item'
    item.innerHTML = `
      <span class="menu-char">${char}</span>
      <span class="menu-pinyin">${option}</span>
      ${option === currentPinyin ? '<span class="menu-current">当前</span>' : ''}
    `
    item.style.cssText = `
      padding: 8px 12px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s ease;
      ${option === currentPinyin ? 'background: #e1f3ff; color: #409eff;' : ''}
    `

    item.addEventListener('mouseenter', () => {
      if (option !== currentPinyin) {
        item.style.background = '#f5f5f5'
      }
    })

    item.addEventListener('mouseleave', () => {
      if (option !== currentPinyin) {
        item.style.background = 'transparent'
      }
    })

    item.addEventListener('click', () => {
      updatePinyinElement(rubyElement, option)
      menu.remove()
    })

    menu.appendChild(item)
  })

  // 添加分隔线
  if (pinyinOptions.length > 0) {
    const separator = document.createElement('div')
    separator.style.cssText = `
      height: 1px;
      background: #eee;
      margin: 4px 0;
    `
    menu.appendChild(separator)
  }

  // 添加编辑选项
  const editItem = document.createElement('div')
  editItem.className = 'pinyin-menu-item'
  editItem.innerHTML = `
    <span class="menu-icon">✏️</span>
    <span>编辑拼音</span>
  `
  editItem.style.cssText = `
    padding: 8px 12px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: background 0.2s ease;
  `

  editItem.addEventListener('mouseenter', () => {
    editItem.style.background = '#f5f5f5'
  })

  editItem.addEventListener('mouseleave', () => {
    editItem.style.background = 'transparent'
  })

  editItem.addEventListener('click', () => {
    menu.remove()
    // 延迟执行，确保菜单先关闭
    setTimeout(() => {
      handlePinyinEdit(rubyElement, editor)
    }, 50)
  })

  menu.appendChild(editItem)

  // 添加删除选项
  const deleteItem = document.createElement('div')
  deleteItem.className = 'pinyin-menu-item'
  deleteItem.innerHTML = `
    <span class="menu-icon">🗑️</span>
    <span>删除拼音</span>
  `
  deleteItem.style.cssText = `
    padding: 8px 12px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #f56c6c;
    transition: background 0.2s ease;
  `

  deleteItem.addEventListener('mouseenter', () => {
    deleteItem.style.background = '#fef0f0'
  })

  deleteItem.addEventListener('mouseleave', () => {
    deleteItem.style.background = 'transparent'
  })

  deleteItem.addEventListener('click', () => {
    removePinyinElement(editor, rubyElement)
    menu.remove()
  })

  menu.appendChild(deleteItem)

  // 调整菜单位置，确保不超出屏幕
  document.body.appendChild(menu)

  const menuRect = menu.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  // 如果菜单超出右边界，向左调整
  if (menuRect.right > viewportWidth) {
    menu.style.left = (mouseX - menuRect.width) + 'px'
  }

  // 如果菜单超出下边界，向上调整
  if (menuRect.bottom > viewportHeight) {
    menu.style.top = (mouseY - menuRect.height) + 'px'
  }

  // 点击其他地方关闭菜单
  const closeMenu = (e) => {
    if (!menu.contains(e.target)) {
      menu.remove()
      document.removeEventListener('click', closeMenu)
      document.removeEventListener('contextmenu', closeMenu)
    }
  }

  // 延迟添加事件监听，避免立即触发
  setTimeout(() => {
    document.addEventListener('click', closeMenu)
    document.addEventListener('contextmenu', closeMenu)
  }, 100)
}

/**
 * 更新拼音元素
 * @param {Element} rubyElement - 拼音元素
 * @param {string} newPinyin - 新的拼音
 */
function updatePinyinElement(rubyElement, newPinyin) {
  const rtElement = rubyElement.querySelector('rt')
  if (rtElement) {
    rtElement.textContent = newPinyin
  }
  rubyElement.setAttribute('data-pinyin', newPinyin)
}



/**
 * 为文本添加拼音注音
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {string} text - 要注音的文本
 * @returns {string} 带拼音的HTML
 */
export function addPinyinToText(editor, text) {
  if (!text) return ''

  const chars = Array.from(text)
  let annotatedHtml = ''

  chars.forEach((char, index) => {
    if (/[\u4e00-\u9fff]/.test(char)) {
      // 是中文字符，使用 ruby 标签添加拼音
      const pinyinOptions = getAllPinyinOptions(char)
      const defaultPinyin = pinyinOptions[0] || char

      // 使用标准 ruby 标签，添加零宽度空格确保光标可以正常移动
      const pinyinData = JSON.stringify(pinyinOptions).replace(/"/g, '&quot;')
      annotatedHtml += `<ruby class="pinyin-ruby" data-pinyin="${defaultPinyin}" data-char="${char}" data-pinyin-options="${pinyinData}"><rt>${defaultPinyin}</rt><rb>${char}</rb></ruby>&#8203;`
    } else if (char === ' ') {
      // 空格字符，保持原样
      annotatedHtml += '&nbsp;'
    } else {
      // 其他非中文字符，直接添加
      annotatedHtml += char
    }
  })

  return annotatedHtml
}

/**
 * 移除文本中的拼音注音
 * @param {string} htmlContent - 包含拼音的HTML内容
 * @returns {string} 移除拼音后的HTML
 */
export function removePinyinFromText(htmlContent) {
  if (!htmlContent) return ''

  // 移除 ruby 标签，保留 rb 标签内的文字内容
  let cleanHtml = htmlContent.replace(/<ruby[^>]*class="pinyin-ruby"[^>]*><rt[^>]*>.*?<\/rt><rb[^>]*>(.*?)<\/rb><\/ruby>/g, '$1')
  cleanHtml = cleanHtml.replace(/<ruby[^>]*><rt[^>]*>.*?<\/rt><rb[^>]*>(.*?)<\/rb><\/ruby>/g, '$1')
  
  // 处理可能的嵌套span标签
  cleanHtml = cleanHtml.replace(/<span>([^<]*)<\/span>/g, '$1')
  
  // 移除零宽度空格
  cleanHtml = cleanHtml.replace(/&#8203;/g, '')

  return cleanHtml
}
