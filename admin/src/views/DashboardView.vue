<template>
  <PageLayout
    title="仪表板"
    subtitle="欢迎使用红旗小学考试系统管理后台"
  >
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon semester">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ stats.semesters }}</h3>
          <p>学期数量</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon grade">
          <el-icon><School /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ stats.grades }}</h3>
          <p>年级数量</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon subject">
          <el-icon><Reading /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ stats.subjects }}</h3>
          <p>学科数量</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon question">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ stats.questions }}</h3>
          <p>试题数量</p>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速操作</h2>
      <div class="action-grid">
        <div class="action-card" @click="$router.push('/questions')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Plus /></el-icon>
            </div>
            <h3>添加试题</h3>
            <p>创建新的考试题目，支持富文本编辑和注音功能</p>
          </div>
        </div>

        <div class="action-card" @click="$router.push('/categories')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Collection /></el-icon>
            </div>
            <h3>管理分类</h3>
            <p>管理题目分类，支持多级分类结构</p>
          </div>
        </div>

        <div class="action-card" @click="$router.push('/subjects')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><Reading /></el-icon>
            </div>
            <h3>管理学科</h3>
            <p>管理学科信息和相关配置</p>
          </div>
        </div>

        <div class="action-card" @click="$router.push('/grades')">
          <div class="action-content">
            <div class="action-icon">
              <el-icon><School /></el-icon>
            </div>
            <h3>管理年级</h3>
            <p>管理年级信息和级别设置</p>
          </div>
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Calendar,
  School,
  Reading,
  Document,
  Plus,
  Collection
} from '@element-plus/icons-vue'
import api from '../utils/api'
import PageLayout from '../components/PageLayout.vue'

const stats = ref({
  semesters: 0,
  grades: 0,
  subjects: 0,
  questions: 0
})

onMounted(async () => {
  await loadStats()
})

async function loadStats() {
  try {
    const [semestersRes, gradesRes, subjectsRes, questionsRes] = await Promise.all([
      api.get('/semesters/'),
      api.get('/grades/'),
      api.get('/subjects/'),
      api.get('/questions/', { params: { limit: 1 } })
    ])
    
    stats.value = {
      semesters: semestersRes.data.length,
      grades: gradesRes.data.length,
      subjects: subjectsRes.data.length,
      questions: questionsRes.data.length
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stat-icon.semester {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.grade {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.subject {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.question {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content h3 {
  font-size: 36px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-content p {
  color: #718096;
  font-size: 14px;
  font-weight: 500;
}

.quick-actions {
  margin-top: 32px;
}

.quick-actions h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.action-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
}

.action-content {
  text-align: center;
  padding: 32px 24px;
}

.action-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.action-card:hover .action-icon {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.action-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
}

.action-content p {
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .action-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .stat-card {
    padding: 20px;
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }

  .stat-content h3 {
    font-size: 28px;
  }

  .action-content {
    padding: 24px 20px;
  }

  .action-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }
}
</style>
