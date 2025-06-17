<template>
  <div class="tinymce-editor">


    <!-- TinyMCE 编辑器 -->
    <Editor
      :api-key="apiKey"
      v-model="content"
      :init="editorConfig"
      @onSelectionChange="handleSelectionChange"
      @onInput="handleInput"
      @onChange="handleChange"
    />

    <!-- 快捷键提示 -->
    <div v-if="showShortcuts" class="shortcuts-hint">
      <div class="shortcuts-grid">
        <div class="shortcut-item">
          <kbd>Ctrl</kbd> + <kbd>+</kbd> 增大字体
        </div>
        <div class="shortcut-item">
          <kbd>Ctrl</kbd> + <kbd>-</kbd> 减小字体
        </div>
        <div class="shortcut-item">
          <kbd>Shift</kbd> + <kbd>Enter</kbd> 换行
        </div>
        <div class="shortcut-item">
          <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> 粘贴文本
        </div>
      </div>
    </div>

    <!-- 统计对话框 -->
    <StatsDialog
      v-model="showStatsDialog"
      :stats="contentStats"
      @refresh="refreshStats"
    />

    <!-- 预览对话框 -->
    <PreviewDialog
      v-model="showPreviewDialog"
      :content="content"
      @refresh="refreshPreview"
    />

    <!-- 符号对话框 -->
    <SymbolDialog
      v-model="showSymbolDialog"
      @insert="insertSymbol"
    />

    <!-- 模板对话框 -->
    <TemplateDialog
      v-model="showTemplateDialog"
      @insert="insertTemplate"
    />

    <!-- 拼音编辑对话框 -->
    <PinyinEditDialog
      v-model="showPinyinEditDialog"
      :character="pinyinEditData.character"
      :current-pinyin="pinyinEditData.currentPinyin"
      :pinyin-options="pinyinEditData.pinyinOptions"
      @confirm="handlePinyinConfirm"
      @remove="handlePinyinRemove"
    />

    <!-- 浮动工具栏 -->
    <FloatingToolbar
      :visible="showFloatingToolbar"
      :selection="floatingToolbarSelection"
      :formats="currentFormats"
      :format-brush-active="formatBrushActive"
      @toggle-format="floatingToggleFormat"
      @adjust-font-size="floatingAdjustFontSize"
      @apply-text-color="floatingApplyTextColor"
      @apply-bg-color="floatingApplyBgColor"
      @add-pinyin="floatingAddPinyin"
      @toggle-format-brush="floatingToggleFormatBrush"
      @clear-format="floatingClearFormat"
    />

    <!-- 代码编辑器对话框 -->
    <CodeEditorDialog
      v-model="showCodeEditorDialog"
      :content="content"
      @apply="handleCodeApply"
    />


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Editor from '@tinymce/tinymce-vue'

// 导入 TinyMCE 核心和插件
import tinymce from 'tinymce/tinymce'
import 'tinymce/models/dom'
import 'tinymce/themes/silver'
import 'tinymce/icons/default'

// 导入所有必要的插件
import 'tinymce/plugins/advlist'
import 'tinymce/plugins/autolink'
import 'tinymce/plugins/lists'
import 'tinymce/plugins/link'
import 'tinymce/plugins/image'
import 'tinymce/plugins/charmap'
import 'tinymce/plugins/preview'
import 'tinymce/plugins/anchor'
import 'tinymce/plugins/searchreplace'
import 'tinymce/plugins/visualblocks'
import 'tinymce/plugins/code'
import 'tinymce/plugins/fullscreen'
import 'tinymce/plugins/insertdatetime'
import 'tinymce/plugins/media'
import 'tinymce/plugins/table'
import 'tinymce/plugins/help'
import 'tinymce/plugins/wordcount'
import 'tinymce/plugins/emoticons'
import 'tinymce/plugins/autosave'
import 'tinymce/plugins/directionality'
import 'tinymce/plugins/nonbreaking'
import 'tinymce/plugins/pagebreak'
import 'tinymce/plugins/quickbars'

// 导入组件和工具
import { useEditor } from './composables/useEditor.js'
import StatsDialog from './dialogs/StatsDialog.vue'
import PreviewDialog from './dialogs/PreviewDialog.vue'
import SymbolDialog from './dialogs/SymbolDialog.vue'
import TemplateDialog from './dialogs/TemplateDialog.vue'
import PinyinEditDialog from './dialogs/PinyinEditDialog.vue'
import FloatingToolbar from './components/FloatingToolbar.vue'
import CodeEditorDialog from './dialogs/CodeEditorDialog.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  height: {
    type: [String, Number],
    default: 400
  },
  showPinyinTools: {
    type: Boolean,
    default: true
  },
  showWordCount: {
    type: Boolean,
    default: true
  },
  showStatusBar: {
    type: Boolean,
    default: true
  },
  showShortcuts: {
    type: Boolean,
    default: false
  },
  toolbarMode: {
    type: String,
    default: 'sliding'
  },
  apiKey: {
    type: String,
    default: 'gpl'
  },
  autoStyleImages: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

// 使用编辑器 composable
const {
  editorInstance,
  content,
  selectedText,
  contentStats,
  formatBrushActive,
  hasSelection,
  wordCount,
  editorConfig,
  showContentStats,
  showSymbolDialog,
  showTemplateDialog,
  showPreviewDialog,
  showPinyinEditDialog,
  pinyinEditData,
  showFloatingToolbar,
  floatingToolbarSelection,
  currentFormats,
  showCodeEditorDialog,
  openSymbolDialog,
  openTemplateDialog,
  openResponsivePreview,
  handleCodeApply,
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
} = useEditor(props, emit)

// 统计对话框状态
const showStatsDialog = ref(false)

// 刷新统计
function refreshStats() {
  const stats = showContentStats()
  contentStats.value = stats
}

// 刷新预览
function refreshPreview() {
  // 预览内容会自动更新，这里可以添加额外的刷新逻辑
  console.log('预览已刷新')
}

// 插入符号
function insertSymbol(symbol) {
  if (editorInstance.value) {
    editorInstance.value.insertContent(symbol)
  }
  showSymbolDialog.value = false
}

// 插入模板
function insertTemplate(template) {
  if (editorInstance.value) {
    editorInstance.value.insertContent(template.content)
  }
  showTemplateDialog.value = false
}

// 组件挂载时的初始化
onMounted(() => {
  // 可以在这里添加额外的初始化逻辑
  console.log('TinyMCE 编辑器组件已挂载')
  console.log('浮动工具栏状态:', {
    showFloatingToolbar: showFloatingToolbar.value,
    floatingToolbarSelection: floatingToolbarSelection.value,
    currentFormats: currentFormats.value
  })
})
</script>

<style scoped>
.tinymce-editor {
  position: relative;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
  background: white;
}



.shortcuts-hint {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  z-index: 1000;
  max-width: 300px;
  backdrop-filter: blur(10px);
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

kbd {
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 11px;
  font-family: monospace;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .shortcuts-hint {
    position: relative;
    bottom: auto;
    right: auto;
    margin-top: 10px;
    max-width: none;
  }

  .shortcuts-grid {
    grid-template-columns: 1fr;
  }
}

/* TinyMCE 编辑器样式覆盖 */
:deep(.tox-tinymce) {
  border: none !important;
  border-radius: 0 !important;
}

:deep(.tox-toolbar-overlord) {
  background: #fafafa !important;
}

:deep(.tox-toolbar__primary) {
  background: transparent !important;
}

:deep(.tox-editor-header) {
  border-bottom: 1px solid #e9ecef !important;
}

:deep(.tox-statusbar) {
  border-top: 1px solid #e9ecef !important;
  background: #f8f9fa !important;
}

/* 编辑器内容区域样式 */
:deep(.tox-edit-area) {
  background: white !important;
}

/* 工具栏按钮样式优化 */
:deep(.tox-tbtn) {
  border-radius: 4px !important;
  margin: 1px !important;
}

:deep(.tox-tbtn:hover) {
  background: #e9ecef !important;
}

:deep(.tox-tbtn--enabled) {
  background: #409eff !important;
  color: white !important;
}

/* 菜单样式优化 */
:deep(.tox-menu) {
  border-radius: 6px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

:deep(.tox-collection__item) {
  border-radius: 4px !important;
  margin: 2px 4px !important;
}

/* 对话框样式优化 */
:deep(.tox-dialog) {
  border-radius: 8px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

:deep(.tox-dialog__header) {
  background: #f8f9fa !important;
  border-bottom: 1px solid #e9ecef !important;
}

:deep(.tox-dialog__footer) {
  background: #f8f9fa !important;
  border-top: 1px solid #e9ecef !important;
}
</style>
