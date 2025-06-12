<template>
  <PageLayout
    title="年级管理"
    subtitle="管理学校的年级信息，设置年级级别和排序"
  >
    <CrudTable
      ref="crudTable"
      :data="crud.filteredData.value"
      :loading="crud.loading.value"
      :form="crud.form"
      :rules="rules"
      add-title="添加年级"
      edit-title="编辑年级"
      delete-confirm-field="name"
      show-add-button
      add-button-text="添加年级"
      @search="crud.handleSearch"
      @reset-filters="crud.resetFilters"
      @edit="crud.handleEdit"
      @delete="handleDelete"
      @submit="crud.handleSubmit"
    >
      <template #filters="{ filters, resetFilters }">
        <!-- 搜索框 -->
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索年级名称或代码"
            :prefix-icon="Search"
            clearable
            style="width: 250px"
            @keyup.enter="crud.handleSearch"
          />
        </el-form-item>

        <!-- 状态筛选 -->
        <el-form-item>
          <el-select
            v-model="filters.is_active"
            placeholder="状态"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 级别筛选 -->
        <el-form-item>
          <el-select
            v-model="filters.level"
            placeholder="年级级别"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="level in 12"
              :key="level"
              :label="`第${level}级`"
              :value="level"
            />
          </el-select>
        </el-form-item>
      </template>

      <template #columns>
        <el-table-column prop="name" label="年级名称" min-width="200">
          <template #default="{ row }">
            <div class="grade-name">
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="年级代码" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="年级级别" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getLevelType(row.level)">
              第{{ row.level }}级
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="primary">{{ row.sort_order }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
      </template>

      <template #form-items="{ form }">
        <el-form-item label="年级名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入年级名称"/>
        </el-form-item>

        <el-form-item label="年级代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入年级代码"/>
        </el-form-item>

        <el-form-item label="年级级别" prop="level">
          <el-input-number v-model="form.level" :min="1" :max="12" placeholder="请输入年级级别"/>
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="1" placeholder="请输入排序"/>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active"/>
        </el-form-item>
      </template>
    </CrudTable>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useCrud, commonRules, formatDate } from '../composables/useCrud'
import CrudTable from '../components/CrudTable.vue'
import PageLayout from '../components/PageLayout.vue'

// 扩展筛选器以支持级别筛选
const extendedFilters = reactive({
  search: '',
  is_active: null,
  level: null
})

// 使用CRUD Composable（使用服务端筛选）
const crud = useCrud('/grades/', {
  defaultForm: {
    name: '',
    code: '',
    level: 1,
    sort_order: 1,
    is_active: true
  },
  messages: {
    createSuccess: '年级创建成功',
    updateSuccess: '年级更新成功',
    deleteSuccess: '年级删除成功',
    loadError: '加载年级列表失败',
    createError: '创建年级失败',
    updateError: '更新年级失败',
    deleteError: '删除年级失败'
  },
  clientFilter: false // 使用服务端筛选
})

// 扩展筛选逻辑 - 添加级别筛选字段
Object.assign(crud.filters, extendedFilters)

// 表单验证规则
const rules = {
  name: commonRules.name,
  code: commonRules.code,
  level: [
    { required: true, message: '请输入年级级别', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序', trigger: 'blur' }
  ]
}

// 组件引用
const crudTable = ref()

// 处理删除
async function handleDelete(row) {
  await crud.deleteData(row.id)
}

// 获取级别类型
function getLevelType(level) {
  if (level <= 3) return 'success'
  if (level <= 6) return 'info'
  if (level <= 9) return 'warning'
  return 'danger'
}

// 初始化加载数据
crud.loadData()
</script>

<style scoped>
.grade-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name-text {
  font-weight: 500;
  color: #2d3748;
}

.code-tag {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.date-text {
  color: #718096;
  font-size: 13px;
}
</style>
