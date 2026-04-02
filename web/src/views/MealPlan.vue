<template>
  <div class="meal-plan-page">
    <!-- Page header -->
    <div class="page-header">
      <h1 class="page-title">Meal Planner</h1>
      <p class="page-sub">Generate personalized multi-day meal plans powered by AI</p>
    </div>

    <!-- LIST MODE -->
    <div v-if="mode === 'list'" class="list-mode">
      <div class="list-toolbar">
        <button class="btn btn-primary" @click="mode = 'create'">+ New Meal Plan</button>
      </div>

      <div v-if="loadingPlans" class="loading-state">Loading plans…</div>

      <div v-else-if="savedPlans.length === 0" class="empty-state">
        <div class="empty-icon">📅</div>
        <h3>No meal plans yet</h3>
        <p>Create your first AI-generated meal plan to get started.</p>
        <button class="btn btn-primary" @click="mode = 'create'">+ New Meal Plan</button>
      </div>

      <div v-else class="plans-grid">
        <div
          v-for="plan in savedPlans"
          :key="plan.id"
          class="plan-card"
        >
          <div class="plan-card-header">
            <h3 class="plan-name">{{ plan.name }}</h3>
            <span class="plan-servings">{{ plan.servings }} serving{{ plan.servings !== 1 ? 's' : '' }}</span>
          </div>
          <p class="plan-dates">{{ formatDateRange(plan.start_date, plan.end_date) }}</p>
          <p v-if="plan.created_at" class="plan-created">
            Created {{ formatCreatedAt(plan.created_at) }}
          </p>
          <div class="plan-card-actions">
            <button class="btn btn-secondary btn-sm" @click="viewSavedPlan(plan)">View</button>
            <button class="btn btn-danger btn-sm" @click="onDeletePlan(plan.id)">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE MODE: Wizard -->
    <div v-else-if="mode === 'create'" class="create-mode">
      <MealPlanWizard
        :saved-recipes="savedRecipes"
        @submit="startGeneration"
        @cancel="mode = 'list'"
      />
    </div>

    <!-- VIEW MODE: Calendar + generation + grocery diff -->
    <div v-else-if="mode === 'view'" class="view-mode">
      <div class="view-toolbar">
        <button class="btn btn-ghost" @click="mode = 'list'">← Back to plans</button>
        <h2 class="view-plan-name">{{ currentWizardData?.name || activePlan?.name }}</h2>
      </div>

      <!-- Generation progress -->
      <div v-if="!generationDone" class="gen-progress-wrap">
        <div class="gen-progress-bar-track">
          <div
            class="gen-progress-bar-fill"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
        <p class="gen-progress-text">
          Planning day {{ generationProgress.current + 1 }} of {{ generationProgress.total }}…
          <span v-if="generatingDate" class="gen-date">{{ generatingDate }}</span>
        </p>
      </div>

      <!-- Generation errors -->
      <div v-if="generationErrors.length > 0" class="error-list">
        <p class="error-heading">Some days failed to generate:</p>
        <ul>
          <li v-for="(err, i) in generationErrors" :key="i" class="error-item">{{ err }}</li>
        </ul>
      </div>

      <!-- Calendar -->
      <MealCalendar
        v-if="entries.length > 0 || !generationDone"
        :entries="entries"
        :start-date="calendarStartDate"
        :end-date="calendarEndDate"
        :meal-types="calendarMealTypes"
        :generating-date="generatingDate"
        @meal-click="selectedMeal = $event"
      />

      <!-- Grocery diff panel -->
      <div v-if="generationDone && groceryDiff.length > 0" class="grocery-diff-panel">
        <div class="diff-header">
          <h3 class="diff-title">Missing from Pantry</h3>
          <span class="diff-count">{{ groceryDiff.filter(i => i.selected).length }} selected</span>
        </div>
        <p class="diff-subtitle">These ingredients are needed but not currently in your pantry:</p>

        <div class="diff-list">
          <label
            v-for="(item, i) in groceryDiff"
            :key="i"
            class="diff-item"
          >
            <input type="checkbox" v-model="item.selected" class="diff-checkbox" />
            <div class="diff-info">
              <span class="diff-name">{{ item.name }}</span>
              <span v-if="item.pantryNote" class="diff-pantry-note">{{ item.pantryNote }}</span>
            </div>
            <span class="diff-qty">
              {{ item.quantity ? item.quantity + ' ' : '' }}{{ item.unit || '' }}
              <span v-if="item.pantryNote === 'check stock'" class="diff-check-stock">check stock</span>
            </span>
            <span class="diff-cat">{{ item.category || '' }}</span>
          </label>
        </div>

        <div class="diff-actions">
          <button class="btn btn-secondary btn-sm" @click="toggleAllDiff">
            {{ allDiffSelected ? 'Deselect All' : 'Select All' }}
          </button>
          <button
            class="btn btn-primary"
            @click="onAddToGroceryList"
            :disabled="groceryDiff.filter(i => i.selected).length === 0"
          >
            Add selected to Grocery List
          </button>
        </div>

        <div v-if="groceryAddedConfirm" class="diff-confirm">
          ✓ Added to grocery list
        </div>
      </div>

      <!-- Save status banner -->
      <div v-if="generationDone" class="save-actions">
        <div v-if="savingPlan" class="saving-badge">Saving plan…</div>
        <div v-else-if="planSaved" class="saved-badge">✓ Plan saved</div>
      </div>
    </div>

    <!-- Recipe detail modal -->
    <Transition name="modal">
      <div v-if="selectedMeal" class="modal-overlay" @click.self="selectedMeal = null">
        <div class="modal-content">
          <div class="modal-toolbar">
            <button class="modal-close" @click="selectedMeal = null">✕ Close</button>
            <button
              class="btn btn-secondary btn-sm regen-btn"
              @click="regenerateMeal"
              :disabled="regeneratingMeal"
            >
              {{ regeneratingMeal ? 'Regenerating…' : '🔄 Regenerate' }}
            </button>
          </div>
          <RecipeDisplay
            :recipe="selectedMeal.recipe"
            :hide-actions="true"
            :show-add-to-grocery="true"
            :show-made-this="true"
            :show-save-to-collection="true"
            :id-prefix="`mp-${selectedMeal.date}-${selectedMeal.meal_type}`"
            @add-to-grocery="(ings) => addIngredientsToGrocery(selectedMeal.recipe, ings)"
            @made-this="() => { madeThisMeal = selectedMeal.recipe; selectedMeal = null }"
            @save-to-collection="onSaveToCollection"
          />
          <div v-if="madeThisConfirm" class="made-confirm">✓ Pantry updated</div>
          <div v-if="savedToCollectionConfirm" class="made-confirm">✓ Saved to My Recipes</div>
        </div>
      </div>
    </Transition>

    <!-- Use pantry modal — rendered last so it always sits on top -->
    <UsePantryModal
      v-if="madeThisMeal"
      :recipe="madeThisMeal"
      :pantry-items="pantryItems"
      @confirm="onPantryConfirm"
      @cancel="madeThisMeal = null"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { fuzzyMatch, toBase, fromBase, normalizeUnit, formatQty } from '@/utils/ingredientMatch.js'
import { usePrepMateStore } from '@/store/prepMateStore'
import { usePantryStore } from '@/store/pantryStore'
import {
  generateMealPlanDay,
  saveMealPlan,
  fetchMealPlans,
  fetchMealPlan,
  deleteMealPlan,
  updatePlannedMeal,
  saveRecipeToCollection,
} from '@/services/api'
import MealPlanWizard from '@/components/MealPlanWizard.vue'
import MealCalendar from '@/components/MealCalendar.vue'
import RecipeDisplay from '@/components/RecipeDisplay.vue'
import UsePantryModal from '@/components/UsePantryModal.vue'

export default {
  name: 'MealPlan',
  components: { MealPlanWizard, MealCalendar, RecipeDisplay, UsePantryModal },
  setup() {
    const store = usePrepMateStore()
    const pantryStore = usePantryStore()

    const savedRecipes = computed(() => store.savedRecipes.value)

    // Mode: 'list' | 'create' | 'view'
    const mode = ref('list')

    // List state
    const savedPlans = ref([])
    const loadingPlans = ref(false)

    // View state
    const entries = ref([])
    const generatingDate = ref(null)
    const generationProgress = reactive({ current: 0, total: 0 })
    const generationDone = ref(false)
    const generationErrors = ref([])
    const groceryDiff = ref([])
    const planSaved = ref(false)
    const savingPlan = ref(false)
    const currentWizardData = ref(null)
    const selectedMeal = ref(null)
    const activePlan = ref(null)
    const groceryAddedConfirm = ref(false)
    const regeneratingMeal = ref(false)
    const savedToCollectionConfirm = ref(false)
    const madeThisMeal = ref(null)
    const madeThisConfirm = ref(false)

    // Computed props for calendar
    const calendarStartDate = computed(() => {
      return currentWizardData.value?.startDate || activePlan.value?.start_date || ''
    })

    const calendarEndDate = computed(() => {
      if (currentWizardData.value) {
        const dates = getDateRange(currentWizardData.value.startDate, currentWizardData.value.numDays)
        return dates[dates.length - 1] || currentWizardData.value.startDate
      }
      return activePlan.value?.end_date || ''
    })

    const calendarMealTypes = computed(() => {
      if (currentWizardData.value?.mealTypes) return currentWizardData.value.mealTypes
      // Derive from entries when viewing a saved plan
      const types = [...new Set(entries.value.map(e => e.meal_type))]
      return types.length > 0 ? types : ['breakfast', 'lunch', 'dinner']
    })

    const progressPercent = computed(() => {
      if (generationProgress.total === 0) return 0
      return Math.round((generationProgress.current / generationProgress.total) * 100)
    })

    const allDiffSelected = computed(() => groceryDiff.value.every(i => i.selected))

    // ── Helpers ──────────────────────────────────────────

    function getDateRange(startDate, numDays) {
      const dates = []
      const start = new Date(startDate + 'T12:00:00')
      for (let i = 0; i < numDays; i++) {
        const d = new Date(start)
        d.setDate(d.getDate() + i)
        dates.push(d.toISOString().split('T')[0])
      }
      return dates
    }

    function getDayOfWeek(dateStr) {
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      return days[new Date(dateStr + 'T12:00:00').getDay()]
    }

    function getDayCount(start, end) {
      const s = new Date(start + 'T12:00:00')
      const e = new Date(end + 'T12:00:00')
      return Math.round((e - s) / (1000 * 60 * 60 * 24)) + 1
    }

    function formatDateRange(start, end) {
      const opts = { month: 'short', day: 'numeric', year: 'numeric' }
      const s = new Date(start + 'T12:00:00').toLocaleDateString(undefined, opts)
      const e = new Date(end + 'T12:00:00').toLocaleDateString(undefined, opts)
      return `${s} – ${e}`
    }

    function formatCreatedAt(iso) {
      return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    }

    // ── Generation ───────────────────────────────────────

    async function startGeneration(wizardData) {
      mode.value = 'view'
      entries.value = []
      generationErrors.value = []
      groceryDiff.value = []
      planSaved.value = false
      generationDone.value = false
      activePlan.value = null
      currentWizardData.value = wizardData

      const dates = getDateRange(wizardData.startDate, wizardData.numDays)
      generationProgress.total = dates.length
      generationProgress.current = 0

      const previousDays = []
      // Track remaining pinned recipes — remove each once it appears in a generated day
      let remainingPinned = [...(wizardData.pinnedRecipes || [])]

      for (const date of dates) {
        generatingDate.value = date

        const request = {
          date,
          meal_types: wizardData.mealTypes,
          servings: wizardData.servings,
          goals: wizardData.goals,
          dietary_restrictions: wizardData.dietaryRestrictions || null,
          cuisine_preferences: wizardData.cuisinePreferences,
          weekday_cooking_time: wizardData.weekdayCookingTime,
          weekend_cooking_time: wizardData.weekendCookingTime,
          pantry_items: pantryStore.items.value.map(i => ({
            name: i.name,
            quantity: i.quantity || '',
            unit: i.unit || '',
            location: i.location || '',
            category: i.category || '',
          })),
          pinned_recipes: remainingPinned,
          previous_days: previousDays,
          use_leftovers: wizardData.useLeftovers || false,
          pantry_mode: wizardData.pantryMode || 'balanced',
          cooking_skill: wizardData.cookingSkill || 'intermediate',
        }

        try {
          const result = await generateMealPlanDay(request)
          entries.value.push(...result.entries)

          // Remove any pinned recipes that were used today
          const usedTitles = new Set(result.entries.map(e => e.recipe?.title?.toLowerCase().trim()))
          remainingPinned = remainingPinned.filter(
            p => !usedTitles.has(p.name.toLowerCase().trim())
          )

          previousDays.push({
            date,
            day_of_week: getDayOfWeek(date),
            meals: result.entries.map(e => ({
              meal_type: e.meal_type,
              recipe_name: e.recipe.title,
              ingredients: (e.recipe.ingredients || [])
                .slice(0, 8)
                .map(ing => `${ing.quantity} ${ing.unit} ${ing.name}`),
            })),
          })
        } catch (err) {
          generationErrors.value.push(`${date}: ${err.message}`)
        }

        generationProgress.current++
      }

      generatingDate.value = null
      generationDone.value = true
      computeGroceryDiff()
      await onSavePlan()
    }

    // ── Grocery diff ─────────────────────────────────────

    function computeGroceryDiff() {
      const pantryItems = pantryStore.items.value

      // ── Pass 1: accumulate total needed per ingredient across all non-leftover meals ──
      // Key: lowercased ingredient name. Value: { meta, totalBase, baseType, displayUnit }
      // totalBase is null when units are incompatible across recipes or not convertible.
      const ingredientMap = new Map()

      for (const entry of entries.value) {
        const title = entry.recipe?.title || entry.recipe?.name || ''
        const isLeftover =
          title.toLowerCase().startsWith('leftover ') ||
          entry.meal_type === 'leftover'
        if (isLeftover) continue

        for (const ing of entry.recipe?.ingredients || []) {
          const key = ing.name.toLowerCase().trim()
          const ingQty = parseFloat(ing.quantity)

          if (!ingredientMap.has(key)) {
            const base = (!isNaN(ingQty) && ing.unit) ? toBase(ingQty, ing.unit) : null
            ingredientMap.set(key, {
              name: ing.name,
              category: ing.category,
              location: ing.location,
              displayUnit: ing.unit,
              totalBase: base ? base.value : (!isNaN(ingQty) ? ingQty : null),
              baseType: base ? base.type : null,
              // keep original qty/unit for fallback display when conversion isn't possible
              firstQty: ingQty,
              firstUnit: ing.unit,
              selected: true,
            })
          } else {
            // Accumulate into existing entry
            const existing = ingredientMap.get(key)
            if (existing.totalBase !== null && !isNaN(ingQty) && ing.unit) {
              const base = toBase(ingQty, ing.unit)
              if (base && base.type === existing.baseType) {
                existing.totalBase += base.value
              } else if (!base && normalizeUnit(ing.unit) === normalizeUnit(existing.displayUnit)) {
                // Same non-convertible unit — add directly
                existing.totalBase += ingQty
              } else {
                // Incompatible units — mark as unknown total
                existing.totalBase = null
              }
            }
          }
        }
      }

      // ── Pass 2: compare totals against pantry ─────────────────────────────
      const diff = []

      for (const [, ing] of ingredientMap) {
        const pantryItem = pantryItems.find(p => fuzzyMatch(p.name, ing.name))

        if (!pantryItem) {
          // Not in pantry at all — need full amount
          diff.push({
            name: ing.name,
            quantity: ing.totalBase !== null
              ? formatQty(fromBase(ing.totalBase, ing.displayUnit, ing.baseType) ?? ing.totalBase)
              : (isNaN(ing.firstQty) ? null : formatQty(ing.firstQty)),
            unit: ing.displayUnit,
            category: ing.category,
            location: ing.location,
            pantryNote: null,
            selected: true,
          })
          continue
        }

        // Pantry has this ingredient — check if quantity is enough
        const pantryQty = parseFloat(pantryItem.quantity)
        if (isNaN(pantryQty) || ing.totalBase === null) {
          // Can't compute — tell user to check stock
          diff.push({
            name: ing.name,
            quantity: null,
            unit: ing.displayUnit,
            category: ing.category,
            location: ing.location,
            pantryNote: 'check stock',
            selected: false,
          })
          continue
        }

        // Convert pantry qty to the same base
        const pantryBase = toBase(pantryQty, pantryItem.unit)
        let pantryInBase = null
        if (pantryBase && pantryBase.type === ing.baseType) {
          pantryInBase = pantryBase.value
        } else if (!pantryBase && ing.baseType === null &&
                   normalizeUnit(pantryItem.unit) === normalizeUnit(ing.displayUnit)) {
          pantryInBase = pantryQty
        }

        if (pantryInBase === null) {
          // Units in different dimensions (e.g. recipe in cups, pantry in oz) — can't compare
          diff.push({
            name: ing.name,
            quantity: null,
            unit: ing.displayUnit,
            category: ing.category,
            location: ing.location,
            pantryNote: 'check stock',
            selected: false,
          })
          continue
        }

        const shortfallBase = ing.totalBase - pantryInBase
        if (shortfallBase <= 0) continue  // pantry covers it fully

        // Need to buy the shortfall amount
        const shortfallDisplay = fromBase(shortfallBase, ing.displayUnit, ing.baseType) ?? shortfallBase
        diff.push({
          name: ing.name,
          quantity: formatQty(shortfallDisplay),
          unit: ing.displayUnit,
          category: ing.category,
          location: ing.location,
          pantryNote: `${formatQty(fromBase(pantryInBase, ing.displayUnit, ing.baseType) ?? pantryInBase)} ${pantryItem.unit} in pantry`,
          selected: true,
        })
      }

      groceryDiff.value = diff
    }

    async function regenerateMeal() {
      if (!selectedMeal.value || regeneratingMeal.value) return
      const { date, meal_type } = selectedMeal.value
      regeneratingMeal.value = true
      try {
        const request = {
          date,
          meal_types: [meal_type],
          servings: currentWizardData.value?.servings || activePlan.value?.servings || 2,
          goals: currentWizardData.value?.goals || [],
          dietary_restrictions: currentWizardData.value?.dietaryRestrictions || null,
          cuisine_preferences: currentWizardData.value?.cuisinePreferences || [],
          weekday_cooking_time: currentWizardData.value?.weekdayCookingTime || 'moderate',
          weekend_cooking_time: currentWizardData.value?.weekendCookingTime || 'moderate',
          pantry_items: pantryStore.items.value.map(i => ({
            name: i.name, quantity: i.quantity || '',
            unit: i.unit || '', location: i.location || '', category: i.category || '',
          })),
          use_leftovers: currentWizardData.value?.useLeftovers || false,
          pantry_mode: currentWizardData.value?.pantryMode || 'balanced',
          cooking_skill: currentWizardData.value?.cookingSkill || 'intermediate',
          pinned_recipes: [],
          previous_days: entries.value
            .filter(e => !(e.date === date && e.meal_type === meal_type))
            .reduce((acc, e) => {
              const day = acc.find(d => d.date === e.date)
              const mealEntry = {
                meal_type: e.meal_type,
                recipe_name: e.recipe.title,
                ingredients: (e.recipe.ingredients || []).slice(0, 8)
                  .map(ing => `${ing.quantity} ${ing.unit} ${ing.name}`),
              }
              if (day) { day.meals.push(mealEntry) }
              else { acc.push({ date: e.date, day_of_week: getDayOfWeek(e.date), meals: [mealEntry] }) }
              return acc
            }, []),
        }
        const result = await generateMealPlanDay(request)
        if (result.entries?.length) {
          const newEntry = result.entries[0]
          const idx = entries.value.findIndex(e => e.date === date && e.meal_type === meal_type)
          if (idx !== -1) entries.value.splice(idx, 1, newEntry)
          else entries.value.push(newEntry)

          // Update saved plan in DB
          const planId = activePlan.value?.id || (savedPlans.value.find(p =>
            p.start_date <= date && p.end_date >= date
          )?.id)
          if (planId && newEntry.recipe?.id) {
            await updatePlannedMeal(planId, date, meal_type, newEntry.recipe.id)
          }

          selectedMeal.value = newEntry
        }
      } catch (err) {
        console.error('Regeneration failed:', err)
      } finally {
        regeneratingMeal.value = false
      }
    }

    function toggleAllDiff() {
      const val = !allDiffSelected.value
      groceryDiff.value.forEach(i => { i.selected = val })
    }

    // ── Save plan ─────────────────────────────────────────

    async function onSavePlan() {
      if (savingPlan.value) return
      savingPlan.value = true
      try {
        const dates = getDateRange(currentWizardData.value.startDate, currentWizardData.value.numDays)
        const endDate = dates[dates.length - 1]

        const meals = entries.value
          .filter(e => e.recipe?.id)
          .map(e => ({
            date: e.date,
            meal_type: e.meal_type,
            recipe_id: e.recipe.id,
          }))

        const planData = {
          name: currentWizardData.value.name,
          start_date: currentWizardData.value.startDate,
          end_date: endDate,
          servings: currentWizardData.value.servings,
          meals,
        }

        const saved = await saveMealPlan(planData)
        planSaved.value = true
        savedPlans.value.unshift(saved)
      } catch (err) {
        console.error('Failed to save meal plan:', err)
      } finally {
        savingPlan.value = false
      }
    }

    // ── Grocery list integration ──────────────────────────

    function onAddToGroceryList() {
      const selected = groceryDiff.value.filter(i => i.selected)
      for (const item of selected) {
        store.addGroceryItem({
          name: item.name,
          amount: item.quantity ? String(item.quantity) : '',
          unit: item.unit || '',
          category: item.category || 'Other',
          suggestedLocation: item.location || '',
        })
      }
      groceryAddedConfirm.value = true
      setTimeout(() => { groceryAddedConfirm.value = false }, 3000)
    }

    function addIngredientsToGrocery(recipe, ingredients) {
      const seen = new Set(
        store.groceryItems.value.map(i => i.name.toLowerCase().trim())
      )
      for (const ing of ingredients) {
        const key = ing.name.toLowerCase().trim()
        if (!seen.has(key)) {
          seen.add(key)
          store.addGroceryItem({
            name: ing.name,
            amount: ing.quantity ? String(ing.quantity) : '',
            unit: ing.unit || '',
            category: ing.category || 'Other',
            suggestedLocation: ing?.location ?? '',
          })
        }
      }
    }

    // ── Delete plan ───────────────────────────────────────

    async function onDeletePlan(id) {
      if (!confirm('Delete this meal plan?')) return
      try {
        await deleteMealPlan(id)
        savedPlans.value = savedPlans.value.filter(p => p.id !== id)
      } catch (err) {
        console.error('Failed to delete plan:', err)
      }
    }

    // ── View saved plan ───────────────────────────────────

    async function viewSavedPlan(plan) {
      activePlan.value = plan
      entries.value = []
      generationErrors.value = []
      groceryDiff.value = []
      planSaved.value = true
      generationDone.value = true
      generatingDate.value = null
      currentWizardData.value = null
      mode.value = 'view'

      try {
        const full = await fetchMealPlan(plan.id)
        entries.value = full.meals
          .filter(m => m.recipe)
          .map(m => ({
            date: m.date,
            meal_type: m.meal_type,
            recipe: m.recipe,
          }))
        // Build wizard-like context so calendar knows date range + meal types
        currentWizardData.value = {
          name: full.name,
          startDate: full.start_date,
          numDays: getDayCount(full.start_date, full.end_date),
          mealTypes: [...new Set(entries.value.map(e => e.meal_type))],
          servings: full.servings,
        }
      } catch (err) {
        console.error('Failed to load meal plan:', err)
        generationErrors.value = [`Failed to load plan: ${err.message}`]
      }
    }

    // ── "I made this" ─────────────────────────────────────

    async function onPantryConfirm({ updates, deletes }) {
      for (const { id, newQty, newUnit } of updates) {
        await pantryStore.updateItem(id, { quantity: newQty, unit: newUnit })
      }
      for (const id of deletes) {
        await pantryStore.removeItem(id)
      }
      madeThisMeal.value = null
      madeThisConfirm.value = true
      setTimeout(() => { madeThisConfirm.value = false }, 3000)
    }

    async function onSaveToCollection() {
      const recipeId = selectedMeal.value?.recipe?.id
      if (!recipeId) return
      try {
        const saved = await saveRecipeToCollection(recipeId)
        store.addRecipeToState(saved)
        savedToCollectionConfirm.value = true
        setTimeout(() => { savedToCollectionConfirm.value = false }, 3000)
      } catch (err) {
        console.error('Failed to save recipe to collection:', err)
      }
    }

    // ── onMounted ─────────────────────────────────────────

    onMounted(async () => {
      await store.initialize()
      await pantryStore.initialize()
      loadingPlans.value = true
      try {
        savedPlans.value = await fetchMealPlans()
      } catch (err) {
        console.error('Failed to load meal plans:', err)
      } finally {
        loadingPlans.value = false
      }
    })

    return {
      mode,
      savedPlans,
      loadingPlans,
      savedRecipes,
      entries,
      generatingDate,
      generationProgress,
      generationDone,
      generationErrors,
      groceryDiff,
      planSaved,
      savingPlan,
      currentWizardData,
      selectedMeal,
      activePlan,
      groceryAddedConfirm,
      calendarStartDate,
      calendarEndDate,
      calendarMealTypes,
      progressPercent,
      allDiffSelected,
      startGeneration,
      onSavePlan,
      onAddToGroceryList,
      toggleAllDiff,
      addIngredientsToGrocery,
      onDeletePlan,
      viewSavedPlan,
      regenerateMeal,
      regeneratingMeal,
      pantryItems: computed(() => pantryStore.items.value),
      madeThisMeal,
      madeThisConfirm,
      onPantryConfirm,
      savedToCollectionConfirm,
      onSaveToCollection,
      formatDateRange,
      formatCreatedAt,
    }
  },
}
</script>

<style scoped>
.meal-plan-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 0.5rem 3rem;
}

/* Header */
.page-header {
  margin-bottom: 1.75rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--prep-text);
  margin-bottom: 0.25rem;
}

.page-sub {
  font-size: 0.88rem;
  color: var(--prep-muted);
}

/* Buttons */
.btn {
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: var(--prep-font-body);
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--prep-primary);
  color: var(--prep-bg);
}

.btn-primary:hover:not(:disabled) {
  background: var(--prep-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--prep-border);
  color: var(--prep-text);
}

.btn-secondary:hover {
  background: #3d4450;
}

.btn-danger {
  background: rgba(248, 81, 73, 0.15);
  color: var(--prep-error);
  border: 1px solid rgba(248, 81, 73, 0.3);
}

.btn-danger:hover {
  background: rgba(248, 81, 73, 0.25);
}

.btn-ghost {
  background: transparent;
  color: var(--prep-muted);
  border: 1px solid var(--prep-border);
}

.btn-ghost:hover {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

.btn-sm {
  padding: 0.35rem 0.8rem;
  font-size: 0.82rem;
}

.btn-large {
  padding: 0.7rem 2rem;
  font-size: 1rem;
}

/* List mode */
.list-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.25rem;
}

.loading-state {
  text-align: center;
  color: var(--prep-muted);
  padding: 3rem;
}

.empty-state {
  text-align: center;
  padding: 3.5rem 1rem;
  border: 1px dashed var(--prep-border);
  border-radius: 12px;
  color: var(--prep-muted);
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.empty-state h3 {
  font-size: 1.1rem;
  color: var(--prep-text);
  margin-bottom: 0.4rem;
}

.empty-state p {
  font-size: 0.88rem;
  margin-bottom: 1.25rem;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.plan-card {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  transition: border-color 0.2s;
}

.plan-card:hover {
  border-color: var(--prep-primary);
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.plan-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--prep-text);
}

.plan-servings {
  font-size: 0.75rem;
  color: var(--prep-muted);
  white-space: nowrap;
}

.plan-dates {
  font-size: 0.85rem;
  color: var(--prep-muted);
}

.plan-created {
  font-size: 0.78rem;
  color: var(--prep-muted);
  opacity: 0.7;
}

.plan-card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* View mode */
.view-mode {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.view-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-plan-name {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--prep-text);
}

/* Generation progress */
.gen-progress-wrap {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 10px;
  padding: 1rem 1.25rem;
}

.gen-progress-bar-track {
  height: 6px;
  background: var(--prep-border);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.6rem;
}

.gen-progress-bar-fill {
  height: 100%;
  background: var(--prep-primary);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.gen-progress-text {
  font-size: 0.85rem;
  color: var(--prep-muted);
}

.gen-date {
  color: var(--prep-primary);
  margin-left: 0.5rem;
  font-family: var(--prep-font-display);
  font-size: 0.8rem;
}

/* Errors */
.error-list {
  background: rgba(248, 81, 73, 0.08);
  border: 1px solid rgba(248, 81, 73, 0.3);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.error-heading {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--prep-error);
  margin-bottom: 0.4rem;
}

.error-item {
  font-size: 0.82rem;
  color: var(--prep-error);
  opacity: 0.85;
  margin-left: 1rem;
}

/* Grocery diff panel */
.grocery-diff-panel {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.diff-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.diff-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--prep-text);
}

.diff-count {
  font-size: 0.8rem;
  color: var(--prep-muted);
}

.diff-subtitle {
  font-size: 0.85rem;
  color: var(--prep-muted);
  margin-bottom: 1rem;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-height: 260px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.diff-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
}

.diff-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.diff-checkbox {
  accent-color: var(--prep-primary);
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.diff-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.diff-name {
  font-size: 0.88rem;
  color: var(--prep-text);
}

.diff-pantry-note {
  font-size: 0.7rem;
  color: var(--prep-primary);
  opacity: 0.8;
}

.diff-check-stock {
  display: inline-block;
  font-size: 0.68rem;
  color: var(--prep-warning, #e3a008);
  font-style: italic;
}

.diff-qty {
  font-size: 0.78rem;
  color: var(--prep-muted);
  min-width: 60px;
  text-align: right;
}

.diff-cat {
  font-size: 0.72rem;
  color: var(--prep-muted);
  opacity: 0.7;
  min-width: 90px;
  text-align: right;
}

.diff-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.diff-confirm {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: var(--prep-accent);
}

/* Save actions */
.save-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.saved-badge {
  font-size: 0.95rem;
  color: var(--prep-accent);
  font-weight: 600;
}

.saving-badge {
  font-size: 0.95rem;
  color: var(--prep-muted);
}

.made-confirm {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: var(--prep-accent);
  font-weight: 600;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
  z-index: 100;
  overflow-y: auto;
}

.modal-content {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 14px;
  padding: 1.5rem;
  max-width: 700px;
  width: 100%;
  position: relative;
  overflow-y: auto;
}

.modal-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.regen-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-close {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.85rem;
  border: 1px solid var(--prep-border);
  border-radius: 6px;
  background: transparent;
  color: var(--prep-muted);
  font-size: 0.82rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.2s;
}

.modal-close:hover {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
