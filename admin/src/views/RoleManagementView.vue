<template>
  <PageLayout
    title="角色权限管理"
    subtitle="管理系统角色和权限分配"
  >
    <div class="role-management">
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button
          v-permission="'admins:create'"
          type="primary"
          @click="showCreateDialog = true"
        >
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
        <el-button @click="loadRoles">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <!-- 批量操作 -->
      <BatchOperations
        v-if="selectedRoles.length > 0"
        :selected-count="selectedRoles.length"
        :operations="batchOperations"
        @operation="handleBatchOperation"
        @clear="clearSelection"
      />

      <!-- 角色列表 -->
      <el-table
        :data="roles"
        v-loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色代码" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="permission_count" label="权限数" width="100" align="center" />
        <el-table-column prop="admin_count" label="用户数" width="100" align="center" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_system" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_system ? 'warning' : 'info'">
              {{ row.is_system ? '系统' : '自定义' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="center">
          <template #default="{ row }">
            <el-button
              v-permission="'admins:edit'"
              size="small"
              @click="editRole(row)"
            >
              编辑
            </el-button>
            <el-button
              v-permission="'admins:edit'"
              size="small"
              @click="managePermissions(row)"
            >
              权限
            </el-button>
            <el-button
              v-permission="'admins:delete'"
              size="small"
              type="danger"
              @click="deleteRole(row)"
              :disabled="row.is_system"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 创建/编辑角色对话框 -->
      <el-dialog 
        v-model="showCreateDialog" 
        :title="editingRole ? '编辑角色' : '创建角色'"
        :append-to-body="true"
        width="500px"
      >
        <el-form :model="roleForm" :rules="roleRules" ref="roleFormRef" label-width="100px">
          <el-form-item label="角色名称" prop="name">
            <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
          </el-form-item>
          <el-form-item label="角色代码" prop="code">
            <el-input 
              v-model="roleForm.code" 
              placeholder="请输入角色代码"
              :disabled="editingRole"
            />
          </el-form-item>
          <el-form-item label="描述">
            <el-input 
              v-model="roleForm.description" 
              type="textarea" 
              placeholder="请输入角色描述"
              :rows="3"
            />
          </el-form-item>
          <el-form-item label="状态" v-if="editingRole">
            <el-switch v-model="roleForm.is_active" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveRole" :loading="saving">
            {{ editingRole ? '更新' : '创建' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- 权限管理对话框 -->
      <el-dialog
        v-model="showPermissionDialog"
        :title="`权限管理 - ${currentRole?.name}`"
        :append-to-body="true"
        width="1200px"
        top="5vh"
      >
        <div v-if="currentRole" class="permission-management">
          <!-- 权限统计 -->
          <div class="permission-stats">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="总权限数" :value="totalPermissions" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="已分配" :value="assignedPermissions" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="分配率" :value="permissionRate" suffix="%" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="角色类型" :value="currentRole.code" />
              </el-col>
            </el-row>
          </div>

          <!-- 快速操作 -->
          <div class="quick-actions">
            <div class="action-group">
              <span class="action-label">批量操作：</span>
              <el-button-group>
                <el-button @click="selectAllPermissions" :icon="Check" size="small">全选</el-button>
                <el-button @click="clearAllPermissions" :icon="Close" size="small">清空</el-button>
              </el-button-group>
            </div>
            <el-divider direction="vertical" />
            <div class="template-group">
              <span class="template-label">快速模板：</span>
              <div class="template-buttons">
                <el-button
                  @click="selectByTemplate('admin')"
                  class="template-btn template-admin"
                  size="small"
                >
                  <el-icon><User /></el-icon>
                  管理员
                </el-button>
                <el-button
                  @click="selectByTemplate('teacher')"
                  class="template-btn template-teacher"
                  size="small"
                >
                  <el-icon><Reading /></el-icon>
                  教师
                </el-button>
                <el-button
                  @click="selectByTemplate('viewer')"
                  class="template-btn template-viewer"
                  size="small"
                >
                  <el-icon><View /></el-icon>
                  查看者
                </el-button>
              </div>
            </div>
          </div>

          <!-- 权限分组卡片 -->
          <div class="permission-groups">
            <el-row :gutter="16">
              <el-col :span="12" v-for="group in permissionGroups" :key="group.key">
                <el-card class="permission-group-card" shadow="hover">
                  <template #header>
                    <div class="group-header">
                      <div class="group-info">
                        <el-icon class="group-icon" :style="{ color: group.color }">
                          <component :is="group.icon" />
                        </el-icon>
                        <div>
                          <h4>{{ group.title }}</h4>
                          <p>{{ group.description }}</p>
                        </div>
                      </div>
                      <div class="group-actions">
                        <el-checkbox
                          :model-value="isGroupFullySelected(group)"
                          :indeterminate="isGroupPartiallySelected(group)"
                          @change="toggleGroupSelection(group, $event)"
                          size="large"
                        >
                          全选
                        </el-checkbox>
                      </div>
                    </div>
                  </template>

                  <div class="permission-items">
                    <div
                      v-for="permission in group.permissions"
                      :key="permission.code"
                      class="permission-item"
                    >
                      <el-checkbox
                        v-model="selectedPermissionCodes"
                        :label="permission.code"
                        :value="permission.code"
                        class="permission-checkbox"
                      >
                        <div class="permission-content">
                          <span class="permission-name">{{ permission.name }}</span>
                          <span class="permission-desc">{{ permission.description }}</span>
                        </div>
                      </el-checkbox>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>

        <template #footer>
          <div class="dialog-footer">
            <div class="footer-info">
              <el-tag type="info">已选择 {{ selectedPermissionCodes.length }} 个权限</el-tag>
            </div>
            <div class="footer-actions">
              <el-button @click="showPermissionDialog = false">取消</el-button>
              <el-button
                type="primary"
                :loading="savingPermissions"
                @click="savePermissions"
                :disabled="selectedPermissionCodes.length === 0"
              >
                保存权限
              </el-button>
            </div>
          </div>
        </template>
      </el-dialog>

      <!-- 批量权限分配对话框 -->
      <el-dialog
        v-model="showBatchPermissionDialog"
        title="批量权限分配"
        width="800px"
        @close="batchPermissionForm.permission_codes = []"
      >
        <div class="batch-permission-content">
          <div class="selected-roles">
            <h4>选中的角色 ({{ selectedRoles.length }}个)</h4>
            <div class="role-list">
              <el-tag
                v-for="role in selectedRoles"
                :key="role.id"
                type="info"
                style="margin-right: 8px; margin-bottom: 8px;"
              >
                {{ role.name }}
              </el-tag>
            </div>
          </div>

          <el-divider />

          <div class="permission-selection">
            <h4>选择要分配的权限</h4>
            <div class="permission-groups">
              <div
                v-for="group in permissionGroups"
                :key="group.key"
                class="permission-group"
              >
                <div class="group-header">
                  <el-checkbox
                    :model-value="isGroupSelected(group)"
                    :indeterminate="isGroupIndeterminate(group)"
                    @change="toggleGroup(group, $event)"
                  >
                    {{ group.title }}
                  </el-checkbox>
                </div>
                <div class="group-permissions">
                  <el-checkbox
                    v-for="permission in group.permissions"
                    :key="permission.code"
                    v-model="batchPermissionForm.permission_codes"
                    :label="permission.code"
                    :value="permission.code"
                  >
                    {{ permission.name }}
                  </el-checkbox>
                </div>
              </div>
            </div>
          </div>
        </div>

        <template #footer>
          <el-button @click="showBatchPermissionDialog = false">取消</el-button>
          <el-button
            type="primary"
            :loading="savingPermissions"
            @click="handleBatchPermissionAssign"
          >
            分配权限
          </el-button>
        </template>
      </el-dialog>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Check, Close, Document, User, Setting,
  Monitor, FolderOpened, Reading, View
} from '@element-plus/icons-vue'
import { usePermissions } from '../composables/usePermissions'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'
import BatchOperations from '../components/BatchOperations.vue'

const { hasAnyRole } = usePermissions()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const savingPermissions = ref(false)
const showCreateDialog = ref(false)
const showPermissionDialog = ref(false)
const editingRole = ref(null)
const currentRole = ref(null)
const roles = ref([])
const permissions = ref([])
const permissionTree = ref([])
const selectedPermissions = ref([])
const selectedPermissionCodes = ref([])
const selectedRoles = ref([])
const showBatchPermissionDialog = ref(false)
const batchPermissionForm = reactive({
  permission_codes: []
})

// 批量操作配置
const batchOperations = [
  {
    key: 'assign_permissions',
    label: '批量分配权限',
    type: 'primary',
    icon: 'Setting',
    confirm: false
  },
  {
    key: 'activate',
    label: '批量激活',
    type: 'success',
    icon: 'Check',
    confirm: true,
    confirmText: '确定要激活选中的角色吗？'
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'warning',
    icon: 'Close',
    confirm: true,
    confirmText: '确定要禁用选中的角色吗？'
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'Delete',
    confirm: true,
    confirmText: '确定要删除选中的角色吗？此操作不可恢复！'
  }
]

// 表单数据
const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
})

// 表单验证规则
const roleRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' },
    { pattern: /^[a-z_]+$/, message: '角色代码只能包含小写字母和下划线', trigger: 'blur' }
  ]
}

// 引用
const roleFormRef = ref()
const permissionTreeRef = ref()

// 权限分组配置
const permissionGroups = ref([
  {
    key: 'questions',
    title: '试题管理',
    description: '试题的查看、创建、编辑、删除等操作',
    icon: 'Document',
    color: '#409EFF',
    permissions: []
  },
  {
    key: 'templates',
    title: '模板管理',
    description: '模板的查看、创建、编辑、删除等操作',
    icon: 'FolderOpened',
    color: '#67C23A',
    permissions: []
  },
  {
    key: 'basic_data',
    title: '基础数据',
    description: '学期、年级、学科、分类等基础数据管理',
    icon: 'Setting',
    color: '#E6A23C',
    permissions: []
  },
  {
    key: 'admins',
    title: '用户管理',
    description: '管理员账户和角色权限管理',
    icon: 'User',
    color: '#F56C6C',
    permissions: []
  },
  {
    key: 'system',
    title: '系统管理',
    description: '系统监控、配置、备份等高级功能',
    icon: 'Monitor',
    color: '#909399',
    permissions: []
  }
])

// 计算属性
const totalPermissions = computed(() => permissions.value.length)
const assignedPermissions = computed(() => selectedPermissionCodes.value.length)
const permissionRate = computed(() => {
  if (totalPermissions.value === 0) return 0
  return Math.round((assignedPermissions.value / totalPermissions.value) * 100)
})

// 生命周期
onMounted(() => {
  loadRoles()
  loadPermissions()
})

// 方法
async function loadRoles() {
  try {
    loading.value = true
    const response = await api.get('/roles/')
    roles.value = response.data
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

async function loadPermissions() {
  try {
    const response = await api.get('/roles/permissions')
    permissions.value = response.data
    buildPermissionTree()
    buildPermissionGroups()
  } catch (error) {
    console.error('加载权限列表失败:', error)
  }
}

function buildPermissionTree() {
  const tree = {}
  
  permissions.value.forEach(permission => {
    if (!tree[permission.resource]) {
      tree[permission.resource] = {
        id: permission.resource,
        label: getResourceName(permission.resource),
        children: []
      }
    }
    
    tree[permission.resource].children.push({
      id: permission.id,
      label: permission.name,
      code: permission.code
    })
  })
  
  permissionTree.value = Object.values(tree)
}

function getResourceName(resource) {
  const names = {
    'questions': '试题管理',
    'admins': '用户管理',
    'basic_data': '基础数据',
    'templates': '模板管理',
    'system': '系统管理',
    'analytics': '统计分析'
  }
  return names[resource] || resource
}

function buildPermissionGroups() {
  // 重置权限分组
  permissionGroups.value.forEach(group => {
    group.permissions = []
  })

  // 按资源分组权限
  permissions.value.forEach(permission => {
    const group = permissionGroups.value.find(g => g.key === permission.resource)
    if (group) {
      group.permissions.push({
        id: permission.id,
        code: permission.code,
        name: permission.name,
        description: permission.description || getPermissionDescription(permission.code)
      })
    }
  })
}

function getPermissionDescription(code) {
  const descriptions = {
    'questions:view': '查看试题列表和详情',
    'questions:create': '创建新的试题',
    'questions:edit': '编辑现有试题',
    'questions:delete': '删除试题',
    'questions:export': '导出试题数据',
    'questions:batch': '批量操作试题',
    'templates:view': '查看模板列表',
    'templates:create': '创建新模板',
    'templates:edit': '编辑模板内容',
    'templates:delete': '删除模板',
    'basic_data:view': '查看基础数据',
    'basic_data:edit': '编辑基础数据',
    'admins:view': '查看管理员列表',
    'admins:create': '创建管理员账户',
    'admins:edit': '编辑管理员信息',
    'admins:delete': '删除管理员账户',
    'system:view': '查看系统信息',
    'system:config': '修改系统配置',
    'system:backup': '数据备份管理',
    'system:logs': '查看系统日志'
  }
  return descriptions[code] || '执行相关操作'
}

function editRole(role) {
  editingRole.value = role
  Object.assign(roleForm, {
    name: role.name,
    code: role.code,
    description: role.description,
    is_active: role.is_active
  })
  showCreateDialog.value = true
}

async function saveRole() {
  try {
    await roleFormRef.value.validate()
    saving.value = true
    
    if (editingRole.value) {
      // 更新角色
      await api.put(`/roles/${editingRole.value.id}`, {
        name: roleForm.name,
        description: roleForm.description,
        is_active: roleForm.is_active
      })
      ElMessage.success('角色更新成功')
    } else {
      // 创建角色
      await api.post('/roles/', {
        name: roleForm.name,
        code: roleForm.code,
        description: roleForm.description
      })
      ElMessage.success('角色创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    await loadRoles()
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error('保存角色失败')
  } finally {
    saving.value = false
  }
}

async function deleteRole(role) {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/roles/${role.id}`)
    ElMessage.success('角色删除成功')
    await loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除角色失败:', error)
      ElMessage.error('删除角色失败')
    }
  }
}

async function managePermissions(role) {
  try {
    currentRole.value = role

    // 获取角色当前权限
    const response = await api.get(`/roles/${role.id}/permissions`)
    selectedPermissions.value = response.data.map(p => p.id)
    selectedPermissionCodes.value = response.data.map(p => p.code)

    showPermissionDialog.value = true
  } catch (error) {
    console.error('加载角色权限失败:', error)
    ElMessage.error('加载角色权限失败')
  }
}

// 权限组操作方法
function isGroupFullySelected(group) {
  if (group.permissions.length === 0) return false
  return group.permissions.every(p => selectedPermissionCodes.value.includes(p.code))
}

function isGroupPartiallySelected(group) {
  if (group.permissions.length === 0) return false
  const selectedCount = group.permissions.filter(p => selectedPermissionCodes.value.includes(p.code)).length
  return selectedCount > 0 && selectedCount < group.permissions.length
}

function toggleGroupSelection(group, selected) {
  if (selected) {
    // 选中组内所有权限
    group.permissions.forEach(permission => {
      if (!selectedPermissionCodes.value.includes(permission.code)) {
        selectedPermissionCodes.value.push(permission.code)
      }
    })
  } else {
    // 取消选中组内所有权限
    group.permissions.forEach(permission => {
      const index = selectedPermissionCodes.value.indexOf(permission.code)
      if (index > -1) {
        selectedPermissionCodes.value.splice(index, 1)
      }
    })
  }
}

// 快速操作方法
function selectAllPermissions() {
  selectedPermissionCodes.value = permissions.value.map(p => p.code)
}

function clearAllPermissions() {
  selectedPermissionCodes.value = []
}

function selectByTemplate(template) {
  const templates = {
    admin: [
      'questions:view', 'questions:create', 'questions:edit', 'questions:delete',
      'templates:view', 'templates:create', 'templates:edit', 'templates:delete',
      'basic_data:view', 'basic_data:edit',
      'admins:view', 'admins:create', 'admins:edit',
      'system:view'
    ],
    teacher: [
      'questions:view', 'templates:view', 'basic_data:view'
    ],
    viewer: [
      'questions:view', 'templates:view', 'basic_data:view'
    ]
  }

  selectedPermissionCodes.value = templates[template] || []
}

async function savePermissions() {
  try {
    savingPermissions.value = true

    // 根据选中的权限代码获取权限ID
    const permissionIds = permissions.value
      .filter(p => selectedPermissionCodes.value.includes(p.code))
      .map(p => p.id)

    await api.post('/roles/assign-permissions', {
      role_id: currentRole.value.id,
      permission_ids: permissionIds
    })

    ElMessage.success('权限分配成功')
    showPermissionDialog.value = false
    await loadRoles()
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存权限失败')
  } finally {
    savingPermissions.value = false
  }
}

function resetForm() {
  editingRole.value = null
  Object.assign(roleForm, {
    name: '',
    code: '',
    description: '',
    is_active: true
  })
  roleFormRef.value?.resetFields()
}

// 批量操作相关方法
function handleSelectionChange(selection) {
  selectedRoles.value = selection
}

function clearSelection() {
  selectedRoles.value = []
}

async function handleBatchOperation(operation) {
  if (selectedRoles.value.length === 0) {
    ElMessage.warning('请先选择要操作的角色')
    return
  }

  try {
    const roleIds = selectedRoles.value.map(role => role.id)

    switch (operation.key) {
      case 'assign_permissions':
        // 打开批量权限分配对话框
        showBatchPermissionDialog.value = true
        return
      case 'activate':
        await api.post('/roles/batch-activate', { role_ids: roleIds })
        ElMessage.success(`成功激活 ${roleIds.length} 个角色`)
        break
      case 'deactivate':
        await api.post('/roles/batch-deactivate', { role_ids: roleIds })
        ElMessage.success(`成功禁用 ${roleIds.length} 个角色`)
        break
      case 'delete':
        // 过滤掉系统角色
        const deletableIds = selectedRoles.value
          .filter(role => !role.is_system)
          .map(role => role.id)

        if (deletableIds.length === 0) {
          ElMessage.warning('选中的角色中没有可删除的角色')
          return
        }

        await api.post('/roles/batch-delete', { role_ids: deletableIds })
        ElMessage.success(`成功删除 ${deletableIds.length} 个角色`)
        break
    }

    clearSelection()
    await loadRoles()
  } catch (error) {
    console.error('批量操作失败:', error)
    ElMessage.error('批量操作失败')
  }
}

// 批量权限分配
async function handleBatchPermissionAssign() {
  if (selectedRoles.value.length === 0) {
    ElMessage.warning('请先选择要操作的角色')
    return
  }

  if (batchPermissionForm.permission_codes.length === 0) {
    ElMessage.warning('请选择要分配的权限')
    return
  }

  try {
    savingPermissions.value = true
    const roleIds = selectedRoles.value.map(role => role.id)

    await api.post('/roles/batch-assign-permissions', {
      role_ids: roleIds,
      permission_codes: batchPermissionForm.permission_codes
    })

    ElMessage.success(`成功为 ${roleIds.length} 个角色分配权限`)
    showBatchPermissionDialog.value = false
    batchPermissionForm.permission_codes = []
    clearSelection()
    await loadRoles()
  } catch (error) {
    console.error('批量权限分配失败:', error)
    ElMessage.error('批量权限分配失败')
  } finally {
    savingPermissions.value = false
  }
}

// 批量权限分配的辅助方法
function isGroupSelected(group) {
  if (group.permissions.length === 0) return false
  return group.permissions.every(p => batchPermissionForm.permission_codes.includes(p.code))
}

function isGroupIndeterminate(group) {
  if (group.permissions.length === 0) return false
  const selectedCount = group.permissions.filter(p => batchPermissionForm.permission_codes.includes(p.code)).length
  return selectedCount > 0 && selectedCount < group.permissions.length
}

function toggleGroup(group, selected) {
  if (selected) {
    // 选中组内所有权限
    group.permissions.forEach(permission => {
      if (!batchPermissionForm.permission_codes.includes(permission.code)) {
        batchPermissionForm.permission_codes.push(permission.code)
      }
    })
  } else {
    // 取消选中组内所有权限
    group.permissions.forEach(permission => {
      const index = batchPermissionForm.permission_codes.indexOf(permission.code)
      if (index > -1) {
        batchPermissionForm.permission_codes.splice(index, 1)
      }
    })
  }
}
</script>

<style scoped>
.role-management {
  padding: 20px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.permission-tree {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
}

/* 权限管理对话框样式 */
.permission-management {
  max-height: 70vh;
  overflow-y: auto;
}

.permission-stats {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.quick-actions {
  margin-bottom: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.action-group,
.template-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-label,
.template-label {
  color: #495057;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

.template-buttons {
  display: flex;
  gap: 8px;
}

.template-btn {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.template-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.template-admin {
  background: #409eff;
  color: #ffffff;
  border-color: #409eff;
}

.template-admin:hover {
  background: #337ecc;
  border-color: #337ecc;
  color: #ffffff;
}

.template-admin:focus {
  background: #337ecc;
  border-color: #337ecc;
  color: #ffffff;
}

.template-teacher {
  background: #67c23a;
  color: #ffffff;
  border-color: #67c23a;
}

.template-teacher:hover {
  background: #529b2e;
  border-color: #529b2e;
  color: #ffffff;
}

.template-teacher:focus {
  background: #529b2e;
  border-color: #529b2e;
  color: #ffffff;
}

.template-viewer {
  background: #e6a23c;
  color: #ffffff;
  border-color: #e6a23c;
}

.template-viewer:hover {
  background: #b88230;
  border-color: #b88230;
  color: #ffffff;
}

.template-viewer:focus {
  background: #b88230;
  border-color: #b88230;
  color: #ffffff;
}

.permission-groups {
  margin-bottom: 20px;
}

.permission-group-card {
  margin-bottom: 16px;
  border-radius: 8px;
  transition: all 0.3s;
}

.permission-group-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-icon {
  font-size: 24px;
}

.group-info h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.group-info p {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.permission-items {
  max-height: 200px;
  overflow-y: auto;
}

.permission-item {
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.permission-item:hover {
  background-color: #f5f7fa;
}

.permission-checkbox {
  width: 100%;
}

.permission-content {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.permission-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.permission-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

/* 自定义滚动条 */
.permission-management::-webkit-scrollbar,
.permission-items::-webkit-scrollbar {
  width: 6px;
}

.permission-management::-webkit-scrollbar-track,
.permission-items::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.permission-management::-webkit-scrollbar-thumb,
.permission-items::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.permission-management::-webkit-scrollbar-thumb:hover,
.permission-items::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 批量权限分配对话框样式 */
.batch-permission-content {
  max-height: 60vh;
  overflow-y: auto;
}

.selected-roles h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
}

.role-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-selection h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.batch-permission-content .permission-groups {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.batch-permission-content .permission-group {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.batch-permission-content .group-header {
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}

.batch-permission-content .group-permissions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.batch-permission-content .group-permissions .el-checkbox {
  margin-right: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .batch-permission-content .group-permissions {
    grid-template-columns: 1fr;
  }
}
</style>
