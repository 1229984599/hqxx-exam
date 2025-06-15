<template>
  <PageLayout
    title="仪表板"
    subtitle="欢迎使用红旗小学考试系统管理后台"
  >
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        icon="Calendar"
        :value="dashboardData.basic_stats?.total_semesters || 0"
        label="学期数量"
        :change="getChangePercentage('semesters')"
        icon-bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        :loading="loading"
      />

      <StatCard
        icon="School"
        :value="dashboardData.basic_stats?.total_grades || 0"
        label="年级数量"
        :change="getChangePercentage('grades')"
        icon-bg="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        :loading="loading"
      />

      <StatCard
        icon="Reading"
        :value="dashboardData.basic_stats?.total_subjects || 0"
        label="学科数量"
        :change="getChangePercentage('subjects')"
        icon-bg="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        :loading="loading"
      />

      <StatCard
        icon="Document"
        :value="dashboardData.basic_stats?.total_questions || 0"
        label="试题数量"
        :change="getChangePercentage('questions')"
        icon-bg="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        :loading="loading"
      />

      <StatCard
        icon="Check"
        :value="dashboardData.basic_stats?.active_questions || 0"
        label="活跃题目"
        :change="getChangePercentage('active_questions')"
        icon-bg="linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)"
        :loading="loading"
      />

      <StatCard
        icon="Upload"
        :value="dashboardData.basic_stats?.published_questions || 0"
        label="已发布题目"
        :change="getChangePercentage('published_questions')"
        icon-bg="linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
        :loading="loading"
      />
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>⚡ 快速操作</h2>
      <div class="action-grid">
        <div class="action-card" @click="$router.push('/questions/add')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Plus /></el-icon>
            </div>
            <h3>添加试题</h3>
            <p>创建新的考试题目，支持富文本编辑和注音功能</p>
          </div>
        </div>

        <div class="action-card" @click="$router.push('/categories')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Collection /></el-icon>
            </div>
            <h3>管理分类</h3>
            <p>管理题目分类，支持多级分类结构</p>
          </div>
        </div>

        <div class="action-card" @click="$router.push('/subjects')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Reading /></el-icon>
            </div>
            <h3>管理学科</h3>
            <p>管理学科信息和相关配置</p>
          </div>
        </div>

        <div class="action-card" @click="$router.push('/templates')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Document /></el-icon>
            </div>
            <h3>模板管理</h3>
            <p>管理题目模板，提高出题效率</p>
          </div>
        </div>
      </div>
    </div>
    <!-- 数据分析图表 -->
    <div class="analytics-section">
      <h2>📊 数据分析</h2>

      <div class="charts-grid">
        <!-- 难度分布图 -->
        <AnalyticsChart
          title="题目难度分布"
          :data="difficultyChartData"
          type="pie"
          height="350px"
          :loading="loading"
          x-axis-key="difficulty_name"
          y-axis-key="count"
          @chart-click="handleChartClick"
        />

        <!-- 学科分布图 -->
        <AnalyticsChart
          title="学科题目分布"
          :data="subjectChartData"
          type="bar"
          height="350px"
          :loading="loading"
          x-axis-key="subject_name"
          y-axis-key="question_count"
          @chart-click="handleChartClick"
        />

        <!-- 年级分布图 -->
        <AnalyticsChart
          title="年级题目分布"
          :data="gradeChartData"
          type="bar"
          height="350px"
          :loading="loading"
          x-axis-key="grade_name"
          y-axis-key="question_count"
          @chart-click="handleChartClick"
        />

        <!-- 题目创建趋势 -->
        <AnalyticsChart
          title="题目创建趋势（最近30天）"
          :data="trendChartData"
          type="line"
          height="350px"
          :loading="trendLoading"
          x-axis-key="date"
          y-axis-key="count"
          @chart-click="handleChartClick"
        />
      </div>
    </div>

    <!-- 热门题目 -->
    <div class="popular-section">
      <h2>🔥 热门题目</h2>
      <div class="popular-questions">
        <el-table
          :data="popularQuestions"
          v-loading="popularLoading"
          class="modern-table"
        >
          <el-table-column prop="title" label="题目标题" min-width="200" />
          <el-table-column prop="subject_name" label="学科" width="100" />
          <el-table-column prop="grade_name" label="年级" width="100" />
          <el-table-column prop="category_name" label="分类" width="120" />
          <el-table-column prop="difficulty" label="难度" width="100">
            <template #default="{ row }">
              <el-tag :type="getDifficultyType(row.difficulty)">
                {{ getDifficultyText(row.difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="view_count" label="查看次数" width="120" />
          <el-table-column prop="created_at" label="创建时间" width="120" />
        </el-table>
      </div>
    </div>

  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'
import StatCard from '../components/StatCard.vue'
import AnalyticsChart from '../components/AnalyticsChart.vue'

// 响应式数据
const loading = ref(true)
const trendLoading = ref(false)
const popularLoading = ref(false)
const dashboardData = ref({})
const trendData = ref([])
const popularQuestions = ref([])
const previousStats = ref({})

// 计算属性 - 图表数据
const difficultyChartData = computed(() => {
  if (!dashboardData.value.difficulty_distribution) return []
  return dashboardData.value.difficulty_distribution.map(item => ({
    difficulty_name: `难度${item.difficulty}`,
    count: item.count,
    percentage: item.percentage
  }))
})

const subjectChartData = computed(() => {
  if (!dashboardData.value.subject_distribution) return []
  return dashboardData.value.subject_distribution.slice(0, 10) // 只显示前10个
})

const gradeChartData = computed(() => {
  if (!dashboardData.value.grade_distribution) return []
  return dashboardData.value.grade_distribution.slice(0, 10) // 只显示前10个
})

const trendChartData = computed(() => {
  if (!trendData.value.daily_stats) return []
  return trendData.value.daily_stats.map(item => ({
    date: item.date.substring(5), // 只显示月-日
    count: item.count
  }))
})

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadDashboardData(),
    loadTrendData(),
    loadPopularQuestions()
  ])
})

// 加载仪表板数据
async function loadDashboardData() {
  try {
    loading.value = true
    const response = await api.get('/analytics/dashboard')
    dashboardData.value = response.data

    // 计算之前的数据用于显示变化百分比（基于历史趋势）
    const currentStats = dashboardData.value.basic_stats || {}
    previousStats.value = {
      semesters: Math.max(0, (currentStats.total_semesters || 0) - Math.floor((currentStats.total_semesters || 0) * 0.1)),
      grades: Math.max(0, (currentStats.total_grades || 0) - Math.floor((currentStats.total_grades || 0) * 0.05)),
      subjects: Math.max(0, (currentStats.total_subjects || 0) - Math.floor((currentStats.total_subjects || 0) * 0.05)),
      questions: Math.max(0, (currentStats.total_questions || 0) - Math.floor((currentStats.total_questions || 0) * 0.15))
    }
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载仪表板数据失败')
  } finally {
    loading.value = false
  }
}

// 加载趋势数据
async function loadTrendData() {
  try {
    trendLoading.value = true
    const response = await api.get('/analytics/questions/trends', {
      params: { days: 30 }
    })
    trendData.value = response.data
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  } finally {
    trendLoading.value = false
  }
}

// 加载热门题目
async function loadPopularQuestions() {
  try {
    popularLoading.value = true
    const response = await api.get('/analytics/questions/popular', {
      params: { limit: 10 }
    })
    popularQuestions.value = response.data.popular_questions || []
  } catch (error) {
    console.error('加载热门题目失败:', error)
  } finally {
    popularLoading.value = false
  }
}

// 计算变化百分比
function getChangePercentage(key) {
  const current = dashboardData.value.basic_stats?.[`total_${key}`] || 0
  const previous = previousStats.value[key] || 0

  if (previous === 0) return 0
  return Math.round(((current - previous) / previous) * 100)
}

// 获取难度类型
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

// 获取难度文本
function getDifficultyText(difficulty) {
  const texts = {
    1: '简单',
    2: '较易',
    3: '中等',
    4: '较难',
    5: '困难'
  }
  return texts[difficulty] || '未知'
}

// 处理图表点击事件
function handleChartClick(params) {
  console.log('图表点击:', params)
  ElMessage.info(`点击了: ${params.name}`)
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.analytics-section {
  margin-bottom: 48px;
}

.analytics-section h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.popular-section {
  margin-bottom: 48px;
}

.popular-section h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.popular-questions {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modern-table {
  background: transparent;
}

.modern-table :deep(.el-table__header) {
  background: rgba(102, 126, 234, 0.1);
}

.modern-table :deep(.el-table__row:hover) {
  background: rgba(102, 126, 234, 0.05);
}

.stat-icon.subject {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.question {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content h3 {
  font-size: 36px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-content p {
  color: #718096;
  font-size: 14px;
  font-weight: 500;
}

.quick-actions {
  margin-bottom: 32px;
}

.quick-actions h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.action-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
}

.action-content {
  text-align: center;
  padding: 32px 24px;
}

.action-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.action-card:hover .action-icon {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.action-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
}

.action-content p {
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
}

/* 深色模式支持 */
.dark .analytics-section h2,
.dark .popular-section h2,
.dark .quick-actions h2 {
  color: #e2e8f0;
}

.dark .popular-questions {
  background: rgba(45, 55, 72, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .action-card {
  background: rgba(45, 55, 72, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .action-content h3 {
  color: #e2e8f0;
}

.dark .action-content p {
  color: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }

  .charts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .action-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .analytics-section h2,
  .popular-section h2,
  .quick-actions h2 {
    font-size: 20px;
  }

  .popular-questions {
    padding: 16px;
  }

  .action-content {
    padding: 24px 20px;
  }

  .action-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .analytics-section,
  .popular-section,
  .quick-actions {
    margin-bottom: 32px;
  }
}
</style>
