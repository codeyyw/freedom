import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Stock from '@/views/Stock.vue'
import Fund from '@/views/Fund.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - 股票基金门户'
    }
  },
  {
    path: '/stocks',
    name: 'Stock',
    component: Stock,
    meta: {
      title: '股票市场 - 股票基金门户'
    }
  },
  {
    path: '/funds',
    name: 'Fund',
    component: Fund,
    meta: {
      title: '基金市场 - 股票基金门户'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router