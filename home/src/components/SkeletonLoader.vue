<template>
  <div class="animate-pulse">
    <!-- 选择框骨架屏 -->
    <div v-if="type === 'select'" class="space-y-3">
      <div class="h-4 bg-gray-200 rounded w-20"></div>
      <div class="h-14 bg-gray-200 rounded-2xl"></div>
    </div>

    <!-- 卡片骨架屏 -->
    <div v-else-if="type === 'card'" class="bg-white rounded-3xl p-8 shadow-medium">
      <div class="flex items-center mb-8">
        <div class="w-12 h-12 bg-gray-200 rounded-xl mr-4"></div>
        <div class="space-y-2">
          <div class="h-6 bg-gray-200 rounded w-32"></div>
          <div class="h-4 bg-gray-200 rounded w-48"></div>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="space-y-3">
          <div class="h-4 bg-gray-200 rounded w-16"></div>
          <div class="h-14 bg-gray-200 rounded-2xl"></div>
        </div>
      </div>
      <div class="flex justify-center mt-12">
        <div class="h-16 bg-gray-200 rounded-2xl w-48"></div>
      </div>
    </div>

    <!-- 题目骨架屏 -->
    <div v-else-if="type === 'question'" class="question-card p-8">
      <div class="space-y-4">
        <div class="h-6 bg-gray-200 rounded w-3/4"></div>
        <div class="h-4 bg-gray-200 rounded w-full"></div>
        <div class="h-4 bg-gray-200 rounded w-5/6"></div>
        <div class="h-4 bg-gray-200 rounded w-4/5"></div>
      </div>
      <div class="mt-8 space-y-4">
        <div class="h-32 bg-gray-200 rounded-xl"></div>
      </div>
      <div class="flex justify-center mt-8">
        <div class="h-12 bg-gray-200 rounded-xl w-32"></div>
      </div>
    </div>

    <!-- 列表骨架屏 -->
    <div v-else-if="type === 'list'" class="space-y-4">
      <div v-for="i in count" :key="i" class="flex items-center space-x-4 p-4 bg-white rounded-xl shadow-soft">
        <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <!-- 默认骨架屏 -->
    <div v-else class="space-y-4">
      <div class="h-4 bg-gray-200 rounded w-3/4"></div>
      <div class="h-4 bg-gray-200 rounded w-1/2"></div>
      <div class="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['select', 'card', 'question', 'list', 'default'].includes(value)
  },
  count: {
    type: Number,
    default: 3
  }
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

.animate-pulse > div {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
}
</style>
