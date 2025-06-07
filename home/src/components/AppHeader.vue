<template>
  <header class="app-header">
    <div class="header-content">
      <!-- 左侧Logo -->
      <div class="logo-section">
        <img src="E:/code/hqxx-exam/logo.png" alt="红旗小学" class="logo" />
        <h1 class="title">红旗小学无纸化测试</h1>
      </div>
      
      <!-- 右侧设置按钮 -->
      <div class="actions">
        <el-button 
          type="primary" 
          :icon="Setting" 
          @click="showSettings = true"
          round
        >
          设置
        </el-button>
      </div>
    </div>
    
    <!-- 设置弹窗 -->
    <el-dialog
      v-model="showSettings"
      title="考试设置"
      width="500px"
      :before-close="handleClose"
    >
      <div class="settings-content">
        <el-form :model="settingsForm" label-width="80px">
          <el-form-item label="学期">
            <el-select 
              v-model="settingsForm.semester" 
              placeholder="请选择学期"
              style="width: 100%"
            >
              <el-option
                v-for="semester in examStore.semesters"
                :key="semester.id"
                :label="semester.name"
                :value="semester"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="年级">
            <el-select 
              v-model="settingsForm.grade" 
              placeholder="请选择年级"
              style="width: 100%"
            >
              <el-option
                v-for="grade in examStore.grades"
                :key="grade.id"
                :label="grade.name"
                :value="grade"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="学科">
            <el-select 
              v-model="settingsForm.subject" 
              placeholder="请选择学科"
              style="width: 100%"
              @change="onSubjectChange"
            >
              <el-option
                v-for="subject in examStore.subjects"
                :key="subject.id"
                :label="subject.name"
                :value="subject"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="题目分类">
            <el-select 
              v-model="settingsForm.category" 
              placeholder="请选择题目分类"
              style="width: 100%"
            >
              <el-option
                v-for="category in examStore.filteredCategories"
                :key="category.id"
                :label="category.name"
                :value="category"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSettings = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </header>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Setting } from '@element-plus/icons-vue'
import { useExamStore } from '../stores/exam'
import { ElMessage } from 'element-plus'

const examStore = useExamStore()
const showSettings = ref(false)

const settingsForm = reactive({
  semester: null,
  grade: null,
  subject: null,
  category: null
})

onMounted(async () => {
  // 加载基础数据
  await Promise.all([
    examStore.loadSemesters(),
    examStore.loadGrades(),
    examStore.loadSubjects(),
    examStore.loadCategories()
  ])
  
  // 初始化表单数据
  settingsForm.semester = examStore.selectedSemester
  settingsForm.grade = examStore.selectedGrade
  settingsForm.subject = examStore.selectedSubject
  settingsForm.category = examStore.selectedCategory
})

function onSubjectChange() {
  // 清空分类选择
  settingsForm.category = null
}

function saveSettings() {
  if (!settingsForm.semester || !settingsForm.grade || !settingsForm.subject || !settingsForm.category) {
    ElMessage.warning('请完整选择所有选项')
    return
  }
  
  // 更新store中的选择
  examStore.selectedSemester = settingsForm.semester
  examStore.selectedGrade = settingsForm.grade
  examStore.selectedSubject = settingsForm.subject
  examStore.selectedCategory = settingsForm.category
  
  // 重置题目
  examStore.resetQuestions()
  
  showSettings.value = false
  ElMessage.success('设置已保存')
}

function handleClose() {
  // 恢复原始值
  settingsForm.semester = examStore.selectedSemester
  settingsForm.grade = examStore.selectedGrade
  settingsForm.subject = examStore.selectedSubject
  settingsForm.category = examStore.selectedCategory
  
  showSettings.value = false
}
</script>

<style scoped>
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  width: 50px;
  height: 50px;
  border-radius: 8px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.settings-content {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .header-content {
    padding: 12px 15px;
  }

  .title {
    font-size: 16px;
    line-height: 1.3;
  }

  .logo {
    width: 35px;
    height: 35px;
  }

  .logo-section {
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 10px 12px;
  }

  .title {
    font-size: 14px;
  }

  .logo {
    width: 30px;
    height: 30px;
  }

  .logo-section {
    gap: 8px;
  }
}
</style>
