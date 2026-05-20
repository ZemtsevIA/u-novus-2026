<template>
  <div class="timeline-item" :class="alignmentClass">
    <div class="card" :class="side">
      <div class="step-number">Шаг {{ course.step }}</div>
      
      <div class="icon">
        {{ getIconForCourse(course.title) }}
      </div>

      <div class="content">
        <h3>{{ course.title }}</h3>
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
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  course: Object,
  side: String
})

// Вычисляем класс для выравнивания родительского контейнера
const alignmentClass = computed(() => {
  return props.side === 'right' ? 'right-aligned' : 'left-aligned'
})

// Функция для выбора иконки на основе названия курса
const getIconForCourse = (title) => {
  if (!title) return '🚀'
  if (title.toLowerCase().includes('python')) return '🐍'
  if (title.toLowerCase().includes('fastapi')) return '⚡'
  if (title.toLowerCase().includes('sql') || title.toLowerCase().includes('баз')) return '🗄️'
  if (title.toLowerCase().includes('docker')) return '🐳'
  if (title.toLowerCase().includes('git')) return '📦'
  return '🚀'
}
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

/* Анимация парения */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.card {
  animation: float 9s ease-in-out infinite;
}

/* Общая неоновая обводка */
.card::before {
  content: "";
  position: absolute;
  inset: -3px;
  z-index: -1;
  filter: blur(1px);
  opacity: 0.75;
  transition: opacity 0.4s ease;
}

/* Правая карточка */
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

/* Левая карточка */
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

.content h3 {
  margin: 0 0 8px 0;
  font-size: 1.6rem;
  font-weight: 700;
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
</style>