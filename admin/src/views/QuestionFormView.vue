<template>
  <PageLayout
    :title="isEdit ? '编辑试题' : '添加试题'"
  >
    <QuestionForm
      ref="questionFormRef"
      :form="form"
      :rules="rules"
      :semesters="semesters"
      :grades="grades"
      :subjects="subjects"
      :categories="categories"
      :saving="saving"
      :is-edit="isEdit"
      @submit="saveQuestion"
      @cancel="handleCancel"
      @preview="handlePreview"
      @subject-change="onSubjectChange"
    />

    <!-- 预览对话框 -->
    <ContentPreview
      v-model="showPreview"
      title="试题预览"
      :content="form.content"
      content-label="题目内容"
      :header-title="form.title"
      :meta="previewMeta"
      :extra-info="previewExtraInfo"
      @close="handlePreviewClose"
    />
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../utils/api'
import { commonRules, getQuestionTypeText, getDifficultyText } from '../composables/useCrud'
import QuestionForm from '../components/QuestionForm.vue'
import ContentPreview from '../components/ContentPreview.vue'
import PageLayout from '../components/PageLayout.vue'

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const showPreview = ref(false)
const questionFormRef = ref()

const semesters = ref([])
const grades = ref([])
const subjects = ref([])
const categories = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  content: '',
  answer: '',
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
  title: commonRules.title,
  content: commonRules.content,
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

// 预览元数据
const previewMeta = computed(() => {
  const meta = []
  
  if (form.question_type) {
    meta.push({
      label: '题目类型',
      value: getQuestionTypeText(form.question_type),
      type: 'info'
    })
  }
  
  if (form.difficulty) {
    meta.push({
      label: '难度等级',
      value: getDifficultyText(form.difficulty),
      type: 'warning'
    })
  }
  
  const semester = semesters.value.find(s => s.id === form.semester_id)
  if (semester) {
    meta.push({
      label: '学期',
      value: semester.name,
      type: 'success'
    })
  }
  
  const grade = grades.value.find(g => g.id === form.grade_id)
  if (grade) {
    meta.push({
      label: '年级',
      value: grade.name,
      type: 'success'
    })
  }
  
  const subject = subjects.value.find(s => s.id === form.subject_id)
  if (subject) {
    meta.push({
      label: '学科',
      value: subject.name,
      type: 'primary'
    })
  }
  
  return meta
})

// 预览额外信息
const previewExtraInfo = computed(() => {
  const info = {}
  
  if (form.answer && form.answer.trim()) {
    info.answer = {
      label: '参考答案',
      content: form.answer
    }
  }
  
  if (form.tags && form.tags.trim()) {
    const tags = (form.tags || '').split(',').map(tag => tag.trim()).filter(Boolean)
    if (tags.length > 0) {
      info.tags = {
        label: '标签',
        content: tags.map(tag => `<span class="tag">${tag}</span>`).join(' ')
      }
    }
  }
  
  return Object.keys(info).length > 0 ? info : null
})

onMounted(() => {
  loadBasicData()
  if (isEdit.value) {
    loadQuestion()
  }
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

async function loadQuestion() {
  try {
    const response = await api.get(`/questions/${route.params.id}`)
    const question = response.data
    
    Object.assign(form, {
      title: question.title,
      content: question.content,
      answer: question.answer || '',
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
  } catch (error) {
    ElMessage.error('加载试题数据失败')
    router.push('/questions')
  }
}

async function saveQuestion() {
  try {
    saving.value = true

    if (isEdit.value) {
      await api.put(`/questions/${route.params.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/questions/', form)
      ElMessage.success('添加成功')
    }

    router.push('/questions')
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
  }
}

function onSubjectChange() {
  form.category_id = null
}

function handleCancel() {
  router.push('/questions')
}

function handlePreview() {
  if (!form.content.trim()) {
    ElMessage.warning('请先输入题目内容')
    return
  }
  showPreview.value = true
}

function handlePreviewClose() {
  showPreview.value = false
}
</script>

<style scoped>
/* 预览相关样式可以移到ContentPreview组件中 */
:deep(.tag) {
  display: inline-block;
  padding: 2px 8px;
  margin: 2px;
  background: #f0f2f5;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}
</style>
