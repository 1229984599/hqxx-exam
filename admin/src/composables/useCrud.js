import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'
import { formatDate } from '../utils/helpers'
import { commonValidationRules } from '../utils/validation'

/**
 * 通用CRUD操作Composable
 * @param {string} apiPath - API路径，如 '/semesters'
 * @param {Object} options - 配置选项
 */
export function useCrud(apiPath, options = {}) {
  const {
    // 默认表单数据
    defaultForm = {},
    // 是否支持分页
    pagination = false,
    // 是否支持前端筛选
    clientFilter = true,
    // 成功消息
    messages = {
      loadSuccess: '',
      loadError: '加载数据失败',
      createSuccess: '创建成功',
      createError: '创建失败',
      updateSuccess: '更新成功',
      updateError: '更新失败',
      deleteSuccess: '删除成功',
      deleteError: '删除失败'
    }
  } = options

  // 响应式数据
  const loading = ref(false)
  const submitting = ref(false)
  const allData = ref([])
  const form = reactive({ ...defaultForm })
  
  // 筛选器
  const filters = reactive({
    search: '',
    is_active: null
  })

  // 分页数据
  const paginationData = reactive({
    page: 1,
    size: 20,
    total: 0
  })

  // 计算属性 - 筛选后的数据
  const filteredData = computed(() => {
    if (!clientFilter) return allData.value
    
    let filtered = allData.value

    // 按状态筛选
    if (filters.is_active !== null) {
      filtered = filtered.filter(item => item.is_active === filters.is_active)
    }

    // 按搜索关键词筛选
    if (filters.search && typeof filters.search === 'string') {
      const searchLower = filters.search.toLowerCase()
      filtered = filtered.filter(item => {
        // 搜索name和code字段，确保字段存在且为字符串
        return (item.name && typeof item.name === 'string' && item.name.toLowerCase().includes(searchLower)) ||
               (item.code && typeof item.code === 'string' && item.code.toLowerCase().includes(searchLower)) ||
               (item.title && typeof item.title === 'string' && item.title.toLowerCase().includes(searchLower))
      })
    }

    return filtered
  })

  // 加载数据
  async function loadData(params = {}) {
    loading.value = true
    try {
      const queryParams = { ...params }
      
      if (pagination) {
        queryParams.page = paginationData.page
        queryParams.size = paginationData.size
      }

      if (!clientFilter) {
        // 服务端筛选 - 动态添加所有非空筛选字段
        Object.keys(filters).forEach(key => {
          const value = filters[key]
          if (value !== null && value !== undefined && value !== '') {
            queryParams[key] = value
          }
        })
      }

      const response = await api.get(apiPath, { params: queryParams })
      
      if (pagination && response.data.results) {
        allData.value = response.data.results
        paginationData.total = response.data.total
      } else {
        allData.value = response.data
      }

      if (messages.loadSuccess) {
        ElMessage.success(messages.loadSuccess)
      }
    } catch (error) {
      ElMessage.error(messages.loadError)
      console.error('Load data error:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建数据
  async function createData(data) {
    submitting.value = true
    try {
      await api.post(apiPath, data)
      ElMessage.success(messages.createSuccess)
      await loadData()
      resetForm()
      return true
    } catch (error) {
      ElMessage.error(messages.createError)
      console.error('Create data error:', error)
      return false
    } finally {
      submitting.value = false
    }
  }

  // 更新数据
  async function updateData(id, data) {
    submitting.value = true
    try {
      await api.put(`${apiPath}/${id}`, data)
      ElMessage.success(messages.updateSuccess)
      await loadData()
      resetForm()
      return true
    } catch (error) {
      ElMessage.error(messages.updateError)
      console.error('Update data error:', error)
      return false
    } finally {
      submitting.value = false
    }
  }

  // 删除数据
  async function deleteData(id) {
    try {
      await api.delete(`${apiPath}/${id}`)
      ElMessage.success(messages.deleteSuccess)
      await loadData()
      return true
    } catch (error) {
      ElMessage.error(messages.deleteError)
      console.error('Delete data error:', error)
      return false
    }
  }

  // 获取单个数据
  async function getData(id) {
    try {
      const response = await api.get(`${apiPath}/${id}`)
      return response.data
    } catch (error) {
      ElMessage.error('获取数据失败')
      console.error('Get data error:', error)
      return null
    }
  }

  // 重置表单
  function resetForm() {
    Object.assign(form, { ...defaultForm })
  }

  // 重置筛选器
  function resetFilters() {
    // 重置所有筛选器字段
    Object.keys(filters).forEach(key => {
      if (typeof filters[key] === 'string') {
        filters[key] = ''
      } else {
        filters[key] = null
      }
    })

    if (pagination) {
      paginationData.page = 1
    }
    loadData()
  }

  // 处理搜索
  function handleSearch(searchFilters = null) {
    // 如果传入了筛选器参数，更新本地筛选器
    if (searchFilters) {
      Object.assign(filters, searchFilters)
    }

    if (pagination) {
      paginationData.page = 1
    }
    loadData()
  }

  // 处理编辑
  function handleEdit(item) {
    Object.assign(form, { ...item })
  }

  // 处理提交
  async function handleSubmit({ isEdit, id, data }) {
    if (isEdit) {
      return await updateData(id, data)
    } else {
      return await createData(data)
    }
  }

  // 处理分页大小变化
  function handleSizeChange(size) {
    paginationData.size = size
    paginationData.page = 1
    loadData()
  }

  // 处理页码变化
  function handleCurrentChange(page) {
    paginationData.page = page
    loadData()
  }

  return {
    // 响应式数据
    loading,
    submitting,
    allData,
    filteredData,
    form,
    filters,
    pagination: paginationData,

    // 方法
    loadData,
    createData,
    updateData,
    deleteData,
    getData,
    resetForm,
    resetFilters,
    handleSearch,
    handleEdit,
    handleSubmit,
    handleSizeChange,
    handleCurrentChange
  }
}

// 导出常用验证规则（从validation.js导入）
export const commonRules = commonValidationRules

// 常用的难度等级映射
export const difficultyMap = {
  1: { text: '简单', type: 'success' },
  2: { text: '较易', type: 'info' },
  3: { text: '中等', type: 'warning' },
  4: { text: '较难', type: 'danger' },
  5: { text: '困难', type: 'danger' }
}

// 常用的题目类型映射
export const questionTypeMap = {
  'single': '单选题',
  'multiple': '多选题',
  'fill': '填空题',
  'essay': '问答题',
  'judge': '判断题'
}

// 工具函数
export function getDifficultyText(difficulty) {
  return difficultyMap[difficulty]?.text || '未知'
}

export function getDifficultyType(difficulty) {
  return difficultyMap[difficulty]?.type || 'info'
}

export function getQuestionTypeText(type) {
  return questionTypeMap[type] || type
}

// 导出格式化函数（从helpers.js导入）
export { formatDate }
