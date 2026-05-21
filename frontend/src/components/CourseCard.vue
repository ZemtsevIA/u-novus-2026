<template>
  <div class="timeline-item" :class="alignmentClass">
    <div class="card" :class="side">
      <div class="step-number">Шаг {{ course.step }}</div>
      
      <div class="icon">
        {{ getIconForCourse(course.title) }}
      </div>

      <div class="content">
        <div class="header-with-completion">
          <h3>{{ course.title }}</h3>
        </div>
        
        <p class="description">{{ course.course_title || course.title }}</p>
        
        <div class="meta">
          <span class="badge" v-if="course.format">📚 {{ course.format }}</span>
          <span class="badge" v-if="course.duration_hours">⏱️ {{ course.duration_hours }} часов</span>
        </div>
        
        <div class="skills" v-if="course.skills && course.skills.length">
          <strong>Навыки:</strong>
          <div class="skill-list">
            <span v-for="skill in course.skills.slice(0, 4)" :key="skill" class="skill">
              {{ skill }}
            </span>
            <span v-if="course.skills.length > 4" class="skill more">
              +{{ course.skills.length - 4 }}
            </span>
          </div>
        </div>
        
        <p class="why" v-if="course.why">
          <strong>Почему это важно:</strong> {{ course.why }}
        </p>
        
        <p class="career-boost" v-if="course.career_boost">
          🎯 {{ course.career_boost }}
        </p>
        
        <a 
          v-if="course.course_url" 
          :href="course.course_url" 
          target="_blank" 
          class="course-link"
        >
          Перейти к курсу →
        </a>
      </div>
      
      <button 
        @click="toggleComplete" 
        class="complete-btn"
        :class="{ completed: isCompleted }"
        :disabled="completionLoading"
      >
        <span class="btn-content">
          <svg v-if="isCompleted" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <div v-else-if="completionLoading" class="loading-spinner-small"></div>
          <span v-else class="unchecked-icon">○</span>
          <span class="btn-text">
            {{ completionLoading ? 'Обработка...' : (isCompleted ? 'Пройдено' : 'Отметить пройденным') }}
          </span>
        </span>
      </button>
    </div>
  </div>

  <!-- Кастомное уведомление -->
  <Teleport to="body">
    <Transition name="notification">
      <div v-if="notification.visible" class="custom-notification" :class="notification.type">
        <div class="notification-icon">
          <span v-if="notification.type === 'success'">🎉</span>
          <span v-else-if="notification.type === 'error'">⚠️</span>
          <span v-else-if="notification.type === 'points'">⭐</span>
          <span v-else>ℹ️</span>
        </div>
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.message }}</div>
          <div v-if="notification.pointsEarned" class="notification-points">
            +{{ notification.pointsEarned }} баллов!
          </div>
        </div>
        <button class="notification-close" @click="closeNotification">✕</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  course: Object,
  side: String,
  userId: String, // Telegram user ID
  roadmapId: String // ID текущего роадмапа
})

const emit = defineEmits(['course-completed', 'course-uncompleted', 'points-updated'])

const isCompleted = ref(props.course.completed || false)
const completionLoading = ref(false)

// Состояние уведомления
const notification = ref({
  visible: false,
  type: 'success',
  title: '',
  message: '',
  pointsEarned: 0
})

let notificationTimeout = null

// Показ уведомления
const showNotification = (type, title, message, pointsEarned = 0) => {
  // Очищаем предыдущий таймаут
  if (notificationTimeout) clearTimeout(notificationTimeout)
  
  notification.value = {
    visible: true,
    type,
    title,
    message,
    pointsEarned
  }
  
  // Автоматически скрываем через 4 секунды
  notificationTimeout = setTimeout(() => {
    closeNotification()
  }, 4000)
}

// Закрытие уведомления
const closeNotification = () => {
  notification.value.visible = false
  if (notificationTimeout) {
    clearTimeout(notificationTimeout)
    notificationTimeout = null
  }
}

// Вычисляем класс для выравнивания родительского контейнера
const alignmentClass = computed(() => {
  return props.side === 'right' ? 'right-aligned' : 'left-aligned'
})

// Функция для выбора иконки на основе названия курса
const getIconForCourse = (title) => {
  if (!title) return '🚀'
  
  const hash = getStringHash(title)
  
  const neutralIcons = [
    '📚', '📖', '🎓', '💻', '⌨️', '🖥️', '💾', '📀', '💿', '🔧',
    '⚙️', '🔨', '🛠️', '🎯', '💡', '⭐', '🌟', '✨', '⚡', '🔥',
    '💎', '🔮', '🎨', '🖌️', '✏️', '📏', '📐', '🧮', '🎲', '🎯',
    '🏆', '🎖️', '🏅', '📊', '📈', '📉', '🗄️', '📁', '📂', '🔒',
    '🔐', '🛡️', '🌐', '☁️', '💨', '🌈', '🌍', '🌎', '🌏', '📱',
    '📲', '🤳', '🖱️', '🖨️', '📟', '☎️', '📞', '✉️', '📧', '💬'
  ]
  
  const index = Math.abs(hash) % neutralIcons.length
  return neutralIcons[index]
}

const getStringHash = (str) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return hash
}

// Расчёт баллов за курс (можно настроить динамически)
const getPointsForCourse = () => {
  // Базовая стоимость курса
  let points = 100
  
  // Бонус за продолжительность (до +100)
  if (props.course.duration_hours) {
    points += Math.min(props.course.duration_hours, 100)
  }
  
  // Бонус за количество навыков (до +50)
  if (props.course.skills?.length) {
    points += Math.min(props.course.skills.length * 5, 50)
  }
  
  // Бонус за формат (практика даёт больше)
  if (props.course.format?.toLowerCase().includes('практик')) {
    points += 30
  }
  
  return points
}

// Основная функция отметки/снятия отметки о прохождении курса
const toggleComplete = async () => {
  if (completionLoading.value) return
  
  completionLoading.value = true
  
  const newStatus = !isCompleted.value
  const pointsEarned = getPointsForCourse()
  
  try {
    const endpoint = newStatus ? '/api/courses/complete' : '/api/courses/uncomplete'
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: props.userId,
        roadmap_id: props.roadmapId,
        course_id: props.course.course_id || props.course.id,
        step: props.course.step,
        course_title: props.course.title,
        points: newStatus ? pointsEarned : -pointsEarned,
        completed_at: new Date().toISOString()
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    isCompleted.value = newStatus
    
    // Показываем красивое уведомление
    if (newStatus) {
      // Поздравление с прохождением курса
      const congratulationsMessages = [
        `🎊 Поздравляем! Вы успешно освоили курс "${props.course.title}"!`,
        `🌟 Отлично! "${props.course.title}" — ещё один шаг к вашей цели!`,
        `💪 Крутой прогресс! Курс "${props.course.title}" пройден!`,
        `🎯 Ещё одна победа! "${props.course.title}" добавлен в копилку знаний!`,
        `🚀 Вы на шаг ближе к карьере мечты! "${props.course.title}" пройден!`
      ]
      const randomMessage = congratulationsMessages[Math.floor(Math.random() * congratulationsMessages.length)]
      
      showNotification(
        'points',
        '🎉 Курс пройден! 🎉',
        randomMessage,
        pointsEarned
      )
      
      emit('course-completed', {
        courseId: props.course.course_id || props.course.id,
        step: props.course.step,
        points: pointsEarned
      })
    } else {
      // Уведомление при отмене
      showNotification(
        'warning',
        'Отметка снята',
        `Вы сняли отметку с курса "${props.course.title}". Баллы будут списаны.`,
        0
      )
      
      emit('course-uncompleted', {
        courseId: props.course.course_id || props.course.id,
        step: props.course.step,
        points: -pointsEarned
      })
    }
    
    // Эмитим событие об обновлении баллов для родителя
    emit('points-updated', {
      userId: props.userId,
      change: newStatus ? pointsEarned : -pointsEarned,
      total: result.total_points || 0
    })
    
  } catch (err) {
    console.error('Ошибка при сохранении прогресса:', err)
    
    // Показываем уведомление об ошибке
    showNotification(
      'error',
      '❌ Ошибка',
      `Не удалось ${newStatus ? 'отметить' : 'снять отметку'} курс. Попробуйте позже.`,
      0
    )
  } finally {
    completionLoading.value = false
  }
}

// Следим за изменением статуса извне
watch(() => props.course.completed, (newVal) => {
  if (newVal !== undefined) {
    isCompleted.value = newVal
  }
})
</script>

<style scoped>
.card {
  position: relative;
  overflow: hidden;
  padding: 28px 32px;
  width: 100%;
  color: white;
  box-sizing: border-box;
  background: rgba(30, 20, 60, 0.65);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transform: translateY(0);
  transition: 
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 10px 30px -10px rgba(0, 0, 0, 0.5),
    0 0 15px rgba(255, 255, 255, 0.05);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.card {
  animation: float 9s ease-in-out infinite;
}

.card::before {
  content: "";
  position: absolute;
  inset: -3px;
  z-index: -1;
  filter: blur(1px);
  opacity: 0.75;
  transition: opacity 0.4s ease;
}

.card.right {
  border-radius: 50px 0 0 50px;
  background: linear-gradient(
    107.95deg,
    rgba(255, 5, 214, 0.25) 19.67%,
    rgba(255, 2, 125, 0.22) 86.89%
  ), rgba(28, 18, 55, 0.88);
  box-shadow: 
    0 0 40px rgba(255, 5, 214, 0.5),
    0 0 70px rgba(255, 2, 125, 0.35),
    0 15px 45px rgba(0, 0, 0, 0.5);
}

.card.right::before {
  background: linear-gradient(107.95deg, #ff05d6, #ff027d);
}

.card.left {
  border-radius: 0 50px 50px 0;
  background: linear-gradient(
    119.4deg,
    rgba(46, 194, 246, 0.22) 28.97%,
    rgba(42, 244, 255, 0.18) 81.83%
  ), rgba(28, 18, 55, 0.88);
  box-shadow: 
    0 0 40px rgba(46, 194, 246, 0.5),
    0 0 70px rgba(42, 244, 255, 0.35),
    0 15px 45px rgba(0, 0, 0, 0.5);
}

.card.left::before {
  background: linear-gradient(119.4deg, #2ec2f6, #2af4ff);
}

.step-number {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: inline-block;
}

.header-with-completion {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.header-with-completion h3 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 700;
  flex: 1;
}

.complete-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 30px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  min-width: 160px;
  margin-top: 10px;
}

.complete-btn:hover:not(:disabled) {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.2);
}

.complete-btn.completed {
  background: linear-gradient(135deg, rgba(0, 255, 100, 0.2), rgba(0, 200, 100, 0.2));
  border-color: #00ff66;
  box-shadow: 0 0 15px rgba(0, 255, 100, 0.3);
}

.complete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: white;
}

.check-icon {
  width: 18px;
  height: 18px;
}

.unchecked-icon {
  font-size: 20px;
  line-height: 1;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-text {
  font-weight: 500;
}

.description {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.meta {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
}

.skills {
  margin-bottom: 16px;
}

.skill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.skill {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
}

.skill.more {
  background: rgba(255, 5, 214, 0.3);
}

.why, .career-boost {
  margin: 12px 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

.career-boost {
  color: #ffd700;
  padding: 8px 12px;
  background: rgba(255, 215, 0, 0.1);
  border-radius: 10px;
}

.course-link {
  display: inline-block;
  margin-top: 16px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #ff05d6, #ff027d);
  border-radius: 30px;
  color: white;
  text-decoration: none;
  font-weight: bold;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.course-link:hover {
  transform: translateX(5px);
  box-shadow: 0 5px 15px rgba(255, 5, 214, 0.4);
}

/* Стили кастомного уведомления */
.custom-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  max-width: 380px;
  background: linear-gradient(135deg, rgba(30, 20, 60, 0.98), rgba(20, 10, 40, 0.98));
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 16px 20px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  z-index: 10000;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 5, 214, 0.3);
  animation: slideInRight 0.4s ease-out;
}

.custom-notification.success {
  border-left: 4px solid #00ff66;
}

.custom-notification.points {
  border-left: 4px solid #ffd700;
  background: linear-gradient(135deg, rgba(30, 20, 60, 0.98), rgba(255, 215, 0, 0.1));
}

.custom-notification.error {
  border-left: 4px solid #ff4444;
}

.custom-notification.warning {
  border-left: 4px solid #ff9800;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.notification-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: bold;
  font-size: 1rem;
  margin-bottom: 4px;
  color: white;
}

.notification-message {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.notification-points {
  margin-top: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  color: #ffd700;
  display: inline-block;
  padding: 2px 10px;
  background: rgba(255, 215, 0, 0.2);
  border-radius: 20px;
}

.notification-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  transition: color 0.2s;
  flex-shrink: 0;
}

.notification-close:hover {
  color: white;
}

/* Анимация уведомления при закрытии */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

@media (max-width: 768px) {
  .header-with-completion {
    flex-direction: column;
  }
  
  .complete-btn {
    width: 100%;
    min-width: auto;
  }
  
  .header-with-completion h3 {
    font-size: 1.3rem;
  }
  
  .custom-notification {
    bottom: 20px;
    right: 20px;
    left: 20px;
    max-width: none;
  }
}
</style>