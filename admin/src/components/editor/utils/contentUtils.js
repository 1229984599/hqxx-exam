/**
 * 内容处理工具函数
 */

/**
 * 清理Word等外部格式
 * @param {string} content - 要清理的HTML内容
 * @returns {string} 清理后的内容
 */
export function cleanWordContent(content) {
  if (!content) return ''

  let cleanedContent = content

  // 移除Word特有的标签和属性
  cleanedContent = cleanedContent.replace(/<o:p\s*\/?>|<\/o:p>/gi, '')
  cleanedContent = cleanedContent.replace(/<w:[^>]*>|<\/w:[^>]*>/gi, '')
  cleanedContent = cleanedContent.replace(/<m:[^>]*>|<\/m:[^>]*>/gi, '')
  cleanedContent = cleanedContent.replace(/<v:[^>]*>|<\/v:[^>]*>/gi, '')

  // 移除多余的样式属性
  cleanedContent = cleanedContent.replace(/\s*mso-[^:]+:[^;"]+;?/gi, '')
  cleanedContent = cleanedContent.replace(/\s*MARGIN[^:]*:[^;"]+;?/gi, '')
  cleanedContent = cleanedContent.replace(/\s*FONT[^:]*:[^;"]+;?/gi, '')
  cleanedContent = cleanedContent.replace(/\s*tab-stops:[^;"]*;?/gi, '')
  cleanedContent = cleanedContent.replace(/\s*tab-interval:[^;"]*;?/gi, '')

  // 清理空的style属性
  cleanedContent = cleanedContent.replace(/\s*style="\s*"/gi, '')
  cleanedContent = cleanedContent.replace(/\s*style='\s*'/gi, '')

  // 移除多余的空白字符
  cleanedContent = cleanedContent.replace(/\s+/g, ' ')
  cleanedContent = cleanedContent.replace(/>\s+</g, '><')

  // 移除空的段落和span标签
  cleanedContent = cleanedContent.replace(/<p[^>]*>\s*<\/p>/gi, '')
  cleanedContent = cleanedContent.replace(/<span[^>]*>\s*<\/span>/gi, '')

  return cleanedContent.trim()
}

/**
 * 提取纯文本内容
 * @param {string} htmlContent - HTML内容
 * @returns {string} 纯文本内容
 */
export function extractTextContent(htmlContent) {
  if (!htmlContent) return ''

  // 创建临时div来解析HTML
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = htmlContent

  // 移除script和style标签
  const scripts = tempDiv.querySelectorAll('script, style')
  scripts.forEach(el => el.remove())

  return tempDiv.textContent || tempDiv.innerText || ''
}

/**
 * 计算内容统计信息
 * @param {string} htmlContent - HTML内容
 * @param {string} textContent - 纯文本内容
 * @returns {Object} 统计信息
 */
export function calculateContentStats(htmlContent, textContent) {
  if (!htmlContent || !textContent) {
    return {
      characters: 0,
      charactersNoSpaces: 0,
      words: 0,
      paragraphs: 0,
      sentences: 0,
      readingTime: 0,
      chineseChars: 0,
      pinyinAnnotations: 0
    }
  }

  // 基础统计
  const characters = textContent.length
  const charactersNoSpaces = textContent.replace(/\s/g, '').length

  // 中文字符统计
  const chineseChars = (textContent.match(/[\u4e00-\u9fff]/g) || []).length

  // 拼音注音统计
  const pinyinAnnotations = (htmlContent.match(/<ruby[^>]*class="pinyin-ruby"[^>]*>/g) || []).length

  // 段落统计
  const paragraphs = Math.max(1, (htmlContent.match(/<p[^>]*>/g) || []).length)

  // 句子统计（基于中文句号、问号、感叹号）
  const sentences = Math.max(1, (textContent.match(/[。！？.!?]/g) || []).length)

  // 词语统计（中文按字符计算，英文按单词计算）
  const englishWords = (textContent.match(/[a-zA-Z]+/g) || []).length
  const words = chineseChars + englishWords

  // 阅读时间估算（中文：300字/分钟，英文：200词/分钟）
  const readingTime = Math.ceil((chineseChars / 300 + englishWords / 200))

  return {
    characters,
    charactersNoSpaces,
    words,
    paragraphs,
    sentences,
    readingTime,
    chineseChars,
    pinyinAnnotations
  }
}

/**
 * 智能选择文本
 * @param {Object} editor - TinyMCE编辑器实例
 * @returns {boolean} 是否成功选择
 */
export function trySmartSelection(editor) {
  if (!editor) {
    return false
  }

  try {
    const currentNode = editor.selection.getNode()
    const range = editor.selection.getRng()

    // 方法1: 如果光标在文本节点中，选择整个文本节点
    if (currentNode.nodeType === Node.TEXT_NODE && currentNode.textContent.trim()) {
      const newRange = editor.dom.createRng()
      newRange.selectNodeContents(currentNode)
      editor.selection.setRng(newRange)
      const content = editor.selection.getContent()
      return content && content.trim().length > 0
    }

    // 方法2: 如果光标在元素中，查找最近的文本内容
    let targetElement = currentNode
    while (targetElement && targetElement !== editor.getBody()) {
      if (targetElement.textContent && targetElement.textContent.trim()) {
        // 优先选择段落、span等文本容器
        if (['P', 'DIV', 'SPAN', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI'].includes(targetElement.tagName)) {
          const newRange = editor.dom.createRng()
          newRange.selectNodeContents(targetElement)
          editor.selection.setRng(newRange)
          const content = editor.selection.getContent()
          if (content && content.trim().length > 0) {
            return true
          }
        }
      }
      targetElement = targetElement.parentNode
    }

    // 方法3: 查找光标附近的文本节点
    const body = editor.getBody()
    const walker = editor.dom.createTreeWalker(
      body,
      NodeFilter.SHOW_TEXT,
      (node) => {
        return node.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
      },
      false
    )

    let node
    while (node = walker.nextNode()) {
      if (node.textContent.trim()) {
        const newRange = editor.dom.createRng()
        newRange.selectNodeContents(node)
        editor.selection.setRng(newRange)
        return true
      }
    }

    // 方法4: 最后尝试选择整个编辑器内容
    const bodyContent = body.textContent
    if (bodyContent && bodyContent.trim()) {
      const newRange = editor.dom.createRng()
      newRange.selectNodeContents(body)
      editor.selection.setRng(newRange)
      return true
    }

  } catch (error) {
    console.warn('智能选择失败:', error)
  }

  return false
}

/**
 * 调整字体大小
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {number} delta - 字体大小变化量（px）
 */
export function adjustFontSize(editor, delta) {
  if (!editor) return

  // 保存当前选择
  const selection = editor.selection
  const bookmark = selection.getBookmark()
  let selectedContent = selection.getContent()

  // 如果没有选中内容，尝试智能选择
  if (!selectedContent) {
    if (!trySmartSelection(editor)) {
      return
    }
    selectedContent = selection.getContent()
  }

  if (!selectedContent) return

  // 获取当前字体大小
  const currentNode = selection.getNode()
  let currentSize = 14

  // 尝试从选中的元素获取字体大小
  if (currentNode) {
    const computedStyle = window.getComputedStyle(currentNode)
    currentSize = parseInt(computedStyle.fontSize) || 14
  }

  // 计算新的字体大小
  const newSize = Math.max(8, Math.min(240, currentSize + delta))

  // 使用TinyMCE的格式化命令来设置字体大小
  editor.formatter.apply('fontsize', { value: newSize + 'px' })

  // 恢复选择，这样用户可以继续调整
  setTimeout(() => {
    try {
      selection.moveToBookmark(bookmark)
      // 触发事件确保UI更新
      editor.fire('SelectionChange')
      editor.fire('NodeChange')
    } catch (error) {
      console.warn('恢复选择失败:', error)
    }
  }, 10)
}

/**
 * 设置行间距
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {string} lineHeight - 行间距值
 */
export function setLineHeight(editor, lineHeight) {
  if (!editor) return

  const selectedContent = editor.selection.getContent()

  // 如果没有选中内容，尝试智能选择
  if (!selectedContent) {
    if (!trySmartSelection(editor)) {
      // 如果智能选择失败，对整个编辑器内容应用行间距
      const body = editor.getBody()
      if (body) {
        body.style.lineHeight = lineHeight
        return
      }
    }
  }

  // 对选中的内容应用行间距
  const currentNode = editor.selection.getNode()

  // 查找最近的块级元素
  let targetElement = currentNode
  while (targetElement && targetElement !== editor.getBody()) {
    if (['P', 'DIV', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI', 'BLOCKQUOTE'].includes(targetElement.tagName)) {
      targetElement.style.lineHeight = lineHeight
      return
    }
    targetElement = targetElement.parentNode
  }

  // 如果没有找到合适的块级元素，包装选中内容
  const wrappedContent = `<div style="line-height: ${lineHeight};">${selectedContent}</div>`
  editor.selection.setContent(wrappedContent)
}

/**
 * 提取格式信息
 * @param {string} htmlContent - HTML内容
 * @returns {Object} 格式信息
 */
export function extractFormat(htmlContent) {
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = htmlContent

  const firstElement = tempDiv.firstElementChild || tempDiv
  const computedStyle = window.getComputedStyle ? window.getComputedStyle(firstElement) : {}

  return {
    fontSize: firstElement.style.fontSize || computedStyle.fontSize,
    fontWeight: firstElement.style.fontWeight || computedStyle.fontWeight,
    fontStyle: firstElement.style.fontStyle || computedStyle.fontStyle,
    color: firstElement.style.color || computedStyle.color,
    backgroundColor: firstElement.style.backgroundColor || computedStyle.backgroundColor,
    textDecoration: firstElement.style.textDecoration || computedStyle.textDecoration,
    lineHeight: firstElement.style.lineHeight || computedStyle.lineHeight,
    textAlign: firstElement.style.textAlign || computedStyle.textAlign
  }
}

/**
 * 应用格式
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {string} htmlContent - 要应用格式的HTML内容
 * @param {Object} format - 格式信息
 */
export function applyFormat(editor, htmlContent, format) {
  if (!editor || !htmlContent || !format) return

  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = htmlContent

  function applyFormatToElement(element) {
    if (format.fontSize) element.style.fontSize = format.fontSize
    if (format.fontWeight) element.style.fontWeight = format.fontWeight
    if (format.fontStyle) element.style.fontStyle = format.fontStyle
    if (format.color) element.style.color = format.color
    if (format.backgroundColor) element.style.backgroundColor = format.backgroundColor
    if (format.textDecoration) element.style.textDecoration = format.textDecoration
    if (format.lineHeight) element.style.lineHeight = format.lineHeight
    if (format.textAlign) element.style.textAlign = format.textAlign
  }

  // 应用格式到所有元素
  if (tempDiv.children.length > 0) {
    Array.from(tempDiv.children).forEach(applyFormatToElement)
  } else {
    // 如果没有子元素，包装在span中
    const span = document.createElement('span')
    span.innerHTML = htmlContent
    applyFormatToElement(span)
    tempDiv.appendChild(span)
  }

  editor.selection.setContent(tempDiv.innerHTML)
}

/**
 * 只粘贴文本内容
 * @param {Object} editor - TinyMCE编辑器实例
 */
export async function pasteTextOnly(editor) {
  if (!editor) return

  try {
    // 尝试从剪贴板读取文本
    if (navigator.clipboard && navigator.clipboard.readText) {
      const text = await navigator.clipboard.readText()
      if (text) {
        // 处理文本内容，保留换行但移除HTML标签
        const processedText = text
          // 先移除所有HTML标签
          .replace(/<[^>]*>/g, '')
          // 转义HTML特殊字符
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;')
          // 处理换行：将连续的换行符转换为段落
          .replace(/\r\n/g, '\n')
          .replace(/\r/g, '\n')
          .split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0)
          .map(line => `<p>${line}</p>`)
          .join('')

        // 如果处理后的文本为空，插入原始文本
        const finalContent = processedText || text.replace(/\n/g, '<br>')

        editor.insertContent(finalContent)

        if (window.ElMessage) {
          window.ElMessage.success('已粘贴纯文本内容')
        }
        return
      }
    }

    // 回退方案：提示用户使用快捷键
    if (window.ElMessage) {
      window.ElMessage.info('请使用 Ctrl+Shift+V 粘贴纯文本，或复制文本后重试')
    }
  } catch (error) {
    console.warn('粘贴文本失败:', error)

    // 如果是权限错误，提供更具体的指导
    if (error.name === 'NotAllowedError') {
      if (window.ElMessage) {
        window.ElMessage.warning('需要剪贴板权限。请使用 Ctrl+Shift+V 粘贴纯文本')
      }
    } else {
      if (window.ElMessage) {
        window.ElMessage.warning('粘贴失败，请使用 Ctrl+Shift+V 粘贴纯文本')
      }
    }
  }
}

/**
 * 设置粘贴为文本模式
 * @param {Object} editor - TinyMCE编辑器实例
 * @param {boolean} enabled - 是否启用粘贴为文本模式
 */
export function setPasteAsTextMode(editor, enabled) {
  if (!editor) return

  if (enabled) {
    // 启用粘贴为文本模式
    editor.settings.paste_as_text = true
    if (window.ElMessage) {
      window.ElMessage.success('已启用粘贴为文本模式，现在粘贴将自动去除格式')
    }
  } else {
    // 禁用粘贴为文本模式
    editor.settings.paste_as_text = false
    if (window.ElMessage) {
      window.ElMessage.info('已禁用粘贴为文本模式，现在粘贴将保留格式')
    }
  }
}
