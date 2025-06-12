<template>
  <PageLayout
    title="系统日志"
    subtitle="查看系统运行日志和操作记录"
  >
    <!-- 日志筛选 -->
    <div class="log-filters">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="filters.level" placeholder="日志级别" clearable @change="loadLogs">
            <el-option label="全部" value="" />
            <el-option label="信息" value="info" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
            <el-option label="调试" value="debug" />
          </el-select>
        </el-col>
        
        <el-col :span="6">
          <el-select v-model="filters.module" placeholder="模块" clearable @change="loadLogs">
            <el-option label="全部" value="" />
            <el-option label="认证" value="auth" />
            <el-option label="试题" value="questions" />
            <el-option label="系统" value="system" />
            <el-option label="上传" value="upload" />
          </el-select>
        </el-col>
        
        <el-col :span="8">
          <el-date-picker
            v-model="filters.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="loadLogs"
          />
        </el-col>
        
        <el-col :span="4">
          <el-button type="primary" @click="loadLogs" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 日志列表 -->
    <div class="logs-container">
      <div class="logs-header">
        <div class="logs-stats">
          <el-tag type="info">总计: {{ totalLogs }}</el-tag>
          <el-tag type="success">信息: {{ logStats.info || 0 }}</el-tag>
          <el-tag type="warning">警告: {{ logStats.warning || 0 }}</el-tag>
          <el-tag type="danger">错误: {{ logStats.error || 0 }}</el-tag>
        </div>
        
        <div class="logs-actions">
          <el-button size="small" @click="exportLogs">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
          <el-button size="small" @click="clearLogs" type="danger">
            <el-icon><Delete /></el-icon>
            清空日志
          </el-button>
        </div>
      </div>

      <div class="logs-list" v-loading="loading">
        <div 
          v-for="log in logs" 
          :key="log.id"
          class="log-item"
          :class="getLogClass(log.level)"
        >
          <div class="log-header">
            <div class="log-level">
              <el-tag :type="getLevelType(log.level)" size="small">
                {{ getLevelText(log.level) }}
              </el-tag>
            </div>
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-module">{{ log.module }}</div>
          </div>
          
          <div class="log-content">
            <div class="log-message">{{ log.message }}</div>
            <div v-if="log.details" class="log-details">
              <el-collapse>
                <el-collapse-item title="详细信息">
                  <pre>{{ formatDetails(log.details) }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
          
          <div v-if="log.user" class="log-user">
            操作用户: {{ log.user }}
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && logs.length === 0" 
          description="暂无日志记录"
          :image-size="120"
        />
      </div>

      <!-- 分页 -->
      <div class="pagination-section" v-if="totalLogs > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[20, 50, 100, 200]"
          :total="totalLogs"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadLogs"
          @current-change="loadLogs"
        />
      </div>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Download, Delete } from '@element-plus/icons-vue'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

// 响应式数据
const loading = ref(false)
const logs = ref([])
const totalLogs = ref(0)
const logStats = ref({})

// 筛选条件
const filters = reactive({
  level: '',
  module: '',
  dateRange: null
})

// 分页
const pagination = reactive({
  page: 1,
  size: 50
})

// 生命周期
onMounted(() => {
  loadLogs()
})

// 方法
async function loadLogs() {
  try {
    loading.value = true
    
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (filters.level) params.level = filters.level
    if (filters.module) params.module = filters.module
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = filters.dateRange[0]
      params.end_time = filters.dateRange[1]
    }
    
    // 模拟API调用 - 实际项目中应该调用真实API
    const response = await mockGetLogs(params)
    
    logs.value = response.data.logs
    totalLogs.value = response.data.total
    logStats.value = response.data.stats
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

// 模拟日志API - 实际项目中应该替换为真实API
async function mockGetLogs(params) {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 模拟日志数据
  const mockLogs = [
    {
      id: 1,
      level: 'info',
      module: 'auth',
      message: '用户登录成功',
      details: { ip: '192.168.1.100', user_agent: 'Mozilla/5.0...' },
      user: 'admin',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString()
    },
    {
      id: 2,
      level: 'warning',
      module: 'questions',
      message: '试题批量操作执行时间较长',
      details: { duration: '5.2s', count: 150 },
      user: 'admin',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString()
    },
    {
      id: 3,
      level: 'error',
      module: 'upload',
      message: '图片上传失败',
      details: { error: 'CDN连接超时', file: 'image.jpg' },
      user: 'admin',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString()
    },
    {
      id: 4,
      level: 'info',
      module: 'system',
      message: '系统备份完成',
      details: { size: '15.6MB', duration: '2.1s' },
      user: 'system',
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString()
    }
  ]
  
  return {
    data: {
      logs: mockLogs,
      total: mockLogs.length,
      stats: {
        info: 2,
        warning: 1,
        error: 1,
        debug: 0
      }
    }
  }
}

function getLogClass(level) {
  return `log-${level}`
}

function getLevelType(level) {
  const types = {
    info: 'info',
    warning: 'warning',
    error: 'danger',
    debug: 'success'
  }
  return types[level] || 'info'
}

function getLevelText(level) {
  const texts = {
    info: '信息',
    warning: '警告',
    error: '错误',
    debug: '调试'
  }
  return texts[level] || level
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function formatDetails(details) {
  if (typeof details === 'string') return details
  return JSON.stringify(details, null, 2)
}

async function exportLogs() {
  try {
    ElMessage.info('导出功能开发中...')
    // 实际项目中应该调用导出API
    // const response = await api.get('/system/logs/export', { responseType: 'blob' })
    // 下载文件逻辑
  } catch (error) {
    console.error('导出日志失败:', error)
    ElMessage.error('导出日志失败')
  }
}

async function clearLogs() {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '清空确认',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('清空功能开发中...')
    // 实际项目中应该调用清空API
    // await api.delete('/system/logs')
    // await loadLogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空日志失败:', error)
      ElMessage.error('清空日志失败')
    }
  }
}
</script>

<style scoped>
.log-filters {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.logs-container {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.logs-stats {
  display: flex;
  gap: 12px;
}

.logs-actions {
  display: flex;
  gap: 8px;
}

.logs-list {
  max-height: 600px;
  overflow-y: auto;
}

.log-item {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.log-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

.log-item:last-child {
  border-bottom: none;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.log-time {
  color: #718096;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.log-module {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.log-content {
  margin-bottom: 8px;
}

.log-message {
  color: #2d3748;
  font-size: 14px;
  line-height: 1.5;
}

.log-details {
  margin-top: 8px;
}

.log-details pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #4a5568;
  overflow-x: auto;
  margin: 0;
}

.log-user {
  color: #718096;
  font-size: 12px;
}

/* 日志级别样式 */
.log-info {
  border-left: 3px solid #3182ce;
}

.log-warning {
  border-left: 3px solid #d69e2e;
}

.log-error {
  border-left: 3px solid #e53e3e;
  background: rgba(229, 62, 62, 0.02);
}

.log-debug {
  border-left: 3px solid #38a169;
}

.pagination-section {
  padding: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
}

/* 深色模式适配 */
.dark .log-filters,
.dark .logs-container {
  background: rgba(30, 30, 40, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .logs-header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.dark .log-item {
  border-bottom-color: rgba(255, 255, 255, 0.05);
}

.dark .log-item:hover {
  background: rgba(255, 255, 255, 0.02);
}

.dark .log-message {
  color: #e2e8f0;
}

.dark .log-details pre {
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e0;
}

.dark .pagination-section {
  border-top-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .logs-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .logs-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .logs-actions {
    justify-content: center;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
