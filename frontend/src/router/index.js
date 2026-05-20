import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../views/HomePage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import LiderboardingPage from '../views/LiderboardingPage.vue'
import ShopPage from '../views/ShopPage.vue'

const routes = [
  {
    path: '/',
    component: HomePage
  },
  {
    path: '/profile',
    component: ProfilePage
  },
  {
    path: '/Liderboarding',
    component: LiderboardingPage
  },
  {
    path: '/Shop',
    component: ShopPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router