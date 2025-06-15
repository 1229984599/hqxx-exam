<template>
  <div class="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50">
    <!-- 设置按钮 - 始终显示 -->
    <div class="flex flex-col gap-3 mb-3">
      <button
        class="floating-btn bg-gradient-to-br from-orange-500 to-red-600 shadow-large"
        @click="showSettings = !showSettings"
        title="按钮设置"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="floating-btn-icon transition-transform duration-300" :class="{ 'rotate-45': showSettings }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>
    </div>

    <!-- 设置面板 -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 transform translate-y-4 scale-95"
      enter-to-class="opacity-100 transform translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 transform translate-y-0 scale-100"
      leave-to-class="opacity-0 transform translate-y-4 scale-95"
    >
      <div
        v-if="showSettings"
        class="absolute bottom-16 right-0 w-64 bg-white rounded-2xl shadow-2xl border border-gray-200 p-4 backdrop-blur-md mb-3"
        style="background: rgba(255, 255, 255, 0.95);"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-gray-800">按钮设置</h3>
          <button
            @click="showSettings = false"
            class="p-1 rounded-full hover:bg-gray-100 transition-colors duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p class="text-xs text-blue-700">
            💡 开启或关闭右侧浮动按钮的显示
          </p>
        </div>

        <div class="space-y-3">
          <div
            v-for="button in availableButtons"
            :key="button.key"
            class="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
          >
            <div class="flex items-center space-x-3">
              <div class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs" :style="{ background: button.color }">
                <div v-html="button.icon"></div>
              </div>
              <span class="text-sm text-gray-700">{{ button.label }}</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="buttonSettings[button.key]"
                @change="saveSettings"
                class="sr-only peer"
              >
              <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-gray-200">
          <button
            @click="resetSettings"
            class="w-full text-xs text-gray-500 hover:text-gray-700 transition-colors duration-200"
          >
            恢复默认设置
          </button>
        </div>
      </div>
    </Transition>

    <!-- 功能按钮组 -->
    <div class="flex flex-col gap-3">
      <!-- 打印按钮 -->
      <button
        v-if="buttonSettings.print"
        class="floating-btn bg-gradient-to-br from-purple-500 to-indigo-600"
        @click="$emit('print')"
        title="打印题目 (P)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="floating-btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
        </svg>
      </button>

      <!-- 分享按钮 -->
      <button
        v-if="buttonSettings.share"
        class="floating-btn bg-gradient-to-br from-green-500 to-emerald-600"
        @click="$emit('share')"
        title="分享题目 (S)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="floating-btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
      </button>

      <!-- 收藏按钮 -->
      <button
        v-if="buttonSettings.favorite"
        class="floating-btn"
        :class="isFavorited ? 'bg-gradient-to-br from-red-500 to-pink-600' : 'bg-gradient-to-br from-gray-500 to-gray-600'"
        @click="$emit('toggleFavorite')"
        :title="isFavorited ? '取消收藏 (F)' : '收藏题目 (F)'"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="floating-btn-icon" :class="{ 'fill-current': isFavorited }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>

      <!-- 换一题按钮 -->
      <button
        v-if="buttonSettings.next"
        class="floating-btn-large bg-gradient-to-br from-primary-500 via-primary-600 to-purple-600"
        @click="$emit('nextQuestion')"
        :disabled="loading"
        title="换一题 (Enter)"
      >
        <!-- 按钮光效 -->
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-all duration-700"></div>
        
        <!-- 按钮内容 -->
        <span v-if="loading" class="animate-spin rounded-full  border-b-2 border-white"></span>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="floating-btn-icon-large group-hover:rotate-180 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>

      <!-- 回到顶部按钮 -->
      <button
        v-if="buttonSettings.scrollTop"
        class="floating-btn bg-gradient-to-br from-gray-500 to-gray-600"
        @click="$emit('scrollTop')"
        title="回到顶部"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="floating-btn-icon group-hover:-translate-y-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const props = defineProps({
  isFavorited: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['print', 'share', 'toggleFavorite', 'nextQuestion', 'scrollTop'])

const showSettings = ref(false)

// 可用按钮配置
const availableButtons = [
  {
    key: 'print',
    label: '打印',
    color: '#8b5cf6',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
    </svg>`
  },
  {
    key: 'share',
    label: '分享',
    color: '#10b981',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
    </svg>`
  },
  {
    key: 'favorite',
    label: '收藏',
    color: '#ef4444',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>`
  },
  {
    key: 'next',
    label: '换一题',
    color: '#3b82f6',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>`
  },
  {
    key: 'scrollTop',
    label: '回顶部',
    color: '#6b7280',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
    </svg>`
  }
]

// 按钮显示设置 - 确保换一题按钮默认显示
const buttonSettings = reactive({
  print: false,
  share: false,
  favorite: false,
  next: true,  // 换一题按钮默认显示
  scrollTop: false
})

// 保存设置到本地存储
const saveSettings = () => {
  localStorage.setItem('floatingButtonSettings', JSON.stringify(buttonSettings))
}

// 从本地存储加载设置
const loadSettings = () => {
  try {
    const stored = localStorage.getItem('floatingButtonSettings')
    if (stored) {
      const settings = JSON.parse(stored)
      Object.assign(buttonSettings, settings)
    }
  } catch (error) {
    console.error('加载按钮设置失败:', error)
  }
}

// 重置设置
const resetSettings = () => {
  buttonSettings.print = false
  buttonSettings.share = false
  buttonSettings.favorite = false
  buttonSettings.next = true  // 换一题按钮始终显示
  buttonSettings.scrollTop = false
  saveSettings()
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
/* 统一的浮动按钮样式 */
.floating-btn {
  width: 3rem;
  height: 3rem;
  border-radius: 9999px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  transform: scale(1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.floating-btn:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
  transform: scale(1.1);
}

.floating-btn:active {
  transform: scale(0.95);
}

.floating-btn-large {
  width: 3rem;
  height: 3rem;
  border-radius: 9999px;
  color: white;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
  transition: all 0.3s ease;
  transform: scale(1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.floating-btn-large:hover {
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35);
  transform: scale(1.1);
}

.floating-btn-large:active {
  transform: scale(0.95);
}

.floating-btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 0.3s ease;
}

.floating-btn:hover .floating-btn-icon {
  transform: scale(1.1);
}

.floating-btn-icon-large {
  width: 1.5rem;
  height: 1.5rem;
}

/* 设置按钮旋转动画 */
.floating-btn-icon.rotate-45 {
  transform: rotate(45deg);
}

/* 自定义滚动条 */
.space-y-3 {
  max-height: 200px;
  overflow-y: auto;
}

.space-y-3::-webkit-scrollbar {
  width: 4px;
}

.space-y-3::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.space-y-3::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.space-y-3::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
