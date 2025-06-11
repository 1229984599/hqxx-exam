<template>
  <PageLayout
      title="年级管理"
      subtitle="管理学校的年级信息，设置年级级别和排序"
  >
    <template #actions>
      <el-button
          type="primary"
          :icon="Plus"
          size="large"
          @click="showAddDialog = true"
      >
        添加年级
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
            添加年级
          </el-button>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="请选择状态" clearable @change="loadGrades"
                     style="width: 120px">
            <el-option label="启用" :value="true"/>
            <el-option label="禁用" :value="false"/>
          </el-select>
        </el-form-item>

        <el-form-item label="年级级别">
          <el-select v-model="filters.level" placeholder="请选择级别" clearable @change="loadGrades"
                     style="width: 120px">
            <el-option v-for="i in 12" :key="i" :label="`第${i}级`" :value="i"/>
          </el-select>
        </el-form-item>

        <el-form-item label="搜索">
          <el-input
              v-model="filters.search"
              placeholder="搜索年级名称或代码"
              clearable
              style="width: 200px"
              @keyup.enter="loadGrades"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadGrades" :icon="Search">
            搜索
          </el-button>
          <el-button @click="resetFilters" :icon="Refresh">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <el-table :data="grades" v-loading="loading" class="modern-table">
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
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" :icon="Edit" @click="editGrade(row)"/>
            <el-button size="small" type="danger" :icon="Delete" @click="deleteGrade(row)"/>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
        v-model="showAddDialog"
        :title="editingId ? '编辑年级' : '添加年级'"
        width="500px"
        :before-close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
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
import {ref, reactive, onMounted, computed} from 'vue'
import {Plus, Edit, Delete, Search, Refresh} from '@element-plus/icons-vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)
const submitting = ref(false)
const showAddDialog = ref(false)
const editingId = ref(null)
const formRef = ref()
const allGrades = ref([])

const filters = reactive({
  is_active: null,
  level: null,
  search: ''
})

// 计算过滤后的年级列表
const grades = computed(() => {
  let filtered = allGrades.value

  // 按状态筛选
  if (filters.is_active !== null) {
    filtered = filtered.filter(grade => grade.is_active === filters.is_active)
  }

  // 按级别筛选
  if (filters.level !== null) {
    filtered = filtered.filter(grade => grade.level === filters.level)
  }

  // 按搜索关键词筛选
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(grade =>
        grade.name.toLowerCase().includes(searchLower) ||
        grade.code.toLowerCase().includes(searchLower)
    )
  }

  return filtered
})

const form = reactive({
  name: '',
  code: '',
  level: 1,
  sort_order: 1,
  is_active: true
})

const rules = {
  name: [{required: true, message: '请输入年级名称', trigger: 'blur'}],
  code: [{required: true, message: '请输入年级代码', trigger: 'blur'}],
  level: [{required: true, message: '请输入年级级别', trigger: 'blur'}],
  sort_order: [{required: true, message: '请输入排序', trigger: 'blur'}]
}

onMounted(() => {
  loadGrades()
})

async function loadGrades() {
  loading.value = true
  try {
    const response = await api.get('/grades/')
    allGrades.value = response.data
  } catch (error) {
    ElMessage.error('加载年级失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, {
    is_active: null,
    level: null,
    search: ''
  })
}

function getLevelType(level) {
  const types = {1: 'primary', 2: 'success', 3: 'warning', 4: 'danger', 5: 'info', 6: 'danger'}
  return types[level] || 'info'
}

function editGrade(grade) {
  editingId.value = grade.id
  Object.assign(form, grade)
  showAddDialog.value = true
}

async function deleteGrade(grade) {
  try {
    await ElMessageBox.confirm(`确定要删除年级"${grade.name}"吗？`, '确认删除', {
      type: 'warning'
    })

    await api.delete(`/grades/${grade.id}`)
    ElMessage.success('删除成功')
    await loadGrades()
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
    level: 1,
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
      await api.put(`/grades/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/grades/', form)
      ElMessage.success('创建成功')
    }

    handleDialogClose()
    await loadGrades()
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

.grade-name {
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

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>
