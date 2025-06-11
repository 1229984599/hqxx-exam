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
