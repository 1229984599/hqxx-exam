<template>
  <div class="question-view">
    <div class="container">
      <!-- 当前选择信息 -->
      <div class="selection-info">
        <el-tag type="info" size="large">{{ examStore.selectedSemester?.name }}</el-tag>
        <el-tag type="success" size="large">{{ examStore.selectedGrade?.name }}</el-tag>
        <el-tag 
          type="warning" 
          size="large"
          :style="{ backgroundColor: examStore.selectedSubject?.color, borderColor: examStore.selectedSubject?.color }"
        >
          {{ examStore.selectedSubject?.name }}
        </el-tag>
        <el-tag type="primary" size="large">{{ examStore.selectedCategory?.name }}</el-tag>
      </div>
      
      <!-- 题目卡片 -->
      <div class="question-card" v-if="examStore.currentQuestion">
        <div class="question-header">
          <h2 class="question-title">{{ examStore.currentQuestion.title }}</h2>
          <div class="question-meta">
            <el-tag size="small" type="info">
              难度: {{ getDifficultyText(examStore.currentQuestion.difficulty) }}
            </el-tag>
            <el-tag size="small" type="success">
              类型: {{ getQuestionTypeText(examStore.currentQuestion.question_type) }}
            </el-tag>
          </div>
        </div>
        
        <div class="question-content" v-html="examStore.currentQuestion.content"></div>
        
        <!-- 答案区域 -->
        <div class="answer-section" v-if="showAnswer">
          <h3 class="answer-title">
            <el-icon><Check /></el-icon>
            参考答案
          </h3>
          <div class="answer-content" v-html="examStore.currentQuestion.answer"></div>
          
          <div v-if="examStore.currentQuestion.explanation" class="explanation-section">
            <h3 class="explanation-title">
              <el-icon><InfoFilled /></el-icon>
              解析
            </h3>
            <div class="explanation-content" v-html="examStore.currentQuestion.explanation"></div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button
            v-if="!showAnswer"
            type="success"
            @click="showAnswer = true"
            :icon="View"
            size="large"
            class="action-btn"
          >
            查看答案
          </el-button>

          <el-button
            v-if="showAnswer"
            type="warning"
            @click="hideAnswer"
            :icon="Hide"
            size="large"
            class="action-btn"
          >
            隐藏答案
          </el-button>

          <el-button
            type="primary"
            @click="loadNextQuestion"
            :loading="loading"
            :icon="Refresh"
            size="large"
            class="action-btn next-btn"
          >
            下一题
          </el-button>

          <el-button
            type="info"
            @click="toggleFullscreen"
            :icon="isFullscreen ? 'FullScreen' : 'Aim'"
            size="large"
            class="action-btn"
            plain
          >
            {{ isFullscreen ? '退出全屏' : '全屏显示' }}
          </el-button>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div class="empty-state" v-else-if="!loading">
        <el-empty description="点击下方按钮开始答题">
          <el-button
            type="primary"
            @click="loadFirstQuestion"
            :loading="loading"
            size="large"
            class="start-test-btn"
          >
            开始答题
          </el-button>
        </el-empty>
      </div>
      
      <!-- 加载状态 -->
      <div class="loading-state" v-if="loading">
        <el-skeleton :rows="8" animated />
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-section" v-if="examStore.viewedQuestions.length > 0">
        <h3>答题统计</h3>
        <p>已完成题目: {{ examStore.viewedQuestions.length }} 道</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Check, InfoFilled, View, Hide, Refresh } from '@element-plus/icons-vue'
import { useExamStore } from '../stores/exam'
import { ElMessage } from 'element-plus'

const router = useRouter()
const examStore = useExamStore()

const loading = ref(false)
const showAnswer = ref(false)
const isFullscreen = ref(false)

onMounted(() => {
  // 检查是否已完成选择
  if (!examStore.isSelectionComplete) {
    ElMessage.warning('请先完成选择')
    router.push('/')
    return
  }
})

async function loadFirstQuestion() {
  await loadNextQuestion()
}

async function loadNextQuestion() {
  loading.value = true
  showAnswer.value = false
  
  try {
    await examStore.loadRandomQuestion()
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.info('当前分类下没有更多题目了')
    } else {
      ElMessage.error('加载题目失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

function hideAnswer() {
  showAnswer.value = false
}

function getDifficultyText(difficulty) {
  const difficultyMap = {
    1: '简单',
    2: '较易',
    3: '中等',
    4: '较难',
    5: '困难'
  }
  return difficultyMap[difficulty] || '未知'
}

function getQuestionTypeText(type) {
  const typeMap = {
    'single': '单选题',
    'multiple': '多选题',
    'fill': '填空题',
    'essay': '问答题',
    'judge': '判断题'
  }
  return typeMap[type] || '其他'
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().then(() => {
      isFullscreen.value = true
    }).catch(err => {
      console.error('无法进入全屏模式:', err)
    })
  } else {
    document.exitFullscreen().then(() => {
      isFullscreen.value = false
    }).catch(err => {
      console.error('无法退出全屏模式:', err)
    })
  }
}
</script>

<style scoped>
.question-view {
  min-height: calc(100vh - 80px);
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.selection-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 30px;
  justify-content: center;
}

.question-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  margin-bottom: 30px;
}

.question-header {
  margin-bottom: 25px;
}

.question-title {
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
  line-height: 1.5;
}

.question-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.question-content {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  margin-bottom: 25px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.answer-section {
  margin-top: 30px;
  padding-top: 25px;
  border-top: 2px solid #e1e8ed;
}

.answer-title,
.explanation-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
}

.answer-content,
.explanation-content {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 12px;
  border-left: 4px solid #67c23a;
}

.explanation-section {
  margin-top: 20px;
}

.explanation-content {
  background: #fff7e6;
  border-left-color: #e6a23c;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 15px 30px;
  font-size: 16px;
  border-radius: 25px;
  min-width: 120px;
}

.next-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.start-test-btn {
  padding: 18px 40px;
  font-size: 18px;
  border-radius: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.stats-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.stats-section h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.stats-section p {
  color: #666;
  font-size: 16px;
}

/* 富文本内容样式 */
.question-content :deep(p),
.answer-content :deep(p),
.explanation-content :deep(p) {
  margin-bottom: 10px;
}

.question-content :deep(img),
.answer-content :deep(img),
.explanation-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 10px 0;
}

@media (max-width: 768px) {
  .question-view {
    padding: 15px 10px;
  }

  .question-card {
    padding: 20px 15px;
    margin-bottom: 20px;
  }

  .question-title {
    font-size: 18px;
    line-height: 1.6;
  }

  .question-content,
  .answer-content,
  .explanation-content {
    font-size: 15px;
    padding: 15px;
    line-height: 1.8;
  }

  .selection-info {
    gap: 8px;
    margin-bottom: 20px;
  }

  .selection-info .el-tag {
    font-size: 12px;
    padding: 4px 8px;
  }

  .action-buttons {
    gap: 12px;
    margin-top: 25px;
  }

  .action-btn {
    padding: 16px 25px;
    font-size: 15px;
    min-width: 110px;
    flex: 1;
    max-width: 150px;
  }

  .start-test-btn {
    padding: 20px 35px;
    font-size: 16px;
    width: 100%;
    max-width: 280px;
  }
}

@media (max-width: 480px) {
  .question-view {
    padding: 10px 8px;
  }

  .question-card {
    padding: 15px 12px;
  }

  .question-title {
    font-size: 16px;
  }

  .question-content,
  .answer-content,
  .explanation-content {
    font-size: 14px;
    padding: 12px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }

  .action-btn {
    width: 100%;
    max-width: 200px;
    padding: 18px 20px;
  }
}
</style>
