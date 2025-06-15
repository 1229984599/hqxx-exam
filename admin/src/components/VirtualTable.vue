<template>
  <div class="virtual-table" ref="containerRef">
    <div class="table-header">
      <div class="table-row header-row">
        <div 
          v-for="column in columns" 
          :key="column.key"
          class="table-cell header-cell"
          :style="{ width: column.width || 'auto' }"
        >
          {{ column.title }}
        </div>
      </div>
    </div>
    
    <div 
      class="table-body" 
      ref="scrollRef"
      @scroll="handleScroll"
      :style="{ height: `${height}px` }"
    >
      <div 
        class="table-content"
        :style="{ 
          height: `${totalHeight}px`,
          paddingTop: `${offsetY}px`
        }"
      >
        <div 
          v-for="(item, index) in visibleData" 
          :key="getRowKey(item, startIndex + index)"
          class="table-row"
          :style="{ height: `${itemHeight}px` }"
        >
          <div 
            v-for="column in columns" 
            :key="column.key"
            class="table-cell"
            :style="{ width: column.width || 'auto' }"
          >
            <slot 
              :name="column.key" 
              :row="item" 
              :index="startIndex + index"
              :column="column"
            >
              {{ getColumnValue(item, column) }}
            </slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  },
  height: {
    type: Number,
    default: 400
  },
  itemHeight: {
    type: Number,
    default: 50
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  buffer: {
    type: Number,
    default: 5
  }
})

// 响应式数据
const containerRef = ref()
const scrollRef = ref()
const scrollTop = ref(0)

// 计算属性
const totalHeight = computed(() => props.data.length * props.itemHeight)

const visibleCount = computed(() => Math.ceil(props.height / props.itemHeight))

const startIndex = computed(() => {
  const index = Math.floor(scrollTop.value / props.itemHeight) - props.buffer
  return Math.max(0, index)
})

const endIndex = computed(() => {
  const index = startIndex.value + visibleCount.value + props.buffer * 2
  return Math.min(props.data.length, index)
})

const visibleData = computed(() => {
  return props.data.slice(startIndex.value, endIndex.value)
})

const offsetY = computed(() => startIndex.value * props.itemHeight)

// 方法
function handleScroll(event) {
  scrollTop.value = event.target.scrollTop
}

function getRowKey(item, index) {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item, index)
  }
  return item[props.rowKey] || index
}

function getColumnValue(item, column) {
  if (column.render) {
    return column.render(item)
  }

  const keys = (column.key || '').split('.')
  let value = item
  for (const key of keys) {
    value = value?.[key]
  }
  return value
}

function scrollTo(index) {
  if (scrollRef.value) {
    scrollRef.value.scrollTop = index * props.itemHeight
  }
}

function scrollToTop() {
  scrollTo(0)
}

function scrollToBottom() {
  scrollTo(props.data.length - 1)
}

// 暴露方法
defineExpose({
  scrollTo,
  scrollToTop,
  scrollToBottom
})

// 监听数据变化，重置滚动位置
watch(() => props.data.length, (newLength, oldLength) => {
  // 只有在数据长度显著变化时才重置滚动位置
  if (Math.abs(newLength - oldLength) > 10) {
    scrollTop.value = 0
    if (scrollRef.value) {
      scrollRef.value.scrollTop = 0
    }
  }
})

// 性能优化：使用 requestAnimationFrame 优化滚动处理
let rafId = null
const optimizedHandleScroll = (event) => {
  if (rafId) {
    cancelAnimationFrame(rafId)
  }

  rafId = requestAnimationFrame(() => {
    handleScroll(event)
  })
}

// 在组件挂载时使用优化的滚动处理
onMounted(() => {
  if (scrollRef.value) {
    scrollRef.value.addEventListener('scroll', optimizedHandleScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (rafId) {
    cancelAnimationFrame(rafId)
  }
  if (scrollRef.value) {
    scrollRef.value.removeEventListener('scroll', optimizedHandleScroll)
  }
})
</script>

<style scoped>
.virtual-table {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.table-header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.table-row {
  display: flex;
  border-bottom: 1px solid #ebeef5;
}

.table-row:last-child {
  border-bottom: none;
}

.header-row {
  font-weight: 600;
  color: #909399;
}

.table-cell {
  padding: 12px;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  word-break: break-word;
}

.header-cell {
  background-color: #f5f7fa;
}

.table-body {
  overflow-y: auto;
  position: relative;
}

.table-content {
  position: relative;
}

/* 滚动条样式 */
.table-body::-webkit-scrollbar {
  width: 8px;
}

.table-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 斑马纹效果 */
.table-row:nth-child(even) {
  background-color: #fafafa;
}

.table-row:hover {
  background-color: #f5f7fa;
}
</style>
