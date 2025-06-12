<template>
  <PageLayout
    title="学科管理"
    subtitle="管理学校的学科信息，设置学科颜色和排序"
  >
    <CrudTable
      ref="crudTable"
      :data="crud.filteredData.value"
      :loading="crud.loading.value"
      :form="crud.form"
      :rules="rules"
      add-title="添加学科"
      edit-title="编辑学科"
      delete-confirm-field="name"
      show-add-button
      add-button-text="添加学科"
      @search="crud.handleSearch"
      @reset-filters="crud.resetFilters"
      @edit="crud.handleEdit"
      @delete="handleDelete"
      @submit="crud.handleSubmit"
    >
      <template #columns>
        <el-table-column prop="name" label="学科名称" min-width="200">
          <template #default="{ row }">
            <div class="subject-name">
              <div class="color-indicator" :style="{ backgroundColor: row.color }"></div>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="学科代码" width="130">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="color" label="主题色" width="120" align="center">
          <template #default="{ row }">
            <div class="color-display">
              <div class="color-block" :style="{ backgroundColor: row.color }"></div>
              <span class="color-text">{{ row.color }}</span>
            </div>
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
        <el-form-item label="学科名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入学科名称" />
        </el-form-item>

        <el-form-item label="学科代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入学科代码" />
        </el-form-item>

        <el-form-item label="主题色" prop="color">
          <el-color-picker v-model="form.color" />
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="1" placeholder="请输入排序" />
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </template>
    </CrudTable>
  </PageLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useCrud, commonRules, formatDate } from '../composables/useCrud'
import CrudTable from '../components/CrudTable.vue'
import PageLayout from '../components/PageLayout.vue'

// 使用CRUD Composable
const crud = useCrud('/subjects/', {
  defaultForm: {
    name: '',
    code: '',
    color: '#667eea',
    sort_order: 1,
    is_active: true
  },
  messages: {
    createSuccess: '学科创建成功',
    updateSuccess: '学科更新成功',
    deleteSuccess: '学科删除成功',
    loadError: '加载学科列表失败',
    createError: '创建学科失败',
    updateError: '更新学科失败',
    deleteError: '删除学科失败'
  }
})

// 表单验证规则
const rules = {
  name: commonRules.name,
  code: commonRules.code,
  color: [
    { required: true, message: '请选择主题色', trigger: 'blur' }
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

// 初始化加载数据
crud.loadData()
</script>

<style scoped>
.subject-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.name-text {
  font-weight: 500;
  color: #2d3748;
}

.code-tag {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-block {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.color-text {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #666;
}

.date-text {
  color: #718096;
  font-size: 13px;
}
</style>
