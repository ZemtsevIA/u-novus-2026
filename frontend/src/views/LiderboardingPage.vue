<template>
  <AppHeader />

  <div class="leaderboard-page">
    <div class="header">
      <h1>Наши чемпионы</h1>
      
    </div>

    <!-- 🏆 PODIUM -->
    <div class="podium">
      <!-- 2 место -->
      <div class="podium-card second">
        <div class="avatar">M</div>
        <h3>Maria Blade</h3>
        <span>2980</span>
        <div class="place">🥈 2</div>
      </div>

      <!-- 1 место -->
      <div class="podium-card first">
        <div class="avatar big">A</div>
        <h3>Alex Storm</h3>
        <span>3200</span>
        <div class="place">🥇 1</div>
      </div>

      <!-- 3 место -->
      <div class="podium-card third">
        <div class="avatar">J</div>
        <h3>John Peak</h3>
        <span>2750</span>
        <div class="place">🥉 3</div>
      </div>
    </div>

    <!-- 📊 TABLE -->
    <div class="board">
      <div class="row head">
        <span>#</span>
        <span>Игрок</span>
        <span>Очки</span>
        
      </div>

      <div
        v-for="(user, index) in users"
        :key="user.id"
        class="row"
      >
        <span class="rank">{{ index + 4 }}</span>

        <div class="player">
          <div class="avatar">{{ user.name[0] }}</div>
          <span>{{ user.name }}</span>
        </div>

        <span class="score">{{ user.points }}</span>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import AppHeader from '../components/AppHeader.vue'

const users = [
  { id: 4, name: 'Neo Fox', points: 2400, wins: 30 },
]
</script>

<style scoped>
.leaderboard-page {
  min-height: 100vh;
  padding: 40px 20px;
  color: #fff;

  display: flex;
  flex-direction: column;
  

  
}

/* HEADER */
.header {
  text-align: center;
  margin-bottom: 20px;
}

/* 🏆 PODIUM */
.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 20px;

  margin: 30px 0 50px;
}

.podium-card {
  width: 160px;
  padding: 20px;

  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);

  border-radius: 18px;
  text-align: center;

  transition: 0.3s ease;
}

.podium-card h3{
  margin-bottom: 4px;
}

.podium-card:hover {
  transform: translateY(-5px);
}

/* 1 место — центр и выше */
.first {
  transform: scale(1.1);
  background: rgba(255, 215, 0, 0.12);
  border-color: rgba(255, 215, 0, 0.4);
}

/* 2 и 3 */
.second {
  transform: translateY(15px);
}

.third {
  transform: translateY(25px);
}

/* avatars */
.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;

  display: flex;
  align-items: center;
  justify-content: center;

  margin: 0 auto 10px;

  background: linear-gradient(135deg, #6a11cb, #2575fc);
  font-weight: 700;
}

.avatar.big {
  width: 70px;
  height: 70px;
  font-size: 22px;
}

/* place badge */
.place {
  margin-top: 10px;
  font-size: 18px;
}

/* TABLE */
.board {
  width: 100%;
  max-width: 900px;

  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(16px);

  border-radius: 20px;
  overflow: hidden;
}

.row {
  display: flex;
  grid-template-columns: 60px 1fr 120px 120px;
  padding: 16px 20px;
  align-items: center;
  justify-content: space-between;

  transition: 0.2s ease;
}

.row:not(.head):hover {
  background: rgba(255, 255, 255, 0.06);
}

.head {
  font-size: 12px;
  opacity: 0.6;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.rank {
  opacity: 0.7;
}

.player {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score {
  color: #7df9ff;
  font-weight: 600;
}

.wins {
  color: #ffd36e;
  font-weight: 600;
}
</style>