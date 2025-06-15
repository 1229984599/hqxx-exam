<template>
  <div class="rich-text-editor">
    <div class="editor-toolbar">
      <el-button-group>
        <el-button
          size="small"
          @click="formatText('bold')"
          :class="{ active: isFormatActive('bold') }"
        >
          <strong>B</strong>
        </el-button>
        <el-button
          size="small"
          @click="formatText('italic')"
          :class="{ active: isFormatActive('italic') }"
        >
          <em>I</em>
        </el-button>
        <el-button
          size="small"
          @click="formatText('underline')"
          :class="{ active: isFormatActive('underline') }"
        >
          <u>U</u>
        </el-button>
      </el-button-group>

      <el-button-group>
        <el-button
          size="small"
          @click="setFontSize('24px')"
        >
          大字
        </el-button>
        <el-button
          size="small"
          @click="setFontSize('18px')"
        >
          中字
        </el-button>
        <el-button
          size="small"
          @click="setFontSize('14px')"
        >
          小字
        </el-button>
      </el-button-group>

      <el-button-group>
        <el-button
          size="small"
          @click="setTextAlign('left')"
        >
          左对齐
        </el-button>
        <el-button
          size="small"
          @click="setTextAlign('center')"
        >
          居中
        </el-button>
        <el-button
          size="small"
          @click="setTextAlign('right')"
        >
          右对齐
        </el-button>
      </el-button-group>

      <el-button-group>
        <el-button
          size="small"
          @click="addPinyin"
          :disabled="!hasSelection"
          type="primary"
        >
          <el-icon><Reading /></el-icon>
          注音
        </el-button>
        <el-button
          size="small"
          @click="removePinyin"
          :disabled="!hasSelection"
        >
          <el-icon><Delete /></el-icon>
          移除注音
        </el-button>
      </el-button-group>

      <el-button-group>
        <el-button
          size="small"
          @click="insertTemplate"
          type="success"
        >
          <el-icon><DocumentAdd /></el-icon>
          插入模板
        </el-button>
        <el-button
          size="small"
          @click="clearAll"
          type="warning"
        >
          <el-icon><Close /></el-icon>
          清空
        </el-button>
      </el-button-group>
    </div>

    <div
      ref="editorRef"
      class="editor-container"
      contenteditable="true"
      @input="handleInput"
      @mouseup="checkSelection"
      @keyup="checkSelection"
      @paste="handlePaste"
      :placeholder="placeholder"
      v-html="content"
    ></div>

    <div class="editor-footer">
      <span class="word-count">字数: {{ wordCount }}</span>
      <span class="selection-info" v-if="selectedText">
        已选择: "{{ selectedText }}"
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Reading, Delete, Close, DocumentAdd } from '@element-plus/icons-vue'
import { pinyin } from 'pinyin-pro'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入题目内容...'
  },
  height: {
    type: String,
    default: '300px'
  }
})

const emit = defineEmits(['update:modelValue'])

const editorRef = ref(null)
const content = ref('')
const selectedText = ref('')
const hasSelection = computed(() => selectedText.value.length > 0)
const wordCount = computed(() => {
  const text = content.value.replace(/<[^>]*>/g, '')
  return text.replace(/\s/g, '').length
})

onMounted(() => {
  content.value = props.modelValue || ''
  if (editorRef.value) {
    editorRef.value.style.height = props.height
    editorRef.value.innerHTML = content.value
  }
})

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal || ''
    if (editorRef.value) {
      editorRef.value.innerHTML = content.value
    }
  }
})

// 处理输入
function handleInput() {
  if (editorRef.value) {
    content.value = editorRef.value.innerHTML
    emit('update:modelValue', content.value)
  }
}

// 处理粘贴
function handlePaste(event) {
  event.preventDefault()
  const text = event.clipboardData.getData('text/plain')
  document.execCommand('insertText', false, text)
  handleInput()
}

// 检查选中文本
function checkSelection() {
  const selection = window.getSelection()
  if (selection && selection.toString()) {
    selectedText.value = selection.toString().trim()
  } else {
    selectedText.value = ''
  }
}

// 格式化文本
function formatText(command) {
  document.execCommand(command, false, null)
  handleInput()
}

// 检查格式是否激活
function isFormatActive(command) {
  return document.queryCommandState(command)
}

// 设置字体大小
function setFontSize(size) {
  const selection = window.getSelection()
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0)
    if (!range.collapsed) {
      const span = document.createElement('span')
      span.style.fontSize = size
      try {
        range.surroundContents(span)
        handleInput()
      } catch (e) {
        // 如果选择跨越多个元素，使用execCommand
        document.execCommand('fontSize', false, '7')
        const fontElements = editorRef.value.querySelectorAll('font[size="7"]')
        fontElements.forEach(el => {
          el.style.fontSize = size
          el.removeAttribute('size')
        })
        handleInput()
      }
    }
  }
}

// 设置文本对齐
function setTextAlign(align) {
  if (!align || typeof align !== 'string') return

  const command = 'justify' + align.charAt(0).toUpperCase() + align.slice(1)
  document.execCommand(command, false, null)
  handleInput()
}

// 添加注音
function addPinyin() {
  if (!selectedText.value) {
    ElMessage.warning('请先选择要注音的文字')
    return
  }

  try {
    const text = selectedText.value
    const pinyinText = pinyin(text, {
      toneType: 'symbol',
      type: 'array'
    })

    // 创建注音HTML
    let rubyHtml = ''
    for (let i = 0; i < text.length; i++) {
      const char = text[i]
      const py = pinyinText[i] || ''

      if (/[\u4e00-\u9fa5]/.test(char)) {
        // 中文字符添加注音
        rubyHtml += `<ruby style="ruby-align: center;">${char}<rt style="font-size: 0.7em; color: #666;">${py}</rt></ruby>`
      } else {
        // 非中文字符直接添加
        rubyHtml += char
      }
    }

    // 替换选中文本
    const selection = window.getSelection()
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0)
      range.deleteContents()
      const fragment = range.createContextualFragment(rubyHtml)
      range.insertNode(fragment)
      selection.removeAllRanges()
    }

    selectedText.value = ''
    handleInput() // 更新内容

    ElMessage.success('注音添加成功')
  } catch (error) {
    console.error('注音失败:', error)
    ElMessage.error('注音失败，请重试')
  }
}

// 移除注音
function removePinyin() {
  if (!selectedText.value) {
    ElMessage.warning('请先选择要移除注音的文字')
    return
  }

  try {
    const selection = window.getSelection()
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0)
      const container = range.commonAncestorContainer

      // 查找并移除ruby标签
      let element = container.nodeType === Node.TEXT_NODE ? container.parentElement : container
      const rubyElements = element.querySelectorAll('ruby')

      rubyElements.forEach(ruby => {
        // 只保留中文字符，移除拼音
        const text = ruby.firstChild ? ruby.firstChild.textContent : ''
        ruby.replaceWith(document.createTextNode(text))
      })

      selectedText.value = ''
      handleInput() // 更新内容
      ElMessage.success('注音移除成功')
    }
  } catch (error) {
    console.error('移除注音失败:', error)
    ElMessage.error('移除注音失败，请重试')
  }
}

// 插入模板
function insertTemplate() {
  ElMessageBox.prompt('请选择要插入的模板：', '插入模板', {
    confirmButtonText: '插入',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '选择模板类型：\n1 - 拼音练习\n2 - 汉字练习\n3 - 数学计算\n4 - 阅读理解\n5 - 自定义',
    inputValue: '1'
  }).then(({ value }) => {
    let template = ''

    switch (value.trim()) {
      case '1':
        template = `
          <div style="text-align: center; margin: 20px 0;">
            <h3 style="color: #409eff; margin-bottom: 20px;">请读出下面的拼音：</h3>
            <div style="font-size: 36px; letter-spacing: 8px; margin: 30px 0;">
              ba  bi  bu  bo
            </div>
          </div>
        `
        break
      case '2':
        template = `
          <div style="text-align: center; margin: 20px 0;">
            <h3 style="color: #f56c6c; margin-bottom: 20px;">请读出下面的汉字：</h3>
            <div style="font-size: 48px; letter-spacing: 20px; margin: 30px 0;">
              大  小  多  少
            </div>
          </div>
        `
        break
      case '3':
        template = `
          <div style="text-align: center; margin: 20px 0;">
            <h3 style="color: #e6a23c; margin-bottom: 20px;">计算下面的题目：</h3>
            <div style="font-size: 32px; margin: 30px 0;">
              5 + 3 = ?
            </div>
            <div style="border: 2px solid #ddd; width: 100px; height: 50px; margin: 20px auto;"></div>
          </div>
        `
        break
      case '4':
        template = `
          <div style="margin: 20px 0;">
            <h3 style="color: #67c23a; margin-bottom: 15px;">阅读下面的短文，回答问题：</h3>
            <div style="background: #f5f7fa; padding: 20px; border-radius: 8px; margin: 20px 0; line-height: 2;">
              请在这里输入阅读材料...
            </div>
            <div style="margin-top: 20px;">
              <strong>问题：</strong>请在这里输入问题...
            </div>
          </div>
        `
        break
      case '5':
        template = `
          <div style="margin: 20px 0;">
            <h3 style="margin-bottom: 15px;">题目要求：</h3>
            <div style="margin: 20px 0; line-height: 2;">
              请在这里输入自定义内容...
            </div>
          </div>
        `
        break
      default:
        ElMessage.warning('请输入有效的模板编号（1-5）')
        return
    }

    const selection = window.getSelection()
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0)
      const fragment = range.createContextualFragment(template)
      range.insertNode(fragment)
      selection.removeAllRanges()
      handleInput()
      ElMessage.success('模板插入成功')
    }
  }).catch(() => {
    // 用户取消
  })
}

// 清空内容
function clearAll() {
  content.value = ''
  if (editorRef.value) {
    editorRef.value.innerHTML = ''
  }
  selectedText.value = ''
  emit('update:modelValue', '')
  ElMessage.success('内容已清空')
}
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
}

.editor-toolbar {
  padding: 8px 12px;
  background: #fafafa;
  border-bottom: 1px solid #d9d9d9;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.editor-toolbar .el-button.active {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.editor-toolbar .el-button-group {
  margin-right: 8px;
}

.editor-container {
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  min-height: 200px;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
  overflow-y: auto;
}

.editor-container:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.editor-container:empty:before {
  content: attr(placeholder);
  color: #c0c4cc;
  pointer-events: none;
}

.editor-container p {
  margin: 8px 0;
}

.editor-container h1, .editor-container h2, .editor-container h3 {
  margin: 16px 0 12px 0;
  font-weight: bold;
}

.editor-container h1 {
  font-size: 24px;
}

.editor-container h2 {
  font-size: 20px;
}

.editor-container h3 {
  font-size: 18px;
}

.editor-container ruby {
  ruby-align: center;
  margin: 0 2px;
}

.editor-container rt {
  font-size: 0.7em !important;
  color: #666 !important;
  line-height: 1.2;
}

.editor-footer {
  padding: 8px 12px;
  background: #fafafa;
  border-top: 1px solid #d9d9d9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.word-count {
  color: #999;
}

.selection-info {
  color: #409eff;
  font-weight: 500;
}

/* 编辑器样式覆盖 */
:deep(.w-e-text-container) {
  background: white !important;
}

:deep(.w-e-text-placeholder) {
  color: #c0c4cc !important;
}

:deep(ruby) {
  ruby-align: center;
}

:deep(rt) {
  font-size: 0.7em !important;
  color: #666 !important;
  line-height: 1.2;
}
</style>
