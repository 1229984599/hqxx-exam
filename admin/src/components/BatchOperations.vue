<template>
  <div class="batch-operations">
    <div class="batch-header" v-show="selectedItems.length > 0">
      <span class="selected-count" >
          已选择 {{ selectedItems.length }} 项
        </span>
      
      <div class="batch-actions">
        <el-button-group>
          <el-button
            v-if="canEdit"
            size="small"
            @click="showBatchUpdateDialog = true"
            :icon="Edit"
          >
            批量编辑
          </el-button>

          <el-button
            v-if="canCreate"
            size="small"
            @click="showBatchCopyDialog = true"
            :icon="CopyDocument"
          >
            批量复制
          </el-button>

          <el-button
            v-if="canDelete"
            size="small"
            type="danger"
            @click="handleBatchDelete"
            :icon="Delete"
          >
            批量删除
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 批量更新对话框 -->
    <el-dialog
      v-model="showBatchUpdateDialog"
      title="批量更新"
      width="600px"
      :before-close="closeBatchUpdateDialog"
    >
      <el-form :model="batchUpdateForm" label-width="100px">
        <el-form-item label="学期">
          <el-select v-model="batchUpdateForm.semester_id" placeholder="选择学期" clearable>
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="年级">
          <el-select v-model="batchUpdateForm.grade_id" placeholder="选择年级" clearable>
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="学科">
          <el-select v-model="batchUpdateForm.subject_id" placeholder="选择学科" clearable>
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select v-model="batchUpdateForm.category_id" placeholder="选择分类" clearable>
            <el-option
              v-for="category in filteredCategories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="难度">
          <el-select v-model="batchUpdateForm.difficulty" placeholder="选择难度" clearable>
            <el-option label="简单" :value="1" />
            <el-option label="较易" :value="2" />
            <el-option label="中等" :value="3" />
            <el-option label="较难" :value="4" />
            <el-option label="困难" :value="5" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="batchUpdateForm.is_active" placeholder="选择状态" clearable>
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="发布状态">
          <el-select v-model="batchUpdateForm.is_published" placeholder="选择发布状态" clearable>
            <el-option label="已发布" :value="true" />
            <el-option label="未发布" :value="false" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeBatchUpdateDialog">取消</el-button>
        <el-button type="primary" @click="handleBatchUpdate" :loading="batchLoading">
          确认更新
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量复制对话框 -->
    <el-dialog
      v-model="showBatchCopyDialog"
      title="批量复制"
      width="600px"
      :before-close="closeBatchCopyDialog"
    >
      <el-form :model="batchCopyForm" label-width="100px">
        <el-form-item label="目标学期">
          <el-select v-model="batchCopyForm.target_semester_id" placeholder="选择目标学期">
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标年级">
          <el-select v-model="batchCopyForm.target_grade_id" placeholder="选择目标年级">
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标学科">
          <el-select v-model="batchCopyForm.target_subject_id" placeholder="选择目标学科">
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标分类">
          <el-select v-model="batchCopyForm.target_category_id" placeholder="选择目标分类">
            <el-option
              v-for="category in copyFilteredCategories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeBatchCopyDialog">取消</el-button>
        <el-button type="primary" @click="handleBatchCopy" :loading="batchLoading">
          确认复制
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, CopyDocument, Delete } from '@element-plus/icons-vue'
import api from '../utils/api'
import { usePermissions } from '../composables/usePermissions'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  selectedItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:selectedItems', 'refresh'])

// 权限检查
const { hasPermission } = usePermissions()

// 响应式数据
const selectAll = ref(false)
const showBatchUpdateDialog = ref(false)
const showBatchCopyDialog = ref(false)
const batchLoading = ref(false)

// 表单数据
const batchUpdateForm = ref({
  semester_id: null,
  grade_id: null,
  subject_id: null,
  category_id: null,
  difficulty: null,
  is_active: null,
  is_published: null
})

const batchCopyForm = ref({
  target_semester_id: null,
  target_grade_id: null,
  target_subject_id: null,
  target_category_id: null
})

// 基础数据
const semesters = ref([])
const grades = ref([])
const subjects = ref([])
const categories = ref([])

// 计算属性
const isIndeterminate = computed(() => {
  const selectedCount = props.selectedItems.length
  return selectedCount > 0 && selectedCount < props.items.length
})

const filteredCategories = computed(() => {
  if (!batchUpdateForm.value.subject_id) return categories.value
  return categories.value.filter(cat => cat.subject_id === batchUpdateForm.value.subject_id)
})

const copyFilteredCategories = computed(() => {
  if (!batchCopyForm.value.target_subject_id) return categories.value
  return categories.value.filter(cat => cat.subject_id === batchCopyForm.value.target_subject_id)
})

// 权限计算属性
const canEdit = computed(() => hasPermission('questions:edit'))
const canCreate = computed(() => hasPermission('questions:create'))
const canDelete = computed(() => hasPermission('questions:delete'))

// 生命周期
onMounted(async () => {
  await loadBasicData()
})

// 监听全选状态
watch(() => props.selectedItems.length, (newLength) => {
  selectAll.value = newLength === props.items.length && newLength > 0
})

// 方法
async function loadBasicData() {
  try {
    const [semestersRes, gradesRes, subjectsRes, categoriesRes] = await Promise.all([
      api.get('/semesters/'),
      api.get('/grades/'),
      api.get('/subjects/'),
      api.get('/categories/')
    ])
    
    semesters.value = semestersRes.data
    grades.value = gradesRes.data
    subjects.value = subjectsRes.data
    categories.value = categoriesRes.data
  } catch (error) {
    console.error('加载基础数据失败:', error)
    ElMessage.error('加载基础数据失败')
  }
}

function handleSelectAll(checked) {
  if (checked) {
    emit('update:selectedItems', [...props.items])
  } else {
    emit('update:selectedItems', [])
  }
}

async function handleBatchUpdate() {
  if (props.selectedItems.length === 0) {
    ElMessage.warning('请先选择要更新的项目')
    return
  }

  try {
    batchLoading.value = true
    
    // 过滤掉空值
    const updateData = {}
    Object.keys(batchUpdateForm.value).forEach(key => {
      if (batchUpdateForm.value[key] !== null && batchUpdateForm.value[key] !== '') {
        updateData[key] = batchUpdateForm.value[key]
      }
    })
    
    if (Object.keys(updateData).length === 0) {
      ElMessage.warning('请至少选择一个要更新的字段')
      return
    }

    await api.post('/questions/batch/update', {
      question_ids: props.selectedItems.map(item => item.id),
      update_data: updateData
    })

    ElMessage.success(`成功更新 ${props.selectedItems.length} 个项目`)
    closeBatchUpdateDialog()
    emit('refresh')
  } catch (error) {
    console.error('批量更新失败:', error)
    ElMessage.error('批量更新失败')
  } finally {
    batchLoading.value = false
  }
}

async function handleBatchCopy() {
  if (props.selectedItems.length === 0) {
    ElMessage.warning('请先选择要复制的项目')
    return
  }

  try {
    batchLoading.value = true

    await api.post('/questions/batch/copy', {
      question_ids: props.selectedItems.map(item => item.id),
      ...batchCopyForm.value
    })

    ElMessage.success(`成功复制 ${props.selectedItems.length} 个项目`)
    closeBatchCopyDialog()
    emit('refresh')
  } catch (error) {
    console.error('批量复制失败:', error)
    ElMessage.error('批量复制失败')
  } finally {
    batchLoading.value = false
  }
}

async function handleBatchDelete() {
  if (props.selectedItems.length === 0) {
    ElMessage.warning('请先选择要删除的项目')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${props.selectedItems.length} 个项目吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    batchLoading.value = true

    await api.post('/questions/batch/delete', {
      question_ids: props.selectedItems.map(item => item.id)
    })

    ElMessage.success(`成功删除 ${props.selectedItems.length} 个项目`)
    emit('update:selectedItems', [])
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  } finally {
    batchLoading.value = false
  }
}

function closeBatchUpdateDialog() {
  showBatchUpdateDialog.value = false
  batchUpdateForm.value = {
    semester_id: null,
    grade_id: null,
    subject_id: null,
    category_id: null,
    difficulty: null,
    is_active: null,
    is_published: null
  }
}

function closeBatchCopyDialog() {
  showBatchCopyDialog.value = false
  batchCopyForm.value = {
    target_semester_id: null,
    target_grade_id: null,
    target_subject_id: null,
    target_category_id: null
  }
}
</script>

<style scoped>
.batch-operations {
  margin-bottom: 16px;
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-count {
  color: #409eff;
  font-weight: 500;
  font-size: 14px;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

/* 深色模式支持 */
.dark .batch-header {
  background: rgba(45, 55, 72, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .batch-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .batch-actions {
    justify-content: center;
  }
}
</style>
