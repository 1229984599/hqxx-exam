<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <img src="/logo.png" alt="红旗小学" class="logo" />
        <h1 class="title">红旗小学考试系统</h1>
        <p class="subtitle">管理后台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>默认账号: admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    await authStore.login(loginForm)

    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录错误:', error)

    // 处理不同类型的错误
    if (error.response?.data?.detail) {
      // 后端返回的具体错误信息
      ElMessage.error(error.response.data.detail)
    } else if (error.response?.status === 400) {
      ElMessage.error('请求参数错误，请检查输入信息')
    } else if (error.response?.status === 401) {
      ElMessage.error('认证失败，请检查用户名和密码')
    } else if (error.response?.status === 403) {
      ElMessage.error('账户被禁用，请联系管理员')
    } else if (error.response?.status === 500) {
      ElMessage.error('服务器内部错误，请稍后重试')
    } else if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      ElMessage.error('网络连接失败，请检查网络连接')
    } else if (error.code === 'ECONNREFUSED') {
      ElMessage.error('无法连接到服务器，请联系管理员')
    } else {
      ElMessage.error('登录失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #666;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 25px;
}

.login-footer {
  text-align: center;
  color: #999;
  font-size: 14px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .logo {
    width: 60px;
    height: 60px;
  }
}
</style>
