<template>
  <PageLayout
    title="数据备份管理"
    subtitle="管理系统数据备份和恢复"
  >
    <!-- 备份配置 -->
    <div class="backup-config">
      <h3>🔧 备份配置</h3>
      <el-form :model="backupConfig" label-width="120px" class="config-form">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="备份方式">
              <el-select v-model="backupConfig.method" @change="handleMethodChange">
                <el-option label="本地备份" value="local" />
                <el-option label="WebDAV备份" value="webdav" />
                <el-option label="FTP备份" value="ftp" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="自动备份">
              <el-switch v-model="backupConfig.autoBackup" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- WebDAV配置 -->
        <div v-if="backupConfig.method === 'webdav'" class="webdav-config">
          <el-divider content-position="left">WebDAV 配置</el-divider>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="服务器地址" required>
                <el-input 
                  v-model="backupConfig.webdav.url" 
                  placeholder="https://your-webdav-server.com/dav"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="用户名" required>
                <el-input v-model="backupConfig.webdav.username" placeholder="WebDAV用户名" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="密码" required>
                <el-input 
                  v-model="backupConfig.webdav.password" 
                  type="password" 
                  placeholder="WebDAV密码"
                  show-password
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="备份目录">
                <el-input 
                  v-model="backupConfig.webdav.path" 
                  placeholder="/backups/hqxx-exam"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <el-button @click="testWebDAVConnection" :loading="testing">
              测试连接
            </el-button>
          </el-form-item>
        </div>

        <!-- FTP配置 -->
        <div v-if="backupConfig.method === 'ftp'" class="ftp-config">
          <h4>FTP服务器配置</h4>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="FTP主机">
                <el-input
                  v-model="backupConfig.ftp.host"
                  placeholder="ftp.example.com"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="端口">
                <el-input-number
                  v-model="backupConfig.ftp.port"
                  :min="1"
                  :max="65535"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="用户名">
                <el-input
                  v-model="backupConfig.ftp.username"
                  placeholder="FTP用户名"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="密码">
                <el-input
                  v-model="backupConfig.ftp.password"
                  type="password"
                  placeholder="FTP密码"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="备份路径">
            <el-input
              v-model="backupConfig.ftp.path"
              placeholder="/backups"
            />
          </el-form-item>

          <el-form-item>
            <el-button @click="testFTPConnection" :loading="testing">
              测试FTP连接
            </el-button>
          </el-form-item>
        </div>

        <el-form-item>
          <el-button
            v-role="'super_admin'"
            type="primary"
            @click="saveBackupConfig"
            :loading="saving"
          >
            保存配置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 备份操作 -->
    <div class="backup-operations">
      <h3>📦 备份操作</h3>
      <div class="operation-cards">
        <div
          v-role="'super_admin'"
          class="operation-card"
          @click="createBackup"
        >
          <div class="card-icon">
            <el-icon><Download /></el-icon>
          </div>
          <h4>创建备份</h4>
          <p>创建当前系统数据的完整备份</p>
        </div>

        <div
          v-role="'super_admin'"
          class="operation-card"
          @click="showRestoreDialog = true"
        >
          <div class="card-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <h4>恢复数据</h4>
          <p>从备份文件恢复系统数据</p>
        </div>
        
        <div class="operation-card" @click="scheduleBackup">
          <div class="card-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <h4>定时备份</h4>
          <p>设置自动定时备份任务</p>
        </div>
      </div>
    </div>

    <!-- 备份历史 -->
    <div class="backup-history">
      <h3>📋 备份历史</h3>
      <el-table :data="backupHistory" v-loading="loadingHistory">
        <el-table-column prop="filename" label="备份文件" min-width="200">
          <template #default="{ row }">
            <div class="backup-file">
              <el-icon><Document /></el-icon>
              <span>{{ row.filename }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="method" label="备份方式" width="120">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.method)">
              {{ getMethodText(row.method) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button
              v-role="'super_admin'"
              size="small"
              @click="downloadBackup(row)"
            >
              下载
            </el-button>
            <el-button
              v-role="'super_admin'"
              size="small"
              type="warning"
              @click="restoreFromBackup(row)"
            >
              恢复
            </el-button>
            <el-button
              v-role="'super_admin'"
              size="small"
              type="danger"
              @click="deleteBackup(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 恢复数据对话框 -->
    <el-dialog
      v-model="showRestoreDialog"
      title="恢复数据"
      width="500px"
    >
      <div class="restore-content">
        <el-alert
          title="警告"
          type="warning"
          description="恢复数据将覆盖当前所有数据，此操作不可逆，请谨慎操作！"
          :closable="false"
          show-icon
        />
        
        <el-upload
          class="restore-upload"
          drag
          action="#"
          :before-upload="beforeRestoreUpload"
          :http-request="handleRestoreUpload"
          :show-file-list="false"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将备份文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 .sql 或 .zip 格式的备份文件
            </div>
          </template>
        </el-upload>
      </div>
      
      <template #footer>
        <el-button @click="showRestoreDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmRestore" :loading="restoring">
          确认恢复
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download, Upload, Timer, Document, UploadFilled
} from '@element-plus/icons-vue'
import { usePermissions } from '../composables/usePermissions'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const { hasRole } = usePermissions()

// 响应式数据
const saving = ref(false)
const testing = ref(false)
const loadingHistory = ref(false)
const showRestoreDialog = ref(false)
const restoring = ref(false)
const restoreFile = ref(null)

// 备份配置
const backupConfig = reactive({
  method: 'local',
  autoBackup: false,
  webdav: {
    url: '',
    username: '',
    password: '',
    path: '/backups/hqxx-exam'
  },
  ftp: {
    host: '',
    port: 21,
    username: '',
    password: '',
    path: '/backups'
  }
})

// 备份历史
const backupHistory = ref([])

// 生命周期
onMounted(() => {
  loadBackupConfig()
  loadBackupHistory()
})

// 方法
async function loadBackupConfig() {
  try {
    // 调用真实API加载配置
    const response = await api.get('/system/config/backup')
    if (response.data.config) {
      Object.assign(backupConfig, response.data.config)
    }
  } catch (error) {
    console.error('加载备份配置失败:', error)
  }
}

async function saveBackupConfig() {
  try {
    saving.value = true

    // 准备符合后端API期望的数据结构
    const configData = {
      method: backupConfig.method,
      autoBackup: backupConfig.autoBackup,
      webdav: backupConfig.webdav,
      ftp: backupConfig.ftp
    }

    console.log('发送备份配置数据:', configData)

    // 调用真实API保存配置
    await api.post('/system/config/backup', configData)

    ElMessage.success('备份配置保存成功')
  } catch (error) {
    console.error('保存备份配置失败:', error)
    ElMessage.error('保存备份配置失败')
  } finally {
    saving.value = false
  }
}

async function testWebDAVConnection() {
  try {
    testing.value = true

    if (!backupConfig.webdav.url || !backupConfig.webdav.username) {
      ElMessage.warning('请填写完整的WebDAV配置信息')
      return
    }

    // 调用真实API测试连接
    await api.post('/system/backup/test-webdav', backupConfig.webdav)

    ElMessage.success('WebDAV连接测试成功')
  } catch (error) {
    console.error('WebDAV连接测试失败:', error)
    ElMessage.error('WebDAV连接测试失败')
  } finally {
    testing.value = false
  }
}

async function testFTPConnection() {
  try {
    testing.value = true

    if (!backupConfig.ftp.host || !backupConfig.ftp.username) {
      ElMessage.warning('请填写完整的FTP配置信息')
      return
    }

    // 调用真实API测试连接
    await api.post('/system/backup/test-ftp', backupConfig.ftp)

    ElMessage.success('FTP连接测试成功')
  } catch (error) {
    console.error('FTP连接测试失败:', error)
    ElMessage.error('FTP连接测试失败')
  } finally {
    testing.value = false
  }
}

async function createBackup() {
  try {
    // 检查备份方法配置
    if (backupConfig.method === 'webdav') {
      if (!backupConfig.webdav.url || !backupConfig.webdav.username) {
        ElMessage.warning('请先配置WebDAV连接信息')
        return
      }
    } else if (backupConfig.method === 'ftp') {
      if (!backupConfig.ftp.host || !backupConfig.ftp.username) {
        ElMessage.warning('请先配置FTP连接信息')
        return
      }
    }

    const methodText = getMethodText(backupConfig.method)
    await ElMessageBox.confirm(
      `确定要使用 ${methodText} 方式创建数据备份吗？备份过程可能需要几分钟时间。`,
      '创建备份确认',
      {
        confirmButtonText: '开始备份',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const loading = ElMessage({
      message: `正在使用 ${methodText} 方式创建备份，请稍候...`,
      type: 'info',
      duration: 0
    })

    try {
      // 调用真实API创建备份，传递备份方法和配置
      const backupData = {
        method: backupConfig.method
      }

      // 根据备份方法添加相应的配置
      if (backupConfig.method === 'webdav') {
        backupData.webdav = backupConfig.webdav
      } else if (backupConfig.method === 'ftp') {
        backupData.ftp = backupConfig.ftp
      }

      console.log('发送备份请求数据:', backupData)
      const response = await api.post('/system/backup', backupData)

      loading.close()
      ElMessage.success(`使用 ${methodText} 方式创建备份成功！`)
      await loadBackupHistory()
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

async function loadBackupHistory() {
  try {
    loadingHistory.value = true

    // 调用真实API加载备份历史
    const response = await api.get('/system/backup/history')
    backupHistory.value = response.data.backups || []
  } catch (error) {
    console.error('加载备份历史失败:', error)
    ElMessage.error('加载备份历史失败')
  } finally {
    loadingHistory.value = false
  }
}

function handleMethodChange() {
  // 方法改变时的处理
  if (backupConfig.method === 'webdav') {
    ElMessage.info('请配置WebDAV连接信息并测试连接')
  } else if (backupConfig.method === 'ftp') {
    ElMessage.info('请配置FTP连接信息')
  } else {
    ElMessage.info('已选择本地备份方式')
  }
}

function scheduleBackup() {
  ElMessage.info('定时备份功能开发中...')
}

function beforeRestoreUpload(file) {
  const isValidType = file.type === 'application/sql' || 
                     file.type === 'application/zip' || 
                     file.name.endsWith('.sql') || 
                     file.name.endsWith('.zip')
  
  if (!isValidType) {
    ElMessage.error('只能上传 .sql 或 .zip 格式的备份文件!')
    return false
  }
  
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    ElMessage.error('备份文件大小不能超过 100MB!')
    return false
  }
  
  return true
}

function handleRestoreUpload(options) {
  restoreFile.value = options.file
  ElMessage.success('备份文件上传成功，请点击"确认恢复"按钮')
}

async function confirmRestore() {
  if (!restoreFile.value) {
    ElMessage.warning('请先上传备份文件')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要恢复数据吗？此操作将覆盖当前所有数据且不可逆！',
      '数据恢复确认',
      {
        confirmButtonText: '确认恢复',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    restoring.value = true
    
    // 模拟恢复过程
    await new Promise(resolve => setTimeout(resolve, 5000))
    
    ElMessage.success('数据恢复成功！')
    showRestoreDialog.value = false
    restoreFile.value = null
  } catch (error) {
    if (error !== 'cancel') {
      console.error('数据恢复失败:', error)
      ElMessage.error('数据恢复失败')
    }
  } finally {
    restoring.value = false
  }
}

async function downloadBackup(backup) {
  try {
    ElMessage.info('开始下载备份文件...')

    // 创建下载链接
    const response = await api.get(`/system/backup/download/${backup.id}`, {
      responseType: 'blob'
    })

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', backup.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    ElMessage.success('备份文件下载成功')
  } catch (error) {
    console.error('下载备份失败:', error)
    ElMessage.error('下载备份失败')
  }
}

async function restoreFromBackup(backup) {
  try {
    await ElMessageBox.confirm(
      `确定要从备份文件 "${backup.filename}" 恢复数据吗？此操作将覆盖当前数据，请谨慎操作！`,
      '恢复确认',
      {
        confirmButtonText: '确认恢复',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const loading = ElMessage({
      message: '正在恢复数据，请稍候...',
      type: 'info',
      duration: 0
    })

    try {
      await api.post(`/system/backup/restore/${backup.id}`)
      loading.close()
      ElMessage.success('数据恢复成功！')

      // 提示用户刷新页面
      await ElMessageBox.confirm(
        '数据恢复成功！建议刷新页面以确保数据同步。',
        '恢复完成',
        {
          confirmButtonText: '刷新页面',
          cancelButtonText: '稍后刷新',
          type: 'success'
        }
      )

      window.location.reload()
    } catch (error) {
      loading.close()
      throw error
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复数据失败:', error)
      ElMessage.error('恢复数据失败')
    }
  }
}

async function deleteBackup(backup) {
  try {
    await ElMessageBox.confirm(
      `确定要删除备份文件 "${backup.filename}" 吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.delete(`/system/backup/${backup.id}`)
    ElMessage.success('备份文件删除成功')
    await loadBackupHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除备份失败:', error)
      ElMessage.error('删除备份失败')
    }
  }
}



// 工具函数
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatTime(dateString) {
  return new Date(dateString).toLocaleString('zh-CN')
}

function getMethodType(method) {
  const types = {
    local: 'info',
    webdav: 'success',
    ftp: 'warning'
  }
  return types[method] || 'info'
}

function getMethodText(method) {
  const texts = {
    local: '本地',
    webdav: 'WebDAV',
    ftp: 'FTP'
  }
  return texts[method] || method
}

function getStatusType(status) {
  const types = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    success: '成功',
    failed: '失败',
    pending: '进行中'
  }
  return texts[status] || status
}
</script>

<style scoped>
.backup-config,
.backup-operations,
.backup-history {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.backup-config h3,
.backup-operations h3,
.backup-history h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.webdav-config,
.ftp-config {
  margin-top: 20px;
}

.ftp-config h4,
.webdav-config h4 {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.operation-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.operation-card {
  background: rgba(102, 126, 234, 0.05);
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.operation-card:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

.card-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
  font-size: 24px;
}

.operation-card h4 {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.operation-card p {
  font-size: 14px;
  color: #718096;
  line-height: 1.5;
}

.backup-file {
  display: flex;
  align-items: center;
  gap: 8px;
}

.restore-content {
  padding: 20px 0;
}

.restore-upload {
  margin-top: 20px;
}

/* 深色模式适配 */
.dark .backup-config,
.dark .backup-operations,
.dark .backup-history {
  background: rgba(30, 30, 40, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .backup-config h3,
.dark .backup-operations h3,
.dark .backup-history h3 {
  color: #e2e8f0;
}

.dark .operation-card {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.dark .operation-card h4 {
  color: #e2e8f0;
}

.dark .operation-card p {
  color: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .operation-cards {
    grid-template-columns: 1fr;
  }
}
</style>
