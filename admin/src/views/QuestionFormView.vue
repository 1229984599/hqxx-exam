<template>
  <PageLayout
    :title="isEdit ? '编辑试题' : '添加试题'"
  >
    <div class="question-form-container">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        size="large"
      >
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="题目标题" prop="title">
                <el-input
                  v-model="form.title"
                  placeholder="请输入题目标题"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="学期" prop="semester_id">
                <el-select v-model="form.semester_id" placeholder="请选择学期" style="width: 100%">
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
                <el-select v-model="form.grade_id" placeholder="请选择年级" style="width: 100%">
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
                <el-select
                  v-model="form.subject_id"
                  placeholder="请选择学科"
                  style="width: 100%"
                  @change="onSubjectChange"
                >
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
                <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
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
            <el-col :span="6">
              <el-form-item label="题目类型" prop="question_type">
                <el-select v-model="form.question_type" placeholder="请选择题目类型" style="width: 100%">
                  <el-option label="单选题" value="single" />
                  <el-option label="多选题" value="multiple" />
                  <el-option label="填空题" value="fill" />
                  <el-option label="问答题" value="essay" />
                  <el-option label="判断题" value="judge" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="难度等级" prop="difficulty">
                <el-select v-model="form.difficulty" placeholder="请选择难度" style="width: 100%">
                  <el-option label="简单" :value="1" />
                  <el-option label="较易" :value="2" />
                  <el-option label="中等" :value="3" />
                  <el-option label="较难" :value="4" />
                  <el-option label="困难" :value="5" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="状态设置">
                <div class="status-switches-horizontal">
                  <div class="switch-item">
                    <span class="switch-label">是否发布</span>
                    <el-switch v-model="form.is_published" />
                  </div>
                  <div class="switch-item">
                    <span class="switch-label">是否激活</span>
                    <el-switch v-model="form.is_active" />
                  </div>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="题目内容" prop="content">
            <TinyMCEEditor
              v-model="form.content"
              placeholder="请输入题目内容，支持富文本编辑和注音功能"
              :height="500"
              :show-pinyin-tools="true"
              :show-word-count="false"
            />
          </el-form-item>

          <el-form-item label="参考答案" prop="answer">
            <TinyMCEEditor
              v-model="form.answer"
              placeholder="请输入参考答案，支持富文本编辑和注音功能"
              :height="300"
              :show-pinyin-tools="true"
              :show-word-count="false"
            />
          </el-form-item>

          <el-form-item label="标签">
            <el-input
              v-model="form.tags"
              placeholder="请输入标签，多个标签用逗号分隔"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <div class="form-actions">
              <el-button size="large" @click="handleCancel">取消</el-button>
              <el-button size="large" @click="showPreview = true" :icon="View">预览</el-button>
              <el-button type="primary" size="large" @click="saveQuestion" :loading="saving">
                {{ isEdit ? '更新' : '保存' }}
              </el-button>
            </div>
          </el-form-item>
        </el-form>
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreview"
      title="试题预览"
      width="80%"
      :before-close="handlePreviewClose"
      class="preview-dialog"
      :append-to-body="true"

    >
      <div class="preview-container">
        <div class="preview-header">
          <h3>{{ form.title || '未设置标题' }}</h3>
          <div class="preview-meta">
            <el-tag v-if="form.question_type" type="primary">{{ getQuestionTypeText(form.question_type) }}</el-tag>
            <el-tag v-if="form.difficulty" type="warning">{{ getDifficultyText(form.difficulty) }}</el-tag>
          </div>
        </div>

        <div class="preview-content">
          <h4>题目内容：</h4>
          <div class="content-preview" v-html="processPreviewContent(form.content)"></div>
        </div>

        <div class="preview-answer" v-if="form.answer">
          <h4>参考答案：</h4>
          <div class="answer-preview" v-html="processPreviewContent(form.answer)"></div>
        </div>

        <div class="preview-info" v-if="form.tags">
          <h4>标签：</h4>
          <div class="tags-preview">
            <el-tag
              v-for="tag in form.tags.split(',')"
              :key="tag.trim()"
              size="small"
              style="margin-right: 8px;"
            >
              {{ tag.trim() }}
            </el-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showPreview = false">关闭</el-button>
        <el-button type="primary" @click="copyPreviewContent">复制内容</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import api from '../utils/api'
import TinyMCEEditor from '../components/TinyMCEEditor.vue'
import PageLayout from '../components/PageLayout.vue'

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const formRef = ref()
const showPreview = ref(false)

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
  title: [
    { required: true, message: '请输入题目标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ],
  answer: [
    { required: true, message: '请输入参考答案', trigger: 'blur' }
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
  if (!formRef.value) return

  try {
    await formRef.value.validate()
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

function handlePreviewClose() {
  showPreview.value = false
}

function getQuestionTypeText(type) {
  const types = {
    'single': '单选题',
    'multiple': '多选题',
    'fill': '填空题',
    'essay': '问答题',
    'judge': '判断题'
  }
  return types[type] || type
}

function getDifficultyText(difficulty) {
  const difficulties = {
    1: '简单',
    2: '较易',
    3: '中等',
    4: '较难',
    5: '困难'
  }
  return difficulties[difficulty] || difficulty
}

function processPreviewContent(content) {
  if (!content) return ''

  console.log('原始内容:', content)

  // 确保所有 ruby 标签都有正确的 class 和内联样式
  let processedContent = content.replace(/<ruby(?![^>]*class=)/g, '<ruby class="pinyin-ruby"')

  // 确保 rt 和 rb 标签的顺序正确（rt 在前，rb 在后）
  processedContent = processedContent.replace(
    /<ruby([^>]*)><rb([^>]*)>(.*?)<\/rb><rt([^>]*)>(.*?)<\/rt><\/ruby>/g,
    '<ruby$1><rt$4>$5</rt><rb$2>$3</rb></ruby>'
  )

  // 处理可能存在的其他格式问题
  processedContent = processedContent.replace(
    /<ruby([^>]*)class="pinyin-ruby"([^>]*)><rb([^>]*)>(.*?)<\/rb><rt([^>]*)>(.*?)<\/rt><\/ruby>/g,
    '<ruby$1class="pinyin-ruby"$2><rt$5>$6</rt><rb$3>$4</rb></ruby>'
  )

  // 添加内联样式确保样式生效
  processedContent = processedContent.replace(
    /<ruby([^>]*)class="pinyin-ruby"([^>]*)>/g,
    '<ruby$1class="pinyin-ruby"$2 style="ruby-align: center; display: inline-block; white-space: nowrap; margin: 0 2px; vertical-align: baseline; line-height: 2.2; position: relative; background: rgba(64, 158, 255, 0.05); border-radius: 4px; padding: 3px 2px 1px 2px; cursor: pointer;">'
  )

  processedContent = processedContent.replace(
    /<rt([^>]*)>/g,
    '<rt$1 style="font-size: 0.75em; color: #409eff; font-weight: 500; display: block; text-align: center; line-height: 1.2; margin-bottom: 3px; user-select: none; min-width: 1em; padding: 0 1px; position: relative; z-index: 1;">'
  )

  processedContent = processedContent.replace(
    /<rb([^>]*)>/g,
    '<rb$1 style="display: block; text-align: center; user-select: text; font-size: 1em; line-height: 1.4; position: relative; z-index: 1;">'
  )

  console.log('处理后内容:', processedContent)

  return processedContent
}

function copyPreviewContent() {
  try {
    // 创建一个临时的 div 来获取纯文本内容
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = form.content
    const textContent = tempDiv.textContent || tempDiv.innerText || ''

    // 复制到剪贴板
    navigator.clipboard.writeText(form.content).then(() => {
      ElMessage.success('内容已复制到剪贴板')
    }).catch(() => {
      // 降级方案
      const textArea = document.createElement('textarea')
      textArea.value = form.content
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      ElMessage.success('内容已复制到剪贴板')
    })
  } catch (error) {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.question-form-container {
  width: 100%;
  margin: 0;
  padding: 0 24px;
}



.status-switches-horizontal {
  display: flex;
  align-items: center;
  gap: 30px;
}

.switch-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.switch-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #4a5568;
}

:deep(.el-input__inner) {
  border-radius: 8px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
}

/* 滚动条样式优化 - 与主题融合 */
:deep(*::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(*::-webkit-scrollbar-track) {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 4px;
}

:deep(*::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
}

:deep(*::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
  transform: scale(1.1);
}

:deep(*::-webkit-scrollbar-corner) {
  background: rgba(102, 126, 234, 0.05);
}

/* TinyMCE 编辑器滚动条特殊处理 */
:deep(.tox-edit-area__iframe::-webkit-scrollbar) {
  width: 8px;
}

:deep(.tox-edit-area__iframe::-webkit-scrollbar-track) {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 4px;
}

:deep(.tox-edit-area__iframe::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-radius: 4px;
}

:deep(.tox-edit-area__iframe::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
}

/* 预览对话框样式 */
.preview-container {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.preview-meta {
  display: flex;
  gap: 10px;
}

.preview-content {
  margin-bottom: 20px;
}

.preview-content h4,
.preview-info h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.content-preview {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  min-height: 100px;
  line-height: 1.8;
}

/* 预览内容中的 Ruby 标签样式 - 与编辑器保持一致，使用更高优先级 */
:deep(.content-preview ruby) {
  ruby-align: center !important;
  display: inline-block !important;
  white-space: nowrap !important;
  margin: 0 2px !important;
  vertical-align: baseline !important;
  line-height: 2.2 !important;
  position: relative !important;
}

:deep(.content-preview ruby.pinyin-ruby) {
  border-radius: 4px !important;
  padding: 3px 2px 1px 2px !important;
  cursor: pointer !important;
  position: relative !important;
  transition: background-color 0.2s ease !important;
}

:deep(.content-preview ruby.pinyin-ruby:hover) {
  background: rgba(64, 158, 255, 0.1) !important;
}

:deep(.content-preview rt) {
  font-size: 0.75em !important;
  color: #409eff !important;
  font-weight: 500 !important;
  display: block !important;
  text-align: center !important;
  line-height: 1.1 !important;
  margin-bottom: 2px !important;
  user-select: none !important;
  min-width: 1em !important;
  padding: 0 1px !important;
  position: relative !important;
  z-index: 1 !important;
}

:deep(.content-preview rb) {
/*  border-bottom: 1px dotted #409eff !important;*/
  display: block !important;
  text-align: center !important;
  user-select: text !important;
  font-size: 1em !important;
  line-height: 1.4 !important;
  position: relative !important;
  z-index: 1 !important;
}

/* 确保非拼音的 ruby 标签不受影响 */
:deep(.content-preview ruby:not(.pinyin-ruby)) {
  background: transparent !important;
  padding: 0 !important;
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 预览对话框全局样式 */
:deep(.preview-dialog .el-dialog__body) {
  /* 确保对话框内的 Ruby 标签样式正确应用 */
}

:deep(.preview-dialog ruby) {
  ruby-align: center !important;
  display: inline-block !important;
  white-space: nowrap !important;
  margin: 0 2px !important;
  vertical-align: baseline !important;
  line-height: 2.2 !important;
  position: relative !important;
}

:deep(.preview-dialog ruby.pinyin-ruby) {
  border-radius: 4px !important;
  padding: 3px 2px 1px 2px !important;
  cursor: pointer !important;
  position: relative !important;
  transition: background-color 0.2s ease !important;
}

:deep(.preview-dialog ruby.pinyin-ruby:hover) {
  background: rgba(64, 158, 255, 0.1) !important;
}

:deep(.preview-dialog rt) {
  font-size: 0.75em !important;
  color: #409eff !important;
  font-weight: 500 !important;
  display: block !important;
  text-align: center !important;
  line-height: 1.2 !important;
  margin-bottom: 3px !important;
  user-select: none !important;
  min-width: 1em !important;
  padding: 0 1px !important;
  position: relative !important;
  z-index: 1 !important;
}

:deep(.preview-dialog rb) {
  display: block !important;
  text-align: center !important;
  user-select: text !important;
  font-size: 1em !important;
  line-height: 1.4 !important;
  position: relative !important;
  z-index: 1 !important;
}

:deep(.preview-dialog ruby:not(.pinyin-ruby)) {
  background: transparent !important;
  padding: 0 !important;
}

/* 预览对话框样式 */
.preview-container {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
}

.preview-meta {
  display: flex;
  gap: 10px;
}

.preview-content,
.preview-answer {
  margin-bottom: 20px;
}

.preview-content h4,
.preview-answer h4,
.preview-info h4 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-size: 14px;
  font-weight: 600;
}

.content-preview,
.answer-preview {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-height: 50px;
  line-height: 1.6;
}

.answer-preview {
  background: #f0f9ff;
  border-color: #bfdbfe;
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
