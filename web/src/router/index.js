import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Recipes from '@/views/Recipes.vue'
import GroceryList from '@/views/GroceryList.vue'
import Pantry from '@/views/Pantry.vue'
import MealPlan from '@/views/MealPlan.vue'
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
  },
  {
    path: '/pantry',
    name: 'Pantry',
    component: Pantry
  },
  {
    path: '/meal-plan',
    name: 'MealPlan',
    component: MealPlan
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
