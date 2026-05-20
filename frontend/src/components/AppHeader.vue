<template>
  <header class="header">
    <div class="logo">
      <img @click="navigateTo('home')" class="logo-img" src="/src/assets/logo.png" alt="logo">
    </div>

    <div class="menu-container">
      <!-- Кнопка меню -->
      <button class="menu-btn" @click="toggleMenu">
        <span class="line" :class="{ 'open': isMenuOpen }"></span>
        <span class="line" :class="{ 'open': isMenuOpen }"></span>
        <span class="line" :class="{ 'open': isMenuOpen }"></span>
      </button>

      <!-- Выпадающее меню -->
      <div v-if="isMenuOpen" class="dropdown-menu">
        <ul>
          <li @click="navigateTo('shop')">Магазин</li>
          <li @click="navigateTo('leaderboard')">Лидерборд</li>
          <li @click="navigateTo('profile')">Профиль</li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const navigateTo = (page) => {
  switch (page) {
    case 'profile':
      router.push('/profile')
      break
    case 'shop':
      router.push('/Shop')
      break
    case 'leaderboard':
      router.push('/Liderboarding')
      break
    case 'home':
      router.push('/')
      break
  }
  isMenuOpen.value = false // закрываем меню после перехода
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: 'Times New Roman', Times, serif;
  width: 100%;
  padding: 3vh 20px;
  position: relative;
  z-index: 1000;
}

.logo {
  height: 100%;
  width: auto;
}

.logo-img {
  height: 100%;
  max-height: 60px;
  width: auto;
  object-fit: contain;
}

/* ==================== Кнопка меню ==================== */
.menu-container {
  position: relative;
}

.menu-btn {
  width: 60px;
  height: 60px;
  border: none;
  border-radius: 18px;
  background: #07051a; 
  display: flex; 
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  box-shadow:
    inset 0 0 10px rgba(255, 0, 140, 0.08),
    0 0 15px rgba(255, 0, 140, 0.15);
  transition: 0.25s ease;
}

.line {
  width: 28px;
  height: 4px;
  border-radius: 10px;
  background: #ff00b7;
  box-shadow: 0 0 6px #ff00b7, 0 0 12px rgba(255, 0, 183, 0.8);
  transition: all 0.3s ease;
}

/* Превращение в крестик */
.menu-btn:hover {
  transform: scale(1.05);
  box-shadow:
    inset 0 0 14px rgba(255, 0, 183, 0.15),
    0 0 20px rgba(255, 0, 183, 0.3);
}

.menu-btn:hover .line {
  background: #ff33c8;
}

.line.open:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.line.open:nth-child(2) {
  opacity: 0;
}

.line.open:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* ==================== Выпадающее меню ==================== */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 12px);     /* Чуть ниже кнопки */
  right: 0;
  background: #ffffff;
  border-radius: 16px;
  padding: 12px 8px;
  min-width: 180px;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.4),
    0 0 20px rgba(255, 0, 183, 0.2);
  border: 1px solid rgba(255, 0, 183, 0.15);
  z-index: 1100;
  animation: fadeIn 0.2s ease;
}

.dropdown-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dropdown-menu li {
  padding: 14px 20px;
  color: #07051a;
  font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
  font-size: 1.05rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dropdown-menu li:hover {
  background: rgba(255, 0, 183, 0.15);
  color: #ff33c8;
  transform: translateX(4px);
}

/* Анимация появления */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>