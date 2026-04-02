<template>
  <div class="wizard">
    <!-- Step indicator -->
    <div class="step-indicator">
      <div
        v-for="(label, idx) in stepLabels"
        :key="idx"
        :class="['step-dot', { active: currentStep === idx + 1, done: currentStep > idx + 1 }]"
        @click="currentStep > idx + 1 ? (currentStep = idx + 1) : null"
      >
        <span class="step-num">{{ idx + 1 }}</span>
        <span class="step-label">{{ label }}</span>
      </div>
      <div class="step-line" :style="{ width: ((currentStep - 1) / (stepLabels.length - 1) * 100) + '%' }"></div>
    </div>

    <!-- Step 1: Basics -->
    <div v-if="currentStep === 1" class="step-content">
      <h2 class="step-title">Plan Basics</h2>

      <div class="field">
        <label class="field-label">Plan Name <span class="required">*</span></label>
        <input
          v-model="form.name"
          type="text"
          class="field-input"
          placeholder="e.g. Week of March 25"
          maxlength="80"
        />
        <p v-if="step1Errors.name" class="field-error">{{ step1Errors.name }}</p>
      </div>

      <div class="field">
        <label class="field-label">Start Date <span class="required">*</span></label>
        <input
          v-model="form.startDate"
          type="date"
          class="field-input"
        />
        <p v-if="step1Errors.startDate" class="field-error">{{ step1Errors.startDate }}</p>
      </div>

      <div class="field-row">
        <div class="field">
          <label class="field-label">Duration</label>
          <select v-model="form.numDays" class="field-input">
            <option :value="3">3 days</option>
            <option :value="5">5 days</option>
            <option :value="7">7 days</option>
            <option :value="10">10 days</option>
            <option :value="14">14 days</option>
          </select>
        </div>

        <div class="field">
          <label class="field-label">Servings</label>
          <select v-model="form.servings" class="field-input">
            <option v-for="n in 10" :key="n" :value="n">{{ n }} {{ n === 1 ? 'person' : 'people' }}</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label class="field-label">Meals to include <span class="required">*</span></label>
        <div class="checkbox-pills">
          <label
            v-for="mt in mealTypeOptions"
            :key="mt.value"
            :class="['pill', { selected: form.mealTypes.includes(mt.value) }]"
          >
            <input
              type="checkbox"
              :value="mt.value"
              v-model="form.mealTypes"
              class="pill-checkbox"
            />
            {{ mt.label }}
          </label>
        </div>
        <p v-if="step1Errors.mealTypes" class="field-error">{{ step1Errors.mealTypes }}</p>
      </div>

      <div class="field">
        <label class="toggle-row">
          <input type="checkbox" v-model="form.useLeftovers" class="toggle-checkbox" />
          <span class="toggle-label">Plan next-day leftovers from dinner</span>
        </label>
        <p class="field-hint">When enabled, the AI will repurpose big dinners as next-day lunch or snacks instead of generating a new recipe.</p>
      </div>
    </div>

    <!-- Step 2: Goals -->
    <div v-else-if="currentStep === 2" class="step-content">
      <h2 class="step-title">Nutrition Goals</h2>
      <p class="step-subtitle">Select all that apply (optional)</p>

      <div class="checkbox-pills large-pills">
        <label
          v-for="goal in goalOptions"
          :key="goal"
          :class="['pill', { selected: form.goals.includes(goal) }]"
        >
          <input
            type="checkbox"
            :value="goal"
            v-model="form.goals"
            class="pill-checkbox"
          />
          {{ goal }}
        </label>
      </div>
    </div>

    <!-- Step 3: Schedule & Preferences -->
    <div v-else-if="currentStep === 3" class="step-content">
      <h2 class="step-title">Schedule &amp; Preferences</h2>

      <div class="field">
        <label class="field-label">Dietary Restrictions</label>
        <input
          v-model="form.dietaryRestrictions"
          type="text"
          class="field-input"
          placeholder="e.g. vegetarian, no nuts, gluten-free"
        />
      </div>

      <div class="field">
        <label class="field-label">Cuisine Preferences</label>
        <div class="checkbox-pills">
          <label
            v-for="cuisine in cuisineOptions"
            :key="cuisine"
            :class="['pill', { selected: form.cuisinePreferences.includes(cuisine) }]"
          >
            <input
              type="checkbox"
              :value="cuisine"
              v-model="form.cuisinePreferences"
              class="pill-checkbox"
            />
            {{ cuisine }}
          </label>
        </div>
      </div>

      <div class="field">
        <label class="field-label">Cooking skill level</label>
        <div class="freedom-options">
          <label
            v-for="opt in skillOptions"
            :key="opt.value"
            :class="['freedom-card', { selected: form.cookingSkill === opt.value }]"
          >
            <input type="radio" :value="opt.value" v-model="form.cookingSkill" class="pill-checkbox" />
            <span class="freedom-title">{{ opt.icon }} {{ opt.label }}</span>
            <span class="freedom-desc">{{ opt.desc }}</span>
          </label>
        </div>
      </div>

      <div class="field">
        <label class="field-label">Ingredient freedom</label>
        <div class="freedom-options">
          <label
            v-for="opt in pantryModeOptions"
            :key="opt.value"
            :class="['freedom-card', { selected: form.pantryMode === opt.value }]"
          >
            <input type="radio" :value="opt.value" v-model="form.pantryMode" class="pill-checkbox" />
            <span class="freedom-title">{{ opt.label }}</span>
            <span class="freedom-desc">{{ opt.desc }}</span>
          </label>
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label class="field-label">Weekday Cooking Time</label>
          <div class="radio-group">
            <label v-for="opt in cookingTimeOptions" :key="opt.value" class="radio-label">
              <input type="radio" :value="opt.value" v-model="form.weekdayCookingTime" />
              {{ opt.label }}
            </label>
          </div>
        </div>

        <div class="field">
          <label class="field-label">Weekend Cooking Time</label>
          <div class="radio-group">
            <label v-for="opt in cookingTimeOptions" :key="opt.value" class="radio-label">
              <input type="radio" :value="opt.value" v-model="form.weekendCookingTime" />
              {{ opt.label }}
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 4: Pin Recipes -->
    <div v-else-if="currentStep === 4" class="step-content">
      <h2 class="step-title">Pin Recipes</h2>
      <p class="step-subtitle">
        Select saved recipes to include in your plan (optional). The AI will try to fit them in.
      </p>

      <div v-if="!savedRecipes || savedRecipes.length === 0" class="empty-recipes">
        <p>No saved recipes yet. Generate and save some recipes first.</p>
      </div>

      <div v-else class="recipe-chips">
        <label
          v-for="recipe in savedRecipes"
          :key="recipe.id"
          :class="['recipe-chip', { selected: isPinned(recipe) }]"
        >
          <input
            type="checkbox"
            :checked="isPinned(recipe)"
            @change="togglePin(recipe)"
            class="pill-checkbox"
          />
          <span class="chip-title">{{ recipe.title }}</span>
          <span class="chip-meta">{{ recipe.meal_type }}</span>
        </label>
      </div>

      <div v-if="form.pinnedRecipes.length > 0" class="pinned-summary">
        <p>{{ form.pinnedRecipes.length }} recipe{{ form.pinnedRecipes.length !== 1 ? 's' : '' }} pinned</p>
      </div>
    </div>

    <!-- Navigation buttons -->
    <div class="wizard-actions">
      <button v-if="currentStep > 1" class="btn btn-secondary" @click="currentStep--">
        Back
      </button>
      <button class="btn btn-ghost" @click="$emit('cancel')">
        Cancel
      </button>
      <div class="actions-right">
        <button
          v-if="currentStep < totalSteps"
          class="btn btn-primary"
          @click="nextStep"
        >
          Next
        </button>
        <button
          v-else
          class="btn btn-primary"
          @click="submit"
        >
          Generate Plan
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'

export default {
  name: 'MealPlanWizard',
  props: {
    savedRecipes: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const totalSteps = 4
    const currentStep = ref(1)
    const stepLabels = ['Basics', 'Goals', 'Schedule', 'Recipes']

    const mealTypeOptions = [
      { value: 'breakfast', label: 'Breakfast' },
      { value: 'lunch', label: 'Lunch' },
      { value: 'dinner', label: 'Dinner' },
      { value: 'snack', label: 'Snack' },
    ]

    const goalOptions = [
      'Balanced',
      'High Protein',
      'Weight Loss',
      'Low Carb',
      'Budget-Friendly',
      'Muscle Gain',
      'Quick & Easy',
      'Family-Friendly',
    ]

    const cuisineOptions = [
      'American', 'Italian', 'Mexican', 'Indian', 'Thai',
      'Japanese', 'Chinese', 'French', 'Mediterranean', 'Greek',
      'Korean', 'Spanish',
    ]

    const skillOptions = [
      { value: 'beginner',     icon: '🥄', label: 'Beginner',     desc: 'Simple steps, minimal technique' },
      { value: 'intermediate', icon: '🍳', label: 'Intermediate',  desc: 'Sauces, stir-fry, braising' },
      { value: 'advanced',     icon: '👨‍🍳', label: 'Advanced',      desc: 'Pro techniques, complex dishes' },
    ]

    const pantryModeOptions = [
      { value: 'strict',   label: 'Pantry Only',    desc: 'Only use what you already have. No extra shopping.' },
      { value: 'balanced', label: 'Balanced',        desc: 'Prefer pantry items, but a few extras are fine.' },
      { value: 'free',     label: 'Plan Freely',     desc: 'Best recipes regardless of pantry. Missing items go to your grocery list.' },
    ]

    const cookingTimeOptions = [
      { value: 'quick', label: 'Quick <30min' },
      { value: 'moderate', label: 'Moderate 30-60min' },
      { value: 'elaborate', label: 'Elaborate 60+min' },
    ]

    // Get today's date as default
    const today = new Date()
    const defaultDate = today.toISOString().split('T')[0]

    const form = reactive({
      name: '',
      startDate: defaultDate,
      numDays: 7,
      servings: 2,
      mealTypes: ['breakfast', 'lunch', 'dinner'],
      goals: [],
      dietaryRestrictions: '',
      cuisinePreferences: [],
      weekdayCookingTime: 'moderate',
      weekendCookingTime: 'moderate',
      pinnedRecipes: [],
      useLeftovers: false,
      pantryMode: 'balanced',
      cookingSkill: 'intermediate',
    })

    const step1Errors = reactive({
      name: '',
      startDate: '',
      mealTypes: '',
    })

    function validateStep1() {
      let valid = true
      step1Errors.name = ''
      step1Errors.startDate = ''
      step1Errors.mealTypes = ''

      if (!form.name.trim()) {
        step1Errors.name = 'Plan name is required'
        valid = false
      }
      if (!form.startDate) {
        step1Errors.startDate = 'Start date is required'
        valid = false
      }
      if (form.mealTypes.length === 0) {
        step1Errors.mealTypes = 'Select at least one meal type'
        valid = false
      }
      return valid
    }

    function nextStep() {
      if (currentStep.value === 1 && !validateStep1()) return
      if (currentStep.value < totalSteps) {
        currentStep.value++
      }
    }

    function isPinned(recipe) {
      return form.pinnedRecipes.some(p => p.name === recipe.title)
    }

    function togglePin(recipe) {
      const idx = form.pinnedRecipes.findIndex(p => p.name === recipe.title)
      if (idx === -1) {
        form.pinnedRecipes.push({ name: recipe.title, meal_type: recipe.meal_type })
      } else {
        form.pinnedRecipes.splice(idx, 1)
      }
    }

    function submit() {
      emit('submit', {
        name: form.name.trim(),
        startDate: form.startDate,
        numDays: form.numDays,
        servings: form.servings,
        mealTypes: [...form.mealTypes],
        goals: [...form.goals],
        dietaryRestrictions: form.dietaryRestrictions.trim(),
        cuisinePreferences: [...form.cuisinePreferences],
        weekdayCookingTime: form.weekdayCookingTime,
        weekendCookingTime: form.weekendCookingTime,
        pinnedRecipes: [...form.pinnedRecipes],
        useLeftovers: form.useLeftovers,
        pantryMode: form.pantryMode,
        cookingSkill: form.cookingSkill,
      })
    }

    return {
      currentStep,
      totalSteps,
      stepLabels,
      form,
      step1Errors,
      mealTypeOptions,
      goalOptions,
      cuisineOptions,
      cookingTimeOptions,
      skillOptions,
      pantryModeOptions,
      nextStep,
      isPinned,
      togglePin,
      submit,
    }
  },
}
</script>

<style scoped>
.wizard {
  max-width: 680px;
  margin: 0 auto;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 2rem;
}

/* Step indicator */
.step-indicator {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
  margin-bottom: 2.5rem;
  padding: 0 0.5rem;
}

.step-indicator::before {
  content: '';
  position: absolute;
  top: 16px;
  left: 10%;
  right: 10%;
  height: 2px;
  background: var(--prep-border);
  z-index: 0;
}

.step-line {
  display: none; /* using ::before for the full track */
}

.step-dot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  position: relative;
  z-index: 1;
  cursor: default;
}

.step-dot.done {
  cursor: pointer;
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
  border: 2px solid var(--prep-border);
  background: var(--prep-bg);
  color: var(--prep-muted);
  transition: all 0.2s;
}

.step-dot.active .step-num {
  border-color: var(--prep-primary);
  background: var(--prep-primary);
  color: var(--prep-bg);
}

.step-dot.done .step-num {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.15);
  color: var(--prep-primary);
}

.step-label {
  font-size: 0.72rem;
  color: var(--prep-muted);
  text-align: center;
}

.step-dot.active .step-label {
  color: var(--prep-primary);
}

/* Step content */
.step-content {
  min-height: 320px;
}

.step-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--prep-text);
}

.step-subtitle {
  font-size: 0.88rem;
  color: var(--prep-muted);
  margin-bottom: 1.5rem;
}

/* Fields */
.field {
  margin-bottom: 1.25rem;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.field-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--prep-muted);
  margin-bottom: 0.4rem;
}

.required {
  color: var(--prep-error);
}

.field-input {
  width: 100%;
  padding: 0.55rem 0.8rem;
  background: var(--prep-bg);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  color: var(--prep-text);
  font-size: 0.9rem;
  font-family: var(--prep-font-body);
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: var(--prep-primary);
}

.field-error {
  font-size: 0.78rem;
  color: var(--prep-error);
  margin-top: 0.3rem;
}

/* Pills */
.checkbox-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.large-pills {
  gap: 0.6rem;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--prep-border);
  border-radius: 20px;
  font-size: 0.82rem;
  color: var(--prep-muted);
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}

.pill:hover {
  border-color: var(--prep-primary);
  color: var(--prep-text);
}

.pill.selected {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.12);
  color: var(--prep-primary);
}

.pill-checkbox {
  display: none;
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  user-select: none;
}

.toggle-checkbox {
  accent-color: var(--prep-primary);
  width: 15px;
  height: 15px;
  cursor: pointer;
}

.toggle-label {
  font-size: 0.88rem;
  color: var(--prep-text);
  font-weight: 500;
}

.field-hint {
  font-size: 0.78rem;
  color: var(--prep-muted);
  margin-top: 0.3rem;
  line-height: 1.4;
}

.freedom-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
  margin-top: 0.25rem;
}

.freedom-card {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--prep-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}

.freedom-card:hover {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.04);
}

.freedom-card.selected {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.1);
}

.freedom-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--prep-text);
}

.freedom-card.selected .freedom-title {
  color: var(--prep-primary);
}

.freedom-desc {
  font-size: 0.75rem;
  color: var(--prep-muted);
  line-height: 1.35;
}

/* Radio group */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.4rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--prep-text);
  cursor: pointer;
}

.radio-label input[type="radio"] {
  accent-color: var(--prep-primary);
}

/* Recipe chips (step 4) */
.recipe-chips {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.recipe-chip {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.9rem;
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}

.recipe-chip:hover {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.05);
}

.recipe-chip.selected {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.1);
}

.chip-title {
  flex: 1;
  font-size: 0.88rem;
  color: var(--prep-text);
}

.chip-meta {
  font-size: 0.75rem;
  color: var(--prep-muted);
  text-transform: capitalize;
}

.pinned-summary {
  margin-top: 0.75rem;
  font-size: 0.82rem;
  color: var(--prep-primary);
}

.empty-recipes {
  padding: 2rem;
  text-align: center;
  color: var(--prep-muted);
  font-size: 0.88rem;
  border: 1px dashed var(--prep-border);
  border-radius: 8px;
}

/* Actions */
.wizard-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--prep-border);
}

.actions-right {
  margin-left: auto;
}

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

.btn-primary:hover {
  background: var(--prep-primary-hover);
}

.btn-secondary {
  background: var(--prep-border);
  color: var(--prep-text);
}

.btn-secondary:hover {
  background: #3d4450;
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
</style>
