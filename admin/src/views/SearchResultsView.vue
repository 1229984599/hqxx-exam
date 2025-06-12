<template>
  <PageLayout
    :title="`搜索结果: ${searchQuery}`"
    :subtitle="`找到 ${totalResults} 个相关结果`"
  >
    <!-- 搜索筛选 -->
    <div class="search-filters">
      <div class="filter-tabs">
        <el-button
          v-for="tab in filterTabs"
          :key="tab.key"
          :type="activeTab === tab.key ? 'primary' : ''"
          @click="activeTab = tab.key"
          class="filter-tab"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          {{ tab.label }}
          <el-badge 
            v-if="getTabCount(tab.key) > 0" 
            :value="getTabCount(tab.key)" 
            class="tab-badge"
          />
        </el-button>
      </div>
      
      <div class="search-actions">
        <el-input
          v-model="searchQuery"
          placeholder="重新搜索..."
          :prefix-icon="Search"
          @keydown.enter="performSearch"
          class="search-input"
        />
        <el-button type="primary" @click="performSearch" :loading="loading">
          搜索
        </el-button>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results" v-loading="loading">
      <!-- 试题结果 -->
      <div v-if="activeTab === 'all' || activeTab === 'questions'" class="result-section">
        <div v-if="searchResults.questions?.length > 0" class="questions-results">
          <h3 class="section-title">
            <el-icon><Document /></el-icon>
            试题结果 ({{ searchResults.questions.length }})
          </h3>
          
          <div class="questions-grid">
            <div 
              v-for="question in searchResults.questions"
              :key="question.id"
              class="question-card"
              @click="viewQuestion(question)"
            >
              <div class="question-header">
                <div class="question-title" v-html="highlightText(question.title)"></div>
                <div class="question-actions">
                  <el-button size="small" type="primary" @click.stop="editQuestion(question)">
                    编辑
                  </el-button>
                </div>
              </div>
              
              <div class="question-content" v-html="highlightText(question.content)"></div>
              
              <div class="question-meta">
                <el-tag size="small" type="info">{{ question.subject?.name }}</el-tag>
                <el-tag size="small" type="success">{{ question.grade?.name }}</el-tag>
                <el-tag size="small">{{ question.category?.name }}</el-tag>
                <el-tag size="small" :type="getDifficultyType(question.difficulty)">
                  难度{{ question.difficulty }}
                </el-tag>
                <span class="view-count">
                  <el-icon><View /></el-icon>
                  {{ question.view_count }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 学科结果 -->
      <div v-if="activeTab === 'all' || activeTab === 'subjects'" class="result-section">
        <div v-if="searchResults.subjects?.length > 0" class="subjects-results">
          <h3 class="section-title">
            <el-icon><Reading /></el-icon>
            学科结果 ({{ searchResults.subjects.length }})
          </h3>
          
          <div class="subjects-grid">
            <div 
              v-for="subject in searchResults.subjects"
              :key="subject.id"
              class="subject-card"
              @click="viewSubject(subject)"
            >
              <div class="subject-header">
                <div class="subject-name" v-html="highlightText(subject.name)"></div>
                <div class="subject-code">{{ subject.code }}</div>
              </div>
              
              <div class="subject-description" v-html="highlightText(subject.description || '暂无描述')"></div>
              
              <div class="subject-stats">
                <span class="question-count">
                  <el-icon><Document /></el-icon>
                  {{ subject.question_count }} 个题目
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分类结果 -->
      <div v-if="activeTab === 'all' || activeTab === 'categories'" class="result-section">
        <div v-if="searchResults.categories?.length > 0" class="categories-results">
          <h3 class="section-title">
            <el-icon><Collection /></el-icon>
            分类结果 ({{ searchResults.categories.length }})
          </h3>
          
          <div class="categories-grid">
            <div 
              v-for="category in searchResults.categories"
              :key="category.id"
              class="category-card"
              @click="viewCategory(category)"
            >
              <div class="category-header">
                <div class="category-name" v-html="highlightText(category.name)"></div>
                <div class="category-code">{{ category.code }}</div>
              </div>
              
              <div class="category-description" v-html="highlightText(category.description || '暂无描述')"></div>
              
              <div class="category-meta">
                <el-tag size="small" type="primary">{{ category.subject?.name }}</el-tag>
                <span class="question-count">
                  <el-icon><Document /></el-icon>
                  {{ category.question_count }} 个题目
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无结果 -->
      <div v-if="!loading && totalResults === 0" class="no-results">
        <el-icon><DocumentDelete /></el-icon>
        <h3>未找到相关结果</h3>
        <p>尝试使用不同的关键词或检查拼写</p>
        <div class="search-suggestions">
          <p>搜索建议：</p>
          <ul>
            <li>使用更简短的关键词</li>
            <li>检查关键词拼写</li>
            <li>尝试使用同义词</li>
            <li>减少搜索条件</li>
          </ul>
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Search, Document, Reading, Collection, 
  DocumentDelete, View, Edit 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const searchResults = ref({})
const activeTab = ref('all')

// 筛选标签配置
const filterTabs = ref([
  { key: 'all', label: '全部', icon: 'Search' },
  { key: 'questions', label: '试题', icon: 'Document' },
  { key: 'subjects', label: '学科', icon: 'Reading' },
  { key: 'categories', label: '分类', icon: 'Collection' }
])

// 计算属性
const totalResults = computed(() => {
  let total = 0
  if (searchResults.value.questions) total += searchResults.value.questions.length
  if (searchResults.value.subjects) total += searchResults.value.subjects.length
  if (searchResults.value.categories) total += searchResults.value.categories.length
  if (searchResults.value.grades) total += searchResults.value.grades.length
  if (searchResults.value.semesters) total += searchResults.value.semesters.length
  return total
})

// 生命周期
onMounted(() => {
  searchQuery.value = route.query.q || ''
  activeTab.value = route.query.type || 'all'
  
  if (searchQuery.value) {
    performSearch()
  }
})

// 监听路由变化
watch(() => route.query, (newQuery) => {
  searchQuery.value = newQuery.q || ''
  activeTab.value = newQuery.type || 'all'
  
  if (searchQuery.value) {
    performSearch()
  }
})

// 方法
async function performSearch() {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  loading.value = true
  try {
    const params = {
      q: searchQuery.value.trim(),
      limit: 50
    }
    
    if (activeTab.value !== 'all') {
      params.type = activeTab.value
    }

    const response = await api.get('/search/global', { params })
    searchResults.value = response.data
    
    // 更新URL
    router.replace({
      query: {
        q: searchQuery.value.trim(),
        ...(activeTab.value !== 'all' && { type: activeTab.value })
      }
    })
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function getTabCount(tabKey) {
  switch (tabKey) {
    case 'all':
      return totalResults.value
    case 'questions':
      return searchResults.value.questions?.length || 0
    case 'subjects':
      return searchResults.value.subjects?.length || 0
    case 'categories':
      return searchResults.value.categories?.length || 0
    default:
      return 0
  }
}

function highlightText(text) {
  if (!searchQuery.value.trim() || !text) return text
  
  const query = searchQuery.value.trim()
  const regex = new RegExp(`(${query})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function getDifficultyType(difficulty) {
  const types = {
    1: 'success',
    2: 'info',
    3: 'warning',
    4: 'danger',
    5: 'danger'
  }
  return types[difficulty] || 'info'
}

function viewQuestion(question) {
  router.push(`/questions/edit/${question.id}`)
}

function editQuestion(question) {
  router.push(`/questions/edit/${question.id}`)
}

function viewSubject(subject) {
  router.push({
    path: '/subjects',
    query: { search: subject.name }
  })
}

function viewCategory(category) {
  router.push({
    path: '/categories',
    query: { search: category.name }
  })
}
</script>

<style scoped>
.search-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  position: relative;
  border-radius: 8px;
}

.tab-badge {
  margin-left: 8px;
}

.search-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.search-results {
  min-height: 400px;
}

.result-section {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.questions-grid,
.subjects-grid,
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.question-card,
.subject-card,
.category-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}

.question-card:hover,
.subject-card:hover,
.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.question-header,
.subject-header,
.category-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.question-title,
.subject-name,
.category-name {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  flex: 1;
}

.question-title :deep(mark),
.subject-name :deep(mark),
.category-name :deep(mark),
.question-content :deep(mark),
.subject-description :deep(mark),
.category-description :deep(mark) {
  background: var(--el-color-warning-light-8);
  color: var(--el-color-warning);
  padding: 0 2px;
  border-radius: 2px;
}

.subject-code,
.category-code {
  font-size: 12px;
  color: #718096;
  background: var(--el-fill-color-light);
  padding: 2px 8px;
  border-radius: 4px;
}

.question-content,
.subject-description,
.category-description {
  font-size: 14px;
  color: #4a5568;
  margin-bottom: 12px;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.question-meta,
.subject-stats,
.category-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.view-count,
.question-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #718096;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #718096;
}

.no-results .el-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #cbd5e0;
}

.no-results h3 {
  font-size: 20px;
  margin-bottom: 12px;
  color: #4a5568;
}

.no-results p {
  font-size: 14px;
  margin-bottom: 20px;
}

.search-suggestions {
  text-align: left;
  max-width: 300px;
  margin: 0 auto;
}

.search-suggestions p {
  font-weight: 600;
  margin-bottom: 8px;
}

.search-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.search-suggestions li {
  margin-bottom: 4px;
  font-size: 13px;
}

/* 深色模式适配 */
.dark .search-filters,
.dark .question-card,
.dark .subject-card,
.dark .category-card {
  background: rgba(30, 30, 40, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .section-title {
  color: #e2e8f0;
}

.dark .question-title,
.dark .subject-name,
.dark .category-name {
  color: #e2e8f0;
}

.dark .question-content,
.dark .subject-description,
.dark .category-description {
  color: #cbd5e0;
}

.dark .subject-code,
.dark .category-code {
  background: rgba(255, 255, 255, 0.1);
  color: #a0aec0;
}

.dark .no-results h3 {
  color: #e2e8f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-tabs {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .search-actions {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
    max-width: 300px;
  }
  
  .questions-grid,
  .subjects-grid,
  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>
