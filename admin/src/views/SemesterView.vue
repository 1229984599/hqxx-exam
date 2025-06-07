<template>
  <PageLayout
    title="学期管理"
    subtitle="管理学校的学期信息，设置学期状态和排序"
  >
    <template #actions>
      <el-button
        type="primary"
        @click="showAddDialog = true"
        :icon="Plus"
        size="large"
      >
        添加学期
      </el-button>
    </template>

    <!-- 数据表格 -->
    <el-table :data="semesters" v-loading="loading" class="modern-table">
      <el-table-column prop="name" label="学期名称" min-width="200">
        <template #default="{ row }">
          <div class="semester-name">
            <span class="name-text">{{ row.name }}</span>
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
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
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          <span class="date-text">{{ formatDate(row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" @click="editSemester(row)" :icon="Edit" />
            <el-button
              size="small"
              type="danger"
              @click="deleteSemester(row)"
              :icon="Delete"
            />
          </div>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingId ? '编辑学期' : '添加学期'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="学期名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入学期名称" />
        </el-form-item>
        
        <el-form-item label="学期代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入学期代码" />
        </el-form-item>
        
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSemester" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingId = ref(null)
const semesters = ref([])
const formRef = ref()

const form = reactive({
  name: '',
  code: '',
  sort_order: 0,
  is_active: true,
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入学期名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入学期代码', trigger: 'blur' }
  ]
}

onMounted(() => {
  loadSemesters()
})

async function loadSemesters() {
  loading.value = true
  try {
    const response = await api.get('/semesters/')
    semesters.value = response.data
  } catch (error) {
    ElMessage.error('加载学期列表失败')
  } finally {
    loading.value = false
  }
}

function editSemester(semester) {
  editingId.value = semester.id
  Object.assign(form, semester)
  showAddDialog.value = true
}

async function saveSemester() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    if (editingId.value) {
      await api.put(`/semesters/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/semesters/', form)
      ElMessage.success('添加成功')
    }
    
    showAddDialog.value = false
    resetForm()
    loadSemesters()
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
  }
}

async function deleteSemester(semester) {
  try {
    await ElMessageBox.confirm(`确定要删除学期"${semester.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/semesters/${semester.id}`)
    ElMessage.success('删除成功')
    loadSemesters()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    name: '',
    code: '',
    sort_order: 0,
    is_active: true,
    description: ''
  })
  formRef.value?.resetFields()
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.semester-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name-text {
  font-weight: 600;
  color: #2d3748;
  flex: 1;
}

.code-tag {
  flex-shrink: 0;
}

.date-text {
  color: #718096;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
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
</style>
