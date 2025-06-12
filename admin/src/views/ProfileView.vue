<template>
  <PageLayout
    title="个人资料"
    subtitle="管理您的个人信息和账户设置"
  >
    <div class="profile-container">
      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-section">
            <el-avatar :size="80" class="profile-avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <div class="avatar-actions">
              <el-button size="small" type="primary" @click="showAvatarDialog = true">
                更换头像
              </el-button>
            </div>
          </div>
          
          <div class="profile-info">
            <h2>{{ authStore.user?.username }}</h2>
            <p class="user-role">{{ authStore.user?.is_superuser ? '超级管理员' : '管理员' }}</p>
            <p class="join-date">加入时间：{{ formatDate(authStore.user?.created_at) }}</p>
          </div>
        </div>
      </div>

      <!-- 基本信息编辑 -->
      <div class="info-section">
        <h3>基本信息</h3>
        <el-form 
          :model="profileForm" 
          :rules="profileRules" 
          ref="profileFormRef" 
          label-width="100px"
          class="profile-form"
        >
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="用户名" prop="username">
                <el-input 
                  v-model="profileForm.username" 
                  placeholder="请输入用户名"
                  disabled
                />
                <div class="form-tip">用户名不可修改</div>
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email">
                <el-input 
                  v-model="profileForm.email" 
                  placeholder="请输入邮箱"
                  type="email"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="姓名" prop="full_name">
                <el-input 
                  v-model="profileForm.full_name" 
                  placeholder="请输入真实姓名"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="手机号" prop="phone">
                <el-input 
                  v-model="profileForm.phone" 
                  placeholder="请输入手机号"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <el-button type="primary" @click="updateProfile" :loading="updating">
              保存修改
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 密码修改 -->
      <div class="password-section">
        <h3>修改密码</h3>
        <el-form 
          :model="passwordForm" 
          :rules="passwordRules" 
          ref="passwordFormRef" 
          label-width="100px"
          class="password-form"
        >
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="当前密码" prop="old_password">
                <el-input 
                  v-model="passwordForm.old_password" 
                  type="password" 
                  placeholder="请输入当前密码"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="新密码" prop="new_password">
                <el-input 
                  v-model="passwordForm.new_password" 
                  type="password" 
                  placeholder="请输入新密码"
                  show-password
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="确认密码" prop="confirm_password">
                <el-input 
                  v-model="passwordForm.confirm_password" 
                  type="password" 
                  placeholder="请再次输入新密码"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <el-button type="danger" @click="changePassword" :loading="changingPassword">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 账户统计 -->
      <div class="stats-section">
        <h3>账户统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ userStats.created_questions || 0 }}</div>
              <div class="stat-label">创建题目</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ userStats.last_login_days || 0 }}</div>
              <div class="stat-label">天前登录</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ userStats.total_login_count || 0 }}</div>
              <div class="stat-label">登录次数</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="showAvatarDialog"
      title="更换头像"
      width="400px"
      :before-close="closeAvatarDialog"
    >
      <div class="avatar-upload">
        <el-upload
          class="avatar-uploader"
          action="#"
          :show-file-list="false"
          :before-upload="beforeAvatarUpload"
          :http-request="uploadAvatar"
        >
          <img v-if="avatarUrl" :src="avatarUrl" class="avatar-preview" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
        <div class="upload-tip">
          <p>支持 JPG、PNG 格式</p>
          <p>文件大小不超过 2MB</p>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="closeAvatarDialog">取消</el-button>
        <el-button type="primary" @click="saveAvatar" :loading="uploadingAvatar">
          保存
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Edit, Clock, Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const authStore = useAuthStore()

// 响应式数据
const updating = ref(false)
const changingPassword = ref(false)
const showAvatarDialog = ref(false)
const uploadingAvatar = ref(false)
const avatarUrl = ref('')

// 表单数据
const profileForm = reactive({
  username: '',
  email: '',
  full_name: '',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const userStats = reactive({
  created_questions: 0,
  last_login_days: 0,
  total_login_count: 0
})

// 表单引用
const profileFormRef = ref()
const passwordFormRef = ref()

// 表单验证规则
const profileRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
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
        if (value !== passwordForm.new_password) {
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
onMounted(() => {
  loadUserProfile()
  loadUserStats()
})

// 方法
function loadUserProfile() {
  const user = authStore.user
  if (user) {
    profileForm.username = user.username || ''
    profileForm.email = user.email || ''
    profileForm.full_name = user.full_name || ''
    profileForm.phone = user.phone || ''
  }
}

async function loadUserStats() {
  try {
    // 这里可以调用API获取用户统计数据
    // const response = await api.get('/auth/profile/stats')
    // userStats = response.data
    
    // 模拟数据
    userStats.created_questions = 15
    userStats.last_login_days = 1
    userStats.total_login_count = 42
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

async function updateProfile() {
  try {
    await profileFormRef.value.validate()
    updating.value = true
    
    const updateData = {
      email: profileForm.email,
      full_name: profileForm.full_name,
      phone: profileForm.phone
    }
    
    await api.put('/auth/profile', updateData)
    
    // 更新本地用户信息
    authStore.updateUser(updateData)
    
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新个人信息失败')
  } finally {
    updating.value = false
  }
}

async function changePassword() {
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    await api.post('/system/change-password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    
    ElMessage.success('密码修改成功')
    
    // 清空表单
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    passwordFormRef.value.resetFields()
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    changingPassword.value = false
  }
}

function resetForm() {
  loadUserProfile()
  profileFormRef.value.clearValidate()
}

function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

async function uploadAvatar(options) {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('folder', 'avatars')

  try {
    const response = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // 根据实际API响应结构调整
    avatarUrl.value = response.data.url || response.data.data?.url || URL.createObjectURL(options.file)
    ElMessage.success('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    // 如果上传失败，使用本地预览
    avatarUrl.value = URL.createObjectURL(options.file)
    ElMessage.warning('头像上传失败，使用本地预览')
  }
}

async function saveAvatar() {
  if (!avatarUrl.value) {
    ElMessage.warning('请先上传头像')
    return
  }
  
  try {
    uploadingAvatar.value = true
    
    await api.put('/auth/profile', {
      avatar: avatarUrl.value
    })
    
    authStore.updateUser({ avatar: avatarUrl.value })
    
    ElMessage.success('头像更新成功')
    closeAvatarDialog()
  } catch (error) {
    console.error('保存头像失败:', error)
    ElMessage.error('保存头像失败')
  } finally {
    uploadingAvatar.value = false
  }
}

function closeAvatarDialog() {
  showAvatarDialog.value = false
  avatarUrl.value = ''
}

function formatDate(dateString) {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-section {
  text-align: center;
}

.profile-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 32px;
  margin-bottom: 12px;
}

.avatar-actions {
  margin-top: 12px;
}

.profile-info h2 {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.user-role {
  color: #667eea;
  font-weight: 600;
  margin-bottom: 4px;
}

.join-date {
  color: #718096;
  font-size: 14px;
}

.info-section,
.password-section,
.stats-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.info-section h3,
.password-section h3,
.stats-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-tip {
  font-size: 12px;
  color: #a0aec0;
  margin-top: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
}

.stat-label {
  font-size: 14px;
  color: #718096;
}

.avatar-upload {
  text-align: center;
}

.avatar-uploader {
  display: inline-block;
}

.avatar-uploader :deep(.el-upload) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploader :deep(.el-upload:hover) {
  border-color: #667eea;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
}

.upload-tip {
  margin-top: 16px;
  color: #8c939d;
  font-size: 12px;
}

.upload-tip p {
  margin: 4px 0;
}

/* 深色模式适配 */
.dark .profile-card,
.dark .info-section,
.dark .password-section,
.dark .stats-section {
  background: rgba(30, 30, 40, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .profile-info h2,
.dark .info-section h3,
.dark .password-section h3,
.dark .stats-section h3 {
  color: #e2e8f0;
}

.dark .stat-value {
  color: #e2e8f0;
}

.dark .stat-item {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
