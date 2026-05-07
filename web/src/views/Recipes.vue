<template>
  <div class="page">
    <header class="page-header">
      <h1 class="page-title">Recipes</h1>
      <div class="add-wrap" ref="addWrapRef">
        <button
          type="button"
          class="btn-add"
          aria-label="Add recipe"
          aria-haspopup="true"
          :aria-expanded="addDropdownOpen"
          @click="addDropdownOpen = !addDropdownOpen"
        >
          <span class="plus">+</span>
          <span class="btn-add-label">Add recipe</span>
        </button>
        <Transition name="dropdown">
          <div v-if="addDropdownOpen" class="add-dropdown">
            <button type="button" class="add-option" @click="onAddOption('social')">
              Save Recipe From Social Media
            </button>
            <button type="button" class="add-option" @click="onAddOption('image')">
              Save Recipe From Image
            </button>
            <button type="button" class="add-option" @click="onAddOption('text')">
              Save Recipe From Text
            </button>
            <button type="button" class="add-option" @click="onAddOption('ai')">
              Generate AI Recipe
            </button>
          </div>
        </Transition>
      </div>
    </header>

    <!-- Add-recipe panel (AI, Social, Image, or Text) -->
    <section v-if="addMode" class="add-panel">
      <div class="panel-header">
        <h2 class="panel-title">{{ panelTitle }}</h2>
        <button type="button" class="btn-close-panel" @click="closeAddPanel">Close</button>
      </div>

      <!-- Result: show RecipeDisplay when we have a generated recipe from any flow -->
      <Transition v-if="generatedRecipe" name="slide-in">
        <div class="generated-wrap">
          <RecipeDisplay
            :recipe="generatedRecipe"
            @close="onGenerateAnother"
            @save="onSaveGenerated"
          />
        </div>
      </Transition>

      <!-- Forms (when no result yet) -->
      <template v-else>
        <!-- Generate AI Recipe -->
        <div v-if="addMode === 'ai'" class="form-section">
          <!-- Mode Toggle -->
          <div class="ai-mode-toggle">
            <button
              type="button"
              class="toggle-btn"
              :class="{ active: aiMode === 'ingredients' }"
              @click="aiMode = 'ingredients'"
            >
              By Ingredients
            </button>
            <button
              type="button"
              class="toggle-btn"
              :class="{ active: aiMode === 'name' }"
              @click="aiMode = 'name'"
            >
              By Recipe Name
            </button>
          </div>

          <form @submit.prevent="onGenerateRecipe" class="recipe-form">

            <!-- By Ingredients -->
            <template v-if="aiMode === 'ingredients'">
              <!-- Pantry selector -->
              <div class="form-group pantry-group" v-if="pantryItems.length">
                <div class="pantry-header" @click="pantryExpanded = !pantryExpanded">
                  <span class="pantry-header-label">Use from Pantry <span class="pantry-count">({{ pantryItems.length }} items)</span></span>
                  <span class="pantry-chevron" :class="{ open: pantryExpanded }">&#9662;</span>
                </div>
                <Transition name="expand">
                  <div v-if="pantryExpanded" class="pantry-picker">
                    <div class="pantry-picker-controls">
                      <button type="button" class="pantry-ctrl-btn" @click="selectAllPantry">Use all</button>
                      <button type="button" class="pantry-ctrl-btn" @click="clearPantrySelection">Clear</button>
                    </div>
                    <div class="pantry-item-grid">
                      <label
                        v-for="item in pantryItems"
                        :key="item.id"
                        class="pantry-item-check"
                        :class="{ selected: selectedPantryIds.has(item.id) }"
                      >
                        <input
                          type="checkbox"
                          :checked="selectedPantryIds.has(item.id)"
                          @change="togglePantryItem(item.id)"
                        />
                        <span class="pantry-item-name">{{ item.name }}</span>
                        <span v-if="item.quantity" class="pantry-item-qty">{{ item.quantity }}{{ item.unit ? ' ' + item.unit : '' }}</span>
                        <span v-if="item.location" class="pantry-item-loc">{{ item.location }}</span>
                      </label>
                    </div>
                  </div>
                </Transition>
              </div>

              <div class="form-group ing-builder">
                <label>Ingredients</label>
                <div class="ing-add-row">
                  <input
                    v-model="ingName"
                    type="text"
                    class="ing-input ing-input--name"
                    placeholder="Ingredient name"
                    autocomplete="off"
                    @keydown.enter.prevent="onAddIngredient"
                  />
                  <input v-model="ingQty" type="number" min="0" step="any" class="ing-input ing-input--qty" placeholder="Qty" @keydown="(e) => ['e','E','+','-'].includes(e.key) && e.preventDefault()" />
                  <select v-model="ingUnit" class="ing-input ing-input--unit">
                    <option value="">Unit</option>
                    <optgroup label="Volume">
                      <option value="tsp">tsp</option>
                      <option value="tbsp">tbsp</option>
                      <option value="fl oz">fl oz</option>
                      <option value="cup">cup</option>
                      <option value="cups">cups</option>
                      <option value="pint">pint</option>
                      <option value="quart">quart</option>
                      <option value="gallon">gallon</option>
                      <option value="ml">ml</option>
                      <option value="L">L</option>
                    </optgroup>
                    <optgroup label="Weight">
                      <option value="oz">oz</option>
                      <option value="lbs">lbs</option>
                      <option value="g">g</option>
                      <option value="kg">kg</option>
                    </optgroup>
                    <optgroup label="Count">
                      <option value="count">count</option>
                      <option value="piece">piece</option>
                      <option value="pieces">pieces</option>
                      <option value="slice">slice</option>
                      <option value="slices">slices</option>
                      <option value="clove">clove</option>
                      <option value="cloves">cloves</option>
                      <option value="bunch">bunch</option>
                      <option value="head">head</option>
                      <option value="can">can</option>
                      <option value="package">package</option>
                    </optgroup>
                    <optgroup label="Other">
                      <option value="pinch">pinch</option>
                      <option value="dash">dash</option>
                      <option value="to taste">to taste</option>
                    </optgroup>
                  </select>
                  <input v-model="ingBrand" type="text" class="ing-input ing-input--brand" placeholder="Brand" />
                  <select v-model="ingLocation" class="ing-input ing-input--loc">
                    <option value="">Location</option>
                    <option value="fridge">Fridge</option>
                    <option value="freezer">Freezer</option>
                    <option value="pantry">Pantry</option>
                    <option value="spices">Spices</option>
                  </select>
                  <button type="button" class="ing-add-btn" :disabled="!ingName.trim()" @click="onAddIngredient">Add</button>
                </div>
                <TransitionGroup v-if="manualIngredients.length" name="ing-item" tag="ul" class="ing-list">
                  <li v-for="ing in manualIngredients" :key="ing._id" class="ing-chip">
                    <span class="ing-chip-text">
                      <span v-if="ing.quantity" class="ing-chip-qty">{{ ing.quantity }}{{ ing.unit ? ' ' + ing.unit : '' }}</span>
                      {{ ing.name }}
                      <span v-if="ing.brand" class="ing-chip-brand">· {{ ing.brand }}</span>
                      <span v-if="ing.location" class="ing-chip-loc">{{ ing.location }}</span>
                    </span>
                    <button type="button" class="ing-chip-remove" @click="removeIngredient(ing._id)">&times;</button>
                  </li>
                </TransitionGroup>
                <p v-if="!manualIngredients.length && !selectedPantryIds.size" class="ing-empty-hint">
                  Add ingredients above or select from your pantry.
                </p>
                <p v-else-if="selectedPantryIds.size" class="pantry-note">
                  + {{ selectedPantryIds.size }} pantry item{{ selectedPantryIds.size === 1 ? '' : 's' }} selected
                </p>
              </div>
            </template>

            <!-- By Recipe Name -->
            <template v-else>
              <div class="form-group">
                <label for="recipe-name">Recipe Name</label>
                <input
                  id="recipe-name"
                  v-model="recipeName"
                  type="text"
                  placeholder="Chicken pot pie, beef stroganoff, tiramisu ..."
                />
              </div>
            </template>

            <!-- Shared fields -->
            <div class="form-group">
              <label for="servings">Serving Size</label>
              <select id="servings" v-model="servings">
                <option v-for="n in 10" :key="n" :value="n">
                  {{ n }} {{ n === 1 ? 'Serving' : 'Servings' }}
                </option>
              </select>
            </div>
            <div v-if="aiMode === 'ingredients'" class="form-group">
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
            <div class="form-group">
              <label for="dietary">Dietary Preferences</label>
              <input
                id="dietary"
                v-model="dietary"
                type="text"
                placeholder="vegetarian, gluten-free, low-carb"
              />
            </div>

            <div class="form-group">
              <label>Cooking Skill Level</label>
              <div class="skill-options">
                <label
                  v-for="opt in skillOptions"
                  :key="opt.value"
                  :class="['skill-card', { selected: cookingSkill === opt.value }]"
                >
                  <input type="radio" :value="opt.value" v-model="cookingSkill" class="skill-radio" />
                  <span class="skill-icon">{{ opt.icon }}</span>
                  <span class="skill-title">{{ opt.label }}</span>
                  <span class="skill-desc">{{ opt.desc }}</span>
                </label>
              </div>
            </div>

            <AiLoader v-if="generating" :active="generating" type="recipe" />
            <button v-else type="submit" class="btn-generate">Generate My Recipe</button>
          </form>
        </div>

        <!-- Save Recipe From Social Media -->
        <div v-else-if="addMode === 'social'" class="form-section">
          <p class="panel-message">
            Grab a recipe from Instagram, Facebook, TikTok, or YouTube—paste the link below and we’ll turn it into clear, step-by-step instructions for you.
          </p>
          <form @submit.prevent="onSubmitSocial" class="recipe-form">
            <div class="form-group">
              <label for="social-link">Recipe link</label>
              <input
                id="social-link"
                v-model="socialLink"
                type="url"
                placeholder="https://www.instagram.com/..."
                autocomplete="off"
              />
            </div>
            <AiLoader v-if="generating" :active="generating" type="recipe" />
            <button v-else type="submit" class="btn-generate" :disabled="!socialLink.trim()">
              Save recipe from link
            </button>
          </form>
        </div>

        <!-- Save Recipe From Image -->
        <div v-else-if="addMode === 'image'" class="form-section">
          <p class="panel-message">
            Add an image of handwritten recipe cards, a cookbook page, menu items, or a dish you want to try—we’ll turn it into a clear recipe. We accept PNG, JPG, JPEG, WEBP, and other common image formats.
          </p>
          <!-- Live camera view (when Take Photo is used) -->
          <div v-if="showCameraView" class="camera-view">
            <video ref="videoRef" class="camera-video" autoplay playsinline muted />
            <p v-if="cameraError" class="camera-error">{{ cameraError }}</p>
            <div class="camera-actions">
              <button type="button" class="btn-image-action" @click="stopCamera">Cancel</button>
              <button type="button" class="btn-capture" @click="capturePhoto">Capture photo</button>
            </div>
          </div>
          <template v-else>
            <div class="image-actions">
              <input
                ref="fileInputRef"
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/webp,image/*"
                class="hidden-input"
                @change="onImageSelected"
              />
              <button type="button" class="btn-image-action" @click="startCamera">
                Take Photo
              </button>
              <button type="button" class="btn-image-action" @click="fileInputRef?.click()">
                Select Image
              </button>
            </div>
          </template>
          <div v-if="imageFile" class="image-preview-wrap">
            <img :src="imagePreviewUrl" alt="Selected recipe" class="image-preview" />
            <p class="image-name">{{ imageFile.name }}</p>
            <button type="button" class="btn-clear-image" @click="clearImage">Remove image</button>
          </div>
          <AiLoader v-if="generating" :active="generating" type="recipe" />
          <button
            v-else
            type="button"
            class="btn-generate"
            :disabled="!imageFile"
            @click="onSubmitImage"
          >
            Save recipe from image
          </button>
        </div>

        <!-- Save Recipe From Text -->
        <div v-else-if="addMode === 'text'" class="form-section">
          <p class="panel-message">
            Paste your recipe in any format—messy notes, a blog post, or a list of steps—and we’ll turn it into clear, easy-to-follow instructions.
          </p>
          <form @submit.prevent="onSubmitText" class="recipe-form">
            <div class="form-group">
              <label for="pasted-text">Recipe text</label>
              <textarea
                id="pasted-text"
                v-model="pastedText"
                placeholder="Paste or type your recipe here..."
                rows="6"
              />
            </div>
            <AiLoader v-if="generating" :active="generating" type="recipe" />
            <button v-else type="submit" class="btn-generate" >
              Save recipe from text
            </button>
          </form>
        </div>
      </template>

      <div v-if="recipeMessage && !generatedRecipe" class="recipe-message" :class="recipeMessage.error ? 'error' : 'success'">
        {{ recipeMessage.text }}
      </div>
    </section>

    <!-- Saved recipes list (on the same page) -->
    <section class="saved-section">
    <h2 class="section-title">Saved Recipes</h2>
    <div v-if="!savedRecipes.length" class="placeholder">
      <p class="empty-state">No saved recipes yet.</p>
      <p class="hint">Use the Add recipe menu to generate an AI recipe, save from a link (Instagram, TikTok, YouTube, etc.), save from an image, or paste text—then save to add it here.</p>
    </div>
      <div v-else class="recipes-list">
        <article
          v-for="recipe in savedRecipes"
          :key="recipe.id"
          class="recipe-card"
        >
        <header 
          class="recipe-card-header" 
          :class="{ 'is-expanded': expandedRecipes.has(recipe.id) }"
          @click="toggleRecipe(recipe.id)"
        >
            <h3 class="recipe-card-title">
              {{ recipe.title || `Recipe #${recipe.id}` }}
            </h3>
            <div class="recipe-card-header-actions">
              <span class="collapse-icon">{{ expandedRecipes.has(recipe.id) ? '▲' : '▼' }}</span>
              <button type="button" class="btn-remove" @click.stop="remove(recipe.id)">Remove</button>
            </div>
          </header>

          <template v-if="expandedRecipes.has(recipe.id)">
            <div class="recipe-display-wrap">
              <RecipeDisplay
                :recipe="recipe"
                :hide-actions="true"
                :show-add-checked-to-pantry="true"
                :show-add-to-grocery="true"
                :show-made-this="true"
                :id-prefix="`saved-${recipe.id}`"
                @add-to-pantry="addCheckedIngredientsToPantry"
                @add-to-grocery="(ings) => addUncheckedIngredientsToGrocery(recipe, ings)"
                @made-this="onMadeThis(recipe)"
              />
            </div>
        </template>
      </article>
    </div>
  </section>

  <UsePantryModal
    v-if="madeThisRecipe"
    :recipe="madeThisRecipe"
    :pantry-items="pantryItems"
    @confirm="onPantryConfirm"
    @cancel="madeThisRecipe = null"
  />

  <Transition name="toast">
    <div v-if="toastMessage" class="toast" role="status" aria-live="polite">
      {{ toastMessage }}
    </div>
  </Transition>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import {
  generateRecipeFromIngredients,
  extractRecipeFromSocialLink,
  extractRecipeFromImage,
  extractRecipeFromText,
  generateRecipeFromName,
  saveRecipe,  
} from '@/services/api'
import { usePrepMateStore } from '@/store/prepMateStore'
import { usePantryStore, PANTRY_CATEGORIES } from '@/store/pantryStore'
import AiLoader from '@/components/AiLoader.vue'
import RecipeDisplay from '@/components/RecipeDisplay.vue'
import UsePantryModal from '@/components/UsePantryModal.vue'

const ADD_MODE_TITLES = {
  ai: 'Generate AI Recipe',
  social: 'Save Recipe From Social Media',
  image: 'Save Recipe From Image',
  text: 'Save Recipe From Text'
}

export default {
  name: 'Recipes',
  components: { AiLoader, RecipeDisplay, UsePantryModal },
  setup() {
    const store = usePrepMateStore()
    const pantryStore = usePantryStore()
    const addDropdownOpen = ref(false)
    const addWrapRef = ref(null)
    const addMode = ref(null)

    const servings = ref(2)
    const cuisine = ref('')
    const dietary = ref('')
    const cookingSkill = ref('intermediate')
    const skillOptions = [
      { value: 'beginner',     icon: '🥄', label: 'Beginner',     desc: 'Simple steps, minimal technique' },
      { value: 'intermediate', icon: '🍳', label: 'Intermediate',  desc: 'Sauces, stir-fry, braising' },
      { value: 'advanced',     icon: '👨‍🍳', label: 'Advanced',      desc: 'Pro techniques, complex dishes' },
    ]
    const generating = ref(false)
    const recipeMessage = ref(null)
    const generatedRecipe = ref(null)
    const aiMode = ref('ingredients')

    // Pantry ingredient selection
    const pantryItems = computed(() => pantryStore.items.value)
    const pantryExpanded = ref(false)
    const selectedPantryIds = ref(new Set())

    function togglePantryItem(id) {
      const next = new Set(selectedPantryIds.value)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      selectedPantryIds.value = next
    }

    function selectAllPantry() {
      selectedPantryIds.value = new Set(pantryItems.value.map((i) => i.id))
    }

    function clearPantrySelection() {
      selectedPantryIds.value = new Set()
    }

    // ── Manual ingredient builder ──────────────────
    const manualIngredients = ref([])
    const ingName = ref('')
    const ingQty = ref('')
    const ingUnit = ref('')
    const ingBrand = ref('')
    const ingLocation = ref('')
    let _ingId = 0

    function onAddIngredient() {
      const name = ingName.value.trim()
      if (!name) return
      manualIngredients.value.push({
        _id: ++_ingId,
        name,
        quantity: ingQty.value !== '' && ingQty.value !== null ? String(ingQty.value) : '',
        unit: ingUnit.value,
        brand: ingBrand.value.trim(),
        location: ingLocation.value,
      })
      ingName.value = ''
      ingQty.value = ''
      ingUnit.value = ''
      ingBrand.value = ''
      ingLocation.value = ''
    }

    function removeIngredient(id) {
      manualIngredients.value = manualIngredients.value.filter((i) => i._id !== id)
    }

    function buildIngredientsString() {
      const lines = []

      for (const i of pantryItems.value.filter((i) => selectedPantryIds.value.has(i.id))) {
        const parts = []
        if (i.quantity) parts.push(`qty: ${i.quantity}${i.unit ? ' ' + i.unit : ''}`)
        if (i.location) parts.push(`stored in: ${i.location}`)
        const detail = parts.length ? ` (${parts.join(', ')})` : ''
        lines.push(`- ${i.name}${detail}`)
      }

      for (const i of manualIngredients.value) {
        const parts = []
        if (i.quantity) parts.push(`qty: ${i.quantity}${i.unit ? ' ' + i.unit : ''}`)
        if (i.brand) parts.push(`brand: ${i.brand}`)
        if (i.location) parts.push(`stored in: ${i.location}`)
        const detail = parts.length ? ` (${parts.join(', ')})` : ''
        lines.push(`- ${i.name}${detail}`)
      }

      return lines.join('\n')
    }

    const recipeName = ref('')

    const socialLink = ref('')
    const imageFile = ref(null)
    const imagePreviewUrl = ref(null)
    const pastedText = ref('')
    const fileInputRef = ref(null)
    const showCameraView = ref(false)
    const cameraError = ref(null)
    const videoRef = ref(null)
    const mediaStreamRef = ref(null)

    const panelTitle = computed(() => (addMode.value ? ADD_MODE_TITLES[addMode.value] || 'Add recipe' : ''))
    const expandedRecipes = ref(new Set())

    const toastMessage = ref('')
    let toastTimer = null
    // ──────────────────────────────────────────────────────
    // LOAD SAVED RECIPES ON MOUNT
    // ──────────────────────────────────────────────────────
    onMounted(async () => {
      document.addEventListener('click', onDocClick)
      await store.initialize()
      await pantryStore.initialize()
    })

    onUnmounted(() => {
      document.removeEventListener('click', onDocClick)
      stopCamera()
      if (imagePreviewUrl.value) URL.revokeObjectURL(imagePreviewUrl.value)
    })

    function onAddOption(option) {
      addDropdownOpen.value = false
      addMode.value = option
      generatedRecipe.value = null
      recipeMessage.value = null
      socialLink.value = ''
      clearImage()
      pastedText.value = ''
      aiMode.value = 'ingredients' 
      recipeName.value = ''           
    }

    function toggleRecipe(id) {
      const next = new Set(expandedRecipes.value)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      expandedRecipes.value = next
    }

    function closeAddPanel() {
      stopCamera()
      addMode.value = null
      generatedRecipe.value = null
      recipeMessage.value = null
      clearImage()
    }

    function onDocClick(e) {
      if (addWrapRef.value && !addWrapRef.value.contains(e.target)) {
        addDropdownOpen.value = false
      }
    }

    // ──────────────────────────────────────────────────────
    // GENERATE RECIPE 
    // ──────────────────────────────────────────────────────
    async function onGenerateRecipe() {
      recipeMessage.value = null

      if (aiMode.value === "ingredients") {
        if (!manualIngredients.value.length && selectedPantryIds.value.size === 0) {
          recipeMessage.value = { text: 'Please enter at least one ingredient or select items from your pantry.', error: true }
          return
        }
      } else {
        if (!recipeName.value.trim()) {
          recipeMessage.value = { text: 'Please enter the name of the recipe you would like to create', error: true }
          return
        }
      }

      generating.value = true

      try {
        let recipe
        
        if (aiMode.value === "ingredients") {
          recipe = await generateRecipeFromIngredients(
            buildIngredientsString(),
            servings.value,
            cuisine.value,
            dietary.value,
            cookingSkill.value
          )
        } else {
          recipe = await generateRecipeFromName(
            recipeName.value,
            servings.value,
            dietary.value,
            cookingSkill.value
          )
        }
        
        // Show the recipe
        generatedRecipe.value = recipe
        recipeMessage.value = { text: `Generated: ${recipe.title}`, error: false }
        
      } catch (err) {
        recipeMessage.value = { text: `Error: ${err.message}`, error: true }
      } finally {
        generating.value = false
      }
    }

    function onGenerateAnother() {
      // Close the recipe display, show form again
      generatedRecipe.value = null
      recipeMessage.value = null
    }

    // ──────────────────────────────────────────────────────
    // Save RECIPE
    // ──────────────────────────────────────────────────────
    async function onSaveGenerated() {
      if (!generatedRecipe.value) return
      try {
        const saved = await saveRecipe(generatedRecipe.value)
        store.addRecipeToState(saved)
        recipeMessage.value = { text: `"${saved.data?.title || saved.title}" saved!`, error: false }
        closeAddPanel()
      } catch (err) {
        recipeMessage.value = { text: `Failed to save: ${err.message}`, error: true }
      }
    }

    // ──────────────────────────────────────────────────────
    // IMAGE HANDLING
    // ──────────────────────────────────────────────────────
    function onImageSelected(e) {
      const file = e.target?.files?.[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        recipeMessage.value = { text: 'Please choose an image file (PNG, JPG, JPEG, WEBP).', error: true }
        return
      }
      if (imagePreviewUrl.value) URL.revokeObjectURL(imagePreviewUrl.value)
      imageFile.value = file
      imagePreviewUrl.value = URL.createObjectURL(file)
      recipeMessage.value = null
      e.target.value = ''
    }

    function clearImage() {
      stopCamera()
      if (imagePreviewUrl.value) {
        URL.revokeObjectURL(imagePreviewUrl.value)
      }
      imageFile.value = null
      imagePreviewUrl.value = null
      if (fileInputRef.value) fileInputRef.value.value = ''
    }

    async function startCamera() {
      cameraError.value = null
      showCameraView.value = true
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false
        })
        mediaStreamRef.value = stream
        await nextTick()
        if (videoRef.value) {
          videoRef.value.srcObject = stream
        }
      } catch (err) {
        cameraError.value = err.name === 'NotAllowedError'
          ? 'Camera access was denied. Please allow camera access to take a photo.'
          : err.message || 'Could not access camera.'
        showCameraView.value = false
      }
    }

    function stopCamera() {
      if (mediaStreamRef.value) {
        mediaStreamRef.value.getTracks().forEach((track) => track.stop())
        mediaStreamRef.value = null
      }
      if (videoRef.value && videoRef.value.srcObject) {
        videoRef.value.srcObject = null
      }
      showCameraView.value = false
      cameraError.value = null
    }

    function capturePhoto() {
      const video = videoRef.value
      if (!video || !video.videoWidth || !mediaStreamRef.value) return
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0)
      canvas.toBlob(
        (blob) => {
          if (!blob) return
          const file = new File([blob], `recipe-photo-${Date.now()}.jpg`, { type: 'image/jpeg' })
          if (imagePreviewUrl.value) URL.revokeObjectURL(imagePreviewUrl.value)
          imageFile.value = file
          imagePreviewUrl.value = URL.createObjectURL(blob)
          recipeMessage.value = null
          stopCamera()
        },
        'image/jpeg',
        0.92
      )
    }

    async function onSubmitImage() {
      if (!imageFile.value) return
      recipeMessage.value = null
      generating.value = true
      try {
        const recipe = await extractRecipeFromImage(imageFile.value)
        
        generatedRecipe.value = recipe
        recipeMessage.value = { text: `Extracted: ${recipe.title || 'Recipe'}`, error: false }
      } catch (err) {
        recipeMessage.value = { text: err.message || 'Could not get recipe from image.', error: true }
      } finally {
        generating.value = false
      }
    }

    // ──────────────────────────────────────────────────────
    // Social media recipe extract
    // ──────────────────────────────────────────────────────
    async function onSubmitSocial() {
      const url = socialLink.value.trim()
      if (!url) {
        recipeMessage.value = { text: 'Please paste a link.', error: true }
        return
      }
      recipeMessage.value = null
      generating.value = true
      try {
        const recipe = await extractRecipeFromSocialLink(url)
        
        generatedRecipe.value = recipe
        recipeMessage.value = { text: `Extracted: ${recipe.title || 'Recipe'}`, error: false }
      } catch (err) {
        recipeMessage.value = { text: err.message || 'Could not get recipe from link.', error: true }
      } finally {
        generating.value = false
      }
    }

    // ──────────────────────────────────────────────────────
    // extract recipe from text
    // ──────────────────────────────────────────────────────
    async function onSubmitText() {
      const text = pastedText.value.trim()
      if (!text) {
        recipeMessage.value = { text: 'Please paste or type your recipe.', error: true }
        return
      }
      recipeMessage.value = null
      generating.value = true
      try {
        const recipe = await extractRecipeFromText(text)
        
        generatedRecipe.value = recipe
        recipeMessage.value = { text: `Converted: ${recipe.title || 'Recipe'}`, error: false }
      } catch (err) {
        recipeMessage.value = { text: err.message || 'Could not convert recipe from text.', error: true }
      } finally {
        generating.value = false
      }
    }

    // ──────────────────────────────────────────────────────
    // DELETE RECIPE
    // ──────────────────────────────────────────────────────
    async function remove(id) {
      if (confirm('Delete this recipe?')) {
        await store.removeSavedRecipe(id)
      }
    }

    function addUncheckedIngredientsToGrocery(recipe, ingredients) {
      const existing = new Set(
        (store.groceryItems.value || []).map((i) => (i.name || '').trim().toLowerCase())
      )

      const category = (recipe?.title || recipe?.name || 'Recipe').trim()
      let addedCount = 0

      for (const ing of ingredients || []) {
        const name = (typeof ing === 'string' ? ing : ing?.name) || ''
        const trimmed = name.trim()
        if (!trimmed) continue
        const key = trimmed.toLowerCase()
        if (existing.has(key)) continue
        store.addGroceryItem({
          name: trimmed,
          amount: ing?.quantity ?? '',
          unit: ing?.unit ?? '',
          category: ing?.category || category,
          suggestedLocation: ing?.location ?? '',
        })
        existing.add(key)
        addedCount++
      }

      if (toastTimer) clearTimeout(toastTimer)
      toastMessage.value =
        addedCount > 0
          ? `Added ${addedCount} item${addedCount === 1 ? '' : 's'} to your grocery list.`
          : 'Nothing new to add — everything was already on your grocery list.'
      toastTimer = setTimeout(() => {
        toastMessage.value = ''
      }, 3000)
    }

    const PANTRY_LOCATIONS = new Set(['fridge', 'freezer', 'pantry', 'spices'])

    async function addCheckedIngredientsToPantry(ingredients) {
      const selectedCount = (ingredients || []).reduce((count, i) => {
        const n = (typeof i === 'string' ? i : i?.name) || ''
        return count + (n.trim().length > 0 ? 1 : 0)
      }, 0)
      const existing = new Set(
        (pantryStore.items.value || []).map((i) => (i.name || '').trim().toLowerCase())
      )

      let addedCount = 0
      const failed = []

      for (const ing of ingredients || []) {
        const name = (typeof ing === 'string' ? ing : ing?.name) || ''
        const trimmed = name.trim()
        if (!trimmed) continue
        const key = trimmed.toLowerCase()
        if (existing.has(key)) continue

        const rawLoc = (ing?.location || '').toString().toLowerCase()
        const location = PANTRY_LOCATIONS.has(rawLoc) ? rawLoc : 'pantry'
        const qty = ing?.quantity
        const quantityStr = qty != null && qty !== '' ? String(qty) : ''
        const cat = ing?.category && PANTRY_CATEGORIES.includes(ing.category) ? ing.category : 'Other'

        try {
          await pantryStore.addItem({
            name: trimmed,
            quantity: quantityStr,
            unit: (ing?.unit ?? '').toString(),
            location,
            category: cat,
          })
          existing.add(key)
          addedCount++
        } catch {
          failed.push(trimmed)
        }
      }

      if (toastTimer) clearTimeout(toastTimer)
      if (failed.length) {
        toastMessage.value = `Could not add: ${failed.join(', ')}. Try again.`
      } else if (addedCount > 0) {
        toastMessage.value =
          selectedCount === addedCount
            ? `Added ${addedCount} item${addedCount === 1 ? '' : 's'} to your pantry.`
            : `Added ${addedCount} of ${selectedCount} selected items to your pantry.`
      } else {
        const hadSelection = selectedCount > 0
        toastMessage.value = hadSelection
          ? 'Nothing new to add — selected items are already in your pantry.'
          : 'Check the ingredients you have, then tap Add selected to Pantry.'
      }
      toastTimer = setTimeout(() => {
        toastMessage.value = ''
      }, 3000)
    }


    // ── "I made this" pantry deduction ──────────────────
    const madeThisRecipe = ref(null)

    function onMadeThis(recipe) {
      madeThisRecipe.value = recipe
    }

    async function onPantryConfirm({ updates, deletes }) {
      for (const { id, newQty, newUnit } of updates) {
        await pantryStore.updateItem(id, { quantity: newQty, unit: newUnit })
      }
      for (const id of deletes) {
        await pantryStore.removeItem(id)
      }
      madeThisRecipe.value = null
      toastMessage.value = 'Pantry updated!'
      toastTimer = setTimeout(() => { toastMessage.value = '' }, 3000)
    }

    return {
      addDropdownOpen,
      addWrapRef,
      addMode,
      panelTitle,
      manualIngredients,
      ingName,
      ingQty,
      ingUnit,
      ingBrand,
      ingLocation,
      onAddIngredient,
      removeIngredient,
      servings,
      cuisine,
      dietary,
      cookingSkill,
      skillOptions,
      generating,
      recipeMessage,
      generatedRecipe,
      socialLink,
      imageFile,
      imagePreviewUrl,
      pastedText,
      fileInputRef,
      showCameraView,
      cameraError,
      videoRef,
      savedRecipes: store.savedRecipes,
      onAddOption,
      closeAddPanel,
      onGenerateRecipe,
      onGenerateAnother,
      startCamera,
      stopCamera,
      capturePhoto,
      onImageSelected,
      clearImage,
      onSubmitSocial,
      onSubmitImage,
      onSubmitText,
      remove,
      addUncheckedIngredientsToGrocery,
      addCheckedIngredientsToPantry,
      toastMessage,
      aiMode,
      recipeName,
      onSaveGenerated,
      expandedRecipes,
      toggleRecipe,
      pantryItems,
      pantryExpanded,
      selectedPantryIds,
      togglePantryItem,
      selectAllPantry,
      clearPantrySelection,
      madeThisRecipe,
      onMadeThis,
      onPantryConfirm,
    }
  }
}
</script>

<style scoped>
/* ─────────────────────────────────────────────
   PAGE LAYOUT
───────────────────────────────────────────── */
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
  background: var(--prep-card);
  border: 1px solid var(--prep-primary);
  color: var(--prep-text);
  padding: 0.75rem 1rem;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  z-index: 100;
  max-width: min(560px, calc(100vw - 32px));
}

/* ── Pantry picker ───────────────────────────── */
.pantry-group {
  border: 1px solid rgba(0, 200, 180, 0.3);
  border-radius: 10px;
  overflow: hidden;
}

.pantry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  cursor: pointer;
  background: rgba(0, 200, 180, 0.07);
  user-select: none;
}

.pantry-header:hover {
  background: rgba(0, 200, 180, 0.12);
}

.pantry-header-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--prep-primary);
}

.pantry-count {
  font-weight: 400;
  color: var(--prep-muted);
}

.pantry-chevron {
  font-size: 0.7rem;
  color: var(--prep-muted);
  transition: transform 0.2s;
}

.pantry-chevron.open {
  transform: rotate(180deg);
}

.pantry-picker {
  padding: 0.75rem 0.85rem;
  border-top: 1px solid rgba(0, 200, 180, 0.2);
}

.pantry-picker-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.pantry-ctrl-btn {
  padding: 0.25rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
  border-radius: 5px;
  border: 1px solid var(--prep-border);
  background: transparent;
  color: var(--prep-muted);
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.12s;
}

.pantry-ctrl-btn:hover {
  color: var(--prep-primary);
  border-color: var(--prep-primary);
}

.pantry-item-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.pantry-item-check {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.65rem;
  border-radius: 20px;
  border: 1px solid var(--prep-border);
  background: var(--prep-card);
  cursor: pointer;
  font-size: 0.82rem;
  color: var(--prep-muted);
  transition: all 0.12s;
  user-select: none;
}

.pantry-item-check:hover {
  border-color: var(--prep-primary);
  color: var(--prep-text);
}

.pantry-item-check.selected {
  background: rgba(0, 200, 180, 0.15);
  border-color: var(--prep-primary);
  color: var(--prep-primary);
}

.pantry-item-check input[type='checkbox'] {
  display: none;
}

.pantry-item-name {
  font-weight: 600;
}

.pantry-item-qty {
  font-weight: 400;
  opacity: 0.75;
}

.pantry-item-loc {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.1);
  border-radius: 4px;
  padding: 0.05rem 0.35rem;
  margin-left: 0.2rem;
  text-transform: capitalize;
}

/* ── Ingredient builder ──────────────────────── */
.ing-builder {
  margin-bottom: 0;
}

.ing-add-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.ing-input {
  padding: 0.45rem 0.6rem;
  border-radius: 7px;
  border: 1px solid var(--prep-border);
  font-size: 0.875rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.ing-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.15);
}

.ing-input--qty::-webkit-inner-spin-button,
.ing-input--qty::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.ing-input--qty { -moz-appearance: textfield; appearance: textfield; }

.ing-input--name  { flex: 1; min-width: 140px; }
.ing-input--qty   { width: 70px; }
.ing-input--unit  { width: 120px; }
.ing-input--brand { width: 110px; }
.ing-input--loc   { width: 110px; }

.ing-add-btn {
  padding: 0.45rem 0.9rem;
  border-radius: 7px;
  border: 1px solid var(--prep-primary);
  background: transparent;
  color: var(--prep-primary);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}

.ing-add-btn:hover:not(:disabled) {
  background: rgba(0, 200, 180, 0.1);
}

.ing-add-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ing-list {
  list-style: none;
  padding: 0;
  margin: 0.6rem 0 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.ing-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 999px;
  padding: 0.25rem 0.3rem 0.25rem 0.7rem;
  font-size: 0.82rem;
}

.ing-chip-text {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--prep-text);
}

.ing-chip-qty {
  color: var(--prep-primary);
  font-weight: 600;
}

.ing-chip-brand {
  color: var(--prep-muted);
}

.ing-chip-loc {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.12);
  border-radius: 4px;
  padding: 0.05rem 0.35rem;
  text-transform: capitalize;
}

.ing-chip-remove {
  background: transparent;
  border: none;
  color: var(--prep-muted);
  font-size: 0.95rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 0.2rem;
  border-radius: 50%;
  transition: color 0.12s, background 0.12s;
}

.ing-chip-remove:hover {
  color: var(--prep-error);
  background: rgba(248, 81, 73, 0.1);
}

.ing-empty-hint {
  font-size: 0.8rem;
  color: var(--prep-muted);
  margin-top: 0.5rem;
}

.ing-item-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.ing-item-leave-active { transition: opacity 0.1s ease; }
.ing-item-enter-from { opacity: 0; transform: scale(0.9); }
.ing-item-leave-to   { opacity: 0; }

.pantry-note {
  margin-top: 0.4rem;
  font-size: 0.78rem;
  color: var(--prep-primary);
  font-weight: 500;
}

.expand-enter-active, .expand-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px);
}

/* ─────────────────────────────────────────────
   PAGE HEADER (title + add button row)
───────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--prep-text);
  font-family: var(--prep-font-display);
  margin: 0;
}

/* ─────────────────────────────────────────────
   ADD RECIPE BUTTON + DROPDOWN
───────────────────────────────────────────── */
.add-wrap {
  position: relative;
}

.btn-add {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: background 0.2s, transform 0.15s;
}

.btn-add:hover {
  background: var(--prep-primary-hover);
  transform: translateY(-1px);
}

.plus {
  font-size: 1.25rem;
  line-height: 1;
  font-weight: 400;
}

.add-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  min-width: 240px;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  padding: 0.35rem 0;
  z-index: 20;
}

.add-option {
  display: block;
  width: 100%;
  padding: 0.6rem 1rem;
  background: transparent;
  border: none;
  text-align: left;
  font-size: 0.9rem;
  color: var(--prep-text);
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: background 0.15s;
}

.add-option:hover {
  background: rgba(0, 200, 180, 0.12);
}

/* Dropdown open/close animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ─────────────────────────────────────────────
   ADD RECIPE PANEL (slide-in form container)
───────────────────────────────────────────── */
.add-panel {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.panel-message {
  color: var(--prep-muted);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 1rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--prep-text);
  margin: 0;
  font-family: var(--prep-font-body);
}

.btn-close-panel {
  padding: 0.35rem 0.75rem;
  background: transparent;
  color: var(--prep-muted);
  border: 1px solid var(--prep-border);
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-close-panel:hover {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

/* ─────────────────────────────────────────────
   CAMERA / IMAGE UPLOAD (image flow)
───────────────────────────────────────────── */
.hidden-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.camera-view {
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--prep-bg);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
}

.camera-video {
  display: block;
  width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 6px;
  background: #000;
}

.camera-error {
  margin: 0.75rem 0 0;
  font-size: 0.9rem;
  color: var(--prep-error);
}

.camera-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
  justify-content: center;
}

.btn-capture {
  padding: 0.6rem 1.25rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-capture:hover {
  background: var(--prep-primary-hover);
}

.image-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.btn-image-action {
  padding: 0.6rem 1rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: background 0.2s, border-color 0.2s;
}

.btn-image-action:hover {
  background: rgba(0, 200, 180, 0.08);
  border-color: var(--prep-primary);
}

.image-preview-wrap {
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--prep-bg);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
}

.image-preview {
  display: block;
  max-width: 100%;
  max-height: 240px;
  width: auto;
  height: auto;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.image-name {
  font-size: 0.85rem;
  color: var(--prep-muted);
  margin: 0 0 0.5rem;
}

.btn-clear-image {
  padding: 0.35rem 0.75rem;
  background: transparent;
  color: var(--prep-error);
  border: 1px solid var(--prep-error);
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-clear-image:hover {
  background: rgba(248, 81, 73, 0.12);
}

/* ─────────────────────────────────────────────
   RECIPE FORM (shared across all add modes)
───────────────────────────────────────────── */
.form-section .recipe-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-weight: 600;
  color: var(--prep-text);
  font-size: 0.9rem;
}

.skill-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-top: 0.15rem;
}

.skill-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.65rem 0.5rem;
  border: 1px solid var(--prep-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
  text-align: center;
}

.skill-card:hover {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.04);
}

.skill-card.selected {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.1);
}

.skill-radio { display: none; }

.skill-icon { font-size: 1.3rem; }

.skill-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--prep-text);
}

.skill-card.selected .skill-title { color: var(--prep-primary); }

.skill-desc {
  font-size: 0.7rem;
  color: var(--prep-muted);
  line-height: 1.3;
}

.form-group textarea,
.form-group select,
.form-group input {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  font-size: 1rem;
  font-family: var(--prep-font-body);
  background: var(--prep-bg);
  color: var(--prep-text);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.btn-generate {
  margin-top: 0.25rem;
  padding: 0.85rem 1.5rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-generate:hover:not(:disabled) {
  background: var(--prep-primary-hover);
}

/* ─────────────────────────────────────────────
   AI MODE TOGGLE (By Ingredients / By Name)
───────────────────────────────────────────── */
.ai-mode-toggle {
  display: flex;
  background: var(--prep-bg);
  border: 1px solid var(--prep-border);
  border-radius: 10px;
  padding: 4px;
  gap: 4px;
  margin-bottom: 1.25rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.55rem 1rem;
  background: transparent;
  color: var(--prep-muted);
  border: none;
  border-radius: 7px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: background 0.2s, color 0.2s;
}

.toggle-btn:hover:not(.active) {
  background: rgba(0, 200, 180, 0.08);
  color: var(--prep-text);
}

.toggle-btn.active {
  background: var(--prep-primary);
  color: var(--prep-bg);
  font-weight: 600;
}

/* ─────────────────────────────────────────────
   SUCCESS / ERROR MESSAGE BANNER
───────────────────────────────────────────── */
.recipe-message {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.recipe-message.success {
  background: rgba(0, 200, 180, 0.15);
  border: 1px solid var(--prep-primary);
  color: var(--prep-primary);
}

.recipe-message.error {
  background: rgba(248, 81, 73, 0.15);
  border: 1px solid var(--prep-error);
  color: var(--prep-error);
}

/* ─────────────────────────────────────────────
   GENERATED RECIPE PREVIEW (before saving)
───────────────────────────────────────────── */
.generated-wrap {
  margin-top: 0.5rem;
}

/* Slide-in animation for generated recipe */
.slide-in-enter-active,
.slide-in-leave-active {
  transition: all 0.3s ease;
}
.slide-in-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.slide-in-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ─────────────────────────────────────────────
   SAVED RECIPES SECTION
───────────────────────────────────────────── */
.saved-section {
  margin-top: 0.5rem;
}

.section-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--prep-text);
  margin: 0 0 1rem;
  font-family: var(--prep-font-body);
}

/* Empty state shown when no recipes are saved */
.placeholder {
  padding: 1.5rem;
  border-radius: 12px;
  background: var(--prep-card);
  border: 1px dashed var(--prep-border);
}

.empty-state {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--prep-text);
}

.hint {
  color: var(--prep-muted);
  font-size: 0.9rem;
}

/* ─────────────────────────────────────────────
   RECIPE CARD (individual saved recipe row)
───────────────────────────────────────────── */
.recipes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recipe-card {
  padding: 1rem;
  border-radius: 12px;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
}

/* Card header row — title + collapse/remove actions */
.recipe-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  margin-bottom: 0;
}

/* Restore spacing below header when card is expanded */
.recipe-card-header.is-expanded {
  margin-bottom: 0.75rem;
}

.recipe-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--prep-text);
  margin: 0;
  font-family: var(--prep-font-body);
}

/* Right-side actions group (collapse chevron + remove button) */
.recipe-card-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Collapse chevron icon */
.collapse-icon {
  font-size: 0.65rem;
  color: #888;
}

/* RecipeDisplay component wrapper inside a saved card */
.recipe-display-wrap {
  margin-bottom: 0.75rem;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--prep-border);
}

/* Override RecipeDisplay's own box-shadow/border-radius when embedded */
.recipe-display-wrap :deep(.recipe-display) {
  box-shadow: none;
  border-radius: 0;
}

.recipe-text {
  white-space: pre-wrap;
  background: var(--prep-bg);
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--prep-border);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

/* Bottom action row inside a saved card (grocery button) */
.recipe-actions {
  display: flex;
  justify-content: flex-end;
}

/* ─────────────────────────────────────────────
   SHARED BUTTONS
───────────────────────────────────────────── */

/* Primary action button (e.g. Add to Grocery) */
.btn-secondary {
  padding: 0.45rem 1rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-secondary:hover {
  background: var(--prep-primary-hover);
}

/* Destructive remove button on each recipe card */
.btn-remove {
  padding: 0.3rem 0.75rem;
  background: transparent;
  color: var(--prep-error);
  border: 1px solid var(--prep-error);
  border-radius: 8px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-remove:hover {
  background: rgba(248, 81, 73, 0.12);
}
</style>
