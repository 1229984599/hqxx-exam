<template>
  <div class="container mx-auto px-4 py-6">
    <!-- 配置未完成提示 -->
    <div v-if="!configStore.isConfigComplete">
      <ErrorState
        type="empty"
        title="请先完成配置"
        description="请返回首页完成学期、年级、学科、分类的选择"
        :show-retry="false"
        :show-go-back="true"
        @go-back="goHome"
      />
    </div>
    
    <!-- 主要内容 -->
    <div v-else>
      <!-- 顶部信息栏 -->
      <div class="card-modern p-4 sm:p-6 mb-6">
        <!-- 移动端简化版 -->
        <div class="block sm:hidden">
          <div class="text-center mb-4">
            <div class="bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-3 rounded-2xl text-sm font-semibold shadow-medium inline-block">
              {{ configStore.configSummary }}
            </div>
          </div>
          <div class="flex gap-3">
            <button 
              class="btn-secondary-modern flex-1"
              @click="goHome"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              首页
            </button>
            <button 
              class="btn-primary-modern flex-1"
              @click="getRandomQuestion"
              :disabled="questionsStore.loading"
            >
              <span v-if="questionsStore.loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              换题
            </button>
          </div>
        </div>

        <!-- 桌面端完整版 -->
        <div class="hidden sm:flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-medium">
              {{ configStore.configSummary }}
            </div>
            <div v-if="questionsStore.hasQuestions" class="flex items-center space-x-4 text-gray-600">
              <div class="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 616 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span class="text-sm font-medium">已练习 {{ questionsStore.viewedQuestionIds.length }} / {{ questionsStore.totalQuestions }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span class="text-sm font-medium">收藏 {{ favoriteQuestions.size }}</span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <button 
              class="btn-secondary-modern"
              @click="goHome"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              返回首页
            </button>
            <button 
              class="btn-primary-modern"
              @click="getRandomQuestion"
              :disabled="questionsStore.loading"
            >
              <span v-if="questionsStore.loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              换一题
            </button>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="questionsStore.loading && !questionsStore.currentQuestion" class="flex flex-col items-center justify-center py-20">
        <span class="loading loading-spinner loading-lg mb-4"></span>
        <p class="text-lg">正在加载试题...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="questionsStore.error" class="alert alert-error mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 class="font-bold">加载失败</h3>
          <div class="text-xs">{{ questionsStore.error }}</div>
        </div>
        <div>
          <button class="btn btn-sm btn-outline" @click="initializeQuestions">重试</button>
        </div>
      </div>
      
      <!-- 无题目状态 -->
      <div v-else-if="!questionsStore.currentQuestion && !questionsStore.loading" class="text-center py-20">
        <div class="text-6xl mb-4">📝</div>
        <h3 class="text-2xl font-bold mb-2">暂无试题</h3>
        <p class="text-base-content/70 mb-6">当前配置下没有找到试题，请检查配置或联系管理员</p>
        <button class="btn btn-primary" @click="initializeQuestions">重新加载</button>
      </div>
      
      <!-- 试题内容 -->
      <div v-else-if="questionsStore.currentQuestion" class="space-y-6">
        <!-- 试题卡片 -->
        <div class="question-card p-6 sm:p-8">
          <!-- 试题标题 -->
          <h2 class="question-title text-xl sm:text-3xl font-bold mb-4 leading-relaxed">
            {{ questionsStore.currentQuestion.title }}
          </h2>
          
          <!-- 试题难度和类型 -->
          <div class="flex flex-wrap items-center gap-3 mb-6">
            <div class="bg-gradient-to-r from-orange-400 to-orange-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
              {{ getDifficultyText(questionsStore.currentQuestion.difficulty) }}
            </div>
            <div class="bg-gradient-to-r from-blue-400 to-blue-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
              {{ getQuestionTypeText(questionsStore.currentQuestion.question_type) }}
            </div>
          </div>
          
          <!-- 试题内容 -->
          <div class="question-content prose prose-lg max-w-none mb-8 text-gray-700 leading-relaxed" v-html="questionsStore.currentQuestion.content"></div>
          
          <!-- 答案区域 -->
          <div class="answer-section rounded-2xl overflow-hidden">
            <button 
              @click="showAnswer = !showAnswer"
              class="w-full px-6 py-4 bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex items-center justify-between text-left"
            >
              <div class="flex items-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="font-semibold text-gray-800 text-lg">参考答案</span>
              </div>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                :class="`h-6 w-6 text-gray-500 transition-transform duration-200 ${showAnswer ? 'rotate-180' : ''}`"
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div v-if="showAnswer" class="px-6 py-6 bg-white border-t border-gray-200 animate-slide-up">
              <div 
                v-if="questionsStore.currentQuestion.answer"
                class="question-content prose prose-lg max-w-none text-gray-700 leading-relaxed"
                v-html="questionsStore.currentQuestion.answer"
              ></div>
              <div v-else class="text-gray-500 italic text-center py-4">暂无参考答案</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 浮动操作按钮组 -->
    <FloatingButtons
      v-if="configStore.isConfigComplete && questionsStore.currentQuestion"
      :is-favorited="isFavorited"
      :loading="questionsStore.loading"
      @print="printQuestion"
      @share="shareQuestion"
      @toggle-favorite="toggleFavorite"
      @next-question="getRandomQuestionAndScrollTop"
      @scroll-top="scrollToTop"
    />


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '../stores/config'
import { useQuestionsStore } from '../stores/questions'
import { message } from '../utils/message.js'
import { scrollToTop, copyToClipboard } from '../utils/ui.js'
import { useKeyboard, commonKeys } from '../composables/useKeyboard.js'
import ErrorState from '../components/ErrorState.vue'
import SkeletonLoader from '../components/SkeletonLoader.vue'
import FloatingButtons from '../components/FloatingButtons.vue'


const router = useRouter()
const configStore = useConfigStore()
const questionsStore = useQuestionsStore()
const { registerKey } = useKeyboard()

const showAnswer = ref(false)
const favoriteQuestions = ref(new Set())

// 计算当前题目是否已收藏
const isFavorited = computed(() => {
  return questionsStore.currentQuestion && favoriteQuestions.value.has(questionsStore.currentQuestion.id)
})



// 初始化检查试题
const initializeQuestions = () => {
  if (!configStore.isConfigComplete) {
    router.push('/')
    return
  }

  // 检查是否有试题数据
  if (!questionsStore.hasQuestions) {
    console.log('没有试题数据，返回首页重新配置')
    router.push('/')
    return
  }

  console.log(`当前有 ${questionsStore.totalQuestions} 道试题，已查看 ${questionsStore.viewedQuestionIds.length} 道`)
}

// 获取随机试题
const getRandomQuestion = () => {
  if (!configStore.isConfigComplete) {
    router.push('/')
    return
  }

  // 检查是否有试题数据
  if (!questionsStore.hasQuestions) {
    message.warning('暂无试题数据，请返回首页重新配置')
    router.push('/')
    return
  }

  showAnswer.value = false

  // 从本地数据中随机选择
  const success = questionsStore.getRandomQuestion()
  if (success) {
    message.success('已为您推荐新题目', {
      // description: `剩余 ${questionsStore.availableQuestions.length} 道未练习题目`,
      duration: 2000
    })
  } else if (questionsStore.error) {
    message.error(questionsStore.error, {
      description: '请尝试重新加载或返回首页重新配置'
    })
  }
}

// 获取随机试题并滚动到顶部
const getRandomQuestionAndScrollTop = () => {
  getRandomQuestion()
  scrollToTop()
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 切换收藏状态
const toggleFavorite = () => {
  if (!questionsStore.currentQuestion) return

  const questionId = questionsStore.currentQuestion.id

  if (favoriteQuestions.value.has(questionId)) {
    favoriteQuestions.value.delete(questionId)
    message.success('已取消收藏', {
      description: '题目已从收藏夹中移除',
      duration: 2000
    })
  } else {
    favoriteQuestions.value.add(questionId)
    message.success('收藏成功', {
      description: '题目已添加到收藏夹',
      duration: 2000
    })
  }

  // 保存到本地存储
  saveFavoritesToStorage()
}

// 保存收藏到本地存储
const saveFavoritesToStorage = () => {
  const favorites = Array.from(favoriteQuestions.value)
  localStorage.setItem('favoriteQuestions', JSON.stringify(favorites))
}

// 从本地存储加载收藏
const loadFavoritesFromStorage = () => {
  try {
    const stored = localStorage.getItem('favoriteQuestions')
    if (stored) {
      const favorites = JSON.parse(stored)
      favoriteQuestions.value = new Set(favorites)
    }
  } catch (error) {
    console.error('加载收藏数据失败:', error)
  }
}

// 分享题目
const shareQuestion = async () => {
  if (!questionsStore.currentQuestion) return

  const question = questionsStore.currentQuestion
  const shareText = `【题目分享】
题目：${question.title}
类型：${getQuestionTypeText(question.question_type)}
难度：${getDifficultyText(question.difficulty)}
内容：${question.content.replace(/<[^>]*>/g, '')}

来自：红旗小学考试系统`

  // 尝试使用Web Share API
  if (navigator.share) {
    try {
      await navigator.share({
        title: '题目分享',
        text: shareText,
        url: window.location.href
      })
      message.success('分享成功', {
        description: '题目已成功分享',
        duration: 2000
      })
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('分享失败:', error)
        fallbackShare(shareText)
      }
    }
  } else {
    fallbackShare(shareText)
  }
}

// 降级分享方案
const fallbackShare = async (text) => {
  const success = await copyToClipboard(text)
  if (success) {
    message.success('已复制到剪贴板', {
      description: '题目内容已复制，可以粘贴分享给他人',
      duration: 3000
    })
  } else {
    message.error('分享失败', {
      description: '无法复制到剪贴板，请手动复制题目内容',
      duration: 3000
    })
  }
}

// 打印题目
const printQuestion = () => {
  if (!questionsStore.currentQuestion) return

  const question = questionsStore.currentQuestion
  const printContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>题目打印 - ${question.title}</title>
      <style>
        body {
          font-family: 'Microsoft YaHei', Arial, sans-serif;
          line-height: 1.6;
          margin: 40px;
          color: #333;
        }
        .header {
          text-align: center;
          border-bottom: 2px solid #333;
          padding-bottom: 20px;
          margin-bottom: 30px;
        }
        .title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 10px;
        }
        .meta {
          font-size: 14px;
          color: #666;
        }
        .content {
          margin: 30px 0;
          font-size: 16px;
        }
        .answer-section {
          margin-top: 40px;
          padding-top: 20px;
          border-top: 1px solid #ddd;
        }
        .answer-title {
          font-weight: bold;
          margin-bottom: 15px;
          color: #2563eb;
        }
        .footer {
          margin-top: 50px;
          text-align: center;
          font-size: 12px;
          color: #999;
          border-top: 1px solid #eee;
          padding-top: 20px;
        }
        @media print {
          body { margin: 20px; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div class="title">${question.title}</div>
        <div class="meta">
          类型：${getQuestionTypeText(question.question_type)} |
          难度：${getDifficultyText(question.difficulty)} |
          题目ID：${question.id}
        </div>
      </div>

      <div class="content">
        <h3>题目内容：</h3>
        ${question.content}
      </div>

      ${question.answer ? `
        <div class="answer-section">
          <div class="answer-title">参考答案：</div>
          ${question.answer}
        </div>
      ` : ''}

      <div class="footer">
        红旗小学考试系统 - 打印时间：${new Date().toLocaleString()}
      </div>
    </body>
    </html>
  `

  const printWindow = window.open('', '_blank')
  printWindow.document.write(printContent)
  printWindow.document.close()

  // 等待内容加载完成后打印
  printWindow.onload = () => {
    printWindow.print()
    printWindow.close()
  }

  message.success('打印预览已打开', {
    description: '请在新窗口中完成打印操作',
    duration: 2000
  })
}

// 获取难度文本
const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    1: '简单',
    2: '较易', 
    3: '中等',
    4: '较难',
    5: '困难'
  }
  return difficultyMap[difficulty] || '未知'
}

// 获取题目类型文本
const getQuestionTypeText = (type) => {
  const typeMap = {
    'single': '单选题',
    'multiple': '多选题',
    'judge': '判断题',
    'fill': '填空题',
    'essay': '问答题',
    'calculation': '计算题'
  }
  return typeMap[type] || type
}

// 组件挂载时检查试题
onMounted(() => {
  initializeQuestions()
  loadFavoritesFromStorage()

  // 注册键盘快捷键
  registerKey(commonKeys.SPACE, () => {
    if (questionsStore.currentQuestion && !showAnswer.value) {
      showAnswer.value = true
    } else {
      getRandomQuestionAndScrollTop()
    }
  })

  registerKey(commonKeys.ENTER, () => {
    getRandomQuestionAndScrollTop()
  })

  registerKey('h', () => {
    showAnswer.value = !showAnswer.value
  })

  registerKey('f', () => {
    toggleFavorite()
  })

  registerKey('s', () => {
    shareQuestion()
  })

  registerKey('p', () => {
    printQuestion()
  })

  registerKey(commonKeys.ESCAPE, () => {
    router.push('/')
  })
})
</script>

<style scoped>
.question-content {
  line-height: 1.8;
}

.question-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  margin: 16px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.question-content :deep(p) {
  margin: 16px 0;
}

.question-content :deep(ul), 
.question-content :deep(ol) {
  margin: 16px 0;
  padding-left: 24px;
}

.question-content :deep(li) {
  margin: 8px 0;
}

.question-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.question-content :deep(th),
.question-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 12px 16px;
  text-align: left;
}

.question-content :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}

/* 动画效果 */
.animate-slide-up {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
