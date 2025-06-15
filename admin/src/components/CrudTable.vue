<template>
  <div class="crud-table-container">
    <!-- 搜索筛选区域 -->
    <div class="filter-section" v-if="showFilters">
      <el-form :model="filters" inline>
        <!-- 添加按钮（可选） -->
        <el-form-item v-if="showAddButton && canCreate">
          <el-button
            type="primary"
            @click="showDialog = true"
            :icon="Plus"
            size="default"
          >
            {{ addButtonText }}
          </el-button>
        </el-form-item>

        <slot name="filters" :filters="filters" :resetFilters="resetFilters">
          <!-- 默认搜索框 -->
          <el-form-item>
            <el-input
              v-model="filters.search"
              placeholder="搜索..."
              :prefix-icon="Search"
              clearable
              style="width: 250px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>

          <!-- 状态筛选 -->
          <el-form-item v-if="showStatusFilter">
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
        </slot>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">
            搜索
          </el-button>
          <el-button @click="resetFilters" :icon="Refresh">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 批量操作 -->
    <BatchOperationsGeneric
      v-if="enableBatch && selectedItems.length > 0"
      :selected-count="selectedItems.length"
      :operations="batchOperations"
      :enable-edit="enableBatchEdit"
      :enable-copy="enableBatchCopy"
      :edit-fields="batchEditFields"
      :copy-fields="batchCopyFields"
      @operation="handleBatchOperation"
      @clear="clearSelection"
      @batch-edit="handleBatchEdit"
      @batch-copy="handleBatchCopy"
    />

    <!-- 表格容器 -->
    <div class="table-wrapper">
      <!-- 数据表格 -->
      <el-table
        :data="data"
        v-loading="loading"
        class="modern-table"
        v-bind="tableProps"
        @selection-change="handleSelectionChange"
        height="100%"
      >
      <el-table-column v-if="enableBatch" type="selection" width="55" />
      <slot name="columns" />
      
      <!-- 操作列 -->
      <el-table-column 
        v-if="showActions"
        label="操作" 
        align="center" 
        :width="actionWidth" 
        fixed="right"
      >
        <template #default="{ row }">
          <div class="action-buttons">
            <slot name="actions" :row="row" :edit="() => handleEdit(row)" :delete="() => handleDelete(row)">
              <el-button
                v-if="canEdit"
                size="small"
                @click="handleEdit(row)"
                :icon="Edit"
              />
              <el-button
                v-if="canDelete"
                size="small"
                type="danger"
                @click="handleDelete(row)"
                :icon="Delete"
              />
            </slot>
          </div>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section" v-if="showPagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingId ? editTitle : addTitle"
      :width="dialogWidth"
      :before-close="handleDialogClose"
      :append-to-body="true"
    >
      <slot name="form" :form="form" :rules="rules" :formRef="formRef" :isEdit="!!editingId">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
        >
          <slot name="form-items" :form="form" :isEdit="!!editingId" />
        </el-form>
      </slot>
      
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingId ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Search, Refresh, Edit, Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BatchOperationsGeneric from './BatchOperationsGeneric.vue'

const props = defineProps({
  // 数据相关
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  
  // 表格配置
  tableProps: {
    type: Object,
    default: () => ({})
  },
  
  // 功能开关
  showFilters: {
    type: Boolean,
    default: true
  },
  showStatusFilter: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: false
  },
  showAddButton: {
    type: Boolean,
    default: false
  },
  addButtonText: {
    type: String,
    default: '添加'
  },
  
  // 对话框配置
  addTitle: {
    type: String,
    default: '添加'
  },
  editTitle: {
    type: String,
    default: '编辑'
  },
  dialogWidth: {
    type: String,
    default: '500px'
  },
  actionWidth: {
    type: [String, Number],
    default: 160
  },
  
  // 表单配置
  form: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    default: () => ({})
  },
  
  // 删除确认配置
  deleteConfirmField: {
    type: String,
    default: 'name'
  },

  // 权限控制
  canCreate: {
    type: Boolean,
    default: true
  },
  canEdit: {
    type: Boolean,
    default: true
  },
  canDelete: {
    type: Boolean,
    default: true
  },

  // 批量操作
  enableBatch: {
    type: Boolean,
    default: false
  },
  batchOperations: {
    type: Array,
    default: () => []
  },
  enableBatchEdit: {
    type: Boolean,
    default: false
  },
  enableBatchCopy: {
    type: Boolean,
    default: false
  },
  batchEditFields: {
    type: Object,
    default: () => ({})
  },
  batchCopyFields: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits([
  'search',
  'reset-filters',
  'edit',
  'delete',
  'submit',
  'size-change',
  'current-change',
  'batch-operation',
  'batch-edit',
  'batch-copy'
])

// 响应式数据
const showDialog = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref()
const selectedItems = ref([])

const filters = reactive({
  search: '',
  is_active: null
})

// 监听筛选器变化，自动触发搜索（防抖处理）
let searchTimeout = null
watch(filters, (newFilters, oldFilters) => {
  // 只有在筛选器真正变化时才触发搜索
  if (JSON.stringify(newFilters) !== JSON.stringify(oldFilters)) {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    searchTimeout = setTimeout(() => {
      emit('search', { ...filters })
    }, 300) // 300ms防抖
  }
}, { deep: true })

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 方法
function handleSearch() {
  emit('search', { ...filters })
}

function resetFilters() {
  Object.keys(filters).forEach(key => {
    if (typeof filters[key] === 'string') {
      filters[key] = ''
    } else {
      filters[key] = null
    }
  })
  emit('reset-filters')
}

function handleEdit(row) {
  editingId.value = row.id
  emit('edit', row)
  showDialog.value = true
}

async function handleDelete(row) {
  try {
    const confirmText = `确定要删除"${row[props.deleteConfirmField]}"吗？`
    await ElMessageBox.confirm(confirmText, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    emit('delete', row)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await emit('submit', {
      isEdit: !!editingId.value,
      id: editingId.value,
      data: { ...props.form }
    })
    
    showDialog.value = false
    resetForm()
  } catch (error) {
    // 错误处理由父组件负责
  } finally {
    submitting.value = false
  }
}

function handleDialogClose() {
  showDialog.value = false
  resetForm()
}

function resetForm() {
  editingId.value = null
  formRef.value?.resetFields()
}

function handleSizeChange(size) {
  pagination.size = size
  emit('size-change', size)
}

function handleCurrentChange(page) {
  pagination.page = page
  emit('current-change', page)
}

// 批量操作相关方法
function handleSelectionChange(selection) {
  selectedItems.value = selection
}

function clearSelection() {
  selectedItems.value = []
}

function handleBatchOperation(operation) {
  emit('batch-operation', operation, selectedItems.value)
}

function handleBatchEdit(editData) {
  emit('batch-edit', editData, selectedItems.value)
}

function handleBatchCopy(copyData) {
  emit('batch-copy', copyData, selectedItems.value)
}

// 暴露方法给父组件
defineExpose({
  showDialog: () => { showDialog.value = true },
  hideDialog: () => { showDialog.value = false },
  resetForm,
  filters,
  pagination
})
</script>

<style scoped>
.crud-table-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-section {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.table-wrapper {
  flex: 1;
  overflow: hidden;
  margin-bottom: 24px;
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  height: 100%;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  margin-top: auto;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
}

:deep(.el-pagination .btn-next),
:deep(.el-pagination .btn-prev) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

:deep(.el-pagination .btn-next:hover),
:deep(.el-pagination .btn-prev:hover) {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

:deep(.el-pager li) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  margin: 0 4px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

:deep(.el-pager li:hover) {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

:deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}
</style>
