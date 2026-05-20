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
    
    <CourseCard
      v-for="(step, index) in roadmapData?.roadmap?.steps || []"
      :key="step.step || step.course_id || index"
      :course="step"
      :side="getSideByIndex(index)"
    />
    
    <div v-if="roadmapData?.roadmap?.career_opportunities?.length" class="career">
      <h3>Возможности после прохождения:</h3>
      <div class="career-list">
        <span v-for="career in roadmapData.roadmap.career_opportunities" :key="career">
          {{ career }}
        </span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CourseCard from './CourseCard.vue'

const roadmapData = ref(null)
const loading = ref(true)
const error = ref(null)

// Вычисляемое свойство для отображения темы
const topicName = computed(() => {
  return roadmapData.value?.search_request?.topic || 
         roadmapData.value?.refined_search_request?.topic || 
         'Python backend'
})

// Функция для определения стороны карточки
const getSideByIndex = (index) => {
  // Четные индексы (0, 2, 4...) - правая сторона
  // Нечетные индексы (1, 3, 5...) - левая сторона
  return index % 2 === 0 ? 'right' : 'left'
}

// Функция для получения данных от backend
const fetchRoadmapData = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Вариант 1: GET запрос к API
    const response = await fetch('/api/roadmap', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    roadmapData.value = data
    
    
    
  } catch (err) {
    console.error('Ошибка при загрузке данных:', err)
    error.value = err.message || 'Не удалось загрузить маршрут обучения'
    
    // Для разработки: используем mock данные при ошибке
    if (import.meta.env.DEV) {
      console.warn('Используются mock данные для разработки')
      roadmapData.value = getMockData()
      error.value = null
    }
  } finally {
    loading.value = false
  }
}

// Mock данные для тестирования (только для разработки)
const getMockData = () => {
  return {
    search_request: {
      topic: "Python backend",
      preferences: "FastAPI, REST API, базы данных",
      level: "",
      limit: 40
    },
    refined_search_request: {
      topic: "Python backend",
      preferences: "FastAPI, REST API, базы данных",
      level: ""
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

// Функция для обновления данных (если нужно изменить поисковый запрос)
const updateSearchRequest = async (searchParams) => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch('/api/roadmap/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchParams)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    roadmapData.value = data
    
  } catch (err) {
    console.error('Ошибка при обновлении данных:', err)
    error.value = err.message || 'Не удалось обновить маршрут'
  } finally {
    loading.value = false
  }
}

// Загружаем данные при монтировании компонента
onMounted(() => {
  fetchRoadmapData()
})

// Для отладки - выводим данные в консоль
// watch(roadmapData, (newData) => {
//   console.log('Roadmap data updated:', newData)
// })
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

.career {
  margin-top: 40px;
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

/* Стили для карточек */
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
  
  .summary, .career {
    padding: 16px 20px;
  }
}
</style>