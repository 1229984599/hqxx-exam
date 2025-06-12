<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :before-close="handleClose"
    class="preview-dialog"
  >
    <div class="preview-container">
      <!-- 预览头部信息 -->
      <div class="preview-header" v-if="showHeader">
        <h3>{{ headerTitle }}</h3>
        <div class="preview-meta" v-if="meta && meta.length">
          <el-tag
            v-for="tag in meta"
            :key="tag.label"
            :type="tag.type || 'info'"
            size="small"
          >
            {{ tag.label }}: {{ tag.value }}
          </el-tag>
        </div>
      </div>

      <!-- 内容预览 -->
      <div class="preview-content">
        <h4>{{ contentLabel }}</h4>
        <div 
          class="content-preview" 
          v-html="processedContent"
        ></div>
      </div>

      <!-- 额外信息 -->
      <div class="preview-info" v-if="extraInfo">
        <slot name="extra-info" :info="extraInfo">
          <div v-for="(info, key) in extraInfo" :key="key" class="info-item">
            <h4>{{ info.label }}</h4>
            <div class="info-content" v-html="info.content"></div>
          </div>
        </slot>
      </div>
    </div>

    <template #footer>
      <div class="preview-footer">
        <el-button @click="copyContent" :icon="DocumentCopy">
          复制内容
        </el-button>
        <el-button @click="handleClose">
          关闭
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '内容预览'
  },
  width: {
    type: String,
    default: '800px'
  },
  content: {
    type: String,
    default: ''
  },
  contentLabel: {
    type: String,
    default: '内容'
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  headerTitle: {
    type: String,
    default: ''
  },
  meta: {
    type: Array,
    default: () => []
  },
  extraInfo: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const visible = ref(false)

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 处理内容，确保拼音注音正确显示
const processedContent = computed(() => {
  if (!props.content) return ''

  let content = props.content

  // 确保所有 ruby 标签都有正确的 class
  content = content.replace(/<ruby(?![^>]*class=)/g, '<ruby class="pinyin-ruby"')

  // 确保 rt 和 rb 标签的顺序正确（rt 在前，rb 在后）
  content = content.replace(
    /<ruby([^>]*)><rb([^>]*)>(.*?)<\/rb><rt([^>]*)>(.*?)<\/rt><\/ruby>/g,
    '<ruby$1><rt$4>$5</rt><rb$2>$3</rb></ruby>'
  )

  // 处理可能存在的其他格式问题
  content = content.replace(
    /<ruby([^>]*)class="pinyin-ruby"([^>]*)><rb([^>]*)>(.*?)<\/rb><rt([^>]*)>(.*?)<\/rt><\/ruby>/g,
    '<ruby$1class="pinyin-ruby"$2><rt$5>$6</rt><rb$3>$4</rb></ruby>'
  )

  return content
})

function handleClose() {
  visible.value = false
  emit('close')
}

function copyContent() {
  try {
    // 创建一个临时的 div 来获取纯文本内容
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = props.content
    const textContent = tempDiv.textContent || tempDiv.innerText || ''

    // 复制到剪贴板
    navigator.clipboard.writeText(props.content).then(() => {
      ElMessage.success('内容已复制到剪贴板')
    }).catch(() => {
      // 降级方案
      const textArea = document.createElement('textarea')
      textArea.value = props.content
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      ElMessage.success('内容已复制到剪贴板')
    })
  } catch (error) {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.preview-container {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.preview-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.preview-content {
  margin-bottom: 20px;
}

.preview-content h4,
.info-item h4 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-size: 14px;
  font-weight: 600;
}

.content-preview,
.info-content {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  min-height: 100px;
  line-height: 1.8;
}

.info-item {
  margin-bottom: 15px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.preview-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 预览内容中的 Ruby 标签样式 */
:deep(.content-preview ruby),
:deep(.info-content ruby) {
  ruby-align: center !important;
  display: inline-block !important;
  white-space: nowrap !important;
  margin: 0 2px !important;
  vertical-align: baseline !important;
  line-height: 2.2 !important;
  position: relative !important;
}

:deep(.content-preview ruby.pinyin-ruby),
:deep(.info-content ruby.pinyin-ruby) {
  background: rgba(64, 158, 255, 0.05) !important;
  border-radius: 4px !important;
  padding: 3px 2px 1px 2px !important;
  cursor: pointer !important;
  position: relative !important;
  transition: background-color 0.2s ease !important;
}

:deep(.content-preview ruby.pinyin-ruby:hover),
:deep(.info-content ruby.pinyin-ruby:hover) {
  background: rgba(64, 158, 255, 0.1) !important;
}

:deep(.content-preview rt),
:deep(.info-content rt) {
  font-size: 0.75em !important;
  color: #409eff !important;
  font-weight: 500 !important;
  display: block !important;
  text-align: center !important;
  line-height: 1.2 !important;
  margin-bottom: 3px !important;
  user-select: none !important;
  min-width: 1em !important;
  padding: 0 1px !important;
  position: relative !important;
  z-index: 1 !important;
}

:deep(.content-preview rb),
:deep(.info-content rb) {
  display: block !important;
  text-align: center !important;
  user-select: text !important;
  font-size: 1em !important;
  line-height: 1.4 !important;
  position: relative !important;
  z-index: 1 !important;
}

/* 确保非拼音的 ruby 标签不受影响 */
:deep(.content-preview ruby:not(.pinyin-ruby)),
:deep(.info-content ruby:not(.pinyin-ruby)) {
  background: transparent !important;
  padding: 0 !important;
}

/* 滚动条样式 */
:deep(.preview-container::-webkit-scrollbar) {
  width: 8px;
}

:deep(.preview-container::-webkit-scrollbar-track) {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 4px;
}

:deep(.preview-container::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
}

:deep(.preview-container::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
}
</style>
