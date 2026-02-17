<template>
  <div class="page">
    <header class="header">
      <h1 class="title">Saved Recipes</h1>
      <p class="subtitle">
        Recipes you save from the generator will appear here. 
      </p>
    </header>

    <section v-if="!savedRecipes.length" class="placeholder">
      <p class="empty-state">
        You don’t have any saved recipes yet.
      </p>
      <p class="hint">
        Generate a recipe and favorite it to keep it here for later.
      </p>
    </section>

    <section v-else class="recipes">
      <article
        v-for="recipe in savedRecipes"
        :key="recipe.id"
        class="recipe-card"
      >
        <header class="recipe-header">
          <h2 class="recipe-title">Saved Recipe #{{ recipe.id }}</h2>
          <button
            type="button"
            class="btn-remove"
            @click="remove(recipe.id)"
          >
            Remove
          </button>
        </header>
        <pre class="recipe-text">
{{ recipe.text }}
        </pre>
        <div class="recipe-actions">
          <button
            type="button"
            class="btn-secondary"
            @click="onAddToGroceryPlaceholder"
          >
            Add to Grocery (coming soon)
          </button>
        </div>
      </article>
    </section>
  </div>
</template>

<script>
import { usePrepMateStore } from '@/store/prepMateStore'

export default {
  name: 'SavedRecipes',
  setup() {
    const store = usePrepMateStore()

    function remove(id) {
      store.removeSavedRecipe(id)
    }

    function onAddToGroceryPlaceholder() {
      alert('Adding ingredients from a recipe to your grocery list is coming in a future sprint.')
    }

    return {
      savedRecipes: store.savedRecipes,
      remove,
      onAddToGroceryPlaceholder
    }
  }
}
</script>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  margin-bottom: 1.5rem;
}

.title {
  font-size: 1.6rem;
  margin-bottom: 0.5rem;
  color: #222;
}

.subtitle {
  color: #666;
  font-size: 0.95rem;
}

.placeholder {
  padding: 1.5rem;
  border-radius: 12px;
  background: #f8f9fa;
  border: 1px dashed #cfd4da;
}

.empty-state {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.hint {
  color: #666;
  font-size: 0.9rem;
}

.recipes {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recipe-card {
  padding: 1rem;
  border-radius: 12px;
  background: #f8f9fa;
  border: 1px solid #e2e6ea;
}

.recipe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.recipe-title {
  font-size: 1rem;
  font-weight: 600;
  color: #222;
}

.recipe-text {
  white-space: pre-wrap;
  background: #ffffff;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #e2e6ea;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.recipe-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-secondary {
  padding: 0.45rem 1rem;
  background: #607d8b;
  color: white;
  border: none;
  border-radius: 999px;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #546e7a;
}

.btn-remove {
  padding: 0.3rem 0.75rem;
  background: transparent;
  color: #b00020;
  border: 1px solid #f2b8c6;
  border-radius: 999px;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-remove:hover {
  background: #ffebee;
}
</style>

