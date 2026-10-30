<template>
  <div v-if="session.isLoggedIn" class="notification-bar">
    <RouterLink to="/notifications" class="notification-link" :aria-label="`消息中心，${inbox.count}条未读`">
      <span>消息中心</span><span v-if="inbox.count" class="unread-badge">{{ inbox.count > 99 ? '99+' : inbox.count }}</span><span v-else class="empty-count">暂无未读</span>
    </RouterLink>
    <span class="notification-status" role="status" aria-live="polite">{{ inbox.count ? `${inbox.count} 条未读` : '' }}</span>
    <button v-if="inbox.error" type="button" class="retry" @click="inbox.refresh">检查失败，重试</button>
  </div>
</template>
<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue';
import { useUserStore } from '../../stores/user';
import { useNotificationsStore } from '../../stores/notifications';
const session = useUserStore(), inbox = useNotificationsStore();
let timer: ReturnType<typeof setInterval> | undefined;
function refreshVisible() { if (session.isLoggedIn && !document.hidden) void inbox.refresh(); }
watch(() => session.token, () => {
  clearInterval(timer); inbox.reset();
  if (session.isLoggedIn) { refreshVisible(); timer = setInterval(refreshVisible, 30000); }
}, { immediate: true });
// Session restoration may populate the user after the token has been read.
watch(() => session.isLoggedIn, loggedIn => {
  clearInterval(timer);
  if (loggedIn) { refreshVisible(); timer = setInterval(refreshVisible, 30000); } else inbox.reset();
});
onMounted(() => { document.addEventListener('visibilitychange', refreshVisible); window.addEventListener('focus', refreshVisible); });
onUnmounted(() => { clearInterval(timer); document.removeEventListener('visibilitychange', refreshVisible); window.removeEventListener('focus', refreshVisible); inbox.reset(); });
</script>
<style scoped>
.notification-bar { flex-shrink: 0; min-height: 44px; display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); padding-inline: var(--space-base); background: var(--color-bg-card); border-bottom: 1px solid var(--color-border-regular); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.notification-link { display: inline-flex; align-items: center; gap: var(--space-sm); min-height: 44px; color: var(--color-text-main); font-weight: 600; }
.unread-badge { min-width: 22px; padding: 2px var(--space-xs); border-radius: var(--radius-pill); background: var(--color-price); color: var(--color-bg-card); text-align: center; }
.empty-count { color: var(--color-text-muted); font-weight: 400; }
.notification-status { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
.retry { min-height: 44px; color: var(--color-price-sub); }
</style>
