<template>
  <div 
    class="lazy-image-container"
    :style="{ width, height }"
    ref="containerRef"
  >
    <transition name="fade">
      <img
        v-if="loaded"
        :src="currentSrc"
        :alt="alt"
        :class="['lazy-image', { error: hasError }]"
        @load="onLoad"
        @error="onError"
      />
    </transition>
    
    <div 
      v-if="!loaded || hasError" 
      class="placeholder"
      :style="{ width, height }"
    >
      <div v-if="loading" class="loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="hasError" class="error">
        <el-icon><Picture /></el-icon>
        <span>加载失败</span>
      </div>
      <div v-else class="waiting">
        <el-icon><Picture /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Loading, Picture } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: 'auto'
  },
  placeholder: {
    type: String,
    default: ''
  },
  errorImage: {
    type: String,
    default: ''
  },
  threshold: {
    type: Number,
    default: 0.1
  },
  rootMargin: {
    type: String,
    default: '50px'
  }
})

// 响应式数据
const containerRef = ref()
const loaded = ref(false)
const loading = ref(false)
const hasError = ref(false)
const currentSrc = ref('')
const observer = ref(null)

// 方法
function startLoading() {
  if (loading.value || loaded.value) return
  
  loading.value = true
  hasError.value = false
  currentSrc.value = props.src
}

function onLoad() {
  loading.value = false
  loaded.value = true
  hasError.value = false
}

function onError() {
  loading.value = false
  hasError.value = true
  
  if (props.errorImage) {
    currentSrc.value = props.errorImage
    loaded.value = true
  }
}

function createObserver() {
  if (!window.IntersectionObserver) {
    // 不支持 IntersectionObserver，直接加载
    startLoading()
    return
  }

  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          startLoading()
          observer.value?.unobserve(entry.target)
        }
      })
    },
    {
      threshold: props.threshold,
      rootMargin: props.rootMargin
    }
  )

  if (containerRef.value) {
    observer.value.observe(containerRef.value)
  }
}

function destroyObserver() {
  if (observer.value) {
    observer.value.disconnect()
    observer.value = null
  }
}

// 重新加载图片
function reload() {
  loaded.value = false
  loading.value = false
  hasError.value = false
  currentSrc.value = ''
  
  if (containerRef.value && observer.value) {
    observer.value.observe(containerRef.value)
  } else {
    startLoading()
  }
}

// 生命周期
onMounted(() => {
  createObserver()
})

onUnmounted(() => {
  destroyObserver()
})

// 监听 src 变化
watch(() => props.src, () => {
  if (props.src) {
    loaded.value = false
    loading.value = false
    hasError.value = false
    currentSrc.value = ''
    
    if (containerRef.value) {
      createObserver()
    }
  }
})

// 暴露方法
defineExpose({
  reload
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  overflow: hidden;
  display: inline-block;
}

.lazy-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.lazy-image.error {
  opacity: 0.5;
}

.placeholder {
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 14px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
}

.waiting {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
