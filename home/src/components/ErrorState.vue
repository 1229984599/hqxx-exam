<template>
  <div class="text-center py-12 px-6">
    <!-- 错误图标 -->
    <div class="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
      <svg v-if="type === 'network'" xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <svg v-else-if="type === 'empty'" xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>

    <!-- 错误标题 -->
    <h3 class="text-xl font-bold text-gray-800 mb-3">{{ title }}</h3>

    <!-- 错误描述 -->
    <p class="text-gray-600 mb-6 max-w-md mx-auto leading-relaxed">{{ description }}</p>

    <!-- 操作按钮 -->
    <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
      <button
        v-if="showRetry"
        @click="$emit('retry')"
        class="btn-primary-modern btn-modern-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        重试
      </button>

      <button
        v-if="showGoBack"
        @click="$emit('goBack')"
        class="btn-secondary-modern btn-modern-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回
      </button>
    </div>

    <!-- 额外提示 -->
    <div v-if="tips && tips.length > 0" class="mt-8 p-4 bg-blue-50 rounded-xl border border-blue-200">
      <h4 class="text-sm font-semibold text-blue-800 mb-2">💡 小提示</h4>
      <ul class="text-sm text-blue-700 space-y-1">
        <li v-for="tip in tips" :key="tip" class="flex items-start">
          <span class="text-blue-500 mr-2">•</span>
          <span>{{ tip }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'error',
    validator: (value) => ['error', 'network', 'empty'].includes(value)
  },
  title: {
    type: String,
    default: '出现了一些问题'
  },
  description: {
    type: String,
    default: '请稍后重试或联系管理员'
  },
  showRetry: {
    type: Boolean,
    default: true
  },
  showGoBack: {
    type: Boolean,
    default: false
  },
  tips: {
    type: Array,
    default: () => []
  }
})

defineEmits(['retry', 'goBack'])
</script>
