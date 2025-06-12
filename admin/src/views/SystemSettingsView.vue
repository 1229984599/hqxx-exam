<template>
  <PageLayout
    title="系统设置"
    subtitle="配置系统各项参数和功能"
  >
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基础设置 -->
      <el-tab-pane label="基础设置" name="basic">
        <div class="settings-section">
          <h3>🏫 学校信息</h3>
          <el-form :model="basicSettings" label-width="120px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="学校名称">
                  <el-input v-model="basicSettings.schoolName" placeholder="请输入学校名称" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="学校代码">
                  <el-input v-model="basicSettings.schoolCode" placeholder="请输入学校代码" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="basicSettings.phone" placeholder="请输入联系电话" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="邮箱地址">
                  <el-input v-model="basicSettings.email" placeholder="请输入邮箱地址" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="学校地址">
              <el-input 
                v-model="basicSettings.address" 
                type="textarea" 
                :rows="3"
                placeholder="请输入学校地址"
              />
            </el-form-item>
            
            <el-form-item label="学校简介">
              <el-input 
                v-model="basicSettings.description" 
                type="textarea" 
                :rows="4"
                placeholder="请输入学校简介"
              />
            </el-form-item>
          </el-form>
        </div>

        <div class="settings-section">
          <h3>⚙️ 系统配置</h3>
          <el-form :model="basicSettings" label-width="120px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="系统名称">
                  <el-input v-model="basicSettings.systemName" placeholder="考试管理系统" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="系统版本">
                  <el-input v-model="basicSettings.version" placeholder="v1.0.0" readonly />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="时区设置">
                  <el-select v-model="basicSettings.timezone" placeholder="请选择时区">
                    <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                    <el-option label="东京时间 (UTC+9)" value="Asia/Tokyo" />
                    <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="语言设置">
                  <el-select v-model="basicSettings.language" placeholder="请选择语言">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="繁体中文" value="zh-TW" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="维护模式">
                  <el-switch 
                    v-model="basicSettings.maintenanceMode"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="调试模式">
                  <el-switch 
                    v-model="basicSettings.debugMode"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 安全设置 -->
      <el-tab-pane label="安全设置" name="security">
        <div class="settings-section">
          <h3>🔐 登录安全</h3>
          <el-form :model="securitySettings" label-width="150px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="密码最小长度">
                  <el-input-number 
                    v-model="securitySettings.minPasswordLength" 
                    :min="6" 
                    :max="20"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="登录失败锁定次数">
                  <el-input-number 
                    v-model="securitySettings.maxLoginAttempts" 
                    :min="3" 
                    :max="10"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="Token有效期(分钟)">
                  <el-input-number 
                    v-model="securitySettings.tokenExpireMinutes" 
                    :min="30" 
                    :max="1440"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="账户锁定时间(分钟)">
                  <el-input-number 
                    v-model="securitySettings.lockoutMinutes" 
                    :min="5" 
                    :max="60"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="强制复杂密码">
                  <el-switch 
                    v-model="securitySettings.requireComplexPassword"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="启用双因子认证">
                  <el-switch 
                    v-model="securitySettings.enableTwoFactor"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="settings-section">
          <h3>🛡️ 系统安全</h3>
          <el-form :model="securitySettings" label-width="150px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="IP白名单">
                  <el-switch 
                    v-model="securitySettings.enableIpWhitelist"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="API访问限制">
                  <el-switch 
                    v-model="securitySettings.enableApiRateLimit"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="允许的IP地址" v-if="securitySettings.enableIpWhitelist">
              <el-input 
                v-model="securitySettings.allowedIps" 
                type="textarea" 
                :rows="3"
                placeholder="请输入允许访问的IP地址，每行一个"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 文件设置 -->
      <el-tab-pane label="文件设置" name="file">
        <div class="settings-section">
          <h3>📁 文件上传</h3>
          <el-form :model="fileSettings" label-width="150px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="最大文件大小(MB)">
                  <el-input-number 
                    v-model="fileSettings.maxFileSize" 
                    :min="1" 
                    :max="100"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="允许的文件类型">
                  <el-select 
                    v-model="fileSettings.allowedTypes" 
                    multiple 
                    placeholder="请选择允许的文件类型"
                  >
                    <el-option label="图片 (jpg, png, gif)" value="image" />
                    <el-option label="文档 (pdf, doc, docx)" value="document" />
                    <el-option label="音频 (mp3, wav)" value="audio" />
                    <el-option label="视频 (mp4, avi)" value="video" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="存储方式">
              <el-radio-group v-model="fileSettings.storageType">
                <el-radio label="local">本地存储</el-radio>
                <el-radio label="oss">阿里云OSS</el-radio>
                <el-radio label="qiniu">七牛云</el-radio>
                <el-radio label="aws">AWS S3</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </div>

        <!-- CDN配置 -->
        <div class="settings-section" v-if="fileSettings.storageType !== 'local'">
          <h3>☁️ CDN配置</h3>
          <el-form :model="fileSettings.cdn" label-width="150px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="访问密钥">
                  <el-input 
                    v-model="fileSettings.cdn.accessKey" 
                    placeholder="请输入访问密钥"
                    show-password
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="私有密钥">
                  <el-input 
                    v-model="fileSettings.cdn.secretKey" 
                    placeholder="请输入私有密钥"
                    show-password
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="存储桶名称">
                  <el-input v-model="fileSettings.cdn.bucket" placeholder="请输入存储桶名称" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="访问域名">
                  <el-input v-model="fileSettings.cdn.domain" placeholder="https://cdn.example.com" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button @click="testCdnConnection" :loading="testingCdn">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 邮件设置 -->
      <el-tab-pane label="邮件设置" name="email">
        <div class="settings-section">
          <h3>📧 SMTP配置</h3>
          <el-form :model="emailSettings" label-width="120px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="SMTP服务器">
                  <el-input v-model="emailSettings.host" placeholder="smtp.example.com" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="端口">
                  <el-input-number v-model="emailSettings.port" :min="1" :max="65535" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="emailSettings.username" placeholder="请输入邮箱用户名" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="密码">
                  <el-input 
                    v-model="emailSettings.password" 
                    type="password" 
                    placeholder="请输入邮箱密码"
                    show-password
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="发件人名称">
                  <el-input v-model="emailSettings.fromName" placeholder="红旗小学考试系统" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="发件人邮箱">
                  <el-input v-model="emailSettings.fromEmail" placeholder="noreply@hqxx.edu.cn" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="启用SSL">
                  <el-switch 
                    v-model="emailSettings.ssl"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="启用TLS">
                  <el-switch 
                    v-model="emailSettings.tls"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button @click="testEmailConnection" :loading="testingEmail">
                测试邮件发送
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 保存按钮 -->
    <div class="settings-actions">
      <el-button type="primary" @click="saveAllSettings" :loading="saving" size="large">
        保存所有设置
      </el-button>
      <el-button @click="resetSettings" size="large">
        重置设置
      </el-button>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

// 响应式数据
const activeTab = ref('basic')
const saving = ref(false)
const testingCdn = ref(false)
const testingEmail = ref(false)

// 基础设置
const basicSettings = reactive({
  schoolName: '红旗小学',
  schoolCode: 'HQXX001',
  phone: '010-12345678',
  email: 'admin@hqxx.edu.cn',
  address: '北京市朝阳区红旗街123号',
  description: '红旗小学是一所具有悠久历史的优秀学校...',
  systemName: '红旗小学考试管理系统',
  version: 'v1.0.0',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN',
  maintenanceMode: false,
  debugMode: false
})

// 安全设置
const securitySettings = reactive({
  minPasswordLength: 6,
  maxLoginAttempts: 5,
  tokenExpireMinutes: 120,
  lockoutMinutes: 15,
  requireComplexPassword: true,
  enableTwoFactor: false,
  enableIpWhitelist: false,
  enableApiRateLimit: true,
  allowedIps: ''
})

// 文件设置
const fileSettings = reactive({
  maxFileSize: 10,
  allowedTypes: ['image', 'document'],
  storageType: 'local',
  cdn: {
    accessKey: '',
    secretKey: '',
    bucket: '',
    domain: ''
  }
})

// 邮件设置
const emailSettings = reactive({
  host: '',
  port: 587,
  username: '',
  password: '',
  fromName: '红旗小学考试系统',
  fromEmail: 'noreply@hqxx.edu.cn',
  ssl: false,
  tls: true
})

// 生命周期
onMounted(() => {
  loadSettings()
})

// 方法
async function loadSettings() {
  try {
    // 模拟加载设置
    // const response = await api.get('/system/settings')
    // Object.assign(basicSettings, response.data.basic)
    // Object.assign(securitySettings, response.data.security)
    // Object.assign(fileSettings, response.data.file)
    // Object.assign(emailSettings, response.data.email)
  } catch (error) {
    console.error('加载系统设置失败:', error)
  }
}

async function saveAllSettings() {
  try {
    saving.value = true
    
    const settings = {
      basic: basicSettings,
      security: securitySettings,
      file: fileSettings,
      email: emailSettings
    }
    
    // 模拟保存设置
    await new Promise(resolve => setTimeout(resolve, 2000))
    // await api.post('/system/settings', settings)
    
    ElMessage.success('系统设置保存成功')
  } catch (error) {
    console.error('保存系统设置失败:', error)
    ElMessage.error('保存系统设置失败')
  } finally {
    saving.value = false
  }
}

async function resetSettings() {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置为默认值吗？此操作不可逆。',
      '重置确认',
      {
        confirmButtonText: '确认重置',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await loadSettings()
    ElMessage.success('设置已重置为默认值')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置设置失败:', error)
      ElMessage.error('重置设置失败')
    }
  }
}

async function testCdnConnection() {
  try {
    testingCdn.value = true
    
    if (!fileSettings.cdn.accessKey || !fileSettings.cdn.secretKey) {
      ElMessage.warning('请填写完整的CDN配置信息')
      return
    }
    
    // 模拟测试CDN连接
    await new Promise(resolve => setTimeout(resolve, 2000))
    // await api.post('/system/test-cdn', fileSettings.cdn)
    
    ElMessage.success('CDN连接测试成功')
  } catch (error) {
    console.error('CDN连接测试失败:', error)
    ElMessage.error('CDN连接测试失败')
  } finally {
    testingCdn.value = false
  }
}

async function testEmailConnection() {
  try {
    testingEmail.value = true
    
    if (!emailSettings.host || !emailSettings.username) {
      ElMessage.warning('请填写完整的邮件配置信息')
      return
    }
    
    // 模拟测试邮件发送
    await new Promise(resolve => setTimeout(resolve, 3000))
    // await api.post('/system/test-email', emailSettings)
    
    ElMessage.success('测试邮件发送成功')
  } catch (error) {
    console.error('邮件发送测试失败:', error)
    ElMessage.error('邮件发送测试失败')
  } finally {
    testingEmail.value = false
  }
}
</script>

<style scoped>
.settings-tabs {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.settings-section {
  margin-bottom: 32px;
}

.settings-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.settings-form {
  background: rgba(248, 250, 252, 0.8);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.settings-actions {
  text-align: center;
  padding: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-top: 24px;
}

/* 深色模式适配 */
.dark .settings-tabs,
.dark .settings-actions {
  background: rgba(30, 30, 40, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .settings-section h3 {
  color: #e2e8f0;
}

.dark .settings-form {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-tabs {
    padding: 16px;
  }
  
  .settings-form {
    padding: 16px;
  }
}
</style>
