import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../views/HomePage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import OnboardingPage from '../views/OnboardingPage.vue'

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
    path: '/onboarding',
    component: OnboardingPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router