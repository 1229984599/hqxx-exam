<template>
  <div class="advanced-upload">
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :data="uploadData"
      :multiple="multiple"
      :accept="accept"
      :before-upload="beforeUpload"
      :on-progress="onProgress"
      :on-success="onSuccess"
      :on-error="onError"
      :on-remove="onRemove"
      :file-list="fileList"
      :auto-upload="autoUpload"
      :show-file-list="showFileList"
      drag
    >
      <div class="upload-area">
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          <p>将文件拖到此处，或<em>点击上传</em></p>
          <p class="upload-tip">
            支持 {{ acceptText }}，单个文件不超过 {{ maxSizeMB }}MB
          </p>
        </div>
      </div>
    </el-upload>

    <!-- 上传进度 -->
    <div v-if="uploadingFiles.length > 0" class="upload-progress">
      <h4>上传进度</h4>
      <div 
        v-for="file in uploadingFiles" 
        :key="file.uid"
        class="progress-item"
      >
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
        <el-progress 
          :percentage="file.percentage" 
          :status="file.status"
          :stroke-width="6"
        />
        <div class="progress-actions">
          <el-button 
            size="small" 
            type="danger" 
            @click="cancelUpload(file)"
            v-if="file.status === 'uploading'"
          >
            取消
          </el-button>
        </div>
      </div>
    </div>

    <!-- 压缩选项 -->
    <div v-if="enableCompression && isImageFile" class="compression-options">
      <el-checkbox v-model="compressImage">压缩图片</el-checkbox>
      <div v-if="compressImage" class="compression-settings">
        <el-slider
          v-model="compressionQuality"
          :min="0.1"
          :max="1"
          :step="0.1"
          show-tooltip
          :format-tooltip="(val) => `质量: ${Math.round(val * 100)}%`"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

// Props
const props = defineProps({
  action: {
    type: String,
    default: '/api/v1/upload'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  accept: {
    type: String,
    default: 'image/*'
  },
  maxSize: {
    type: Number,
    default: 10 * 1024 * 1024 // 10MB
  },
  autoUpload: {
    type: Boolean,
    default: true
  },
  showFileList: {
    type: Boolean,
    default: true
  },
  enableCompression: {
    type: Boolean,
    default: true
  },
  compressionQuality: {
    type: Number,
    default: 0.8
  }
})

// Emits
const emit = defineEmits(['success', 'error', 'progress', 'remove'])

// 响应式数据
const uploadRef = ref()
const fileList = ref([])
const uploadingFiles = ref([])
const compressImage = ref(true)
const compressionQuality = ref(props.compressionQuality)
const authStore = useAuthStore()

// 计算属性
const uploadUrl = computed(() => {
  return import.meta.env.VITE_API_BASE_URL + props.action
})

const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))

const uploadData = computed(() => ({
  compress: compressImage.value,
  quality: compressionQuality.value
}))

const maxSizeMB = computed(() => Math.round(props.maxSize / 1024 / 1024))

const acceptText = computed(() => {
  const types = (props.accept || '').split(',').map(type => type.trim())
  return types.join(', ')
})

const isImageFile = computed(() => {
  return (props.accept || '').includes('image')
})

// 方法
function beforeUpload(file) {
  // 检查文件大小
  if (file.size > props.maxSize) {
    ElMessage.error(`文件大小不能超过 ${maxSizeMB.value}MB`)
    return false
  }

  // 检查文件类型
  if (props.accept && props.accept !== '*') {
    const acceptTypes = props.accept.split(',').map(type => type.trim())
    const fileType = file.type
    const fileName = (file.name || '').toLowerCase()
    
    const isValidType = acceptTypes.some(type => {
      if (type.includes('*')) {
        const mainType = type.split('/')[0]
        return fileType.startsWith(mainType)
      }
      return fileType === type || fileName.endsWith(type.replace('.', ''))
    })

    if (!isValidType) {
      ElMessage.error(`只支持 ${acceptText.value} 格式的文件`)
      return false
    }
  }

  // 添加到上传列表
  const uploadFile = {
    uid: file.uid,
    name: file.name,
    size: file.size,
    status: 'uploading',
    percentage: 0,
    raw: file
  }
  uploadingFiles.value.push(uploadFile)

  return true
}

function onProgress(event, file) {
  const uploadFile = uploadingFiles.value.find(f => f.uid === file.uid)
  if (uploadFile) {
    uploadFile.percentage = Math.round(event.percent)
  }
  emit('progress', event, file)
}

function onSuccess(response, file) {
  const uploadFile = uploadingFiles.value.find(f => f.uid === file.uid)
  if (uploadFile) {
    uploadFile.status = 'success'
    uploadFile.percentage = 100
  }

  // 移除成功的文件
  setTimeout(() => {
    const index = uploadingFiles.value.findIndex(f => f.uid === file.uid)
    if (index > -1) {
      uploadingFiles.value.splice(index, 1)
    }
  }, 2000)

  ElMessage.success('文件上传成功')
  emit('success', response, file)
}

function onError(error, file) {
  const uploadFile = uploadingFiles.value.find(f => f.uid === file.uid)
  if (uploadFile) {
    uploadFile.status = 'exception'
  }

  ElMessage.error('文件上传失败')
  emit('error', error, file)
}

function onRemove(file) {
  const index = uploadingFiles.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    uploadingFiles.value.splice(index, 1)
  }
  emit('remove', file)
}

function cancelUpload(file) {
  uploadRef.value?.abort(file.raw)
  onRemove(file)
}

function formatFileSize(size) {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return Math.round(size / 1024) + ' KB'
  } else {
    return Math.round(size / 1024 / 1024 * 100) / 100 + ' MB'
  }
}

function clearFiles() {
  uploadingFiles.value = []
  fileList.value = []
  uploadRef.value?.clearFiles()
}

function submitUpload() {
  uploadRef.value?.submit()
}

// 暴露方法
defineExpose({
  clearFiles,
  submitUpload
})
</script>

<style scoped>
.advanced-upload {
  width: 100%;
}

.upload-area {
  padding: 40px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  background-color: #fafafa;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 8px 0;
  color: #606266;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.upload-progress h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.progress-item {
  margin-bottom: 16px;
  padding: 12px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.progress-item:last-child {
  margin-bottom: 0;
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.file-name {
  font-weight: 500;
  color: #303133;
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #909399;
  font-size: 12px;
}

.progress-actions {
  margin-top: 8px;
  text-align: right;
}

.compression-options {
  margin-top: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.compression-settings {
  margin-top: 12px;
  padding: 0 16px;
}
</style>
