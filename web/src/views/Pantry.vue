<template>
  <div class="page">
    <header class="header">
      <div class="header-top">
        <div>
          <h1 class="title">Pantry</h1>
          <p class="subtitle">Track what you have on hand.</p>
        </div>
        <div class="header-actions">
          <button class="btn-scan-receipt" @click="onToggleBarcode">
            {{ showBarcodePanel ? 'Cancel' : '🔍 Scan Barcode' }}
          </button>
          <button class="btn-scan-receipt" @click="onToggleScan">
            {{ showScanPanel ? 'Cancel Scan' : '📷 Scan Receipt' }}
          </button>
          <button class="btn-add-item" @click="showAddForm = !showAddForm">
            {{ showAddForm ? 'Cancel' : '+ Add Item' }}
          </button>
        </div>
      </div>

      <!-- Add item form -->
      <Transition name="expand">
        <form v-if="showAddForm" class="add-form" @submit.prevent="onAddItem">
          <div class="add-fields">
            <div class="field field--name">
              <label class="field-label">Item name *</label>
              <input v-model="addName" type="text" class="field-input" placeholder="e.g. Eggs" autocomplete="off" ref="addNameRef" />
            </div>
            <div class="field field--qty">
              <label class="field-label">Qty</label>
              <input v-model="addQuantity" type="text" inputmode="decimal" class="field-input" placeholder="2" />
            </div>
            <div class="field field--unit">
              <label class="field-label">Unit</label>
              <select v-model="addUnit" class="field-input">
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
            <div class="field field--location">
              <label class="field-label">Location *</label>
              <select v-model="addLocation" class="field-input">
                <option v-for="loc in PANTRY_LOCATIONS" :key="loc.value" :value="loc.value">
                  {{ loc.label }}
                </option>
              </select>
            </div>
            <div class="field field--category">
              <label class="field-label">Category</label>
              <select v-model="addCategory" class="field-input">
                <option value="">Auto</option>
                <option v-for="cat in PANTRY_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
          </div>
          <div class="add-actions">
            <button type="submit" class="btn-save" :disabled="!addName.trim()">Add to Pantry</button>
            <button type="button" class="btn-cancel" @click="resetAddForm">Cancel</button>
          </div>
        </form>
      </Transition>

      <!-- Barcode scan panel -->
      <Transition name="expand">
        <div v-if="showBarcodePanel" class="scan-panel">

          <!-- Camera view (live scanning) -->
          <template v-if="barcodeSupported && !barcodeProduct && !barcodeLookingUp">
            <div v-if="barcodeCameraActive" class="barcode-camera-wrap">
              <video ref="barcodeVideoRef" class="barcode-video" autoplay playsinline muted />
              <div class="barcode-reticle">
                <div class="barcode-reticle-inner" />
              </div>
              <p class="barcode-hint">Point at a product barcode</p>
              <button type="button" class="btn-cancel barcode-cancel-btn" @click="stopBarcodeCamera">Cancel</button>
            </div>
            <div v-else class="scan-drop-zone" @click="startBarcodeCamera">
              <span class="scan-drop-icon">🔍</span>
              <p class="scan-drop-title">Scan a product barcode</p>
              <p class="scan-drop-hint">Click to open camera and point at any product barcode</p>
            </div>
          </template>

          <!-- Fallback: manual UPC entry (non-Chrome browsers) -->
          <template v-else-if="!barcodeSupported && !barcodeProduct && !barcodeLookingUp">
            <p class="barcode-unsupported-note">Live scanning requires Chrome or Edge. Enter the barcode number manually:</p>
            <div class="barcode-manual-row">
              <input
                v-model="manualUpc"
                type="text"
                inputmode="numeric"
                class="field-input barcode-manual-input"
                placeholder="e.g. 049000028904"
                @keydown.enter.prevent="onManualUpcLookup"
              />
              <button type="button" class="btn-save" :disabled="!manualUpc.trim()" @click="onManualUpcLookup">Look up</button>
            </div>
          </template>

          <!-- Looking up -->
          <div v-else-if="barcodeLookingUp" class="scan-loading">
            <span class="scan-spinner" />
            <p class="scan-loading-text">Looking up product…</p>
          </div>

          <!-- Product found — confirm form -->
          <template v-else-if="barcodeProduct">
            <p class="barcode-found-title" :class="{ 'barcode-not-found': barcodeProduct._notFound }">
              {{ barcodeProduct._notFound ? 'Product not in database — enter details manually' : 'Product found — confirm details' }}
            </p>
            <div class="barcode-confirm-form">
              <div class="add-fields">
                <div class="field field--name">
                  <label class="field-label">Item name *</label>
                  <input v-model="barcodeProduct.name" type="text" class="field-input" />
                </div>
                <div class="field field--qty">
                  <label class="field-label">Qty</label>
                  <input v-model="barcodeProduct.quantity" type="text" inputmode="decimal" class="field-input" />
                </div>
                <div class="field field--unit">
                  <label class="field-label">Unit</label>
                  <input v-model="barcodeProduct.unit" type="text" class="field-input" />
                </div>
                <div class="field field--location">
                  <label class="field-label">Location *</label>
                  <select v-model="barcodeProduct.location" class="field-input">
                    <option v-for="loc in PANTRY_LOCATIONS" :key="loc.value" :value="loc.value">{{ loc.label }}</option>
                  </select>
                </div>
                <div class="field field--category">
                  <label class="field-label">Category</label>
                  <select v-model="barcodeProduct.category" class="field-input">
                    <option v-for="cat in PANTRY_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                  </select>
                </div>
                <div v-if="barcodeProduct.brand" class="field field--brand">
                  <label class="field-label">Brand</label>
                  <input v-model="barcodeProduct.brand" type="text" class="field-input" />
                </div>
              </div>
              <div class="add-actions">
                <button type="button" class="btn-save" :disabled="!barcodeProduct.name.trim()" @click="onConfirmBarcode">
                  Add to Pantry
                </button>
                <button type="button" class="btn-cancel" @click="onScanAnother">Scan another</button>
              </div>
            </div>
          </template>

          <p v-if="barcodeError" class="scan-error">{{ barcodeError }}</p>
        </div>
      </Transition>

      <!-- Receipt scan panel -->
      <Transition name="expand">
        <div v-if="showScanPanel" class="scan-panel">
          <!-- Upload area (shown when no items extracted yet) -->
          <template v-if="!scanItems.length && !scanLoading">
            <div
              class="scan-drop-zone"
              :class="{ 'scan-drop-zone--over': scanDragOver }"
              @click="triggerScanUpload"
              @dragover.prevent="scanDragOver = true"
              @dragleave="scanDragOver = false"
              @drop.prevent="onScanDrop"
            >
              <span class="scan-drop-icon">🧾</span>
              <p class="scan-drop-title">Upload a receipt photo</p>
              <p class="scan-drop-hint">Click to browse or drag & drop an image</p>
            </div>
            <input
              ref="scanFileInputRef"
              type="file"
              accept="image/*"
              capture="environment"
              class="scan-file-input"
              @change="onScanFileChange"
            />
            <p v-if="scanError" class="scan-error">{{ scanError }}</p>
          </template>

          <!-- Loading state -->
          <div v-else-if="scanLoading" class="scan-loading">
            <span class="scan-spinner"></span>
            <p class="scan-loading-text">Scanning receipt…</p>
          </div>

          <!-- Review items -->
          <template v-else>
            <div class="scan-review-header">
              <div>
                <p class="scan-review-title">Review extracted items</p>
                <p class="scan-review-hint">Uncheck any items you don't want to add.</p>
              </div>
              <button class="btn-scan-again" type="button" @click="resetScan">Try again</button>
            </div>

            <ul class="scan-item-list">
              <li
                v-for="item in scanItems"
                :key="item._sid"
                class="scan-item-row"
                :class="{ 'scan-item-row--unchecked': !item.selected }"
              >
                <input
                  type="checkbox"
                  class="scan-checkbox"
                  :checked="item.selected"
                  @change="item.selected = !item.selected"
                />
                <div class="scan-item-fields">
                  <input v-model="item.name" class="scan-field scan-field--name" placeholder="Name" />
                  <input v-model="item.quantity" type="text" inputmode="decimal" class="scan-field scan-field--qty" placeholder="Qty" />
                  <input v-model="item.unit" class="scan-field scan-field--unit" placeholder="Unit" />
                  <select v-model="item.category" class="scan-field scan-field--cat">
                    <option v-for="cat in PANTRY_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                  </select>
                </div>
              </li>
            </ul>

            <div class="scan-confirm-row">
              <div class="scan-location-wrap">
                <label class="scan-location-label">Add to</label>
                <select v-model="scanLocation" class="scan-location-select">
                  <option v-for="loc in PANTRY_LOCATIONS" :key="loc.value" :value="loc.value">
                    {{ loc.label }}
                  </option>
                </select>
              </div>
              <button
                type="button"
                class="btn-scan-confirm"
                :disabled="!scanSelectedCount"
                @click="onConfirmScan"
              >
                Add {{ scanSelectedCount }} item{{ scanSelectedCount === 1 ? '' : 's' }} to Pantry
              </button>
            </div>
          </template>
        </div>
      </Transition>
    </header>

    <!-- Search + tabs -->
    <div class="controls">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search pantry..."
          autocomplete="off"
        />
        <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''" aria-label="Clear search">&times;</button>
      </div>

      <div class="tabs" role="tablist">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          type="button"
          role="tab"
          :class="['tab', { active: activeTab === tab.value }]"
          :aria-selected="activeTab === tab.value"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
          <span v-if="tabCounts[tab.value]" class="tab-count">{{ tabCounts[tab.value] }}</span>
        </button>
      </div>
    </div>

    <!-- Item list -->
    <div v-if="visibleGroups.length" class="groups">
      <section v-for="group in visibleGroups" :key="group.category" class="category-group">
        <h2 class="category-heading">{{ group.category }}</h2>
        <TransitionGroup name="item" tag="ul" class="item-list">
          <li v-for="item in group.items" :key="item.id" class="item-row">

            <!-- Edit mode -->
            <template v-if="editingId === item.id">
              <form class="edit-form" @submit.prevent="onSaveEdit(item.id)">
                <input v-model="editName" class="edit-input edit-input--name" placeholder="Name" />
                <input v-model="editQuantity" type="text" inputmode="decimal" class="edit-input edit-input--qty" placeholder="Qty" />
                <input v-model="editUnit" class="edit-input edit-input--unit" placeholder="Unit" />
                <select v-model="editLocation" class="edit-input edit-input--loc">
                  <option v-for="loc in PANTRY_LOCATIONS" :key="loc.value" :value="loc.value">{{ loc.label }}</option>
                </select>
                <select v-model="editCategory" class="edit-input edit-input--cat">
                  <option v-for="cat in PANTRY_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                </select>
                <button type="submit" class="btn-edit-save">Save</button>
                <button type="button" class="btn-edit-cancel" @click="cancelEdit">Cancel</button>
              </form>
            </template>

            <!-- Normal display -->
            <template v-else>
              <div class="item-info">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-qty" v-if="item.quantity">{{ item.quantity }}{{ item.unit ? ' ' + item.unit : '' }}</span>
                <span class="item-location-badge">{{ locationLabel(item.location) }}</span>
              </div>
              <div class="item-actions">
                <!-- Quick qty controls -->
                <div class="qty-controls">
                  <button type="button" class="qty-btn" @click="adjustQty(item, -1)" aria-label="Decrease">−</button>
                  <span class="qty-display">{{ item.quantity || '—' }}</span>
                  <button type="button" class="qty-btn" @click="adjustQty(item, +1)" aria-label="Increase">+</button>
                </div>
                <button type="button" class="btn-icon btn-edit-icon" @click="onStartEdit(item)">Edit</button>
                <button type="button" class="btn-icon btn-remove" @click="store.removeItem(item.id)" aria-label="Remove">&times;</button>
              </div>
            </template>

          </li>
        </TransitionGroup>
      </section>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <template v-if="searchQuery">
        <p class="empty-title">No results for "{{ searchQuery }}"</p>
        <p class="empty-hint">Try a different search term.</p>
      </template>
      <template v-else-if="activeTab !== 'all'">
        <p class="empty-title">Nothing in your {{ currentTabLabel }} yet</p>
        <p class="empty-hint">Add an item above or move checked groceries here from the <router-link :to="{ name: 'GroceryList' }" class="empty-link">Grocery List</router-link>.</p>
      </template>
      <template v-else>
        <p class="empty-title">Your pantry is empty</p>
        <p class="empty-hint">Add items above or move purchased groceries from the <router-link :to="{ name: 'GroceryList' }" class="empty-link">Grocery List</router-link> page.</p>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { usePantryStore, PANTRY_LOCATIONS, PANTRY_CATEGORIES } from '@/store/pantryStore'
import { scanReceipt, lookupBarcode } from '@/services/api'

export default {
  name: 'Pantry',
  setup() {
    const store = usePantryStore()

    onMounted(() => store.initialize())
    onUnmounted(() => stopBarcodeCamera())

    // ── Tabs ───────────────────────────────────────
    const tabs = [
      { value: 'all',     label: 'All' },
      ...PANTRY_LOCATIONS.map((l) => ({ value: l.value, label: l.label })),
    ]
    const activeTab = ref('all')
    const currentTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label ?? '')

    // ── Search ─────────────────────────────────────
    const searchQuery = ref('')

    // ── Filtered + grouped items ───────────────────
    const filteredItems = computed(() => {
      let items = store.items.value
      if (activeTab.value !== 'all') {
        items = items.filter((i) => i.location === activeTab.value)
      }
      const q = searchQuery.value.trim().toLowerCase()
      if (q) {
        items = items.filter((i) => i.name.toLowerCase().includes(q))
      }
      return items
    })

    const visibleGroups = computed(() => {
      const byCat = new Map()
      for (const item of filteredItems.value) {
        const cat = item.category || 'Other'
        if (!byCat.has(cat)) byCat.set(cat, [])
        byCat.get(cat).push(item)
      }
      return Array.from(byCat.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([category, items]) => ({
          category,
          items: items.sort((a, b) => a.name.localeCompare(b.name)),
        }))
    })

    // Count per tab (ignoring search to keep tabs stable)
    const tabCounts = computed(() => {
      const counts = { all: store.items.value.length }
      for (const loc of PANTRY_LOCATIONS) {
        counts[loc.value] = store.items.value.filter((i) => i.location === loc.value).length
      }
      return counts
    })

    // ── Add form ───────────────────────────────────
    const showAddForm = ref(false)
    const addNameRef = ref(null)
    const addName = ref('')
    const addQuantity = ref('')
    const addUnit = ref('')
    const addLocation = ref('pantry')
    const addCategory = ref('')

    function resetAddForm() {
      showAddForm.value = false
      addName.value = ''
      addQuantity.value = ''
      addUnit.value = ''
      addLocation.value = 'pantry'
      addCategory.value = ''
    }

    async function onAddItem() {
      if (!addName.value.trim()) return
      store.addItem({
        name: addName.value,
        quantity: addQuantity.value.trim(),
        unit: addUnit.value.trim(),
        location: addLocation.value,
        category: addCategory.value || 'Other',
      })
      addName.value = ''
      addQuantity.value = ''
      addUnit.value = ''
      // keep location/category for batch adding
      await nextTick()
      addNameRef.value?.focus()
    }

    // ── Edit ───────────────────────────────────────
    const editingId = ref(null)
    const editName = ref('')
    const editQuantity = ref('')
    const editUnit = ref('')
    const editLocation = ref('pantry')
    const editCategory = ref('Other')

    function onStartEdit(item) {
      editingId.value = item.id
      editName.value = item.name
      editQuantity.value = item.quantity ?? ''
      editUnit.value = item.unit ?? ''
      editLocation.value = item.location
      editCategory.value = item.category || 'Other'
    }

    function onSaveEdit(id) {
      if (!editName.value.trim()) return
      store.updateItem(id, {
        name: editName.value.trim(),
        quantity: editQuantity.value.trim(),
        unit: editUnit.value.trim(),
        location: editLocation.value,
        category: editCategory.value,
      })
      editingId.value = null
    }

    function cancelEdit() {
      editingId.value = null
    }

    // ── Quick qty adjust ───────────────────────────
    function adjustQty(item, delta) {
      const current = parseFloat(item.quantity) || 0
      const next = Math.max(0, current + delta)
      store.updateItem(item.id, { quantity: next === 0 ? '' : String(next) })
    }

    // ── Helpers ────────────────────────────────────
    function locationLabel(val) {
      return PANTRY_LOCATIONS.find((l) => l.value === val)?.label ?? val
    }

    // ── Barcode scan ───────────────────────────────
    const showBarcodePanel = ref(false)
    const barcodeSupported = typeof window !== 'undefined' && 'BarcodeDetector' in window
    const barcodeVideoRef = ref(null)
    const barcodeCameraActive = ref(false)
    const barcodeLookingUp = ref(false)
    const barcodeError = ref('')
    const barcodeProduct = ref(null)
    const manualUpc = ref('')
    let _barcodeStream = null
    let _barcodeRafId = null
    let _barcodeDetector = null

    function onToggleBarcode() {
      showBarcodePanel.value = !showBarcodePanel.value
      if (!showBarcodePanel.value) resetBarcode()
    }

    function resetBarcode() {
      stopBarcodeCamera()
      barcodeProduct.value = null
      barcodeError.value = ''
      barcodeLookingUp.value = false
      manualUpc.value = ''
    }

    async function startBarcodeCamera() {
      barcodeError.value = ''
      try {
        _barcodeDetector = new window.BarcodeDetector({ formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e'] })
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
          audio: false,
        })
        _barcodeStream = stream
        barcodeCameraActive.value = true
        await nextTick()
        if (barcodeVideoRef.value) {
          barcodeVideoRef.value.srcObject = stream
          barcodeVideoRef.value.play()
        }
        _scanLoop()
      } catch (err) {
        barcodeError.value = err.name === 'NotAllowedError'
          ? 'Camera access denied. Please allow camera access.'
          : 'Could not start camera.'
      }
    }

    function _scanLoop() {
      if (!barcodeCameraActive.value || !barcodeVideoRef.value) return
      _barcodeRafId = requestAnimationFrame(async () => {
        try {
          const barcodes = await _barcodeDetector.detect(barcodeVideoRef.value)
          if (barcodes.length) {
            const upc = barcodes[0].rawValue
            stopBarcodeCamera()
            await doBarcodeLookup(upc)
            return
          }
        } catch (_) {}
        _scanLoop()
      })
    }

    function stopBarcodeCamera() {
      if (_barcodeRafId) { cancelAnimationFrame(_barcodeRafId); _barcodeRafId = null }
      if (_barcodeStream) { _barcodeStream.getTracks().forEach((t) => t.stop()); _barcodeStream = null }
      if (barcodeVideoRef.value) barcodeVideoRef.value.srcObject = null
      barcodeCameraActive.value = false
    }

    async function onManualUpcLookup() {
      const upc = manualUpc.value.trim()
      if (!upc) return
      await doBarcodeLookup(upc)
    }

    async function doBarcodeLookup(upc) {
      barcodeError.value = ''
      barcodeLookingUp.value = true
      try {
        const product = await lookupBarcode(upc)
        barcodeProduct.value = {
          name: product.name,
          brand: product.brand || '',
          quantity: product.quantity != null ? String(product.quantity) : '',
          unit: product.unit || '',
          category: product.category || 'Other',
          location: 'pantry',
          _notFound: false,
        }
      } catch (err) {
        const isNotFound = err.message?.includes('not found') || err.message?.includes('404')
        if (isNotFound) {
          // Open blank form so user can fill in the name manually
          barcodeProduct.value = {
            name: '',
            brand: '',
            quantity: '',
            unit: '',
            category: 'Other',
            location: 'pantry',
            _notFound: true,
          }
        } else {
          barcodeError.value = err.message || 'Lookup failed. Try scanning again.'
          if (barcodeSupported) barcodeCameraActive.value = false
        }
      } finally {
        barcodeLookingUp.value = false
      }
    }

    function onConfirmBarcode() {
      const p = barcodeProduct.value
      if (!p?.name?.trim()) return
      store.addItem({
        name: p.name.trim(),
        quantity: p.quantity,
        unit: p.unit,
        location: p.location,
        category: p.category,
      })
      resetBarcode()
      showBarcodePanel.value = false
    }

    function onScanAnother() {
      barcodeProduct.value = null
      barcodeError.value = ''
      manualUpc.value = ''
    }

    // ── Receipt scan ───────────────────────────────
    const showScanPanel = ref(false)
    const scanFileInputRef = ref(null)
    const scanLoading = ref(false)
    const scanError = ref('')
    const scanItems = ref([])
    const scanLocation = ref('pantry')
    const scanDragOver = ref(false)
    let _scanSid = 0

    const scanSelectedCount = computed(() => scanItems.value.filter((i) => i.selected).length)

    function onToggleScan() {
      showScanPanel.value = !showScanPanel.value
      if (!showScanPanel.value) resetScan()
    }

    function resetScan() {
      scanItems.value = []
      scanError.value = ''
      scanLoading.value = false
      scanDragOver.value = false
    }

    function triggerScanUpload() {
      scanFileInputRef.value?.click()
    }

    function onScanFileChange(event) {
      const file = event.target.files?.[0]
      if (file) doScan(file)
      event.target.value = ''
    }

    function onScanDrop(event) {
      scanDragOver.value = false
      const file = event.dataTransfer.files?.[0]
      if (file) doScan(file)
    }

    async function doScan(file) {
      scanError.value = ''
      scanLoading.value = true
      scanItems.value = []
      try {
        const result = await scanReceipt(file)
        if (!result.items?.length) {
          scanError.value = 'No food items found. Try a clearer photo.'
          scanLoading.value = false
          return
        }
        scanItems.value = result.items.map((item) => ({
          _sid: ++_scanSid,
          selected: true,
          name: item.name,
          quantity: item.quantity != null ? String(item.quantity) : '',
          unit: item.unit ?? '',
          category: item.category || 'Other',
        }))
      } catch (err) {
        scanError.value = 'Failed to scan receipt. Please try again.'
      } finally {
        scanLoading.value = false
      }
    }

    function onConfirmScan() {
      scanItems.value
        .filter((i) => i.selected && i.name.trim())
        .forEach((i) => {
          store.addItem({
            name: i.name.trim(),
            quantity: i.quantity.trim(),
            unit: i.unit.trim(),
            location: scanLocation.value,
            category: i.category || 'Other',
          })
        })
      showScanPanel.value = false
      resetScan()
    }

    return {
      store,
      tabs,
      activeTab,
      currentTabLabel,
      searchQuery,
      visibleGroups,
      tabCounts,
      showAddForm,
      addNameRef,
      addName,
      addQuantity,
      addUnit,
      addLocation,
      addCategory,
      resetAddForm,
      onAddItem,
      editingId,
      editName,
      editQuantity,
      editUnit,
      editLocation,
      editCategory,
      onStartEdit,
      onSaveEdit,
      cancelEdit,
      adjustQty,
      locationLabel,
      PANTRY_LOCATIONS,
      PANTRY_CATEGORIES,
      // barcode
      showBarcodePanel,
      barcodeSupported,
      barcodeVideoRef,
      barcodeCameraActive,
      barcodeLookingUp,
      barcodeError,
      barcodeProduct,
      manualUpc,
      onToggleBarcode,
      startBarcodeCamera,
      stopBarcodeCamera,
      onManualUpcLookup,
      onConfirmBarcode,
      onScanAnother,
      // scan
      showScanPanel,
      scanFileInputRef,
      scanLoading,
      scanError,
      scanItems,
      scanLocation,
      scanDragOver,
      scanSelectedCount,
      onToggleScan,
      resetScan,
      triggerScanUpload,
      onScanFileChange,
      onScanDrop,
      onConfirmScan,
    }
  },
}
</script>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

/* ── Header ──────────────────────────────────── */
.header {
  margin-bottom: 1.25rem;
}

.header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
  color: var(--prep-text);
  font-family: var(--prep-font-display);
}

.subtitle {
  color: var(--prep-muted);
  font-size: 0.9rem;
}

.btn-add-item {
  padding: 0.55rem 1.1rem;
  border-radius: 8px;
  border: 1px solid var(--prep-primary);
  background: transparent;
  color: var(--prep-primary);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}

.btn-add-item:hover {
  background: rgba(0, 200, 180, 0.1);
}

/* ── Add form ────────────────────────────────── */
.add-form {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.add-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.field--name { flex: 1; min-width: 180px; }
.field--qty  { width: 70px; }
.field--unit { width: 90px; }
.field--location { width: 110px; }
.field--category { width: 140px; }

.field-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--prep-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field-input {
  padding: 0.5rem 0.65rem;
  border-radius: 7px;
  border: 1px solid var(--prep-border);
  font-size: 0.9rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.field-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.15);
}

.add-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-save {
  padding: 0.5rem 1.1rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 7px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-save:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-save:hover:not(:disabled) { background: var(--prep-primary-hover); }

.btn-cancel {
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--prep-muted);
  border: 1px solid var(--prep-border);
  border-radius: 7px;
  font-size: 0.9rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-cancel:hover { color: var(--prep-text); border-color: var(--prep-text); }

/* ── Controls (search + tabs) ────────────────── */
.controls {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.7rem;
  font-size: 0.85rem;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.6rem 2.2rem 0.6rem 2.2rem;
  border-radius: 9px;
  border: 1px solid var(--prep-border);
  font-size: 0.92rem;
  background: var(--prep-card);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.search-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.12);
}

.search-clear {
  position: absolute;
  right: 0.6rem;
  background: transparent;
  border: none;
  font-size: 1.1rem;
  color: var(--prep-muted);
  cursor: pointer;
  padding: 0 0.25rem;
  line-height: 1;
}

.search-clear:hover { color: var(--prep-text); }

.tabs {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.85rem;
  border-radius: 20px;
  border: 1px solid var(--prep-border);
  background: transparent;
  color: var(--prep-muted);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.15s;
}

.tab:hover { color: var(--prep-text); border-color: var(--prep-text); }

.tab.active {
  background: var(--prep-primary);
  border-color: var(--prep-primary);
  color: var(--prep-bg);
  font-weight: 600;
}

.tab-count {
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(0,0,0,0.15);
  border-radius: 999px;
  padding: 0 0.4rem;
}

.tab.active .tab-count {
  background: rgba(0,0,0,0.2);
}

/* ── Groups / items ──────────────────────────── */
.groups {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.category-group {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  overflow: hidden;
}

.category-heading {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--prep-primary);
  font-family: var(--prep-font-display);
  padding: 0.6rem 1rem 0.4rem;
  border-bottom: 1px solid var(--prep-border);
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--prep-border);
  transition: background 0.12s;
}

.item-row:last-child { border-bottom: none; }
.item-row:hover { background: rgba(0, 200, 180, 0.04); }

/* ── Item info ───────────────────────────────── */
.item-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--prep-text);
}

.item-qty {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--prep-primary);
}

.item-location-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--prep-muted);
  background: rgba(139, 148, 158, 0.12);
  border-radius: 4px;
  padding: 0.1rem 0.45rem;
  margin-left: auto;
  white-space: nowrap;
}

/* ── Item actions ────────────────────────────── */
.item-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}

.item-row:hover .item-actions,
.item-row:focus-within .item-actions {
  opacity: 1;
}

.qty-controls {
  display: flex;
  align-items: center;
  gap: 0.1rem;
  border: 1px solid var(--prep-border);
  border-radius: 6px;
  overflow: hidden;
}

.qty-btn {
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  color: var(--prep-muted);
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--prep-font-body);
  transition: background 0.12s, color 0.12s;
}

.qty-btn:hover {
  background: rgba(0, 200, 180, 0.12);
  color: var(--prep-primary);
}

.qty-display {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--prep-text);
  min-width: 22px;
  text-align: center;
  padding: 0 0.1rem;
}

.btn-icon {
  padding: 0.2rem 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-family: var(--prep-font-body);
  font-size: 0.78rem;
  font-weight: 600;
  background: transparent;
  transition: background 0.12s, color 0.12s;
}

.btn-edit-icon { color: var(--prep-muted); }
.btn-edit-icon:hover { color: var(--prep-primary); background: rgba(0,200,180,0.1); }

.btn-remove {
  color: var(--prep-muted);
  font-size: 1.05rem;
  padding: 0.1rem 0.4rem;
}

.btn-remove:hover { color: var(--prep-error); background: rgba(248,81,73,0.1); }

/* ── Edit form ───────────────────────────────── */
.edit-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
  flex: 1;
}

.edit-input {
  padding: 0.35rem 0.55rem;
  border-radius: 6px;
  border: 1px solid var(--prep-border);
  font-size: 0.85rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.edit-input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.15);
}

.edit-input--name { flex: 1; min-width: 100px; }
.edit-input--qty  { width: 55px; }
.edit-input--unit { width: 70px; }
.edit-input--loc  { width: 95px; }
.edit-input--cat  { width: 120px; }

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

.btn-edit-save:hover { background: var(--prep-primary-hover); }

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

.btn-edit-cancel:hover { color: var(--prep-text); border-color: var(--prep-text); }

/* ── Empty state ─────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 3.5rem 1.5rem;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
}

.empty-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--prep-text);
  margin-bottom: 0.4rem;
}

.empty-hint {
  color: var(--prep-muted);
  font-size: 0.88rem;
  line-height: 1.6;
}

.empty-link {
  color: var(--prep-primary);
  text-decoration: none;
  font-weight: 600;
}

.empty-link:hover { text-decoration: underline; }

/* ── Transitions ─────────────────────────────── */
.expand-enter-active, .expand-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.item-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.item-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.item-enter-from { opacity: 0; transform: translateX(-10px); }
.item-leave-to   { opacity: 0; transform: translateX(10px); }
.item-move       { transition: transform 0.2s ease; }

/* ── Header actions ──────────────────────────── */
.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-shrink: 0;
}

.btn-scan-receipt {
  padding: 0.55rem 1.1rem;
  border-radius: 8px;
  border: 1px solid var(--prep-border);
  background: transparent;
  color: var(--prep-muted);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  white-space: nowrap;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.btn-scan-receipt:hover {
  color: var(--prep-text);
  border-color: var(--prep-text);
}

/* ── Barcode panel ───────────────────────────── */
.barcode-camera-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.barcode-video {
  width: 100%;
  max-height: 280px;
  border-radius: 10px;
  object-fit: cover;
  background: #000;
}

.barcode-reticle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
  width: 220px;
  height: 100px;
  border: 2px solid var(--prep-primary);
  border-radius: 8px;
  pointer-events: none;
  box-shadow: 0 0 0 9999px rgba(0,0,0,0.35);
}

.barcode-reticle-inner {
  position: absolute;
  inset: 0;
  border-radius: 6px;
  animation: barcode-pulse 1.5s ease-in-out infinite;
}

@keyframes barcode-pulse {
  0%, 100% { border-top: 2px solid var(--prep-primary); top: 10%; }
  50% { border-top: 2px solid var(--prep-primary); top: 80%; }
}

.barcode-hint {
  font-size: 0.82rem;
  color: var(--prep-muted);
  text-align: center;
}

.barcode-cancel-btn {
  align-self: center;
}

.barcode-unsupported-note {
  font-size: 0.85rem;
  color: var(--prep-muted);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.barcode-manual-row {
  display: flex;
  gap: 0.5rem;
}

.barcode-manual-input {
  flex: 1;
}

.barcode-found-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--prep-primary);
  margin-bottom: 0.75rem;
}

.barcode-not-found {
  color: var(--prep-muted);
}

.barcode-confirm-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.field--brand { flex: 1; min-width: 140px; }

/* ── Scan panel ──────────────────────────────── */
.scan-panel {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.scan-drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  border: 2px dashed var(--prep-border);
  border-radius: 10px;
  padding: 2.5rem 1rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
}

.scan-drop-zone:hover,
.scan-drop-zone--over {
  border-color: var(--prep-primary);
  background: rgba(0, 200, 180, 0.04);
}

.scan-drop-icon {
  font-size: 2.2rem;
  margin-bottom: 0.25rem;
}

.scan-drop-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--prep-text);
}

.scan-drop-hint {
  font-size: 0.82rem;
  color: var(--prep-muted);
}

.scan-file-input {
  display: none;
}

.scan-error {
  color: var(--prep-error);
  font-size: 0.85rem;
  margin-top: 0.75rem;
  text-align: center;
}

/* Loading */
.scan-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1rem;
}

.scan-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--prep-border);
  border-top-color: var(--prep-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.scan-loading-text {
  color: var(--prep-muted);
  font-size: 0.9rem;
}

/* Review */
.scan-review-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.scan-review-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--prep-text);
}

.scan-review-hint {
  font-size: 0.82rem;
  color: var(--prep-muted);
  margin-top: 0.1rem;
}

.btn-scan-again {
  padding: 0.3rem 0.75rem;
  border: 1px solid var(--prep-border);
  background: transparent;
  color: var(--prep-muted);
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-scan-again:hover { color: var(--prep-text); border-color: var(--prep-text); }

.scan-item-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-height: 320px;
  overflow-y: auto;
}

.scan-item-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.25rem;
  border-radius: 7px;
  transition: opacity 0.15s;
}

.scan-item-row--unchecked {
  opacity: 0.4;
}

.scan-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--prep-primary);
  flex-shrink: 0;
  cursor: pointer;
}

.scan-item-fields {
  display: flex;
  gap: 0.4rem;
  flex: 1;
  flex-wrap: wrap;
}

.scan-field {
  padding: 0.32rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--prep-border);
  font-size: 0.84rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.scan-field:focus {
  outline: none;
  border-color: var(--prep-primary);
}

.scan-field--name { flex: 1; min-width: 120px; }
.scan-field--qty  { width: 58px; }
.scan-field--unit { width: 72px; }
.scan-field--cat  { width: 130px; }

.scan-confirm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding-top: 0.75rem;
  border-top: 1px solid var(--prep-border);
}

.scan-location-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scan-location-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--prep-muted);
}

.scan-location-select {
  padding: 0.38rem 0.65rem;
  border-radius: 7px;
  border: 1px solid var(--prep-border);
  font-size: 0.88rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.btn-scan-confirm {
  padding: 0.5rem 1.1rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 7px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: background 0.15s;
}

.btn-scan-confirm:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-scan-confirm:hover:not(:disabled) { background: var(--prep-primary-hover); }

/* ── Responsive ──────────────────────────────── */
@media (max-width: 480px) {
  .item-actions { opacity: 1; }
  .add-fields { flex-direction: column; }
  .field--qty, .field--unit, .field--location, .field--category { width: 100%; }
  .header-actions { flex-direction: column; align-items: stretch; }
  .scan-item-fields { flex-direction: column; }
  .scan-field--qty, .scan-field--unit, .scan-field--cat { width: 100%; }
  .scan-confirm-row { flex-direction: column; align-items: stretch; }
  .btn-scan-confirm { text-align: center; }
}
</style>
