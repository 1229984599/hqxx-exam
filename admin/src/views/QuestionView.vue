<template>
  <PageLayout
    title="试题管理"
    subtitle="创建和管理考试题目，支持富文本编辑和注音功能"
  >
    <template #actions>
      <el-button
        v-permission="'questions:create'"
        type="primary"
        @click="$router.push('/questions/add')"
        :icon="Plus"
        size="large"
      >
        添加试题
      </el-button>
    </template>

    <!-- 搜索筛选区域 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索题目标题"
            :prefix-icon="Search"
            clearable
            style="width: 250px"
            @input="handleSearchInput"
            @clear="loadQuestions"
          />
        </el-form-item>
        
        <el-form-item>
          <el-select
            v-model="filters.semester_id"
            placeholder="学期"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="filters.grade_id"
            placeholder="年级"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="filters.subject_id"
            placeholder="学科"
            clearable
            style="width: 140px"
            @change="handleSubjectChange"
            :loading="loading"
          >
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="filters.category_id"
            placeholder="分类"
            clearable
            style="width: 140px"
            :disabled="!filters.subject_id"
          >
            <el-option
              v-for="category in filteredCategories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="filters.question_type"
            placeholder="题目类型"
            clearable
            style="width: 140px"
          >
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="填空题" value="fill" />
            <el-option label="判断题" value="judge" />
            <el-option label="问答题" value="essay" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="filters.difficulty"
            placeholder="难度"
            clearable
            style="width: 120px"
          >
            <el-option label="很简单" :value="1" />
            <el-option label="简单" :value="2" />
            <el-option label="中等" :value="3" />
            <el-option label="困难" :value="4" />
            <el-option label="很困难" :value="5" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadQuestions" :icon="Search">
            搜索
          </el-button>
          <el-button @click="resetFilters" :icon="Refresh">
            重置
          </el-button>
          <el-button type="success" @click="$router.push('/questions/add')" :icon="Plus">
            添加试题
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 批量操作 -->
    <BatchOperations
      :items="questions"
      v-model:selectedItems="selectedQuestions"
      @refresh="loadQuestions"
    />

    <!-- 空状态 -->
    <div v-if="!loading && questions.length === 0" class="empty-state">
      <el-empty
        :description="getEmptyDescription()"
        :image-size="120"
      >
        <el-button
          v-if="!hasFilters"
          type="primary"
          @click="$router.push('/questions/add')"
          :icon="Plus"
        >
          添加第一个试题
        </el-button>
        <el-button
          v-else
          @click="resetFilters"
          :icon="Refresh"
        >
          清除筛选条件
        </el-button>
      </el-empty>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-else
      :data="questions"
      v-loading="loading"
      class="modern-table"
      @selection-change="handleSelectionChange"
    >
      <!-- 选择列 -->
      <el-table-column type="selection" width="55" />
      <el-table-column prop="title" label="题目标题" width="340">
        <template #default="{ row }">
          <div class="question-title">
            <span class="title-text">{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="内容简要" min-width="300">
        <template #default="{ row }">
          <div class="content-summary">
            <p class="summary-text">{{ getContentSummary(row.content, 50) }}</p>
            <div class="content-meta">
              <el-tag size="small" type="info">{{ getQuestionTypeText(row.question_type) }}</el-tag>
              <el-tag size="small" :type="getDifficultyType(row.difficulty)">
                {{ getDifficultyText(row.difficulty) }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="category.name" label="题目分类" width="120">
        <template #default="{ row }">
          <div class="question-title">
            <el-tag
              size="small"
              class="type-tag"
            >
              {{ row.category?.name || '未分类' }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="semester.name" label="学期" width="140" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.semester" type="success" size="small">
            {{ row.semester.name }}
          </el-tag>
          <span v-else class="text-gray-400">未设置</span>
        </template>
      </el-table-column>

      <el-table-column prop="grade.name" label="年级" width="120" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.grade" type="info" size="small">
            {{ row.grade.name }}
          </el-tag>
          <span v-else class="text-gray-400">未设置</span>
        </template>
      </el-table-column>

      <el-table-column prop="subject.name" label="学科" width="120" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.subject" type="primary" size="small">
            {{ row.subject.name }}
          </el-tag>
          <span v-else class="text-gray-400">未设置</span>
        </template>
      </el-table-column>

      <el-table-column prop="is_published" align="center" label="状态" width="100">
        <template #default="{ row }">
          <el-tag
            :type="row.is_published ? 'success' : 'warning'"
            size="small"
            style="cursor: pointer"
            @click="togglePublishStatus(row)"
            v-permission="'questions:edit'"
          >
            {{ row.is_published ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" align="center" label="查看次数" width="120" />
      <el-table-column label="操作" align="center" width="200" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              v-permission="'questions:edit'"
              size="small"
              @click="$router.push(`/questions/edit/${row.id}`)"
              :icon="Edit"
              title="编辑试题"
            />
            <el-button
              v-permission="'questions:create'"
              size="small"
              type="success"
              @click="copyQuestion(row)"
              :icon="CopyDocument"
              title="复制试题"
            />
            <el-button
              v-permission="'questions:delete'"
              size="small"
              type="danger"
              @click="deleteQuestion(row)"
              :icon="Delete"
              title="删除试题"
            />
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-section">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </PageLayout>
</template>

<script setup name="QuestionView">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, Search, Refresh, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import { getDifficultyText, getDifficultyType, getQuestionTypeText } from '../composables/useCrud'
import { usePermissions } from '../composables/usePermissions'
import { useErrorHandler } from '../composables/useErrorHandler'
import PageLayout from '../components/PageLayout.vue'
import BatchOperations from '../components/BatchOperations.vue'

const { hasRole, hasAnyRole, isAdmin, isTeacher, isSubjectAdmin } = usePermissions()
const { handleApiError } = useErrorHandler()
const router = useRouter()

const loading = ref(false)

// 根据选择的学科过滤分类
const filteredCategories = computed(() => {
  if (!filters.subject_id) {
    return []
  }
  return categories.value.filter(category => category.subject_id === filters.subject_id)
})

// 检查是否有筛选条件
const hasFilters = computed(() => {
  return Object.values(filters).some(value => value !== null && value !== '')
})

const questions = ref([])
const selectedQuestions = ref([])
const semesters = ref([])
const grades = ref([])
const subjects = ref([])
const categories = ref([])

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const filters = reactive({
  semester_id: null,
  grade_id: null,
  subject_id: null,
  category_id: null,
  question_type: null,
  difficulty: null,
  search: ''
})

onMounted(() => {
  loadBasicData()
  loadQuestions()
})

async function loadBasicData() {
  try {
    const [semestersRes, gradesRes, subjectsRes, categoriesRes] = await Promise.all([
      api.get('/semesters/'),
      api.get('/grades/'),
      api.get('/subjects/'),
      api.get('/categories/', { params: { limit: 1000 } }) // 加载所有分类，不限制数量
    ])

    semesters.value = semestersRes.data
    grades.value = gradesRes.data
    subjects.value = subjectsRes.data
    categories.value = categoriesRes.data
  } catch (error) {
    handleApiError(error, '加载基础数据失败', {
      showRetry: true,
      onRetry: loadBasicData
    })
  }
}

async function loadQuestions() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    }

    // 添加筛选条件
    if (filters.semester_id) params.semester_id = filters.semester_id
    if (filters.grade_id) params.grade_id = filters.grade_id
    if (filters.subject_id) params.subject_id = filters.subject_id
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.question_type) params.question_type = filters.question_type
    if (filters.difficulty) params.difficulty = filters.difficulty
    if (filters.search) params.search = filters.search

    const response = await api.get('/questions/', { params })

    // 处理响应数据结构
    if (response.data && typeof response.data === 'object') {
      if (Array.isArray(response.data)) {
        // 如果直接返回数组
        questions.value = response.data
        pagination.total = response.data.length
      } else if (response.data.items && Array.isArray(response.data.items)) {
        // 如果返回 { items: [], total: number } 结构
        questions.value = response.data.items
        pagination.total = response.data.total || response.data.items.length
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // 如果返回 { results: [], total: number } 结构
        questions.value = response.data.results
        pagination.total = response.data.total || response.data.results.length
      } else {
        // 其他情况，尝试直接使用data
        questions.value = Array.isArray(response.data) ? response.data : []
        pagination.total = questions.value.length
      }
    } else {
      questions.value = []
      pagination.total = 0
    }

    // 数据验证和清理
    questions.value = questions.value.map(question => ({
      ...question,
      // 确保基本字段存在
      id: question.id || 0,
      title: question.title || '无标题',
      content: question.content || '',
      difficulty: question.difficulty || 1,
      question_type: question.question_type || 'single',
      is_published: question.is_published || false,
      view_count: question.view_count || 0,
      // 确保关联对象存在
      semester: question.semester || null,
      grade: question.grade || null,
      subject: question.subject || null,
      category: question.category || null
    }))


  } catch (error) {
    questions.value = [] // 确保在错误时清空数据
    pagination.total = 0

    handleApiError(error, '加载试题列表失败', {
      showRetry: true,
      onRetry: loadQuestions
    })
  } finally {
    loading.value = false
  }
}

async function deleteQuestion(question) {
  try {
    await ElMessageBox.confirm(
      `确定要删除试题"${question.title}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )

    const deleteLoading = ElMessage({
      message: '正在删除试题...',
      type: 'info',
      duration: 0
    })

    try {
      await api.delete(`/questions/${question.id}`)
      deleteLoading.close()
      ElMessage.success('试题删除成功')

      // 如果当前页没有数据了，回到上一页
      if (questions.value.length === 1 && pagination.page > 1) {
        pagination.page--
      }

      loadQuestions()
    } catch (deleteError) {
      deleteLoading.close()
      console.error('删除试题失败:', deleteError)
      const errorMessage = deleteError.response?.data?.detail || deleteError.message || '删除试题失败'
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除操作异常:', error)
    }
  }
}

function resetFilters() {
  Object.assign(filters, {
    semester_id: null,
    grade_id: null,
    subject_id: null,
    category_id: null,
    question_type: null,
    difficulty: null,
    search: ''
  })
  pagination.page = 1
  loadQuestions()
}

function handleSizeChange(size) {
  pagination.size = size
  pagination.page = 1
  loadQuestions()
}

function handleCurrentChange(page) {
  pagination.page = page
  loadQuestions()
}

function getQuestionTypeColor(type) {
  const colorMap = {
    'single': 'primary',
    'multiple': 'success',
    'fill': 'warning',
    'essay': 'info',
    'judge': 'danger'
  }
  return colorMap[type] || 'info'
}

function handleSelectionChange(selection) {
  selectedQuestions.value = selection
}

// 实时搜索防抖
let searchTimeout = null
function handleSearchInput() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    pagination.page = 1
    loadQuestions()
  }, 500) // 500ms防抖
}

// 处理学科变化
function handleSubjectChange(subjectId) {
  // 当学科变化时，清空分类选择
  if (filters.category_id) {
    // 检查当前选择的分类是否属于新选择的学科
    const currentCategory = categories.value.find(cat => cat.id === filters.category_id)
    if (!currentCategory || currentCategory.subject_id !== subjectId) {
      filters.category_id = null
    }
  }

  // 重新加载试题
  pagination.page = 1
  loadQuestions()
}

// 复制试题
async function copyQuestion(question) {
  try {
    await ElMessageBox.confirm(
      `确定要复制试题"${question.title}"吗？复制后将自动跳转到编辑页面。`,
      '复制试题确认',
      {
        confirmButtonText: '确认复制',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const copyLoading = ElMessage({
      message: '正在复制试题...',
      type: 'info',
      duration: 0
    })

    try {
      // 调用后端复制API
      const response = await api.post('/questions/batch/copy', {
        question_ids: [question.id],
        target_semester_id: question.semester_id,
        target_grade_id: question.grade_id,
        target_subject_id: question.subject_id,
        target_category_id: question.category_id
      })

      copyLoading.close()

      // 获取复制后的试题ID
      const copiedQuestionIds = response.data.copied_question_ids

      if (copiedQuestionIds && copiedQuestionIds.length > 0) {
        const copiedQuestionId = copiedQuestionIds[0]
        ElMessage.success('试题复制成功，正在跳转到编辑页面...')
        // 跳转到复制后试题的编辑页面
        setTimeout(() => {
          router.push(`/questions/edit/${copiedQuestionId}`)
        }, 500)
      } else {
        ElMessage.success('试题复制成功')
        loadQuestions() // 刷新列表
      }
    } catch (copyError) {
      copyLoading.close()
      console.error('复制试题失败:', copyError)
      const errorMessage = copyError.response?.data?.detail || copyError.message || '复制试题失败'
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('复制操作异常:', error)
      ElMessage.error('复制操作失败')
    }
  }
}

// 切换发布状态
async function togglePublishStatus(question) {
  try {
    const newStatus = !question.is_published
    const statusText = newStatus ? '发布' : '取消发布'

    await ElMessageBox.confirm(
      `确定要${statusText}试题"${question.title}"吗？`,
      `${statusText}确认`,
      {
        confirmButtonText: `确认${statusText}`,
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const updateLoading = ElMessage({
      message: `正在${statusText}试题...`,
      type: 'info',
      duration: 0
    })

    try {
      await api.put(`/questions/${question.id}`, {
        is_published: newStatus
      })

      updateLoading.close()
      ElMessage.success(`试题${statusText}成功`)

      // 更新本地数据
      question.is_published = newStatus
    } catch (updateError) {
      updateLoading.close()
      console.error(`${statusText}试题失败:`, updateError)
      const errorMessage = updateError.response?.data?.detail || updateError.message || `${statusText}试题失败`
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换发布状态异常:', error)
    }
  }
}

/**
 * 获取内容简介
 * @param text
 * @param length
 */
function getContentSummary(text, length = 30) {
  if (!text) return ''

  // 去掉HTML标签，只保留文字内容
  const cleanText = text.replace(/<[^>]+>/g, '')

  // 提取中文字符
  const chineseChars = cleanText.match(/[\u4e00-\u9fa5]/g)

  if (!chineseChars || chineseChars.length === 0) {
    // 如果没有中文字符，返回前length个字符
    return cleanText.length > length ? cleanText.substring(0, length) + '...' : cleanText
  }

  // 如果有中文字符，返回前length个中文字符
  const summary = chineseChars.slice(0, length).join('')
  return summary + (chineseChars.length > length ? '...' : '')
}

/**
 * 获取空状态描述
 */
function getEmptyDescription() {
  if (hasFilters.value) {
    return '没有找到符合条件的试题，请调整筛选条件'
  }
  return '暂无试题数据，点击下方按钮开始创建第一个试题'
}
</script>

<style scoped>
.filter-section {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.question-title {
  display: flex;
  align-items: center;
  gap: 8px;

}

.title-text {
  flex: 1;
  font-weight: 500;
  color: #2d3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type-tag {
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.content-summary {
  text-align: left;
}

.summary-text {
  margin: 0 0 8px 0;
  line-height: 1.4;
  color: #606266;
  font-size: 14px;
}

.content-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
}

:deep(.el-pagination .btn-next),
:deep(.el-pagination .btn-prev) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

:deep(.el-pagination .btn-next:hover),
:deep(.el-pagination .btn-prev:hover) {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

:deep(.el-pager li) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  margin: 0 4px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

:deep(.el-pager li:hover) {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

:deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.text-gray-400 {
  color: #9ca3af;
  font-size: 12px;
}

/* 表格行悬停效果 */
:deep(.el-table__row:hover) {
  background-color: rgba(102, 126, 234, 0.05) !important;
}

/* 表格头部样式 */
:deep(.el-table__header-wrapper) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

:deep(.el-table th) {
  background: transparent !important;
  font-weight: 600;
  color: #374151;
}

/* 标签样式优化 */
.type-tag {
  font-weight: 500;
  border-radius: 6px;
}

/* 操作按钮样式 */
.action-buttons .el-button {
  border-radius: 6px;
  transition: all 0.2s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 空状态样式 */
.empty-state {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 40px 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  text-align: center;
}

.empty-state :deep(.el-empty__description) {
  color: #6b7280;
  font-size: 16px;
  margin-bottom: 20px;
}

.empty-state :deep(.el-empty__image) {
  margin-bottom: 20px;
}
</style>
