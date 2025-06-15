<template>
  <PageLayout
    title="管理员管理"
    subtitle="管理系统管理员账户和角色分配"
  >
    <template #actions>
      <el-button
        v-permission="'admins:create'"
        type="primary"
        @click="showAddDialog = true"
        :icon="Plus"
        size="large"
      >
        添加管理员
      </el-button>
    </template>

    <!-- 搜索筛选 -->
    <div class="search-filters">
      <el-form :model="searchForm" inline class="filter-form">
        <el-form-item>
          <el-input
            v-model="searchForm.search"
            placeholder="搜索用户名、邮箱或姓名"
            clearable
            :prefix-icon="Search"
            style="width: 280px"
            @keyup.enter="loadAdmins"
          />
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="searchForm.is_active"
            placeholder="选择状态"
            clearable
            style="width: 140px"
          >
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadAdmins" :icon="Search">搜索</el-button>
          <el-button @click="resetSearch" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 批量操作 -->
    <BatchOperations
      v-if="selectedAdmins.length > 0"
      :selected-count="selectedAdmins.length"
      :operations="batchOperations"
      @operation="handleBatchOperation"
      @clear="clearSelection"
    />

    <!-- 管理员列表 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="admins"
        stripe
        style="width: 100%"
        :header-cell-style="{ background: '#f8f9fa', color: '#495057' }"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="full_name" label="姓名" min-width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column align="center" label="超级管理员" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_superuser" type="warning">是</el-tag>
            <el-tag type="danger" v-else>否</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="150">
          <template #default="{ row }">
            <div class="role-tags">
              <el-tag
                v-for="role in row.roles || []"
                :key="role.id"
                size="small"
                type="info"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ role.name }}
              </el-tag>
              <span v-if="!row.roles || row.roles.length === 0" class="no-roles">
                未分配角色
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                v-permission="'admins:edit'"
                size="small"
                @click="editAdmin(row)"
                :icon="Edit"
              />
              <el-button
                v-permission="'admins:delete'"
                v-if="!row.is_superuser && row.id !== authStore.user?.id"
                size="small"
                type="danger"
                @click="deleteAdmin(row)"
                :icon="Delete"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadAdmins"
          @current-change="loadAdmins"
        />
      </div>
    </div>
  </PageLayout>

    <!-- 添加/编辑管理员对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingAdmin ? '编辑管理员' : '添加管理员'"
      width="700px"
      @close="resetForm"
      :close-on-click-modal="false"
    >
      <el-form
        ref="adminFormRef"
        :model="adminForm"
        :rules="adminRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="adminForm.username" 
            :disabled="!!editingAdmin"
            placeholder="请输入用户名"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="adminForm.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="adminForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="adminForm.password"
            type="password"
            :placeholder="editingAdmin ? '留空则不修改密码' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch 
            v-model="adminForm.is_active" 
            active-text="激活" 
            inactive-text="禁用"
          />
        </el-form-item>
        <el-form-item label="超级管理员">
          <el-switch
            v-model="adminForm.is_superuser"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
        <el-form-item label="分配角色">
          <el-select
            v-model="adminForm.role_ids"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option
              v-for="role in availableRoles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="saving"
          @click="saveAdmin"
        >
          {{ editingAdmin ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useAuthStore } from '../stores/auth'
import { usePermissions } from '../composables/usePermissions'
import PageLayout from '../components/PageLayout.vue'
import BatchOperations from '../components/BatchOperations.vue'

const authStore = useAuthStore()
const { hasRole, hasAnyRole, isAdmin } = usePermissions()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const admins = ref([])
const availableRoles = ref([])
const showAddDialog = ref(false)
const editingAdmin = ref(null)
const adminFormRef = ref()
const selectedAdmins = ref([])

// 批量操作配置
const batchOperations = [
  {
    key: 'activate',
    label: '批量激活',
    type: 'success',
    icon: 'Check',
    confirm: true,
    confirmText: '确定要激活选中的管理员吗？'
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'warning',
    icon: 'Close',
    confirm: true,
    confirmText: '确定要禁用选中的管理员吗？'
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'Delete',
    confirm: true,
    confirmText: '确定要删除选中的管理员吗？此操作不可恢复！'
  }
]

// 搜索表单
const searchForm = reactive({
  search: '',
  is_active: null
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 管理员表单
const adminForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  is_active: true,
  is_superuser: false,
  role_ids: []
})

// 表单验证规则
const adminRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
    {
      validator: async (rule, value, callback) => {
        if (!value || editingAdmin.value) {
          callback()
          return
        }
        try {
          const response = await api.get('/system/admins/check-username', {
            params: { username: value }
          })
          if (response.data.exists) {
            callback(new Error('用户名已存在'))
          } else {
            callback()
          }
        } catch (error) {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    {
      validator: (rule, value, callback) => {
        if (!editingAdmin.value && !value) {
          callback(new Error('请输入密码'))
        } else if (value && value.length < 6) {
          callback(new Error('密码长度至少 6 个字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载管理员列表
async function loadAdmins() {
  try {
    loading.value = true
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      include_roles: true  // 请求包含角色信息
    }

    if (searchForm.search) {
      params.search = searchForm.search
    }

    if (searchForm.is_active !== null) {
      params.is_active = searchForm.is_active
    }

    const response = await api.get('/system/admins', { params })
    admins.value = response.data.items || response.data
    pagination.total = response.data.total || admins.value.length
  } catch (error) {
    console.error('加载管理员列表失败:', error)
    ElMessage.error('加载管理员列表失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
function resetSearch() {
  searchForm.search = ''
  searchForm.is_active = null
  pagination.page = 1
  loadAdmins()
}

// 编辑管理员
async function editAdmin(admin) {
  editingAdmin.value = admin

  // 从管理员数据中获取角色ID
  const roleIds = admin.roles ? admin.roles.map(role => role.id) : []

  Object.assign(adminForm, {
    username: admin.username,
    email: admin.email,
    full_name: admin.full_name || '',
    password: '',
    is_active: admin.is_active,
    is_superuser: admin.is_superuser,
    role_ids: roleIds
  })

  showAddDialog.value = true
}

// 保存管理员
async function saveAdmin() {
  try {
    await adminFormRef.value.validate()
    saving.value = true

    const data = { ...adminForm }

    if (editingAdmin.value) {
      // 编辑时不发送密码字段（除非有值）
      if (!data.password) {
        delete data.password
      }

      // 更新管理员信息（包括角色分配）
      await api.put(`/system/admins/${editingAdmin.value.id}`, data)
      ElMessage.success('管理员更新成功')
    } else {
      // 创建新管理员（包括角色分配）
      await api.post('/system/admins', data)
      ElMessage.success('管理员创建成功')
    }

    showAddDialog.value = false
    await loadAdmins()
  } catch (error) {
    console.error('保存管理员失败:', error)
    ElMessage.error('保存管理员失败')
  } finally {
    saving.value = false
  }
}

// 删除管理员
async function deleteAdmin(admin) {
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 "${admin.username}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/system/admins/${admin.id}`)
    ElMessage.success('管理员删除成功')
    await loadAdmins()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除管理员失败:', error)
      ElMessage.error('删除管理员失败')
    }
  }
}

// 重置表单
function resetForm() {
  editingAdmin.value = null
  Object.assign(adminForm, {
    username: '',
    email: '',
    full_name: '',
    password: '',
    is_active: true,
    is_superuser: false,
    role_ids: []
  })
  adminFormRef.value?.resetFields()
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载时加载数据
onMounted(() => {
  loadAdmins()
  loadRoles()
})

// 加载可用角色
async function loadRoles() {
  try {
    const response = await api.get('/roles/')
    availableRoles.value = response.data.filter(role => role.is_active)
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

// 批量操作相关方法
function handleSelectionChange(selection) {
  selectedAdmins.value = selection
}

function clearSelection() {
  selectedAdmins.value = []
}

async function handleBatchOperation(operation) {
  if (selectedAdmins.value.length === 0) {
    ElMessage.warning('请先选择要操作的管理员')
    return
  }

  try {
    const adminIds = selectedAdmins.value.map(admin => admin.id)

    switch (operation.key) {
      case 'activate':
        await api.post('/system/admins/batch-activate', { admin_ids: adminIds })
        ElMessage.success(`成功激活 ${adminIds.length} 个管理员`)
        break
      case 'deactivate':
        await api.post('/system/admins/batch-deactivate', { admin_ids: adminIds })
        ElMessage.success(`成功禁用 ${adminIds.length} 个管理员`)
        break
      case 'delete':
        // 过滤掉超级管理员和当前用户
        const deletableIds = selectedAdmins.value
          .filter(admin => !admin.is_superuser && admin.id !== authStore.user?.id)
          .map(admin => admin.id)

        if (deletableIds.length === 0) {
          ElMessage.warning('选中的管理员中没有可删除的用户')
          return
        }

        await api.post('/system/admins/batch-delete', { admin_ids: deletableIds })
        ElMessage.success(`成功删除 ${deletableIds.length} 个管理员`)
        break
    }

    clearSelection()
    await loadAdmins()
  } catch (error) {
    console.error('批量操作失败:', error)
    ElMessage.error('批量操作失败')
  }
}
</script>

<style scoped>
/* 搜索筛选区域 */
.search-filters {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
}

.filter-form {
  margin: 0;
}

.filter-form .el-form-item {
  margin-bottom: 0;
  margin-right: 16px;
}

.filter-form .el-form-item:last-child {
  margin-right: 0;
}

/* 表格容器 */
.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-buttons .el-button {
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 分页 */
.pagination-wrapper {
  padding: 20px;
  display: flex;
  justify-content: center;
  background: #fafbfc;
  border-top: 1px solid #e4e7ed;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 0;
}

:deep(.el-table th) {
  background: #f8f9fa !important;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #e9ecef;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f1f3f4;
  padding: 16px 0;
}

:deep(.el-table tr:hover > td) {
  background-color: #f8f9fa !important;
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  padding: 4px 12px;
}

/* 角色标签 */
.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.no-roles {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  margin: 0;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

/* 表单样式 */
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #495057;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-switch) {
  --el-switch-on-color: #67c23a;
  --el-switch-off-color: #dcdfe6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filters {
    padding: 16px;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 16px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
