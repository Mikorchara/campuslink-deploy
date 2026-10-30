import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getUnreadCount } from '../api/activity';
import { errorMessage } from '../api/request';
import { useUserStore } from './user';

export const useNotificationsStore = defineStore('notifications', () => {
  const count = ref(0), error = ref('');
  let generation = 0;
  function reset() { generation++; count.value = 0; error.value = ''; }
  async function refresh() {
    const session = useUserStore();
    if (!session.isLoggedIn) { reset(); return; }
    const token = session.token, current = ++generation;
    try {
      const value = await getUnreadCount();
      if (current === generation && token === session.token) { count.value = value; error.value = ''; }
    } catch (e) {
      if (current === generation && token === session.token) error.value = errorMessage(e);
    }
  }
  return { count, error, refresh, reset };
});
