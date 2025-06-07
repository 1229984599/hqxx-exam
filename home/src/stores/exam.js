import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useExamStore = defineStore('exam', () => {
  // 状态
  const selectedSemester = ref(null)
  const selectedGrade = ref(null)
  const selectedSubject = ref(null)
  const selectedCategory = ref(null)
  
  const semesters = ref([])
  const grades = ref([])
  const subjects = ref([])
  const categories = ref([])
  
  const currentQuestion = ref(null)
  const viewedQuestions = ref([])
  
  // 计算属性
  const isSelectionComplete = computed(() => {
    return selectedSemester.value && 
           selectedGrade.value && 
           selectedSubject.value && 
           selectedCategory.value
  })
  
  const filteredCategories = computed(() => {
    if (!selectedSubject.value) return []
    return categories.value.filter(cat => cat.subject_id === selectedSubject.value.id)
  })
  
  // 方法
  async function loadSemesters() {
    try {
      const response = await api.get('/semesters/', {
        params: { is_active: true }
      })
      semesters.value = response.data
    } catch (error) {
      console.error('加载学期失败:', error)
    }
  }
  
  async function loadGrades() {
    try {
      const response = await api.get('/grades/', {
        params: { is_active: true }
      })
      grades.value = response.data
    } catch (error) {
      console.error('加载年级失败:', error)
    }
  }
  
  async function loadSubjects() {
    try {
      const response = await api.get('/subjects/', {
        params: { is_active: true }
      })
      subjects.value = response.data
    } catch (error) {
      console.error('加载学科失败:', error)
    }
  }
  
  async function loadCategories() {
    try {
      const response = await api.get('/categories/', {
        params: { is_active: true }
      })
      categories.value = response.data
      console.log('分类数据加载成功:', response.data)
    } catch (error) {
      console.error('加载分类失败:', error)
      console.error('错误详情:', error.response?.data)
    }
  }
  
  async function loadRandomQuestion() {
    if (!isSelectionComplete.value) {
      throw new Error('请先完成选择')
    }
    
    try {
      const excludeIds = viewedQuestions.value.map(q => q.id).join(',')
      const response = await api.get('/questions/random', {
        params: {
          semester_id: selectedSemester.value.id,
          grade_id: selectedGrade.value.id,
          subject_id: selectedSubject.value.id,
          category_id: selectedCategory.value.id,
          exclude_ids: excludeIds || undefined
        }
      })
      
      currentQuestion.value = response.data
      
      // 添加到已查看列表
      if (!viewedQuestions.value.find(q => q.id === response.data.id)) {
        viewedQuestions.value.push(response.data)
      }
      
      return response.data
    } catch (error) {
      console.error('加载题目失败:', error)
      throw error
    }
  }
  
  function resetSelection() {
    selectedSemester.value = null
    selectedGrade.value = null
    selectedSubject.value = null
    selectedCategory.value = null
    currentQuestion.value = null
    viewedQuestions.value = []
  }
  
  function resetQuestions() {
    currentQuestion.value = null
    viewedQuestions.value = []
  }
  
  return {
    // 状态
    selectedSemester,
    selectedGrade,
    selectedSubject,
    selectedCategory,
    semesters,
    grades,
    subjects,
    categories,
    currentQuestion,
    viewedQuestions,
    
    // 计算属性
    isSelectionComplete,
    filteredCategories,
    
    // 方法
    loadSemesters,
    loadGrades,
    loadSubjects,
    loadCategories,
    loadRandomQuestion,
    resetSelection,
    resetQuestions
  }
})
