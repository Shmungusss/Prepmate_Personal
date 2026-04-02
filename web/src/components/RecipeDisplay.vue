<template>
    <div class="recipe-display">
      <!-- Header: Title + meta info -->
      <header class="recipe-header">
        <h2 class="recipe-title">{{ recipe.title }}</h2>
        <p class="recipe-description">{{ recipe.description }}</p>
        
        <div class="recipe-meta">
          <span class="meta-badge">
            <span class="meta-icon">🍴</span>
            {{ recipe.servings }} {{ recipe.servings === 1 ? 'serving' : 'servings' }}
          </span>
          <span class="meta-badge">
            <span class="meta-icon">⏱</span>
            {{ recipe.total_time_minutes }} min
          </span>
          <span class="meta-badge">
            <span class="meta-icon">📊</span>
            {{ recipe.difficulty }}
          </span>
          <span class="meta-badge" v-if="recipe.cuisine">
            <span class="meta-icon">🌍</span>
            {{ formatCuisine(recipe.cuisine) }}
          </span>
        </div>
      </header>
  
      <!-- Tabbed content -->
      <div class="recipe-tabs">
        <!-- Tab buttons -->
        <div class="tab-buttons">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>
  
        <!-- Tab panels -->
        <div class="tab-content">
          <!-- Ingredients tab -->
          <Transition name="tab-fade" mode="out-in">
            <div v-if="activeTab === 'ingredients'" key="ingredients" class="tab-panel">
              <ul class="ingredients-list">
                <li
                  v-for="(ingredient, idx) in recipe.ingredients"
                  :key="idx"
                  class="ingredient-item"
                >
                  <input
                    type="checkbox"
                    :id="`${idPrefix}-ing-${idx}`"
                    class="ingredient-checkbox"
                    :checked="isIngredientChecked(idx)"
                    @change="toggleIngredientChecked(idx)"
                  />
                  <label :for="`${idPrefix}-ing-${idx}`" class="ingredient-label">
                    <span class="ingredient-qty">
                      {{ formatQuantity(ingredient.quantity) }} {{ ingredient.unit }}
                    </span>
                    <span class="ingredient-name">{{ ingredient.name }}</span>
                    <span v-if="ingredient.notes" class="ingredient-notes">
                      — {{ ingredient.notes }}
                    </span>
                    <span v-if="ingredient.optional" class="optional-tag">optional</span>
                  </label>
                </li>
              </ul>
            </div>
  
            <!-- Steps tab -->
            <div v-else-if="activeTab === 'steps'" key="steps" class="tab-panel">
              <ol class="steps-list">
                <li
                  v-for="step in recipe.instructions"
                  :key="step.step_number"
                  class="step-item"
                >
                  <input
                    type="checkbox"
                    :id="`${idPrefix}-step-${step.step_number}`"
                    class="step-checkbox"
                  />
                  <label :for="`${idPrefix}-step-${step.step_number}`" class="step-label">
                    <span class="step-number">{{ step.step_number }}</span>
                    <span class="step-text">{{ step.instruction }}</span>
                  </label>
                </li>
              </ol>
            </div>
  
            <!-- Tips tab -->
            <div v-else-if="activeTab === 'tips'" key="tips" class="tab-panel">
              <ul class="tips-list" v-if="recipe.tips && recipe.tips.length">
                <li v-for="(tip, idx) in recipe.tips" :key="idx" class="tip-item">
                  <span class="tip-icon">💡</span>
                  <span class="tip-text">{{ tip }}</span>
                </li>
              </ul>
              <p v-else class="empty-state">No tips available for this recipe.</p>
            </div>
          </Transition>
        </div>
      </div>
  
      <!-- Action buttons -->
      <div v-if="!hideActions || showAddToGrocery || showMadeThis || showSaveToCollection" class="recipe-actions">
        <button
          v-if="!hideActions"
          class="action-btn action-btn--secondary"
          @click="$emit('close')"
        >
          ← Generate Another
        </button>
        <button
          v-if="!hideActions"
          class="action-btn action-btn--primary"
          @click="$emit('save')"
        >
          💾 Save Recipe
        </button>
        <button
          v-if="showAddToGrocery"
          class="action-btn action-btn--primary"
          @click="emitAddUncheckedToGrocery"
        >
          Add unchecked to Grocery
        </button>
        <button
          v-if="showMadeThis"
          class="action-btn action-btn--cook"
          @click="$emit('made-this')"
        >
          🍳 I made this
        </button>
        <button
          v-if="showSaveToCollection"
          class="action-btn action-btn--primary"
          @click="$emit('save-to-collection')"
        >
          💾 Save to My Recipes
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, watch } from 'vue'
  
  export default {
    name: 'RecipeDisplay',
  
    props: {
      recipe: {
        type: Object,
        required: true,
      },
      hideActions: {
        type: Boolean,
        default: false,
      },
      showAddToGrocery: {
        type: Boolean,
        default: false,
      },
      showMadeThis: {
        type: Boolean,
        default: false,
      },
      showSaveToCollection: {
        type: Boolean,
        default: false,
      },
      idPrefix: {
        type: String,
        default: 'recipe',
      },
    },

    emits: ['close', 'save', 'add-to-grocery', 'made-this', 'save-to-collection'],
  
    setup(props, { emit }) {
      const activeTab = ref('ingredients')
      const checkedIngredientIdxs = ref(new Set())
  
      const tabs = [
        { id: 'ingredients', label: 'Ingredients' },
        { id: 'steps', label: 'Steps' },
        { id: 'tips', label: 'Tips' },
      ]

      watch(
        () => props.recipe,
        () => {
          checkedIngredientIdxs.value = new Set()
          activeTab.value = 'ingredients'
        }
      )

      function isIngredientChecked(idx) {
        return checkedIngredientIdxs.value.has(idx)
      }

      function toggleIngredientChecked(idx) {
        const next = new Set(checkedIngredientIdxs.value)
        if (next.has(idx)) next.delete(idx)
        else next.add(idx)
        checkedIngredientIdxs.value = next
      }

      function emitAddUncheckedToGrocery() {
        const ingredients = props.recipe?.ingredients || []
        const unchecked = ingredients.filter((_, idx) => !checkedIngredientIdxs.value.has(idx))
        emit('add-to-grocery', unchecked)
      }
  
      function formatQuantity(qty) {
        // Handle fractions nicely
        if (qty === 0.25) return '¼'
        if (qty === 0.5) return '½'
        if (qty === 0.75) return '¾'
        if (qty === 0.33 || qty === 0.333) return '⅓'
        if (qty === 0.67 || qty === 0.666) return '⅔'
        
        // Remove .0 from whole numbers
        return qty % 1 === 0 ? qty.toString() : qty.toString()
      }
  
      function formatCuisine(cuisine) {
        // Capitalize first letter
        return cuisine.charAt(0).toUpperCase() + cuisine.slice(1)
      }
  
      return {
        activeTab,
        isIngredientChecked,
        toggleIngredientChecked,
        emitAddUncheckedToGrocery,
        tabs,
        formatQuantity,
        formatCuisine,
      }
    },
  }
  </script>
  
  <style scoped>
  .recipe-display {
  font-family: var(--prep-font-body);
  background: var(--prep-card);
  border-radius: 16px;
  padding: 1.75rem 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--prep-border);
  height: 100%;
  overflow: hidden;
  color: var(--prep-text);
}

  /* ── Header ───────────────────────────────── */
  .recipe-header {
    border-bottom: 2px solid var(--prep-border);
    padding-bottom: 1.25rem;
  }
  
  .recipe-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--prep-text);
    margin: 0 0 0.5rem;
    letter-spacing: -0.02em;
    line-height: 1.3;
  }
  
  .recipe-description {
    font-size: 0.95rem;
    color: var(--prep-muted);
    margin: 0 0 1rem;
    line-height: 1.6;
  }
  
  .recipe-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
  }
  
  .meta-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.4rem 0.75rem;
    background: rgba(0, 200, 180, 0.12);
    border: 1px solid var(--prep-primary);
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--prep-primary);
  }
  
  .meta-icon {
    font-size: 1rem;
    line-height: 1;
  }
  
  /* ── Tabs ─────────────────────────────────── */
  .recipe-tabs {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  
  .tab-buttons {
    display: flex;
    gap: 0.5rem;
    border-bottom: 2px solid var(--prep-border);
    margin-bottom: 1.25rem;
  }
  
  .tab-btn {
    padding: 0.65rem 1.25rem;
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--prep-muted);
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: -2px;
    font-family: inherit;
  }
  
  .tab-btn:hover {
    color: var(--prep-primary);
    background: rgba(0, 200, 180, 0.08);
    border-radius: 8px 8px 0 0;
  }
  
  .tab-btn.active {
    color: var(--prep-primary);
    border-bottom-color: var(--prep-primary);
  }
  
  .tab-content {
    flex: 1;
    overflow-y: auto;
    min-height: 0;       
}
  
  .tab-panel {
    animation: slideIn 0.3s ease;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* ── Ingredients list ─────────────────────── */
  .ingredients-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
  }
  
  .ingredient-item {
    display: flex;
    align-items: flex-start;
  }
  
  .ingredient-checkbox {
    margin-right: 0.65rem;
    margin-top: 0.25rem;
    cursor: pointer;
    width: 17px;
    height: 17px;
    accent-color: var(--prep-primary);
    flex-shrink: 0;
  }
  
  .ingredient-label {
    cursor: pointer;
    line-height: 1.6;
    font-size: 0.92rem;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.35rem;
  }
  
  .ingredient-checkbox:checked + .ingredient-label {
    opacity: 0.5;
    text-decoration: line-through;
  }
  
  .ingredient-qty {
    font-weight: 700;
    color: var(--prep-primary);
    white-space: nowrap;
  }
  
  .ingredient-name {
    font-weight: 600;
    color: var(--prep-text);
  }
  
  .ingredient-notes {
    font-weight: 400;
    color: var(--prep-muted);
    font-style: italic;
  }
  
  .optional-tag {
    font-size: 0.75rem;
    padding: 0.15rem 0.45rem;
    background: rgba(0, 200, 180, 0.2);
    color: var(--prep-primary);
    border-radius: 4px;
    font-weight: 600;
  }
  
  /* ── Steps list ───────────────────────────── */
  .steps-list {
    list-style: none;
    padding: 0;
    margin: 0;
    counter-reset: step-counter;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .step-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .step-checkbox {
    margin-top: 0.2rem;
    cursor: pointer;
    width: 17px;
    height: 17px;
    accent-color: var(--prep-primary);
    flex-shrink: 0;
  }
  
  .step-label {
    cursor: pointer;
    display: flex;
    gap: 0.75rem;
    flex: 1;
    align-items: flex-start;
  }
  
  .step-checkbox:checked + .step-label .step-text {
    opacity: 0.5;
    text-decoration: line-through;
  }
  
  .step-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--prep-primary);
    color: var(--prep-bg);
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
  }
  
  .step-text {
    flex: 1;
    line-height: 1.7;
    font-size: 0.92rem;
    color: var(--prep-text);
    padding-top: 0.2rem;
  }
  
  /* ── Tips list ────────────────────────────── */
  .tips-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .tip-item {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(0, 200, 180, 0.08);
    border-left: 4px solid var(--prep-primary);
    border-radius: 8px;
  }
  
  .tip-icon {
    font-size: 1.25rem;
    line-height: 1;
    flex-shrink: 0;
  }
  
  .tip-text {
    flex: 1;
    line-height: 1.6;
    font-size: 0.9rem;
    color: var(--prep-muted);
  }
  
  .empty-state {
    text-align: center;
    color: var(--prep-muted);
    font-style: italic;
    padding: 2rem 1rem;
  }
  
  /* ── Action buttons ───────────────────────── */
  .recipe-actions {
    display: flex;
    gap: 0.75rem;
    padding-top: 1rem;
    border-top: 2px solid var(--prep-border);
  }
  
  .action-btn {
    flex: 1;
    padding: 0.75rem 1.25rem;
    border: none;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s ease;
  }
  
  .action-btn--primary {
    background: var(--prep-primary);
    color: var(--prep-bg);
  }
  
  .action-btn--primary:hover {
    background: var(--prep-primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 200, 180, 0.3);
  }
  
  .action-btn--secondary {
    background: transparent;
    color: var(--prep-primary);
    border: 2px solid var(--prep-primary);
  }
  
  .action-btn--secondary:hover {
    background: rgba(0, 200, 180, 0.12);
  }

  .action-btn--cook {
    background: rgba(255, 180, 0, 0.15);
    color: #f5a623;
    border: 2px solid rgba(255, 180, 0, 0.4);
  }

  .action-btn--cook:hover {
    background: rgba(255, 180, 0, 0.25);
  }
  
  /* ── Transitions ──────────────────────────── */
  .tab-fade-enter-active,
  .tab-fade-leave-active {
    transition: opacity 0.2s ease;
  }
  
  .tab-fade-enter-from,
  .tab-fade-leave-to {
    opacity: 0;
  }
  
  /* ── Scrollbar styling ────────────────────── */
  .recipe-display::-webkit-scrollbar,
  .tab-content::-webkit-scrollbar {
    width: 8px;
  }
  
  .recipe-display::-webkit-scrollbar-track,
  .tab-content::-webkit-scrollbar-track {
    background: var(--prep-bg);
    border-radius: 10px;
  }
  
  .recipe-display::-webkit-scrollbar-thumb,
  .tab-content::-webkit-scrollbar-thumb {
    background: var(--prep-border);
    border-radius: 10px;
  }
  
  .recipe-display::-webkit-scrollbar-thumb:hover,
  .tab-content::-webkit-scrollbar-thumb:hover {
    background: var(--prep-primary);
  }
  </style>