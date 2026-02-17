import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import RecipeGenerator from '@/views/RecipeGenerator.vue'
import SavedRecipes from '@/views/SavedRecipes.vue'
import GroceryList from '@/views/GroceryList.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/recipe-generator',
    name: 'RecipeGenerator',
    component: RecipeGenerator
  },
  {
    path: '/saved-recipes',
    name: 'SavedRecipes',
    component: SavedRecipes
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

export default router
