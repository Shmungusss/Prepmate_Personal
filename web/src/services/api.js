const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const AUTH_STORAGE_KEY = 'prepMateAuth'

function getAuthHeaders() {
  if (typeof window === 'undefined') return {}
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return {}
    const auth = JSON.parse(raw)
    if (!auth?.id) return {}
    return { 'X-User-Id': String(auth.id) }
  } catch {
    return {}
  }
}

function jsonHeaders() {
  return { 'Content-Type': 'application/json', ...getAuthHeaders() }
}

/**
 * Calls the root endpoint to verify backend connection
 * @returns {Promise<Object>} Response with welcome message
 */
export async function getRootMessage() {
  const response = await fetch(`${API_BASE_URL}/`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

/**
 * Checks backend health status
 * @returns {Promise<Object>} Health status object
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}


/**
 * Generate a recipe from ingredients and preferences
 * @param {string} ingredients - Comma-separated ingredients string
 * @param {number} servings - Number of servings
 * @param {string} cuisine - Cuisine type
 * @param {string} dietary - Dietary restrictions string
 * @returns {Promise<Object>} Generated recipe object
 */
export async function generateRecipeFromIngredients(ingredients, servings, cuisine, dietary, cookingSkill = 'intermediate') {
  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-ingredients`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ingredients: ingredients,
      servings: servings,
      cuisine: cuisine || null,
      dietary_restrictions: dietary ? dietary.split(',').map(d => d.trim()) : null,
      cooking_skill: cookingSkill,
    })
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

/**
 * Generate a recipe from ingredients and preferences
 * @param {string} name - name of recipe
 * @param {number} servings - Number of servings
 * @param {string} dietary - Dietary restrictions string
 * @returns {Promise<Object>} Generated recipe object
 */
export async function generateRecipeFromName(name, servings, dietary, cookingSkill = 'intermediate') {
  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-name`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      recipe: name,
      servings: servings,
      dietary_restrictions: dietary ? dietary.split(',').map(d => d.trim()) : null,
      cooking_skill: cookingSkill,
    })
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

/**
 * Save recipe from a social media link (Instagram, Facebook, TikTok, YouTube, etc.)
 * Backend extracts recipe from the link and returns structured recipe.
 * @param {string} url - Full URL to the post/video
 * @returns {Promise<Object>} Recipe object (title, ingredients, instructions, etc.)
 */
export async function extractRecipeFromSocialLink(url) {
  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-link`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url.trim() })
  })

  if (!response.ok) {
    const errText = await response.text()
    throw new Error(errText || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

/**
 * Save recipe from an image (handwritten cards, cookbook, menu, dish photo).
 * Backend accepts multipart image and returns structured recipe.
 * @param {File} file - Image file (PNG, JPG, JPEG, WEBP, etc.)
 * @returns {Promise<Object>} Recipe object
 */
export async function extractRecipeFromImage(file) {
  const formData = new FormData()
  formData.append('image', file)

  const response = await fetch(`${API_BASE_URL}/api/recipes/from-image`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const errText = await response.text()
    throw new Error(errText || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}



/**
 * Save recipe from pasted or typed text. AI turns it into readable recipe instructions.
 * @param {string} text - Raw recipe text in any format
 * @returns {Promise<Object>} Recipe object
 */
export async function extractRecipeFromText(text) {
  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text.trim() })
  })

  if (!response.ok) {
    const errText = await response.text()
    throw new Error(errText || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}



/**
 * Fetch all saved recipes
 */
export async function fetchAllRecipes() {
  const response = await fetch(`${API_BASE_URL}/recipes`, {
    method: 'GET',
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch recipes: ${response.status}`)
  }
  return await response.json()
}

export async function registerUser(userData) {
  const response = await fetch(`${API_BASE_URL}/users/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  })
  if (!response.ok) {
    const err = await response.json().catch(() => null)
    throw new Error(err?.error?.message || err?.detail || `Failed to register user: ${response.status}`)
  }
  return await response.json()
}

export async function loginUser(credentials) {
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  })
  if (!response.ok) {
    const err = await response.json().catch(() => null)
    throw new Error(err?.error?.message || err?.detail || `Failed to login: ${response.status}`)
  }
  return await response.json()
}

export async function fetchGroceryLists() {
  const response = await fetch(`${API_BASE_URL}/grocery-lists`, {
    method: 'GET',
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch grocery lists: ${response.status}`)
  }
  return await response.json()
}

export async function createGroceryList(groceryList) {
  const response = await fetch(`${API_BASE_URL}/grocery-lists`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify(groceryList),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => null)
    throw new Error(err?.detail || `Failed to create grocery list: ${response.status}`)
  }
  return await response.json()
}

export async function updateGroceryList(listId, groceryList) {
  const response = await fetch(`${API_BASE_URL}/grocery-lists/${listId}`, {
    method: 'PUT',
    headers: jsonHeaders(),
    body: JSON.stringify(groceryList),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => null)
    throw new Error(err?.detail || `Failed to update grocery list: ${response.status}`)
  }
  return await response.json()
}

/**
 * Delete a recipe by ID
 */
export async function deleteRecipe(id) {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`, {
    method: 'DELETE'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to delete recipe: ${response.status}`)
  }
  
  return await response.json()
}

/**
 * Get a single recipe by ID
 */
export async function getRecipe(id) {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch recipe: ${response.status}`)
  }
  
  return await response.json()
}

// ── Pantry API ────────────────────────────────────────

export async function fetchPantryItems() {
  const res = await fetch(`${API_BASE_URL}/pantry/items`, {
    method: 'GET',
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch pantry: ${res.status}`)
  return res.json()
}

export async function createPantryItem(item) {
  const res = await fetch(`${API_BASE_URL}/pantry/items`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify(item),
  })
  if (!res.ok) throw new Error(`Failed to create pantry item: ${res.status}`)
  return res.json()
}

export async function bulkCreatePantryItems(items) {
  const res = await fetch(`${API_BASE_URL}/pantry/items/bulk`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ items }),
  })
  if (!res.ok) throw new Error(`Failed to bulk create pantry items: ${res.status}`)
  return res.json()
}

export async function updatePantryItem(id, patch) {
  const res = await fetch(`${API_BASE_URL}/pantry/items/${id}`, {
    method: 'PUT',
    headers: jsonHeaders(),
    body: JSON.stringify(patch),
  })
  if (!res.ok) throw new Error(`Failed to update pantry item: ${res.status}`)
  return res.json()
}

export async function deletePantryItem(id) {
  const res = await fetch(`${API_BASE_URL}/pantry/items/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Failed to delete pantry item: ${res.status}`)
}


/**
 * Look up a product by UPC barcode using Open Food Facts
 * @param {string} upc - The UPC/EAN barcode number
 * @returns {Promise<Object>} { name, brand, category, quantity, unit }
 */
export async function lookupBarcode(upc) {
  const response = await fetch(`${API_BASE_URL}/pantry/barcode/${upc}`)

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err?.detail || `Product not found (${response.status})`)
  }

  return await response.json()
}


/**
 * Scan a grocery receipt image and extract food items using vision AI
 * @param {File} file - Image file of the receipt
 * @returns {Promise<Object>} { items: [{ name, quantity, unit, category }] }
 */
export async function scanReceipt(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/pantry/scan-receipt`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  })

  if (!response.ok) {
    const errText = await response.text()
    throw new Error(errText || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}


// ── Meal Plan API ──────────────────────────────────────

export async function generateMealPlanDay(request) {
  const res = await fetch(`${API_BASE_URL}/meal-plans/generate/day`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify(request),
  })
  if (!res.ok) {
    const e = await res.json().catch(() => ({}))
    throw new Error(e?.detail || e?.error?.message || `Error ${res.status}`)
  }
  return res.json()
}

export async function saveMealPlan(plan) {
  const res = await fetch(`${API_BASE_URL}/meal-plans`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify(plan),
  })
  if (!res.ok) throw new Error(`Failed to save meal plan: ${res.status}`)
  return res.json()
}

export async function fetchMealPlans() {
  const res = await fetch(`${API_BASE_URL}/meal-plans`, {
    method: 'GET',
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch meal plans: ${res.status}`)
  return res.json()
}

export async function fetchMealPlan(id) {
  const res = await fetch(`${API_BASE_URL}/meal-plans/${id}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch meal plan: ${res.status}`)
  return res.json()
}

export async function deleteMealPlan(id) {
  const res = await fetch(`${API_BASE_URL}/meal-plans/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to delete meal plan: ${res.status}`)
}

export async function updatePlannedMeal(planId, date, mealType, recipeId) {
  const res = await fetch(`${API_BASE_URL}/meal-plans/${planId}/meals`, {
    method: 'PUT',
    headers: jsonHeaders(),
    body: JSON.stringify({ date, meal_type: mealType, recipe_id: recipeId }),
  })
  if (!res.ok) throw new Error(`Failed to update planned meal: ${res.status}`)
  return res.json()
}


/**
 * Save recipe
 * @param {string} recipe - Raw recipe text in any format
 */
export async function saveRecipe(recipe) {
  const response = await fetch(`${API_BASE_URL}/recipes/save`, {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify(recipe)
  })
  
  if (!response.ok) {
    throw new Error(`Failed to save recipe: ${response.status}`)
  }

  return await response.json()
}

export async function saveRecipeToCollection(recipeId) {
  const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/save-to-collection`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Failed to save recipe to collection: ${response.status}`)
  }
  return await response.json()
}