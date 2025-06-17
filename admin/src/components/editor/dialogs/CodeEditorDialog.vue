<template>
  <el-dialog
    v-model="visible"
    width="90%"
    height="90%"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :append-to-body="true"
    class="monaco-editor-dialog"
    @close="handleClose"
  >
    <div class="monaco-editor-container">
      <!-- Monaco编辑器容器 -->
      <div
        ref="monacoContainer"
        class="monaco-editor-wrapper"
      ></div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <el-button @click="formatCode" :loading="formatting">
            🎨 格式化
          </el-button>
          <el-button @click="toggleTheme">
            {{ isDarkTheme ? '☀️ 浅色' : '🌙 深色' }}
          </el-button>
        </div>
        <div class="footer-right">
          <el-button @click="handleClose">取消</el-button>
          <el-button @click="resetCode" type="warning">重置</el-button>
          <el-button @click="applyCode" type="primary" :loading="applying">
            应用更改
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import loader from '@monaco-editor/loader'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  content: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'apply'])

// 响应式数据
const visible = ref(false)
const monacoContainer = ref(null)
const originalContent = ref('')
const formatting = ref(false)
const applying = ref(false)

// 编辑器实例和配置
let monacoEditor = null
const isDarkTheme = ref(true)

// 监听显示状态
watch(() => props.modelValue, async (newVal) => {
  visible.value = newVal
  if (newVal) {
    originalContent.value = props.content
    await nextTick()
    await initMonacoEditor()
  }
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
  if (!newVal && monacoEditor) {
    // 对话框关闭时清理编辑器
    monacoEditor.dispose()
    monacoEditor = null
  }
})

// Monaco Editor 初始化
async function initMonacoEditor() {
  if (!monacoContainer.value) return

  try {
    // 尝试多个CDN源，提高可用性（包含国内CDN）
    const cdnSources = [
      'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs',
      'https://unpkg.com/monaco-editor@0.45.0/min/vs',
      'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs',
      'https://registry.npmmirror.com/monaco-editor/0.45.0/files/min/vs',
      'https://cdn.bootcdn.net/ajax/libs/monaco-editor/0.45.0/min/vs'
    ]

    let monaco = null
    for (let i = 0; i < cdnSources.length; i++) {
      const cdnUrl = cdnSources[i]
      try {
        // 重置loader配置
        loader.config({
          paths: {
            vs: cdnUrl
          }
        })

        // 设置超时
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('加载超时')), 10000)
        })

        monaco = await Promise.race([
          loader.init(),
          timeoutPromise
        ])

        break
      } catch (error) {
        if (i === cdnSources.length - 1) {
          // 只在所有CDN都失败时显示错误
          ElMessage.error('Monaco Editor 加载失败，请检查网络连接')
        }
        continue
      }
    }

    if (!monaco) {
      throw new Error('所有CDN源都无法加载Monaco Editor')
    }

    // 创建编辑器实例
    monacoEditor = monaco.editor.create(monacoContainer.value, {
      value: props.content || '',
      language: 'html',
      theme: isDarkTheme.value ? 'vs-dark' : 'vs',
      automaticLayout: true,
      wordWrap: 'on',
      minimap: {
        enabled: false
      },
      fontSize: 14,
      lineNumbers: 'on',
      renderWhitespace: 'selection',
      scrollBeyondLastLine: false,
      folding: true,
      contextmenu: true,
      mouseWheelZoom: true,
      cursorBlinking: 'smooth',
      renderLineHighlight: 'all',
      selectOnLineNumbers: true,
      readOnly: false,
      cursorStyle: 'line'
    })



    // 添加快捷键
    monacoEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      applyCode()
    })

  } catch (error) {
    ElMessage.error('Monaco Editor 初始化失败')
  }
}



// 方法
function handleClose() {
  visible.value = false
}

// 格式化代码
async function formatCode() {
  if (!monacoEditor) return

  formatting.value = true
  try {
    await monacoEditor.getAction('editor.action.formatDocument').run()
  } catch (error) {
    ElMessage.error('代码格式化失败')
  } finally {
    formatting.value = false
  }
}

// 切换主题
async function toggleTheme() {
  if (!monacoEditor) return

  isDarkTheme.value = !isDarkTheme.value
  const theme = isDarkTheme.value ? 'vs-dark' : 'vs'

  // 通过loader获取monaco实例来设置主题
  const monaco = await loader.init()
  monaco.editor.setTheme(theme)
}



// 重置代码
function resetCode() {
  if (!monacoEditor) return

  monacoEditor.setValue(originalContent.value)
}

// 应用代码
async function applyCode() {
  if (!monacoEditor) return

  applying.value = true
  try {
    const currentValue = monacoEditor.getValue()
    emit('apply', currentValue)
    visible.value = false
  } catch (error) {
    ElMessage.error('应用代码失败')
  } finally {
    applying.value = false
  }
}

// 组件生命周期
onMounted(() => {
  // Monaco Editor 会在 watch 中初始化
})

onBeforeUnmount(() => {
  if (monacoEditor) {
    monacoEditor.dispose()
    monacoEditor = null
  }
})
</script>

<style scoped>
.monaco-editor-dialog {
  --el-dialog-padding-primary: 0;
}

.monaco-editor-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: 92vh;
  display: flex;
  flex-direction: column;
}

.monaco-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e1e;
  color: #d4d4d4;
}

.monaco-editor-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  height: 100%;
  min-height: 650px;
}



.dialog-footer {
  padding: 15px;
  background: #f5f5f5;
  border-top: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  gap: 10px;
}

.footer-right {
  display: flex;
  gap: 10px;
}

/* Monaco Editor 自定义样式 */
.monaco-editor-wrapper :deep(.monaco-editor) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
}

.monaco-editor-wrapper :deep(.monaco-editor .margin) {
  background-color: #1e1e1e !important;
}

.monaco-editor-wrapper :deep(.monaco-editor .monaco-editor-background) {
  background-color: #1e1e1e !important;
}

/* 工具栏按钮样式优化 */
.toolbar-left :deep(.el-button) {
  border-color: #3e3e42;
  background-color: #2d2d30;
  color: #cccccc;
}

.toolbar-left :deep(.el-button:hover) {
  border-color: #007acc;
  background-color: #094771;
  color: #ffffff;
}

.toolbar-left :deep(.el-button.is-loading) {
  border-color: #007acc;
  background-color: #094771;
}
</style>
