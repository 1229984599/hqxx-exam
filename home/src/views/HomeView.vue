<template>
  <div class="home-view">
    <div class="container">
      <div class="welcome-section">
        <h2 class="welcome-title">红旗小学无纸化测试</h2>
        <p class="welcome-subtitle">请选择学期、年级、学科和题目分类开始答题</p>
      </div>
      
      <div class="selection-grid">
        <!-- 学期选择 -->
        <div class="selection-card">
          <h3 class="card-title">
            <el-icon><Calendar /></el-icon>
            选择学期
          </h3>
          <div class="options-grid">
            <div
              v-for="semester in examStore.semesters"
              :key="semester.id"
              class="option-item"
              :class="{ active: examStore.selectedSemester?.id === semester.id }"
              @click="selectSemester(semester)"
            >
              {{ semester.name }}
            </div>
          </div>
        </div>
        
        <!-- 年级选择 -->
        <div class="selection-card">
          <h3 class="card-title">
            <el-icon><School /></el-icon>
            选择年级
          </h3>
          <div class="options-grid">
            <div
              v-for="grade in examStore.grades"
              :key="grade.id"
              class="option-item"
              :class="{ active: examStore.selectedGrade?.id === grade.id }"
              @click="selectGrade(grade)"
            >
              {{ grade.name }}
            </div>
          </div>
        </div>
        
        <!-- 学科选择 -->
        <div class="selection-card">
          <h3 class="card-title">
            <el-icon><Reading /></el-icon>
            选择学科
          </h3>
          <div class="options-grid">
            <div
              v-for="subject in examStore.subjects"
              :key="subject.id"
              class="option-item subject-item"
              :class="{ active: examStore.selectedSubject?.id === subject.id }"
              :style="{ borderColor: subject.color }"
              @click="selectSubject(subject)"
            >
              <div class="subject-color" :style="{ backgroundColor: subject.color }"></div>
              {{ subject.name }}
            </div>
          </div>
        </div>
        
        <!-- 题目分类选择 -->
        <div class="selection-card">
          <h3 class="card-title">
            <el-icon><Collection /></el-icon>
            选择题目分类
          </h3>
          <div class="options-grid">
            <div
              v-for="category in examStore.filteredCategories"
              :key="category.id"
              class="option-item"
              :class="{ active: examStore.selectedCategory?.id === category.id }"
              @click="selectCategory(category)"
            >
              {{ category.name }}
            </div>
            <div v-if="!examStore.selectedSubject" class="no-options">
              请先选择学科
            </div>
            <div v-else-if="examStore.selectedSubject && examStore.filteredCategories.length === 0" class="no-options">
              该学科暂无分类，请联系管理员添加
            </div>
          </div>
        </div>
      </div>
      
      <!-- 开始按钮 -->
      <div class="action-section">
        <el-button
          type="primary"
          size="large"
          :disabled="!examStore.isSelectionComplete"
          @click="startExam"
          class="start-button"
        >
          <el-icon><Right /></el-icon>
          开始答题
        </el-button>

        <div class="demo-section">
          <el-button
            type="info"
            size="large"
            @click="$router.push('/demo')"
            class="demo-button"
            plain
          >
            <el-icon><View /></el-icon>
            查看题目演示
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, School, Reading, Collection, Right, View } from '@element-plus/icons-vue'
import { useExamStore } from '../stores/exam'
import { ElMessage } from 'element-plus'

const router = useRouter()
const examStore = useExamStore()

onMounted(async () => {
  // 加载基础数据
  await Promise.all([
    examStore.loadSemesters(),
    examStore.loadGrades(),
    examStore.loadSubjects(),
    examStore.loadCategories()
  ])
})

function selectSemester(semester) {
  examStore.selectedSemester = semester
}

function selectGrade(grade) {
  examStore.selectedGrade = grade
}

function selectSubject(subject) {
  examStore.selectedSubject = subject
  // 清空分类选择
  examStore.selectedCategory = null
}

function selectCategory(category) {
  examStore.selectedCategory = category
}

function startExam() {
  if (!examStore.isSelectionComplete) {
    ElMessage.warning('请完成所有选择')
    return
  }
  
  // 重置题目状态
  examStore.resetQuestions()
  
  // 跳转到题目页面
  router.push('/question')
}
</script>

<style scoped>
.home-view {
  min-height: calc(100vh - 80px);
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 50px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  color: white;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.welcome-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.selection-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease;
}

.selection-card:hover {
  transform: translateY(-5px);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.option-item {
  padding: 15px 12px;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  font-weight: 500;
  color: #2c3e50;
}

.option-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-2px);
}

.option-item.active {
  border-color: #409eff;
  background: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.subject-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.subject-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.no-options {
  grid-column: 1 / -1;
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 20px;
}

.action-section {
  text-align: center;
}

.start-button {
  padding: 15px 40px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.demo-section {
  margin-top: 20px;
}

.demo-button {
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 20px;
}

@media (max-width: 768px) {
  .home-view {
    padding: 20px 15px;
  }

  .welcome-title {
    font-size: 22px;
  }

  .welcome-subtitle {
    font-size: 15px;
  }

  .selection-grid {
    grid-template-columns: 1fr;
    gap: 15px;
    margin-bottom: 30px;
  }

  .selection-card {
    padding: 20px 15px;
  }

  .card-title {
    font-size: 18px;
    margin-bottom: 15px;
  }

  .options-grid {
    grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
    gap: 10px;
  }

  .option-item {
    padding: 15px 10px;
    font-size: 14px;
    border-radius: 8px;
  }

  .start-button {
    padding: 18px 35px;
    font-size: 16px;
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .home-view {
    padding: 15px 10px;
  }

  .welcome-title {
    font-size: 20px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .selection-card {
    padding: 15px 12px;
  }

  .card-title {
    font-size: 16px;
  }

  .options-grid {
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 8px;
  }

  .option-item {
    padding: 12px 8px;
    font-size: 13px;
  }
}
</style>
