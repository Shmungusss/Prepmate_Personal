<template>
  <div id="app">
    <header class="top-nav">
      <div class="brand" @click="$router.push({ name: 'Home' })">
        PrepMate
      </div>
      <nav class="nav-links">
        <router-link to="/" exact-active-class="active" exact>Home</router-link>
        <router-link
          :to="{ name: 'RecipeGenerator' }"
          active-class="active"
        >
          Recipe Generator
        </router-link>
        <router-link
          :to="{ name: 'SavedRecipes' }"
          active-class="active"
        >
          Saved Recipes
        </router-link>
        <router-link
          :to="{ name: 'GroceryList' }"
          active-class="active"
        >
          Grocery List
        </router-link>
      </nav>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
}

#app {
  padding: 0;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e2e6ea;
  position: sticky;
  top: 0;
  z-index: 10;
}

.brand {
  font-weight: 700;
  font-size: 1.1rem;
  color: #2d8a5e;
  cursor: pointer;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  text-decoration: none;
  color: #444;
  font-size: 0.95rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
}

.nav-links a.active {
  background: #2d8a5e;
  color: #fff;
}

.nav-links a:hover {
  background: #edf4f1;
}

.main-content {
  padding: 1.5rem;
}
</style>