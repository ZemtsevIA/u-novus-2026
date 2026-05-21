<template>
  <div class="text">
    <h1>Маршрут обучения: {{ topicName }}</h1>
  </div>
  
  <div v-if="loading" class="loading">
    <div class="spinner"></div>
    <p>Загрузка маршрута...</p>
  </div>
  
  <div v-else-if="error" class="error">
    <p>❌ {{ error }}</p>
    <button @click="fetchRoadmapData" class="retry-btn">Попробовать снова</button>
  </div>
  
  <section v-else class="roadmap">
    <div class="summary">
      <p>{{ roadmapData?.roadmap?.summary }}</p>
      <div class="info">
        <span>⏱️ Примерно {{ roadmapData?.roadmap?.estimated_weeks }} недель</span>
      </div>
    </div>

    <div class="progress-section" v-if="totalSteps > 0">
      <div class="progress-info">
        <span>Прогресс обучения</span>
        <span>{{ completedStepsCount }} / {{ totalSteps }} шагов</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <div v-if="isRoadmapCompleted" class="completion-badge">
        🎉 Маршрут пройден! 🎉
      </div>
    </div>
    
    <CourseCard
      v-for="(step, index) in roadmapData?.roadmap?.steps || []"
      :key="step.step || step.course_id || index"
      :course="step"
      :side="getSideByIndex(index)"
      :user-id="telegramUserId"
      :roadmap-id="currentRoadmapId"
      @course-completed="handleCourseCompleted"
      @course-uncompleted="handleCourseUncompleted"
    />
    
    <div v-if="roadmapData?.roadmap?.career_opportunities?.length" class="career">
      <h3>Возможности после прохождения:</h3>
      <div class="career-list">
        <span v-for="career in roadmapData.roadmap.career_opportunities" :key="career">
          {{ career }}
        </span>
      </div>
    </div>
    
    <!-- Блок с вакансиями/стажировками - показывается при 100% прогрессе -->
    <div v-if="isRoadmapCompleted" class="opportunities-section">
      <div class="section-header">
        <h2>🎯 Актуальные возможности</h2>
        <p>Подобраны специально для вас на основе пройденного маршрута</p>
      </div>
      
      <!-- Загрузка -->
      <div v-if="loadingVacancies" class="loading-opportunities">
        <div class="spinner-small"></div>
        <p>Поиск актуальных вакансий и стажировок...</p>
      </div>
      
      <!-- Ошибка -->
      <div v-else-if="vacanciesError" class="error-opportunities">
        <p>⚠️ {{ vacanciesError }}</p>
        <button @click="fetchVacancies" class="retry-small-btn">Повторить поиск</button>
      </div>
      
      <!-- Вакансии -->
      <div v-else-if="vacanciesData?.results?.length" class="opportunities-list">
        <div 
          v-for="(item, idx) in vacanciesData.results" 
          :key="idx"
          class="opportunity-card"
          :class="'type-' + (item.vacancy_data.type || 'default')"
        >
          <div class="card-badge">
            <span class="badge-type">{{ getTypeLabel(item.vacancy_data.type) }}</span>
            <span class="badge-match">Совпадение: {{ Math.round(item.similarity_score * 100) }}%</span>
          </div>
          
          <h3 class="opportunity-title">{{ item.vacancy_data.title }}</h3>
          
          <div class="opportunity-meta">
            <span class="meta-company">🏢 {{ item.vacancy_data.organization || 'Не указана' }}</span>
            <span v-if="item.vacancy_data.deadline" class="meta-deadline">
              ⏰ {{ formatDeadline(item.vacancy_data.deadline) }}
            </span>
          </div>
          
          <div class="opportunity-tags" v-if="item.vacancy_data.tags?.length">
            <span v-for="tag in item.vacancy_data.tags.slice(0, 5)" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
          
          <a 
            v-if="item.vacancy_data.url"
            :href="item.vacancy_data.url" 
            target="_blank" 
            rel="noopener noreferrer"
            class="opportunity-link"
          >
            Подробнее →
          </a>
          <div v-else class="no-link">Ссылка временно недоступна</div>
        </div>
      </div>
      
      <!-- Нет результатов -->
      <div v-else-if="!loadingVacancies && !vacanciesError" class="no-opportunities">
        <p>😔 На данный момент нет актуальных предложений по вашему профилю</p>
        <p>Рекомендуем проверить позже или расширить поисковый запрос</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import CourseCard from './CourseCard.vue'

// Данные роадмапа
const roadmapData = ref(null)
const loading = ref(true)
const error = ref(null)

// Данные о вакансиях
const vacanciesData = ref(null)
const loadingVacancies = ref(false)
const vacanciesError = ref(null)

// Данные пользователя
const telegramUserId = ref('')
const currentRoadmapId = ref('')
const roadmapInfo = ref(null) // Храним информацию о роадмапе для запроса вакансий

// Прогресс
const completedSteps = ref(new Set())

// Тема роадмапа
const topicName = computed(() => {
  return roadmapData.value?.search_request?.topic || 
         roadmapData.value?.refined_search_request?.topic || 
         'Python backend'
})

// Общее количество шагов
const totalSteps = computed(() => {
  return roadmapData.value?.roadmap?.steps?.length || 0
})

// Количество пройденных шагов
const completedStepsCount = computed(() => {
  return completedSteps.value.size
})

// Процент прогресса
const progressPercentage = computed(() => {
  if (totalSteps.value === 0) return 0
  return Math.round((completedStepsCount.value / totalSteps.value) * 100)
})

// Флаг завершения роадмапа
const isRoadmapCompleted = computed(() => {
  return totalSteps.value > 0 && completedStepsCount.value === totalSteps.value
})

// Определение стороны карточки
const getSideByIndex = (index) => {
  return index % 2 === 0 ? 'right' : 'left'
}

// Тип вакансии на русском
const getTypeLabel = (type) => {
  const types = {
    'internship': 'Стажировка',
    'junior': 'Junior',
    'practice': 'Практика',
    'hackathon': 'Хакатон',
    'vacancy': 'Вакансия',
    'job': 'Вакансия'
  }
  return types[type] || 'Предложение'
}

// Форматирование дедлайна
const formatDeadline = (dateString) => {
  if (!dateString) return 'Дедлайн не указан'
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24))
    
    if (diffDays < 0) return 'Дедлайн прошёл'
    if (diffDays === 0) return 'Сегодня последний день!'
    if (diffDays === 1) return 'Остался 1 день'
    return `Осталось ${diffDays} дней`
  } catch {
    return dateString
  }
}

// Загрузка прогресса
const loadUserProgress = async () => {
  if (!telegramUserId.value || !currentRoadmapId.value) return
  
  try {
    const response = await fetch(`/api/user/progress?user_id=${telegramUserId.value}&roadmap_id=${currentRoadmapId.value}`)
    
    if (response.ok) {
      const data = await response.json()
      completedSteps.value.clear()
      data.completed_courses?.forEach(courseId => {
        completedSteps.value.add(courseId)
      })
    }
  } catch (err) {
    console.error('Ошибка загрузки прогресса:', err)
  }
}

// Сохранение прогресса
const saveProgress = async () => {
  if (!telegramUserId.value || !currentRoadmapId.value) return
  
  try {
    await fetch('/api/user/progress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: telegramUserId.value,
        roadmap_id: currentRoadmapId.value,
        completed_courses: Array.from(completedSteps.value)
      })
    })
  } catch (err) {
    console.error('Ошибка сохранения прогресса:', err)
  }
}

// Обработчики курсов
const handleCourseCompleted = async ({ courseId }) => {
  completedSteps.value.add(courseId)
  await saveProgress()
}

const handleCourseUncompleted = async ({ courseId }) => {
  completedSteps.value.delete(courseId)
  await saveProgress()
}

// Получение вакансий
const fetchVacancies = async () => {
  if (!currentRoadmapId.value) {
    console.warn('Нет ID роадмапа')
    return
  }
  
  loadingVacancies.value = true
  vacanciesError.value = null
  
  try {
    // Шаг 1: Получаем информацию о роадмапе по ID
    const roadmapResponse = await fetch(`/api/roadmaps/${currentRoadmapId.value}`)
    
    if (!roadmapResponse.ok) {
      throw new Error(`Ошибка получения роадмапа: ${roadmapResponse.status}`)
    }
    
    const roadmapInfoData = await roadmapResponse.json()
    roadmapInfo.value = roadmapInfoData
    
    // Извлекаем нужные поля
    const title = roadmapInfoData.title || topicName.value
    const topic = roadmapInfoData.topic || topicName.value
    const level = roadmapInfoData.level || 
                  roadmapData.value?.search_request?.level || 
                  roadmapData.value?.refined_search_request?.level || 
                  'Junior'
    
    // Шаг 2: Формируем поисковый контекст
    const searchContext = `${title} ${topic} уровень ${level}`
    
    console.log('Поиск вакансий по контексту:', searchContext)
    
    // Шаг 3: Запрашиваем вакансии у сервиса Паши
    const vacanciesResponse = await fetch('/api/search_vacancies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: searchContext })
    })
    
    if (!vacanciesResponse.ok) {
      throw new Error(`Ошибка поиска: ${vacanciesResponse.status}`)
    }
    
    const result = await vacanciesResponse.json()
    
    // Фильтруем результаты с низкой релевантностью (ниже 0.3)
    if (result.results && Array.isArray(result.results)) {
      result.results = result.results.filter(item => item.similarity_score > 0.3)
    }
    
    vacanciesData.value = result
    
  } catch (err) {
    console.error('Ошибка получения вакансий:', err)
    vacanciesError.value = err.message || 'Не удалось загрузить актуальные предложения'
  } finally {
    loadingVacancies.value = false
  }
}

// Следим за завершением роадмапа
watch(isRoadmapCompleted, (completed) => {
  if (completed && !vacanciesData.value && !loadingVacancies.value && !vacanciesError.value) {
    fetchVacancies()
  }
})

// Получение данных роадмапа от бэкенда
const fetchRoadmapData = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch('/api/roadmap', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    roadmapData.value = data
    
    // Генерируем или используем ID роадмапа
    currentRoadmapId.value = data.roadmap?.id || generateRoadmapId(data)
    
    // Загружаем прогресс пользователя
    if (data.roadmap?.steps && telegramUserId.value) {
      await loadUserProgress()
      
      // Добавляем флаг completed в каждый шаг
      data.roadmap.steps.forEach(step => {
        const courseId = step.course_id || step.id
        step.completed = completedSteps.value.has(courseId)
      })
    }
    
  } catch (err) {
    console.error('Ошибка загрузки данных:', err)
    error.value = err.message || 'Не удалось загрузить маршрут обучения'
    
    // Для разработки - используем mock данные
    if (import.meta.env.DEV) {
      console.warn('Используются mock данные для разработки')
      roadmapData.value = getMockData()
      error.value = null
    }
  } finally {
    loading.value = false
  }
}

// Генерация ID роадмапа
const generateRoadmapId = (data) => {
  const topic = data.search_request?.topic || 'roadmap'
  const timestamp = Date.now()
  return `${topic.toLowerCase().replace(/\s+/g, '_')}_${timestamp}`
}

// Установка Telegram User ID (из родителя)
const setTelegramUser = (userId) => {
  telegramUserId.value = userId
  if (roadmapData.value) {
    loadUserProgress()
  }
}

// Mock данные для разработки
const getMockData = () => {
  return {
    search_request: {
      topic: "Python backend",
      preferences: "FastAPI, REST API, базы данных",
      level: "Junior",
      limit: 40
    },
    refined_search_request: {
      topic: "Python backend",
      preferences: "FastAPI, REST API, базы данных",
      level: "Junior"
    },
    search_fallback_used: false,
    courses: [
      {
        id: "123456",
        title: "Python для начинающих",
        platform: "Stepik",
        level: "новичок",
        format: "курс",
        description: "Основы Python: синтаксис, структуры данных, ООП",
        url: "https://stepik.org/course/67"
      }
    ],
    roadmap: {
      id: "python_backend_mock",
      summary: "Маршрут от нуля до Junior Python Backend Developer: освоение языка, работа с базами данных, разработка REST API и контейнеризация.",
      estimated_weeks: 24,
      career_opportunities: [
        "Junior Python Developer",
        "Backend Developer",
        "Junior FastAPI Developer"
      ],
      steps: [
        {
          step: 1,
          title: "Основы Python",
          course_id: "123456",
          course_title: "Python для начинающих",
          course_url: "https://stepik.org/course/67",
          format: "курс",
          duration_hours: 40,
          skills: ["синтаксис Python", "списки", "словари", "функции", "ООП"],
          why: "Без знания базового синтаксиса Python невозможно двигаться дальше.",
          career_boost: "Позволяет претендовать на стажировку или позицию Junior Developer"
        },
        {
          step: 2,
          title: "Разработка REST API на FastAPI",
          course_id: "789012",
          course_title: "FastAPI — современный веб-фреймворк",
          course_url: "https://stepik.org/course/12345",
          format: "курс",
          duration_hours: 30,
          skills: ["FastAPI", "REST API", "PostgreSQL", "Docker"],
          why: "FastAPI — самый популярный фреймворк для backend на Python в 2024 году.",
          career_boost: "Открывает вакансии Python Backend Developer с зарплатой от 80k рублей"
        }
      ]
    }
  }
}

// Обновление поискового запроса
const updateSearchRequest = async (searchParams) => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch('/api/roadmap/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(searchParams)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    roadmapData.value = data
    
    if (telegramUserId.value) {
      await loadUserProgress()
    }
    
  } catch (err) {
    console.error('Ошибка обновления:', err)
    error.value = err.message || 'Не удалось обновить маршрут'
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp
    telegramUserId.value = tg.initDataUnsafe?.user?.id?.toString() || ''
    tg.expand()
  }
  fetchRoadmapData()
})

// Экспорт методов
defineExpose({
  setTelegramUser,
  updateSearchRequest,
  fetchVacancies
})
</script>

<style scoped>
.roadmap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding: 0 0px;
  max-width: 1200px;
  margin: 0 auto;
}

.text {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px;
}

.text h1 {
  font-family: "LoosBold", sans-serif;
  font-size: 2rem;
  background: linear-gradient(135deg, #fff, #ff05d6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.summary {
  background: rgba(30, 20, 60, 0.65);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  margin-left: 20px;
  margin-right: 20px;
  padding: 24px 32px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.summary p {
  color: white;
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.info {
  display: inline-block;
  background: linear-gradient(135deg, rgba(255, 5, 214, 0.2), rgba(255, 2, 125, 0.2));
  padding: 8px 16px;
  border-radius: 50px;
  color: #ff05d6;
  font-weight: bold;
}

.progress-section {
  margin: 0 20px;
  padding: 20px 24px;
  background: rgba(30, 20, 60, 0.65);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  color: white;
  margin-bottom: 12px;
  font-weight: 500;
}

.progress-bar {
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff05d6, #2af4ff);
  border-radius: 10px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(255, 5, 214, 0.5);
}

.completion-badge {
  margin-top: 16px;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  background: linear-gradient(135deg, #ff05d6, #2af4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.02); }
}

.career {
  margin-top: 20px;
  padding: 24px 32px;
  margin-left: 20px;
  margin-right: 20px;
  background: rgba(30, 20, 60, 0.65);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.career h3 {
  color: white;
  margin-bottom: 16px;
}

.career-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.career-list span {
  background: linear-gradient(135deg, rgba(46, 194, 246, 0.2), rgba(42, 244, 255, 0.2));
  padding: 8px 16px;
  border-radius: 50px;
  color: #2af4ff;
  font-weight: 500;
}

/* Блок возможностей (вакансии/стажировки) */
.opportunities-section {
  margin-top: 40px;
  margin-bottom: 40px;
  margin-left: 20px;
  margin-right: 20px;
  padding: 32px;
  background: linear-gradient(135deg, rgba(30, 20, 60, 0.8), rgba(20, 10, 40, 0.9));
  backdrop-filter: blur(10px);
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-header {
  text-align: center;
  margin-bottom: 32px;
}

.section-header h2 {
  font-size: 1.8rem;
  background: linear-gradient(135deg, #fff, #ff05d6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.section-header p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.opportunities-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.opportunity-card {
  background: rgba(15, 10, 35, 0.7);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s ease;
  border-left: 4px solid;
}

.opportunity-card.type-internship {
  border-left-color: #2af4ff;
}
.opportunity-card.type-junior {
  border-left-color: #ff05d6;
}
.opportunity-card.type-practice {
  border-left-color: #4caf50;
}
.opportunity-card.type-hackathon {
  border-left-color: #ff9800;
}
.opportunity-card.type-default {
  border-left-color: #9c27b0;
}

.opportunity-card:hover {
  transform: translateX(8px);
  background: rgba(25, 15, 50, 0.8);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.card-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}

.badge-type {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-internship .badge-type {
  background: rgba(42, 244, 255, 0.2);
  color: #2af4ff;
}
.type-junior .badge-type {
  background: rgba(255, 5, 214, 0.2);
  color: #ff05d6;
}
.type-practice .badge-type {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}
.type-hackathon .badge-type {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.badge-match {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  color: #ffd700;
  font-weight: 500;
}

.opportunity-title {
  font-size: 1.25rem;
  color: white;
  margin-bottom: 12px;
  font-weight: 600;
  line-height: 1.4;
}

.opportunity-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-company, .meta-deadline {
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.opportunity-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.tag {
  background: rgba(255, 255, 255, 0.08);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s;
}

.tag:hover {
  background: rgba(255, 5, 214, 0.2);
  color: #ff05d6;
}

.opportunity-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #ff05d6, #ff027d);
  padding: 8px 20px;
  border-radius: 30px;
  color: white;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.opportunity-link:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(255, 5, 214, 0.3);
}

.no-link {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.8rem;
  font-style: italic;
}

.loading-opportunities, .error-opportunities, .no-opportunities {
  text-align: center;
  padding: 40px;
}

.loading-opportunities p, .no-opportunities p {
  color: rgba(255, 255, 255, 0.7);
  margin-top: 12px;
}

.error-opportunities p {
  color: #ff6b6b;
  margin-bottom: 16px;
}

.spinner-small {
  width: 40px;
  height: 40px;
  margin: 0 auto;
  border: 3px solid rgba(255, 5, 214, 0.2);
  border-top: 3px solid #ff05d6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.retry-small-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 20px;
  border-radius: 30px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.retry-small-btn:hover {
  background: rgba(255, 5, 214, 0.3);
  border-color: #ff05d6;
}

.loading, .error {
  text-align: center;
  color: white;
  padding: 40px;
  font-size: 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.error {
  color: #ff027d;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 5, 214, 0.3);
  border-top: 3px solid #ff05d6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: linear-gradient(135deg, #ff05d6, #ff027d);
  border: none;
  padding: 10px 24px;
  border-radius: 30px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.retry-btn:hover {
  transform: scale(1.05);
}

/* Стили для карточек курсов */
.roadmap :deep(.timeline-item) {
  width: auto;
  max-width: 70%;
  min-width: 69%;
  display: flex;
  flex-wrap: wrap;
}

.roadmap :deep(.timeline-item.right-aligned) {
  justify-content: flex-end;
  margin-left: auto;
  margin-right: 0;
}

.roadmap :deep(.timeline-item.left-aligned) {
  justify-content: flex-start;
  margin-left: 0;
  margin-right: auto;
}

@font-face {
  font-family: 'LoosBold';
  src: url('./assets/fonts/LoosExtraWide-Bold.ttf') format('truetype');
  font-weight: 400;
}

@media (max-width: 768px) {
  .roadmap :deep(.timeline-item) {
    max-width: 90%;
    min-width: 90%;
  }
  
  .text h1 {
    font-size: 1.5rem;
  }
  
  .summary, .career, .progress-section, .opportunities-section {
    padding: 16px 20px;
  }
  
  .section-header h2 {
    font-size: 1.3rem;
  }
  
  .opportunity-title {
    font-size: 1rem;
  }
  
  .card-badge {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>