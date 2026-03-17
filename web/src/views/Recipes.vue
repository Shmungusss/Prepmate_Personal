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
              <div class="form-group">
                <label for="ingredients">Ingredients</label>
                <textarea
                  id="ingredients"
                  v-model="ingredients"
                  placeholder="chicken, rice, garlic, onions, pasta ..."
                  rows="3"
                />
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
              <RecipeDisplay :recipe="recipe" :hide-actions="true" />
            </div>
            <div class="recipe-actions">
              <button type="button" class="btn-secondary" @click="onAddToGroceryPlaceholder">
                Add to Grocery (coming soon)
              </button>
            </div>
        </template>
      </article>
    </div>
  </section>
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
import AiLoader from '@/components/AiLoader.vue'
import RecipeDisplay from '@/components/RecipeDisplay.vue'

const ADD_MODE_TITLES = {
  ai: 'Generate AI Recipe',
  social: 'Save Recipe From Social Media',
  image: 'Save Recipe From Image',
  text: 'Save Recipe From Text'
}

export default {
  name: 'Recipes',
  components: { AiLoader, RecipeDisplay },
  setup() {
    const store = usePrepMateStore()
    const addDropdownOpen = ref(false)
    const addWrapRef = ref(null)
    const addMode = ref(null)

    const ingredients = ref('')
    const servings = ref(2)
    const cuisine = ref('')
    const dietary = ref('')
    const generating = ref(false)
    const recipeMessage = ref(null)
    const generatedRecipe = ref(null)
    const aiMode = ref('ingredients')
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
    // ──────────────────────────────────────────────────────
    // LOAD SAVED RECIPES ON MOUNT
    // ──────────────────────────────────────────────────────
    onMounted(async () => {
      document.addEventListener('click', onDocClick)
      await store.initialize()  // Load all saved recipes from backend
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
        if (!ingredients.value.trim()) {
          recipeMessage.value = { text: 'Please enter at least one ingredient.', error: true }
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
            ingredients.value,
            servings.value,
            cuisine.value,
            dietary.value
          )
        } else {
          recipe = await generateRecipeFromName(
            recipeName.value,
            servings.value,
            dietary.value
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

    //temp
    function onAddToGroceryPlaceholder() {
      alert('Adding ingredients from a recipe to your grocery list is coming in a future sprint.')
    }


    return {
      addDropdownOpen,
      addWrapRef,
      addMode,
      panelTitle,
      ingredients,
      servings,
      cuisine,
      dietary,
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
      onAddToGroceryPlaceholder,
      aiMode,
      recipeName,
      onSaveGenerated,
      expandedRecipes,
      toggleRecipe,
      
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
