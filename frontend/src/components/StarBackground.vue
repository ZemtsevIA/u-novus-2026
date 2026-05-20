<template>
  <canvas
    ref="canvas"
    class="star-background"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  // === Звёзды ===
  starCount: { type: Number, default: 850 },
  minStarSize: { type: Number, default: 0.8 },
  maxStarSize: { type: Number, default: 2.8 },

  // === Мерцание ===
  twinkleSpeed: { type: Number, default: 1 },      // 0.5 = медленно, 2 = быстро
  twinkleIntensity: { type: Number, default: 0.4 }, // сила обычного мерцания

  // === Случайные вспышки ===
  flashChance: { type: Number, default: 0.008 },    // вероятность вспышки за кадр (0.003 = редко, 0.015 = часто)
  flashIntensity: { type: Number, default: 0.9 },   // насколько ярко вспыхивает (0.6–1.2)
  flashDuration: { type: Number, default: 35 },     // длительность вспышки в кадрах

  // === Кометы ===
  cometCount: { type: Number, default: 3 },
  cometSpeed: { type: Number, default: 4.8 },
  cometLength: { type: Number, default: 130 }
})

const canvas = ref(null)
let animationFrame = null
let stars = []
let comets = []
let ctx = null

class Star {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.size = Math.random() * (props.maxStarSize - props.minStarSize) + props.minStarSize
    this.baseOpacity = Math.random() * 0.75 + 0.25
    this.twinkleSpeed = (Math.random() * 0.018 + 0.009) * props.twinkleSpeed

    // Для вспышек
    this.flashProgress = 0
    this.flashDuration = props.flashDuration
  }

  update() {
    // Обычное мерцание
    const twinkle = Math.sin(Date.now() * this.twinkleSpeed) * props.twinkleIntensity
    this.opacity = this.baseOpacity + twinkle

    // Случайная вспышка
    if (this.flashProgress <= 0 && Math.random() < props.flashChance) {
      this.flashProgress = this.flashDuration
    }

    if (this.flashProgress > 0) {
      const flash = Math.sin((this.flashProgress / this.flashDuration) * Math.PI) * props.flashIntensity
      this.opacity += flash
      this.flashProgress--
    }

    // Ограничиваем opacity
    this.opacity = Math.max(0.1, Math.min(1, this.opacity))
  }

  draw() {
    ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`
    ctx.fillRect(this.x, this.y, this.size, this.size)

    // Дополнительный блик во время сильной вспышки
    if (this.flashProgress > this.flashDuration * 0.4) {
      ctx.fillStyle = `rgba(255, 245, 220, ${this.opacity * 0.6})`
      ctx.fillRect(this.x - 0.5, this.y - 0.5, this.size + 1, this.size + 1)
    }
  }
}

class Comet {
  constructor() {
    this.reset()
  }

  reset() {
    this.x = Math.random() * window.innerWidth * 1.4 - 400
    this.y = Math.random() * window.innerHeight * 0.65 - 80
    this.length = props.cometLength + Math.random() * 80
    this.speed = props.cometSpeed + Math.random() * 4
    this.opacity = Math.random() * 0.7 + 0.75
  }

  update() {
    this.x += this.speed
    this.y += this.speed * 0.27

    if (this.x > window.innerWidth + 400) {
      this.reset()
    }
  }

  draw() {
    const gradient = ctx.createLinearGradient(
      this.x, this.y,
      this.x - this.length, this.y - this.length * 0.38
    )
    gradient.addColorStop(0, `rgba(235, 245, 255, ${this.opacity})`)
    gradient.addColorStop(1, 'rgba(200, 230, 255, 0)')

    ctx.strokeStyle = gradient
    ctx.lineWidth = 3.2
    ctx.lineCap = 'round'
    ctx.beginPath()
    ctx.moveTo(this.x, this.y)
    ctx.lineTo(this.x - this.length, this.y - this.length * 0.38)
    ctx.stroke()

    // Головка
    ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity + 0.25})`
    ctx.beginPath()
    ctx.arc(this.x, this.y, 3.8, 0, Math.PI * 2)
    ctx.fill()
  }
}

const resizeCanvas = () => {
  if (!canvas.value) return
  canvas.value.width = window.innerWidth
  canvas.value.height = window.innerHeight
}

const init = () => {
  const c = canvas.value
  if (!c) return

  ctx = c.getContext('2d', { alpha: true })

  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)

  stars = Array.from({ length: props.starCount }, () => new Star())
  comets = Array.from({ length: props.cometCount }, () => new Comet())

  const animate = () => {
    ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)

    stars.forEach(star => {
      star.update()
      star.draw()
    })

    comets.forEach(comet => {
      comet.update()
      comet.draw()
    })

    animationFrame = requestAnimationFrame(animate)
  }

  animate()
}

onMounted(init)

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame)
  window.removeEventListener('resize', resizeCanvas)
})
</script>

<style scoped>
.star-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: radial-gradient(
    circle at 50% 25%,
    #2a1b5f 0%,
    #0f0829 35%,
    #05020f 65%,
    #000 100%
  );
  pointer-events: none;
}
</style>