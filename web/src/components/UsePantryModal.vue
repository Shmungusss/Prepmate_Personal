<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-box">
      <h3 class="modal-title">🍳 Update Pantry After Cooking</h3>
      <p class="modal-sub">
        Select the ingredients to deduct from your pantry. Items that run out will be removed.
      </p>

      <!-- Matched items -->
      <div class="section" v-if="matched.length > 0">
        <div class="section-label">Found in pantry</div>
        <div class="item-list">
          <div
            v-for="(m, i) in matched"
            :key="i"
            :class="['use-item', { depleted: m.willDeplete && !m.editing, 'is-editing': m.editing }]"
          >
            <input type="checkbox" v-model="m.selected" class="use-checkbox" @click.stop />
            <div class="use-info">
              <span class="use-name">{{ m.pantryItem.name }}</span>

              <!-- Edit mode -->
              <div v-if="m.editing" class="edit-panel" @click.stop>
                <div class="edit-qty-row">
                  <span class="edit-label">New amount</span>
                  <div class="edit-stepper" :class="{ disabled: m.manualRemove }">
                    <button class="stepper-btn" @click.stop="stepQty(m, -1)" :disabled="m.manualRemove">−</button>
                    <input
                      class="edit-qty-input"
                      type="number"
                      min="0"
                      step="any"
                      v-model="m.manualQty"
                      :disabled="m.manualRemove"
                      @click.stop
                    />
                    <span class="stepper-unit">{{ m.pantryItem.unit }}</span>
                    <button class="stepper-btn" @click.stop="stepQty(m, 1)" :disabled="m.manualRemove">+</button>
                  </div>
                </div>
                <div class="edit-actions-row">
                  <button
                    class="remove-danger-btn"
                    :class="{ active: m.manualRemove }"
                    @click.stop="m.manualRemove = !m.manualRemove"
                  >
                    {{ m.manualRemove ? '✕ Remove from pantry' : 'Remove from pantry' }}
                  </button>
                  <div class="edit-confirm-btns">
                    <button class="edit-action-btn cancel" @click.stop="cancelEdit(m)">Cancel</button>
                    <button class="edit-action-btn apply" @click.stop="commitEdit(m)">Apply</button>
                  </div>
                </div>
              </div>

              <!-- Display mode -->
              <div v-else class="use-change">
                <span class="use-before">{{ m.pantryItem.quantity || '?' }} {{ m.pantryItem.unit }}</span>
                <span class="use-arrow">→</span>
                <template v-if="m.manualRemove || (m.manualQty !== null && parseFloat(m.manualQty) <= 0)">
                  <span class="use-after depleted-text">removed</span>
                </template>
                <template v-else-if="m.manualQty !== null">
                  <span class="use-after">{{ formatQty(parseFloat(m.manualQty)) }} {{ m.pantryItem.unit }}</span>
                </template>
                <template v-else-if="m.willDeplete">
                  <span class="use-after depleted-text">removed</span>
                </template>
                <template v-else-if="m.newQty !== null">
                  <span class="use-after">{{ formatQty(m.newQty) }} {{ m.newUnit }}</span>
                </template>
                <template v-else-if="!m.canCompute">
                  <span class="use-after muted-text">remove (unit mismatch)</span>
                </template>
                <button class="icon-btn edit-btn" @click.stop="startEdit(m)" title="Edit">✎</button>
              </div>

              <span v-if="!m.editing && m.manualQty === null && !m.manualRemove && m.canCompute && !m.willDeplete && normalizeUnit(m.pantryItem.unit) !== normalizeUnit(m.ingredient.unit)" class="converted-note">
                {{ m.ingredient.quantity }} {{ m.ingredient.unit }} converted to {{ m.pantryItem.unit }}
              </span>
              <span v-if="!m.editing && !m.canCompute && m.manualQty === null && !m.manualRemove" class="converted-note warn-note">
                Units don't match — edit to set a new quantity manually
              </span>
            </div>
            <span v-if="!m.editing && (m.manualRemove || (m.manualQty !== null && parseFloat(m.manualQty) <= 0) || (m.manualQty === null && m.willDeplete))" class="depleted-badge">depleted</span>
          </div>
        </div>
      </div>

      <!-- Unmatched items (informational) -->
      <div class="section" v-if="unmatched.length > 0">
        <div class="section-label muted-label">Not in pantry ({{ unmatched.length }})</div>
        <div class="unmatched-list">
          <span v-for="(u, i) in unmatched" :key="i" class="unmatched-chip">
            {{ u.name }}
          </span>
        </div>
      </div>

      <div v-if="matched.length === 0" class="empty-msg">
        None of this recipe's ingredients are currently in your pantry.
      </div>

      <div class="modal-actions">
        <button class="btn btn-ghost" @click="$emit('cancel')">Cancel</button>
        <button
          class="btn btn-primary"
          :disabled="matched.filter(m => m.selected).length === 0"
          @click="onConfirm"
        >
          Update Pantry ({{ matched.filter(m => m.selected).length }} items)
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, computed } from 'vue'
import { normalizeUnit, toBase, fromBase, tryConvert, fuzzyMatch, formatQty } from '../utils/ingredientMatch.js'

export default {
  name: 'UsePantryModal',
  props: {
    recipe: { type: Object, required: true },
    pantryItems: { type: Array, required: true },
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const matched = reactive(
      (props.recipe.ingredients || [])
        .map(ing => {
          const pantryItem = props.pantryItems.find(p => fuzzyMatch(p.name, ing.name))
          if (!pantryItem) return null

          const pantryQty = parseFloat(pantryItem.quantity)
          const ingQty    = ing.quantity

          let newQty = null
          let willDeplete = false
          let canCompute = false
          let newUnit = pantryItem.unit

          if (!isNaN(pantryQty) && ingQty != null) {
            const sameUnit = normalizeUnit(pantryItem.unit) === normalizeUnit(ing.unit)
            if (sameUnit) {
              canCompute = true
              const result = pantryQty - ingQty
              newQty = Math.max(0, result)
              willDeplete = result <= 0
            } else {
              const ingInPantryUnit = tryConvert(pantryQty, pantryItem.unit, ingQty, ing.unit)
              if (ingInPantryUnit !== null) {
                canCompute = true
                const result = pantryQty - ingInPantryUnit
                willDeplete = result <= 0
                newQty = Math.max(0, result)
              }
            }
          }

          // Unit-mismatch items start unchecked — user must opt in
          const selected = canCompute

          return {
            ingredient: ing,
            pantryItem,
            newQty,
            newUnit,
            willDeplete,
            canCompute,
            selected,
            // edit state
            editing: false,
            manualQty: null,   // null = use computed value; string = user override
            manualRemove: false,
            _editSnapshot: null,
          }
        })
        .filter(Boolean)
    )

    function stepQty(m, delta) {
      const current = parseFloat(m.manualQty) || 0
      const stepped = Math.max(0, current + delta)
      m.manualQty = String(formatQty(stepped))
    }

    function startEdit(m) {
      // Snapshot current manual state so we can cancel
      m._editSnapshot = { manualQty: m.manualQty, manualRemove: m.manualRemove }
      // Pre-fill input with current effective qty
      if (m.manualQty !== null) {
        // keep as-is
      } else if (m.willDeplete || m.newQty === null) {
        m.manualQty = '0'
        m.manualRemove = true
      } else {
        m.manualQty = String(formatQty(m.newQty))
      }
      m.editing = true
    }

    function commitEdit(m) {
      m.editing = false
      m._editSnapshot = null
      // Auto-select the row when the user edits it
      m.selected = true
    }

    function cancelEdit(m) {
      m.manualQty = m._editSnapshot.manualQty
      m.manualRemove = m._editSnapshot.manualRemove
      m.editing = false
      m._editSnapshot = null
    }

    const unmatched = computed(() =>
      (props.recipe.ingredients || []).filter(
        ing => !props.pantryItems.some(p => fuzzyMatch(p.name, ing.name))
      )
    )

    function onConfirm() {
      const updates = []
      const deletes = []
      for (const m of matched) {
        if (!m.selected) continue
        const qty = m.manualQty !== null ? parseFloat(m.manualQty) : null
        if (m.manualRemove || (qty !== null && qty <= 0)) {
          deletes.push(m.pantryItem.id)
        } else if (qty !== null) {
          updates.push({ id: m.pantryItem.id, newQty: String(formatQty(qty)), newUnit: m.pantryItem.unit })
        } else if (m.willDeplete || m.newQty === null) {
          deletes.push(m.pantryItem.id)
        } else {
          updates.push({ id: m.pantryItem.id, newQty: String(formatQty(m.newQty)), newUnit: m.pantryItem.unit })
        }
      }
      emit('confirm', { updates, deletes })
    }

    return { matched, unmatched, formatQty, onConfirm, normalizeUnit, startEdit, commitEdit, cancelEdit, stepQty }
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 200;
}

.modal-box {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 14px;
  padding: 1.75rem;
  max-width: 480px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--prep-text);
}

.modal-sub {
  font-size: 0.85rem;
  color: var(--prep-muted);
  margin-top: -0.75rem;
}

.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--prep-primary);
  margin-bottom: 0.5rem;
}

.muted-label {
  color: var(--prep-muted);
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.use-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  transition: background 0.15s;
}

.use-item:hover {
  background: rgba(255,255,255,0.03);
}

.use-item.depleted {
  border-color: rgba(248, 81, 73, 0.3);
}

.use-item.is-editing {
  border-color: var(--prep-primary);
  background: rgba(255,255,255,0.02);
}

.use-checkbox {
  accent-color: var(--prep-primary);
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  cursor: pointer;
}

.use-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.use-name {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--prep-text);
}

.use-change {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
}

.edit-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  flex-wrap: wrap;
}

.use-before {
  color: var(--prep-muted);
}

.use-arrow {
  color: var(--prep-muted);
}

.use-after {
  color: var(--prep-primary);
  font-weight: 600;
}

.depleted-text {
  color: var(--prep-error);
}

.muted-text {
  color: var(--prep-muted);
  font-style: italic;
}

.converted-note {
  font-size: 0.68rem;
  color: var(--prep-muted);
  font-style: italic;
  margin-top: 0.1rem;
}

.warn-note {
  color: var(--prep-warning, #e3a008);
}

.depleted-badge {
  font-size: 0.68rem;
  padding: 0.15rem 0.4rem;
  background: rgba(248, 81, 73, 0.12);
  color: var(--prep-error);
  border-radius: 4px;
  font-weight: 600;
  flex-shrink: 0;
}

.edit-panel {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.edit-qty-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.edit-label {
  font-size: 0.72rem;
  color: var(--prep-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.edit-stepper {
  display: flex;
  align-items: center;
  border: 1px solid var(--prep-primary);
  border-radius: 6px;
  overflow: hidden;
}

.edit-stepper.disabled {
  border-color: var(--prep-border);
  opacity: 0.45;
}

.stepper-btn {
  background: rgba(255,255,255,0.05);
  border: none;
  color: var(--prep-text);
  width: 2rem;
  height: 2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}

.stepper-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.12);
}

.stepper-btn:disabled {
  cursor: not-allowed;
}

.edit-qty-input {
  width: 4.5rem;
  padding: 0.3rem 0.4rem;
  border: none;
  border-left: 1px solid var(--prep-border);
  border-right: 1px solid var(--prep-border);
  background: var(--prep-bg);
  color: var(--prep-text);
  font-size: 0.88rem;
  font-family: var(--prep-font-body);
  text-align: center;
}

.edit-qty-input:focus {
  outline: none;
}

.edit-qty-input:disabled {
  opacity: 0.4;
}

.stepper-unit {
  padding: 0 0.5rem;
  font-size: 0.75rem;
  color: var(--prep-muted);
  white-space: nowrap;
}

.edit-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.remove-danger-btn {
  background: none;
  border: 1px solid transparent;
  border-radius: 5px;
  font-size: 0.72rem;
  color: var(--prep-muted);
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  transition: all 0.15s;
}

.remove-danger-btn:hover {
  color: var(--prep-error);
  border-color: rgba(248, 81, 73, 0.3);
}

.remove-danger-btn.active {
  color: var(--prep-error);
  background: rgba(248, 81, 73, 0.1);
  border-color: rgba(248, 81, 73, 0.4);
}

.edit-confirm-btns {
  display: flex;
  gap: 0.4rem;
}

.edit-action-btn {
  padding: 0.3rem 0.8rem;
  border-radius: 5px;
  font-size: 0.78rem;
  font-family: var(--prep-font-body);
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}

.edit-action-btn.cancel {
  background: transparent;
  color: var(--prep-muted);
  border: 1px solid var(--prep-border);
}

.edit-action-btn.cancel:hover {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

.edit-action-btn.apply {
  background: var(--prep-primary);
  color: var(--prep-bg);
}

.edit-action-btn.apply:hover {
  background: var(--prep-primary-hover);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  font-size: 0.85rem;
  line-height: 1;
  transition: background 0.15s;
}

.edit-btn {
  color: var(--prep-muted);
  opacity: 0.45;
  margin-left: auto;
}

.edit-btn:hover {
  opacity: 1;
  background: rgba(255,255,255,0.08);
}

.unmatched-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.unmatched-chip {
  font-size: 0.78rem;
  padding: 0.2rem 0.55rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--prep-border);
  border-radius: 20px;
  color: var(--prep-muted);
}

.empty-msg {
  text-align: center;
  font-size: 0.85rem;
  color: var(--prep-muted);
  padding: 1rem;
  border: 1px dashed var(--prep-border);
  border-radius: 8px;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding-top: 0.25rem;
  border-top: 1px solid var(--prep-border);
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

.btn-primary:hover:not(:disabled) {
  background: var(--prep-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
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
