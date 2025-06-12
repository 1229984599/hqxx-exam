<template>
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
        <el-col :span="8">
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
        <el-col :span="8">
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
        <el-col :span="8">
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
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
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
        <el-col :span="8">
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
        <el-col :span="8">
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
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="题目内容" prop="content">
            <TinyMCEEditor
              v-model="form.content"
              :height="400"
              :toolbar-mode="'wrap'"
              placeholder="请输入题目内容，支持富文本编辑和拼音注音"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="参考答案" prop="answer">
            <TinyMCEEditor
              v-model="form.answer"
              :height="200"
              placeholder="请输入参考答案（可选）"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="标签" prop="tags">
            <el-input
              v-model="form.tags"
              placeholder="请输入标签，多个标签用逗号分隔"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="状态设置">
            <div class="status-switches-horizontal">
              <div class="switch-item">
                <span class="switch-label">启用状态</span>
                <el-switch v-model="form.is_active" />
              </div>
              <div class="switch-item">
                <span class="switch-label">发布状态</span>
                <el-switch v-model="form.is_published" />
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <div class="form-actions">
        <el-button @click="handleCancel" size="large">
          取消
        </el-button>
        <el-button @click="handlePreview" :icon="View" size="large">
          预览
        </el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="saving"
          size="large"
        >
          {{ isEdit ? '更新' : '保存' }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { View } from '@element-plus/icons-vue'
import TinyMCEEditor from './TinyMCEEditor.vue'

const props = defineProps({
  form: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    required: true
  },
  semesters: {
    type: Array,
    default: () => []
  },
  grades: {
    type: Array,
    default: () => []
  },
  subjects: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  saving: {
    type: Boolean,
    default: false
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel', 'preview', 'subject-change'])

const formRef = ref()

// 根据选择的学科筛选分类
const filteredCategories = computed(() => {
  if (!props.form.subject_id) return []
  return props.categories.filter(cat => cat.subject_id === props.form.subject_id)
})

// 监听学科变化，清空分类选择
function onSubjectChange() {
  props.form.category_id = null
  emit('subject-change')
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    emit('submit')
  } catch (error) {
    // 验证失败
  }
}

function handleCancel() {
  emit('cancel')
}

function handlePreview() {
  emit('preview')
}

// 暴露表单引用给父组件
defineExpose({
  formRef,
  validate: () => formRef.value?.validate()
})
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
</style>
