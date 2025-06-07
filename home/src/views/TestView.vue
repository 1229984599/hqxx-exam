<template>
  <div class="test-view">
    <h1>API连接测试</h1>
    
    <div class="test-section">
      <h2>学期数据</h2>
      <div v-if="semesters.length > 0">
        <div v-for="semester in semesters" :key="semester.id">
          {{ semester.name }} ({{ semester.code }})
        </div>
      </div>
      <div v-else>
        <p>加载中或无数据...</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>年级数据</h2>
      <div v-if="grades.length > 0">
        <div v-for="grade in grades" :key="grade.id">
          {{ grade.name }} ({{ grade.code }})
        </div>
      </div>
      <div v-else>
        <p>加载中或无数据...</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>学科数据</h2>
      <div v-if="subjects.length > 0">
        <div v-for="subject in subjects" :key="subject.id">
          {{ subject.name }} ({{ subject.code }})
        </div>
      </div>
      <div v-else>
        <p>加载中或无数据...</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>分类数据</h2>
      <div v-if="categories.length > 0">
        <div v-for="category in categories" :key="category.id">
          {{ category.name }} ({{ category.code }})
        </div>
      </div>
      <div v-else>
        <p>加载中或无数据...</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>试题数据</h2>
      <div v-if="questions.length > 0">
        <div v-for="question in questions" :key="question.id">
          {{ question.title }}
        </div>
      </div>
      <div v-else>
        <p>加载中或无数据...</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>错误信息</h2>
      <div v-if="errors.length > 0">
        <div v-for="error in errors" :key="error" style="color: red;">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const semesters = ref([])
const grades = ref([])
const subjects = ref([])
const categories = ref([])
const questions = ref([])
const errors = ref([])

onMounted(async () => {
  await loadAllData()
})

async function loadAllData() {
  try {
    console.log('开始加载数据...')
    
    // 测试学期
    try {
      const semesterRes = await api.get('/semesters/')
      semesters.value = semesterRes.data
      console.log('学期数据:', semesterRes.data)
    } catch (error) {
      errors.value.push('学期数据加载失败: ' + error.message)
      console.error('学期数据加载失败:', error)
    }
    
    // 测试年级
    try {
      const gradeRes = await api.get('/grades/')
      grades.value = gradeRes.data
      console.log('年级数据:', gradeRes.data)
    } catch (error) {
      errors.value.push('年级数据加载失败: ' + error.message)
      console.error('年级数据加载失败:', error)
    }
    
    // 测试学科
    try {
      const subjectRes = await api.get('/subjects/')
      subjects.value = subjectRes.data
      console.log('学科数据:', subjectRes.data)
    } catch (error) {
      errors.value.push('学科数据加载失败: ' + error.message)
      console.error('学科数据加载失败:', error)
    }
    
    // 测试分类
    try {
      const categoryRes = await api.get('/categories/')
      categories.value = categoryRes.data
      console.log('分类数据:', categoryRes.data)
    } catch (error) {
      errors.value.push('分类数据加载失败: ' + error.message)
      console.error('分类数据加载失败:', error)
    }
    
    // 测试试题
    try {
      const questionRes = await api.get('/questions/')
      questions.value = questionRes.data
      console.log('试题数据:', questionRes.data)
    } catch (error) {
      errors.value.push('试题数据加载失败: ' + error.message)
      console.error('试题数据加载失败:', error)
    }
    
  } catch (error) {
    errors.value.push('总体加载失败: ' + error.message)
    console.error('总体加载失败:', error)
  }
}
</script>

<style scoped>
.test-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
}

.test-section h2 {
  margin-bottom: 15px;
  color: #333;
}
</style>
