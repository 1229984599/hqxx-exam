<template>
  <el-dialog
    v-model="visible"
    title="📋 插入模板"
    width="900px"
    :append-to-body="true"
    class="template-dialog"
    @close="handleClose"
  >
    <div class="template-container" v-loading="loading">
      <!-- 搜索和筛选 -->
      <div class="template-filters">
        <div class="filter-row">
          <el-input
            v-model="searchText"
            placeholder="搜索模板名称或描述..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            clearable
            class="category-select"
          >
            <el-option label="全部分类" value="" />
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </div>
      </div>

      <!-- 田字格文字替换功能 -->
      <div v-if="showTextReplaceInput && isTianzigeTemplate(selectedTemplate)" class="text-replace-section">
        <div class="replace-header">
          <h4>🔤 智能文字替换</h4>
          <p>输入要练习的文字，将自动替换到田字格模板中</p>
        </div>
        <div class="replace-input-area">
          <el-input
            v-model="replaceText"
            type="textarea"
            :rows="3"
            placeholder="请输入要练习的中文字符，例如：春夏秋冬"
            maxlength="100"
            show-word-limit
            class="replace-textarea"
          />

          <!-- 田字格参数设置 -->
          <div class="tianzige-settings">
            <div class="setting-row">
              <label>对齐方式：</label>
              <el-radio-group v-model="tianzigeAlignment" size="small">
                <el-radio label="center">居中对齐</el-radio>
                <el-radio label="left">左对齐</el-radio>
              </el-radio-group>
            </div>
            <div class="setting-row">
              <label>每行个数：</label>
              <el-input-number
                v-model="tianzigePerRow"
                :min="1"
                :max="10"
                size="small"
                style="width: 120px;"
              />
            </div>
          </div>

          <div class="replace-actions">
            <el-button @click="cancelTextReplace">取消</el-button>
            <el-button type="primary" @click="applyTextReplace" :disabled="!replaceText.trim()">
              应用替换
            </el-button>
          </div>
        </div>
      </div>

      <!-- 计算题算式替换功能 -->
      <div v-if="showTextReplaceInput && isCalculationTemplate(selectedTemplate)" class="text-replace-section">
        <div class="replace-header">
          <h4>🧮 智能算式替换</h4>
          <p>输入计算题，将自动替换到神机妙算模板中</p>
        </div>
        <div class="replace-input-area">
          <el-input
            v-model="replaceText"
            type="textarea"
            :rows="4"
            placeholder="请输入计算题，例如：18÷9=    49÷7=    81÷9=    7500-500="
            maxlength="500"
            show-word-limit
            class="replace-textarea"
          />
          <div class="replace-actions">
            <el-button @click="cancelTextReplace">取消</el-button>
            <el-button type="primary" @click="applyTextReplace" :disabled="!replaceText.trim()">
              应用替换
            </el-button>
          </div>
        </div>
      </div>

      <!-- 模板网格 -->
      <div class="template-grid" :class="{ 'hidden': showTextReplaceInput }">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          @click="handleTemplateClick(template)"
        >
          <div class="template-header">
            <div class="template-icon">{{ template.icon || '📄' }}</div>
            <div class="template-info">
              <h4 class="template-name">{{ template.name }}</h4>
              <p class="template-description">{{ template.description || '暂无描述' }}</p>
            </div>
          </div>
          <div class="template-meta">
            <el-tag size="small" type="primary">{{ template.category }}</el-tag>
            <el-tag v-if="template.subject" size="small" type="info">
              {{ template.subject.name }}
            </el-tag>
            <el-tag v-if="template.is_system" size="small" type="warning">系统模板</el-tag>
            <span class="usage-count">使用 {{ template.usage_count || 0 }} 次</span>
            <!-- 田字格模板标识 -->
            <el-tag v-if="isTianzigeTemplate(template)" size="small" type="success">
              🔤 支持文字替换
            </el-tag>
            <!-- 计算题模板标识 -->
            <el-tag v-if="isCalculationTemplate(template)" size="small" type="success">
              🧮 支持算式替换
            </el-tag>
          </div>
          <div class="template-preview" v-html="getTemplatePreview(template.content)"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredTemplates.length === 0 && !loading"
        description="未找到符合条件的模板"
        :image-size="100"
      />
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshTemplates">刷新模板</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, ref, watch} from 'vue'
import {Search} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import api from '../../../utils/api.js'
import {useAuthStore} from '../../../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'insert'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const searchText = ref('')
const selectedCategory = ref('')
const loading = ref(false)
const templates = ref([])
const authStore = useAuthStore()

// 文字替换功能
const showTextReplaceInput = ref(false)
const replaceText = ref('')
const selectedTemplate = ref(null)

// 田字格参数设置
const tianzigeAlignment = ref('center') // 对齐方式：center 或 left
const tianzigePerRow = ref(2) // 每行个数，默认2个

// 计算属性
const categories = computed(() => {
  const cats = [...new Set(templates.value.map(t => t.category))]
  return cats.sort()
})

const filteredTemplates = computed(() => {
  let filtered = templates.value

  // 按分类过滤
  if (selectedCategory.value) {
    filtered = filtered.filter(t => t.category === selectedCategory.value)
  }

  // 按搜索文本过滤
  if (searchText.value.trim()) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.name.toLowerCase().includes(search) ||
      (t.description && t.description.toLowerCase().includes(search))
    )
  }

  return filtered
})

// 方法
function getTemplatePreview(content) {
  if (!content) return ''

  // 移除HTML标签，只保留文本内容作为预览
  const text = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

// 判断是否为田字格模板
function isTianzigeTemplate(template) {
  if (!template.content) return false

  // 检查模板内容是否包含田字格相关的类名或结构
  const content = template.content.toLowerCase()
  return content.includes('tianzige') ||
         content.includes('田字格') ||
         template.name.includes('田字格') ||
         template.category === '田字格'
}

// 判断是否为计算题模板
function isCalculationTemplate(template) {
  if (!template || !template.content) return false



  // 检查模板内容是否包含计算题相关的类名或结构
  const content = template.content.toLowerCase()
  const name = template.name ? template.name.toLowerCase() : ''
  const category = template.category ? template.category.toLowerCase() : ''
  const description = template.description ? template.description.toLowerCase() : ''

  const isCalculation = content.includes('calculation') ||
         content.includes('神机妙算') ||
         content.includes('计算题') ||
         content.includes('{{calculation_') ||
         content.includes('🧮') ||
         name.includes('神机妙算') ||
         name.includes('计算题') ||
         name.includes('计算') ||
         category.includes('计算题') ||
         category.includes('神机妙算') ||
         category.includes('计算') ||
         description.includes('计算题') ||
         description.includes('算式')

  return isCalculation
}

// 处理模板点击
function handleTemplateClick(template) {


  if (isTianzigeTemplate(template) || isCalculationTemplate(template)) {
    // 如果是田字格模板或计算题模板，显示替换输入框
    selectedTemplate.value = template
    showTextReplaceInput.value = true
  } else {
    // 普通模板直接插入
    insertTemplate(template)
  }
}

// 取消文字替换
function cancelTextReplace() {
  showTextReplaceInput.value = false
  replaceText.value = ''
  selectedTemplate.value = null
  // 重置田字格参数为默认值
  tianzigeAlignment.value = 'center'
  tianzigePerRow.value = 2
}

// 应用文字替换
function applyTextReplace() {
  if (!selectedTemplate.value || !replaceText.value.trim()) return

  let processedTemplate
  if (isTianzigeTemplate(selectedTemplate.value)) {
    processedTemplate = replaceTemplateText(selectedTemplate.value, replaceText.value.trim())
  } else if (isCalculationTemplate(selectedTemplate.value)) {
    processedTemplate = replaceCalculationText(selectedTemplate.value, replaceText.value.trim())
  } else {
    processedTemplate = selectedTemplate.value
  }

  insertTemplate(processedTemplate)

  // 重置状态
  cancelTextReplace()
}

// 替换模板中的文字
function replaceTemplateText(template, newText) {
  if (!template.content) return template

  // 提取中文字符
  const chineseChars = newText.match(/[\u4e00-\u9fff]/g) || []

  if (chineseChars.length === 0) {
    ElMessage.warning('请输入中文字符')
    return template
  }

  // 显示解析结果
  ElMessage.success(`成功解析到 ${chineseChars.length} 个汉字`)

  // 根据参数生成田字格布局
  const generatedContent = generateTianzigeLayout(chineseChars, tianzigeAlignment.value, tianzigePerRow.value)

  return {
    ...template,
    content: generatedContent,
    name: `${template.name} - ${chineseChars.length}字`
  }
}

// 生成田字格布局
function generateTianzigeLayout(chars, alignment = 'center', perRow = 2) {
  // 基础田字格样式
  const tianzigeStyle = `display: inline-block; width: 80px; height: 80px; border: 2px solid #333; position: relative; margin: 4px; text-align: center; line-height: 80px; font-size: 32px; background: #fafafa;`
  const crossLineStyle = `position: absolute; background: #ccc; z-index: 1;`
  const horizontalLine = `top: 50%; left: 0; right: 0; height: 1px;`
  const verticalLine = `left: 50%; top: 0; bottom: 0; width: 1px;`
  const charStyle = `font-size: 60px; font-weight: bold; color: #000; font-family: '楷体', 'KaiTi', serif; user-select: text;position: relative; z-index: 2;`

  // 按每行个数分组
  const rows = []
  for (let i = 0; i < chars.length; i += perRow) {
    rows.push(chars.slice(i, i + perRow))
  }

  // 生成每行的田字格
  const rowsHtml = rows.map(rowChars => {
    const tianzigeItems = rowChars.map(char =>
      `<div class="tianzige-char" style="${tianzigeStyle}">
        <div style="${crossLineStyle} ${horizontalLine}"></div>
        <div style="${crossLineStyle} ${verticalLine}"></div>
        <span style="${charStyle}">${char}</span>
      </div>`
    ).join('')

    return `<div style="display: flex; ${alignment === 'center' ? 'justify-content: center;' : 'justify-content: flex-start;'} margin: 10px 0; flex-wrap: wrap;">
      ${tianzigeItems}
    </div>`
  }).join('')

  // 整体容器
  return `<div style="text-align: ${alignment}; padding: 20px;">
    <div style="margin: 0;">
      ${rowsHtml}
    </div>
  </div>`
}

// 提取田字格项目模板
function extractTianzigeItemTemplate(content) {
  // 查找第一个包含田字格的div作为模板
  const patterns = [
    // 匹配完整的田字格 div（包含 tianzige-char 类）
    /<div[^>]*class[^>]*tianzige-char[^>]*>.*?<\/div>/i,
    // 匹配任何包含中文字符的div
    /<div[^>]*>.*?[\u4e00-\u9fff].*?<\/div>/i,
    // 备用：查找任何包含样式的div
    /<div[^>]*style[^>]*>.*?<\/div>/i
  ]

  for (const pattern of patterns) {
    const match = content.match(pattern)
    if (match) {
      return match[0]
    }
  }

  // 如果没有找到合适的模板，使用默认田字格样式
  return `<div class="tianzige-char" style="display: inline-block; width: 80px; height: 80px; border: 2px solid #333; position: relative; margin: 4px; text-align: center; line-height: 80px; font-size: 32px; background: #fafafa;">
    <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #ccc; z-index: 1;"></div>
    <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #ccc; z-index: 1;"></div>
    <span style="position: relative; z-index: 2; color: #333;">字</span>
  </div>`
}

// 生成额外的田字格网格（保持与新逻辑一致，但保留以防需要）
function generateAdditionalTianzigeGrids(chars) {
  return chars.map(char =>
    `<div class="tianzige-char" style="display: inline-block; width: 80px; height: 80px; border: 2px solid #333; position: relative; margin: 4px; text-align: center; line-height: 80px; font-size: 32px; background: #fafafa;">
      <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #ccc; z-index: 1;"></div>
      <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #ccc; z-index: 1;"></div>
      <span style="position: relative; z-index: 2; color: #333;">${char}</span>
    </div>`
  ).join('')
}

// 替换计算题模板中的算式
function replaceCalculationText(template, newText) {
  if (!template.content) return template

  // 解析计算题文本，提取算式
  const calculations = parseCalculations(newText)

  if (calculations.length === 0) {
    ElMessage.warning('请输入有效的计算题，例如：18÷9= 或 27+3+5=')
    return template
  }

  // 显示解析结果
  ElMessage.success(`成功解析到 ${calculations.length} 个算式`)

  // 参考田字格的实现方式，直接生成完整的计算题布局
  const generatedContent = generateCalculationLayout(calculations)

  return {
    ...template,
    content: generatedContent,
    name: `${template.name} - ${calculations.length}题`
  }
}

// 生成计算题布局（根据用户输入的算式数量动态生成）
function generateCalculationLayout(calculations) {
  // 基础算式样式模板（从您的原模板中提取）
  const baseTemplate = `<p class="MsoNormal" style="text-align: center;">
    <strong><span style="font-family: '微软雅黑', 'Microsoft YaHei', Arial, sans-serif;font-size: 42px;">CALCULATION_PLACEHOLDER</span></strong>
  </p>`

  // 根据用户输入的算式数量动态生成相应数量的算式
  const calculationItems = calculations.map(calc =>
    baseTemplate.replace('CALCULATION_PLACEHOLDER', calc)
  ).join('')

  return calculationItems
}



// 解析计算题文本，提取算式
function parseCalculations(text) {
  if (!text) return []


  // 预处理：移除多余的空格和换行
  const cleanText = text.replace(/\s+/g, ' ').trim()

  // 更简单直接的匹配模式，考虑运算符和数字之间的空格
  const patterns = [
    // 匹配所有可能的算式格式，允许运算符前后有空格
    /\d+\s*[\+\-×÷\*\/]\s*\d+(?:\s*[\+\-×÷\*\/]\s*\d+)*\s*=?/g
  ]

  let allMatches = []

  // 使用所有模式匹配
  for (const pattern of patterns) {
    const matches = cleanText.match(pattern) || []
    allMatches = allMatches.concat(matches)
  }

  // 如果没有匹配到，尝试按空格分割
  if (allMatches.length === 0) {
    const parts = cleanText.split(/\s+/).filter(part => part.trim())
    for (const part of parts) {
      if (/\d+\s*[\+＋\-×÷\*\/]\s*\d+/.test(part)) {
        allMatches.push(part)
      }
    }
  }
  // 去重
  const uniqueMatches = [...new Set(allMatches)]

  return uniqueMatches.map(calc => {
    // 移除多余空格
    let cleaned = calc.replace(/\s+/g, '')

    // 统一运算符
    cleaned = cleaned.replace(/\*/g, '×').replace(/\//g, '÷').replace(/＋/g, '+')

    // 在所有运算符前后添加空格
    cleaned = cleaned.replace(/([+\-×÷])/g, ' $1 ')

    // 清理多余的空格
    cleaned = cleaned.replace(/\s+/g, ' ').trim()

    // 确保有等号
    if (!cleaned.endsWith('=')) {
      cleaned += ' ='
    } else {
      // 如果已经有等号，确保等号前有空格
      cleaned = cleaned.replace(/\s*=\s*$/, ' =')
    }

    return cleaned
  }).filter(calc => {
    // 过滤：必须包含运算符且长度合理
    return calc.length >= 4 && /[+\-×÷]/.test(calc)
  })
}

// 生成额外的计算题行（每行一个算式）
function generateAdditionalCalculationGrids(calculations) {
  return calculations.map(calc =>
    `<p style="text-align: center; margin: 20px 0; line-height: 1.8;">
      <strong><span style="font-family: '微软雅黑', 'Microsoft YaHei', Arial, sans-serif; font-size: 36px; color: #333;">${calc}</span></strong>
    </p>`
  ).join('')
}

async function insertTemplate(template) {
  try {
    // 检查是否已登录
    if (authStore.isAuthenticated) {
      // 增加使用次数
      await api.put(`/templates/${template.id}`, {
        usage_count: (template.usage_count || 0) + 1
      })

      // 更新本地数据
      template.usage_count = (template.usage_count || 0) + 1
    }

    emit('insert', template)
  } catch (error) {
    console.error('更新模板使用次数失败:', error)
    // 即使更新失败也继续插入模板
    emit('insert', template)
  }
}

function handleClose() {
  visible.value = false
}

async function refreshTemplates() {
  // 检查是否已登录
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }

  loading.value = true
  try {
    const response = await api.get('/templates/', {
      params: {
        is_active: true,
        limit: 100
      }
    })
    templates.value = response.data || []
    // ElMessage.success('模板列表已刷新')
  } catch (error) {
    console.error('获取模板失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法访问模板')
    } else {
      ElMessage.error('获取模板失败')
    }
  } finally {
    loading.value = false
  }
}

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal && templates.value.length === 0 && authStore.isAuthenticated) {
    refreshTemplates()
  }
})

// 不在组件挂载时自动加载，只在对话框打开时加载
</script>

<style scoped>
.template-container {
  max-height: 70vh;
  overflow-y: auto;
}

.template-filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  min-width: 300px;
  max-width: 500px;
}

.category-select {
  min-width: 180px;
}

/* 文字替换功能样式 */
.text-replace-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 2px solid #409eff;
}

.replace-header {
  margin-bottom: 15px;
}

.replace-header h4 {
  margin: 0 0 5px 0;
  color: #409eff;
  font-size: 16px;
  font-weight: 600;
}

.replace-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.replace-input-area {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.replace-textarea {
  font-size: 16px;
}

.replace-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 田字格参数设置样式 */
.tianzige-settings {
  background: #f0f9ff;
  border: 1px solid #e0f2fe;
  border-radius: 6px;
  padding: 15px;
  margin: 15px 0;
}

.setting-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.setting-row:last-child {
  margin-bottom: 0;
}

.setting-row label {
  min-width: 80px;
  font-size: 14px;
  color: #666;
  margin-right: 10px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px 0;
  transition: opacity 0.3s ease;
}

.template-grid.hidden {
  opacity: 0.3;
  pointer-events: none;
}

.template-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.template-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.template-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
}

.template-description {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.usage-count {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}

.template-preview {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 10px;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
  max-height: 60px;
  overflow: hidden;
  position: relative;
}

.template-preview::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, #f8f9fa);
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-input,
  .category-select {
    width: 100%;
    max-width: none;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .template-card {
    padding: 12px;
  }
  
  .template-header {
    gap: 10px;
  }
  
  .template-icon {
    font-size: 20px;
  }
  
  .template-name {
    font-size: 15px;
  }
  
  .template-description {
    font-size: 13px;
  }
}
</style>
