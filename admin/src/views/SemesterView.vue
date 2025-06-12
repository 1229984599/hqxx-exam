<template>
  <PageLayout
    title="学期管理"
    subtitle="管理学校的学期信息，设置学期状态和排序"
  >
    <CrudTable
      ref="crudTable"
      :data="crud.filteredData.value"
      :loading="crud.loading.value"
      :form="crud.form"
      :rules="rules"
      add-title="添加学期"
      edit-title="编辑学期"
      delete-confirm-field="name"
      show-add-button
      add-button-text="添加学期"
      @search="crud.handleSearch"
      @reset-filters="crud.resetFilters"
      @edit="crud.handleEdit"
      @delete="handleDelete"
      @submit="crud.handleSubmit"
    >
      <template #columns>
        <el-table-column prop="name" label="学期名称" min-width="200">
          <template #default="{ row }">
            <div class="semester-name">
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="学期代码" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
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
        <el-form-item label="学期名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入学期名称"/>
        </el-form-item>

        <el-form-item label="学期代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入学期代码"/>
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0"/>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active"/>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入学期描述（可选）"
          />
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
const crud = useCrud('/semesters/', {
  defaultForm: {
    name: '',
    code: '',
    sort_order: 0,
    is_active: true,
    description: ''
  },
  messages: {
    createSuccess: '学期创建成功',
    updateSuccess: '学期更新成功',
    deleteSuccess: '学期删除成功',
    loadError: '加载学期列表失败',
    createError: '创建学期失败',
    updateError: '更新学期失败',
    deleteError: '删除学期失败'
  }
})

// 表单验证规则
const rules = {
  name: commonRules.title,
  code: commonRules.code
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
.semester-name {
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
