import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/utils/api'

export const useQuestionsStore = defineStore('questions', () => {
  // 状态
  const questions = ref([]) // 当前配置下的所有试题
  const currentQuestion = ref(null) // 当前显示的试题
  const currentQuestionIndex = ref(0)
  const loading = ref(false)
  const error = ref(null)
  const viewedQuestionIds = ref([]) // 已查看的试题ID列表
  const currentConfig = ref(null) // 当前配置信息

  // 计算属性
  const hasQuestions = computed(() => questions.value.length > 0)
  const totalQuestions = computed(() => questions.value.length)
  const hasNextQuestion = computed(() => currentQuestionIndex.value < questions.value.length - 1)
  const hasPrevQuestion = computed(() => currentQuestionIndex.value > 0)
  const availableQuestions = computed(() => {
    // 获取未查看的试题
    return questions.value.filter(q => !viewedQuestionIds.value.includes(q.id))
  })
  const canGetNewQuestion = computed(() => {
    // 是否可以获取新试题（至少有2道题，且有未查看的）
    return questions.value.length > 1 && availableQuestions.value.length > 0
  })
  
  // 方法
  const loadAllQuestions = async (config, forceRefresh = false) => {
    try {
      loading.value = true
      error.value = null

      console.log(`开始加载试题数据 ${forceRefresh ? '(强制刷新)' : ''}...`)

      // 保存当前配置
      currentConfig.value = { ...config }

      const params = {
        semester_id: config.semester_id,
        grade_id: config.grade_id,
        subject_id: config.subject_id,
        category_id: config.category_id,
        is_active: true,
        is_published: true,
        limit: 1000, // 获取所有题目
        _t: forceRefresh ? Date.now() : undefined // 强制刷新时添加时间戳避免缓存
      }

      // 如果是强制刷新，清除相关缓存
      if (forceRefresh) {
        // 这里可以添加清除缓存的逻辑
        console.log('强制刷新：清除缓存并重新请求数据')
      }

      const response = await apiService.getQuestions(params)
      const data = response.data || response || []
      questions.value = data

      // 重置状态
      viewedQuestionIds.value = []
      currentQuestionIndex.value = 0

      if (questions.value.length > 0) {
        // 随机选择第一道题
        const randomIndex = Math.floor(Math.random() * questions.value.length)
        currentQuestion.value = questions.value[randomIndex]
        viewedQuestionIds.value = [currentQuestion.value.id]
        currentQuestionIndex.value = randomIndex

        console.log(`成功加载 ${questions.value.length} 道试题，当前显示第 ${randomIndex + 1} 道`)
      } else {
        currentQuestion.value = null
        error.value = '该配置下暂无试题'
        console.log('该配置下没有找到试题')
      }

    } catch (err) {
      console.error('加载试题失败:', err)
      error.value = '加载试题失败，请稍后重试'
      questions.value = []
      currentQuestion.value = null
    } finally {
      loading.value = false
    }
  }
  
  const getRandomQuestion = () => {
    try {
      loading.value = true
      error.value = null

      // 检查是否有足够的试题
      if (questions.value.length === 0) {
        error.value = '暂无试题数据'
        return false
      }

      if (questions.value.length === 1) {
        error.value = '试题数量过少，无法刷新'
        return false
      }

      // 获取未查看的试题
      let availableQuestions = questions.value.filter(q => !viewedQuestionIds.value.includes(q.id))

      // 如果所有题目都看过了，重置已查看列表（保留当前题目）
      if (availableQuestions.length === 0) {
        viewedQuestionIds.value = currentQuestion.value ? [currentQuestion.value.id] : []
        availableQuestions = questions.value.filter(q => !viewedQuestionIds.value.includes(q.id))
      }

      if (availableQuestions.length === 0) {
        error.value = '没有更多题目了'
        return false
      }

      // 随机选择一道题
      const randomIndex = Math.floor(Math.random() * availableQuestions.length)
      const selectedQuestion = availableQuestions[randomIndex]

      // 更新当前题目
      currentQuestion.value = selectedQuestion
      viewedQuestionIds.value.push(selectedQuestion.id)

      // 更新索引
      currentQuestionIndex.value = questions.value.findIndex(q => q.id === selectedQuestion.id)

      console.log(`随机选择了第 ${currentQuestionIndex.value + 1} 道题，已查看 ${viewedQuestionIds.value.length} 道题`)

      return true

    } catch (err) {
      console.error('获取随机试题失败:', err)
      error.value = '获取试题失败，请稍后重试'
      return false
    } finally {
      loading.value = false
    }
  }
  
  const nextQuestion = () => {
    if (hasNextQuestion.value) {
      currentQuestionIndex.value++
      currentQuestion.value = questions.value[currentQuestionIndex.value]
      
      if (!viewedQuestionIds.value.includes(currentQuestion.value.id)) {
        viewedQuestionIds.value.push(currentQuestion.value.id)
      }
    }
  }
  
  const prevQuestion = () => {
    if (hasPrevQuestion.value) {
      currentQuestionIndex.value--
      currentQuestion.value = questions.value[currentQuestionIndex.value]
    }
  }
  
  const goToQuestion = (index) => {
    if (index >= 0 && index < questions.value.length) {
      currentQuestionIndex.value = index
      currentQuestion.value = questions.value[index]
      
      if (!viewedQuestionIds.value.includes(currentQuestion.value.id)) {
        viewedQuestionIds.value.push(currentQuestion.value.id)
      }
    }
  }
  
  const clearQuestions = () => {
    questions.value = []
    currentQuestion.value = null
    currentQuestionIndex.value = 0
    error.value = null
    viewedQuestionIds.value = []
    currentConfig.value = null
  }

  const resetViewedQuestions = () => {
    viewedQuestionIds.value = currentQuestion.value ? [currentQuestion.value.id] : []
  }

  // 检查配置是否改变
  const isConfigChanged = (newConfig) => {
    if (!currentConfig.value) return true

    return (
      currentConfig.value.semester_id !== newConfig.semester_id ||
      currentConfig.value.grade_id !== newConfig.grade_id ||
      currentConfig.value.subject_id !== newConfig.subject_id ||
      currentConfig.value.category_id !== newConfig.category_id
    )
  }
  
  return {
    // 状态
    questions,
    currentQuestion,
    currentQuestionIndex,
    loading,
    error,
    viewedQuestionIds,
    currentConfig,

    // 计算属性
    hasQuestions,
    totalQuestions,
    hasNextQuestion,
    hasPrevQuestion,
    availableQuestions,
    canGetNewQuestion,

    // 方法
    loadAllQuestions,
    getRandomQuestion,
    nextQuestion,
    prevQuestion,
    goToQuestion,
    clearQuestions,
    resetViewedQuestions,
    isConfigChanged
  }
}, {
  persist: {
    key: 'questions-store',
    storage: localStorage,
    paths: ['questions', 'currentQuestion', 'viewedQuestionIds', 'currentConfig']
  }
})
