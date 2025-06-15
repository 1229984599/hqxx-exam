<template>
  <!-- 配置对话框 -->
  <dialog ref="configDialog" class="modal">
    <div class="modal-box w-11/12 max-w-4xl card-modern max-h-[90vh] overflow-y-auto">
      <div class="flex items-center mb-8">
        <div class="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl mr-4 shadow-medium">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-2xl font-bold text-gray-800 mb-1">学习配置设置</h3>
          <p class="text-gray-600">调整您的学习参数</p>
        </div>
      </div>
      
      <!-- 配置表单 -->
      <div class="space-y-4">
        <!-- 学期选择 -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">学期 <span class="text-error">*</span></span>
          </label>
          <div class="relative">
            <select
              v-model="localConfig.semester_id"
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
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">年级 <span class="text-error">*</span></span>
          </label>
          <div class="relative">
            <select
              v-model="localConfig.grade_id"
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
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">学科 <span class="text-error">*</span></span>
          </label>
          <div class="relative">
            <select
              v-model="localConfig.subject_id"
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
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">分类 <span class="text-error">*</span></span>
          </label>
          <div class="relative">
            <select
              v-model="localConfig.category_id"
              class="select-modern w-full"
              :disabled="configStore.loading || !localConfig.subject_id"
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
        
        <!-- 加载状态 -->
        <div v-if="configStore.loading" class="flex items-center justify-center py-4">
          <span class="loading loading-spinner loading-md mr-2"></span>
          <span>加载中...</span>
        </div>
      </div>
      
      <!-- 对话框操作按钮 -->
      <div class="flex justify-end gap-4 mt-8 pt-6 border-t border-gray-200">
        <button
          class="btn-secondary-modern btn-modern-sm"
          @click="closeDialog"
          :disabled="saving"
        >
          取消
        </button>
        <button
          class="btn-primary-modern btn-modern-sm"
          @click="saveConfig"
          :disabled="!isConfigValid || saving"
        >
          <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          确定
        </button>
      </div>
    </div>
    
    <!-- 点击背景关闭 -->
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '../stores/config'
import { useQuestionsStore } from '../stores/questions'
import { cacheUtils } from '../utils/api'
import { message } from '../utils/message.js'

const router = useRouter()
const configStore = useConfigStore()
const questionsStore = useQuestionsStore()

const configDialog = ref(null)
const saving = ref(false)

// 本地配置状态
const localConfig = reactive({
  semester_id: '',
  grade_id: '',
  subject_id: '',
  category_id: ''
})

// 计算属性
const isConfigValid = computed(() => {
  return localConfig.semester_id && 
         localConfig.grade_id && 
         localConfig.subject_id && 
         localConfig.category_id
})

// 监听学科变化，重新加载分类
const onSubjectChange = async () => {
  localConfig.category_id = ''
  if (localConfig.subject_id) {
    await configStore.loadCategories(localConfig.subject_id)
  }
}

// 保存配置
const saveConfig = async () => {
  if (!isConfigValid.value) return

  try {
    saving.value = true

    // 保存到store
    configStore.setConfig(localConfig)

    // 强制清空试题数据，确保重新加载
    questionsStore.clearQuestions()

    // 清除相关缓存
    cacheUtils.clearPattern('questions')
    console.log('已清除试题相关缓存')

    // 强制重新加载试题数据
    const config = {
      semester_id: localConfig.semester_id,
      grade_id: localConfig.grade_id,
      subject_id: localConfig.subject_id,
      category_id: localConfig.category_id
    }

    console.log('配置已更新，强制重新加载试题数据...')
    await questionsStore.loadAllQuestions(config, true) // 第二个参数为true表示强制刷新

    // 关闭对话框
    closeDialog()

    // 检查是否有试题
    if (!questionsStore.hasQuestions) {
      message.warning('该配置下暂无试题，请选择其他配置', {
        description: '请尝试选择其他学期、年级、学科或分类'
      })
      return
    }

    console.log(`配置更新完成，已加载 ${questionsStore.totalQuestions} 道试题`)

    // 显示成功消息
    message.success('配置更新成功', {
      description: `已加载 ${questionsStore.totalQuestions} 道试题，开始练习吧！`,
      duration: 2500
    })

    // 如果不在试题页面，跳转到试题页面
    if (router.currentRoute.value.path !== '/questions') {
      router.push('/questions')
    }

  } catch (error) {
    console.error('保存配置失败:', error)
    message.error('保存配置失败', {
      description: '请检查网络连接后重试',
      duration: 4000
    })
  } finally {
    saving.value = false
  }
}

// 打开对话框
const openDialog = () => {
  // 同步当前配置到本地状态
  const currentConfig = configStore.getConfig()
  Object.assign(localConfig, {
    semester_id: currentConfig.semester_id || '',
    grade_id: currentConfig.grade_id || '',
    subject_id: currentConfig.subject_id || '',
    category_id: currentConfig.category_id || ''
  })
  
  // 如果有选择的学科，加载对应分类
  if (localConfig.subject_id) {
    configStore.loadCategories(localConfig.subject_id)
  }
  
  configDialog.value?.showModal()
}

// 关闭对话框
const closeDialog = () => {
  configDialog.value?.close()
}

// 监听全局事件
onMounted(() => {
  window.addEventListener('open-config-dialog', openDialog)
})
</script>

<style scoped>
.modal-box {
  max-height: 90vh;
  overflow-y: auto;
}
</style>
