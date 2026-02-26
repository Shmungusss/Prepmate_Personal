const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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
export async function generateRecipeFromIngredients(ingredients, servings, cuisine, dietary) {
  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-ingredients`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ingredients: ingredients,
      servings: servings,
      cuisine: cuisine || null,
      dietary_restrictions: dietary ? dietary.split(',').map(d => d.trim()) : null
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
export async function generateRecipeFromName(name, servings, dietary) {
  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-name`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      recipe: name,
      servings: servings,
      dietary_restrictions: dietary ? dietary.split(',').map(d => d.trim()) : null
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

  const response = await fetch(`${API_BASE_URL}/recipe/generate/from-image`, {
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
    headers: { 'Content-Type': 'application/json' }
  })
  console.log(response)
  if (!response.ok) {
    throw new Error(`Failed to fetch recipes: ${response.status}`)
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

/**
 * Save recipe
 * @param {string} recipe - Raw recipe text in any format
 */
export async function saveRecipe(recipe) {
  const response = await fetch(`${API_BASE_URL}/recipes/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(recipe)
  })
  
  if (!response.ok) {
    throw new Error(`Failed to save recipe: ${response.status}`)
  }
  
  return await response.json()
}