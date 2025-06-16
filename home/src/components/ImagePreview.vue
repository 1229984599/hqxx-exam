<template>
  <!-- 图片预览遮罩层 -->
  <div 
    v-if="visible" 
    class="image-preview-overlay"
    @click="handleOverlayClick"
    @wheel.prevent="handleWheel"
  >
    <!-- 预览容器 -->
    <div class="image-preview-container" ref="containerRef">
      <!-- 图片 -->
      <img
        :src="imageSrc"
        :alt="imageAlt"
        class="preview-image"
        :style="imageStyle"
        @load="handleImageLoad"
        @error="handleImageError"
        @click.stop
        @mousedown="handleMouseDown"
        @dragstart.prevent
      />
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p class="loading-text">图片加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-if="error" class="error-overlay">
        <div class="error-icon">⚠️</div>
        <p class="error-text">图片加载失败</p>
      </div>
    </div>
    
    <!-- 工具栏 -->
    <div class="toolbar">
      <!-- 缩放控制 -->
      <div class="toolbar-group">
        <button 
          class="toolbar-btn" 
          @click="zoomOut"
          :disabled="scale <= minScale"
          title="缩小 (Ctrl + -)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13H5v-2h14v2z"/>
          </svg>
        </button>
        
        <span class="scale-text">{{ Math.round(scale * 100) }}%</span>
        
        <button 
          class="toolbar-btn" 
          @click="zoomIn"
          :disabled="scale >= maxScale"
          title="放大 (Ctrl + +)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
        </button>
      </div>
      
      <!-- 旋转控制 -->
      <div class="toolbar-group">
        <button 
          class="toolbar-btn" 
          @click="rotateLeft"
          title="逆时针旋转 (Ctrl + ←)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M7.11 8.53L5.7 7.11C4.8 8.27 4.24 9.61 4.07 11h2.02c.14-.87.49-1.72 1.02-2.47zM6.09 13H4.07c.17 1.39.72 2.73 1.62 3.89l1.41-1.42c-.52-.75-.87-1.59-1.01-2.47zm1.01 5.32c1.16.9 2.51 1.44 3.9 1.61V17.9c-.87-.15-1.71-.49-2.46-1.03L7.1 18.32zM13 4.07V1L8.45 5.55 13 10V6.09c2.84.48 5 2.94 5 5.91s-2.16 5.43-5 5.91v2.02c3.95-.49 7-3.85 7-7.93s-3.05-7.44-7-7.93z"/>
          </svg>
        </button>
        
        <button 
          class="toolbar-btn" 
          @click="rotateRight"
          title="顺时针旋转 (Ctrl + →)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.55 5.55L11 1v3.07C7.06 4.56 4 7.92 4 12s3.05 7.44 7 7.93v-2.02c-2.84-.48-5-2.94-5-5.91s2.16-5.43 5-5.91V10l4.55-4.45zM19.93 11c-.17-1.39-.72-2.73-1.62-3.89l-1.42 1.42c.54.75.88 1.6 1.02 2.47h2.02zM13 17.9v2.02c1.39-.17 2.74-.71 3.9-1.61l-1.44-1.44c-.75.54-1.59.89-2.46 1.03zm3.89-2.42l1.42 1.41c.9-1.16 1.45-2.5 1.62-3.89h-2.02c-.14.87-.48 1.72-1.02 2.48z"/>
          </svg>
        </button>
      </div>
      
      <!-- 其他控制 -->
      <div class="toolbar-group">
        <button 
          class="toolbar-btn" 
          @click="resetTransform"
          title="重置 (Ctrl + 0)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
          </svg>
        </button>
        
        <button 
          class="toolbar-btn" 
          @click="toggleFullscreen"
          title="全屏 (F)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
        </button>
        
        <button 
          class="toolbar-btn close-btn" 
          @click="close"
          title="关闭 (ESC)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 图片信息 -->
    <div v-if="showInfo" class="image-info">
      <p><strong>尺寸:</strong> {{ imageWidth }} × {{ imageHeight }}</p>
      <p><strong>缩放:</strong> {{ Math.round(scale * 100) }}%</p>
      <p><strong>旋转:</strong> {{ rotation }}°</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  imageSrc: {
    type: String,
    required: true
  },
  imageAlt: {
    type: String,
    default: ''
  },
  showInfo: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['close', 'load', 'error'])

// 响应式数据
const containerRef = ref(null)
const loading = ref(true)
const error = ref(false)
const scale = ref(1)
const rotation = ref(0)
const translateX = ref(0)
const translateY = ref(0)
const imageWidth = ref(0)
const imageHeight = ref(0)

// 拖拽相关
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartTranslateX = ref(0)
const dragStartTranslateY = ref(0)

// 配置常量
const minScale = 0.1
const maxScale = 5
const scaleStep = 0.2
const rotationStep = 90

// 计算样式
const imageStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value}) rotate(${rotation.value}deg)`,
  transformOrigin: 'center center',
  transition: isDragging.value ? 'none' : 'transform 0.3s ease'
}))

// 图片加载完成
const handleImageLoad = (event) => {
  loading.value = false
  error.value = false
  imageWidth.value = event.target.naturalWidth
  imageHeight.value = event.target.naturalHeight
  emit('load', event)
}

// 图片加载错误
const handleImageError = (event) => {
  loading.value = false
  error.value = true
  emit('error', event)
}

// 缩放功能
const zoomIn = () => {
  if (scale.value < maxScale) {
    scale.value = Math.min(scale.value + scaleStep, maxScale)
  }
}

const zoomOut = () => {
  if (scale.value > minScale) {
    scale.value = Math.max(scale.value - scaleStep, minScale)
  }
}

// 旋转功能
const rotateLeft = () => {
  rotation.value = (rotation.value - rotationStep) % 360
}

const rotateRight = () => {
  rotation.value = (rotation.value + rotationStep) % 360
}

// 重置变换
const resetTransform = () => {
  scale.value = 1
  rotation.value = 0
  translateX.value = 0
  translateY.value = 0
}

// 鼠标滚轮缩放
const handleWheel = (event) => {
  const delta = event.deltaY > 0 ? -scaleStep : scaleStep
  const newScale = Math.max(minScale, Math.min(maxScale, scale.value + delta))
  scale.value = newScale
}

// 鼠标拖拽
const handleMouseDown = (event) => {
  if (event.button !== 0) return // 只处理左键
  
  isDragging.value = true
  dragStartX.value = event.clientX
  dragStartY.value = event.clientY
  dragStartTranslateX.value = translateX.value
  dragStartTranslateY.value = translateY.value
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event) => {
  if (!isDragging.value) return
  
  const deltaX = event.clientX - dragStartX.value
  const deltaY = event.clientY - dragStartY.value
  
  translateX.value = dragStartTranslateX.value + deltaX
  translateY.value = dragStartTranslateY.value + deltaY
}

const handleMouseUp = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

// 点击遮罩层关闭
const handleOverlayClick = (event) => {
  if (event.target === event.currentTarget) {
    close()
  }
}

// 全屏切换
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    containerRef.value?.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

// 关闭预览
const close = () => {
  emit('close')
}

// 键盘事件处理
const handleKeydown = (event) => {
  if (!props.visible) return
  
  switch (event.key) {
    case 'Escape':
      close()
      break
    case 'f':
    case 'F':
      toggleFullscreen()
      break
    case '0':
      if (event.ctrlKey) {
        event.preventDefault()
        resetTransform()
      }
      break
    case '=':
    case '+':
      if (event.ctrlKey) {
        event.preventDefault()
        zoomIn()
      }
      break
    case '-':
      if (event.ctrlKey) {
        event.preventDefault()
        zoomOut()
      }
      break
    case 'ArrowLeft':
      if (event.ctrlKey) {
        event.preventDefault()
        rotateLeft()
      }
      break
    case 'ArrowRight':
      if (event.ctrlKey) {
        event.preventDefault()
        rotateRight()
      }
      break
  }
}

// 监听visible变化，重置状态
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    loading.value = true
    error.value = false
    resetTransform()
  }
})

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.image-preview-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  cursor: grab;
  user-select: none;
  pointer-events: auto;
}

.preview-image:active {
  cursor: grabbing;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text,
.error-text {
  font-size: 16px;
  margin: 0;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.toolbar {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  gap: 16px;
  align-items: center;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.toolbar-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn.close-btn {
  background: rgba(239, 68, 68, 0.8);
}

.toolbar-btn.close-btn:hover {
  background: rgba(239, 68, 68, 1);
}

.toolbar-btn svg {
  width: 20px;
  height: 20px;
}

.scale-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
  min-width: 50px;
  text-align: center;
}

.image-info {
  position: fixed;
  top: 40px;
  right: 40px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 16px;
  border-radius: 8px;
  font-size: 14px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.image-info p {
  margin: 4px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    bottom: 20px;
    padding: 8px 12px;
    gap: 12px;
  }
  
  .toolbar-btn {
    width: 36px;
    height: 36px;
  }
  
  .toolbar-btn svg {
    width: 18px;
    height: 18px;
  }
  
  .image-info {
    top: 20px;
    right: 20px;
    padding: 12px;
    font-size: 12px;
  }
  
  .preview-image {
    max-width: 95vw;
    max-height: 95vh;
  }
}
</style>
