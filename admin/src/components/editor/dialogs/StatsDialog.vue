<template>
  <el-dialog
    v-model="visible"
    title="📊 内容统计"
    width="500px"
    :append-to-body="true"
    @close="handleClose"
  >
    <div class="stats-container">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats.characters }}</div>
          <div class="stat-label">总字符数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.charactersNoSpaces }}</div>
          <div class="stat-label">字符数（不含空格）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.chineseChars }}</div>
          <div class="stat-label">中文字符</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.words }}</div>
          <div class="stat-label">词语数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.paragraphs }}</div>
          <div class="stat-label">段落数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.sentences }}</div>
          <div class="stat-label">句子数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.pinyinAnnotations }}</div>
          <div class="stat-label">拼音注音</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.readingTime }} 分钟</div>
          <div class="stat-label">预计阅读时间</div>
        </div>
      </div>

      <div class="stats-tips">
        <h4>📝 统计说明</h4>
        <ul>
          <li>阅读时间基于中文300字/分钟，英文200词/分钟计算</li>
          <li>词语数包含中文字符和英文单词</li>
          <li>句子数基于句号、问号、感叹号统计</li>
          <li>拼音注音统计当前文档中的注音数量</li>
        </ul>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshStats">刷新统计</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  stats: {
    type: Object,
    default: () => ({
      characters: 0,
      charactersNoSpaces: 0,
      words: 0,
      paragraphs: 0,
      sentences: 0,
      readingTime: 0,
      chineseChars: 0,
      pinyinAnnotations: 0
    })
  }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

function handleClose() {
  visible.value = false
}

function refreshStats() {
  emit('refresh')
}
</script>

<style scoped>
.stats-container {
  padding: 10px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.stats-tips {
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 15px;
}

.stats-tips h4 {
  margin: 0 0 10px 0;
  color: #1e40af;
  font-size: 16px;
}

.stats-tips ul {
  margin: 0;
  padding-left: 20px;
}

.stats-tips li {
  margin-bottom: 5px;
  color: #374151;
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-item {
    padding: 12px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}
</style>
