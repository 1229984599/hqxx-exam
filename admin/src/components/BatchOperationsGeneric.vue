<template>
  <div class="batch-operations">
    <div class="batch-info">
      <el-icon class="info-icon"><InfoFilled /></el-icon>
      <span class="selected-text">已选择 {{ selectedCount }} 项</span>
    </div>

    <div class="batch-actions">
      <!-- 预定义的常用操作 -->
      <el-button
        v-if="enableEdit"
        size="small"
        type="primary"
        @click="showBatchEditDialog = true"
      >
        <el-icon><Edit /></el-icon>
        批量编辑
      </el-button>

      <el-button
        v-if="enableCopy"
        size="small"
        type="success"
        @click="showBatchCopyDialog = true"
      >
        <el-icon><CopyDocument /></el-icon>
        批量复制
      </el-button>

      <!-- 自定义操作 -->
      <el-button
        v-for="operation in operations"
        :key="operation.key"
        :type="operation.type || 'default'"
        size="small"
        @click="handleOperation(operation)"
      >
        <el-icon v-if="operation.icon">
          <component :is="getIconComponent(operation.icon)" />
        </el-icon>
        {{ operation.label }}
      </el-button>

      <el-button size="small" @click="handleClear">
        <el-icon><Close /></el-icon>
        取消选择
      </el-button>
    </div>

    <!-- 批量编辑对话框 -->
    <el-dialog
      v-model="showBatchEditDialog"
      title="批量编辑"
      width="600px"
      @close="resetBatchEditForm"
    >
      <el-form :model="batchEditForm" label-width="100px">
        <slot name="batch-edit-form" :form="batchEditForm">
          <!-- 默认的批量编辑表单 -->
          <el-form-item label="状态">
            <el-select v-model="batchEditForm.is_active" placeholder="选择状态" clearable>
              <el-option label="启用" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </el-form-item>
        </slot>
      </el-form>

      <template #footer>
        <el-button @click="showBatchEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchEdit" :loading="loading">
          确认编辑
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量复制对话框 -->
    <el-dialog
      v-model="showBatchCopyDialog"
      title="批量复制"
      width="600px"
      @close="resetBatchCopyForm"
    >
      <el-form :model="batchCopyForm" label-width="100px">
        <slot name="batch-copy-form" :form="batchCopyForm">
          <!-- 默认的批量复制表单 -->
          <el-form-item label="复制数量">
            <el-input-number v-model="batchCopyForm.copy_count" :min="1" :max="10" />
          </el-form-item>
        </slot>
      </el-form>

      <template #footer>
        <el-button @click="showBatchCopyDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchCopy" :loading="loading">
          确认复制
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  InfoFilled, Close, Check, Delete, Edit, Refresh,
  Download, Upload, Setting, CopyDocument
} from '@element-plus/icons-vue'

const props = defineProps({
  selectedCount: {
    type: Number,
    required: true
  },
  operations: {
    type: Array,
    default: () => []
  },
  enableEdit: {
    type: Boolean,
    default: false
  },
  enableCopy: {
    type: Boolean,
    default: false
  },
  editFields: {
    type: Object,
    default: () => ({})
  },
  copyFields: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['operation', 'clear', 'batch-edit', 'batch-copy'])

// 响应式数据
const loading = ref(false)
const showBatchEditDialog = ref(false)
const showBatchCopyDialog = ref(false)

// 表单数据
const batchEditForm = reactive({
  is_active: null,
  ...props.editFields
})

const batchCopyForm = reactive({
  copy_count: 1,
  ...props.copyFields
})

// 图标组件映射
const iconComponents = {
  Check,
  Close,
  Delete,
  Edit,
  Refresh,
  Download,
  Upload,
  Setting,
  CopyDocument
}

function getIconComponent(iconName) {
  return iconComponents[iconName] || Check
}

async function handleOperation(operation) {
  if (operation.confirm) {
    try {
      await ElMessageBox.confirm(
        operation.confirmText || `确定要执行"${operation.label}"操作吗？`,
        '确认操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: operation.type === 'danger' ? 'warning' : 'info'
        }
      )
      emit('operation', operation)
    } catch (error) {
      // 用户取消操作
    }
  } else {
    emit('operation', operation)
  }
}

function handleClear() {
  emit('clear')
}

async function handleBatchEdit() {
  try {
    loading.value = true

    // 过滤掉空值
    const editData = {}
    Object.keys(batchEditForm).forEach(key => {
      if (batchEditForm[key] !== null && batchEditForm[key] !== '') {
        editData[key] = batchEditForm[key]
      }
    })

    if (Object.keys(editData).length === 0) {
      ElMessage.warning('请至少选择一个要编辑的字段')
      return
    }

    emit('batch-edit', editData)
    showBatchEditDialog.value = false
    resetBatchEditForm()
    ElMessage.success('批量编辑操作已提交')
  } catch (error) {
    console.error('批量编辑失败:', error)
    ElMessage.error('批量编辑失败')
  } finally {
    loading.value = false
  }
}

async function handleBatchCopy() {
  try {
    loading.value = true

    const copyData = { ...batchCopyForm }
    emit('batch-copy', copyData)
    showBatchCopyDialog.value = false
    resetBatchCopyForm()
    ElMessage.success('批量复制操作已提交')
  } catch (error) {
    console.error('批量复制失败:', error)
    ElMessage.error('批量复制失败')
  } finally {
    loading.value = false
  }
}

function resetBatchEditForm() {
  Object.keys(batchEditForm).forEach(key => {
    if (key !== 'is_active') {
      batchEditForm[key] = null
    } else {
      batchEditForm[key] = null
    }
  })
}

function resetBatchCopyForm() {
  Object.keys(batchCopyForm).forEach(key => {
    if (key === 'copy_count') {
      batchCopyForm[key] = 1
    } else {
      batchCopyForm[key] = null
    }
  })
}
</script>

<style scoped>
.batch-operations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 1px solid #bbdefb;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1976d2;
  font-weight: 500;
}

.info-icon {
  font-size: 18px;
  color: #2196f3;
}

.selected-text {
  font-size: 14px;
}

.batch-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.batch-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.batch-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .batch-operations {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .batch-info {
    justify-content: center;
  }
  
  .batch-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
