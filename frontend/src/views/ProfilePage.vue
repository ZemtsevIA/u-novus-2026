<template>
  <AppHeader />
  
  <div class="profile-page">
    <!-- Profile Header with Avatar and Stats -->
    <div class="profile-header">
      <div class="avatar-wrapper">
        <div class="avatar">
          <img :src="userAvatar" alt="Avatar" />
          <button class="edit-avatar-btn" @click="openAvatarModal">✎</button>
        </div>
      </div>
      
      <div class="profile-info">
        <h1 class="username">{{ username }}</h1>
        <p class="user-email">{{ userEmail }}</p>
        
        <div class="stats-row">
          <div class="stat-card">
            <span class="stat-value">{{ userPoints.toLocaleString() }}</span>
            <span class="stat-label">⚡ Баллов</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ totalPurchases }}</span>
            <span class="stat-label">🎁 Покупок</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ dailyStreak }}</span>
            <span class="stat-label">🔥 Дней подряд</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Achievements Section -->
    <div class="achievements-section">
      <div class="section-header">
        <h2>Достижения</h2>
        <span class="section-subtitle">Коллекция наград</span>
      </div>
      
      <div class="achievements-grid">
        <div 
          v-for="achievement in achievements" 
          :key="achievement.id"
          class="achievement-card"
          :class="{ unlocked: achievement.isUnlocked }"
        >
          <div class="achievement-icon">
            {{ achievement.isUnlocked ? achievement.icon : '🔒' }}
          </div>
          <div class="achievement-info">
            <h4>{{ achievement.title }}</h4>
            <p>{{ achievement.description }}</p>
          </div>
          <div v-if="!achievement.isUnlocked" class="achievement-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: achievement.progress + '%' }"></div>
            </div>
            <span>{{ achievement.current }}/{{ achievement.required }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Purchases -->
    <div class="purchases-section">
      <div class="section-header">
        <h2>Последние покупки</h2>
        <span class="section-subtitle">Ваши приобретения</span>
      </div>
      
      <div v-if="recentPurchases.length > 0" class="purchases-list">
        <div 
          v-for="purchase in recentPurchases" 
          :key="purchase.id"
          class="purchase-item"
        >
          <div class="purchase-image">
            <img :src="purchase.image" />
          </div>
          <div class="purchase-details">
            <h4>{{ purchase.title }}</h4>
            <p>{{ purchase.description }}</p>
          </div>
          <div class="purchase-price">
            <span class="price-value">{{ purchase.price }} ⚡</span>
            <span class="purchase-date">{{ formatDate(purchase.purchaseDate) }}</span>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <span class="empty-icon">🛍️</span>
        <p>У вас пока нет покупок</p>
        <router-link to="/shop" class="shop-link">Перейти в магазин</router-link>
      </div>
    </div>

    <!-- Avatar Edit Modal -->
    <div v-if="showAvatarModal" class="modal-overlay" @click.self="closeAvatarModal">
      <div class="modal-content">
        <h3>Выберите аватар</h3>
        <div class="avatar-options">
          <div 
            v-for="avatar in avatarOptions" 
            :key="avatar.id"
            class="avatar-option"
            :class="{ selected: selectedAvatar === avatar.url }"
            @click="selectAvatar(avatar.url)"
          >
            <img :src="avatar.url" />
          </div>
        </div>
        <div class="modal-buttons">
          <button class="cancel-btn" @click="closeAvatarModal">Отмена</button>
          <button class="save-btn" @click="saveAvatar">Сохранить</button>
        </div>
      </div>
    </div>

    <!-- Notification Toast -->
    <div v-if="notification.show" class="notification-toast" :class="notification.type">
      <span class="notification-icon">{{ notification.type === 'success' ? '✅' : '❌' }}</span>
      <span class="notification-message">{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../components/AppHeader.vue'

// API Base URL
const API_BASE_URL = 'https://your-backend-api.com/api'

// User data
const userId = ref(null)
const username = ref('Пользователь')
const userEmail = ref('')
const userAvatar = ref('https://cdn-icons-png.flaticon.com/512/3135/3135715.png')
const userPoints = ref(0)
const dailyStreak = ref(0)
const totalPurchases = ref(0)

// Achievements
const achievements = ref([
  {
    id: 1,
    title: 'Первые шаги',
    description: 'Совершить первую покупку',
    icon: '🏆',
    isUnlocked: false,
    current: 0,
    required: 1
  },
  {
    id: 2,
    title: 'Коллекционер',
    description: 'Купить 5 товаров',
    icon: '🎯',
    isUnlocked: false,
    current: 0,
    required: 5
  },
  {
    id: 3,
    title: 'Магнат',
    description: 'Накопить 100 000 баллов',
    icon: '💰',
    isUnlocked: false,
    current: 0,
    required: 100000
  },
  {
    id: 4,
    title: 'Преданный фанат',
    description: 'Заходить в приложение 30 дней подряд',
    icon: '⭐',
    isUnlocked: false,
    current: 0,
    required: 30
  }
])

// Recent purchases
const recentPurchases = ref([])

// UI state
const showAvatarModal = ref(false)
const selectedAvatar = ref('')
const avatarOptions = ref([
  { id: 1, url: 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png' },
  { id: 2, url: 'https://cdn-icons-png.flaticon.com/512/3135/3135768.png' },
  { id: 3, url: 'https://cdn-icons-png.flaticon.com/512/3135/3135789.png' },
  { id: 4, url: 'https://cdn-icons-png.flaticon.com/512/3135/3135823.png' },
  { id: 5, url: 'https://cdn-icons-png.flaticon.com/512/3135/3135845.png' }
])

// Notification
const notification = ref({
  show: false,
  message: '',
  type: 'success'
})

// Get Telegram user data
const getTelegramUser = () => {
  // Проверяем, что мы в Telegram Mini App
  if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp
    const initData = webApp.initDataUnsafe
    
    if (initData && initData.user) {
      const telegramUser = initData.user
      
      // Заполняем данные из Telegram
      userId.value = telegramUser.id.toString()
      username.value = telegramUser.first_name + (telegramUser.last_name ? ' ' + telegramUser.last_name : '')
      userEmail.value = telegramUser.username ? `@${telegramUser.username}` : 'Telegram пользователь'
      
      // Если есть фото профиля в Telegram
      if (telegramUser.photo_url) {
        userAvatar.value = telegramUser.photo_url
      }
      
      // Сохраняем ID в localStorage для дальнейшего использования
      localStorage.setItem('userId', userId.value)
      localStorage.setItem('telegramUsername', telegramUser.username || '')
      
      // Показываем интерфейс и раскрываем на весь экран
      webApp.ready()
      webApp.expand()
      
      return true
    }
  }
  
  // Если не в Telegram или нет данных, используем fallback
  console.warn('Not in Telegram or no user data available')
  const fallbackId = 'user-' + Math.random().toString(36).substr(2, 9)
  userId.value = fallbackId
  username.value = 'Гость'
  userEmail.value = 'Не в Telegram'
  localStorage.setItem('userId', fallbackId)
  
  return false
}

// Telegram authentication on backend
const telegramAuth = async () => {
  if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp
    const initData = webApp.initDataUnsafe
    
    if (initData && initData.user) {
      try {
        const response = await fetch(`${API_BASE_URL}/telegram-auth`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            id: initData.user.id,
            first_name: initData.user.first_name,
            last_name: initData.user.last_name,
            username: initData.user.username,
            language_code: initData.user.language_code,
            init_data: webApp.initData
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.token) {
            localStorage.setItem('token', data.token)
          }
          return true
        }
      } catch (error) {
        console.error('Telegram auth error:', error)
      }
    }
  }
  return false
}

// Fetch user profile data from backend
const fetchUserProfile = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId.value}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      userPoints.value = data.points || 0
      dailyStreak.value = data.dailyStreak || 1
      
      // Если есть сохранённый username из Telegram, используем его
      if (data.username && !window.Telegram?.WebApp?.initDataUnsafe?.user) {
        username.value = data.username
      }
    }
  } catch (error) {
    console.error('Error fetching profile:', error)
    loadLocalData()
  }
}

// Load purchases from localStorage (demo mode)
const loadPurchases = () => {
  const purchases = JSON.parse(localStorage.getItem('purchases') || '[]')
  const userPurchases = purchases.filter(p => p.userId === userId.value)
  
  totalPurchases.value = userPurchases.length
  
  // Map purchases to display format
  const productsMap = {
    1: { title: 'Встреча с разработчиком', description: 'Личная беседа и совместный созвон', price: '1 000 000', image: 'https://avatars.mds.yandex.net/i?id=c70e9491ed7d8aa4b97ea0c54f9ac501_l-4600590-images-thumbs&n=13' },
    2: { title: 'Premium статус', description: 'Уникальный значок и привилегии', price: '250 000', image: 'https://avatars.mds.yandex.net/i?id=b9781a28f26f05a36a6f877920bff765_l-5218797-images-thumbs&n=13' },
    3: { title: 'Секретный дроп', description: 'Эксклюзивный подарок от команды', price: '500 000', image: 'https://images.pravilamag.ru/upload/img_cache/d3f/d3f1546787d35fe525c3b7e593313141_ce_2000x1334x0x33_cropped_510x340.webp' },
    4: { title: 'VIP доступ', description: 'Ранний доступ ко всем функциям', price: '750 000', image: 'https://avatars.mds.yandex.net/i?id=69a97bc586facd3f7460ed03030bb224_l-5252264-images-thumbs&n=13' }
  }
  
  recentPurchases.value = userPurchases.slice(-5).reverse().map(purchase => ({
    id: purchase.productId,
    title: productsMap[purchase.productId]?.title || 'Товар',
    description: productsMap[purchase.productId]?.description || '',
    price: productsMap[purchase.productId]?.price || '0',
    image: productsMap[purchase.productId]?.image || '',
    purchaseDate: purchase.purchaseDate
  }))
}

// Update achievements based on user progress
const updateAchievements = () => {
  achievements.value[0].isUnlocked = totalPurchases.value >= 1
  achievements.value[0].current = totalPurchases.value
  
  achievements.value[1].isUnlocked = totalPurchases.value >= 5
  achievements.value[1].current = totalPurchases.value
  
  achievements.value[2].isUnlocked = userPoints.value >= 100000
  achievements.value[2].current = userPoints.value
  
  achievements.value[3].isUnlocked = dailyStreak.value >= 30
  achievements.value[3].current = dailyStreak.value
}

// Load local data
const loadLocalData = () => {
  const savedAvatar = localStorage.getItem('userAvatar')
  if (savedAvatar) userAvatar.value = savedAvatar
}

// Avatar modal functions
const openAvatarModal = () => {
  selectedAvatar.value = userAvatar.value
  showAvatarModal.value = true
}

const closeAvatarModal = () => {
  showAvatarModal.value = false
}

const selectAvatar = (avatarUrl) => {
  selectedAvatar.value = avatarUrl
}

const saveAvatar = async () => {
  userAvatar.value = selectedAvatar.value
  localStorage.setItem('userAvatar', selectedAvatar.value)
  
  // Save to backend
  try {
    await fetch(`${API_BASE_URL}/user/${userId.value}/avatar`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: JSON.stringify({ avatar: selectedAvatar.value })
    })
  } catch (error) {
    console.error('Error saving avatar:', error)
  }
  
  closeAvatarModal()
  showNotification('Аватар обновлён', 'success')
}

// Format date
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'Вчера'
  if (diffDays < 7) return `${diffDays} дня назад`
  
  return date.toLocaleDateString('ru-RU')
}

// Show notification
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

// Initialize component
onMounted(async () => {
  getTelegramUser() // Получаем данные из Telegram
  await telegramAuth() // Авторизуемся на бэкенде
  await fetchUserProfile() // Загружаем профиль
  loadPurchases() // Загружаем покупки
  updateAchievements() // Обновляем достижения
  loadLocalData() // Загружаем локальные данные
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 20px;
  color: white;
  padding-right: 0;
  
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border-radius: 32px;
  box-shadow: 
    20px 20px 40px rgba(0, 0, 0, 0.3),
    -8px -8px 16px rgba(255, 255, 255, 0.1),
    inset 2px 2px 4px rgba(255, 255, 255, 0.15),
    inset -2px -2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin: 20px;
  transition: all 0.3s ease;
}

.profile-page:hover {
  box-shadow: 
    22px 22px 44px rgba(0, 0, 0, 0.35),
    -10px -10px 20px rgba(255, 255, 255, 0.12),
    inset 3px 3px 6px rgba(255, 255, 255, 0.18),
    inset -3px -3px 6px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* Profile Header */
.profile-header {
  display: flex;
  gap: 30px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 28px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  overflow: hidden;
  border: 3px solid rgba(124, 247, 212, 0.5);
  position: relative;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-avatar-btn {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 32px;
  height: 32px;
  border-radius: 16px;
  background: rgba(124, 247, 212, 0.9);
  border: none;
  color: #1a1a2e;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.edit-avatar-btn:hover {
  transform: scale(1.1);
}

.profile-info {
  flex: 1;
}

.username {
  font-size: 28px;
  margin: 0 0 8px 0;
  font-weight: 700;
  background: linear-gradient(135deg, #fff, #7cf7d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-email {
  opacity: 0.7;
  margin-bottom: 20px;
}

.stats-row {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 12px 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #7cf7d4;
}

.stat-label {
  font-size: 12px;
  opacity: 0.7;
}

/* Section Header */
.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 22px;
  margin: 0;
  font-weight: 600;
}

.section-subtitle {
  font-size: 13px;
  opacity: 0.6;
}

/* Achievements */
.achievements-section,
.purchases-section {
  margin-bottom: 40px;
  
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.achievement-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
  opacity: 0.6;
}

.achievement-card.unlocked {
  opacity: 1;
  background: linear-gradient(135deg, rgba(124, 247, 212, 0.1), rgba(78, 205, 196, 0.05));
  border-color: rgba(124, 247, 212, 0.3);
}

.achievement-icon {
  font-size: 40px;
}

.achievement-info {
  flex: 1;
}

.achievement-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.achievement-info p {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
}

.achievement-progress {
  text-align: right;
}

.progress-bar {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: #7cf7d4;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.achievement-progress span {
  font-size: 11px;
  opacity: 0.7;
}

/* Purchases */
.purchases-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.purchase-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

.purchase-item:hover {
  transform: translateX(5px);
  background: rgba(255, 255, 255, 0.08);
}

.purchase-image {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
}

.purchase-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.purchase-details {
  flex: 1;
}

.purchase-details h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.purchase-details p {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
}

.purchase-price {
  text-align: right;
}

.price-value {
  display: block;
  font-weight: 600;
  color: #7cf7d4;
}

.purchase-date {
  font-size: 11px;
  opacity: 0.5;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 24px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.shop-link {
  display: inline-block;
  margin-top: 16px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #7cf7d4, #4ecdc4);
  border-radius: 24px;
  color: #1a1a2e;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.shop-link:hover {
  transform: scale(1.05);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border-radius: 24px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-content h3 {
  margin: 0 0 20px 0;
}

.avatar-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.avatar-option {
  cursor: pointer;
  border-radius: 50%;
  border: 3px solid transparent;
  transition: all 0.3s ease;
}

.avatar-option img {
  width: 100%;
  border-radius: 50%;
}

.avatar-option.selected {
  border-color: #7cf7d4;
  transform: scale(1.05);
}

.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn,
.save-btn {
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.save-btn {
  background: linear-gradient(135deg, #7cf7d4, #4ecdc4);
  color: #1a1a2e;
}

.cancel-btn:hover,
.save-btn:hover {
  transform: scale(1.05);
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
  z-index: 1001;
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
  
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .stats-row {
    justify-content: center;
  }
  
  .achievements-grid {
    grid-template-columns: 1fr;
  }
  
  .purchase-item {
    flex-direction: column;
    text-align: center;
  }
  
  .purchase-price {
    text-align: center;
  }
  
  .notification-toast {
    left: 20px;
    right: 20px;
    min-width: auto;
  }
}
</style>