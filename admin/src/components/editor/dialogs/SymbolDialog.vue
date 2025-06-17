<template>
  <el-dialog
    v-model="visible"
    title="🔣 插入符号"
    width="800px"
    :append-to-body="true"
    class="symbol-dialog"
    @close="handleClose"
  >
    <div class="symbol-container">
      <!-- 搜索和筛选 -->
      <div class="symbol-filters">
        <div class="filter-row">
          <el-input
            v-model="searchText"
            placeholder="搜索符号或名称..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            clearable
            class="category-select"
          >
            <el-option label="全部分类" value="all" />
            <el-option
              v-for="group in symbolGroups"
              :key="group.id"
              :label="group.title"
              :value="group.id"
            >
              <span class="category-option">
                <span class="category-icon">{{ group.icon }}</span>
                <span class="category-name">{{ group.title }}</span>
              </span>
            </el-option>
          </el-select>
        </div>
      </div>

      <!-- 符号网格 -->
      <div class="symbol-groups">
        <div
          v-for="group in filteredSymbols"
          :key="group.id"
          class="symbol-group"
        >
          <div class="group-header">
            <span class="group-icon">{{ group.icon }}</span>
            <span class="group-title">{{ group.title }}</span>
            <span class="group-count">({{ group.symbols.length }})</span>
          </div>
          <div class="symbol-grid">
            <div
              v-for="item in group.symbols"
              :key="item.symbol"
              class="symbol-item"
              @click="insertSymbol(item.symbol)"
              :title="item.name"
            >
              <span class="symbol-char">{{ item.symbol }}</span>
              <span class="symbol-name">{{ item.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredSymbols.length === 0"
        description="未找到符合条件的符号"
        :image-size="100"
      />
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'insert'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const searchText = ref('')
const selectedCategory = ref('all')

// 符号数据
const symbolGroups = [
  {
    id: 'emoji',
    title: '常用表情',
    icon: '😀',
    symbols: [
      { symbol: '😀', name: '开心' },
      { symbol: '😁', name: '露齿笑' },
      { symbol: '😂', name: '笑哭' },
      { symbol: '😃', name: '大笑' },
      { symbol: '😄', name: '眯眼笑' },
      { symbol: '😅', name: '苦笑' },
      { symbol: '😆', name: '咧嘴笑' },
      { symbol: '😇', name: '天使' },
      { symbol: '😉', name: '眨眼' },
      { symbol: '😊', name: '微笑' },
      { symbol: '😋', name: '美味' },
      { symbol: '😌', name: '满足' },
      { symbol: '😍', name: '花痴' },
      { symbol: '😘', name: '飞吻' },
      { symbol: '😎', name: '酷' },
      { symbol: '😏', name: '得意' },
      { symbol: '😐', name: '面无表情' },
      { symbol: '😒', name: '无聊' },
      { symbol: '🙄', name: '翻白眼' },
      { symbol: '🤔', name: '思考' },
      { symbol: '😳', name: '脸红' },
      { symbol: '😞', name: '失望' },
      { symbol: '😟', name: '担心' },
      { symbol: '😠', name: '生气' },
      { symbol: '😡', name: '愤怒' },
      { symbol: '😢', name: '哭泣' },
      { symbol: '😭', name: '大哭' },
      { symbol: '😷', name: '口罩' },
      { symbol: '😴', name: '睡觉' },
      { symbol: '👍', name: '点赞' },
      { symbol: '👎', name: '点踩' },
      { symbol: '👏', name: '鼓掌' },
      { symbol: '👋', name: '挥手' },
      { symbol: '👌', name: 'OK' },
      { symbol: '✋', name: '停止' },
      { symbol: '💪', name: '肌肉' },
      { symbol: '🙏', name: '祈祷' },
      { symbol: '❤️', name: '红心' },
      { symbol: '💛', name: '黄心' },
      { symbol: '💚', name: '绿心' },
      { symbol: '💙', name: '蓝心' },
      { symbol: '💜', name: '紫心' },
      { symbol: '💔', name: '心碎' },
      { symbol: '💯', name: '满分' },
      { symbol: '✨', name: '闪亮' },
      { symbol: '⭐', name: '星星' },
      { symbol: '🔥', name: '火' },
      { symbol: '🎉', name: '庆祝' },
      { symbol: '🚀', name: '火箭' },
      { symbol: '📚', name: '书本' },
      { symbol: '📖', name: '打开的书' },
      { symbol: '📝', name: '记录' },
      { symbol: '💡', name: '灯泡' },
      { symbol: '🎓', name: '学士帽' },
      { symbol: '🍎', name: '苹果' },
      { symbol: '🏆', name: '奖杯' }
    ]
  },
  {
    id: 'punctuation',
    title: '标点符号',
    icon: '📝',
    symbols: [
      { symbol: '。', name: '句号' },
      { symbol: '，', name: '逗号' },
      { symbol: '；', name: '分号' },
      { symbol: '：', name: '冒号' },
      { symbol: '？', name: '问号' },
      { symbol: '！', name: '感叹号' },
      { symbol: '、', name: '顿号' },
      { symbol: '（', name: '左括号' },
      { symbol: '）', name: '右括号' },
      { symbol: '【', name: '左方括号' },
      { symbol: '】', name: '右方括号' },
      { symbol: '《', name: '左书名号' },
      { symbol: '》', name: '右书名号' },
      { symbol: '"', name: '左双引号' },
      { symbol: '"', name: '右双引号' },
      { symbol: "'", name: '左单引号' },
      { symbol: "'", name: '右单引号' }
    ]
  },
  {
    id: 'math',
    title: '数学符号',
    icon: '🔢',
    symbols: [
      { symbol: '＋', name: '加号' },
      { symbol: '－', name: '减号' },
      { symbol: '×', name: '乘号' },
      { symbol: '÷', name: '除号' },
      { symbol: '＝', name: '等号' },
      { symbol: '≠', name: '不等号' },
      { symbol: '＞', name: '大于号' },
      { symbol: '＜', name: '小于号' },
      { symbol: '≥', name: '大于等于' },
      { symbol: '≤', name: '小于等于' },
      { symbol: '±', name: '正负号' },
      { symbol: '∞', name: '无穷大' },
      { symbol: '√', name: '根号' },
      { symbol: '∑', name: '求和' },
      { symbol: '∏', name: '求积' },
      { symbol: '∫', name: '积分' },
      { symbol: '∂', name: '偏微分' },
      { symbol: '∆', name: '增量' },
      { symbol: '∇', name: '梯度' },
      { symbol: '∈', name: '属于' },
      { symbol: '∉', name: '不属于' },
      { symbol: '⊂', name: '包含于' },
      { symbol: '⊃', name: '包含' },
      { symbol: '∪', name: '并集' },
      { symbol: '∩', name: '交集' }
    ]
  },
  {
    id: 'arrows',
    title: '箭头符号',
    icon: '➡️',
    symbols: [
      { symbol: '→', name: '右箭头' },
      { symbol: '←', name: '左箭头' },
      { symbol: '↑', name: '上箭头' },
      { symbol: '↓', name: '下箭头' },
      { symbol: '↗', name: '右上箭头' },
      { symbol: '↖', name: '左上箭头' },
      { symbol: '↘', name: '右下箭头' },
      { symbol: '↙', name: '左下箭头' },
      { symbol: '⇒', name: '双线右箭头' },
      { symbol: '⇐', name: '双线左箭头' },
      { symbol: '⇑', name: '双线上箭头' },
      { symbol: '⇓', name: '双线下箭头' },
      { symbol: '➡', name: '粗右箭头' },
      { symbol: '⬅', name: '粗左箭头' },
      { symbol: '⬆', name: '粗上箭头' },
      { symbol: '⬇', name: '粗下箭头' }
    ]
  }
]

// 过滤后的符号
const filteredSymbols = computed(() => {
  let groups = symbolGroups

  // 按分类过滤
  if (selectedCategory.value !== 'all') {
    groups = groups.filter(group => group.id === selectedCategory.value)
  }

  // 按搜索文本过滤
  if (searchText.value.trim()) {
    const search = searchText.value.toLowerCase()
    groups = groups.map(group => ({
      ...group,
      symbols: group.symbols.filter(item =>
        item.symbol.includes(search) ||
        item.name.toLowerCase().includes(search)
      )
    })).filter(group => group.symbols.length > 0)
  }

  return groups
})

function insertSymbol(symbol) {
  emit('insert', symbol)
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.symbol-container {
  max-height: 60vh;
  overflow-y: auto;
}

.symbol-filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.category-select {
  min-width: 150px;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.symbol-group {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-weight: 500;
}

.group-icon {
  font-size: 18px;
}

.group-count {
  color: #666;
  font-size: 12px;
  margin-left: auto;
}

.symbol-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 1px;
  padding: 15px;
  background: #f8f9fa;
}

.symbol-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 70px;
}

.symbol-item:hover {
  background: #409eff;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.symbol-char {
  font-size: 20px;
  margin-bottom: 4px;
}

.symbol-name {
  font-size: 11px;
  text-align: center;
  line-height: 1.2;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-input,
  .category-select {
    width: 100%;
    max-width: none;
  }
  
  .symbol-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
    padding: 10px;
  }
  
  .symbol-item {
    min-height: 60px;
    padding: 8px 4px;
  }
  
  .symbol-char {
    font-size: 16px;
  }
  
  .symbol-name {
    font-size: 10px;
  }
}
</style>
