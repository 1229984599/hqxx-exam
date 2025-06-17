<template>
  <el-dialog
    v-model="visible"
    title="📋 插入模板"
    width="900px"
    :append-to-body="true"
    class="template-dialog"
    @close="handleClose"
  >
    <div class="template-container" v-loading="loading">
      <!-- 搜索和筛选 -->
      <div class="template-filters">
        <div class="filter-row">
          <el-input
            v-model="searchText"
            placeholder="搜索模板名称或描述..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            clearable
            class="category-select"
          >
            <el-option label="全部分类" value="" />
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </div>
      </div>

      <!-- 田字格文字替换功能 -->
      <div v-if="showTextReplaceInput" class="text-replace-section">
        <div class="replace-header">
          <h4>🔤 智能文字替换</h4>
          <p>输入要练习的文字，将自动替换到田字格模板中</p>
        </div>
        <div class="replace-input-area">
          <el-input
            v-model="replaceText"
            type="textarea"
            :rows="3"
            placeholder="请输入要练习的中文字符，例如：春夏秋冬"
            maxlength="100"
            show-word-limit
            class="replace-textarea"
          />
          <div class="replace-actions">
            <el-button @click="cancelTextReplace">取消</el-button>
            <el-button type="primary" @click="applyTextReplace" :disabled="!replaceText.trim()">
              应用替换
            </el-button>
          </div>
        </div>
      </div>

      <!-- 模板网格 -->
      <div class="template-grid" :class="{ 'hidden': showTextReplaceInput }">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          @click="handleTemplateClick(template)"
        >
          <div class="template-header">
            <div class="template-icon">{{ template.icon || '📄' }}</div>
            <div class="template-info">
              <h4 class="template-name">{{ template.name }}</h4>
              <p class="template-description">{{ template.description || '暂无描述' }}</p>
            </div>
          </div>
          <div class="template-meta">
            <el-tag size="small" type="primary">{{ template.category }}</el-tag>
            <el-tag v-if="template.subject" size="small" type="info">
              {{ template.subject.name }}
            </el-tag>
            <el-tag v-if="template.is_system" size="small" type="warning">系统模板</el-tag>
            <span class="usage-count">使用 {{ template.usage_count || 0 }} 次</span>
            <!-- 田字格模板标识 -->
            <el-tag v-if="isTianzigeTemplate(template)" size="small" type="success">
              🔤 支持文字替换
            </el-tag>
          </div>
          <div class="template-preview" v-html="getTemplatePreview(template.content)"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredTemplates.length === 0 && !loading"
        description="未找到符合条件的模板"
        :image-size="100"
      />
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshTemplates">刷新模板</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../../../utils/api.js'
import { useAuthStore } from '../../../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'insert'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const searchText = ref('')
const selectedCategory = ref('')
const loading = ref(false)
const templates = ref([])
const authStore = useAuthStore()

// 文字替换功能
const showTextReplaceInput = ref(false)
const replaceText = ref('')
const selectedTemplate = ref(null)

// 计算属性
const categories = computed(() => {
  const cats = [...new Set(templates.value.map(t => t.category))]
  return cats.sort()
})

const filteredTemplates = computed(() => {
  let filtered = templates.value

  // 按分类过滤
  if (selectedCategory.value) {
    filtered = filtered.filter(t => t.category === selectedCategory.value)
  }

  // 按搜索文本过滤
  if (searchText.value.trim()) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.name.toLowerCase().includes(search) ||
      (t.description && t.description.toLowerCase().includes(search))
    )
  }

  return filtered
})

// 方法
function getTemplatePreview(content) {
  if (!content) return ''

  // 移除HTML标签，只保留文本内容作为预览
  const text = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

// 判断是否为田字格模板
function isTianzigeTemplate(template) {
  if (!template.content) return false

  // 检查模板内容是否包含田字格相关的类名或结构
  const content = template.content.toLowerCase()
  return content.includes('tianzige') ||
         content.includes('田字格') ||
         template.name.includes('田字格') ||
         template.category === '田字格'
}

// 处理模板点击
function handleTemplateClick(template) {
  if (isTianzigeTemplate(template)) {
    // 如果是田字格模板，显示文字替换输入框
    selectedTemplate.value = template
    showTextReplaceInput.value = true
  } else {
    // 普通模板直接插入
    insertTemplate(template)
  }
}

// 取消文字替换
function cancelTextReplace() {
  showTextReplaceInput.value = false
  replaceText.value = ''
  selectedTemplate.value = null
}

// 应用文字替换
function applyTextReplace() {
  if (!selectedTemplate.value || !replaceText.value.trim()) return

  const processedTemplate = replaceTemplateText(selectedTemplate.value, replaceText.value.trim())
  insertTemplate(processedTemplate)

  // 重置状态
  cancelTextReplace()
}

// 替换模板中的文字
function replaceTemplateText(template, newText) {
  if (!template.content) return template

  // 提取中文字符
  const chineseChars = newText.match(/[\u4e00-\u9fff]/g) || []

  if (chineseChars.length === 0) {
    ElMessage.warning('请输入中文字符')
    return template
  }

  let content = template.content
  let charIndex = 0

  // 只替换标签内部的中文字符，不替换属性和注释中的
  content = content.replace(/>([^<]*)</g, (match, textContent) => {
    // 只处理标签内的文本内容
    const replacedText = textContent.replace(/[\u4e00-\u9fff]/g, (chineseChar) => {
      if (charIndex < chineseChars.length) {
        return chineseChars[charIndex++]
      }
      return chineseChar // 如果新文字不够，保持原字符
    })
    return `>${replacedText}<`
  })

  // 如果新文字比模板中的字符多，在末尾添加额外的田字格
  if (charIndex < chineseChars.length) {
    const remainingChars = chineseChars.slice(charIndex)
    const additionalGrids = generateAdditionalTianzigeGrids(remainingChars)
    content += additionalGrids
  }

  return {
    ...template,
    content: content,
    name: `${template.name} - ${newText.substring(0, 10)}${newText.length > 10 ? '...' : ''}`
  }
}

// 生成额外的田字格网格
function generateAdditionalTianzigeGrids(chars) {
  // 这里需要根据实际的田字格HTML结构来生成
  // 假设田字格的基本结构
  let grids = ''

  chars.forEach(char => {
    grids += `
      <div class="tianzige-char" style="display: inline-block; width: 60px; height: 60px; border: 1px solid #333; position: relative; margin: 2px; text-align: center; line-height: 60px; font-size: 24px;">
        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #ccc;"></div>
        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #ccc;"></div>
        <span style="position: relative; z-index: 1;">${char}</span>
      </div>
    `
  })

  return grids
}

async function insertTemplate(template) {
  try {
    // 检查是否已登录
    if (authStore.isAuthenticated) {
      // 增加使用次数
      await api.put(`/templates/${template.id}`, {
        usage_count: (template.usage_count || 0) + 1
      })

      // 更新本地数据
      template.usage_count = (template.usage_count || 0) + 1
    }

    emit('insert', template)
  } catch (error) {
    console.error('更新模板使用次数失败:', error)
    // 即使更新失败也继续插入模板
    emit('insert', template)
  }
}

function handleClose() {
  visible.value = false
}

async function refreshTemplates() {
  // 检查是否已登录
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }

  loading.value = true
  try {
    const response = await api.get('/templates/', {
      params: {
        is_active: true,
        limit: 100
      }
    })
    templates.value = response.data || []
    ElMessage.success('模板列表已刷新')
  } catch (error) {
    console.error('获取模板失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法访问模板')
    } else {
      ElMessage.error('获取模板失败')
    }
  } finally {
    loading.value = false
  }
}

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal && templates.value.length === 0 && authStore.isAuthenticated) {
    refreshTemplates()
  }
})

// 不在组件挂载时自动加载，只在对话框打开时加载
</script>

<style scoped>
.template-container {
  max-height: 70vh;
  overflow-y: auto;
}

.template-filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  min-width: 300px;
  max-width: 500px;
}

.category-select {
  min-width: 180px;
}

/* 文字替换功能样式 */
.text-replace-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 2px solid #409eff;
}

.replace-header {
  margin-bottom: 15px;
}

.replace-header h4 {
  margin: 0 0 5px 0;
  color: #409eff;
  font-size: 16px;
  font-weight: 600;
}

.replace-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.replace-input-area {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.replace-textarea {
  font-size: 16px;
}

.replace-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px 0;
  transition: opacity 0.3s ease;
}

.template-grid.hidden {
  opacity: 0.3;
  pointer-events: none;
}

.template-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.template-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.template-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
}

.template-description {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.usage-count {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}

.template-preview {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 10px;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
  max-height: 60px;
  overflow: hidden;
  position: relative;
}

.template-preview::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, #f8f9fa);
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-input,
  .category-select {
    width: 100%;
    max-width: none;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .template-card {
    padding: 12px;
  }
  
  .template-header {
    gap: 10px;
  }
  
  .template-icon {
    font-size: 20px;
  }
  
  .template-name {
    font-size: 15px;
  }
  
  .template-description {
    font-size: 13px;
  }
}
</style>
