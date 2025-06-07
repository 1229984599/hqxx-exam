<template>
  <PageLayout
    title="试题管理"
    subtitle="创建和管理考试题目，支持富文本编辑和注音功能"
  >
    <template #actions>
      <el-button
        type="primary"
        @click="showAddDialog = true"
        :icon="Plus"
        size="large"
      >
        添加试题
      </el-button>
    </template>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
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
      <el-table-column prop="title" label="题目标题" min-width="250">
        <template #default="{ row }">
          <div class="question-title">
            <span class="title-text">{{ row.title }}</span>
            <el-tag v-if="row.question_type" size="small" class="type-tag">
              {{ getQuestionTypeText(row.question_type) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="semester.name" label="学期" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.semester" type="info" size="small">
            {{ row.semester.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="grade.name" label="年级" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.grade" type="primary" size="small">
            {{ row.grade.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="subject.name" label="学科" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.subject" type="success" size="small">
            {{ row.subject.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category.name" label="分类" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.category" type="warning" size="small">
            {{ row.category.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="difficulty" label="难度" width="80">
        <template #default="{ row }">
          <el-tag :type="getDifficultyType(row.difficulty)" size="small">
            {{ getDifficultyText(row.difficulty) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_published" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'warning'" size="small">
            {{ row.is_published ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="查看次数" width="100" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" @click="editQuestion(row)" :icon="Edit" />
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
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingId ? '编辑试题' : '添加试题'"
      fullscreen
      :before-close="handleDialogClose"
      :append-to-body="true"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="题目标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入题目标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="题目类型" prop="question_type">
              <el-select v-model="form.question_type" placeholder="请选择题目类型">
                <el-option label="单选题" value="single" />
                <el-option label="多选题" value="multiple" />
                <el-option label="填空题" value="fill" />
                <el-option label="问答题" value="essay" />
                <el-option label="判断题" value="judge" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="学期" prop="semester_id">
              <el-select v-model="form.semester_id" placeholder="请选择学期">
                <el-option
                  v-for="semester in semesters"
                  :key="semester.id"
                  :label="semester.name"
                  :value="semester.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="年级" prop="grade_id">
              <el-select v-model="form.grade_id" placeholder="请选择年级">
                <el-option
                  v-for="grade in grades"
                  :key="grade.id"
                  :label="grade.name"
                  :value="grade.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="学科" prop="subject_id">
              <el-select v-model="form.subject_id" placeholder="请选择学科" @change="onSubjectChange">
                <el-option
                  v-for="subject in subjects"
                  :key="subject.id"
                  :label="subject.name"
                  :value="subject.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="分类" prop="category_id">
              <el-select v-model="form.category_id" placeholder="请选择分类">
                <el-option
                  v-for="category in filteredCategories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="难度等级" prop="difficulty">
              <el-select v-model="form.difficulty" placeholder="请选择难度">
                <el-option label="简单" :value="1" />
                <el-option label="较易" :value="2" />
                <el-option label="中等" :value="3" />
                <el-option label="较难" :value="4" />
                <el-option label="困难" :value="5" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否发布" prop="is_published">
              <el-switch v-model="form.is_published" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否激活" prop="is_active">
              <el-switch v-model="form.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="题目内容" prop="content">
          <RichTextEditor
            v-model="form.content"
            placeholder="请输入题目内容，支持富文本编辑和注音功能"
            height="500px"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input
            v-model="form.tags"
            placeholder="请输入标签，多个标签用逗号分隔"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="saveQuestion" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import RichTextEditor from '../components/RichTextEditor.vue'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingId = ref(null)
const formRef = ref()

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

const form = reactive({
  title: '',
  content: '',
  difficulty: 1,
  question_type: 'single',
  semester_id: null,
  grade_id: null,
  subject_id: null,
  category_id: null,
  is_active: true,
  is_published: false,
  tags: ''
})

const rules = {
  title: [
    { required: true, message: '请输入题目标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ],
  semester_id: [
    { required: true, message: '请选择学期', trigger: 'change' }
  ],
  grade_id: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  subject_id: [
    { required: true, message: '请选择学科', trigger: 'change' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

const filteredCategories = computed(() => {
  if (!form.subject_id) return []
  return categories.value.filter(cat => cat.subject_id === form.subject_id)
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

function editQuestion(question) {
  editingId.value = question.id
  Object.assign(form, {
    title: question.title,
    content: question.content,
    difficulty: question.difficulty,
    question_type: question.question_type,
    semester_id: question.semester_id,
    grade_id: question.grade_id,
    subject_id: question.subject_id,
    category_id: question.category_id,
    is_active: question.is_active,
    is_published: question.is_published,
    tags: question.tags || ''
  })
  showAddDialog.value = true
}

async function saveQuestion() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    if (editingId.value) {
      await api.put(`/questions/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/questions/', form)
      ElMessage.success('添加成功')
    }

    showAddDialog.value = false
    resetForm()
    loadQuestions()
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
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

function onSubjectChange() {
  form.category_id = null
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

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    title: '',
    content: '',
    difficulty: 1,
    question_type: 'single',
    semester_id: null,
    grade_id: null,
    subject_id: null,
    category_id: null,
    is_active: true,
    is_published: false,
    tags: ''
  })
  formRef.value?.resetFields()
}

function handleDialogClose() {
  showAddDialog.value = false
  resetForm()
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

/* 全屏对话框样式优化 */
:deep(.el-dialog.is-fullscreen) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  max-height: none !important;
  top: 0 !important;
  left: 0 !important;
  position: fixed !important;
  z-index: 2000 !important;
}

:deep(.el-dialog.is-fullscreen .el-dialog__header) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 30px;
  margin: 0;
}

:deep(.el-dialog.is-fullscreen .el-dialog__title) {
  color: #2d3748;
  font-size: 24px;
  font-weight: 700;
}

:deep(.el-dialog.is-fullscreen .el-dialog__body) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 30px;
  height: calc(100vh - 140px);
  overflow-y: auto;
  margin: 0;
}

:deep(.el-dialog.is-fullscreen .el-dialog__footer) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 30px;
  text-align: right;
  margin: 0;
}

/* 确保对话框遮罩层覆盖整个屏幕 */
:deep(.el-overlay) {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 1999 !important;
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

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #4a5568;
}

:deep(.el-dialog) {
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  text-align: right;
}
</style>
