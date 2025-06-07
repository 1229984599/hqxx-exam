import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

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
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
