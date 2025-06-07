<template>
  <PageLayout
    title="年级管理"
    subtitle="管理学校的年级信息，设置年级级别和排序"
  >
    <template #actions>
      <el-button
        type="primary"
        :icon="Plus"
        size="large"
      >
        添加年级
      </el-button>
    </template>

    <!-- 数据表格 -->
    <el-table :data="grades" v-loading="loading" class="modern-table">
      <el-table-column prop="name" label="年级名称" min-width="200">
        <template #default="{ row }">
          <div class="grade-name">
            <span class="name-text">{{ row.name }}</span>
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </div>
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
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" :icon="Edit" />
            <el-button size="small" type="danger" :icon="Delete" />
          </div>
        </template>
      </el-table-column>
    </el-table>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const loading = ref(false)
const grades = ref([])

onMounted(() => {
  loadGrades()
})

async function loadGrades() {
  loading.value = true
  try {
    const response = await api.get('/grades/')
    grades.value = response.data
  } catch (error) {
    ElMessage.error('加载年级失败')
  } finally {
    loading.value = false
  }
}

function getLevelType(level) {
  const types = { 1: 'primary', 2: 'success', 3: 'warning', 4: 'danger', 5: 'info', 6: 'danger' }
  return types[level] || 'info'
}
</script>

<style scoped>
.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.grade-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name-text {
  font-weight: 600;
  color: #2d3748;
  flex: 1;
}

.code-tag {
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>
