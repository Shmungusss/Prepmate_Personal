<template>
  <div class="page">
    <header class="header">
      <h1 class="title">Grocery List</h1>
      <p class="subtitle">
        Add items and check them off as you shop.
      </p>
    </header>

    <form class="add-form" @submit.prevent="onAddItem">
      <div class="add-row">
        <input
          id="ingredient-input"
          v-model="addName"
          type="text"
          class="add-input"
          placeholder="Add an item..."
          autocomplete="off"
          @focus="addExpanded = true"
        />
        <button class="btn-add" type="submit" :disabled="!addName.trim()">+</button>
      </div>

      <Transition name="expand">
        <div v-if="addExpanded" class="add-details">
          <div class="add-details-row">
            <div class="detail-field">
              <label class="detail-label">Qty</label>
              <input v-model="addAmount" type="text" inputmode="decimal" class="detail-input detail-input--qty" placeholder="2" />
            </div>
            <div class="detail-field">
              <label class="detail-label">Unit</label>
              <select v-model="addUnit" class="detail-input detail-input--unit">
                <option value="">—</option>
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
                </optgroup>
              </select>
            </div>
            <div class="detail-field detail-field--brand">
              <label class="detail-label">Brand <span class="optional-tag">optional</span></label>
              <input v-model="addBrand" type="text" class="detail-input" placeholder="e.g. Trader Joe's" />
            </div>
          </div>
        </div>
      </Transition>
    </form>

    <!-- Progress bar -->
    <div v-if="items.length" class="progress-strip">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="progress-label">{{ checkedCount }} / {{ items.length }} items</span>
    </div>

    <section class="list-section" v-if="items.length">
      <!-- Unchecked items -->
      <TransitionGroup name="item" tag="ul" class="list">
        <li
          v-for="item in uncheckedItems"
          :key="item.id"
          class="list-item"
        >
          <!-- Inline edit mode -->
          <template v-if="editingId === item.id">
            <form class="edit-form" @submit.prevent="onSaveEdit(item.id)">
              <input v-model="editName" class="edit-input edit-input--name" placeholder="Item name" />
              <input v-model="editAmount" type="text" inputmode="decimal" class="edit-input edit-input--qty" placeholder="Qty" />
              <select v-model="editUnit" class="edit-input edit-input--unit">
                <option value="">—</option>
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
                </optgroup>
              </select>
              <input v-model="editBrand" class="edit-input edit-input--brand" placeholder="Brand" />
              <button type="submit" class="btn-edit-save">Save</button>
              <button type="button" class="btn-edit-cancel" @click="cancelEdit">Cancel</button>
            </form>
          </template>

          <!-- Normal display -->
          <template v-else>
            <label class="check-wrap">
              <input type="checkbox" :checked="false" @change="toggleChecked(item.id)" />
              <span class="check-label">
                <span v-if="item.amount" class="item-amount">{{ item.amount }}{{ item.unit ? ' ' + item.unit : '' }}</span>
                {{ item.name }}<span v-if="item.brand" class="item-brand"> · {{ item.brand }}</span>
                <span v-if="item.suggestedLocation" class="item-location-hint">{{ item.suggestedLocation }}</span>
              </span>
            </label>
            <div class="item-actions">
              <button
                type="button"
                class="btn-icon btn-edit"
                aria-label="Edit item"
                @click="onStartEdit(item)"
              >
                Edit
              </button>
              <button
                type="button"
                class="btn-icon btn-remove"
                aria-label="Remove item"
                @click="onDeleteItem(item.id)"
              >
                &times;
              </button>
            </div>
          </template>
        </li>
      </TransitionGroup>

      <!-- Checked items (collapsible) -->
      <div v-if="checkedItems.length" class="checked-section">
        <button type="button" class="checked-toggle" @click="showChecked = !showChecked">
          <span class="checked-toggle-label">Checked ({{ checkedItems.length }})</span>
          <span class="chevron" :class="{ open: showChecked }">&#9662;</span>
        </button>

        <TransitionGroup v-if="showChecked" name="item" tag="ul" class="list checked-list">
          <li
            v-for="item in checkedItems"
            :key="item.id"
            class="list-item is-checked"
          >
            <label class="check-wrap">
              <input type="checkbox" :checked="true" @change="toggleChecked(item.id)" />
              <span class="check-label">
                <span v-if="item.amount" class="item-amount">{{ item.amount }}{{ item.unit ? ' ' + item.unit : '' }}</span>
                {{ item.name }}<span v-if="item.brand" class="item-brand"> · {{ item.brand }}</span>
              </span>
            </label>
            <button
              type="button"
              class="btn-icon btn-remove"
              aria-label="Remove item"
              @click="onDeleteItem(item.id)"
            >
              &times;
            </button>
          </li>
        </TransitionGroup>
      </div>

      <div class="list-footer">
        <!-- Move to pantry -->
        <div v-if="checkedItems.length" class="move-to-pantry-wrap">
          <span class="move-label">Move checked to Pantry <span class="move-label-hint">(fallback location)</span>:</span>
          <div class="move-controls">
            <select v-model="pantryMoveLocation" class="move-select" :disabled="movingToPantry">
              <option v-for="loc in PANTRY_LOCATIONS" :key="loc.value" :value="loc.value">
                {{ loc.label }}
              </option>
            </select>
            <button type="button" class="btn-move-pantry" @click="onMoveToPantry" :disabled="movingToPantry">
              {{ movingToPantry ? 'Moving…' : `Move (${checkedItems.length})` }}
            </button>
          </div>
          <p v-if="moveError" class="move-error">{{ moveError }}</p>
        </div>
        <div class="clear-actions">
          <button type="button" class="btn-clear" @click="onClearChecked" :disabled="!checkedItems.length">
            Clear checked
          </button>
          <button type="button" class="btn-clear btn-clear--all" @click="onClearAll">
            Clear all
          </button>
        </div>
      </div>
    </section>

    <section class="empty-section" v-else>
      <p class="empty-title">Your list is empty</p>
      <p class="empty-hint">
        Type an item above, or add ingredients directly from a saved recipe on the
        <router-link :to="{ name: 'Recipes' }" class="empty-link">Recipes</router-link> page.
      </p>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePrepMateStore } from '@/store/prepMateStore'
import { usePantryStore, PANTRY_LOCATIONS } from '@/store/pantryStore'

export default {
  name: 'GroceryList',
  setup() {
    const store = usePrepMateStore()
    const pantryStore = usePantryStore()

    const pantryMoveLocation = ref('pantry')

    const movingToPantry = ref(false)
    const moveError = ref('')

    async function onMoveToPantry() {
      if (movingToPantry.value) return
      movingToPantry.value = true
      moveError.value = ''
      const failed = []
      for (const item of checkedItems.value) {
        try {
          await pantryStore.addItem({
            name: item.name,
            quantity: item.amount ?? '',
            unit: item.unit ?? '',
            location: item.suggestedLocation || pantryMoveLocation.value,
            category: item.category || 'Other',
          })
          store.deleteGroceryItem(item.id)
        } catch {
          failed.push(item.name)
        }
      }
      movingToPantry.value = false
      if (failed.length) {
        moveError.value = `Failed to move: ${failed.join(', ')}. Try again.`
      }
    }

    // Add form state
    const addName = ref('')
    const addAmount = ref('')
    const addUnit = ref('')
    const addBrand = ref('')
    const addExpanded = ref(false)
    const showChecked = ref(true)

    // Edit state
    const editingId = ref(null)
    const editName = ref('')
    const editAmount = ref('')
    const editUnit = ref('')
    const editBrand = ref('')

    const items = computed(() => store.groceryItems.value || [])
    const uncheckedItems = computed(() => items.value.filter((i) => !i.checked))
    const checkedItems = computed(() => items.value.filter((i) => i.checked))
    const checkedCount = computed(() => checkedItems.value.length)
    const progressPercent = computed(() =>
      items.value.length ? (checkedCount.value / items.value.length) * 100 : 0
    )

    function onAddItem() {
      const name = addName.value.trim()
      if (!name) return

      const duplicate = items.value.some(
        (i) => i.name.toLowerCase() === name.toLowerCase()
      )
      if (duplicate) return

      store.addGroceryItem({
        name,
        amount: addAmount.value.trim(),
        unit: addUnit.value.trim(),
        brand: addBrand.value.trim(),
        category: 'Other',
      })

      addName.value = ''
      addAmount.value = ''
      addUnit.value = ''
      addBrand.value = ''
      addExpanded.value = false
    }

    function onDeleteItem(id) {
      store.deleteGroceryItem(id)
      if (editingId.value === id) editingId.value = null
    }

    function onStartEdit(item) {
      editingId.value = item.id
      editName.value = item.name
      editAmount.value = item.amount ?? ''
      editUnit.value = item.unit ?? ''
      editBrand.value = item.brand ?? ''
    }

    function onSaveEdit(id) {
      const name = editName.value.trim()
      if (!name) return
      store.updateGroceryItem(id, {
        name,
        amount: editAmount.value.trim(),
        unit: editUnit.value.trim(),
        brand: editBrand.value.trim(),
      })
      editingId.value = null
    }

    function cancelEdit() {
      editingId.value = null
    }

    function onClearChecked() {
      for (const item of checkedItems.value) {
        store.deleteGroceryItem(item.id)
      }
    }

    function onClearAll() {
      store.clearGroceryItems()
    }

    function toggleChecked(id) {
      store.toggleGroceryItemChecked(id)
    }

    function onKeydown(e) {
      if (e.key === 'Escape') {
        if (editingId.value !== null) editingId.value = null
        else addExpanded.value = false
      }
    }

    onMounted(() => {
      store.initialize()
      document.addEventListener('keydown', onKeydown)
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', onKeydown)
    })

    return {
      addName,
      addAmount,
      addUnit,
      addBrand,
      addExpanded,
      items,
      uncheckedItems,
      checkedItems,
      checkedCount,
      progressPercent,
      showChecked,
      editingId,
      editName,
      editAmount,
      editUnit,
      editBrand,
      onAddItem,
      onDeleteItem,
      onStartEdit,
      onSaveEdit,
      cancelEdit,
      onClearChecked,
      onClearAll,
      toggleChecked,
      pantryMoveLocation,
      movingToPantry,
      moveError,
      onMoveToPantry,
      PANTRY_LOCATIONS,
    }
  },
}
</script>

<style scoped>
.page {
  max-width: 600px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

/* ── Header ──────────────────────────────────── */
.header {
  margin-bottom: 1.25rem;
}

.title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
  color: var(--prep-text);
  font-family: var(--prep-font-display);
}

.subtitle {
  color: var(--prep-muted);
  font-size: 0.9rem;
}

/* ── Add form ────────────────────────────────── */
.add-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 0.75rem;
  transition: border-color 0.2s;
}

.add-form:focus-within {
  border-color: var(--prep-primary);
}

.add-row {
  display: flex;
  gap: 0.5rem;
}

.add-input {
  flex: 1;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--prep-border);
  font-size: 0.95rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.add-input::placeholder {
  color: var(--prep-muted);
}

.add-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.15);
}

.btn-add {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  border: none;
  background: var(--prep-primary);
  color: var(--prep-bg);
  font-size: 1.4rem;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s, transform 0.15s;
}

.btn-add:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-add:hover:not(:disabled) {
  background: var(--prep-primary-hover);
  transform: scale(1.05);
}

/* ── Add details row ─────────────────────────── */
.add-details {
  overflow: hidden;
}

.add-details-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.detail-field--brand {
  flex: 1;
  min-width: 140px;
}

.detail-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--prep-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.optional-tag {
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--prep-muted);
  text-transform: none;
  letter-spacing: 0;
  opacity: 0.7;
}

.detail-input {
  padding: 0.45rem 0.6rem;
  border-radius: 7px;
  border: 1px solid var(--prep-border);
  font-size: 0.88rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.detail-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.15);
}

.detail-input--qty {
  width: 60px;
}

.detail-input--unit {
  width: 110px;
}

/* ── Expand transition ───────────────────────── */
.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── Progress strip ──────────────────────────── */
.progress-strip {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.progress-track {
  flex: 1;
  height: 6px;
  background: var(--prep-border);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--prep-primary);
  border-radius: 999px;
  transition: width 0.35s ease;
}

.progress-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--prep-muted);
  white-space: nowrap;
}

/* ── List section ────────────────────────────── */
.list-section {
  border-radius: 12px;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  padding: 0.75rem 1rem;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.25rem;
  border-bottom: 1px solid var(--prep-border);
  transition: background 0.15s;
}

.list-item:last-child {
  border-bottom: none;
}

.list-item:hover {
  background: rgba(0, 200, 180, 0.04);
}

.list-item.is-checked .check-label {
  opacity: 0.45;
  text-decoration: line-through;
}

/* ── Checkbox + label ────────────────────────── */
.check-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.check-wrap input[type='checkbox'] {
  width: 18px;
  height: 18px;
  accent-color: var(--prep-primary);
  cursor: pointer;
  flex-shrink: 0;
}

.check-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--prep-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-amount {
  font-weight: 700;
  color: var(--prep-primary);
  margin-right: 0.2rem;
}

.item-brand {
  font-size: 0.82rem;
  color: var(--prep-muted);
  font-weight: 400;
}

.item-location-hint {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.1);
  border-radius: 4px;
  padding: 0.05rem 0.4rem;
  margin-left: 0.35rem;
  text-transform: capitalize;
  vertical-align: middle;
}

.move-label-hint {
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--prep-muted);
}

/* ── Item action buttons ─────────────────────── */
.item-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}

.list-item:hover .item-actions,
.list-item:focus-within .item-actions {
  opacity: 1;
}

.btn-icon {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-family: var(--prep-font-body);
  font-size: 0.8rem;
  font-weight: 600;
  background: transparent;
  transition: background 0.15s, color 0.15s;
}

.btn-edit {
  color: var(--prep-muted);
}

.btn-edit:hover {
  color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.1);
}

.btn-remove {
  color: var(--prep-muted);
  font-size: 1.1rem;
  line-height: 1;
  padding: 0.15rem 0.4rem;
}

.btn-remove:hover {
  color: var(--prep-error);
  background: rgba(248, 81, 73, 0.1);
}

/* ── Edit form ───────────────────────────────── */
.edit-form {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  flex: 1;
  flex-wrap: wrap;
}

.edit-input {
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  border: 1px solid var(--prep-border);
  font-size: 0.88rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.edit-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.18);
}

.edit-input--name {
  flex: 1;
  min-width: 100px;
}

.edit-input--qty {
  width: 55px;
}

.edit-input--unit {
  width: 110px;
}

.edit-input--brand {
  width: 100px;
}

.btn-edit-save {
  padding: 0.35rem 0.65rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-edit-save:hover {
  background: var(--prep-primary-hover);
}

.btn-edit-cancel {
  padding: 0.35rem 0.65rem;
  background: transparent;
  color: var(--prep-muted);
  border: 1px solid var(--prep-border);
  border-radius: 6px;
  font-size: 0.82rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-edit-cancel:hover {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

/* ── Checked section ─────────────────────────── */
.checked-section {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--prep-border);
}

.checked-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: 100%;
  padding: 0.45rem 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.checked-toggle-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--prep-muted);
}

.chevron {
  font-size: 0.7rem;
  color: var(--prep-muted);
  transition: transform 0.2s;
}

.chevron.open {
  transform: rotate(180deg);
}

.checked-list .list-item {
  padding: 0.4rem 0.25rem;
}

/* ── Footer buttons ──────────────────────────── */
.list-footer {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding-top: 0.75rem;
  margin-top: 0.5rem;
  border-top: 1px solid var(--prep-border);
}

.move-to-pantry-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  padding: 0.6rem 0.75rem;
  background: rgba(0, 200, 180, 0.06);
  border: 1px solid rgba(0, 200, 180, 0.25);
  border-radius: 8px;
}

.move-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--prep-muted);
  white-space: nowrap;
}

.move-controls {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex: 1;
}

.move-select {
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  border: 1px solid var(--prep-border);
  background: var(--prep-bg);
  color: var(--prep-text);
  font-size: 0.85rem;
  font-family: var(--prep-font-body);
}

.btn-move-pantry {
  padding: 0.35rem 0.85rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  white-space: nowrap;
  transition: background 0.15s;
}

.btn-move-pantry:hover:not(:disabled) { background: var(--prep-primary-hover); }
.btn-move-pantry:disabled { opacity: 0.6; cursor: not-allowed; }

.move-error {
  font-size: 0.78rem;
  color: var(--prep-error);
  margin-top: 0.35rem;
}

.clear-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-clear {
  padding: 0.4rem 0.8rem;
  background: transparent;
  color: var(--prep-muted);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.15s;
}

.btn-clear:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-clear:hover:not(:disabled) {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

.btn-clear--all {
  color: var(--prep-error);
  border-color: transparent;
}

.btn-clear--all:hover {
  color: var(--prep-error);
  background: rgba(248, 81, 73, 0.08);
  border-color: var(--prep-error);
}

/* ── Empty state ─────────────────────────────── */
.empty-section {
  text-align: center;
  padding: 3rem 1.5rem;
  border-radius: 12px;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
}

.empty-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--prep-text);
  margin-bottom: 0.5rem;
}

.empty-hint {
  color: var(--prep-muted);
  font-size: 0.9rem;
  line-height: 1.6;
}

.empty-link {
  color: var(--prep-primary);
  text-decoration: none;
  font-weight: 600;
}

.empty-link:hover {
  text-decoration: underline;
}

/* ── List transitions ────────────────────────── */
.item-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.item-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.item-enter-from {
  opacity: 0;
  transform: translateX(-12px);
}

.item-leave-to {
  opacity: 0;
  transform: translateX(12px);
}

.item-move {
  transition: transform 0.25s ease;
}

/* ── Responsive ──────────────────────────────── */
@media (max-width: 480px) {
  .item-actions {
    opacity: 1;
  }
}
</style>
