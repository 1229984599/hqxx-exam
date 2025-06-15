<template>
  <PageLayout
    title="学科管理"
    subtitle="管理学校的学科信息，设置学科颜色和排序"
  >
    <CrudTable
      ref="crudTable"
      :data="crud.filteredData.value"
      :loading="crud.loading.value"
      :form="crud.form"
      :rules="rules"
      add-title="添加学科"
      edit-title="编辑学科"
      delete-confirm-field="name"
      show-add-button
      add-button-text="添加学科"
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
      <template #columns>
        <el-table-column prop="name" label="学科名称" min-width="200">
          <template #default="{ row }">
            <div class="subject-name">
              <div class="color-indicator" :style="{ backgroundColor: row.color }"></div>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="学科代码" width="130">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="color" label="主题色" width="120" align="center">
          <template #default="{ row }">
            <div class="color-display">
              <div class="color-block" :style="{ backgroundColor: row.color }"></div>
              <span class="color-text">{{ row.color }}</span>
            </div>
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
        <el-form-item label="学科名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入学科名称" />
        </el-form-item>

        <el-form-item label="学科代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入学科代码" />
        </el-form-item>

        <el-form-item label="主题色" prop="color">
          <el-color-picker v-model="form.color" />
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="1" placeholder="请输入排序" />
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </template>
    </CrudTable>
  </PageLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
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
    confirmText: '确定要激活选中的学科吗？'
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'warning',
    icon: 'Close',
    confirm: true,
    confirmText: '确定要禁用选中的学科吗？'
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'Delete',
    confirm: true,
    confirmText: '确定要删除选中的学科吗？此操作不可恢复！'
  }
]

// 批量编辑字段配置
const batchEditFields = {
  is_active: null,
  color: '',
  sort_order: null
}

// 批量复制字段配置
const batchCopyFields = {
  copy_count: 1,
  name_suffix: '_副本'
}

// 使用CRUD Composable
const crud = useCrud('/subjects/', {
  defaultForm: {
    name: '',
    code: '',
    color: '#667eea',
    sort_order: 1,
    is_active: true
  },
  messages: {
    createSuccess: '学科创建成功',
    updateSuccess: '学科更新成功',
    deleteSuccess: '学科删除成功',
    loadError: '加载学科列表失败',
    createError: '创建学科失败',
    updateError: '更新学科失败',
    deleteError: '删除学科失败'
  }
})

// 表单验证规则
const rules = {
  name: commonRules.name,
  code: commonRules.code,
  color: [
    { required: true, message: '请选择主题色', trigger: 'blur' }
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
    ElMessage.warning('请先选择要操作的学科')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    switch (operation.key) {
      case 'activate':
        await api.post('/subjects/batch-update', {
          subject_ids: itemIds,
          update_data: { is_active: true }
        })
        ElMessage.success(`成功激活 ${itemIds.length} 个学科`)
        break
      case 'deactivate':
        await api.post('/subjects/batch-update', {
          subject_ids: itemIds,
          update_data: { is_active: false }
        })
        ElMessage.success(`成功禁用 ${itemIds.length} 个学科`)
        break
      case 'delete':
        await api.post('/subjects/batch-delete', { subject_ids: itemIds })
        ElMessage.success(`成功删除 ${itemIds.length} 个学科`)
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
    ElMessage.warning('请先选择要编辑的学科')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    await api.post('/subjects/batch-update', {
      subject_ids: itemIds,
      update_data: editData
    })

    ElMessage.success(`成功编辑 ${itemIds.length} 个学科`)
    await crud.loadData()
  } catch (error) {
    console.error('批量编辑失败:', error)
    ElMessage.error('批量编辑失败')
  }
}

// 批量复制处理
async function handleBatchCopy(copyData, selectedItems) {
  if (selectedItems.length === 0) {
    ElMessage.warning('请先选择要复制的学科')
    return
  }

  try {
    const itemIds = selectedItems.map(item => item.id)

    await api.post('/subjects/batch-copy', {
      subject_ids: itemIds,
      copy_data: copyData
    })

    const totalCopies = itemIds.length * copyData.copy_count
    ElMessage.success(`成功复制 ${totalCopies} 个学科`)
    await crud.loadData()
  } catch (error) {
    console.error('批量复制失败:', error)
    ElMessage.error('批量复制失败')
  }
}

// 初始化加载数据
crud.loadData()
</script>

<style scoped>
.subject-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.name-text {
  font-weight: 500;
  color: #2d3748;
}

.code-tag {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-block {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.color-text {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #666;
}

.date-text {
  color: #718096;
  font-size: 13px;
}
</style>
