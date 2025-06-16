<template>
  <header class="bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-large sticky top-0 z-50 backdrop-blur-sm">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo区域 -->
        <div class="flex items-center space-x-3">
          <router-link to="/" class="flex items-center space-x-3 hover:opacity-80 transition-opacity duration-200">
            <div class="relative">
              <img
                src="/logo.png"
                alt="红旗小学"
                class="w-10 h-10 rounded-full shadow-medium border-2 border-white/20"
                @error="handleLogoError"
              >
              <div class="absolute -top-1 -right-1 w-4 h-4 bg-accent rounded-full border-2 border-white animate-bounce-gentle"></div>
            </div>
            <div class="flex flex-col">
              <span class="text-xl font-bold tracking-tight">红旗小学</span>
              <span class="text-xs opacity-80 font-medium">无纸化测评系统</span>
            </div>
          </router-link>
        </div>

        <!-- 中间区域 - 显示当前配置 -->
        <div class="hidden lg:flex items-center">
          <div class="bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
            <div class="flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-sm font-medium" v-if="configStore.isConfigComplete">
                {{ configStore.configSummary }}
              </span>
              <span class="text-sm opacity-80" v-else>
                请完成学习配置
              </span>
            </div>
          </div>
        </div>

        <!-- 右侧设置按钮 -->
        <div class="flex items-center space-x-2">
          <button
            class="relative group p-3 rounded-full bg-white/10 hover:bg-white/20 transition-all duration-200 border border-white/20 hover:border-white/30"
            @click="openConfigDialog"
            title="学习设置"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <!-- 设置提示点 -->
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full border border-white opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useConfigStore } from '../stores/config'

const configStore = useConfigStore()

const openConfigDialog = () => {
  // 触发配置对话框打开事件
  window.dispatchEvent(new CustomEvent('open-config-dialog'))
}

const handleLogoError = (event) => {
  // 如果logo加载失败，隐藏图片
  event.target.style.display = 'none'
}
</script>

<style scoped>
/* 额外的动画效果 */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(16, 185, 129, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
  }
}

.animate-pulse-glow {
  animation: pulse-glow 2s infinite;
}
</style>
