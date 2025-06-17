<template>
  <el-dialog
      v-model="visible"
      title="👁️ 响应式预览"
      width="95%"
      :close-on-click-modal="true"
      :modal-append-to-body="true"
      class="preview-dialog"
      @close="handleClose"
  >
    <div class="preview-container">
      <!-- 设备选择器 -->
      <div class="device-selector">
        <div class="device-presets">
          <el-button
              v-for="preset in devicePresets"
              :key="preset.name"
              :type="previewWidth === preset.width && previewHeight === preset.height ? 'primary' : 'default'"
              size="small"
              @click="selectDevicePreset(preset)"
              class="device-btn"
          >
            <span class="device-icon">{{ preset.icon }}</span>
            <span class="device-name">{{ preset.name }}</span>
            <span v-if="preset.width > 0" class="device-size">{{ preset.width }}×{{ preset.height }}</span>
          </el-button>
        </div>

        <!-- 自定义尺寸控制 -->
        <div class="custom-size-controls">
          <div class="size-input-group">
            <label>宽度:</label>
            <el-input-number
                v-model="customWidth"
                :min="200"
                :max="2000"
                size="small"
                @change="updateCustomSize"
            />
            <span class="unit">px</span>
          </div>
          <div class="size-input-group">
            <label>高度:</label>
            <el-input-number
                v-model="customHeight"
                :min="200"
                :max="2000"
                size="small"
                @change="updateCustomSize"
            />
            <span class="unit">px</span>
          </div>
        </div>
      </div>

      <!-- 预览区域 -->
      <div class="preview-area">
        <div class="preview-frame-container">
          <div
              class="preview-frame"
              :style="{
              width: previewWidth + 'px',
              height: previewHeight + 'px'
            }"
          >
            <div class="preview-content" v-html="content"></div>
          </div>
          <div class="frame-info">
            {{ previewWidth }} × {{ previewHeight }}
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshPreview">刷新预览</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import {ref, computed, watch} from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  content: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 预览尺寸
const previewWidth = ref(375)
const previewHeight = ref(667)
const customWidth = ref(375)
const customHeight = ref(667)

// 预设设备尺寸
const devicePresets = [
  {name: 'iPhone SE', width: 375, height: 667, icon: '📱'},
  {name: 'iPhone 12', width: 390, height: 844, icon: '📱'},
  {name: 'iPhone 12 Pro Max', width: 428, height: 926, icon: '📱'},
  {name: 'iPad', width: 768, height: 1024, icon: '📱'},
  {name: 'iPad Pro', width: 1024, height: 1366, icon: '📱'},
  {name: 'Desktop', width: 1200, height: 800, icon: '💻'},
  {name: '自定义', width: 0, height: 0, icon: '⚙️'}
]

// 选择设备预设
function selectDevicePreset(preset) {
  if (preset.width > 0 && preset.height > 0) {
    previewWidth.value = preset.width
    previewHeight.value = preset.height
    customWidth.value = preset.width
    customHeight.value = preset.height
  }
}

// 更新自定义尺寸
function updateCustomSize() {
  previewWidth.value = customWidth.value
  previewHeight.value = customHeight.value
}

function handleClose() {
  visible.value = false
}

function refreshPreview() {
  emit('refresh')
}

// 监听自定义尺寸变化
watch([customWidth, customHeight], () => {
  updateCustomSize()
})
</script>

<style scoped>
.preview-dialog {
  --el-dialog-margin-top: 10px;
}

.preview-container {
  display: flex;
  flex-direction: column;
  height: 70vh;
  min-height: 500px;
}

.device-selector {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.device-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.device-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.device-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.device-icon {
  font-size: 16px;
}

.device-name {
  font-weight: 500;
}

.device-size {
  font-size: 12px;
  color: #666;
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.custom-size-controls {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.size-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.size-input-group label {
  font-weight: 500;
  color: #374151;
  min-width: 40px;
}

.unit {
  color: #666;
  font-size: 14px;
}

.preview-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 20px;
  background: #f0f0f0;
  border-radius: 8px;
  overflow: auto;
}

.preview-frame-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.preview-frame {
  background: white;
  border: 1px solid #ddd;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: auto;
  position: relative;
  transition: all 0.3s ease;
}

.preview-frame:hover {
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.2);
}

.preview-content {
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: #333;
}

.frame-info {
  background: #374151;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-container {
    height: 60vh;
  }

  .device-presets {
    justify-content: center;
  }

  .custom-size-controls {
    justify-content: center;
  }

  .preview-area {
    padding: 10px;
  }

  .preview-content {
    padding: 15px;
  }
}

/* 预览内容样式 */
.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 10px 0;
}

.preview-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  padding: 8px 12px;
  border: 1px solid #ddd;
  text-align: left;
}

.preview-content :deep(th) {
  background: #f5f5f5;
  font-weight: bold;
}

/* 拼音样式将在下面统一定义 */

/*拼音相关样式*/
ruby {
  ruby-align: center;
  display: inline-block;
  white-space: nowrap;
  margin: 0 2px;
  vertical-align: baseline;
  line-height: 2.2;
  position: relative;
}

ruby.pinyin-ruby {
  background: rgba(64, 158, 255, 0.05);
  border-radius: 4px;
  padding: 3px 2px 1px 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  margin: 0 1px;
  position: relative;
}

ruby.pinyin-ruby:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
}

ruby.pinyin-ruby:focus-within {
  background: rgba(64, 158, 255, 0.15);
  border-color: rgba(64, 158, 255, 0.5);
  outline: none;
}

rt {
  color: #409eff;
  font-weight: 500;
  display: block;
  text-align: center;
  line-height: 1.2;
  margin-bottom: 3px;
  user-select: none;
  min-width: 1em;
  padding: 0 1px;
  position: relative;
  z-index: 1;
  /* 如果没有设置具体字体大小，使用相对大小 */
  font-size: 0.75em;
}

/* 当rt有具体字体大小时，优先使用 */
rt[style*="font-size"] {
  font-size: inherit !important;
}

rb {
  border-bottom: 1px dotted #409eff;
  display: block;
  text-align: center;
  user-select: text;
  line-height: 1.4;
  position: relative;
  z-index: 1;
  /* 如果没有设置具体字体大小，使用默认大小 */
  font-size: 1em;
}

/* 当rb有具体字体大小时，优先使用 */
rb[style*="font-size"] {
  font-size: inherit !important;
}

/* 确保拼音注音在编辑器中正确显示 */
ruby:not(.pinyin-ruby) {
  background: transparent;
  padding: 0;
}
</style>
