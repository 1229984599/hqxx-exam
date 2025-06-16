import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/utils/api'

export const useConfigStore = defineStore('config', () => {
  // 状态
  const selectedSemester = ref(null)
  const selectedGrade = ref(null)
  const selectedSubject = ref(null)
  const selectedCategory = ref(null)
  
  // 选项数据
  const semesters = ref([])
  const grades = ref([])
  const subjects = ref([])
  const categories = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 计算属性
  const isConfigComplete = computed(() => {
    return selectedSemester.value &&
           selectedGrade.value &&
           selectedSubject.value &&
           selectedCategory.value
  })

  const hasValidSemesters = computed(() => {
    return semesters.value && semesters.value.length > 0
  })

  const configSummary = computed(() => {
    if (!isConfigComplete.value) return ''

    const semester = semesters.value.find(s => s.id === selectedSemester.value)
    const grade = grades.value.find(g => g.id === selectedGrade.value)
    const subject = subjects.value.find(s => s.id === selectedSubject.value)
    const category = categories.value.find(c => c.id === selectedCategory.value)

    return `${semester?.name} - ${grade?.name} - ${subject?.name} - ${category?.name}`
  })

  const semesterStatusMessage = computed(() => {
    if (!hasValidSemesters.value) {
      return {
        type: 'warning',
        message: '暂无可用的学期，请联系管理员开启学期'
      }
    }
    return null
  })
  
  // 方法
  const loadSemesters = async () => {
    try {
      loading.value = true
      const data = await apiService.getSemesters({ is_active: true })
      semesters.value = data || []
    } catch (error) {
      console.error('加载学期列表失败:', error)
      semesters.value = []
    } finally {
      loading.value = false
    }
  }
  
  const loadGrades = async () => {
    try {
      loading.value = true
      const data = await apiService.getGrades({ is_active: true })
      grades.value = data || []
    } catch (error) {
      console.error('加载年级列表失败:', error)
      grades.value = []
    } finally {
      loading.value = false
    }
  }
  
  const loadSubjects = async () => {
    try {
      loading.value = true
      const data = await apiService.getSubjects({ is_active: true })
      subjects.value = data || []
    } catch (error) {
      console.error('加载学科列表失败:', error)
      subjects.value = []
    } finally {
      loading.value = false
    }
  }
  
  const loadCategories = async (subjectId = null) => {
    try {
      loading.value = true
      const params = { is_active: true }
      if (subjectId) {
        params.subject_id = subjectId
      }
      const data = await apiService.getCategories(params)
      categories.value = data || []
    } catch (error) {
      console.error('加载分类列表失败:', error)
      categories.value = []
    } finally {
      loading.value = false
    }
  }
  
  const loadAllData = async () => {
    await Promise.all([
      loadSemesters(),
      loadGrades(),
      loadSubjects()
    ])
    
    // 如果已选择学科，加载对应分类
    if (selectedSubject.value) {
      await loadCategories(selectedSubject.value)
    }
  }
  
  const setConfig = (config) => {
    selectedSemester.value = config.semester_id
    selectedGrade.value = config.grade_id
    selectedSubject.value = config.subject_id
    selectedCategory.value = config.category_id
  }
  
  const clearConfig = () => {
    selectedSemester.value = null
    selectedGrade.value = null
    selectedSubject.value = null
    selectedCategory.value = null
  }
  
  const getConfig = () => {
    return {
      semester_id: selectedSemester.value,
      grade_id: selectedGrade.value,
      subject_id: selectedSubject.value,
      category_id: selectedCategory.value
    }
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
    loading,
    
    // 计算属性
    isConfigComplete,
    hasValidSemesters,
    configSummary,
    semesterStatusMessage,
    
    // 方法
    loadSemesters,
    loadGrades,
    loadSubjects,
    loadCategories,
    loadAllData,
    setConfig,
    clearConfig,
    getConfig
  }
}, {
  persist: true
})
