<template>
  <PageLayout
    title="试题管理"
    subtitle="创建和管理考试题目，支持富文本编辑和注音功能"
  >
    <template #actions>
      <el-button
        type="primary"
        @click="$router.push('/questions/add')"
        :icon="Plus"
        size="large"
      >
        添加试题
      </el-button>
    </template>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item>
          <el-button
            type="primary"
            @click="$router.push('/questions/add')"
            :icon="Plus"
            size="default"
          >
            添加试题
          </el-button>
        </el-form-item>

        <el-form-item label="学期">
          <el-select v-model="filters.semester_id" placeholder="请选择学期" clearable @change="loadQuestions" style="width: 150px">
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="年级">
          <el-select v-model="filters.grade_id" placeholder="请选择年级" clearable @change="loadQuestions" style="width: 150px">
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="学科">
          <el-select v-model="filters.subject_id" placeholder="请选择学科" clearable @change="loadQuestions" style="width: 150px">
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="搜索题目标题"
            clearable
            style="width: 200px"
            @keyup.enter="loadQuestions"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadQuestions" :icon="Search">
            搜索
          </el-button>
          <el-button @click="resetFilters" :icon="Refresh">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 数据表格 -->
    <el-table :data="questions" v-loading="loading" class="modern-table">
      <el-table-column prop="title" label="题目标题"  min-width="150">
        <template #default="{ row }">
          <div class="question-title">
            <span class="title-text">{{ row.title }}</span>

          </div>
        </template>
      </el-table-column>
      <el-table-column prop="question_type" label="题目类型"  width="150">
        <template #default="{ row }">
          <el-tag v-if="row.question_type" size="small" class="type-tag">
              {{ getQuestionTypeText(row.question_type) }}
            </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="semester.name" label="学期" align="center" width="150">
        <template #default="{ row }">
          <el-tag v-if="row.semester" type="info" size="small">
            {{ row.semester.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="grade.name" label="年级" align="center" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.grade" type="primary" size="small">
            {{ row.grade.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="subject.name" label="学科" align="center" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.subject" type="success" size="small">
            {{ row.subject.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category.name" label="分类" align="center" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.category" type="warning" size="small">
            {{ row.category.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="difficulty" label="难度" align="center" width="100">
        <template #default="{ row }">
          <el-tag :type="getDifficultyType(row.difficulty)" size="small">
            {{ getDifficultyText(row.difficulty) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_published" align="center" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'warning'" size="small">
            {{ row.is_published ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" align="center" label="查看次数" width="120" />
      <el-table-column label="操作" align="center" width="160" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" @click="$router.push(`/questions/edit/${row.id}`)" :icon="Edit" />
            <el-button
              size="small"
              type="danger"
              @click="deleteQuestion(row)"
              :icon="Delete"
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
        @size-change="loadQuestions"
        @current-change="loadQuestions"
      />
    </div>

  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)

const questions = ref([])
const semesters = ref([])
const grades = ref([])
const subjects = ref([])
const categories = ref([])

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const filters = reactive({
  semester_id: null,
  grade_id: null,
  subject_id: null,
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
      api.get('/categories/')
    ])

    semesters.value = semestersRes.data
    grades.value = gradesRes.data
    subjects.value = subjectsRes.data
    categories.value = categoriesRes.data
  } catch (error) {
    ElMessage.error('加载基础数据失败')
  }
}

async function loadQuestions() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      ...filters
    }

    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '') {
        delete params[key]
      }
    })

    const response = await api.get('/questions/', { params })
    questions.value = response.data
    pagination.total = response.data.length
  } catch (error) {
    ElMessage.error('加载试题列表失败')
  } finally {
    loading.value = false
  }
}



async function deleteQuestion(question) {
  try {
    await ElMessageBox.confirm(`确定要删除试题"${question.title}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/questions/${question.id}`)
    ElMessage.success('删除成功')
    loadQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function resetFilters() {
  Object.assign(filters, {
    semester_id: null,
    grade_id: null,
    subject_id: null,
    search: ''
  })
  pagination.page = 1
  loadQuestions()
}

function getDifficultyText(difficulty) {
  const map = { 1: '简单', 2: '较易', 3: '中等', 4: '较难', 5: '困难' }
  return map[difficulty] || '未知'
}

function getDifficultyType(difficulty) {
  const map = { 1: 'success', 2: 'info', 3: 'warning', 4: 'danger', 5: 'danger' }
  return map[difficulty] || 'info'
}

function getQuestionTypeText(type) {
  const map = {
    'single': '单选题',
    'multiple': '多选题',
    'fill': '填空题',
    'essay': '问答题',
    'judge': '判断题'
  }
  return map[type] || type
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
}

.type-tag {
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
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


</style>
