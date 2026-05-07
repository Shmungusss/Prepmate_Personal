import { reactive, computed } from 'vue'
import { fetchAllRecipes, deleteRecipe, fetchGroceryLists, createGroceryList, updateGroceryList } from '@/services/api'

const state = reactive({
  savedRecipes: [],
  loading: false,
  error: null,
  groceryItems: [],
  groceryListId: null,
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
    await loadGroceryList()
  } catch (error) {
    state.error = error.message
    console.error('Failed to load recipes or grocery list:', error)
  } finally {
    state.loading = false
  }
}

async function loadGroceryList() {
  try {
    const lists = await fetchGroceryLists()
    if (lists && lists.length) {
      const current = lists[0]
      state.groceryListId = current.id
      state.groceryItems = (current.items || []).map((item) => ({
        id: state.nextGroceryId++,
        name: item.name || '',
        amount: item.quantity != null ? String(item.quantity) : '',
        unit: item.unit || '',
        brand: item.brand || '',
        category: item.category || 'Other',
        checked: false,
        suggestedLocation: item.location || '',
      }))
    }
  } catch (error) {
    console.error('Failed to load saved grocery list:', error)
  }
}

async function saveCurrentGroceryList() {
  const groceryList = {
    title: 'Grocery List',
    items: state.groceryItems.map((item) => ({
      name: item.name,
      quantity: item.amount ? parseFloat(item.amount) : null,
      unit: item.unit || '',
      category: item.category || 'Other',
      estimated_price: null,
      notes: item.brand || '',
    })),
  }

  try {
    if (state.groceryListId) {
      const saved = await updateGroceryList(state.groceryListId, groceryList)
      if (saved && saved.id) {
        state.groceryListId = saved.id
      }
    } else {
      const saved = await createGroceryList(groceryList)
      if (saved && saved.id) {
        state.groceryListId = saved.id
      }
    }
  } catch (error) {
    console.error('Failed to save grocery list:', error)
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
function addGroceryItem({ name, amount, unit, category, brand, suggestedLocation }) {
  state.groceryItems.push({
    id: state.nextGroceryId++,
    name,
    amount: amount ?? '',
    unit: unit ?? '',
    brand: brand ?? '',
    category: category ?? 'Other',
    checked: false,
    suggestedLocation: suggestedLocation ?? '',
  })
  saveCurrentGroceryList()
}

function updateGroceryItem(id, patch) {
  const item = state.groceryItems.find((i) => i.id === id)
  if (!item) return
  Object.assign(item, patch)
  saveCurrentGroceryList()
}

function toggleGroceryItemChecked(id) {
  const item = state.groceryItems.find((i) => i.id === id)
  if (!item) return
  item.checked = !item.checked
  saveCurrentGroceryList()
}

function deleteGroceryItem(id) {
  state.groceryItems = state.groceryItems.filter(item => item.id !== id)
  saveCurrentGroceryList()
}

function clearGroceryItems() {
  state.groceryItems = []
  saveCurrentGroceryList()
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
    updateGroceryItem,
    toggleGroceryItemChecked,
    deleteGroceryItem,
    clearGroceryItems,
  }
}