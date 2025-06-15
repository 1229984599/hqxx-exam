<template>
  <div class="max-w-6xl mx-auto animate-fade-in">
    <!-- 欢迎标题 -->
    <div class="text-center mb-16 relative">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 -z-10">
        <div class="absolute top-10 left-1/4 w-32 h-32 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div class="absolute top-20 right-1/4 w-32 h-32 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" style="animation-delay: 1s;"></div>
        <div class="absolute bottom-10 left-1/3 w-32 h-32 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" style="animation-delay: 2s;"></div>
      </div>

      <!-- 主图标 -->
      <div class="inline-flex items-center justify-center w-24 h-24 sm:w-28 sm:h-28 bg-gradient-to-br from-primary-500 via-purple-500 to-pink-500 rounded-3xl mb-8 shadow-large float-animation">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 sm:h-14 sm:w-14 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>

      <!-- 标题 -->
      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
        <span class="bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          红旗小学
        </span>
        <br>
        <span class="bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">
          考试系统
        </span>
      </h1>

      <!-- 副标题 -->
      <div class="max-w-2xl mx-auto">
        <p class="text-lg sm:text-xl text-gray-600 font-medium mb-4">智能学习，精准练习，助力成长</p>
        <div class="flex flex-wrap justify-center gap-4 text-sm text-gray-500">
          <span class="flex items-center gap-1">
            <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            智能推荐
          </span>
          <span class="flex items-center gap-1">
            <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            个性化学习
          </span>
          <span class="flex items-center gap-1">
            <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            实时反馈
          </span>
        </div>
      </div>
    </div>

    <!-- 配置卡片 -->
    <div class="card-modern p-8 mb-8">
      <div class="flex items-center mb-8">
        <div class="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl mr-4 shadow-medium">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h2 class="text-2xl font-bold text-gray-800 mb-1">学习配置</h2>
          <p class="text-gray-600">请选择您的学习参数，开启智能练习之旅</p>
        </div>
      </div>
        
        <!-- 配置表单 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6 lg:gap-8 config-grid-mobile">
          <!-- 学期选择 -->
          <div class="space-y-3">
            <label class="flex items-center space-x-2 text-gray-700 font-semibold label-mobile">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>学期 <span class="text-red-500">*</span></span>
            </label>
            <div class="relative group">
              <select
                v-model="configStore.selectedSemester"
                class="select-modern w-full"
                :disabled="configStore.loading"
              >
                <option value="">请选择学期</option>
                <option
                  v-for="semester in configStore.semesters"
                  :key="semester.id"
                  :value="semester.id"
                >
                  {{ semester.name }}
                </option>
              </select>
              <div class="select-icon-container">
                <svg xmlns="http://www.w3.org/2000/svg" class="select-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- 年级选择 -->
          <div class="space-y-3">
            <label class="flex items-center space-x-2 text-gray-700 font-semibold label-mobile">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span>年级 <span class="text-red-500">*</span></span>
            </label>
            <div class="relative group">
              <select
                v-model="configStore.selectedGrade"
                class="select-modern w-full"
                :disabled="configStore.loading"
              >
                <option value="">请选择年级</option>
                <option
                  v-for="grade in configStore.grades"
                  :key="grade.id"
                  :value="grade.id"
                >
                  {{ grade.name }}
                </option>
              </select>
              <div class="select-icon-container">
                <svg xmlns="http://www.w3.org/2000/svg" class="select-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- 学科选择 -->
          <div class="space-y-3">
            <label class="flex items-center space-x-2 text-gray-700 font-semibold label-mobile">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span>学科 <span class="text-red-500">*</span></span>
            </label>
            <div class="relative group">
              <select
                v-model="configStore.selectedSubject"
                class="select-modern w-full"
                :disabled="configStore.loading"
                @change="onSubjectChange"
              >
                <option value="">请选择学科</option>
                <option
                  v-for="subject in configStore.subjects"
                  :key="subject.id"
                  :value="subject.id"
                >
                  {{ subject.name }}
                </option>
              </select>
              <div class="select-icon-container">
                <svg xmlns="http://www.w3.org/2000/svg" class="select-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- 分类选择 -->
          <div class="space-y-3">
            <label class="flex items-center space-x-2 text-gray-700 font-semibold label-mobile">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <span>分类 <span class="text-red-500">*</span></span>
            </label>
            <div class="relative group">
              <select
                v-model="configStore.selectedCategory"
                class="select-modern w-full"
                :disabled="configStore.loading || !configStore.selectedSubject"
              >
                <option value="">请选择分类</option>
                <option
                  v-for="category in configStore.categories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </option>
              </select>
              <div class="select-icon-container">
                <svg xmlns="http://www.w3.org/2000/svg" class="select-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="configStore.loading">
          <SkeletonLoader type="card" />
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error">
          <ErrorState
            type="network"
            title="加载配置失败"
            description="无法加载学期、年级、学科等配置信息，请检查网络连接"
            :tips="['检查网络连接是否正常', '刷新页面重试', '联系管理员检查服务器状态']"
            @retry="retryLoadConfig"
          />
        </div>

        <!-- 配置完成提示 -->
        <div v-if="configStore.isConfigComplete" class="mt-8 p-6 success-state rounded-2xl animate-bounce-in">
          <div class="flex items-center space-x-4">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-bold text-green-800 mb-1">🎉 配置完成！</h3>
              <p class="text-sm text-green-700 leading-relaxed">{{ configStore.configSummary }}</p>
              <p class="text-xs text-green-600 mt-2 opacity-80">点击下方按钮开始您的智能练习之旅</p>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-6 mt-12">
          <!-- 主要操作按钮 -->
          <button
            class="btn-primary-modern btn-modern-lg w-full sm:w-auto order-1 relative overflow-hidden group"
            @click="startPractice"
            :disabled="!configStore.isConfigComplete || loading"
          >
            <!-- 按钮背景动画 -->
            <div class="absolute inset-0 bg-gradient-to-r from-primary-400 to-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

            <!-- 按钮内容 -->
            <div class="relative flex items-center justify-center">
              <span v-if="loading" class="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3 group-hover:scale-110 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span class="font-bold">开始智能练习</span>
            </div>
          </button>

          <!-- 次要操作按钮 -->
          <button
            class="btn-secondary-modern btn-modern-sm w-full sm:w-auto order-2 group"
            @click="clearConfig"
            :disabled="!configStore.isConfigComplete"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 group-hover:rotate-180 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            重置配置
          </button>
        </div>

        <!-- 提示信息 -->
        <div v-if="!configStore.isConfigComplete" class="text-center mt-6">
          <p class="text-gray-500 text-sm">请完成上方配置后开始练习</p>
        </div>
      </div>
    </div>
    
    <!-- 功能介绍 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
      <div class="card bg-base-100 shadow-lg">
        <div class="card-body text-center">
          <div class="text-primary text-4xl mb-4">📚</div>
          <h3 class="card-title justify-center">丰富题库</h3>
          <p class="text-sm text-base-content/70">涵盖各个学期、年级、学科的精选试题</p>
        </div>
      </div>
      
      <div class="card bg-base-100 shadow-lg">
        <div class="card-body text-center">
          <div class="text-primary text-4xl mb-4">🎯</div>
          <h3 class="card-title justify-center">智能练习</h3>
          <p class="text-sm text-base-content/70">根据配置智能推荐，随机出题不重复</p>
        </div>
      </div>
      
      <div class="card bg-base-100 shadow-lg">
        <div class="card-body text-center">
          <div class="text-primary text-4xl mb-4">⚡</div>
          <h3 class="card-title justify-center">即时反馈</h3>
          <p class="text-sm text-base-content/70">实时查看答案，快速提升学习效果</p>
        </div>
      </div>
    </div>

</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '../stores/config'
import { useQuestionsStore } from '../stores/questions'
import { message } from '../utils/message.js'
import SkeletonLoader from '../components/SkeletonLoader.vue'
import ErrorState from '../components/ErrorState.vue'

const router = useRouter()
const configStore = useConfigStore()
const questionsStore = useQuestionsStore()

const loading = ref(false)
const error = ref(false)

// 重试加载配置
const retryLoadConfig = async () => {
  try {
    error.value = false
    await configStore.loadAllData()
  } catch (err) {
    console.error('重试加载配置失败:', err)
    error.value = true
    message.error('重试失败，请稍后再试')
  }
}

// 监听学科变化，重新加载分类
const onSubjectChange = async () => {
  try {
    configStore.selectedCategory = null
    if (configStore.selectedSubject) {
      await configStore.loadCategories(configStore.selectedSubject)
    }
  } catch (err) {
    console.error('加载分类失败:', err)
    message.error('加载分类失败，请重试')
  }
}

// 清空配置
const clearConfig = () => {
  configStore.clearConfig()
  questionsStore.clearQuestions()
  message.success('配置已清空', {
    description: '您可以重新选择配置参数',
    duration: 2000
  })
}

// 开始练习
const startPractice = async () => {
  if (!configStore.isConfigComplete) return

  try {
    loading.value = true

    const config = {
      semester_id: configStore.selectedSemester,
      grade_id: configStore.selectedGrade,
      subject_id: configStore.selectedSubject,
      category_id: configStore.selectedCategory
    }

    // 检查配置是否改变，如果改变则重新加载所有试题
    if (questionsStore.isConfigChanged(config)) {
      console.log('配置已改变，重新加载试题数据...')
      await questionsStore.loadAllQuestions(config)
    }

    // 检查是否有试题
    if (!questionsStore.hasQuestions) {
      message.warning('该配置下暂无试题，请选择其他配置', {
        description: '请尝试选择其他学期、年级、学科或分类'
      })
      return
    }


    // 显示成功消息
    message.success('准备就绪，开始练习！', {
      // description: `已为您准备 ${questionsStore.totalQuestions} 道精选试题`,
      duration: 2000
    })

    // 跳转到试题页面
    await router.push('/questions')

  } catch (error) {
    console.error('开始练习失败:', error)
    message.error('开始练习失败', {
      description: '请检查网络连接后重试',
      duration: 4000
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}
</style>
