import { reactive, readonly, watch } from 'vue'

const AUTH_KEY = 'prepMateAuth'
const USERS_KEY = 'prepMateUsers'
const GUEST_SESSION_KEY = 'prepMateGuestSession'

function loadAuth() {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.localStorage.getItem(AUTH_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function saveAuth(user) {
  if (typeof window === 'undefined') return
  if (!user) {
    window.localStorage.removeItem(AUTH_KEY)
    return
  }
  window.localStorage.setItem(AUTH_KEY, JSON.stringify(user))
}

function loadUsers() {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(USERS_KEY)
    if (!raw) return []
    return JSON.parse(raw)
  } catch {
    return []
  }
}

function saveUsers(users) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(USERS_KEY, JSON.stringify(users))
}

const state = reactive({
  currentUser: loadAuth()
})

watch(
  () => state.currentUser,
  (user) => saveAuth(user),
  { deep: true }
)

function isAuthenticated() {
  return state.currentUser !== null && state.currentUser !== undefined
}

function login(credentials) {
  const { usernameOrEmail, password } = credentials
  if (!usernameOrEmail?.trim() || !password) {
    return { success: false, error: 'Please enter username/email and password.' }
  }
  const users = loadUsers()
  const user = users.find(
    (u) =>
      (u.username.toLowerCase() === usernameOrEmail.trim().toLowerCase() ||
        u.email.toLowerCase() === usernameOrEmail.trim().toLowerCase()) &&
      u.password === password
  )
  if (!user) {
    return { success: false, error: 'Invalid username/email or password.' }
  }
  state.currentUser = {
    type: 'user',
    id: user.id,
    username: user.username,
    email: user.email
  }
  return { success: true }
}

function signUp(userData) {
  const { username, email, password, confirmPassword } = userData
  if (!username?.trim()) return { success: false, error: 'Username is required.' }
  if (!email?.trim()) return { success: false, error: 'Email is required.' }
  if (!password) return { success: false, error: 'Password is required.' }
  if (password !== confirmPassword) {
    return { success: false, error: 'Passwords do not match.' }
  }
  const err = validatePassword(password)
  if (err) return { success: false, error: err }

  const users = loadUsers()
  if (users.some((u) => u.username.toLowerCase() === username.trim().toLowerCase())) {
    return { success: false, error: 'Username is already taken.' }
  }
  if (users.some((u) => u.email.toLowerCase() === email.trim().toLowerCase())) {
    return { success: false, error: 'Email is already registered.' }
  }

  const id = Date.now().toString(36) + Math.random().toString(36).slice(2)
  const newUser = {
    id,
    username: username.trim(),
    email: email.trim().toLowerCase(),
    password,
    savedRecipes: [],
    groceryItems: [],
    nextIds: { recipe: 1, groceryItem: 1 }
  }
  users.push(newUser)
  saveUsers(users)
  state.currentUser = {
    type: 'user',
    id: newUser.id,
    username: newUser.username,
    email: newUser.email
  }
  return { success: true }
}

function validatePassword(password) {
  if (password.length < 8) return 'Password must be at least 8 characters.'
  if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter.'
  if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter.'
  if (!/[0-9]/.test(password)) return 'Password must contain at least one number.'
  if (!/[^A-Za-z0-9]/.test(password)) return 'Password must contain at least one special character.'
  return null
}

export function getPasswordChecklist(password) {
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9]/.test(password)
  }
}

function continueAsGuest() {
  state.currentUser = { type: 'guest' }
  return { success: true }
}

function logout() {
  const wasGuest = state.currentUser?.type === 'guest'
  state.currentUser = null
  if (wasGuest && typeof window !== 'undefined') {
    window.localStorage.removeItem(GUEST_SESSION_KEY)
  }
}

export function getGuestSessionKey() {
  return GUEST_SESSION_KEY
}

export function useAuthStore() {
  return {
    state: readonly(state),
    currentUser: state.currentUser,
    isAuthenticated: () => isAuthenticated(),
    login,
    signUp,
    continueAsGuest,
    logout,
    loadUsers,
    saveUsers
  }
}
