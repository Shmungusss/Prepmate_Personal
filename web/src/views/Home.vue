<template>
  <div class="page">
    <header class="hero">
      <h1 class="hero-title">PrepMate</h1>
      <p class="hero-tagline">
        AI-powered recipes and grocery lists. Less stress, less waste, better meals.
      </p>
    </header>

    <!-- Logged in or guest: show Generate Recipe button only -->
    <section class="content" v-if="isAuthenticated">
      <p class="intro-text">
        Tell PrepMate what ingredients you have and your preferences. Generate recipes,
        save favorites, and build your grocery list in one place.
      </p>
      <button class="btn-primary" @click="$router.push({ name: 'Recipes' })">
        Generate Recipe
      </button>
    </section>

    <!-- Not logged in: Get Started reveals auth panel -->
    <section class="content" v-else-if="!showAuthPanel">
      <p class="intro-text">
        Tell PrepMate what ingredients you have and your preferences. Generate recipes,
        save favorites, and build your grocery list in one place.
      </p>
      <button class="btn-primary" @click="showAuthPanel = true">
        Get Started
      </button>
    </section>

    <section class="auth-panel" v-else>
      <div class="auth-tabs">
        <button
          type="button"
          :class="['tab', { active: mode === 'login' }]"
          @click="mode = 'login'; error = null"
        >
          Log in
        </button>
        <button
          type="button"
          :class="['tab', { active: mode === 'signup' }]"
          @click="mode = 'signup'; error = null"
        >
          Sign up
        </button>
      </div>

      <!-- Login form -->
      <form v-if="mode === 'login'" class="auth-form" @submit.prevent="onLogin">
        <div class="field">
          <label for="login-identity">Username or email</label>
          <input
            id="login-identity"
            v-model="loginIdentity"
            type="text"
            placeholder="username or email"
            autocomplete="username"
          />
        </div>
        <div class="field">
          <label for="login-password">Password</label>
          <input
            id="login-password"
            v-model="loginPassword"
            type="password"
            placeholder="password"
            autocomplete="current-password"
          />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-primary btn-block">Log in</button>
      </form>

      <!-- Sign up form -->
      <form v-if="mode === 'signup'" class="auth-form" @submit.prevent="onSignUp">
        <div class="field">
          <label for="signup-username">Username</label>
          <input
            id="signup-username"
            v-model="signupUsername"
            type="text"
            placeholder="username"
            autocomplete="username"
          />
        </div>
        <div class="field">
          <label for="signup-email">Email</label>
          <input
            id="signup-email"
            v-model="signupEmail"
            type="email"
            placeholder="email@example.com"
            autocomplete="email"
          />
        </div>
        <div class="field">
          <label for="signup-password">Password</label>
          <input
            id="signup-password"
            v-model="signupPassword"
            type="password"
            placeholder="password"
            autocomplete="new-password"
          />
          <ul class="password-checklist" aria-live="polite">
            <li :class="{ pass: checklist.length }"><span class="check">{{ checklist.length ? '✓' : '○' }}</span> At least 8 characters</li>
            <li :class="{ pass: checklist.uppercase }"><span class="check">{{ checklist.uppercase ? '✓' : '○' }}</span> One uppercase letter</li>
            <li :class="{ pass: checklist.lowercase }"><span class="check">{{ checklist.lowercase ? '✓' : '○' }}</span> One lowercase letter</li>
            <li :class="{ pass: checklist.number }"><span class="check">{{ checklist.number ? '✓' : '○' }}</span> One number</li>
            <li :class="{ pass: checklist.special }"><span class="check">{{ checklist.special ? '✓' : '○' }}</span> One special character</li>
          </ul>
        </div>
        <div class="field">
          <label for="signup-confirm">Confirm password</label>
          <input
            id="signup-confirm"
            v-model="signupConfirm"
            type="password"
            placeholder="confirm password"
            autocomplete="new-password"
          />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-primary btn-block">Create account</button>
      </form>

      <div class="guest-row">
        <span class="guest-label">or</span>
        <button type="button" class="btn-ghost" @click="onContinueAsGuest">
          Continue as guest
        </button>
      </div>

      <button type="button" class="btn-back" @click="showAuthPanel = false; error = null">
        ← Back
      </button>
    </section>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, getPasswordChecklist } from '@/store/authStore'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated())
    const showAuthPanel = ref(false)
    const mode = ref('login')
    const error = ref(null)

    const loginIdentity = ref('')
    const loginPassword = ref('')

    const signupUsername = ref('')
    const signupEmail = ref('')
    const signupPassword = ref('')
    const signupConfirm = ref('')

    const checklist = computed(() => getPasswordChecklist(signupPassword.value))

    async function onLogin() {
      error.value = null
      const result = await authStore.login({
        usernameOrEmail: loginIdentity.value,
        password: loginPassword.value
      })
      if (result.success) {
        router.push({ name: 'Recipes' })
      } else {
        error.value = result.error
      }
    }

    async function onSignUp() {
      error.value = null
      const result = await authStore.signUp({
        username: signupUsername.value,
        email: signupEmail.value,
        password: signupPassword.value,
        confirmPassword: signupConfirm.value
      })
      if (result.success) {
        router.push({ name: 'Recipes' })
      } else {
        error.value = result.error
      }
    }

    function onContinueAsGuest() {
      authStore.continueAsGuest()
      router.push({ name: 'Recipes' })
    }

    return {
      isAuthenticated,
      showAuthPanel,
      mode,
      error,
      loginIdentity,
      loginPassword,
      signupUsername,
      signupEmail,
      signupPassword,
      signupConfirm,
      checklist,
      onLogin,
      onSignUp,
      onContinueAsGuest
    }
  }
}
</script>

<style scoped>
.page {
  max-width: 440px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}

.hero-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--prep-text);
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
  font-family: var(--prep-font-display);
}

.hero-tagline {
  color: var(--prep-muted);
  line-height: 1.5;
  font-size: 1rem;
  font-family: var(--prep-font-body);
}

.content {
  text-align: center;
}

.intro-text {
  margin-bottom: 1.5rem;
  color: var(--prep-muted);
  line-height: 1.6;
  font-size: 0.98rem;
}

.btn-primary {
  padding: 0.9rem 1.8rem;
  background: var(--prep-primary);
  color: var(--prep-bg);
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: background 0.2s, transform 0.15s;
}

.btn-primary:hover {
  background: var(--prep-primary-hover);
  transform: translateY(-1px);
}

.btn-block {
  width: 100%;
  margin-top: 0.5rem;
}

.auth-panel {
  background: var(--prep-card);
  border: 1px solid var(--prep-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.auth-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.tab {
  flex: 1;
  padding: 0.6rem 1rem;
  background: transparent;
  border: 1px solid var(--prep-border);
  border-radius: 8px;
  color: var(--prep-muted);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.2s;
}

.tab:hover {
  color: var(--prep-text);
  border-color: var(--prep-primary);
}

.tab.active {
  background: var(--prep-primary);
  color: var(--prep-bg);
  border-color: var(--prep-primary);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--prep-text);
}

.field input {
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  border: 1px solid var(--prep-border);
  font-size: 1rem;
  background: var(--prep-bg);
  color: var(--prep-text);
  font-family: var(--prep-font-body);
}

.field input::placeholder {
  color: var(--prep-muted);
}

.field input:focus {
  outline: none;
  border-color: var(--prep-primary);
  box-shadow: 0 0 0 2px rgba(0, 200, 180, 0.2);
}

.password-checklist {
  list-style: none;
  padding: 0.5rem 0 0;
  margin: 0;
  font-size: 0.8rem;
  color: var(--prep-muted);
}

.password-checklist li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.password-checklist li.pass {
  color: var(--prep-accent);
}

.password-checklist .check {
  font-weight: 700;
}

.error-msg {
  color: var(--prep-error);
  font-size: 0.9rem;
  margin: 0;
}

.guest-row {
  text-align: center;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--prep-border);
}

.guest-label {
  display: block;
  font-size: 0.85rem;
  color: var(--prep-muted);
  margin-bottom: 0.5rem;
}

.btn-ghost {
  padding: 0.6rem 1.2rem;
  background: transparent;
  color: var(--prep-primary);
  border: 1px solid var(--prep-primary);
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--prep-font-body);
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: rgba(0, 200, 180, 0.1);
}

.btn-back {
  display: block;
  margin: 1rem auto 0;
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--prep-muted);
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  font-family: var(--prep-font-body);
}

.btn-back:hover {
  color: var(--prep-text);
}
</style>
