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

      <!-- 模板网格 -->
      <div class="template-grid">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          @click="insertTemplate(template)"
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

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px 0;
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
