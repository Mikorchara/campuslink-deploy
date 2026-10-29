import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { pinia, useUserStore } from './stores/user';
import './styles/main.css';
import './styles/account.css';

const app = createApp(App);

app.use(pinia);
window.addEventListener('session-expired', () => {
  useUserStore(pinia).logout();
  const current = router.currentRoute.value;
  if (current.meta.requiresAuth) {
    void router.replace({ path: '/login', query: { redirect: current.fullPath, reason: '登录已过期，请重新登录' } });
  }
});
app.use(router);
app.mount('#app');
