<template>
  <div class="page">
    <!-- Top brand header that routes back to Home -->
    <header class="hero clickable" @click="$router.push({ name: 'Home' })">
      <h1 class="hero-title">PrepMate</h1>
      <p class="hero-tagline">
        <strong>AI Recipe Generator</strong>
      </p>
    </header>

    <!-- Existing form moved from Home.vue -->
    <section class="form-section">
      <h2 class="section-title">Recipe Generator</h2>
      <form @submit.prevent="onGenerateRecipe" class="recipe-form">
        <!-- Ingredients: multi-line text box -->
        <div class="form-group">
          <label for="ingredients">Ingredients</label>
          <textarea
            id="ingredients"
            v-model="ingredients"
            placeholder="chicken, rice, garlic, onions, pasta ..."
            rows="3"
          ></textarea>
        </div>

        <!-- Serving size: dropdown (1–10) -->
        <div class="form-group">
          <label for="servings">Serving Size</label>
          <select id="servings" v-model="servings">
            <option v-for="n in 10" :key="n" :value="n">
              {{ n }} {{ n === 1 ? 'Serving' : 'Servings' }}
            </option>
          </select>
        </div>

        <!-- Cuisine: dropdown -->
        <div class="form-group">
          <label for="cuisine">Cuisine</label>
          <select id="cuisine" v-model="cuisine">
            <option value="">No preference</option>
            <option value="american">American</option>
            <option value="italian">Italian</option>
            <option value="mexican">Mexican</option>
            <option value="indian">Indian</option>
            <option value="french">French</option>
            <option value="thai">Thai</option>
            <option value="greek">Greek</option>
            <option value="japanese">Japanese</option>
            <option value="spanish">Spanish</option>
            <option value="chinese">Chinese</option>
            <option value="russian">Russian</option>
            <option value="korean">Korean</option>
            <option value="ethiopian">Ethiopian</option>
            <option value="peruvian">Peruvian</option>
            <option value="moroccan">Moroccan</option>
          </select>
        </div>

        <!-- Dietary preferences: optional text -->
        <div class="form-group">
          <label for="dietary">Dietary Preferences</label>
          <input
            id="dietary"
            v-model="dietary"
            type="text"
            placeholder="vegetarian, gluten-free, low-carb ..."
          />
        </div>

        <!-- Main action button -->
        <button type="submit" class="btn-generate" :disabled="generating">
          {{ generating ? 'Generating...' : 'Generate My Recipe' }}
        </button>
      </form>

      <!-- Show a message after user clicks Generate -->
      <div
        v-if="recipeMessage"
        class="recipe-message"
        :class="recipeMessage.error ? 'error' : 'success'"
      >
        <div class="recipe-message-text">
          {{ recipeMessage.text }}
        </div>
        <button
          v-if="!recipeMessage.error"
          type="button"
          class="btn-secondary"
          @click="onAddToSaved"
        >
          Save Recipe
        </button>
      </div>
    </section>

    <!-- Developer backend test remains here for now -->
    <details class="dev-section">
      <summary>Backend Connection Test</summary>
      <div class="api-test">
        <button @click="testRootEndpoint">Test Root Endpoint</button>
        <button @click="testHealthEndpoint">Test Health Endpoint</button>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-if="error" class="error"><strong>Error:</strong> {{ error }}</div>
        <div v-if="response" class="response">
          <strong>Response:</strong>
          <pre>{{ JSON.stringify(response, null, 2) }}</pre>
        </div>
      </div>
    </details>
  </div>
</template>

<script>
import { ref } from 'vue'
import { getRootMessage, checkHealth, generateRecipe } from '@/services/example_api'
import { usePrepMateStore } from '@/store/prepMateStore'

export default {
  name: 'RecipeGenerator',
  setup() {
    const store = usePrepMateStore()

    // ----- Form state -----
    const ingredients = ref('')
    const servings = ref(2)
    const cuisine = ref('')
    const dietary = ref('')
    const generating = ref(false)
    const recipeMessage = ref(null)
    const lastRecipeText = ref('')

    // ----- Backend test state -----
    const loading = ref(false)
    const error = ref(null)
    const response = ref(null)

    // ----- When user clicks "Generate My Recipe" -----
    async function onGenerateRecipe() {
      recipeMessage.value = null

      if (!ingredients.value.trim()) {
        recipeMessage.value = { text: 'Please enter at least one ingredient.', error: true }
        return
      }

      generating.value = true

      try {
        const data = await generateRecipe({
          ingredients: ingredients.value,
          servings: servings.value,
          cuisine: cuisine.value || null,
          dietary: dietary.value || null
        })

        const text =
          data && data.recipeText
            ? data.recipeText
            : 'Recipe generated successfully, but no recipeText was returned from the server.'

        recipeMessage.value = {
          text,
          error: false
        }
        lastRecipeText.value = text
      } catch (err) {
        recipeMessage.value = {
          text: `There was a problem generating your recipe: ${err.message}`,
          error: true
        }
      } finally {
        generating.value = false
      }
    }

    function onAddToSaved() {
      if (!lastRecipeText.value) return
      store.addSavedRecipe({ text: lastRecipeText.value })
      // Optional feedback; you can later swap this for a nicer toast.
      alert('Recipe saved! Check the Saved Recipes page.')
    }

    // ----- Backend test functions -----
    const testRootEndpoint = async () => {
      loading.value = true
      error.value = null
      response.value = null
      try {
        const data = await getRootMessage()
        response.value = data
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const testHealthEndpoint = async () => {
      loading.value = true
      error.value = null
      response.value = null
      try {
        const data = await checkHealth()
        response.value = data
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    return {
      ingredients,
      servings,
      cuisine,
      dietary,
      generating,
      recipeMessage,
      lastRecipeText,
      onGenerateRecipe,
      onAddToSaved,
      loading,
      error,
      response,
      testRootEndpoint,
      testHealthEndpoint
    }
  }
}
</script>

<style scoped>
.page {
  max-width: 640px;
  margin: 0 auto;
  padding: 1rem;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}
.hero.clickable {
  cursor: pointer;
}
.hero-title {
  font-size: 1.75rem;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}
.hero-tagline {
  color: #555;
  line-height: 1.4;
  font-size: 1rem;
}
.form-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.section-title {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #222;
}
.recipe-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.form-group label {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}
.form-group textarea,
.form-group select,
.form-group input {
  padding: 0.6rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
}
.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.btn-generate {
  margin-top: 0.5rem;
  padding: 0.85rem 1.5rem;
  background: #2d8a5e;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-generate:hover:not(:disabled) {
  background: #247a50;
}
.btn-generate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  margin-top: 0.75rem;
  padding: 0.6rem 1.1rem;
  background: #607d8b;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-secondary:hover {
  background: #546e7a;
}

.recipe-message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.95rem;
}
.recipe-message.success {
  background: #e8f5e9;
  border: 1px solid #a5d6a7;
  color: #1b5e20;
}
.recipe-message.error {
  background: #ffebee;
  border: 1px solid #ef9a9a;
  color: #b71c1c;
}

.dev-section {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  background: #fafafa;
}
.dev-section summary {
  cursor: pointer;
  font-weight: 600;
  color: #555;
}
.api-test {
  margin-top: 1rem;
}
.api-test button {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem 1rem;
  background: #607d8b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}
.api-test button:hover {
  background: #546e7a;
}
.loading {
  margin-top: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}
.error {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #ffebee;
  border: 1px solid #ef9a9a;
  border-radius: 6px;
  color: #b71c1c;
  font-size: 0.9rem;
}
.response {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #e8f5e9;
  border: 1px solid #a5d6a7;
  border-radius: 6px;
  font-size: 0.9rem;
}
.response pre {
  margin-top: 0.5rem;
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.85rem;
}
</style>

