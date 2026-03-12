import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '../composables/useStore'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('../pages/LandingPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/documents',
    name: 'documents',
    component: () => import('../pages/DocumentsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('../pages/UploadPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../pages/AdminPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const { isAuthenticated, isAdmin, sessionReady } = useStore()

  await sessionReady

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return '/'
  }
  if (to.meta.requiresAdmin && !isAdmin.value) {
    return '/documents'
  }
  if (to.meta.guest && isAuthenticated.value) {
    return '/documents'
  }
})

export default router
