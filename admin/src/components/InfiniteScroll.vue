<template>
  <div 
    ref="containerRef" 
    class="infinite-scroll-container"
    @scroll="handleScroll"
  >
    <!-- 顶部加载指示器 -->
    <div v-if="showTopLoader" class="loader top-loader">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 虚拟滚动内容 -->
    <div 
      class="virtual-content"
      :style="{ 
        height: totalHeight + 'px',
        paddingTop: offsetY + 'px'
      }"
    >
      <!-- 渲染可见项目 -->
      <div
        v-for="(item, index) in visibleItems"
        :key="getItemKey(item, startIndex + index)"
        class="scroll-item"
        :style="{ height: itemHeight + 'px' }"
      >
        <slot 
          :item="item" 
          :index="startIndex + index"
          :isVisible="true"
        >
          {{ item }}
        </slot>
      </div>
    </div>

    <!-- 底部加载指示器 -->
    <div v-if="showBottomLoader" class="loader bottom-loader">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>{{ loadingText }}</span>
    </div>

    <!-- 无更多数据提示 -->
    <div v-if="noMoreData && items.length > 0" class="no-more-data">
      <span>{{ noMoreText }}</span>
    </div>

    <!-- 空数据提示 -->
    <div v-if="items.length === 0 && !loading" class="empty-data">
      <slot name="empty">
        <div class="empty-content">
          <el-icon><DocumentDelete /></el-icon>
          <p>{{ emptyText }}</p>
        </div>
      </slot>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <el-alert
        :title="error"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <el-button size="small" @click="retry">重试</el-button>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElIcon, ElAlert, ElButton } from 'element-plus'
import { Loading, DocumentDelete } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  // 数据项数组
  items: {
    type: Array,
    default: () => []
  },
  // 每项高度
  itemHeight: {
    type: Number,
    default: 60
  },
  // 缓冲区大小（渲染额外的项目数）
  bufferSize: {
    type: Number,
    default: 5
  },
  // 是否正在加载
  loading: {
    type: Boolean,
    default: false
  },
  // 是否没有更多数据
  noMoreData: {
    type: Boolean,
    default: false
  },
  // 错误信息
  error: {
    type: String,
    default: ''
  },
  // 加载阈值（距离底部多少像素时触发加载）
  threshold: {
    type: Number,
    default: 100
  },
  // 是否启用下拉刷新
  pullRefresh: {
    type: Boolean,
    default: false
  },
  // 获取项目唯一键的函数
  itemKey: {
    type: [String, Function],
    default: 'id'
  },
  // 文本配置
  loadingText: {
    type: String,
    default: '加载更多...'
  },
  noMoreText: {
    type: String,
    default: '没有更多数据了'
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  }
})

// Emits
const emit = defineEmits(['load-more', 'refresh', 'retry'])

// 响应式数据
const containerRef = ref(null)
const scrollTop = ref(0)
const containerHeight = ref(0)
const showTopLoader = ref(false)
const showBottomLoader = ref(false)

// 计算属性
const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleCount = computed(() => {
  if (containerHeight.value === 0) return 10
  return Math.ceil(containerHeight.value / props.itemHeight) + props.bufferSize * 2
})

const startIndex = computed(() => {
  const index = Math.floor(scrollTop.value / props.itemHeight) - props.bufferSize
  return Math.max(0, index)
})

const endIndex = computed(() => {
  const index = startIndex.value + visibleCount.value
  return Math.min(props.items.length, index)
})

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value)
})

const offsetY = computed(() => {
  return startIndex.value * props.itemHeight
})

// 方法
function getItemKey(item, index) {
  if (typeof props.itemKey === 'function') {
    return props.itemKey(item, index)
  }
  return item[props.itemKey] || index
}

function handleScroll(event) {
  const container = event.target
  scrollTop.value = container.scrollTop
  
  // 检查是否需要加载更多
  const scrollBottom = container.scrollHeight - container.scrollTop - container.clientHeight
  
  if (scrollBottom <= props.threshold && !props.loading && !props.noMoreData) {
    showBottomLoader.value = true
    emit('load-more')
  }
  
  // 下拉刷新检查
  if (props.pullRefresh && container.scrollTop === 0 && !props.loading) {
    showTopLoader.value = true
    emit('refresh')
  }
}

function updateContainerHeight() {
  if (containerRef.value) {
    containerHeight.value = containerRef.value.clientHeight
  }
}

function retry() {
  emit('retry')
}

function scrollToTop() {
  if (containerRef.value) {
    containerRef.value.scrollTop = 0
  }
}

function scrollToBottom() {
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
}

function scrollToIndex(index) {
  if (containerRef.value) {
    const targetScrollTop = index * props.itemHeight
    containerRef.value.scrollTop = targetScrollTop
  }
}

// 监听器
watch(() => props.loading, (newLoading) => {
  if (!newLoading) {
    showTopLoader.value = false
    showBottomLoader.value = false
  }
})

watch(() => props.items.length, () => {
  nextTick(() => {
    updateContainerHeight()
  })
})

// 生命周期
onMounted(() => {
  updateContainerHeight()
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateContainerHeight)
  
  // 使用 ResizeObserver 监听容器大小变化
  if (window.ResizeObserver) {
    const resizeObserver = new ResizeObserver(() => {
      updateContainerHeight()
    })
    
    if (containerRef.value) {
      resizeObserver.observe(containerRef.value)
    }
    
    onUnmounted(() => {
      resizeObserver.disconnect()
    })
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerHeight)
})

// 暴露方法
defineExpose({
  scrollToTop,
  scrollToBottom,
  scrollToIndex,
  retry
})
</script>

<style scoped>
.infinite-scroll-container {
  height: 100%;
  overflow-y: auto;
  position: relative;
}

.virtual-content {
  position: relative;
}

.scroll-item {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.loader {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  color: #666;
  font-size: 14px;
  gap: 8px;
}

.top-loader {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  z-index: 10;
}

.bottom-loader {
  background: rgba(255, 255, 255, 0.9);
}

.no-more-data {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  color: #999;
  font-size: 14px;
  border-top: 1px solid #f0f0f0;
}

.empty-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
}

.empty-content {
  text-align: center;
}

.empty-content .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #ddd;
}

.empty-content p {
  margin: 0;
  font-size: 14px;
}

.error-message {
  padding: 16px;
}

/* 自定义滚动条 */
.infinite-scroll-container::-webkit-scrollbar {
  width: 6px;
}

.infinite-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.infinite-scroll-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.infinite-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 加载动画 */
.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
