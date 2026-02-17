import { reactive, readonly, watch } from 'vue'

const STORAGE_KEY = 'prepMateStore'

function loadInitialState() {
  if (typeof window === 'undefined') {
    return {
      savedRecipes: [],
      groceryItems: [],
      nextIds: {
        recipe: 1,
        groceryItem: 1
      }
    }
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return {
        savedRecipes: [],
        groceryItems: [],
        nextIds: {
          recipe: 1,
          groceryItem: 1
        }
      }
    }
    const parsed = JSON.parse(raw)
    return {
      savedRecipes: parsed.savedRecipes || [],
      groceryItems: parsed.groceryItems || [],
      nextIds: parsed.nextIds || {
        recipe: 1,
        groceryItem: 1
      }
    }
  } catch {
    return {
      savedRecipes: [],
      groceryItems: [],
      nextIds: {
        recipe: 1,
        groceryItem: 1
      }
    }
  }
}

const state = reactive(loadInitialState())

function persist() {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      savedRecipes: state.savedRecipes,
      groceryItems: state.groceryItems,
      nextIds: state.nextIds
    })
  )
}

// Persist whenever state changes
watch(
  () => state,
  () => persist(),
  { deep: true }
)

function addSavedRecipe({ text }) {
  if (!text) return
  const id = state.nextIds.recipe++
  state.savedRecipes.unshift({
    id,
    text,
    createdAt: new Date().toISOString()
  })
}

function removeSavedRecipe(id) {
  state.savedRecipes = state.savedRecipes.filter((r) => r.id !== id)
}

function clearSavedRecipes() {
  state.savedRecipes = []
}

function addGroceryItem({ name, quantity }) {
  if (!name) return
  const id = state.nextIds.groceryItem++
  state.groceryItems.push({
    id,
    name,
    quantity: quantity || ''
  })
}

function updateGroceryItem(id, patch) {
  const item = state.groceryItems.find((i) => i.id === id)
  if (!item) return
  Object.assign(item, patch)
}

function deleteGroceryItem(id) {
  state.groceryItems = state.groceryItems.filter((i) => i.id !== id)
}

export function usePrepMateStore() {
  return {
    state: readonly(state),
    // Saved recipes
    savedRecipes: state.savedRecipes,
    addSavedRecipe,
    removeSavedRecipe,
    clearSavedRecipes,
    // Grocery items
    groceryItems: state.groceryItems,
    addGroceryItem,
    updateGroceryItem,
    deleteGroceryItem
  }
}

