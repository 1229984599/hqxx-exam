<template>
  <PageLayout
      title="题目分类管理"
      subtitle="管理考试系统中的题目分类，支持多级分类结构"
  >
    <template #actions>
      <el-button
          type="primary"
          :icon="Plus"
          @click="showAddDialog = true"
          size="large"
      >
        添加分类
      </el-button>
    </template>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item>
          <el-button
              type="primary"
              @click="showAddDialog = true"
              :icon="Plus"
              size="default"
          >
            添加分类
          </el-button>
        </el-form-item>

        <el-form-item label="所属学科">
          <el-select v-model="filters.subject_id" placeholder="请选择学科" clearable @change="loadCategories"
                     style="width: 150px">
            <el-option
                v-for="subject in subjects"
                :key="subject.id"
                :label="subject.name"
                :value="subject.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="请选择状态" clearable @change="loadCategories"
                     style="width: 120px">
            <el-option label="启用" :value="true"/>
            <el-option label="禁用" :value="false"/>
          </el-select>
        </el-form-item>

        <el-form-item label="搜索">
          <el-input
              v-model="filters.search"
              placeholder="搜索分类名称或代码"
              clearable
              style="width: 200px"
              @keyup.enter="loadCategories"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadCategories" :icon="Search">
            搜索
          </el-button>
          <el-button @click="resetFilters" :icon="Refresh">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <el-table :data="categories" v-loading="loading" class="modern-table">
      <el-table-column prop="name" label="分类名称" min-width="150">
        <template #default="{ row }">
          <div class="category-name">
            <el-icon v-if="row.level > 1" class="level-icon">
              <Right/>
            </el-icon>
            <span>{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="code" label="分类代码" width="160">
        <template #default="{ row }">
          <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="subject.name" label="所属学科" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.subject" type="info" size="small">
            {{ row.subject.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="level" label="分类级别" width="130">
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.level)" size="small">
            第{{ row.level }}级
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80">
        <template #default="{ row }">
          <el-tag size="small" type="primary">{{ row.sort_order }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
                size="small"
                :icon="Edit"
                @click="editCategory(row)"
            />
            <el-button
                size="small"
                type="danger"
                :icon="Delete"
                @click="deleteCategory(row)"
            />
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
        v-model="showAddDialog"
        :title="editingId ? '编辑分类' : '添加分类'"
        width="600px"
        :before-close="handleDialogClose"
    >
      <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称"/>
        </el-form-item>

        <el-form-item label="分类代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入分类代码"/>
        </el-form-item>

        <el-form-item label="所属学科" prop="subject_id">
          <el-select v-model="form.subject_id" placeholder="请选择学科">
            <el-option
                v-for="subject in subjects"
                :key="subject.id"
                :label="subject.name"
                :value="subject.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="父分类">
          <el-select v-model="form.parent_id" placeholder="请选择父分类（可选）" clearable>
            <el-option
                v-for="category in parentCategories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999"/>
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="form.is_active"/>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入分类描述（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="saveCategory" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import {ref, reactive, computed, onMounted} from 'vue'
import {Plus, Edit, Delete, Search, Refresh, Right} from '@element-plus/icons-vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingId = ref(null)
const formRef = ref()

const categories = ref([])
const subjects = ref([])

const filters = reactive({
  subject_id: null,
  is_active: null,
  search: ''
})

const form = reactive({
  name: '',
  code: '',
  subject_id: null,
  parent_id: null,
  level: 1,
  is_active: true,
  sort_order: 0,
  description: ''
})

const rules = {
  name: [
    {required: true, message: '请输入分类名称', trigger: 'blur'}
  ],
  code: [
    {required: true, message: '请输入分类代码', trigger: 'blur'}
  ],
  subject_id: [
    {required: true, message: '请选择所属学科', trigger: 'change'}
  ]
}

const parentCategories = computed(() => {
  if (!form.subject_id) return []
  return categories.value.filter(cat =>
      cat.subject_id === form.subject_id &&
      cat.id !== editingId.value &&
      cat.level < 3 // 最多支持3级分类
  )
})

onMounted(() => {
  loadBasicData()
  loadCategories()
})

async function loadBasicData() {
  try {
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    ElMessage.error('加载学科数据失败')
  }
}

async function loadCategories() {
  loading.value = true
  try {
    const params = {}
    if (filters.subject_id) params.subject_id = filters.subject_id
    if (filters.is_active !== null) params.is_active = filters.is_active

    const response = await api.get('/categories/', {params})
    let filteredCategories = response.data

    // 前端搜索过滤
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filteredCategories = filteredCategories.filter(category =>
          category.name.toLowerCase().includes(searchLower) ||
          category.code.toLowerCase().includes(searchLower)
      )
    }

    categories.value = filteredCategories
  } catch (error) {
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

function editCategory(category) {
  editingId.value = category.id
  Object.assign(form, {
    name: category.name,
    code: category.code,
    subject_id: category.subject_id,
    parent_id: category.parent_id,
    level: category.level,
    is_active: category.is_active,
    sort_order: category.sort_order,
    description: category.description || ''
  })
  showAddDialog.value = true
}

async function saveCategory() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    // 计算分类级别
    if (form.parent_id) {
      const parent = categories.value.find(cat => cat.id === form.parent_id)
      form.level = parent ? parent.level + 1 : 1
    } else {
      form.level = 1
    }

    if (editingId.value) {
      await api.put(`/categories/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/categories/', form)
      ElMessage.success('添加成功')
    }

    showAddDialog.value = false
    resetForm()
    loadCategories()
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
  }
}

async function deleteCategory(category) {
  try {
    await ElMessageBox.confirm(`确定要删除分类"${category.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/categories/${category.id}`)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function resetFilters() {
  Object.assign(filters, {
    subject_id: null,
    is_active: null,
    search: ''
  })
  loadCategories()
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    name: '',
    code: '',
    subject_id: null,
    parent_id: null,
    level: 1,
    is_active: true,
    sort_order: 0,
    description: ''
  })
  formRef.value?.resetFields()
}

function handleDialogClose() {
  showAddDialog.value = false
  resetForm()
}

function getLevelType(level) {
  const types = {1: 'primary', 2: 'success', 3: 'warning'}
  return types[level] || 'info'
}
</script>

<style scoped>
.filter-section {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.category-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-icon {
  color: #a0aec0;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #4a5568;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  text-align: right;
}

/* 选择器样式优化 */
:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
  background: white;
}

:deep(.el-select .el-input__inner) {
  color: #2d3748;
  font-weight: 500;
}

:deep(.el-select-dropdown) {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

:deep(.el-select-dropdown__item) {
  color: #2d3748;
  font-weight: 500;
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

:deep(.el-select-dropdown__item.selected) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}
</style>
