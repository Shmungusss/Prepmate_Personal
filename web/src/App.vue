<template>
  <div id="app">
    <header v-if="isAuthenticated" class="top-nav">
      <div class="brand" @click="$router.push({ name: 'Recipes' })">
        PrepMate
      </div>
      <nav class="nav-links">
        <router-link to="/" exact-active-class="active" exact>Home</router-link>
        <router-link :to="{ name: 'Recipes' }" active-class="active">
          Recipes
        </router-link>
        <router-link :to="{ name: 'Pantry' }" active-class="active">
          Pantry
        </router-link>
        <router-link :to="{ name: 'MealPlan' }" active-class="active">
          Meal Plan
        </router-link>
        <router-link :to="{ name: 'GroceryList' }" active-class="active">
          Grocery List
        </router-link>
        <div class="user-menu-wrap" ref="userMenuRef">
          <button
            type="button"
            class="btn-user"
            :aria-expanded="userMenuOpen"
            aria-haspopup="true"
            @click="userMenuOpen = !userMenuOpen"
          >
            {{ displayName }}
            <span class="chevron">▼</span>
          </button>
          <Transition name="dropdown">
            <div v-if="userMenuOpen" class="user-dropdown">
              <button type="button" class="user-dropdown-item logout" @click="logout">
                Log out
              </button>
            </div>
          </Transition>
        </div>
      </nav>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated())
    const userMenuOpen = ref(false)
    const userMenuRef = ref(null)

    const displayName = computed(() => {
      const user = authStore.currentUser
      if (!user) return ''
      if (user.type === 'guest') return 'Guest'
      return user.username || 'Account'
    })

    function logout() {
      authStore.logout()
      userMenuOpen.value = false
      router.push({ name: 'Home' })
    }

    function onDocClick(e) {
      if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
        userMenuOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', onDocClick)
    })
    onUnmounted(() => {
      document.removeEventListener('click', onDocClick)
    })

    return { isAuthenticated, displayName, userMenuOpen, userMenuRef, logout }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

:root {
  --prep-bg: #0d1117;
  --prep-card: #161b22;
  --prep-border: #30363d;
  --prep-text: #e6edf3;
  --prep-muted: #8b949e;
  --prep-primary: #00c8b4;
  --prep-primary-hover: #00e5cc;
  --prep-accent: #2ea043;
  --prep-error: #f85149;
  --prep-font-display: 'JetBrains Mono', monospace;
  --prep-font-body: 'Outfit', sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--prep-font-body);
  background: var(--prep-bg);
  color: var(--prep-text);
  min-height: 100vh;
}

#app {
  padding: 0;
  min-height: 100vh;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.5rem;
  background: var(--prep-card);
  border-bottom: 1px solid var(--prep-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.brand {
  font-family: var(--prep-font-display);
  font-weight: 700;
  font-size: 1.15rem;
  color: var(--prep-primary);
  cursor: pointer;
  letter-spacing: -0.02em;
}

.brand:hover {
  color: var(--prep-primary-hover);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-links a {
  text-decoration: none;
  color: var(--prep-muted);
  font-size: 0.9rem;
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
  font-weight: 500;
  transition: color 0.2s, background 0.2s;
}

.nav-links a:hover {
  color: var(--prep-text);
  background: rgba(0, 200, 180, 0.08);
}

.nav-links a.active {
  background: var(--prep-primary);
  color: var(--prep-bg);
}

.user-menu-wrap {
  position: relative;
  margin-left: 0.5rem;
}

.btn-user {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.85rem;
  background: var(--prep-border);
  color: var(--prep-text);
  border: 1px solid var(--prep-border);
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.2s;
}

.btn-user:hover {
  background: rgba(0, 200, 180, 0.12);
  border-color: var(--prep-primary);
  color: var(--prep-primary);
}

.btn-user .chevron {
  font-size: 0.6rem;
  opacity: 0.8;
  transition: transform 0.2s;
}

.btn-user[aria-expanded="true"] .chevron {
  transform: rotate(-180deg);
}

.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 4px);
  min-width: 140px;
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  padding: 0.25rem 0;
  z-index: 20;
}

.user-dropdown-item {
  display: block;
  width: 100%;
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  text-align: left;
  font-size: 0.9rem;
  color: var(--prep-text);
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.user-dropdown-item:hover {
  background: rgba(0, 200, 180, 0.08);
}

.user-dropdown-item.logout {
  color: var(--prep-error);
}

.user-dropdown-item.logout:hover {
  background: rgba(248, 81, 73, 0.12);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.main-content {
  padding: 1.5rem;
  min-height: calc(100vh - 56px);
}
</style>
