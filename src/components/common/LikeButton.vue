<template>
  <div class="like-control">
    <button type="button" class="like-button" :class="{ liked: state.liked }" :aria-pressed="state.liked"
      :disabled="loading || busy" @click="error ? load() : toggle()">
      <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 10v11H3V10h4Zm0 0 5-8c2 0 3 2 2 5l-1 3h6c2 0 2 2 2 3l-2 7c0 1-1 1-2 1H7" /></svg>
      {{ loading ? '加载点赞…' : busy ? '处理中…' : error ? '点赞加载失败，重试' : `${state.liked ? '已赞' : '点赞'} · ${state.count}` }}
    </button>
    <p v-if="error" class="like-error" role="alert">{{ error }}</p>
  </div>
</template>
<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getLike, setLike } from '../../api/activity';
import { errorMessage } from '../../api/request';
import { useUserStore } from '../../stores/user';
const props = defineProps<{ kind: 'product' | 'post'; id: number }>();
const session = useUserStore(), route = useRoute(), router = useRouter();
const state = ref({ count: 0, liked: false }), loading = ref(false), busy = ref(false), error = ref('');
let version = 0;
async function load() {
  const current = ++version;
  loading.value = true; error.value = ''; state.value = { count: 0, liked: false };
  try { const value = await getLike(props.kind, props.id); if (current === version) state.value = value; }
  catch (e) { if (current === version) error.value = errorMessage(e); }
  finally { if (current === version) loading.value = false; }
}
async function toggle() {
  if (!session.isLoggedIn) { void router.push({ path: '/login', query: { redirect: route.fullPath } }); return; }
  if (busy.value || loading.value) return;
  busy.value = true; error.value = '';
  const current = version;
  try { const value = await setLike(props.kind, props.id, !state.value.liked); if (current === version) state.value = value; }
  catch (e) { if (current === version) error.value = errorMessage(e); }
  finally { if (current === version) busy.value = false; }
}
watch(() => [props.kind, props.id, session.user?.id], () => { busy.value = false; void load(); }, { immediate: true });
onUnmounted(() => { version++; });
</script>
<style scoped>
.like-control { margin-block: var(--space-md); }
.like-button { display: inline-flex; align-items: center; justify-content: center; gap: var(--space-sm); min-height: 44px; padding: var(--space-sm) var(--space-base); border: 1px solid var(--color-border-regular); border-radius: var(--radius-pill); color: var(--color-text-secondary); background: var(--color-bg-card); }
.like-button svg { width: 20px; height: 20px; }
.like-button.liked { color: var(--color-primary-dark); background: var(--color-primary-light); border-color: var(--color-primary); }
.like-button:disabled { opacity: .65; }
.like-error { color: var(--color-price-sub); font-size: var(--font-size-sm); overflow-wrap: anywhere; margin-top: var(--space-sm); }
</style>
