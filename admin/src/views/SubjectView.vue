<template>
  <PageLayout
    title="学科管理"
    subtitle="管理学校的学科信息，设置学科颜色和排序"
  >
    <template #actions>
      <el-button
        type="primary"
        :icon="Plus"
        size="large"
      >
        添加学科
      </el-button>
    </template>

    <!-- 数据表格 -->
    <el-table :data="subjects" v-loading="loading" class="modern-table">
      <el-table-column prop="name" label="学科名称" min-width="200">
        <template #default="{ row }">
          <div class="subject-name">
            <div class="color-indicator" :style="{ backgroundColor: row.color }"></div>
            <span class="name-text">{{ row.name }}</span>
            <el-tag size="small" type="info" class="code-tag">{{ row.code }}</el-tag>
          </div>
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
const subjects = ref([])

onMounted(() => {
  loadSubjects()
})

async function loadSubjects() {
  loading.value = true
  try {
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    ElMessage.error('加载学科失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.subject-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.name-text {
  font-weight: 600;
  color: #2d3748;
  flex: 1;
}

.code-tag {
  flex-shrink: 0;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.color-block {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.color-text {
  font-size: 12px;
  color: #718096;
  font-family: monospace;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>
