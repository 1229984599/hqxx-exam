import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { findMenuByRoute } from '../utils/menuConfig'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      component: () => import('../layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        {
          path: 'semesters',
          name: 'semesters',
          component: () => import('../views/SemesterView.vue')
        },
        {
          path: 'grades',
          name: 'grades',
          component: () => import('../views/GradeView.vue')
        },
        {
          path: 'subjects',
          name: 'subjects',
          component: () => import('../views/SubjectView.vue')
        },
        {
          path: 'categories',
          name: 'categories',
          component: () => import('../views/CategoryView.vue')
        },
        {
          path: 'questions',
          name: 'questions',
          component: () => import('../views/QuestionView.vue')
        },
        {
          path: 'questions/add',
          name: 'question-add',
          component: () => import('../views/QuestionFormView.vue')
        },
        {
          path: 'questions/edit/:id',
          name: 'question-edit',
          component: () => import('../views/QuestionFormView.vue')
        },
        {
          path: 'templates',
          name: 'templates',
          component: () => import('../views/TemplateListView.vue')
        },
        {
          path: 'templates/add',
          name: 'template-add',
          component: () => import('../views/TemplateFormView.vue')
        },
        {
          path: 'templates/edit/:id',
          name: 'template-edit',
          component: () => import('../views/TemplateFormView.vue')
        },
        {
          path: 'tinymce-test',
          name: 'tinymce-test',
          component: () => import('../views/TinyMCETestView.vue')
        },
        {
          path: 'permission-help',
          name: 'permission-help',
          component: () => import('../views/PermissionHelpView.vue')
        },
        {
          path: 'permission-guide',
          name: 'permission-guide',
          component: () => import('../views/PermissionManagementGuideView.vue')
        },
        {
          path: 'system',
          name: 'system',
          component: () => import('../views/SystemView.vue')
        },
        {
          path: 'search',
          name: 'search',
          component: () => import('../views/SearchResultsView.vue')
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue')
        },
        {
          path: 'system/logs',
          name: 'system-logs',
          component: () => import('../views/SystemLogsView.vue')
        },
        {
          path: 'system/backup',
          name: 'backup-management',
          component: () => import('../views/BackupManagementView.vue')
        },
        {
          path: 'system/settings',
          name: 'system-settings',
          component: () => import('../views/SystemSettingsView.vue')
        },
        {
          path: 'users/admins',
          name: 'admin-management',
          component: () => import('../views/AdminManagementView.vue')
        },
        {
          path: 'users/roles',
          name: 'role-management',
          component: () => import('../views/RoleManagementView.vue')
        },
        {
          path: 'system/monitor',
          name: 'system-monitor',
          component: () => import('../views/SystemMonitorView.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 检查登录状态
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }

  // 检查页面权限（基于权限的PBAC）
  if (to.meta.requiresAuth && authStore.isAuthenticated) {
    const menuItem = findMenuByRoute(to.name)

    // 如果找到菜单配置且有权限要求
    if (menuItem && (menuItem.permissions || menuItem.roles)) {
      let hasAccess = false

      // 超级管理员可以访问所有页面
      if (authStore.isSuperuser) {
        hasAccess = true
      } else {
        // 优先检查权限，如果没有权限配置则检查角色
        if (menuItem.permissions) {
          if (Array.isArray(menuItem.permissions)) {
            hasAccess = authStore.hasAnyPermission(menuItem.permissions)
          } else {
            hasAccess = authStore.hasPermission(menuItem.permissions)
          }
        } else if (menuItem.roles) {
          // 兼容旧的角色配置
          if (Array.isArray(menuItem.roles)) {
            hasAccess = authStore.hasAnyRole(menuItem.roles)
          } else {
            hasAccess = authStore.hasRole(menuItem.roles)
          }
        }
      }

      if (!hasAccess) {
        ElMessage.error('权限不足，无法访问此页面')
        // 重定向到仪表板或上一页
        if (from.name) {
          next(false) // 阻止导航
        } else {
          next('/') // 重定向到仪表板
        }
        return
      }
    }
  }

  next()
})



export default router
