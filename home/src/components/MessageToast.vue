<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 transform translate-y-2 scale-95"
      enter-to-class="opacity-100 transform translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 transform translate-y-0 scale-100"
      leave-to-class="opacity-0 transform translate-y-2 scale-95"
    >
      <div
        v-if="visible"
        :class="[
          'fixed top-4 left-1/2 transform -translate-x-1/2 z-[9999]',
          'w-[90%] max-w-sm sm:w-auto sm:max-w-md mx-4 sm:mx-0',
          'rounded-2xl shadow-2xl backdrop-blur-md border',
          typeClasses
        ]"
      >
        <div class="flex items-center p-4">
          <!-- 图标 -->
          <div class="flex-shrink-0 mr-3">
            <svg v-if="type === 'success'" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <svg v-else-if="type === 'error'" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <svg v-else-if="type === 'warning'" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          
          <!-- 消息内容 -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium">{{ message }}</p>
            <p v-if="description" class="text-xs opacity-80 mt-1">{{ description }}</p>
          </div>
          
          <!-- 关闭按钮 -->
          <button
            @click="close"
            class="flex-shrink-0 ml-3 p-1 rounded-full hover:bg-black/10 transition-colors duration-200"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        
        <!-- 进度条 -->
        <div v-if="showProgress" class="h-1 bg-black/10 rounded-b-2xl overflow-hidden">
          <div 
            class="h-full bg-current transition-all duration-100 ease-linear"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 3000
  },
  showProgress: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)
const progress = ref(100)
let timer = null
let progressTimer = null

const typeClasses = computed(() => {
  const classes = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  }
  return classes[props.type]
})

const show = () => {
  visible.value = true
  
  if (props.duration > 0) {
    // 设置自动关闭定时器
    timer = setTimeout(() => {
      close()
    }, props.duration)
    
    // 设置进度条动画
    if (props.showProgress) {
      const interval = 50
      const step = (interval / props.duration) * 100
      
      progressTimer = setInterval(() => {
        progress.value -= step
        if (progress.value <= 0) {
          progress.value = 0
          clearInterval(progressTimer)
        }
      }, interval)
    }
  }
}

const close = () => {
  visible.value = false
  clearTimeout(timer)
  clearInterval(progressTimer)
  
  // 延迟触发关闭事件，等待动画完成
  setTimeout(() => {
    emit('close')
  }, 200)
}

onMounted(() => {
  show()
})

onUnmounted(() => {
  clearTimeout(timer)
  clearInterval(progressTimer)
})
</script>
