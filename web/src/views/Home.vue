<template>
  <div class="page">
    <header class="hero">
      <h1 class="hero-title">Free AI Recipe Generator</h1>
      <p class="hero-tagline">
        PrepMate helps you turn whatever is in your kitchen into fast, flexible recipes
        and ready-to-shop grocery lists. Less stress, less waste, better meals.
      </p>
    </header>

    <section class="content">
      <p class="intro-text">
        Tell PrepMate what ingredients you have and your preferences, and our AI will
        suggest recipes tailored to you. Save your favorites and build a grocery list
        in just a few clicks.
      </p>

      <button class="btn-primary" @click="$router.push({ name: 'RecipeGenerator' })">
        Get Started
      </button>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.page {
  max-width: 640px;
  margin: 0 auto;
  padding: 1rem;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}
.hero-title {
  font-size: 1.75rem;
  color: #1a1a1a;
  margin-bottom: 0.75rem;
}
.hero-tagline {
  color: #555;
  line-height: 1.5;
  font-size: 1rem;
}

.content {
  margin-top: 1.5rem;
  text-align: center;
}

.intro-text {
  margin-bottom: 1.5rem;
  color: #555;
  line-height: 1.6;
  font-size: 0.98rem;
}

.btn-primary {
  padding: 0.9rem 1.8rem;
  background: #2d8a5e;
  color: white;
  border: none;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}
.btn-primary:hover {
  background: #247a50;
}
</style>
