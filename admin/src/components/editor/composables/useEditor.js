/**
 * 编辑器核心逻辑 Composable
 */

import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { createEditorConfig } from '../config/editorConfig.js'
import {
  cleanWordContent,
  calculateContentStats,
  trySmartSelection,
  adjustFontSize,
  setLineHeight,
  extractFormat,
  applyFormat
} from '../utils/contentUtils.js'
import {
  getAllPinyinOptions,
  handlePinyinNavigation,
  handlePinyinEdit,
  showPinyinContextMenu,
  addPinyinToText,
  removePinyinFromText,
  setEditorPinyinEditFunction
} from '../utils/pinyinUtils.js'

export function useEditor(props, emit) {
  // 编辑器实例和内容
  const editorInstance = ref(null)
  const content = ref('')
  const selectedText = ref('')

  // 统计相关
  const contentStats = ref({
    characters: 0,
    charactersNoSpaces: 0,
    words: 0,
    paragraphs: 0,
    sentences: 0,
    readingTime: 0,
    chineseChars: 0,
    pinyinAnnotations: 0
  })

  // 格式刷相关
  const formatBrushActive = ref(false)
  const copiedFormat = ref(null)



  // 计算属性
  const hasSelection = computed(() => selectedText.value.length > 0)
  const wordCount = computed(() => {
    const text = content.value.replace(/<[^>]*>/g, '')
    return text.replace(/\s/g, '').length
  })

  // 编辑器配置
  const editorConfig = computed(() => {
    const baseConfig = createEditorConfig(props)
    
    return {
      ...baseConfig,
      setup: (editor) => {
        editorInstance.value = editor
        setupEditorEvents(editor)
        setupEditorButtons(editor)

        // 设置拼音编辑函数引用
        setEditorPinyinEditFunction(openPinyinEditDialog)
      }
    }
  })

  // 监听外部值变化
  watch(() => props.modelValue, (newVal) => {
    if (newVal !== content.value) {
      content.value = newVal || ''
    }
  }, { immediate: true })

  // 对话框状态变量（需要在函数使用前定义）
  const showSymbolDialog = ref(false)
  const showTemplateDialog = ref(false)
  const showPreviewDialog = ref(false)
  const showPinyinEditDialog = ref(false)
  const showCodeEditorDialog = ref(false)

  // 浮动工具栏
  const showFloatingToolbar = ref(false)
  const floatingToolbarSelection = ref({})
  const currentFormats = ref({})

  // 拼音编辑数据
  const pinyinEditData = ref({
    character: '',
    currentPinyin: '',
    pinyinOptions: []
  })

  let pinyinEditCallbacks = {
    onSelect: null,
    onRemove: null
  }

  // 浮动工具栏处理
  function handleFloatingToolbar(editor) {
    const selection = editor.selection
    const selectedContent = selection.getContent({ format: 'text' })

    console.log('浮动工具栏处理:', {
      selectedContent,
      hasContent: selectedContent && selectedContent.trim().length > 0,
      currentShowState: showFloatingToolbar.value
    })

    if (selectedContent && selectedContent.trim().length > 0) {
      // 有选中内容，显示浮动工具栏
      const range = selection.getRng()

      // 获取编辑器iframe的位置信息
      const editorIframe = editor.getContainer().querySelector('iframe')
      const editorBody = editor.getBody()

      console.log('编辑器信息:', {
        iframe: editorIframe ? editorIframe.getBoundingClientRect() : null,
        body: editorBody ? editorBody.getBoundingClientRect() : null,
        range: range
      })

      floatingToolbarSelection.value = {
        range: range,
        content: selectedContent,
        editor: editor,
        iframe: editorIframe
      }

      console.log('设置浮动工具栏显示:', floatingToolbarSelection.value)

      // 延迟获取格式状态，确保选择已稳定
      setTimeout(() => {
        if (editor && editor.selection) {
          currentFormats.value = {
            bold: editor.queryCommandState('Bold'),
            italic: editor.queryCommandState('Italic'),
            underline: editor.queryCommandState('Underline')
          }
          console.log('当前格式状态:', currentFormats.value)
        }
      }, 10)

      showFloatingToolbar.value = true
      console.log('浮动工具栏已设置为显示')
    } else {
      // 没有选中内容，隐藏浮动工具栏
      showFloatingToolbar.value = false
      console.log('浮动工具栏已隐藏')
    }
  }

  // 设置编辑器事件
  function setupEditorEvents(editor) {
    editor.on('init', () => {
      console.log('TinyMCE 编辑器初始化完成')
    })

    editor.on('SelectionChange', () => {
      const selection = editor.selection.getContent({ format: 'text' })
      selectedText.value = selection.trim()

      console.log('SelectionChange 事件触发:', {
        selectedText: selectedText.value,
        hasSelection: selectedText.value.length > 0
      })

      // 处理浮动工具栏显示
      handleFloatingToolbar(editor)
    })

    editor.on('Change', () => {
      content.value = editor.getContent()
      emit('update:modelValue', content.value)
    })

    // 键盘事件处理
    editor.on('keydown', (e) => {
      // 字体大小调整快捷键
      if (e.ctrlKey || e.metaKey) {
        if (e.key === '=' || e.key === '+') {
          e.preventDefault()
          increaseFontSize()
        } else if (e.key === '-') {
          e.preventDefault()
          decreaseFontSize()
        }
      }

      // 拼音导航处理
      handlePinyinNavigation(e, editor)
    })

    // 双击事件处理 - 双击拼音可以编辑
    let lastClickTime = 0
    let lastClickElement = null

    editor.on('dblclick', (e) => {
      const currentTime = Date.now()
      const target = e.target

      // 防抖：如果是同一个元素在短时间内重复双击，忽略
      if (lastClickElement === target && currentTime - lastClickTime < 500) {
        e.preventDefault()
        e.stopPropagation()
        return
      }

      // 检查是否点击在拼音元素上
      let rubyElement = null
      if (target) {
        // 直接检查target是否是ruby元素
        if (target.tagName === 'RUBY' && target.classList.contains('pinyin-ruby')) {
          rubyElement = target
        }
        // 检查target的父元素
        else if (target.closest) {
          rubyElement = target.closest('ruby.pinyin-ruby')
        }
        // 手动向上查找
        else {
          let current = target
          while (current && current.parentNode) {
            if (current.tagName === 'RUBY' && current.classList.contains('pinyin-ruby')) {
              rubyElement = current
              break
            }
            current = current.parentNode
          }
        }
      }

      if (rubyElement) {
        e.preventDefault()
        e.stopPropagation()

        // 记录点击信息
        lastClickTime = currentTime
        lastClickElement = target

        handlePinyinEdit(rubyElement, editor)
      }
    })

    // 右键菜单支持
    editor.on('contextmenu', (e) => {
      const target = e.target

      // 检查是否点击在拼音元素上
      let rubyElement = null
      if (target) {
        // 直接检查target是否是ruby元素
        if (target.tagName === 'RUBY' && target.classList.contains('pinyin-ruby')) {
          rubyElement = target
        }
        // 检查target的父元素
        else if (target.closest) {
          rubyElement = target.closest('ruby.pinyin-ruby')
        }
        // 手动向上查找
        else {
          let current = target
          while (current && current.parentNode) {
            if (current.tagName === 'RUBY' && current.classList.contains('pinyin-ruby')) {
              rubyElement = current
              break
            }
            current = current.parentNode
          }
        }
      }

      if (rubyElement) {
        showPinyinContextMenu(rubyElement, e, editor)
      }
    })

    // 点击事件处理 - 点击编辑器外部隐藏浮动工具栏
    editor.on('click', (e) => {
      // 延迟检查，确保选择状态已更新
      setTimeout(() => {
        const selectedContent = editor.selection.getContent({ format: 'text' })
        if (!selectedContent || selectedContent.trim().length === 0) {
          showFloatingToolbar.value = false
        }
      }, 10)
    })

    // 图片样式应用
    setupImageStyling(editor)

    // 粘贴预处理
    editor.on('paste', (e) => {
      setTimeout(() => {
        const images = editor.getBody().querySelectorAll('img:not([data-styled])')
        if (images.length > 0) {
          applyImageStyles(images, true)
        }
      }, 300)
    })
  }

  // 对话框控制函数（需要在按钮注册之前定义）
  function openSymbolDialog() {
    showSymbolDialog.value = true
  }

  function openTemplateDialog() {
    showTemplateDialog.value = true
  }

  function openResponsivePreview() {
    showPreviewDialog.value = true
  }

  function openCodeEditor() {
    showCodeEditorDialog.value = true
  }

  function handleCodeApply(newCode) {
    if (editorInstance.value) {
      editorInstance.value.setContent(newCode)
      content.value = newCode
      emit('update:modelValue', newCode)
    }
  }

  // 设置编辑器按钮
  function setupEditorButtons(editor) {
    // 添加拼音注音按钮
    editor.ui.registry.addButton('addpinyin', {
      text: '添加拼音',
      tooltip: '为选中的文字添加拼音注音\n💡 多音字支持：双击编辑 | 右键快速切换 | Delete删除',
      onAction: () => addPinyinAnnotation()
    })

    // 移除拼音按钮
    editor.ui.registry.addButton('removepinyin', {
      text: '移除拼音',
      tooltip: '移除选中文字的拼音注音',
      onAction: () => removePinyinAnnotation()
    })

    // 智能拼音按钮
    editor.ui.registry.addButton('smartpinyin', {
      text: '智能拼音',
      tooltip: '为所有中文字符自动添加拼音注音',
      onAction: () => addSmartPinyinAnnotation()
    })



    // 字体大小调整按钮
    editor.ui.registry.addButton('fontsizeplus', {
      text: 'A+',
      tooltip: '增大字体 (Ctrl/Cmd + +)',
      onAction: () => increaseFontSize()
    })

    editor.ui.registry.addButton('fontsizeminus', {
      text: 'A-',
      tooltip: '减小字体 (Ctrl/Cmd + -)',
      onAction: () => decreaseFontSize()
    })

    // 行间距调整按钮
    editor.ui.registry.addMenuButton('lineheight', {
      text: '行距',
      tooltip: '调整行间距',
      fetch: (callback) => {
        const items = [
          { type: 'menuitem', text: '单倍行距 (1.0)', onAction: () => setLineHeightHandler('1.0') },
          { type: 'menuitem', text: '1.15倍行距', onAction: () => setLineHeightHandler('1.15') },
          { type: 'menuitem', text: '1.5倍行距', onAction: () => setLineHeightHandler('1.5') },
          { type: 'menuitem', text: '双倍行距 (2.0)', onAction: () => setLineHeightHandler('2.0') },
          { type: 'menuitem', text: '2.5倍行距', onAction: () => setLineHeightHandler('2.5') },
          { type: 'menuitem', text: '3倍行距', onAction: () => setLineHeightHandler('3.0') }
        ]
        callback(items)
      }
    })

    // 内容统计按钮
    editor.ui.registry.addButton('contentstats', {
      text: '📊 统计',
      tooltip: '查看内容统计信息',
      onAction: () => showContentStats()
    })

    // 图片样式按钮
    editor.ui.registry.addButton('styleimages', {
      text: '🖼️ 图片样式',
      tooltip: '为所有图片应用响应式样式（宽度100%，高度自适应）',
      onAction: () => styleAllImages()
    })

    // 添加快速符号按钮
    editor.ui.registry.addButton('quicksymbols', {
      text: '🔣 符号',
      tooltip: '快速插入常用符号和表情',
      onAction: () => openSymbolDialog()
    })

    // 添加模板按钮
    editor.ui.registry.addButton('inserttemplate', {
      text: '📋 模板',
      tooltip: '插入预设模板',
      onAction: () => openTemplateDialog()
    })

    // 添加响应式预览按钮
    editor.ui.registry.addButton('responsivepreview', {
      text: '👁️ 预览',
      tooltip: '响应式预览 - 查看内容在不同设备上的显示效果',
      onAction: () => openResponsivePreview()
    })

    // 添加高级代码编辑器按钮（替换默认的code按钮）
    editor.ui.registry.addButton('advancedcode', {
      text: '💻 源码',
      tooltip: '高级源代码编辑器 - 支持语法高亮、格式化和验证',
      onAction: () => openCodeEditor()
    })
  }

  // 图片样式处理
  function setupImageStyling(editor) {
    const applyImageStyles = (images, showMessage = false) => {
      if (!props.autoStyleImages) return

      let styledCount = 0
      images.forEach(img => {
        if (!img.hasAttribute('data-styled')) {
          img.style.width = '100%'
          img.style.height = 'auto'
          img.style.maxWidth = '100%'
          img.style.display = 'block'
          img.style.margin = '10px auto'
          img.style.borderRadius = '8px'
          img.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
          img.style.transition = 'all 0.3s ease'
          img.setAttribute('data-styled', 'true')
          styledCount++
        }
      })

      if (showMessage && styledCount > 0) {
        ElMessage.success(`已为 ${styledCount} 张图片应用响应式样式`)
      }
    }

    // 监听各种图片插入事件
    editor.on('NodeChange', (e) => {
      const images = editor.getBody().querySelectorAll('img:not([data-styled])')
      if (images.length > 0) {
        applyImageStyles(images)
      }
    })

    editor.on('SetContent', (e) => {
      setTimeout(() => {
        const images = editor.getBody().querySelectorAll('img:not([data-styled])')
        if (images.length > 0) {
          applyImageStyles(images, true)
        }
      }, 100)
    })

    editor.on('ExecCommand', (e) => {
      if (e.command === 'mceImage' || e.command === 'mceInsertContent') {
        setTimeout(() => {
          const images = editor.getBody().querySelectorAll('img:not([data-styled])')
          if (images.length > 0) {
            applyImageStyles(images, true)
          }
        }, 200)
      }
    })
  }

  // 拼音功能
  function addPinyinAnnotation() {
    if (!editorInstance.value || !selectedText.value) {
      ElMessage.warning('请先选择要注音的文字')
      return
    }

    try {
      const annotatedHtml = addPinyinToText(editorInstance.value, selectedText.value)
      editorInstance.value.selection.setContent(annotatedHtml)

      // 光标定位
      setTimeout(() => {
        try {
          const body = editorInstance.value.getBody()
          const lastRuby = body.querySelector('ruby.pinyin-ruby:last-of-type')

          if (lastRuby) {
            const range = editorInstance.value.dom.createRng()
            const spaceNode = editorInstance.value.getDoc().createTextNode(' ')

            if (lastRuby.nextSibling) {
              lastRuby.parentNode.insertBefore(spaceNode, lastRuby.nextSibling)
            } else {
              lastRuby.parentNode.appendChild(spaceNode)
            }

            range.setStart(spaceNode, 1)
            range.collapse(true)
            editorInstance.value.selection.setRng(range)
          }
        } catch (error) {
          console.error('光标定位失败:', error)
        }
      }, 10)

      selectedText.value = ''
      ElMessage.success('拼音注音添加成功')
    } catch (error) {
      console.error('拼音注音错误:', error)
      ElMessage.error('添加拼音注音失败')
    }
  }

  function removePinyinAnnotation() {
    if (!editorInstance.value) {
      ElMessage.warning('编辑器未初始化')
      return
    }

    const selectedHtml = editorInstance.value.selection.getContent()
    if (!selectedHtml) {
      ElMessage.warning('请先选择要移除注音的文字')
      return
    }

    const cleanHtml = removePinyinFromText(selectedHtml)
    editorInstance.value.selection.setContent(cleanHtml)
    selectedText.value = ''
    ElMessage.success('拼音注音移除成功')
  }

  function addSmartPinyinAnnotation() {
    if (!editorInstance.value) {
      ElMessage.warning('编辑器未初始化')
      return
    }

    const currentContent = editorInstance.value.getContent()
    if (!currentContent) {
      ElMessage.warning('编辑器内容为空')
      return
    }

    try {
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = currentContent

      function processTextNodes(node) {
        if (node.nodeType === Node.TEXT_NODE) {
          const text = node.textContent
          if (text && /[\u4e00-\u9fff]/.test(text)) {
            const annotatedHtml = addPinyinToText(editorInstance.value, text)
            const wrapper = document.createElement('span')
            wrapper.innerHTML = annotatedHtml
            node.parentNode.replaceChild(wrapper, node)
          }
        } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'RUBY') {
          const children = Array.from(node.childNodes)
          children.forEach(child => processTextNodes(child))
        }
      }

      processTextNodes(tempDiv)
      tempDiv.innerHTML = tempDiv.innerHTML.replace(/<span>([^<]*)<\/span>/g, '$1')

      editorInstance.value.setContent(tempDiv.innerHTML)
      ElMessage.success('智能拼音注音添加成功')
    } catch (error) {
      console.error('智能拼音注音错误:', error)
      ElMessage.error('智能拼音注音失败')
    }
  }

  // 字体大小调整
  function increaseFontSize() {
    if (!editorInstance.value) return
    adjustFontSize(editorInstance.value, 2)
  }

  function decreaseFontSize() {
    if (!editorInstance.value) return
    adjustFontSize(editorInstance.value, -2)
  }

  // 行间距设置
  function setLineHeightHandler(lineHeight) {
    if (!editorInstance.value) return
    setLineHeight(editorInstance.value, lineHeight)
  }



  // 内容统计
  function showContentStats() {
    if (!editorInstance.value) return

    const htmlContent = editorInstance.value.getContent()
    const textContent = editorInstance.value.getContent({ format: 'text' })
    contentStats.value = calculateContentStats(htmlContent, textContent)
    
    return contentStats.value
  }

  // 图片样式应用
  function styleAllImages() {
    if (!editorInstance.value) return

    const images = editorInstance.value.getBody().querySelectorAll('img')
    let styledCount = 0

    images.forEach(img => {
      img.style.width = '100%'
      img.style.height = 'auto'
      img.style.maxWidth = '100%'
      img.style.display = 'block'
      img.style.margin = '10px auto'
      img.style.borderRadius = '8px'
      img.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
      img.style.transition = 'all 0.3s ease'
      img.setAttribute('data-styled', 'true')
      styledCount++
    })

    if (styledCount > 0) {
      ElMessage.success(`已为 ${styledCount} 张图片应用响应式样式`)
    } else {
      ElMessage.info('当前文档中没有图片')
    }
  }





  // 拼音编辑相关函数
  function openPinyinEditDialog(character, currentPinyin, pinyinOptions, onSelect, onRemove) {
    if (showPinyinEditDialog.value) {
      return
    }

    pinyinEditData.value = {
      character,
      currentPinyin,
      pinyinOptions
    }

    pinyinEditCallbacks = {
      onSelect,
      onRemove
    }

    showPinyinEditDialog.value = true
  }

  function handlePinyinConfirm(selectedPinyin) {
    if (pinyinEditCallbacks.onSelect) {
      pinyinEditCallbacks.onSelect(selectedPinyin)
    }
    showPinyinEditDialog.value = false
  }

  function handlePinyinRemove() {
    if (pinyinEditCallbacks.onRemove) {
      pinyinEditCallbacks.onRemove()
    }
    showPinyinEditDialog.value = false
  }

  // 浮动工具栏操作函数
  function floatingToggleFormat(format) {
    if (!editorInstance.value) return

    // 保存当前选择
    const selection = editorInstance.value.selection
    const range = selection.getRng()

    // 执行格式命令
    editorInstance.value.execCommand(format)

    // 恢复选择
    setTimeout(() => {
      try {
        selection.setRng(range)
        // 更新格式状态
        currentFormats.value[format.toLowerCase()] = editorInstance.value.queryCommandState(format)
      } catch (error) {
        console.warn('恢复选择失败:', error)
      }
    }, 10)
  }

  function floatingAdjustFontSize(delta) {
    if (!editorInstance.value) return
    adjustFontSize(editorInstance.value, delta)
  }

  function floatingApplyTextColor(color) {
    if (!editorInstance.value) return

    // 保存当前选择
    const selection = editorInstance.value.selection
    const range = selection.getRng()

    // 应用文字颜色
    editorInstance.value.execCommand('ForeColor', false, color)

    // 恢复选择
    setTimeout(() => {
      try {
        selection.setRng(range)
      } catch (error) {
        console.warn('恢复选择失败:', error)
      }
    }, 10)
  }

  function floatingApplyBgColor(color) {
    if (!editorInstance.value) return

    // 保存当前选择
    const selection = editorInstance.value.selection
    const range = selection.getRng()

    // 应用背景颜色
    editorInstance.value.execCommand('BackColor', false, color)

    // 恢复选择
    setTimeout(() => {
      try {
        selection.setRng(range)
      } catch (error) {
        console.warn('恢复选择失败:', error)
      }
    }, 10)
  }

  function floatingAddPinyin() {
    if (!editorInstance.value) return
    addPinyinAnnotation()
    showFloatingToolbar.value = false
  }

  function floatingToggleFormatBrush() {
    // 这里会调用现有的格式刷功能
    // TODO: 实现格式刷功能
  }

  function floatingClearFormat() {
    if (!editorInstance.value) return
    editorInstance.value.execCommand('RemoveFormat')
    showFloatingToolbar.value = false
  }

  // 处理输入和变化
  function handleInput(event) {
    content.value = event.target.getContent()
    emit('update:modelValue', content.value)
  }

  function handleChange(event) {
    content.value = event.target.getContent()
    emit('update:modelValue', content.value)
  }

  function handleSelectionChange(event) {
    if (event.target) {
      const selection = event.target.selection.getContent({ format: 'text' })
      selectedText.value = selection.trim()

      console.log('选择变化:', {
        selectedText: selectedText.value,
        hasSelection: selectedText.value.length > 0
      })

      // 处理浮动工具栏显示
      handleFloatingToolbar(event.target)
    }
  }



  return {
    // 响应式数据
    editorInstance,
    content,
    selectedText,
    contentStats,
    formatBrushActive,
    copiedFormat,
    showSymbolDialog,
    showTemplateDialog,
    showPreviewDialog,
    showPinyinEditDialog,
    pinyinEditData,
    showFloatingToolbar,
    floatingToolbarSelection,
    currentFormats,
    showCodeEditorDialog,

    // 计算属性
    hasSelection,
    wordCount,
    editorConfig,

    // 方法
    addPinyinAnnotation,
    removePinyinAnnotation,
    addSmartPinyinAnnotation,
    increaseFontSize,
    decreaseFontSize,
    setLineHeightHandler,
    showContentStats,
    styleAllImages,
    openSymbolDialog,
    openTemplateDialog,
    openResponsivePreview,
    openCodeEditor,
    handleCodeApply,
    openPinyinEditDialog,
    handlePinyinConfirm,
    handlePinyinRemove,
    floatingToggleFormat,
    floatingAdjustFontSize,
    floatingApplyTextColor,
    floatingApplyBgColor,
    floatingAddPinyin,
    floatingToggleFormatBrush,
    floatingClearFormat,
    handleInput,
    handleChange,
    handleSelectionChange
  }
}
