<template>
  <PageLayout
    title="系统管理"
    subtitle="系统设置、管理员管理和系统监控"
  >
    <!-- 系统概览 -->
    <div class="system-overview">
      <h2>📊 系统概览</h2>
      <div class="overview-grid">
        <StatCard
          icon="Database"
          :value="systemStats.database_size?.questions || 0"
          label="题目总数"
          icon-bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          :loading="statsLoading"
        />
        
        <StatCard
          icon="User"
          :value="systemStats.database_size?.admins || 0"
          label="管理员数量"
          icon-bg="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
          :loading="statsLoading"
        />
        
        <StatCard
          icon="Check"
          :value="`${systemStats.data_quality?.completion_rate || 0}%`"
          label="数据完整率"
          icon-bg="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
          :loading="statsLoading"
        />
        
        <StatCard
          icon="TrendCharts"
          :value="systemStats.performance_metrics?.recent_questions_7days || 0"
          label="近7天新增"
          icon-bg="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
          :loading="statsLoading"
        />
      </div>
    </div>

    <!-- 管理员管理 -->
    <div class="admin-management">
      <h2>👥 管理员管理</h2>
      <div class="admin-section">
        <div class="section-header">
          <el-button type="primary" @click="showAddAdminDialog = true" :icon="Plus">
            添加管理员
          </el-button>
          <el-button @click="loadAdmins" :icon="Refresh" :loading="adminLoading">
            刷新
          </el-button>
        </div>
        
        <el-table :data="admins" v-loading="adminLoading" class="modern-table">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="full_name" label="姓名" />
          <el-table-column prop="is_superuser" label="超级管理员" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_superuser ? 'danger' : 'info'">
                {{ row.is_superuser ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button size="small" @click="editAdmin(row)" :icon="Edit" />
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteAdmin(row)"
                :icon="Delete"
                :disabled="row.id === currentUser?.id"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 系统工具 -->
    <div class="system-tools">
      <h2>🔧 系统工具</h2>
      <div class="tools-grid">
        <div class="tool-card" @click="router.push('/system/backup')">
          <div class="tool-icon">
            <el-icon><Download /></el-icon>
          </div>
          <h3>备份管理</h3>
          <p>管理系统数据备份和恢复</p>
        </div>
        
        <div class="tool-card" @click="showChangePasswordDialog = true">
          <div class="tool-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <h3>修改密码</h3>
          <p>修改当前管理员密码</p>
        </div>
        
        <div class="tool-card" @click="checkSystemHealth">
          <div class="tool-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <h3>系统检查</h3>
          <p>检查系统健康状态</p>
        </div>
        
        <div class="tool-card" @click="viewSystemLogs">
          <div class="tool-icon">
            <el-icon><Document /></el-icon>
          </div>
          <h3>系统日志</h3>
          <p>查看系统操作日志</p>
        </div>
      </div>
    </div>

    <!-- 添加管理员对话框 -->
    <el-dialog
      v-model="showAddAdminDialog"
      title="添加管理员"
      width="500px"
      :before-close="closeAddAdminDialog"
    >
      <el-form :model="adminForm" :rules="adminRules" ref="adminFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="adminForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="adminForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="adminForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="adminForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="超级管理员">
          <el-switch v-model="adminForm.is_superuser" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeAddAdminDialog">取消</el-button>
        <el-button type="primary" @click="handleAddAdmin" :loading="adminSubmitting">
          确认添加
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑管理员对话框 -->
    <el-dialog
      v-model="showEditAdminDialog"
      title="编辑管理员"
      width="500px"
      :before-close="closeEditAdminDialog"
    >
      <el-form :model="editAdminForm" :rules="editAdminRules" ref="editAdminFormRef" label-width="100px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editAdminForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="editAdminForm.full_name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="账户状态">
          <el-switch
            v-model="editAdminForm.is_active"
            active-text="激活"
            inactive-text="禁用"
          />
        </el-form-item>

        <el-form-item label="超级管理员">
          <el-switch
            v-model="editAdminForm.is_superuser"
            :disabled="editingAdmin?.id === currentUser?.id"
          />
          <div v-if="editingAdmin?.id === currentUser?.id" class="form-tip">
            不能修改自己的超级管理员权限
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="closeEditAdminDialog">取消</el-button>
        <el-button type="primary" @click="handleEditAdmin" :loading="adminSubmitting">
          确认修改
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showChangePasswordDialog"
      title="修改密码"
      width="400px"
      :before-close="closeChangePasswordDialog"
    >
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="当前密码" prop="old_password">
          <el-input 
            v-model="passwordForm.old_password" 
            type="password" 
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="new_password">
          <el-input 
            v-model="passwordForm.new_password" 
            type="password" 
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input 
            v-model="passwordForm.confirm_password" 
            type="password" 
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeChangePasswordDialog">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="passwordSubmitting">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Refresh, Edit, Delete, Download, Lock, 
  Monitor, Document 
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'
import StatCard from '../components/StatCard.vue'

// Store
const authStore = useAuthStore()
const router = useRouter()
const currentUser = authStore.user

// 响应式数据
const statsLoading = ref(true)
const adminLoading = ref(false)
const adminSubmitting = ref(false)
const passwordSubmitting = ref(false)

const systemStats = ref({})
const admins = ref([])

const showAddAdminDialog = ref(false)
const showEditAdminDialog = ref(false)
const showChangePasswordDialog = ref(false)
const editingAdmin = ref(null)

// 表单数据
const adminForm = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  is_superuser: false
})

const editAdminForm = ref({
  email: '',
  full_name: '',
  is_active: true,
  is_superuser: false
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单引用
const adminFormRef = ref()
const editAdminFormRef = ref()
const passwordFormRef = ref()

// 表单验证规则
const adminRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ]
}

const editAdminRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadSystemStats(),
    loadAdmins()
  ])
})

// 方法
async function loadSystemStats() {
  try {
    statsLoading.value = true
    const response = await api.get('/system/stats')
    systemStats.value = response.data
  } catch (error) {
    console.error('加载系统统计失败:', error)
    ElMessage.error('加载系统统计失败')
  } finally {
    statsLoading.value = false
  }
}

async function loadAdmins() {
  try {
    adminLoading.value = true
    const response = await api.get('/system/admins')
    admins.value = response.data
  } catch (error) {
    console.error('加载管理员列表失败:', error)
    ElMessage.error('加载管理员列表失败')
  } finally {
    adminLoading.value = false
  }
}

async function handleAddAdmin() {
  try {
    await adminFormRef.value.validate()
    adminSubmitting.value = true
    
    await api.post('/system/admins', adminForm.value)
    
    ElMessage.success('管理员添加成功')
    closeAddAdminDialog()
    await loadAdmins()
  } catch (error) {
    console.error('添加管理员失败:', error)
    ElMessage.error('添加管理员失败')
  } finally {
    adminSubmitting.value = false
  }
}

async function editAdmin(admin) {
  editingAdmin.value = admin
  editAdminForm.value = {
    email: admin.email || '',
    full_name: admin.full_name || '',
    is_active: admin.is_active,
    is_superuser: admin.is_superuser
  }
  showEditAdminDialog.value = true
}

async function deleteAdmin(admin) {
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 "${admin.username}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
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

async function handleChangePassword() {
  try {
    await passwordFormRef.value.validate()
    passwordSubmitting.value = true
    
    await api.post('/system/change-password', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    
    ElMessage.success('密码修改成功')
    closeChangePasswordDialog()
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    passwordSubmitting.value = false
  }
}

async function createBackup() {
  try {
    await ElMessageBox.confirm(
      '确定要进行数据备份吗？备份过程可能需要几分钟时间。',
      '数据备份确认',
      {
        confirmButtonText: '开始备份',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const loading = ElMessage({
      message: '正在备份数据，请稍候...',
      type: 'info',
      duration: 0
    })

    try {
      // 模拟备份过程
      await new Promise(resolve => setTimeout(resolve, 3000))

      // 实际项目中应该调用备份API
      const response = await api.post('/system/backup')

      loading.close()
      ElMessage.success('数据备份完成！备份文件已保存到服务器。')
      console.log('备份信息:', response.data)
    } catch (error) {
      loading.close()
      throw error
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('创建备份失败:', error)
      ElMessage.error('创建备份失败')
    }
  }
}

async function checkSystemHealth() {
  try {
    const response = await api.get('/system/health')
    const health = response.data
    
    if (health.status === 'healthy') {
      ElMessage.success('系统运行正常')
    } else {
      ElMessage.warning('系统存在问题，请检查')
    }
    
    console.log('系统健康状态:', health)
  } catch (error) {
    console.error('系统检查失败:', error)
    ElMessage.error('系统检查失败')
  }
}

function viewSystemLogs() {
  router.push('/system/logs')
}

async function handleEditAdmin() {
  try {
    await editAdminFormRef.value.validate()
    adminSubmitting.value = true

    await api.put(`/system/admins/${editingAdmin.value.id}`, editAdminForm.value)

    ElMessage.success('管理员信息更新成功')
    closeEditAdminDialog()
    await loadAdmins()
  } catch (error) {
    console.error('更新管理员失败:', error)
    ElMessage.error('更新管理员失败')
  } finally {
    adminSubmitting.value = false
  }
}

function closeAddAdminDialog() {
  showAddAdminDialog.value = false
  adminForm.value = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    is_superuser: false
  }
  adminFormRef.value?.resetFields()
}

function closeEditAdminDialog() {
  showEditAdminDialog.value = false
  editingAdmin.value = null
  editAdminForm.value = {
    email: '',
    full_name: '',
    is_active: true,
    is_superuser: false
  }
  editAdminFormRef.value?.resetFields()
}

function closeChangePasswordDialog() {
  showChangePasswordDialog.value = false
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  passwordFormRef.value?.resetFields()
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.system-overview {
  margin-bottom: 48px;
}

.system-overview h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.admin-management {
  margin-bottom: 48px;
}

.admin-management h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.admin-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-header {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.modern-table {
  background: transparent;
}

.form-tip {
  font-size: 12px;
  color: #a0aec0;
  margin-top: 4px;
}

.system-tools h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.tool-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.tool-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.tool-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.tool-card p {
  color: #718096;
  font-size: 14px;
  margin: 0;
}

/* 深色模式支持 */
.dark .system-overview h2,
.dark .admin-management h2,
.dark .system-tools h2 {
  color: #e2e8f0;
}

.dark .admin-section,
.dark .tool-card {
  background: rgba(45, 55, 72, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .tool-card h3 {
  color: #e2e8f0;
}

.dark .tool-card p {
  color: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-grid,
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
  }
  
  .admin-section {
    padding: 16px;
  }
}
</style>
