import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', component: () => import('../components/LoginView.vue') },
  {
    path: '/notification-view',
    component: () => import('../components/NotificationView.vue'),
  },
  {
    path: '/forgetpassword',
    component: () => import('../components/ForgotPassword.vue'),
  },
  {
    path: '/verificate-code',
    component: () => import('../components/GetCode.vue'),
  },
  {
    path: '/changepassword',
    component: () => import('../components/ChangePassword.vue'),
  },
  {
    path: '/consult-view',
    component: () => import('../components/ConsultasView.vue'),
  },
  {
    path: '/resumen-view',
    component: () => import('../components/ResumenView.vue'),
  },
  {
    path: '/employees-view',
    component: () => import('../components/EmpleadosView.vue'),
  },
  {
    path: '/new-employee',
    component: () => import('../components/NewUser.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes,
});

router.beforeEach((to) => {
  if (
    to.path === '/verificate-code' &&
    !sessionStorage.getItem('visitedForgotPassword')
  ) {
    return '/';
  }

  if (
    to.path === '/changepassword' &&
    !sessionStorage.getItem('visitedVerificationCode')
  ) {
    return '/';
  }

  return true;
});

router.afterEach((to) => {
  if (to.path === '/forgetpassword') {
    sessionStorage.setItem('visitedForgotPassword', 'true');
  }

  if (to.path === '/verificate-code') {
    sessionStorage.setItem('visitedVerificationCode', 'true');
  }
});

export default router;
