<template>
  <header class="header">
    <div class="logo">
      <img class="logo-img" src="/src/assets/logo.png" alt="logo">
    </div>
    
    
    <button class="menu-btn">
      <span></span>
      <span></span>
      <span></span>
    </button>
  </header>
</template>

<style scoped>
.header {
  
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: 'Times New Roman', Times, serif;
  width: 100%;
  padding: 3vh 20px;
}
.logo{
  
  display: block;
  height: 100%;          /* Логотип займёт всю высоту шапки */
  width: auto;
  max-height: 3%;
}
.logo img {
  height: 100%;          /* Сама картинка тоже на всю высоту */
  width: auto;
  object-fit: contain;   /* Сохраняет пропорции, не обрезая */
  max-height: 60px;
}
/* Кнопка меню */
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

/* Полоски */
.menu-btn span {
  width: 28px;
  height: 4px;
  border-radius: 10px;
  background: #ff00b7;

  box-shadow:
    0 0 6px #ff00b7,
    0 0 12px rgba(255, 0, 183, 0.8);

  transition: 0.25s ease;
}

/* Hover эффект */
.menu-btn:hover {
  transform: scale(1.05);
  box-shadow:
    inset 0 0 14px rgba(255, 0, 183, 0.15),
    0 0 20px rgba(255, 0, 183, 0.3);
}

.menu-btn:hover span {
  background: #ff33c8;
}
</style>