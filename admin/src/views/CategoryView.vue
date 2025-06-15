<template>
  <PageLayout
    title="题目分类管理"
    subtitle="管理考试系统中的题目分类，支持多级分类结构"
  >
    <CrudTable
      ref="crudTable"
      :data="crud.filteredData.value"
      :loading="crud.loading.value"
      :form="crud.form"
      :rules="rules"
      add-title="添加分类"
      edit-title="编辑分类"
      delete-confirm-field="name"
      dialog-width="600px"
      show-add-button
      add-button-text="添加分类"
      :can-create="canManageBasicData"
      :can-edit="canManageBasicData"
      :can-delete="canManageBasicData"
      :enable-batch="true"
      :enable-batch-edit="true"
      :enable-batch-copy="true"
      :batch-operations="batchOperations"
      :batch-edit-fields="batchEditFields"
      :batch-copy-fields="batchCopyFields"
      @search="crud.handleSearch"
      @reset-filters="crud.resetFilters"
      @edit="handleEdit"
      @delete="handleDelete"
      @submit="handleSubmit"
      @batch-operation="handleBatchOperation"
      @batch-edit="handleBatchEdit"
      @batch-copy="handleBatchCopy"
    >
      <template #filters="{ filters }">
        <!-- 学科筛选 -->
        <el-form-item>
          <el-select
            v-model="filters.subject_id"
            placeholder="所属学科"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        
        <!-- 搜索框 -->
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索分类名称或代码"
            :prefix-icon="Search"
            clearable
            style="width: 250px"
            @keyup.enter="crud.handleSearch"
          />
        </el-form-item>
        
        <!-- 状态筛选 -->
        <el-form-item>
          <el-select
            v-model="filters.is_active"
            placeholder="状态"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
      </template>

      <template #columns>
        <el-table-column prop="name" label="分类名称" min-width="200">
          <template #default="{ row }">
            <div class="category-name">
              <el-icon v-if="row.level > 1" class="level-icon">
                <Right/>
              </el-icon>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="分类代码" width="160">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subject_id" label="所属学科" width="120">
          <template #default="{ row }">
            <el-tag v-if="getSubjectName(row.subject_id)" type="primary" size="small">
              {{ getSubjectName(row.subject_id) }}
            </el-tag>
            <span v-else class="text-secondary">未知学科</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="分类级别" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              第{{ row.level }}级
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.sort_order }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
      </template>

      <template #form-items="{ form }">
        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入分类名称"
            @input="onNameChange"
          />
        </el-form-item>

        <el-form-item label="分类代码" prop="code">
          <div class="code-input-group">
            <el-input
              v-model="form.code"
              placeholder="请输入分类代码"
              :disabled="autoGenerateCode"
            />
            <el-button
              v-if="!autoGenerateCode"
              @click="generateCodeFromName"
              :icon="Refresh"
              size="small"
              title="根据分类名称生成代码"
            >
              生成
            </el-button>
            <el-switch
              v-model="autoGenerateCode"
              size="small"
              active-text="自动"
              inactive-text="手动"
              style="margin-left: 8px;"
            />
          </div>
          <div v-if="autoGenerateCode" class="form-tip">
            <el-text size="small" type="info">
              <el-icon><InfoFilled /></el-icon>
              代码将根据分类名称自动生成
            </el-text>
          </div>
        </el-form-item>

        <el-form-item label="所属学科" prop="subject_id">
          <el-select v-model="form.subject_id" placeholder="请选择学科" style="width: 100%">
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="父分类">
          <el-select v-model="form.parent_id" placeholder="请选择父分类（可选）" clearable style="width: 100%">
            <el-option
              v-for="category in parentCategories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" style="width: 100%"/>
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
      </template>
    </CrudTable>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Search, Right, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { useCrud, commonRules, formatDate } from '../composables/useCrud'
import { usePermissions } from '../composables/usePermissions'
import CrudTable from '../components/CrudTable.vue'
import PageLayout from '../components/PageLayout.vue'
import api from '../utils/api'
import { generateCategoryCode, cleanCode } from '../utils/pinyin'

const { hasPermission } = usePermissions()

// 权限检查
const canManageBasicData = computed(() =>
  hasPermission('basic_data:edit')
)

// 批量操作配置
const batchOperations = [
  {
    key: 'activate',
    label: '批量激活',
    type: 'success',
    icon: 'Check',
    confirm: true,
    confirmText: '确定要激活选中的分类吗？'
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'warning',
    icon: 'Close',
    confirm: true,
    confirmText: '确定要禁用选中的分类吗？'
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'Delete',
    confirm: true,
    confirmText: '确定要删除选中的分类吗？此操作不可恢复！'
  }
]

// 批量编辑字段配置
const batchEditFields = {
  is_active: null,
  subject_id: null,
  sort_order: null
}

// 批量复制字段配置
const batchCopyFields = {
  copy_count: 1,
  name_suffix: '_副本'
}

const subjects = ref([])
const autoGenerateCode = ref(true) // 是否自动生成代码

// 扩展筛选器以支持学科筛选
const extendedFilters = reactive({
  search: '',
  is_active: null,
  subject_id: null
})

// 使用CRUD Composable（使用服务端筛选）
const crud = useCrud('/categories/', {
  defaultForm: {
    name: '',
    code: '',
    subject_id: null,
    parent_id: null,
    level: 1,
    is_active: true,
    sort_order: 0,
    description: ''
  },
  messages: {
    createSuccess: '分类创建成功',
    updateSuccess: '分类更新成功',
    deleteSuccess: '分类删除成功',
    loadError: '加载分类列表失败',
    createError: '创建分类失败',
    updateError: '更新分类失败',
    deleteError: '删除分类失败'
  },
  clientFilter: false // 使用服务端筛选
})

// 扩展筛选逻辑 - 添加学科筛选字段
Object.assign(crud.filters, extendedFilters)

// 表单验证规则
const rules = {
  name: commonRules.title,
  code: commonRules.code,
  subject_id: [
    { required: true, message: '请选择所属学科', trigger: 'change' }
  ]
}

// 组件引用
const crudTable = ref()

// 父分类选项
const parentCategories = computed(() => {
  if (!crud.form.subject_id) return []
  return crud.allData.value.filter(cat =>
    cat.subject_id === crud.form.subject_id &&
    cat.id !== crud.editingId &&
    cat.level < 3 // 最多支持3级分类
  )
})

onMounted(() => {
  loadSubjects()
  crud.loadData()
})

async function loadSubjects() {
  try {
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    console.error('加载学科数据失败:', error)
  }
}

// 处理编辑
function handleEdit(row) {
  crud.handleEdit(row)
}

// 处理删除
async function handleDelete(row) {
  await crud.deleteData(row.id)
}

// 批量操作处理
async function handleBatchOperation(operation, selectedItems) {
  if (selectedItems.length === 0) {
    ElMessage.warning('请先选择要操作的分类')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    switch (operation.key) {
      case 'activate':
        await api.post('/categories/batch-update', {
          category_ids: itemIds,
          update_data: { is_active: true }
        })
        ElMessage.success(`成功激活 ${itemIds.length} 个分类`)
        break
      case 'deactivate':
        await api.post('/categories/batch-update', {
          category_ids: itemIds,
          update_data: { is_active: false }
        })
        ElMessage.success(`成功禁用 ${itemIds.length} 个分类`)
        break
      case 'delete':
        await api.post('/categories/batch-delete', { category_ids: itemIds })
        ElMessage.success(`成功删除 ${itemIds.length} 个分类`)
        break
    }

    await crud.loadData()
  } catch (error) {
    console.error('批量操作失败:', error)
    ElMessage.error('批量操作失败')
  }
}

// 批量编辑处理
async function handleBatchEdit(editData, selectedItems) {
  if (selectedItems.length === 0) {
    ElMessage.warning('请先选择要编辑的分类')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    await api.post('/categories/batch-update', {
      category_ids: itemIds,
      update_data: editData
    })

    ElMessage.success(`成功编辑 ${itemIds.length} 个分类`)
    await crud.loadData()
  } catch (error) {
    console.error('批量编辑失败:', error)
    ElMessage.error('批量编辑失败')
  }
}

// 批量复制处理
async function handleBatchCopy(copyData, selectedItems) {
  if (selectedItems.length === 0) {
    ElMessage.warning('请先选择要复制的分类')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    await api.post('/categories/batch-copy', {
      category_ids: itemIds,
      copy_data: copyData
    })

    const totalCopies = itemIds.length * copyData.copy_count
    ElMessage.success(`成功复制 ${totalCopies} 个分类`)
    await crud.loadData()
  } catch (error) {
    console.error('批量复制失败:', error)
    ElMessage.error('批量复制失败')
  }
}

// 处理提交
async function handleSubmit({ isEdit, id, data }) {
  // 计算分类级别
  if (data.parent_id) {
    const parent = crud.allData.value.find(cat => cat.id === data.parent_id)
    data.level = parent ? parent.level + 1 : 1
  } else {
    data.level = 1
  }

  return await crud.handleSubmit({ isEdit, id, data })
}

// 获取学科名称
function getSubjectName(subjectId) {
  if (!subjectId) return ''
  const subject = subjects.value.find(s => s.id === subjectId)
  return subject ? subject.name : ''
}

// 获取学科代码
function getSubjectCode(subjectId) {
  if (!subjectId) return ''
  const subject = subjects.value.find(s => s.id === subjectId)
  return subject ? subject.code : ''
}

// 自动生成分类代码
function generateCodeFromName() {
  if (!crud.form.name) return

  const subjectCode = getSubjectCode(crud.form.subject_id)
  const generatedCode = generateCategoryCode(crud.form.name, subjectCode)
  crud.form.code = generatedCode
}

// 监听分类名称变化，自动生成代码
function onNameChange() {
  if (autoGenerateCode.value && crud.form.name) {
    generateCodeFromName()
  }
}

// 监听学科变化，重新生成代码
watch(() => crud.form.subject_id, () => {
  if (autoGenerateCode.value && crud.form.name) {
    generateCodeFromName()
  }
})

// 获取级别类型
function getLevelType(level) {
  const types = { 1: 'primary', 2: 'success', 3: 'warning' }
  return types[level] || 'info'
}
</script>

<style scoped>
.category-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-icon {
  color: #a0aec0;
  font-size: 12px;
}

.name-text {
  font-weight: 500;
  color: #2d3748;
}

.code-tag {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.date-text {
  color: #718096;
  font-size: 13px;
}

.text-secondary {
  color: #a0aec0;
  font-size: 12px;
}

.code-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.code-input-group .el-input {
  flex: 1;
}

.code-input-group .el-button {
  flex-shrink: 0;
}

.code-input-group .el-switch {
  flex-shrink: 0;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #a8abb2;
}

:deep(.el-input.is-disabled .el-input__inner) {
  color: #a8abb2;
  -webkit-text-fill-color: #a8abb2;
}

.form-tip {
  margin-top: 4px;
}

.form-tip .el-text {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
