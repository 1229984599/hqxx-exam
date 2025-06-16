import { createRouter, createWebHistory,createWebHashHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Questions from '@/views/Questions.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '配置选择'
    }
  },
  {
    path: '/questions',
    name: 'Questions',
    component: Questions,
    meta: {
      title: '试题练习'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - 红旗小学考试系统`
  next()
})

export default router
