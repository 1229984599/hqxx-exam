<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div :class="['sidebar', { collapsed: isCollapse }]">
      <div class="logo-section">
        <div class="logo-container">
          <div class="logo-icon">🏫</div>
          <div v-show="!isCollapse" class="logo-text">
            <h1 class="logo-title">红旗小学</h1>
            <p class="logo-subtitle">考试管理系统</p>
          </div>
        </div>
      </div>

      <nav class="nav-menu">
        <div style="margin-bottom: 8px" class="menu-item" :class="{ active: $route.name === 'dashboard' }" @click="$router.push('/')">
          <el-icon class="menu-icon"><Odometer /></el-icon>
          <span v-show="!isCollapse" class="menu-text" >仪表板</span>
        </div>

        <div class="menu-group">
          <div v-show="!isCollapse" class="menu-group-title">基础管理</div>

          <div class="menu-item" :class="{ active: $route.name === 'semesters' }" @click="$router.push('/semesters')">
            <el-icon class="menu-icon"><Calendar /></el-icon>
            <span v-show="!isCollapse" class="menu-text">学期管理</span>
          </div>

          <div class="menu-item" :class="{ active: $route.name === 'grades' }" @click="$router.push('/grades')">
            <el-icon class="menu-icon"><School /></el-icon>
            <span v-show="!isCollapse" class="menu-text">年级管理</span>
          </div>

          <div class="menu-item" :class="{ active: $route.name === 'subjects' }" @click="$router.push('/subjects')">
            <el-icon class="menu-icon"><Reading /></el-icon>
            <span v-show="!isCollapse" class="menu-text">学科管理</span>
          </div>

          <div class="menu-item" :class="{ active: $route.name === 'categories' }" @click="$router.push('/categories')">
            <el-icon class="menu-icon"><Collection /></el-icon>
            <span v-show="!isCollapse" class="menu-text">分类管理</span>
          </div>
        </div>

        <div class="menu-group">
          <div v-show="!isCollapse" class="menu-group-title">内容管理</div>

          <div class="menu-item" :class="{ active: ['questions', 'question-add', 'question-edit'].includes($route.name) }" @click="$router.push('/questions')">
            <el-icon class="menu-icon"><Document /></el-icon>
            <span v-show="!isCollapse" class="menu-text">试题管理</span>
          </div>

          <div class="menu-item" :class="{ active: ['templates', 'template-add', 'template-edit'].includes($route.name) }" @click="$router.push('/templates')">
            <el-icon class="menu-icon"><DocumentCopy /></el-icon>
            <span v-show="!isCollapse" class="menu-text">模板管理</span>
          </div>
        </div>

        <div class="menu-group">
          <div v-show="!isCollapse" class="menu-group-title">开发工具</div>

          <div class="menu-item" :class="{ active: $route.name === 'tinymce-test' }" @click="$router.push('/tinymce-test')">
            <el-icon class="menu-icon"><Edit /></el-icon>
            <span v-show="!isCollapse" class="menu-text">编辑器测试</span>
          </div>
        </div>
      </nav>
    </div>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <button class="collapse-btn" @click="toggleCollapse">
            <el-icon><component :is="isCollapse ? Expand : Fold" /></el-icon>
          </button>
          <div class="breadcrumb">
            <span class="breadcrumb-item">{{ getBreadcrumbText() }}</span>
          </div>
        </div>

        <div class="header-right">
          <div class="header-actions">
            <button class="action-btn">
              <el-icon><Bell /></el-icon>
            </button>
            <button class="action-btn">
              <el-icon><Setting /></el-icon>
            </button>
          </div>

          <el-dropdown @command="handleCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar :size="36" class="user-avatar">
                {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div v-show="!isCollapse" class="user-details">
                <span class="username">{{ authStore.user?.username }}</span>
                <span class="user-role">管理员</span>
              </div>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 主内容 -->
      <main class="main-content">
        <RouterView />
      </main>
    </div>

    <!-- Token状态显示 -->
    <TokenStatus :show="appStore.showTokenStatus" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import {
  Odometer,
  Setting,
  Document,
  DocumentCopy,
  Expand,
  Fold,
  ArrowDown,
  Bell,
  Calendar,
  School,
  Reading,
  Collection,
  Edit
} from '@element-plus/icons-vue'
import { useAuthStore, useAppStore } from '../stores'
import { ElMessage, ElMessageBox } from 'element-plus'
import TokenStatus from '../components/TokenStatus.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapsed)

function toggleCollapse() {
  appStore.toggleSidebar()
}

function getBreadcrumbText() {
  const routeNames = {
    'dashboard': '仪表板',
    'semesters': '学期管理',
    'grades': '年级管理',
    'subjects': '学科管理',
    'categories': '分类管理',
    'questions': '试题管理',
    'question-add': '试题管理 / 添加试题',
    'question-edit': '试题管理 / 编辑试题',
    'templates': '模板管理',
    'template-add': '模板管理 / 添加模板',
    'template-edit': '模板管理 / 编辑模板',
    'tinymce-test': '编辑器测试'
  }
  return routeNames[route.name] || '管理后台'
}

async function handleCommand(command) {
  switch (command) {
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
}

.sidebar.collapsed {
  width: 80px;
}

.logo-section {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.logo-text {
  flex: 1;
}

.logo-title {
  font-size: 20px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 12px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

.nav-menu {
  padding: 20px 0;
}

.menu-group {
  margin-bottom: 24px;
}

.menu-group-title {
  font-size: 12px;
  font-weight: 600;
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0 20px 12px;
  margin-bottom: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin: 0 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #4a5568;
  font-weight: 500;
}

.menu-item:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transform: translateX(4px);
}

.menu-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.menu-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #667eea;
}

.collapse-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.05);
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb-item {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #667eea;
}

.action-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.05);
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(102, 126, 234, 0.1);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.user-role {
  font-size: 12px;
  color: #718096;
}

.dropdown-icon {
  color: #a0aec0;
  transition: transform 0.3s ease;
}

.user-info:hover .dropdown-icon {
  transform: rotate(180deg);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }

  .sidebar.collapsed {
    width: 0;
  }

  .header {
    padding: 0 16px;
  }

  .breadcrumb-item {
    font-size: 16px;
  }
}

/* 滚动条样式优化 - 与主题融合 */
.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-track {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
  transform: scale(1.1);
}

/* 侧边栏滚动条样式 */
.nav-menu::-webkit-scrollbar {
  width: 6px;
}

.nav-menu::-webkit-scrollbar-track {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 3px;
}

.nav-menu::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-radius: 3px;
  transition: all 0.3s ease;
}

.nav-menu::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.4) 0%, rgba(118, 75, 162, 0.4) 100%);
}
</style>
