<template>
  <div class="forum-page inbox-page">
    <header class="forum-heading"><RouterLink to="/profile">返回我的</RouterLink><h1>消息中心</h1><button :disabled="loading || busy" @click="load(1)">刷新</button></header>
    <p class="forum-subtitle">预订与交易进展、帖子评论和收到的点赞会保存在这里。网页打开时约每 30 秒检查新消息。</p>
    <div class="forum-actions">
      <button class="forum-button" :aria-pressed="!unreadOnly" :disabled="busy" @click="changeFilter(false)">全部</button>
      <button class="forum-button" :aria-pressed="unreadOnly" :disabled="busy" @click="changeFilter(true)">未读（{{ inbox.count }}）</button>
      <button class="forum-button" :disabled="loading || busy || !items.length || !inbox.count" @click="readAll">全部标为已读</button>
    </div>
    <RequestState v-if="loading || error" :loading="loading" :error="error" @retry="load(page)" />
    <template v-else>
      <p v-if="!items.length" class="forum-panel">{{ unreadOnly ? '暂无未读消息' : '还没有消息。收到预订、评论或点赞后会出现在这里。' }}</p>
      <article v-for="item in items" :key="item.id" class="forum-panel notification-card" :class="{ unread: !item.is_read }">
        <div class="message-meta"><span>{{ item.is_read ? '已读' : '未读' }}</span><time>{{ forumDate(item.created_at) }}</time></div>
        <p class="message-text">{{ item.message }}</p>
        <p v-if="!item.link" class="forum-subtitle">相关内容已删除，消息记录仍然保留。</p>
        <div class="forum-actions"><button v-if="item.link" class="forum-button primary" :disabled="busy" @click="open(item)">查看详情</button><button v-if="!item.is_read" class="forum-button" :disabled="busy" @click="read(item)">标为已读</button></div>
      </article>
      <div v-if="total" class="forum-pagination"><button class="forum-button" :disabled="page === 1 || busy" @click="load(page - 1)">上一页</button><span>第 {{ page }} / {{ Math.ceil(total / 20) }} 页</span><button class="forum-button" :disabled="page * 20 >= total || busy" @click="load(page + 1)">下一页</button></div>
    </template>
    <p v-if="actionError" role="alert" class="forum-error">{{ actionError }}</p>
  </div>
</template>
<script setup lang="ts">
import { onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { getNotifications, markNotificationRead, markNotificationsRead, type NotificationItem } from '../api/activity';
import { forumDate } from '../api/forum';
import { errorMessage } from '../api/request';
import { useNotificationsStore } from '../stores/notifications';
import RequestState from '../components/common/RequestState.vue';
import '../styles/forum.css';
const router = useRouter(), inbox = useNotificationsStore();
const items = ref<NotificationItem[]>([]), total = ref(0), page = ref(1), unreadOnly = ref(false);
const loading = ref(false), busy = ref(false), error = ref(''), actionError = ref('');
let version = 0;
let newestSeen = 0;
async function load(nextPage = 1) {
  const current = ++version;
  loading.value = true; error.value = ''; actionError.value = '';
  try {
    const result = await getNotifications(nextPage, unreadOnly.value);
    if (current !== version) return;
    if (nextPage > 1 && !result.items.length) { await load(nextPage - 1); return; }
    items.value = result.items; total.value = result.total; page.value = nextPage;
    newestSeen = Math.max(newestSeen, ...result.items.map(item => item.id));
    await inbox.refresh();
  } catch (e) { if (current === version) error.value = errorMessage(e); }
  finally { if (current === version) loading.value = false; }
}
function changeFilter(value: boolean) { unreadOnly.value = value; void load(1); }
async function read(item: NotificationItem, navigate = false) {
  if (busy.value) return;
  busy.value = true; actionError.value = '';
  try {
    if (!item.is_read) await markNotificationRead(item.id);
    await inbox.refresh();
    if (navigate && item.link) await router.push(item.link);
    else await load(page.value);
  } catch (e) { actionError.value = errorMessage(e); }
  finally { busy.value = false; }
}
function open(item: NotificationItem) { void read(item, true); }
async function readAll() {
  if (busy.value || !items.value.length) return;
  busy.value = true; actionError.value = '';
  try { await markNotificationsRead(newestSeen); await load(1); }
  catch (e) { actionError.value = errorMessage(e); }
  finally { busy.value = false; }
}
void load();
onUnmounted(() => { version++; });
</script>
<style scoped>
.inbox-page { padding-bottom: 76px; }
.inbox-page h1 { font-size: var(--font-size-lg); }
.notification-card { border-left: 3px solid var(--color-border-regular); }
.notification-card.unread { border-left-color: var(--color-primary); }
.message-meta { display: flex; flex-wrap: wrap; gap: var(--space-sm); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.unread .message-meta > span { color: var(--color-primary-dark); font-weight: 600; }
.message-text { margin-block: var(--space-md); overflow-wrap: anywhere; white-space: pre-wrap; }
button[aria-pressed="true"] { color: var(--color-primary-dark); background: var(--color-primary-light); }
</style>
