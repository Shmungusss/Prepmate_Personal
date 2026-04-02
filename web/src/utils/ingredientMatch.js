// ── Unit aliases ─────────────────────────────────────────────────────────────
const ALIASES = {
  teaspoon: 'tsp', teaspoons: 'tsp',
  tablespoon: 'tbsp', tablespoons: 'tbsp',
  'fluid ounce': 'fl oz', 'fluid ounces': 'fl oz', floz: 'fl oz',
  cup: 'cup', cups: 'cup',
  pint: 'pint', pints: 'pint',
  quart: 'quart', quarts: 'quart',
  gallon: 'gallon', gallons: 'gallon',
  milliliter: 'ml', milliliters: 'ml', millilitre: 'ml', millilitres: 'ml',
  liter: 'l', liters: 'l', litre: 'l', litres: 'l',
  ounce: 'oz', ounces: 'oz',
  pound: 'lbs', pounds: 'lbs', lb: 'lbs',
  gram: 'g', grams: 'g',
  kilogram: 'kg', kilograms: 'kg',
}

export const TO_ML = { tsp: 4.929, tbsp: 14.787, 'fl oz': 29.574, cup: 236.588, pint: 473.176, quart: 946.353, gallon: 3785.41, ml: 1, l: 1000 }
export const TO_G  = { oz: 28.3495, lbs: 453.592, g: 1, kg: 1000 }

export function normalizeUnit(unit) {
  const u = (unit || '').toLowerCase().trim()
  return ALIASES[u] || u
}

export function toBase(qty, unit, forceVolume = false) {
  const u = normalizeUnit(unit)
  if (u === 'oz' && forceVolume) return { value: qty * TO_ML['fl oz'], type: 'volume', canonical: u }
  if (TO_ML[u] !== undefined) return { value: qty * TO_ML[u], type: 'volume', canonical: u }
  if (TO_G[u]  !== undefined) return { value: qty * TO_G[u],  type: 'weight', canonical: u }
  return null
}

export function fromBase(baseVal, unit, type, forceVolume = false) {
  const u = normalizeUnit(unit)
  if (u === 'oz' && forceVolume) return baseVal / TO_ML['fl oz']
  if (type === 'volume' && TO_ML[u]) return baseVal / TO_ML[u]
  if (type === 'weight' && TO_G[u])  return baseVal / TO_G[u]
  return null
}

// Convert ingQty/ingUnit into pantryUnit. Returns the converted value or null if incompatible.
export function tryConvert(pantryQty, pantryUnit, ingQty, ingUnit) {
  const normP = normalizeUnit(pantryUnit)
  const normI = normalizeUnit(ingUnit)
  const pb = toBase(pantryQty, pantryUnit)
  const ib = toBase(ingQty, ingUnit)
  if (pb && ib && pb.type === ib.type) {
    const result = fromBase(ib.value, normP, pb.type)
    if (result !== null) return result
  }
  // Fallback: retry treating oz as fl oz
  if (normP === 'oz' || normI === 'oz') {
    const pb2 = toBase(pantryQty, pantryUnit, normP === 'oz')
    const ib2 = toBase(ingQty, ingUnit,       normI === 'oz')
    if (pb2 && ib2 && pb2.type === ib2.type) {
      const result = fromBase(ib2.value, normP, pb2.type, normP === 'oz')
      if (result !== null) return result
    }
  }
  return null
}

// ── Name matching ─────────────────────────────────────────────────────────────
// Descriptor-only words that can prefix an ingredient without changing what it
// fundamentally is. Food nouns (peanut, sour, almond, coconut…) are excluded so
// "peanut butter" does NOT match the ingredient "butter".
export const QUALIFIERS = new Set([
  'unsalted', 'salted', 'organic', 'fresh', 'frozen', 'whole', 'skim',
  'low-fat', 'lowfat', 'extra', 'virgin', 'large', 'small', 'medium',
  'chopped', 'diced', 'minced', 'sliced', 'shredded', 'grated', 'ground',
  'crushed', 'dried', 'raw', 'cooked', 'roasted', 'reduced', 'fat-free',
  'sugar-free', 'light', 'lite', 'plain', 'regular', 'pure', 'natural',
  'unbleached', 'bleached', 'enriched', 'refined', 'unrefined',
])

// Returns true if pantryName refers to the same ingredient as ingredientName.
// "unsalted butter" matches "butter"; "peanut butter" does not.
export function fuzzyMatch(pantryName, ingredientName) {
  const p = pantryName.toLowerCase().trim()
  const i = ingredientName.toLowerCase().trim()
  if (p === i) return true

  const pWords = p.split(/\s+/)
  const iWords = i.split(/\s+/)

  if (pWords.length > iWords.length) {
    const suffix = pWords.slice(pWords.length - iWords.length)
    const prefix = pWords.slice(0, pWords.length - iWords.length)
    if (suffix.join(' ') === iWords.join(' ') && prefix.every(w => QUALIFIERS.has(w))) {
      return true
    }
  }

  return false
}

// Find the pantry item that matches an ingredient name, or null.
export function findPantryMatch(pantryItems, ingredientName) {
  return pantryItems.find(p => fuzzyMatch(p.name, ingredientName)) || null
}

// ── Quantity helpers ──────────────────────────────────────────────────────────

export function formatQty(n) {
  if (n == null || isNaN(n)) return ''
  return n % 1 === 0 ? String(n) : n.toFixed(2).replace(/\.?0+$/, '')
}
