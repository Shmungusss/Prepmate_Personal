import { reactive, computed } from 'vue'
import { fetchAllRecipes, deleteRecipe } from '@/services/api'

const state = reactive({
  savedRecipes: [],
  loading: false,
  error: null,
  groceryItems: [],
  nextGroceryId: 1,
})

// ─────────────────────────────────────────────
// RECIPES
// ─────────────────────────────────────────────
async function initialize() {
  state.loading = true
  state.error = null
  try {
    state.savedRecipes = await fetchAllRecipes()
  } catch (error) {
    state.error = error.message
    console.error('Failed to load recipes:', error)
  } finally {
    state.loading = false
  }
}

async function refreshRecipes() {
  try {
    state.savedRecipes = await fetchAllRecipes()
  } catch (error) {
    state.error = error.message
    console.error('Failed to refresh recipes:', error)
  }
}

function addRecipeToState(recipe) {
  state.savedRecipes.unshift(recipe)
}

async function removeSavedRecipe(id) {
  const backup = [...state.savedRecipes]
  state.savedRecipes = state.savedRecipes.filter(r => r.id !== id)
  try {
    await deleteRecipe(id)
  } catch (error) {
    state.savedRecipes = backup
    state.error = error.message
    throw error
  }
}

// ─────────────────────────────────────────────
// GROCERY LIST (local only, no backend yet)
// ─────────────────────────────────────────────
function addGroceryItem({ name, quantity }) {
  state.groceryItems.push({
    id: state.nextGroceryId++,
    name,
    quantity,
  })
}

function deleteGroceryItem(id) {
  state.groceryItems = state.groceryItems.filter(item => item.id !== id)
}

// ─────────────────────────────────────────────
// EXPORTS
// ─────────────────────────────────────────────
export function usePrepMateStore() {
  return {
    savedRecipes: computed(() => state.savedRecipes),
    loading: computed(() => state.loading),
    error: computed(() => state.error),
    groceryItems: computed(() => state.groceryItems),

    initialize,
    refreshRecipes,
    addRecipeToState,
    removeSavedRecipe,
    addGroceryItem,
    deleteGroceryItem,
  }
}