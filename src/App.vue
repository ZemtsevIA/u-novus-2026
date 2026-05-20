<template>
  <div class="app-shell">
    <StarBackground 
      :star-count="200"
      :min-star-size="0.8"
      :max-star-size="4"
      :twinkle-speed="1"
      :twinkle-intensity="0.45"
      :flash-chance="0.025"        
      :flash-intensity="1.95"
      :comet-count="3"
      :comet-speed="5.2"
    />
    <RouterView />
  </div>
</template>

<script setup>
import StarBackground from './components/StarBackground.vue'
</script>

<style>
.app-shell {
  min-height: 100vh;
  position: relative;           
  overflow: hidden;
  
}
</style>