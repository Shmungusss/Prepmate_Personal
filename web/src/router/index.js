import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Recipes from '@/views/Recipes.vue'
import GroceryList from '@/views/GroceryList.vue'
import { useAuthStore } from '@/store/authStore'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/recipes',
    name: 'Recipes',
    component: Recipes
  },
  {
    path: '/grocery-list',
    name: 'GroceryList',
    component: GroceryList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated()
  if (to.name !== 'Home' && !isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
