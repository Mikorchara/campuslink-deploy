import { createPinia, defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getCurrentUser, login as loginRequest } from '../api/auth';
import { errorMessage } from '../api/request';
import type { UserProfile } from '../types';

export const pinia = createPinia();

export const useUserStore = defineStore('user', () => {
  const savedToken = localStorage.getItem('token');
  // Discard tokens produced by the old prototype instead of treating them as a session.
  if (savedToken?.startsWith('mock_')) localStorage.removeItem('token');
  const token = ref(localStorage.getItem('token'));
  const user = ref<UserProfile | null>(null);
  const restoreError = ref('');
  const isLoggedIn = computed(() => Boolean(token.value && user.value));
  let pendingRestore: Promise<void> | null = null;

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('fubangbang_user');
  }

  async function login(username: string, password: string) {
    const { data } = await loginRequest({ username, password });
    if (!data.token || !data.user?.id) throw new Error('登录响应不完整，请重试');
    token.value = data.token;
    user.value = data.user;
    restoreError.value = '';
    localStorage.setItem('token', data.token);
  }

  async function restore() {
    token.value = localStorage.getItem('token');
    if (!token.value || user.value) return;
    if (pendingRestore) return pendingRestore;
    const restoringToken = token.value;
    pendingRestore = (async () => {
      try {
        const profile = await getCurrentUser();
        if (token.value === restoringToken) user.value = profile;
        restoreError.value = '';
      } catch (error) {
        restoreError.value = errorMessage(error);
      } finally { pendingRestore = null; }
    })();
    return pendingRestore;
  }

  return { token, user, isLoggedIn, restoreError, login, logout, restore };
});
