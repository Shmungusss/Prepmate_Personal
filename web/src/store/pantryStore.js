import { reactive, computed } from 'vue'
import {
  fetchPantryItems,
  createPantryItem,
  bulkCreatePantryItems,
  updatePantryItem,
  deletePantryItem,
} from '@/services/api'

const PANTRY_KEY = 'prepMatePantry'
const MIGRATED_KEY = 'prepMatePantryMigrated'

export const PANTRY_LOCATIONS = [
  { value: 'fridge',  label: 'Fridge' },
  { value: 'freezer', label: 'Freezer' },
  { value: 'pantry',  label: 'Pantry' },
  { value: 'spices',  label: 'Spices' },
]

export const PANTRY_CATEGORIES = [
  'Produce',
  'Dairy & Eggs',
  'Meat & Seafood',
  'Grains & Bread',
  'Pantry Staples',
  'Beverages',
  'Other',
]

const state = reactive({
  items: [],
  loading: false,
  error: null,
})

// ── Migration: move localStorage items to DB once ──────
async function migrateFromLocalStorage() {
  if (localStorage.getItem(MIGRATED_KEY)) return
  try {
    const raw = localStorage.getItem(PANTRY_KEY)
    if (!raw) { localStorage.setItem(MIGRATED_KEY, '1'); return }
    const parsed = JSON.parse(raw)
    const localItems = parsed?.items || []
    if (!localItems.length) { localStorage.setItem(MIGRATED_KEY, '1'); return }

    const payload = localItems.map((i) => ({
      name: i.name || '',
      quantity: i.quantity != null ? String(i.quantity) : '',
      unit: i.unit || '',
      location: i.location || 'pantry',
      category: i.category || 'Other',
      added_at: i.addedAt || null,
    }))

    const saved = await bulkCreatePantryItems(payload)
    state.items = saved
    localStorage.removeItem(PANTRY_KEY)
    localStorage.setItem(MIGRATED_KEY, '1')
    console.log(`[PrepMate] Migrated ${saved.length} pantry items from localStorage to database.`)
  } catch (err) {
    console.error('[PrepMate] Pantry migration failed:', err)
  }
}

// ── Load from DB ───────────────────────────────────────
async function initialize() {
  state.loading = true
  state.error = null
  try {
    await migrateFromLocalStorage()
    state.items = await fetchPantryItems()
  } catch (err) {
    state.error = err.message
  } finally {
    state.loading = false
  }
}

// ── CRUD ───────────────────────────────────────────────
async function addItem({ name, quantity, unit, location, category }) {
  const item = await createPantryItem({
    name: name.trim(),
    quantity: quantity != null ? String(quantity) : '',
    unit: unit || '',
    location: location || 'pantry',
    category: category || 'Other',
    added_at: new Date().toISOString(),
  })
  state.items.push(item)
}

async function updateItem(id, patch) {
  const updated = await updatePantryItem(id, patch)
  const idx = state.items.findIndex((i) => i.id === id)
  if (idx !== -1) state.items[idx] = updated
}

async function removeItem(id) {
  await deletePantryItem(id)
  state.items = state.items.filter((i) => i.id !== id)
}

async function clearAll() {
  await Promise.all(state.items.map((i) => deletePantryItem(i.id)))
  state.items = []
}

// ── Export ─────────────────────────────────────────────
export function usePantryStore() {
  return {
    items: computed(() => state.items),
    loading: computed(() => state.loading),
    error: computed(() => state.error),
    initialize,
    addItem,
    updateItem,
    removeItem,
    clearAll,
  }
}
