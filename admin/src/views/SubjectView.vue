<template>
  <PageLayout
    title="学科管理"
    subtitle="管理学校的学科信息，设置学科颜色和排序"
  >
    <template #actions>
      <el-button
        type="primary"
        :icon="Plus"
        size="large"
        @click="showAddDialog = true"
      >
        添加学科
      </el-button>
    </template>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item>
          <el-button
            type="primary"
            @click="showAddDialog = true"
            :icon="Plus"
            size="default"
          >
            添加学科
          </el-button>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="请选择状态" clearable @change="loadSubjects" style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="搜索学科名称或代码"
            clearable
            style="width: 200px"
            @keyup.enter="loadSubjects"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadSubjects" :icon="Search">
            搜索
          </el-button>
          <el-button @click="resetFilters" :icon="Refresh">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <el-table :data="subjects" v-loading="loading" class="modern-table">
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
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" :icon="Edit" @click="editSubject(row)" />
            <el-button size="small" type="danger" :icon="Delete" @click="deleteSubject(row)" />
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingId ? '编辑学科' : '添加学科'"
      width="500px"
      :before-close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
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
      </el-form>
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingId ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)
const submitting = ref(false)
const showAddDialog = ref(false)
const editingId = ref(null)
const formRef = ref()
const allSubjects = ref([])

const filters = reactive({
  is_active: null,
  search: ''
})

// 计算过滤后的学科列表
const subjects = computed(() => {
  let filtered = allSubjects.value

  // 按状态筛选
  if (filters.is_active !== null) {
    filtered = filtered.filter(subject => subject.is_active === filters.is_active)
  }

  // 按搜索关键词筛选
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(subject =>
      subject.name.toLowerCase().includes(searchLower) ||
      subject.code.toLowerCase().includes(searchLower)
    )
  }

  return filtered
})

const form = reactive({
  name: '',
  code: '',
  color: '#667eea',
  sort_order: 1,
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入学科名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入学科代码', trigger: 'blur' }],
  color: [{ required: true, message: '请选择主题色', trigger: 'blur' }],
  sort_order: [{ required: true, message: '请输入排序', trigger: 'blur' }]
}

onMounted(() => {
  loadSubjects()
})

async function loadSubjects() {
  loading.value = true
  try {
    const response = await api.get('/subjects/')
    allSubjects.value = response.data
  } catch (error) {
    ElMessage.error('加载学科失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, {
    is_active: null,
    search: ''
  })
}

function editSubject(subject) {
  editingId.value = subject.id
  Object.assign(form, subject)
  showAddDialog.value = true
}

async function deleteSubject(subject) {
  try {
    await ElMessageBox.confirm(`确定要删除学科"${subject.name}"吗？`, '确认删除', {
      type: 'warning'
    })

    await api.delete(`/subjects/${subject.id}`)
    ElMessage.success('删除成功')
    await loadSubjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleDialogClose() {
  showAddDialog.value = false
  editingId.value = null
  resetForm()
}

function resetForm() {
  Object.assign(form, {
    name: '',
    code: '',
    color: '#667eea',
    sort_order: 1,
    is_active: true
  })
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (editingId.value) {
      await api.put(`/subjects/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/subjects/', form)
      ElMessage.success('创建成功')
    }

    handleDialogClose()
    await loadSubjects()
  } catch (error) {
    ElMessage.error(editingId.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
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

.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.subject-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.name-text {
  font-weight: 600;
  color: #2d3748;
  flex: 1;
}

.code-tag {
  flex-shrink: 0;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.color-block {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.color-text {
  font-size: 12px;
  color: #718096;
  font-family: monospace;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>
