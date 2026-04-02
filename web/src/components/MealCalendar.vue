<template>
  <div class="meal-calendar">
    <!-- Week navigation -->
    <div class="cal-nav">
      <button
        class="week-btn"
        :disabled="weekOffset === 0"
        @click="weekOffset = 0"
      >
        &lt; Week 1
      </button>
      <span class="week-label">
        {{ weekOffset === 0 ? 'Week 1' : 'Week 2' }}
        <span class="week-range">{{ weekRangeLabel }}</span>
      </span>
      <button
        v-if="totalDays > 7"
        class="week-btn"
        :disabled="weekOffset === 1"
        @click="weekOffset = 1"
      >
        Week 2 &gt;
      </button>
    </div>

    <!-- Calendar grid -->
    <div class="cal-grid" :style="gridStyle">
      <!-- Header row: empty corner + day columns -->
      <div class="cal-header-corner"></div>
      <div
        v-for="day in visibleDays"
        :key="day.date"
        class="cal-day-header"
      >
        <span class="day-name">{{ day.shortName }}</span>
        <span class="day-date">{{ day.displayDate }}</span>
      </div>

      <!-- One row per meal type -->
      <template v-for="mealType in mealTypes" :key="mealType">
        <div class="cal-meal-label">{{ formatMealType(mealType) }}</div>

        <div
          v-for="day in visibleDays"
          :key="day.date + '-' + mealType"
          :class="['cal-cell', {
            'cal-cell--loading': generatingDate === day.date,
            'cal-cell--filled': getEntry(day.date, mealType) !== null,
            'cal-cell--empty': !getEntry(day.date, mealType) && generatingDate !== day.date,
          }]"
          @click="handleCellClick(day.date, mealType)"
        >
          <!-- Loading shimmer -->
          <div v-if="generatingDate === day.date" class="shimmer">
            <div class="shimmer-line shimmer-line--long"></div>
            <div class="shimmer-line shimmer-line--short"></div>
          </div>

          <!-- Recipe entry -->
          <template v-else-if="getEntry(day.date, mealType)">
            <span
              v-if="mealType === 'leftover'"
              class="cell-leftover-badge"
            >♻ leftover</span>
            <span class="cell-title">{{ getEntry(day.date, mealType).recipe.title }}</span>
            <span class="cell-meta">{{ getEntry(day.date, mealType).recipe.total_time_minutes }}min</span>
          </template>

          <!-- Empty -->
          <span v-else class="cell-empty">—</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'MealCalendar',
  props: {
    entries: {
      type: Array,
      default: () => [],
    },
    startDate: {
      type: String,
      required: true,
    },
    endDate: {
      type: String,
      required: true,
    },
    mealTypes: {
      type: Array,
      default: () => ['breakfast', 'lunch', 'dinner'],
    },
    generatingDate: {
      type: String,
      default: null,
    },
  },
  emits: ['meal-click'],
  setup(props, { emit }) {
    const weekOffset = ref(0)

    const totalDays = computed(() => {
      const s = new Date(props.startDate + 'T12:00:00')
      const e = new Date(props.endDate + 'T12:00:00')
      return Math.round((e - s) / (1000 * 60 * 60 * 24)) + 1
    })

    const allDays = computed(() => {
      const days = []
      const start = new Date(props.startDate + 'T12:00:00')
      const SHORT_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
      for (let i = 0; i < totalDays.value; i++) {
        const d = new Date(start)
        d.setDate(d.getDate() + i)
        const isoDate = d.toISOString().split('T')[0]
        days.push({
          date: isoDate,
          shortName: SHORT_DAYS[d.getDay()],
          displayDate: `${d.getMonth() + 1}/${d.getDate()}`,
        })
      }
      return days
    })

    const visibleDays = computed(() => {
      const start = weekOffset.value * 7
      return allDays.value.slice(start, start + 7)
    })

    const weekRangeLabel = computed(() => {
      if (visibleDays.value.length === 0) return ''
      const first = visibleDays.value[0]
      const last = visibleDays.value[visibleDays.value.length - 1]
      return `${first.displayDate} – ${last.displayDate}`
    })

    const gridStyle = computed(() => ({
      gridTemplateColumns: `90px repeat(${visibleDays.value.length}, 1fr)`,
    }))

    // Build a lookup map for fast access
    const entryMap = computed(() => {
      const map = {}
      for (const e of props.entries) {
        const key = `${e.date}__${e.meal_type}`
        map[key] = e
      }
      return map
    })

    function getEntry(date, mealType) {
      return entryMap.value[`${date}__${mealType}`] || null
    }

    function formatMealType(mt) {
      return mt.charAt(0).toUpperCase() + mt.slice(1)
    }

    function handleCellClick(date, mealType) {
      const entry = getEntry(date, mealType)
      if (entry) {
        emit('meal-click', { date, meal_type: mealType, recipe: entry.recipe })
      }
    }

    return {
      weekOffset,
      totalDays,
      visibleDays,
      weekRangeLabel,
      gridStyle,
      getEntry,
      formatMealType,
      handleCellClick,
    }
  },
}
</script>

<style scoped>
.meal-calendar {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  overflow: hidden;
}

/* Navigation */
.cal-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--prep-border);
  background: rgba(0, 0, 0, 0.15);
}

.week-btn {
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--prep-border);
  border-radius: 6px;
  background: transparent;
  color: var(--prep-text);
  font-size: 0.82rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.2s;
}

.week-btn:hover:not(:disabled) {
  border-color: var(--prep-primary);
  color: var(--prep-primary);
}

.week-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.week-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--prep-text);
  margin-left: auto;
}

.week-range {
  font-size: 0.78rem;
  color: var(--prep-muted);
  font-weight: 400;
  margin-left: 0.5rem;
}

/* Grid */
.cal-grid {
  display: grid;
  overflow-x: auto;
}

.cal-header-corner {
  padding: 0.5rem;
  border-bottom: 1px solid var(--prep-border);
  border-right: 1px solid var(--prep-border);
  background: rgba(0, 0, 0, 0.1);
}

.cal-day-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0.25rem;
  border-bottom: 1px solid var(--prep-border);
  border-right: 1px solid var(--prep-border);
  background: rgba(0, 0, 0, 0.1);
  min-width: 80px;
}

.cal-day-header:last-child {
  border-right: none;
}

.day-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--prep-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.day-date {
  font-size: 0.82rem;
  color: var(--prep-text);
  margin-top: 0.15rem;
}

.cal-meal-label {
  display: flex;
  align-items: center;
  padding: 0 0.75rem;
  border-bottom: 1px solid var(--prep-border);
  border-right: 1px solid var(--prep-border);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--prep-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  min-height: 56px;
}

/* Cells */
.cal-cell {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--prep-border);
  border-right: 1px solid var(--prep-border);
  min-height: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.2rem;
  min-width: 80px;
}

.cal-cell:last-child {
  border-right: none;
}

.cal-cell--filled {
  cursor: pointer;
  transition: background 0.15s;
}

.cal-cell--filled:hover {
  background: rgba(0, 200, 180, 0.08);
}

.cell-title {
  font-size: 0.78rem;
  color: var(--prep-text);
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
}

.cell-meta {
  font-size: 0.68rem;
  color: var(--prep-muted);
}

.cell-empty {
  color: var(--prep-border);
  font-size: 0.9rem;
  text-align: center;
  width: 100%;
}

.cell-leftover-badge {
  font-size: 0.65rem;
  color: var(--prep-primary);
  opacity: 0.8;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

/* Loading shimmer */
.cal-cell--loading {
  background: rgba(0, 200, 180, 0.04);
}

.shimmer {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  width: 100%;
}

.shimmer-line {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(
    90deg,
    var(--prep-border) 25%,
    rgba(0, 200, 180, 0.15) 50%,
    var(--prep-border) 75%
  );
  background-size: 200% 100%;
  animation: shimmer-sweep 1.4s infinite;
}

.shimmer-line--long {
  width: 85%;
}

.shimmer-line--short {
  width: 50%;
}

@keyframes shimmer-sweep {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
