<template>
  <div class="page">
    <header class="header">
      <h1 class="title">Grocery List</h1>
      <p class="subtitle">
        Add, edit, and remove ingredients from your grocery list. Later, recipes will be able
        to push ingredients straight here.
      </p>
    </header>

    <!-- Add item form -->
    <form class="add-form" @submit.prevent="onAddItem">
      <div class="field">
        <label for="name">Ingredient</label>
        <input
          id="name"
          v-model="newItemName"
          type="text"
          placeholder="e.g. chicken breast"
        />
      </div>
      <div class="field">
        <label for="quantity">Quantity</label>
        <input
          id="quantity"
          v-model="newItemQuantity"
          type="text"
          placeholder="e.g. 2 lbs, 3 pcs"
        />
      </div>
      <button class="btn-primary" type="submit">Add to List</button>
    </form>

    <!-- List -->
    <section class="list-section" v-if="items.length">
      <ul class="list">
        <li v-for="item in items" :key="item.id" class="list-item">
          <div class="item-main">
            <input
              class="item-name-input"
              v-model="item.name"
              type="text"
            />
            <input
              class="item-qty-input"
              v-model="item.quantity"
              type="text"
              :ref="el => setQuantityRef(item.id, el)"
            />
          </div>
          <div class="item-menu">
            <button
              type="button"
              class="btn-menu"
              @click="toggleMenu(item.id)"
            >
              ⋮
            </button>
            <div
              v-if="openMenuId === item.id"
              class="menu-dropdown"
            >
              <button
                type="button"
                class="menu-item"
                @click="focusQuantity(item.id)"
              >
                Edit quantity
              </button>
              <button
                type="button"
                class="menu-item delete"
                @click="onDeleteItem(item.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
    </section>
    <section class="list-section" v-else>
      <p class="empty-state">
        Your grocery list is empty. Add your first ingredient above.
      </p>
    </section>
  </div>
</template>

<script>
import { ref } from 'vue'
import { usePrepMateStore } from '@/store/prepMateStore'

export default {
  name: 'GroceryList',
  setup() {
    const store = usePrepMateStore()
    const newItemName = ref('')
    const newItemQuantity = ref('')
    const openMenuId = ref(null)
    const quantityInputs = ref({})

    function setQuantityRef(id, el) {
      if (!el) return
      quantityInputs.value[id] = el
    }

    function toggleMenu(id) {
      openMenuId.value = openMenuId.value === id ? null : id
    }

    function focusQuantity(id) {
      const el = quantityInputs.value[id]
      if (el) {
        el.focus()
      }
      openMenuId.value = null
    }

    function onAddItem() {
      const name = newItemName.value.trim()
      const quantity = newItemQuantity.value.trim()

      if (!name) return

      store.addGroceryItem({
        name,
        quantity: quantity || ''
      })

      newItemName.value = ''
      newItemQuantity.value = ''
    }

    function onDeleteItem(id) {
      store.deleteGroceryItem(id)
      if (openMenuId.value === id) {
        openMenuId.value = null
      }
    }

    return {
      newItemName,
      newItemQuantity,
      items: store.groceryItems,
      openMenuId,
      setQuantityRef,
      toggleMenu,
      focusQuantity,
      onAddItem,
      onDeleteItem
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

.add-form {
  display: grid;
  grid-template-columns: 2fr 1.2fr auto;
  gap: 0.75rem;
  align-items: end;
  margin-bottom: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #444;
}

.field input {
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  border: 1px solid #d0d7de;
  font-size: 0.95rem;
}

.btn-primary {
  padding: 0.65rem 1.2rem;
  background: #2d8a5e;
  color: white;
  border: none;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:hover {
  background: #247a50;
}

.list-section {
  border-radius: 12px;
  background: #f8f9fa;
  padding: 1.25rem;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.item-main {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 0.5rem;
  flex: 1;
}

.item-name-input,
.item-qty-input {
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  border: 1px solid #cfd4da;
  font-size: 0.9rem;
}

.item-menu {
  position: relative;
}

.btn-menu {
  padding: 0.3rem 0.6rem;
  background: #e1e7eb;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.btn-menu:hover {
  background: #cfd7de;
}

.menu-dropdown {
  position: absolute;
  right: 0;
  top: 120%;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 0.25rem 0;
  min-width: 150px;
  z-index: 5;
}

.menu-item {
  display: block;
  width: 100%;
  padding: 0.4rem 0.9rem;
  background: transparent;
  border: none;
  text-align: left;
  font-size: 0.85rem;
  cursor: pointer;
}

.menu-item:hover {
  background: #f3f4f6;
}

.menu-item.delete {
  color: #c62828;
}

.empty-state {
  color: #666;
  font-size: 0.95rem;
}

@media (max-width: 640px) {
  .add-form {
    grid-template-columns: 1fr;
    align-items: stretch;
  }
}
</style>

