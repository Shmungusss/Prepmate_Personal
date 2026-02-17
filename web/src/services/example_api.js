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
 * Generates a recipe from the given inputs.
 *
 * NOTE FOR BACKEND:
 * - Endpoint: POST /api/recipes/generate
 * - Expected request body:
 *   {
 *     ingredients: string,
 *     servings: number,
 *     cuisine: string | null,
 *     dietary: string | null
 *   }
 * - Expected minimal response shape (for the current UI):
 *   {
 *     recipeText: string
 *   }
 *
 * The frontend will display `recipeText` directly. You can later expand this
 * to return a structured recipe object if needed.
 *
 * @param {Object} payload
 * @param {string} payload.ingredients
 * @param {number} payload.servings
 * @param {string} [payload.cuisine]
 * @param {string} [payload.dietary]
 * @returns {Promise<Object>} Response JSON from backend
 */
export async function generateRecipe(payload) {
  const response = await fetch(`${API_BASE_URL}/api/recipes/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}