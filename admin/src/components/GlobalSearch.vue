<template>
  <div class="global-search">
    <el-popover
      :visible="showResults"
      placement="bottom-start"
      :width="480"
      trigger="manual"
      popper-class="search-popover"
      @hide="handlePopoverHide"
    >
      <template #reference>
        <div class="search-input-container">
          <el-input
            v-model="searchQuery"
            placeholder="全局搜索试题、分类、学科..."
            :prefix-icon="Search"
            clearable
            size="large"
            class="search-input"
            @input="handleSearch"
            @focus="handleFocus"
            @blur="handleBlur"
            @keydown.enter="handleEnter"
            @keydown.up.prevent="navigateResults(-1)"
            @keydown.down.prevent="navigateResults(1)"
            @keydown.esc="hideResults"
          />
          <div v-if="loading" class="search-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
        </div>
      </template>

      <!-- 搜索结果 -->
      <div class="search-results" v-if="showResults">
        <!-- 搜索建议 -->
        <div v-if="!searchQuery && recentSearches.length > 0" class="search-section">
          <div class="section-title">
            <el-icon><Clock /></el-icon>
            <span>最近搜索</span>
            <el-button 
              text 
              size="small" 
              @click="clearRecentSearches"
              class="clear-btn"
            >
              清除
            </el-button>
          </div>
          <div class="recent-searches">
            <el-tag
              v-for="(item, index) in recentSearches.slice(0, 5)"
              :key="index"
              size="small"
              class="recent-tag"
              @click="selectRecentSearch(item)"
            >
              {{ item }}
            </el-tag>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div v-if="!searchQuery" class="search-section">
          <div class="section-title">
            <el-icon><Lightning /></el-icon>
            <span>快捷操作</span>
          </div>
          <div class="quick-actions">
            <div 
              v-for="action in quickActions"
              :key="action.key"
              class="quick-action-item"
              @click="handleQuickAction(action)"
            >
              <el-icon>
                <component :is="action.icon" />
              </el-icon>
              <span>{{ action.label }}</span>
              <kbd>{{ action.shortcut }}</kbd>
            </div>
          </div>
        </div>

        <!-- 搜索结果 -->
        <div v-if="searchQuery && searchResults.length > 0" class="search-section">
          <div class="section-title">
            <el-icon><Search /></el-icon>
            <span>搜索结果 ({{ totalResults }})</span>
          </div>
          
          <!-- 试题结果 -->
          <div v-if="searchResults.questions?.length > 0" class="result-group">
            <div class="group-title">试题 ({{ searchResults.questions.length }})</div>
            <div 
              v-for="(item, index) in searchResults.questions.slice(0, 3)"
              :key="`question-${item.id}`"
              class="result-item"
              :class="{ active: selectedIndex === getItemIndex('questions', index) }"
              @click="handleResultClick(item, 'question')"
              @mouseenter="selectedIndex = getItemIndex('questions', index)"
            >
              <div class="result-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="result-content">
                <div class="result-title" v-html="highlightText(item.title)"></div>
                <div class="result-meta">
                  <el-tag size="small" type="info">{{ item.subject?.name }}</el-tag>
                  <el-tag size="small" type="success">{{ item.grade?.name }}</el-tag>
                  <span class="result-difficulty">难度{{ item.difficulty }}</span>
                </div>
              </div>
            </div>
            <div v-if="searchResults.questions.length > 3" class="show-more">
              <el-button text size="small" @click="showAllResults('questions')">
                查看全部 {{ searchResults.questions.length }} 个试题
              </el-button>
            </div>
          </div>

          <!-- 分类结果 -->
          <div v-if="searchResults.categories?.length > 0" class="result-group">
            <div class="group-title">分类 ({{ searchResults.categories.length }})</div>
            <div 
              v-for="(item, index) in searchResults.categories.slice(0, 2)"
              :key="`category-${item.id}`"
              class="result-item"
              :class="{ active: selectedIndex === getItemIndex('categories', index) }"
              @click="handleResultClick(item, 'category')"
              @mouseenter="selectedIndex = getItemIndex('categories', index)"
            >
              <div class="result-icon">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="result-content">
                <div class="result-title" v-html="highlightText(item.name)"></div>
                <div class="result-meta">
                  <el-tag size="small" type="primary">{{ item.subject?.name }}</el-tag>
                  <span class="result-code">{{ item.code }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 学科结果 -->
          <div v-if="searchResults.subjects?.length > 0" class="result-group">
            <div class="group-title">学科 ({{ searchResults.subjects.length }})</div>
            <div 
              v-for="(item, index) in searchResults.subjects"
              :key="`subject-${item.id}`"
              class="result-item"
              :class="{ active: selectedIndex === getItemIndex('subjects', index) }"
              @click="handleResultClick(item, 'subject')"
              @mouseenter="selectedIndex = getItemIndex('subjects', index)"
            >
              <div class="result-icon">
                <el-icon><Reading /></el-icon>
              </div>
              <div class="result-content">
                <div class="result-title" v-html="highlightText(item.name)"></div>
                <div class="result-meta">
                  <span class="result-description">{{ item.description || '暂无描述' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 无结果 -->
        <div v-if="searchQuery && searchResults.length === 0 && !loading" class="no-results">
          <el-icon><DocumentDelete /></el-icon>
          <p>未找到相关结果</p>
          <p class="no-results-tip">尝试使用不同的关键词或检查拼写</p>
        </div>

        <!-- 搜索提示 -->
        <div v-if="searchQuery" class="search-tips">
          <div class="tips-title">搜索提示：</div>
          <ul class="tips-list">
            <li>使用空格分隔多个关键词</li>
            <li>支持拼音首字母搜索</li>
            <li>可搜索题目标题、学科、分类等</li>
          </ul>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Search, Loading, Clock, Lightning, Document, 
  Collection, Reading, DocumentDelete, Plus, Setting 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { debounce } from 'lodash-es'
import api from '../utils/api'

const router = useRouter()

// 响应式数据
const searchQuery = ref('')
const showResults = ref(false)
const loading = ref(false)
const searchResults = ref({})
const selectedIndex = ref(-1)
const recentSearches = ref([])

// 快捷操作配置
const quickActions = ref([
  {
    key: 'add-question',
    label: '添加试题',
    icon: 'Plus',
    shortcut: 'Ctrl+N',
    action: () => router.push('/questions/add')
  },
  {
    key: 'question-list',
    label: '试题管理',
    icon: 'Document',
    shortcut: 'Ctrl+Q',
    action: () => router.push('/questions')
  },
  {
    key: 'category-list',
    label: '分类管理',
    icon: 'Collection',
    shortcut: 'Ctrl+C',
    action: () => router.push('/categories')
  },
  {
    key: 'system-settings',
    label: '系统设置',
    icon: 'Setting',
    shortcut: 'Ctrl+S',
    action: () => router.push('/system')
  }
])

// 计算属性
const totalResults = computed(() => {
  let total = 0
  if (searchResults.value.questions) total += searchResults.value.questions.length
  if (searchResults.value.categories) total += searchResults.value.categories.length
  if (searchResults.value.subjects) total += searchResults.value.subjects.length
  return total
})

// 生命周期
onMounted(() => {
  loadRecentSearches()
  document.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})

// 监听搜索查询
watch(searchQuery, debounce(async (newQuery) => {
  if (newQuery.trim()) {
    await performSearch(newQuery.trim())
  } else {
    searchResults.value = {}
    selectedIndex.value = -1
  }
}, 300))

// 方法
function handleFocus() {
  showResults.value = true
}

function handleBlur() {
  // 延迟隐藏，允许点击结果
  setTimeout(() => {
    if (!document.querySelector('.search-popover:hover')) {
      showResults.value = false
    }
  }, 200)
}

function handlePopoverHide() {
  showResults.value = false
  selectedIndex.value = -1
}

function hideResults() {
  showResults.value = false
  selectedIndex.value = -1
}

async function performSearch(query) {
  loading.value = true
  try {
    const response = await api.get('/search/global', {
      params: { q: query, limit: 10 }
    })
    searchResults.value = response.data
    selectedIndex.value = -1
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = {}
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  if (!showResults.value) {
    showResults.value = true
  }
}

function handleEnter() {
  if (selectedIndex.value >= 0) {
    const item = getSelectedItem()
    if (item) {
      handleResultClick(item.data, item.type)
    }
  } else if (searchQuery.value.trim()) {
    // 保存搜索历史
    saveRecentSearch(searchQuery.value.trim())
    // 跳转到搜索结果页面
    router.push({
      path: '/search',
      query: { q: searchQuery.value.trim() }
    })
    hideResults()
  }
}

function navigateResults(direction) {
  const totalItems = getTotalResultItems()
  if (totalItems === 0) return

  selectedIndex.value += direction
  if (selectedIndex.value < 0) {
    selectedIndex.value = totalItems - 1
  } else if (selectedIndex.value >= totalItems) {
    selectedIndex.value = 0
  }
}

function getTotalResultItems() {
  let total = 0
  if (searchResults.value.questions) total += Math.min(searchResults.value.questions.length, 3)
  if (searchResults.value.categories) total += Math.min(searchResults.value.categories.length, 2)
  if (searchResults.value.subjects) total += searchResults.value.subjects.length
  return total
}

function getItemIndex(type, index) {
  let baseIndex = 0
  if (type === 'categories') {
    baseIndex += Math.min(searchResults.value.questions?.length || 0, 3)
  } else if (type === 'subjects') {
    baseIndex += Math.min(searchResults.value.questions?.length || 0, 3)
    baseIndex += Math.min(searchResults.value.categories?.length || 0, 2)
  }
  return baseIndex + index
}

function getSelectedItem() {
  let currentIndex = 0
  
  // 检查试题
  const questionsCount = Math.min(searchResults.value.questions?.length || 0, 3)
  if (selectedIndex.value < currentIndex + questionsCount) {
    return {
      data: searchResults.value.questions[selectedIndex.value - currentIndex],
      type: 'question'
    }
  }
  currentIndex += questionsCount
  
  // 检查分类
  const categoriesCount = Math.min(searchResults.value.categories?.length || 0, 2)
  if (selectedIndex.value < currentIndex + categoriesCount) {
    return {
      data: searchResults.value.categories[selectedIndex.value - currentIndex],
      type: 'category'
    }
  }
  currentIndex += categoriesCount
  
  // 检查学科
  const subjectsCount = searchResults.value.subjects?.length || 0
  if (selectedIndex.value < currentIndex + subjectsCount) {
    return {
      data: searchResults.value.subjects[selectedIndex.value - currentIndex],
      type: 'subject'
    }
  }
  
  return null
}

function handleResultClick(item, type) {
  if (searchQuery.value.trim()) {
    saveRecentSearch(searchQuery.value.trim())
  }

  hideResults()
  searchQuery.value = ''

  switch (type) {
    case 'question':
      router.push(`/questions/edit/${item.id}`)
      break
    case 'category':
      router.push({
        path: '/categories',
        query: { search: item.name }
      })
      break
    case 'subject':
      router.push({
        path: '/subjects',
        query: { search: item.name }
      })
      break
  }
}

function handleQuickAction(action) {
  hideResults()
  searchQuery.value = ''
  action.action()
}

function showAllResults(type) {
  router.push({
    path: '/search',
    query: { 
      q: searchQuery.value.trim(),
      type: type
    }
  })
  hideResults()
}

function highlightText(text) {
  if (!searchQuery.value.trim()) return text
  
  const query = searchQuery.value.trim()
  const regex = new RegExp(`(${query})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function selectRecentSearch(query) {
  searchQuery.value = query
  // 触发搜索
  performSearch(query)
}

function saveRecentSearch(query) {
  if (!query || query.length < 2) return
  
  const searches = recentSearches.value.filter(item => item !== query)
  searches.unshift(query)
  recentSearches.value = searches.slice(0, 10)
  
  localStorage.setItem('recent-searches', JSON.stringify(recentSearches.value))
}

function loadRecentSearches() {
  try {
    const saved = localStorage.getItem('recent-searches')
    if (saved) {
      recentSearches.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('加载搜索历史失败:', error)
  }
}

function clearRecentSearches() {
  recentSearches.value = []
  localStorage.removeItem('recent-searches')
}

function handleGlobalKeydown(event) {
  // Ctrl/Cmd + K 打开搜索
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    document.querySelector('.search-input input')?.focus()
  }
}
</script>

<style scoped>
.global-search {
  position: relative;
}

.search-input-container {
  position: relative;
  width: 320px;
}

.search-input {
  width: 100%;
}

.search-loading {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--el-color-primary);
}

.search-results {
  max-height: 500px;
  overflow-y: auto;
}

.search-section {
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.search-section:last-child {
  border-bottom: none;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
}

.clear-btn {
  margin-left: auto;
  font-size: 12px;
}

.recent-searches {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recent-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.recent-tag:hover {
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-action-item:hover {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.quick-action-item span {
  flex: 1;
  font-size: 14px;
}

.quick-action-item kbd {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 11px;
  color: var(--el-text-color-secondary);
}

.result-group {
  margin-bottom: 16px;
}

.group-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-item:hover,
.result-item.active {
  background: var(--el-color-primary-light-9);
}

.result-icon {
  width: 32px;
  height: 32px;
  background: var(--el-color-primary-light-8);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-title :deep(mark) {
  background: var(--el-color-warning-light-8);
  color: var(--el-color-warning);
  padding: 0 2px;
  border-radius: 2px;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.result-difficulty,
.result-code,
.result-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.show-more {
  text-align: center;
  margin-top: 8px;
}

.no-results {
  text-align: center;
  padding: 32px 16px;
  color: var(--el-text-color-secondary);
}

.no-results .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--el-text-color-placeholder);
}

.no-results p {
  margin: 8px 0;
}

.no-results-tip {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.search-tips {
  padding: 12px;
  background: var(--el-fill-color-extra-light);
  border-radius: 6px;
  margin-top: 8px;
}

.tips-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.tips-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.tips-list li {
  margin-bottom: 4px;
}

/* 深色模式适配 */
.dark .search-input-container {
  background: rgba(40, 40, 50, 0.8);
  border-radius: 8px;
}

.dark .result-icon {
  background: rgba(102, 126, 234, 0.2);
}

.dark .quick-action-item kbd {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #a0aec0;
}

.dark .search-tips {
  background: rgba(255, 255, 255, 0.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-input-container {
    width: 280px;
  }
  
  .quick-action-item {
    padding: 12px;
  }
  
  .quick-action-item kbd {
    display: none;
  }
}
</style>
