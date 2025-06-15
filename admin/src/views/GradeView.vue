<template>
  <PageLayout
    title="年级管理"
    subtitle="管理学校的年级信息，设置年级级别和排序"
  >
    <CrudTable
      ref="crudTable"
      :data="crud.filteredData.value"
      :loading="crud.loading.value"
      :form="crud.form"
      :rules="rules"
      add-title="添加年级"
      edit-title="编辑年级"
      delete-confirm-field="name"
      show-add-button
      add-button-text="添加年级"
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
      @edit="crud.handleEdit"
      @delete="handleDelete"
      @submit="crud.handleSubmit"
      @batch-operation="handleBatchOperation"
      @batch-edit="handleBatchEdit"
      @batch-copy="handleBatchCopy"
    >
      <template #filters="{ filters, resetFilters }">
        <!-- 搜索框 -->
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索年级名称或代码"
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

        <!-- 级别筛选 -->
        <el-form-item>
          <el-select
            v-model="filters.level"
            placeholder="年级级别"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="level in 12"
              :key="level"
              :label="`第${level}级`"
              :value="level"
            />
          </el-select>
        </el-form-item>
      </template>

      <template #columns>
        <el-table-column prop="name" label="年级名称" min-width="200">
          <template #default="{ row }">
            <div class="grade-name">
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="年级代码" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="年级级别" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getLevelType(row.level)">
              第{{ row.level }}级
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="primary">{{ row.sort_order }}</el-tag>
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
        <el-form-item label="年级名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入年级名称"/>
        </el-form-item>

        <el-form-item label="年级代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入年级代码"/>
        </el-form-item>

        <el-form-item label="年级级别" prop="level">
          <el-input-number v-model="form.level" :min="1" :max="12" placeholder="请输入年级级别"/>
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="1" placeholder="请输入排序"/>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active"/>
        </el-form-item>
      </template>
    </CrudTable>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useCrud, commonRules, formatDate } from '../composables/useCrud'
import { usePermissions } from '../composables/usePermissions'
import CrudTable from '../components/CrudTable.vue'
import PageLayout from '../components/PageLayout.vue'
import api from '../utils/api'

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
    confirmText: '确定要激活选中的年级吗？'
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'warning',
    icon: 'Close',
    confirm: true,
    confirmText: '确定要禁用选中的年级吗？'
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'Delete',
    confirm: true,
    confirmText: '确定要删除选中的年级吗？此操作不可恢复！'
  }
]

// 批量编辑字段配置
const batchEditFields = {
  is_active: null,
  level: null,
  sort_order: null
}

// 批量复制字段配置
const batchCopyFields = {
  copy_count: 1,
  name_suffix: '_副本'
}

// 扩展筛选器以支持级别筛选
const extendedFilters = reactive({
  search: '',
  is_active: null,
  level: null
})

// 使用CRUD Composable（使用服务端筛选）
const crud = useCrud('/grades/', {
  defaultForm: {
    name: '',
    code: '',
    level: 1,
    sort_order: 1,
    is_active: true
  },
  messages: {
    createSuccess: '年级创建成功',
    updateSuccess: '年级更新成功',
    deleteSuccess: '年级删除成功',
    loadError: '加载年级列表失败',
    createError: '创建年级失败',
    updateError: '更新年级失败',
    deleteError: '删除年级失败'
  },
  clientFilter: false // 使用服务端筛选
})

// 扩展筛选逻辑 - 添加级别筛选字段
Object.assign(crud.filters, extendedFilters)

// 表单验证规则
const rules = {
  name: commonRules.name,
  code: commonRules.code,
  level: [
    { required: true, message: '请输入年级级别', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序', trigger: 'blur' }
  ]
}

// 组件引用
const crudTable = ref()

// 处理删除
async function handleDelete(row) {
  await crud.deleteData(row.id)
}

// 批量操作处理
async function handleBatchOperation(operation, selectedItems) {
  if (selectedItems.length === 0) {
    ElMessage.warning('请先选择要操作的年级')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    switch (operation.key) {
      case 'activate':
        await api.post('/grades/batch-update', {
          grade_ids: itemIds,
          update_data: { is_active: true }
        })
        ElMessage.success(`成功激活 ${itemIds.length} 个年级`)
        break
      case 'deactivate':
        await api.post('/grades/batch-update', {
          grade_ids: itemIds,
          update_data: { is_active: false }
        })
        ElMessage.success(`成功禁用 ${itemIds.length} 个年级`)
        break
      case 'delete':
        await api.post('/grades/batch-delete', { grade_ids: itemIds })
        ElMessage.success(`成功删除 ${itemIds.length} 个年级`)
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
    ElMessage.warning('请先选择要编辑的年级')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    await api.post('/grades/batch-update', {
      grade_ids: itemIds,
      update_data: editData
    })

    ElMessage.success(`成功编辑 ${itemIds.length} 个年级`)
    await crud.loadData()
  } catch (error) {
    console.error('批量编辑失败:', error)
    ElMessage.error('批量编辑失败')
  }
}

// 批量复制处理
async function handleBatchCopy(copyData, selectedItems) {
  if (selectedItems.length === 0) {
    ElMessage.warning('请先选择要复制的年级')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    await api.post('/grades/batch-copy', {
      grade_ids: itemIds,
      copy_data: copyData
    })

    const totalCopies = itemIds.length * copyData.copy_count
    ElMessage.success(`成功复制 ${totalCopies} 个年级`)
    await crud.loadData()
  } catch (error) {
    console.error('批量复制失败:', error)
    ElMessage.error('批量复制失败')
  }
}

// 获取级别类型
function getLevelType(level) {
  if (level <= 3) return 'success'
  if (level <= 6) return 'info'
  if (level <= 9) return 'warning'
  return 'danger'
}

// 初始化加载数据
crud.loadData()
</script>

<style scoped>
.grade-name {
  display: flex;
  align-items: center;
  gap: 12px;
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
</style>
