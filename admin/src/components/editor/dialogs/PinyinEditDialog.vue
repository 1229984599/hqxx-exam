<template>
  <el-dialog
    v-model="visible"
    :title="`编辑 ${character} 的拼音`"
    width="400px"
    :append-to-body="true"
    class="pinyin-edit-dialog"
    @close="handleClose"
  >
    <div class="pinyin-edit-container">
      <!-- 字符显示 -->
      <div class="character-display">
        <span class="character">{{ character }}</span>
        <span class="current-pinyin">当前读音：{{ currentPinyin }}</span>
      </div>

      <!-- 拼音选项 -->
      <div class="pinyin-options">
        <h4>选择正确的读音：</h4>
        <div class="options-grid">
          <div
            v-for="(option, index) in pinyinOptions"
            :key="option"
            class="pinyin-option"
            :class="{ 
              'current': option === currentPinyin,
              'selected': option === selectedPinyin 
            }"
            @click="selectPinyin(option)"
          >
            <span class="option-number">{{ index + 1 }}</span>
            <span class="option-pinyin">{{ option }}</span>
            <span v-if="option === currentPinyin" class="current-badge">当前</span>
          </div>
        </div>
      </div>

      <!-- 自定义输入 -->
      <div class="custom-input">
        <h4>或者手动输入：</h4>
        <el-input
          v-model="customPinyin"
          placeholder="输入自定义拼音"
          @keyup.enter="confirmEdit"
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button @click="removePinyin" type="danger">删除拼音</el-button>
        <el-button @click="confirmEdit" type="primary">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  character: {
    type: String,
    default: ''
  },
  currentPinyin: {
    type: String,
    default: ''
  },
  pinyinOptions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'remove'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const selectedPinyin = ref('')
const customPinyin = ref('')

// 监听对话框打开，重置状态
watch(visible, (newVal) => {
  if (newVal) {
    selectedPinyin.value = props.currentPinyin
    customPinyin.value = ''
  }
})

function selectPinyin(pinyin) {
  selectedPinyin.value = pinyin
  customPinyin.value = ''
}

function confirmEdit() {
  const finalPinyin = customPinyin.value.trim() || selectedPinyin.value
  if (finalPinyin) {
    emit('confirm', finalPinyin)
    handleClose()
  }
}

function removePinyin() {
  emit('remove')
  handleClose()
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.pinyin-edit-container {
  padding: 10px 0;
}

.character-display {
  text-align: center;
  margin-bottom: 25px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px solid #e9ecef;
}

.character {
  font-size: 48px;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10px;
}

.current-pinyin {
  font-size: 16px;
  color: #409eff;
  font-weight: 500;
}

.pinyin-options h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 25px;
}

.pinyin-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 15px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  position: relative;
}

.pinyin-option:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.pinyin-option.selected {
  border-color: #409eff;
  background: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.pinyin-option.selected .option-number {
  background: white;
  color: #409eff;
}

.pinyin-option.selected .option-pinyin {
  color: white;
  font-weight: 600;
}

.pinyin-option.current {
  border-color: #67c23a;
  background: #f0f9ff;
}

.pinyin-option.current.selected {
  border-color: #409eff;
  background: #409eff;
  color: white;
}

.option-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.pinyin-option.current .option-number {
  background: #67c23a;
}

.option-pinyin {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  flex: 1;
}

.current-badge {
  background: #67c23a;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.custom-input {
  margin-top: 20px;
}

.custom-input h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer .el-button:first-child {
  margin-right: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .options-grid {
    grid-template-columns: 1fr;
  }
  
  .character {
    font-size: 36px;
  }
  
  .pinyin-option {
    padding: 10px 12px;
  }
}
</style>
