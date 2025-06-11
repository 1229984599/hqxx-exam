<template>
  <div class="token-status" v-if="showStatus">
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>🔐 Token状态</span>
          <el-button 
            type="text" 
            size="small" 
            @click="toggleExpanded"
            :icon="expanded ? ArrowUp : ArrowDown"
          />
        </div>
      </template>
      
      <div v-if="expanded" class="status-content">
        <div class="status-item">
          <span class="label">状态:</span>
          <el-tag :type="tokenInfo.valid ? 'success' : 'danger'" size="small">
            {{ tokenInfo.valid ? '有效' : '无效' }}
          </el-tag>
        </div>
        
        <div class="status-item" v-if="tokenInfo.valid">
          <span class="label">用户:</span>
          <span class="value">{{ tokenInfo.username }}</span>
        </div>
        
        <div class="status-item" v-if="tokenInfo.valid">
          <span class="label">过期时间:</span>
          <span class="value">{{ formatDate(tokenInfo.expiry) }}</span>
        </div>
        
        <div class="status-item" v-if="tokenInfo.valid">
          <span class="label">剩余时间:</span>
          <el-tag 
            :type="tokenInfo.isExpiringSoon ? 'warning' : 'success'" 
            size="small"
          >
            {{ tokenInfo.remainingTimeFormatted }}
          </el-tag>
        </div>
        
        <div class="status-actions" v-if="tokenInfo.valid">
          <el-button 
            size="small" 
            type="primary" 
            @click="handleRefreshToken"
            :loading="refreshing"
          >
            手动刷新
          </el-button>
          <el-button 
            size="small" 
            @click="updateStatus"
          >
            更新状态
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const authStore = useAuthStore()
const showStatus = ref(props.show)
const expanded = ref(false)
const refreshing = ref(false)
const tokenInfo = ref({
  valid: false,
  message: 'No token'
})

let updateInterval = null

onMounted(() => {
  updateStatus()
  // 每5秒更新一次状态
  updateInterval = setInterval(updateStatus, 5000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})

function updateStatus() {
  tokenInfo.value = authStore.getTokenInfo()
}

function toggleExpanded() {
  expanded.value = !expanded.value
}

async function handleRefreshToken() {
  try {
    refreshing.value = true
    await authStore.refreshToken()
    updateStatus()
    ElMessage.success('Token刷新成功')
  } catch (error) {
    ElMessage.error('Token刷新失败')
  } finally {
    refreshing.value = false
  }
}

function formatDate(date) {
  if (!date) return '未知'
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

// 监听props变化
watch(() => props.show, (newVal) => {
  showStatus.value = newVal
})
</script>

<style scoped>
.token-status {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  width: 300px;
}

.status-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.label {
  font-weight: 500;
  color: #606266;
}

.value {
  color: #303133;
}

.status-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
</style>
