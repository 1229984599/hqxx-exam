<template>
  <PageLayout title="模板管理">
    <div class="template-list-container">
      <!-- 搜索和筛选 -->
      <div class="search-filters">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchForm.search"
              placeholder="搜索模板名称"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch" :icon="Search">搜索</el-button>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.category" placeholder="选择分类" clearable @change="handleSearch">
              <el-option
                v-for="cat in categories"
                :key="cat.value"
                :label="cat.label"
                :value="cat.value"
              />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.subject_id" placeholder="选择学科" clearable @change="handleSearch">
              <el-option
                v-for="subject in subjects"
                :key="subject.id"
                :label="subject.name"
                :value="subject.id"
              />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.is_active" placeholder="状态" clearable @change="handleSearch">
              <el-option label="激活" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <div class="action-buttons">
              <el-button
                v-permission="'templates:create'"
                type="primary"
                @click="handleAdd"
                :icon="Plus"
              >
                添加模板
              </el-button>
              <el-button @click="handleRefresh" :icon="Refresh">刷新</el-button>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 模板列表 -->
      <div class="template-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          :class="{ 'inactive': !template.is_active }"
          @click="handleCardClick(template)"
        >
          <div class="template-header">
            <div class="template-icon">{{ template.icon || '📄' }}</div>
            <div class="template-info">
              <h3 class="template-name">{{ template.name }}</h3>
              <p class="template-description">{{ template.description || '暂无描述' }}</p>
            </div>
            <div class="template-actions" @click.stop>
              <el-dropdown @command="handleAction" trigger="click">
                <div class="action-trigger">
                  <el-icon class="action-icon"><MoreFilled /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu class="template-dropdown-menu">
                    <el-dropdown-item :command="{action: 'preview', template}" class="dropdown-item">
                      <el-icon class="item-icon"><View /></el-icon>
                      <span class="item-text">预览</span>
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-permission="'templates:edit'"
                      :command="{action: 'edit', template}"
                      class="dropdown-item"
                    >
                      <el-icon class="item-icon"><Edit /></el-icon>
                      <span class="item-text">编辑</span>
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-permission="'templates:create'"
                      :command="{action: 'copy', template}"
                      class="dropdown-item"
                    >
                      <el-icon class="item-icon"><DocumentCopy /></el-icon>
                      <span class="item-text">复制</span>
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-permission="'templates:delete'"
                      :command="{action: 'delete', template}"
                      :disabled="template.is_system"
                      divided
                      class="dropdown-item danger"
                    >
                      <el-icon class="item-icon"><Delete /></el-icon>
                      <span class="item-text">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <div class="template-meta">
            <el-tag size="small" :type="getCategoryType(template.category)">
              {{ template.category }}
            </el-tag>
            <el-tag v-if="template.subject" size="small" type="info">
              {{ template.subject.name }}
            </el-tag>
            <el-tag v-if="template.is_system" size="small" type="warning">
              系统模板
            </el-tag>
            <span class="usage-count">使用 {{ template.usage_count }} 次</span>
          </div>

          <div class="template-content-preview" v-html="getPreviewContent(template.content)"></div>

          <!-- 点击提示 -->
          <div class="click-hint">
            <el-icon class="hint-icon" v-if="hasEditPermission">
              <Edit />
            </el-icon>
            <el-icon class="hint-icon" v-else>
              <View />
            </el-icon>
            <span class="hint-text">{{ hasEditPermission ? '点击编辑' : '点击预览' }}</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="templates.length === 0" description="暂无模板数据" />
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreview"
      title="模板预览"
      width="80%"
      :append-to-body="true"
      class="preview-dialog"
    >
      <div class="preview-container">
        <div class="preview-header">
          <h3>{{ previewTemplate?.name }}</h3>
          <p>{{ previewTemplate?.description }}</p>
        </div>
        <div class="preview-content" v-html="previewTemplate?.content"></div>
      </div>
      <template #footer>
        <el-button @click="showPreview = false">关闭</el-button>
        <el-button type="primary" @click="copyTemplateContent">复制内容</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Refresh, MoreFilled, View, Edit,
  DocumentCopy, Delete
} from '@element-plus/icons-vue'
import api from '../utils/api'
import { usePermissions } from '../composables/usePermissions'
import PageLayout from '../components/PageLayout.vue'

const { hasRole, hasAnyRole, isAdmin, isSubjectAdmin, hasPermission } = usePermissions()

// 计算属性：检查编辑权限
const hasEditPermission = computed(() => hasPermission('templates:edit'))

const router = useRouter()

const templates = ref([])
const subjects = ref([])
const categories = ref([])
const loading = ref(false)

const searchForm = reactive({
  search: '',
  category: '',
  subject_id: null,
  is_active: null
})

const showPreview = ref(false)
const previewTemplate = ref(null)

onMounted(() => {
  loadTemplates()
  loadSubjects()
  loadCategories()
})

async function loadTemplates() {
  try {
    loading.value = true
    const params = {}
    
    if (searchForm.search) params.search = searchForm.search
    if (searchForm.category) params.category = searchForm.category
    if (searchForm.subject_id) params.subject_id = searchForm.subject_id
    if (searchForm.is_active !== null) params.is_active = searchForm.is_active

    const response = await api.get('/templates/', { params })
    templates.value = response.data
  } catch (error) {
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

async function loadSubjects() {
  try {
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    console.error('加载学科失败:', error)
  }
}

async function loadCategories() {
  try {
    const response = await api.get('/templates/categories')
    categories.value = response.data
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

function handleSearch() {
  loadTemplates()
}

function handleRefresh() {
  Object.assign(searchForm, {
    search: '',
    category: '',
    subject_id: null,
    is_active: null
  })
  loadTemplates()
}

function handleAdd() {
  router.push('/templates/add')
}

function handleCardClick(template) {
  // 检查编辑权限
  if (hasEditPermission.value) {
    // 点击卡片直接进入编辑页面
    router.push(`/templates/edit/${template.id}`)
  } else {
    // 没有编辑权限，提示用户并进入预览页面
    ElMessage.info('您没有编辑权限，为您打开预览模式')
    previewTemplate.value = template
    showPreview.value = true
  }
}

function handleAction({ action, template }) {
  const { hasPermission } = usePermissions()

  switch (action) {
    case 'preview':
      previewTemplate.value = template
      showPreview.value = true
      break
    case 'edit':
      if (hasPermission('templates:edit')) {
        router.push(`/templates/edit/${template.id}`)
      } else {
        ElMessage.warning('您没有编辑模板的权限')
      }
      break
    case 'copy':
      if (hasPermission('templates:create')) {
        copyTemplate(template)
      } else {
        ElMessage.warning('您没有创建模板的权限')
      }
      break
    case 'delete':
      if (hasPermission('templates:delete')) {
        deleteTemplate(template)
      } else {
        ElMessage.warning('您没有删除模板的权限')
      }
      break
  }
}

async function copyTemplate(template) {
  try {
    const newTemplate = {
      ...template,
      name: `${template.name} - 副本`,
      is_system: false
    }
    delete newTemplate.id
    delete newTemplate.created_at
    delete newTemplate.updated_at
    delete newTemplate.usage_count
    delete newTemplate.subject

    await api.post('/templates/', newTemplate)
    ElMessage.success('模板复制成功')
    loadTemplates()
  } catch (error) {
    ElMessage.error('复制模板失败')
  }
}

async function deleteTemplate(template) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.delete(`/templates/${template.id}`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function copyTemplateContent() {
  if (!previewTemplate.value) return
  
  try {
    navigator.clipboard.writeText(previewTemplate.value.content).then(() => {
      ElMessage.success('内容已复制到剪贴板')
    }).catch(() => {
      // 降级方案
      const textArea = document.createElement('textarea')
      textArea.value = previewTemplate.value.content
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

function getCategoryType(category) {
  const types = {
    '语文': 'danger',
    '数学': 'success',
    '英语': 'primary',
    '通用': 'info'
  }
  return types[category] || 'info'
}

function getPreviewContent(content) {
  // 截取前100个字符作为预览
  const text = content.replace(/<[^>]*>/g, '').trim()
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}
</script>

<style scoped>
.template-list-container {
  padding: 0 24px;
}

.search-filters {
  margin-bottom: 24px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.template-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  cursor: pointer;
  position: relative;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.template-card:hover .action-trigger {
  opacity: 1;
  transform: scale(1);
}

.template-card.inactive {
  opacity: 0.6;
  background: #f5f5f5;
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.template-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f9ff;
  border-radius: 8px;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
}

.template-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.template-description {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

.template-actions {
  flex-shrink: 0;
  position: relative;
}

.action-trigger {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.7;
  transform: scale(0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-trigger:hover {
  background: #409eff;
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transform: scale(1.1);
}

.action-trigger:hover .action-icon {
  color: white;
}

.action-icon {
  font-size: 16px;
  color: #606266;
  transition: color 0.3s ease;
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
  color: #909399;
  margin-left: auto;
}

.template-content-preview {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  max-height: 60px;
  overflow: hidden;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.click-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  white-space: nowrap;
  backdrop-filter: blur(8px);
}

.template-card:hover .click-hint {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.hint-icon {
  font-size: 12px;
}

.hint-text {
  font-size: 12px;
}

/* 预览对话框样式 */
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
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.preview-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.preview-content {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-height: 200px;
  line-height: 1.6;
}

/* 下拉菜单样式 */
:deep(.template-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
  padding: 8px 0;
  min-width: 120px;
}

:deep(.dropdown-item) {
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  border-radius: 4px;
  margin: 0 4px;
}

:deep(.dropdown-item:hover) {
  background: #f5f7fa;
  color: #409eff;
}

:deep(.dropdown-item.danger:hover) {
  background: #fef0f0;
  color: #f56c6c;
}

:deep(.dropdown-item .item-icon) {
  font-size: 14px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.dropdown-item .item-text) {
  font-size: 14px;
  font-weight: 500;
}
</style>
