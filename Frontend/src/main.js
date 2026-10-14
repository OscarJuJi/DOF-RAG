import { createApp } from 'vue';
import axios from 'axios';
import 'boxicons/css/boxicons.min.css';

import App from './App.vue';
import router from './router';
import store from './store';

axios.defaults.timeout = 600000;
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.url?.startsWith('/')) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

createApp(App).use(store).use(router).mount('#app');
