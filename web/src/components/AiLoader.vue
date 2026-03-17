<template>
  <Transition name="loader-fade">
    <div v-if="active" class="loader-inline">

      <!-- Top row: spinning icon + title + status -->
      <div class="loader-header">
        <div class="loader-icon-wrap">
          <div class="loader-ring"></div>
          <div class="loader-ring loader-ring--2"></div>
          <span class="loader-emoji">{{ config.icon }}</span>
        </div>

        <div class="loader-header-text">
          <p class="loader-title">{{ config.title }}</p>
          <Transition name="msg-swap" mode="out-in">
            <p class="loader-status" :key="currentStepIndex">
              <span class="loader-dot"></span>
              {{ currentStep }}
            </p>
          </Transition>
        </div>

        <span class="loader-percent">{{ Math.round(progress) }}%</span>
      </div>

      <!-- Progress bar -->
      <div class="loader-bar-track">
        <div class="loader-bar-fill" :style="{ width: progress + '%' }"></div>
        <div class="loader-bar-shimmer"></div>
      </div>

      <!-- Rotating tip -->
      <Transition name="tip-swap" mode="out-in">
        <p class="loader-tip" :key="currentTipIndex">
          💡 {{ currentTip }}
        </p>
      </Transition>

    </div>
  </Transition>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// ── Configurable content per generation type ──────────────────────────
const CONFIGS = {
  recipe: {
    icon: '🍳',
    title: 'Crafting Your Recipe…',
    steps: [
      'Analysing your ingredients…',
      'Checking flavour combinations…',
      'Building the instructions…',
      'Calculating nutrition info…',
      'Adding chefs tips…',
      'Almost on the plate…',
    ],
    tips: [
      'Mise en place — prep everything before you cook.',
      'Salt your pasta water like the sea.',
      'Let meat rest before slicing.',
      'Acid (lemon/vinegar) brightens any dish.',
      'High heat for searing, low heat for sauces.',
    ],
  },
  groceryList: {
    icon: '🛒',
    title: 'Building Your Grocery List…',
    steps: [
      'Reading your preferences…',
      'Planning meals for the week…',
      'Organising by store section…',
      'Estimating prices…',
      'Checking dietary restrictions…',
      'Finalising your list…',
    ],
    tips: [
      'Shop the perimeter first — thats where the fresh food lives.',
      'Buying in bulk saves money on pantry staples.',
      'Frozen veg is just as nutritious as fresh.',
      'Meal-prepping grains on Sunday saves time all week.',
      'Check your pantry before you shop!',
    ],
  },
}

// How long (ms) to run the fake progress. API takes about 20 seconds
const DURATION_MS = 18000

export default {
  name: 'AiLoader',

  props: {
    /** Show / hide the loader */
    active: {
      type: Boolean,
      default: false,
    },
    /**
     * Which generation type — drives the messages & icon.
     * 'recipe' | 'groceryList'
     */
    type: {
      type: String,
      default: 'recipe',
      validator: (v) => Object.keys(CONFIGS).includes(v),
    },
  },

  setup(props) {
    const config = computed(() => CONFIGS[props.type] ?? CONFIGS.recipe)

    // ── Progress bar ──────────────────────────────────────────────────
    const progress = ref(0)
    let progressInterval = null

    function startProgress() {
      progress.value = 0
      const tickMs = 100
      const maxProgress = 94          // never hit 100 until API returns
      const increment = (maxProgress / (DURATION_MS / tickMs))

      progressInterval = setInterval(() => {
        if (progress.value < maxProgress) {
          // Ease-out: slow down as we approach the cap
          const remaining = maxProgress - progress.value
          progress.value += Math.min(increment * (remaining / maxProgress) * 2.2, remaining)
        }
      }, tickMs)
    }

    function finishProgress() {
      clearInterval(progressInterval)
      progress.value = 100
    }

    function resetProgress() {
      clearInterval(progressInterval)
      progress.value = 0
    }

    // ── Step messages ─────────────────────────────────────────────────
    const currentStepIndex = ref(0)
    let stepInterval = null

    function startSteps() {
      currentStepIndex.value = 0
      const stepMs = DURATION_MS / config.value.steps.length
      stepInterval = setInterval(() => {
        const max = config.value.steps.length - 1
        if (currentStepIndex.value < max) {
          currentStepIndex.value++
        }
      }, stepMs)
    }

    function stopSteps() {
      clearInterval(stepInterval)
    }

    const currentStep = computed(
      () => config.value.steps[currentStepIndex.value] ?? ''
    )

    // ── Tip carousel ──────────────────────────────────────────────────
    const currentTipIndex = ref(0)
    let tipInterval = null

    function startTips() {
      currentTipIndex.value = 0
      tipInterval = setInterval(() => {
        currentTipIndex.value =
          (currentTipIndex.value + 1) % config.value.tips.length
      }, 4500)
    }

    function stopTips() {
      clearInterval(tipInterval)
    }

    const currentTip = computed(
      () => config.value.tips[currentTipIndex.value] ?? ''
    )

    // ── Start immediately on mount (component only exists when active=true) ──
    onMounted(() => {
      startProgress()
      startSteps()
      startTips()
    })

    // ── Watch only for when active becomes false (API returned) ──────────
    watch(
      () => props.active,
      (val) => {
        if (!val) {
          finishProgress()
          stopSteps()
          stopTips()
          setTimeout(resetProgress, 400)
        }
      }
    )

    onUnmounted(() => {
      clearInterval(progressInterval)
      clearInterval(stepInterval)
      clearInterval(tipInterval)
    })

    return {
      config,
      progress,
      currentStep,
      currentStepIndex,
      currentTip,
      currentTipIndex,
    }
  },
}
</script>

<style scoped>
/* ── Inline container (replaces the button) ── */
.loader-inline {
  font-family: var(--prep-font-body);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.1rem;
  background: var(--prep-card);
  border: 1px solid var(--prep-primary);
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
  margin-top: 0.5rem;
}

/* ── Top row ───────────────────────────────── */
.loader-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.loader-header-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

/* ── Spinning icon rings ───────────────────── */
.loader-icon-wrap {
  position: relative;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loader-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2.5px solid transparent;
  border-top-color: var(--prep-primary);
  animation: spin 1.1s linear infinite;
}

.loader-ring--2 {
  inset: 6px;
  border-top-color: var(--prep-primary-hover);
  animation-duration: 1.7s;
  animation-direction: reverse;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loader-emoji {
  font-size: 1rem;
  line-height: 1;
  animation: pulse-icon 2s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% { transform: scale(1); }
  50%       { transform: scale(1.12); }
}

/* ── Headings & text ───────────────────────── */
.loader-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--prep-text);
  margin: 0;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loader-status {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--prep-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 1.2em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loader-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--prep-primary);
  flex-shrink: 0;
  animation: blink 1.1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.2; }
}

.loader-percent {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--prep-primary);
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

/* ── Progress bar ──────────────────────────── */
.loader-bar-track {
  width: 100%;
  height: 8px;
  background: var(--prep-border);
  border-radius: 999px;
  overflow: hidden;
  position: relative;
}

.loader-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--prep-primary) 0%, var(--prep-primary-hover) 100%);
  border-radius: 999px;
  transition: width 0.25s ease-out;
  position: relative;
  z-index: 1;
}

/* Shimmer effect on top of the fill */
.loader-bar-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255,255,255,0.45) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.8s linear infinite;
  z-index: 2;
}

@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position:  200% 0; }
}

/* ── Tip ───────────────────────────────────── */
.loader-tip {
  font-size: 0.78rem;
  color: var(--prep-muted);
  margin: 0;
  line-height: 1.5;
  min-height: 1.2em;
}

/* ── Transitions ───────────────────────────── */
.loader-fade-enter-active,
.loader-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.loader-fade-enter-from,
.loader-fade-leave-to {
  opacity: 0;
  transform: scale(0.97);
}

.msg-swap-enter-active,
.msg-swap-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.msg-swap-enter-from  { opacity: 0; transform: translateY(6px); }
.msg-swap-leave-to    { opacity: 0; transform: translateY(-6px); }

.tip-swap-enter-active,
.tip-swap-leave-active {
  transition: opacity 0.5s ease;
}
.tip-swap-enter-from,
.tip-swap-leave-to {
  opacity: 0;
}
</style>