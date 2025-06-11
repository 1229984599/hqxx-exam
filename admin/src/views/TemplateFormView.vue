<template>
  <PageLayout :title="isEdit ? '编辑模板' : '添加模板'">
    <div class="template-form-container">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        size="large"
      >
        <el-row :gutter="32">
          <el-col :span="16">
            <el-form-item label="模板名称" prop="name">
              <el-input
                v-model="form.name"
                placeholder="请输入模板名称"
                maxlength="100"
                show-word-limit
                size="large"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="模板图标" prop="icon">
              <el-input
                v-model="form.icon"
                placeholder="请输入emoji图标，如：📝"
                maxlength="20"
                size="large"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="32">
          <el-col :span="6">
            <el-form-item label="适用学科" prop="subject_id">
              <el-select
                v-model="form.subject_id"
                placeholder="选择学科"
                clearable
                style="width: 100%"
                @change="handleSubjectChange"
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
            <el-form-item label="模板类型" prop="category">
              <el-select v-model="form.category" placeholder="选择类型" style="width: 100%">
                <el-option label="练习模板" value="练习模板" />
                <el-option label="测试模板" value="测试模板" />
                <el-option label="作业模板" value="作业模板" />
                <el-option label="教学模板" value="教学模板" />
                <el-option label="通用模板" value="通用模板" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="排序">
              <div class="setting-item">
                  <el-input-number
                    v-model="form.sort_order"
                    :min="0"
                    :max="999"
                    size="small"
                    style="width: 80px"
                  />
                </div>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="状态">
              <div class="setting-item" >
                  <el-switch
                    v-model="form.is_active"
                    active-text="启用"
                    inactive-text="禁用"
                    size="small"
                    style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
                  />
                </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="模板描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="模板内容" prop="content">
          <div class="editor-container">
            <TinyMCEEditor
              v-model="form.content"
              placeholder="请输入模板内容，支持富文本编辑"
              :height="800"
              :show-pinyin-tools="true"
              :show-word-count="false"
              :toolbar-mode="'wrap'"
            />
          </div>
        </el-form-item>

        <el-row v-if="isEdit && form.is_system" :gutter="32">
          <el-col :span="24">
            <el-form-item label="系统模板">
              <el-tag type="warning" size="large">
                <el-icon style="margin-right: 4px;"><Warning /></el-icon>
                此模板为系统模板，请谨慎修改
              </el-tag>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <div class="form-actions">
            <el-button @click="handlePreview" :icon="View">预览</el-button>
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              {{ isEdit ? '更新' : '创建' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreview"
      title="模板预览"
      width="90%"
      :append-to-body="true"
      class="preview-dialog"
      top="5vh"
    >
      <div class="preview-container">
        <div class="preview-header">
          <h3>{{ form.name || '未命名模板' }}</h3>
          <div class="preview-meta">
            <el-tag size="small" type="primary">{{ form.category || '未分类' }}</el-tag>
            <el-tag v-if="getSubjectName()" size="small" type="info">{{ getSubjectName() }}</el-tag>
          </div>
        </div>
        <div class="preview-content" v-html="processPreviewContent(form.content)"></div>
      </div>
      <template #footer>
        <el-button @click="showPreview = false">关闭</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Warning } from '@element-plus/icons-vue'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'
import TinyMCEEditor from '../components/TinyMCEEditor.vue'

const route = useRoute()
const router = useRouter()

const formRef = ref()
const subjects = ref([])
const submitting = ref(false)
const showPreview = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  description: '',
  content: '',
  category: '',
  icon: '',
  subject_id: null,
  is_active: true,
  sort_order: 0
})

const rules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择模板分类', trigger: 'change' }
  ]
}

onMounted(() => {
  loadSubjects()
  if (isEdit.value) {
    loadTemplate()
  }
})

async function loadSubjects() {
  try {
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    console.error('加载学科失败:', error)
  }
}

async function loadTemplate() {
  try {
    const response = await api.get(`/templates/${route.params.id}`)
    const template = response.data
    
    Object.assign(form, {
      name: template.name,
      description: template.description || '',
      content: template.content,
      category: template.category,
      icon: template.icon || '',
      subject_id: template.subject_id,
      is_active: template.is_active,
      sort_order: template.sort_order,
      is_system: template.is_system
    })
  } catch (error) {
    ElMessage.error('加载模板失败')
    router.push('/templates')
  }
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const submitData = { ...form }
    delete submitData.is_system // 不提交系统模板标识
    
    if (isEdit.value) {
      await api.put(`/templates/${route.params.id}`, submitData)
      ElMessage.success('模板更新成功')
    } else {
      await api.post('/templates/', submitData)
      ElMessage.success('模板创建成功')
    }
    
    router.push('/templates')
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  router.push('/templates')
}

function handlePreview() {
  if (!form.content.trim()) {
    ElMessage.warning('请先输入模板内容')
    return
  }
  showPreview.value = true
}

function getSubjectName() {
  if (!form.subject_id) return ''
  const subject = subjects.value.find(s => s.id === form.subject_id)
  return subject?.name || ''
}

function handleSubjectChange(subjectId) {
  // 当选择学科时，可以自动设置一些默认值
  if (subjectId && !form.category) {
    // 根据学科自动推荐模板类型
    const subject = subjects.value.find(s => s.id === subjectId)
    if (subject) {
      // 可以根据学科特点设置默认类型
      if (subject.name.includes('语文') || subject.name.includes('英语')) {
        form.category = '教学模板'
      } else if (subject.name.includes('数学') || subject.name.includes('物理')) {
        form.category = '练习模板'
      } else {
        form.category = '通用模板'
      }
    }
  }
}

function processPreviewContent(content) {
  if (!content) return ''
  
  // 处理拼音注音的显示
  return content.replace(
    /<ruby class="pinyin-ruby"[^>]*>(.*?)<rt[^>]*>(.*?)<\/rt><\/ruby>/g,
    '<ruby class="pinyin-ruby" style="background: rgba(64, 158, 255, 0.1); border-radius: 4px; padding: 2px 4px; margin: 0 2px;">$1<rt style="color: #409eff; font-size: 0.75em; font-weight: 500;">$2</rt></ruby>'
  )
}
</script>

<style scoped>
.template-form-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 40px;
}

/* 表单样式优化 */
.el-form {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f0f0;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-form-item__label {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

/* 输入框样式优化 */
.el-input__wrapper {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px #409eff;
}

.el-textarea__inner {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.el-select .el-input__wrapper {
  border-radius: 8px;
}

/* 表单设置区域样式 */
.form-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-label {
  font-size: 13px;
  color: #606266;
  min-width: 40px;
  font-weight: 500;
}

/* 富文本编辑器容器优化 */
.editor-container {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.el-form-item:has(.editor-container) {
  margin-bottom: 32px;
}

/* 响应式优化 */
@media (max-width: 1400px) {
  .template-form-container {
    max-width: 1200px;
    padding: 0 24px;
  }

  .el-form {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .template-form-container {
    padding: 0 16px;
  }

  .el-form {
    padding: 20px;
    border-radius: 8px;
  }

  .el-form-item {
    margin-bottom: 20px;
  }

  /* 移动端表单布局调整 */
  .el-row .el-col {
    margin-bottom: 0;
  }

  /* 在小屏幕上将多列布局改为单列 */
  .el-row[gutter="32"] .el-col:not(:last-child) {
    margin-bottom: 16px;
  }
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 预览对话框样式 */
.preview-dialog {
  max-width: 1400px;
}

.preview-dialog .el-dialog__body {
  padding: 24px;
}

.preview-container {
  max-height: 75vh;
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

.preview-content {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-height: 200px;
  line-height: 1.6;
}

/* 预览内容中的拼音样式 */
.preview-content :deep(ruby.pinyin-ruby) {
  background: rgba(64, 158, 255, 0.1) !important;
  border-radius: 4px !important;
  padding: 2px 4px !important;
  margin: 0 2px !important;
}

.preview-content :deep(rt) {
  color: #409eff !important;
  font-size: 0.75em !important;
  font-weight: 500 !important;
}
</style>
