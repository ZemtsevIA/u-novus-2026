<template>
  <AppHeader />

  <div class="profile-page">

    <!-- TITLE -->
    <div class="title-block">
      <h2>Забирай подарки за каждый шаг</h2>
      <span class="subtitle">Ежедневные награды</span>
    </div>

    <!-- CAROUSEL -->
    <div class="carousel-wrapper">
      <div class="carousel">
        <div
          v-for="day in rewards"
          :key="day.id"
          class="reward-card"
          :class="{
            active: day.isToday,
            locked: !day.isUnlocked && !day.isToday,
            claimed: day.isClaimed
          }"
        >
          <div class="icon">
            <img :src="day.icon" />
          </div>

          <div class="label">
            Вход {{ day.day }}
          </div>

          <div v-if="day.isToday" class="today-badge">
            Сегодня
          </div>

          <div v-if="day.isClaimed" class="claimed-badge">
            ✅ Получено
          </div>

          <div v-if="!day.isUnlocked && !day.isToday && !day.isClaimed" class="lock">
            🔒
          </div>

          <button 
            v-if="day.isToday && !day.isClaimed" 
            class="claim-btn"
            @click="claimDailyReward"
          >
            Забрать
          </button>
        </div>
      </div>
    </div>

    <!-- TIMER -->
    <div class="timer">
      Следующий подарок будет доступен через
      <span>{{ timer }}</span>
    </div>

    <!-- ===== SHOP SECTION ===== -->
    <div class="shop-section">

      <!-- SHOP HEADER -->
      <div class="shop-header">
        <div>
          <h2 class="shop-title">Магазин наград</h2>
          <p class="shop-subtitle">
            Трать заработанные баллы на уникальные награды
          </p>
        </div>

        <div class="points-box">
          <span class="points-label">Баланс</span>
          <span class="points-value">{{ userPoints.toLocaleString() }} ⚡</span>
        </div>
      </div>

      <!-- PRODUCTS -->
      <div class="products-grid">
        <div
          v-for="product in products"
          :key="product.id"
          class="product-card"
          :class="{ 'can-afford': userPoints >= product.priceValue }"
        >
          <img
            :src="product.image"
            class="product-image"
          />

          <div class="product-content">
            <h3>{{ product.title }}</h3>
            <p>{{ product.description }}</p>

            <button 
              class="buy-btn"
              :disabled="userPoints < product.priceValue || product.isPurchasing"
              @click="buyProduct(product)"
            >
              <span v-if="product.isPurchasing">⏳</span>
              <span v-else>{{ product.price }} ⚡</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Notification Toast -->
  <div v-if="notification.show" class="notification-toast" :class="notification.type">
    <span class="notification-icon">{{ notification.type === 'success' ? '✅' : '❌' }}</span>
    <span class="notification-message">{{ notification.message }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import AppHeader from '../components/AppHeader.vue'

// API Base URL - замените на ваш реальный backend URL
const API_BASE_URL = 'https://your-backend-api.com/api'

// User data
const userId = ref(null)
const userPoints = ref(0)
const userDailyStep = ref(0)
const nextRewardAvailableAt = ref(null)

// Rewards data
const rewards = ref([])

// Timer
const timer = ref('')
let timerInterval = null

// Products with additional state
const products = ref([
  {
    id: 1,
    title: 'Встреча с разработчиком',
    description: 'Личная беседа и совместный созвон',
    price: '1 000 000',
    priceValue: 1000000,
    image: 'https://avatars.mds.yandex.net/i?id=c70e9491ed7d8aa4b97ea0c54f9ac501_l-4600590-images-thumbs&n=13',
    isPurchasing: false
  },
  {
    id: 2,
    title: 'Premium статус',
    description: 'Уникальный значок и привилегии',
    price: '250 000',
    priceValue: 250000,
    image: 'https://avatars.mds.yandex.net/i?id=b9781a28f26f05a36a6f877920bff765_l-5218797-images-thumbs&n=13',
    isPurchasing: false
  },
  {
    id: 3,
    title: 'Секретный дроп',
    description: 'Эксклюзивный подарок от команды',
    price: '500 000',
    priceValue: 500000,
    image: 'https://images.pravilamag.ru/upload/img_cache/d3f/d3f1546787d35fe525c3b7e593313141_ce_2000x1334x0x33_cropped_510x340.webp',
    isPurchasing: false
  },
  {
    id: 4,
    title: 'VIP доступ',
    description: 'Ранний доступ ко всем функциям',
    price: '750 000',
    priceValue: 750000,
    image: 'https://avatars.mds.yandex.net/i?id=69a97bc586facd3f7460ed03030bb224_l-5252264-images-thumbs&n=13',
    isPurchasing: false
  }
])

// Notification
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Get user ID from URL or localStorage
const getUserId = () => {
  // Способ 1: Из URL параметров
  const urlParams = new URLSearchParams(window.location.search)
  const idFromUrl = urlParams.get('userId') || urlParams.get('id')
  
  // Способ 2: Из localStorage
  const idFromStorage = localStorage.getItem('userId')
  
  // Способ 3: Генерируем тестовый ID (только для разработки)
  const testId = 'test-user-' + Math.random().toString(36).substr(2, 9)
  
  return idFromUrl || idFromStorage || testId
}

// Fetch user data from backend
const fetchUserData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId.value}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      userPoints.value = data.points || 0
      userDailyStep.value = data.dailyStep || 1
      nextRewardAvailableAt.value = data.nextRewardAvailableAt ? new Date(data.nextRewardAvailableAt) : null
      
      // Save user ID if new
      if (data.userId) {
        localStorage.setItem('userId', data.userId)
      }
      
      // Initialize rewards based on user data
      initRewards()
      
      // Start timer if next reward is available
      if (nextRewardAvailableAt.value) {
        startTimer()
      }
    } else {
      console.error('Failed to fetch user data')
      userPoints.value = 0
      initRewards()
    }
  } catch (error) {
    console.error('Error fetching user data:', error)
    userPoints.value = 0
    initRewards()
  }
}

// Initialize rewards array
const initRewards = () => {
  const currentDate = new Date()
  const startDate = new Date(currentDate)
  startDate.setDate(startDate.getDate() - (userDailyStep.value - 1))
  
  rewards.value = []
  
  for (let i = 1; i <= 30; i++) {
    const rewardDate = new Date(startDate)
    rewardDate.setDate(startDate.getDate() + (i - 1))
    
    const isUnlocked = i <= userDailyStep.value
    const isToday = i === userDailyStep.value
    const isClaimed = isUnlocked && i < userDailyStep.value
    
    rewards.value.push({
      id: i,
      day: i,
      isUnlocked: isUnlocked,
      isToday: isToday,
      isClaimed: isClaimed,
      icon: getRewardIcon(i),
      rewardAmount: getRewardAmount(i)
    })
  }
}

// Get reward icon based on day
const getRewardIcon = (day) => {
  const icons = {
    1: 'https://cdn-icons-png.flaticon.com/512/833/833472.png',
    7: 'https://cdn-icons-png.flaticon.com/512/1946/1946421.png',
    14: 'https://cdn-icons-png.flaticon.com/512/3159/3159310.png',
    21: 'https://cdn-icons-png.flaticon.com/512/190/190411.png',
    30: 'https://cdn-icons-png.flaticon.com/512/1041/1041918.png'
  }
  return icons[day] || 'https://cdn-icons-png.flaticon.com/512/833/833472.png'
}

// Get reward amount based on day
const getRewardAmount = (day) => {
  if (day === 1) return 100
  if (day === 7) return 500
  if (day === 14) return 1000
  if (day === 21) return 2000
  if (day === 30) return 5000
  return 50
}

// Claim daily reward
const claimDailyReward = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/claim-daily-reward`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: JSON.stringify({
        userId: userId.value,
        currentStep: userDailyStep.value
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      const rewardAmount = getRewardAmount(userDailyStep.value)
      
      // Update user data
      userPoints.value = data.points || userPoints.value + rewardAmount
      userDailyStep.value = data.dailyStep || userDailyStep.value + 1
      nextRewardAvailableAt.value = data.nextRewardAvailableAt ? new Date(data.nextRewardAvailableAt) : null
      
      // Update rewards display
      initRewards()
      
      // Show success notification
      showNotification(`Вы получили ${rewardAmount} ⚡ за вход ${userDailyStep.value - 1} день!`, 'success')
      
      // Start timer for next reward
      if (nextRewardAvailableAt.value) {
        startTimer()
      }
    } else {
      const error = await response.json()
      showNotification(error.message || 'Не удалось получить награду', 'error')
    }
  } catch (error) {
    console.error('Error claiming reward:', error)
    showNotification('Ошибка при получении награды', 'error')
  }
}

// Buy product
const buyProduct = async (product) => {
  if (userPoints.value < product.priceValue) {
    showNotification(`Недостаточно баллов! Нужно ${product.price} ⚡`, 'error')
    return
  }
  
  // Set purchasing state
  product.isPurchasing = true
  
  try {
    const response = await fetch(`${API_BASE_URL}/purchase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: JSON.stringify({
        userId: userId.value,
        productId: product.id,
        price: product.priceValue
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Update user points
      userPoints.value = data.remainingPoints || userPoints.value - product.priceValue
      
      // Show success notification
      showNotification(`Вы успешно приобрели "${product.title}"!`, 'success')
      
      // Save purchase to localStorage for demo
      const purchases = JSON.parse(localStorage.getItem('purchases') || '[]')
      purchases.push({
        userId: userId.value,
        productId: product.id,
        productTitle: product.title,
        purchaseDate: new Date().toISOString()
      })
      localStorage.setItem('purchases', JSON.stringify(purchases))
      
    } else {
      const error = await response.json()
      showNotification(error.message || 'Ошибка при покупке', 'error')
    }
  } catch (error) {
    console.error('Error buying product:', error)
    showNotification('Ошибка при совершении покупки', 'error')
  } finally {
    product.isPurchasing = false
  }
}

// Start timer for next reward
const startTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  
  const updateTimer = () => {
    if (!nextRewardAvailableAt.value) {
      timer.value = 'Доступно сейчас!'
      return
    }
    
    const now = new Date()
    const diff = nextRewardAvailableAt.value - now
    
    if (diff <= 0) {
      timer.value = 'Доступно сейчас!'
      if (timerInterval) clearInterval(timerInterval)
    } else {
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)
      timer.value = `${hours}ч ${minutes}мин ${seconds}сек`
    }
  }
  
  updateTimer()
  timerInterval = setInterval(updateTimer, 1000)
}

// Show notification
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message: message,
    type: type
  }
  
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

// Initialize component
onMounted(async () => {
  userId.value = getUserId()
  await fetchUserData()
})

// Cleanup timer on component unmount
onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<style scoped>


.profile-page {
  min-height: 100vh;
  padding: 20px;
  color: white;
  padding-right: 0;
  
  /* Современный стеклянный фон */
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  
  /* Эффект выпуклости (neomorphism) */
  border-radius: 32px;
  box-shadow: 
    20px 20px 40px rgba(0, 0, 0, 0.3),
    -8px -8px 16px rgba(255, 255, 255, 0.1),
    inset 2px 2px 4px rgba(255, 255, 255, 0.15),
    inset -2px -2px 4px rgba(0, 0, 0, 0.05);
  
  /* Дополнительные штрихи для современного вида */
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin: 20px;
  transition: all 0.3s ease;
}

/* Эффект при наведении для усиления выпуклости */
.profile-page:hover {
  box-shadow: 
    22px 22px 44px rgba(0, 0, 0, 0.35),
    -10px -10px 20px rgba(255, 255, 255, 0.12),
    inset 3px 3px 6px rgba(255, 255, 255, 0.18),
    inset -3px -3px 6px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* ===== TITLE ===== */
.title-block h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  margin-right: 20px;
}

.subtitle {
  font-size: 13px;
  opacity: 0.6;
}

/* ===== CAROUSEL ===== */
.carousel-wrapper {
  margin-top: 20px;
}

.carousel {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding: 10px 0 20px;
  scroll-snap-type: x mandatory;
  padding-left: 10px;
}

.carousel::-webkit-scrollbar {
  display: none;
}

/* ===== CARD ===== */
.reward-card {
  min-width: 120px;
  height: 160px;
  scroll-snap-align: start;

  position: relative;
  border-radius: 18px;

  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);

  border: 1px solid rgba(255, 255, 255, 0.12);

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  transition: 0.3s ease;
}

/* ACTIVE (сегодняшний день) */
.reward-card.active {
  background: linear-gradient(
    145deg,
    rgba(140, 90, 255, 0.35),
    rgba(80, 200, 255, 0.15)
  );
  border: 1px solid rgba(160, 120, 255, 0.5);
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(120, 90, 255, 0.25);
}

/* LOCKED */
.reward-card.locked {
  opacity: 0.4;
  filter: grayscale(1);
}

/* ICON */
.icon img {
  width: 48px;
  height: 48px;
}

/* LABEL */
.label {
  margin-top: 10px;
  font-size: 14px;
  font-weight: 500;
}

/* TODAY BADGE */
.today-badge {
  position: absolute;
  bottom: 10px;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(120, 90, 255, 0.3);
  border: 1px solid rgba(160, 120, 255, 0.4);
}

/* LOCK */
.lock {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 14px;
}

/* TIMER */
.timer {
  margin-top: 15px;
  font-size: 14px;
  opacity: 0.7;
}

.timer span {
  color: #7cf7d4;
  font-weight: 600;
}

/* =========================
   SHOP SECTION
========================= */

.shop-section {
  margin-top: 40px;
  padding-right: 20px;
}

/* HEADER */
.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 20px;
}

.shop-title {
  font-size: 24px;
  margin: 0;
  font-weight: 700;
}

.shop-subtitle {
  margin-top: 6px;
  opacity: 0.65;
  font-size: 14px;
}

/* POINTS */
.points-box {
  min-width: 120px;

  padding: 14px 18px;
  border-radius: 20px;

  background: rgba(255, 255, 255, 0.08);

  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  border: 1px solid rgba(255,255,255,0.1);

  display: flex;
  flex-direction: column;
  align-items: center;

  box-shadow:
    0 8px 24px rgba(0,0,0,0.25),
    inset 1px 1px 2px rgba(255,255,255,0.08);
}

.points-label {
  font-size: 12px;
  opacity: 0.6;
}

.points-value {
  font-size: 20px;
  font-weight: 700;
  color: #7cf7d4;
  margin-top: 4px;
}

/* GRID */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

/* CARD */
.product-card {
  overflow: hidden;
  border-radius: 24px;

  background: rgba(255,255,255,0.06);

  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);

  border: 1px solid rgba(255,255,255,0.08);

  transition: 0.3s ease;

  box-shadow:
    0 10px 30px rgba(0,0,0,0.25),
    inset 1px 1px 1px rgba(255,255,255,0.06);
}

.product-card:hover {
  transform: translateY(-6px);
  box-shadow:
    0 14px 40px rgba(120,90,255,0.2);
}

/* IMAGE */
.product-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

/* CONTENT */
.product-content {
  padding: 18px;
}

.product-content h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.product-content p {
  margin-top: 8px;
  font-size: 13px;
  opacity: 0.7;
  line-height: 1.4;
}

/* BUTTON */
.buy-btn {
  margin-top: 18px;
  width: 100%;
  padding: 12px;

  border: none;
  border-radius: 14px;

  font-weight: 600;
  font-size: 14px;

  color: white;

  cursor: pointer;

  background: linear-gradient(
    135deg,
    rgba(140,90,255,0.9),
    rgba(80,200,255,0.8)
  );

  transition: 0.25s ease;
}

.buy-btn:hover {
  transform: scale(1.03);
  box-shadow:
    0 8px 20px rgba(120,90,255,0.35);
}



.claim-btn {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 12px;
  background: linear-gradient(135deg, #7cf7d4, #4ecdc4);
  border: none;
  border-radius: 20px;
  color: #1a1a2e;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.claim-btn:hover {
  transform: translateX(-50%) scale(1.05);
  box-shadow: 0 4px 12px rgba(124, 247, 212, 0.3);
}

.claimed-badge {
  position: absolute;
  bottom: 10px;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(76, 175, 80, 0.3);
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.product-card.can-afford .buy-btn {
  background: linear-gradient(135deg, #7cf7d4, #4ecdc4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.buy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Notification Toast */
.notification-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  min-width: 300px;
  padding: 16px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.notification-toast.success {
  background: rgba(76, 175, 80, 0.9);
  border-left: 4px solid #4caf50;
}

.notification-toast.error {
  background: rgba(244, 67, 54, 0.9);
  border-left: 4px solid #f44336;
}

.notification-icon {
  font-size: 24px;
}

.notification-message {
  flex: 1;
  font-size: 14px;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .profile-page {
    margin: 10px;
    padding: 15px;
  }
  
  .shop-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .points-box {
    width: 100%;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .notification-toast {
    left: 20px;
    right: 20px;
    min-width: auto;
  }
}
</style>