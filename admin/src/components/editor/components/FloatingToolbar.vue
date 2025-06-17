<template>
  <Teleport to="body">
    <div
      v-if="visible"
      ref="toolbarRef"
      class="floating-toolbar"
      :style="toolbarStyle"
      @mousedown.prevent
    >
      <!-- 工具栏箭头 -->
      <div class="toolbar-arrow"></div>
      
      <!-- 工具栏内容 -->
      <div class="toolbar-content">
        <!-- 字体样式 -->
        <div class="toolbar-group">
          <button
            class="toolbar-btn"
            :class="{ active: formats.bold }"
            @click="toggleFormat('bold')"
            title="粗体 (Ctrl+B)"
          >
            <strong>B</strong>
          </button>
          <button
            class="toolbar-btn"
            :class="{ active: formats.italic }"
            @click="toggleFormat('italic')"
            title="斜体 (Ctrl+I)"
          >
            <em>I</em>
          </button>
          <button
            class="toolbar-btn"
            :class="{ active: formats.underline }"
            @click="toggleFormat('underline')"
            title="下划线 (Ctrl+U)"
          >
            <u>U</u>
          </button>
        </div>

        <!-- 分隔线 -->
        <div class="toolbar-divider"></div>

        <!-- 字体大小 -->
        <div class="toolbar-group">
          <button
            class="toolbar-btn"
            @click="adjustFontSize(-2)"
            title="减小字体"
          >
            A-
          </button>
          <button
            class="toolbar-btn"
            @click="adjustFontSize(2)"
            title="增大字体"
          >
            A+
          </button>
        </div>

        <!-- 分隔线 -->
        <div class="toolbar-divider"></div>

        <!-- 颜色 -->
        <div class="toolbar-group">
          <div class="color-picker-wrapper">
            <button
              class="toolbar-btn color-btn"
              @click="showColorPicker = !showColorPicker"
              title="文字颜色"
            >
              <span class="color-icon">A</span>
              <span class="color-bar" :style="{ backgroundColor: currentTextColor }"></span>
            </button>
            <div v-if="showColorPicker" class="color-picker-panel">
              <div class="color-grid">
                <div
                  v-for="color in commonColors"
                  :key="color"
                  class="color-item"
                  :style="{ backgroundColor: color }"
                  @click="applyTextColor(color)"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="color-picker-wrapper">
            <button
              class="toolbar-btn color-btn"
              @click="showBgColorPicker = !showBgColorPicker"
              title="背景颜色"
            >
              <span class="bg-icon">🎨</span>
              <span class="color-bar" :style="{ backgroundColor: currentBgColor }"></span>
            </button>
            <div v-if="showBgColorPicker" class="color-picker-panel">
              <div class="color-grid">
                <div
                  v-for="color in commonColors"
                  :key="color"
                  class="color-item"
                  :style="{ backgroundColor: color }"
                  @click="applyBgColor(color)"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="toolbar-divider"></div>

        <!-- 特殊功能 -->
        <div class="toolbar-group">
          <button
            class="toolbar-btn"
            @click="addPinyin"
            title="添加拼音注音"
          >
            拼
          </button>
          <button
            class="toolbar-btn"
            :class="{ active: formatBrushActive }"
            @click="toggleFormatBrush"
            title="格式刷"
          >
            🖌️
          </button>
          <button
            class="toolbar-btn"
            @click="clearFormat"
            title="清除格式"
          >
            🧹
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selection: {
    type: Object,
    default: () => ({})
  },
  formats: {
    type: Object,
    default: () => ({})
  },
  formatBrushActive: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'toggleFormat',
  'adjustFontSize', 
  'applyTextColor',
  'applyBgColor',
  'addPinyin',
  'toggleFormatBrush',
  'clearFormat'
])

const toolbarRef = ref(null)
const showColorPicker = ref(false)
const showBgColorPicker = ref(false)

// 常用颜色
const commonColors = [
  '#000000', '#333333', '#666666', '#999999', '#CCCCCC', '#FFFFFF',
  '#FF0000', '#FF6600', '#FFCC00', '#00FF00', '#0066FF', '#6600FF',
  '#FF3366', '#FF9933', '#FFFF33', '#33FF33', '#3366FF', '#9933FF'
]

// 当前颜色
const currentTextColor = ref('#000000')
const currentBgColor = ref('transparent')

// 工具栏位置样式
const toolbarStyle = ref({
  position: 'absolute',
  top: '0px',
  left: '0px',
  zIndex: 10000
})

// 监听显示状态变化，计算位置
watch(() => props.visible, async (newVal) => {
  console.log('FloatingToolbar 显示状态变化:', newVal, props.selection)

  if (newVal && props.selection.range) {
    await nextTick()
    // 多次延迟确保DOM完全渲染
    setTimeout(() => {
      calculatePosition()
    }, 50)
  }

  // 隐藏时关闭颜色选择器
  if (!newVal) {
    showColorPicker.value = false
    showBgColorPicker.value = false
  }
})

// 监听selection变化，重新计算位置
watch(() => props.selection, async (newVal) => {
  if (props.visible && newVal && newVal.range) {
    await nextTick()
    setTimeout(() => {
      calculatePosition()
    }, 50)
  }
})

// 计算工具栏位置
function calculatePosition() {
  if (!props.selection.range || !toolbarRef.value) {
    console.log('计算位置失败: 缺少range或toolbarRef')
    return
  }

  // 确保工具栏已经渲染
  if (!toolbarRef.value.offsetWidth || !toolbarRef.value.offsetHeight) {
    console.log('工具栏尚未完全渲染，延迟计算')
    setTimeout(calculatePosition, 20)
    return
  }

  const range = props.selection.range
  const iframe = props.selection.iframe

  // 获取选中区域在iframe内的位置
  let rect
  try {
    rect = range.getBoundingClientRect()
  } catch (error) {
    console.error('获取选中区域位置失败:', error)
    return
  }

  // 获取iframe在页面中的位置
  let iframeRect = { top: 0, left: 0 }
  if (iframe) {
    iframeRect = iframe.getBoundingClientRect()
  }

  // 计算选中区域在页面中的绝对位置
  const absoluteRect = {
    top: rect.top + iframeRect.top,
    left: rect.left + iframeRect.left,
    bottom: rect.bottom + iframeRect.top,
    right: rect.right + iframeRect.left,
    width: rect.width,
    height: rect.height
  }

  const toolbarRect = toolbarRef.value.getBoundingClientRect()

  // 计算工具栏位置
  let top = absoluteRect.top - toolbarRect.height - 10
  let left = absoluteRect.left + (absoluteRect.width - toolbarRect.width) / 2

  // 边界检查
  const margin = 10
  if (left < margin) {
    left = margin
  } else if (left + toolbarRect.width > window.innerWidth - margin) {
    left = window.innerWidth - toolbarRect.width - margin
  }

  if (top < margin) {
    // 上方空间不够，显示在下方
    top = absoluteRect.bottom + 10
  }

  toolbarStyle.value = {
    position: 'fixed',
    top: `${Math.round(top)}px`,
    left: `${Math.round(left)}px`,
    zIndex: 10000
  }
}

// 格式化操作
function toggleFormat(format) {
  emit('toggleFormat', format)
}

function adjustFontSize(delta) {
  emit('adjustFontSize', delta)
}

function applyTextColor(color) {
  currentTextColor.value = color
  emit('applyTextColor', color)
  showColorPicker.value = false
}

function applyBgColor(color) {
  currentBgColor.value = color
  emit('applyBgColor', color)
  showBgColorPicker.value = false
}

function addPinyin() {
  emit('addPinyin')
}

function toggleFormatBrush() {
  emit('toggleFormatBrush')
}

function clearFormat() {
  emit('clearFormat')
}

// 点击外部关闭颜色选择器
function handleClickOutside(event) {
  if (!toolbarRef.value?.contains(event.target)) {
    showColorPicker.value = false
    showBgColorPicker.value = false
  }
}

// 监听点击事件
document.addEventListener('click', handleClickOutside)
</script>

<style scoped>
.floating-toolbar {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  user-select: none;
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.2s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.toolbar-arrow {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid white;
}

.toolbar-content {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.toolbar-btn:hover {
  background: #f0f0f0;
}

.toolbar-btn.active {
  background: #409eff;
  color: white;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #ddd;
  margin: 0 4px;
}

.color-picker-wrapper {
  position: relative;
}

.color-btn {
  flex-direction: column;
  padding: 4px;
}

.color-icon,
.bg-icon {
  font-size: 12px;
  line-height: 1;
}

.color-bar {
  width: 20px;
  height: 3px;
  margin-top: 2px;
  border-radius: 1px;
}

.color-picker-panel {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px;
  z-index: 10001;
  margin-top: 4px;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 4px;
  width: 120px;
}

.color-item {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  cursor: pointer;
  border: 1px solid #ddd;
  transition: transform 0.2s ease;
}

.color-item:hover {
  transform: scale(1.2);
}
</style>
