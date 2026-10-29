<template>
  <div class="forum-page forum-list-page">
    <header class="forum-heading"><h1>{{ mine ? '我的帖子' : '校园论坛' }}</h1><RouterLink to="/forum/new">写帖子</RouterLink></header>
    <p class="forum-subtitle">分享学习经验与校园生活，交流真实有用的信息。</p>
    <div class="forum-actions"><RouterLink class="forum-button" :to="mine ? '/forum' : '/my-posts'">{{ mine ? '浏览全部帖子' : '我的帖子' }}</RouterLink></div>
    <form v-if="!mine" class="forum-search" @submit.prevent="search"><input v-model="keyword" aria-label="搜索帖子" maxlength="120" placeholder="搜索标题或正文" /><button class="forum-button" type="submit">搜索</button></form>
    <nav v-if="!mine" class="forum-tabs" aria-label="帖子分类"><button v-for="cat in ['全部', ...forumCategories]" :key="cat" :class="{ active: category === cat }" :aria-pressed="category === cat" @click="chooseCategory(cat)">{{ cat }}</button></nav>
    <RequestState v-if="loading || error" :loading="loading" :error="error" @retry="load" />
    <RequestState v-else-if="!posts.length" :empty-text="mine ? '还没有发布帖子，写下你的第一篇校园经验吧' : '没有找到帖子，试试其他关键词或分类'" />
    <div v-else class="forum-posts"><article v-for="post in posts" :key="post.id"><ForumPostCard :post="post" @click="router.push(`/forum/${post.id}`)" /><div v-if="mine" class="forum-actions"><RouterLink :to="`/forum/${post.id}/edit`" class="forum-button">编辑帖子</RouterLink></div></article></div>
    <nav v-if="total" class="forum-pagination" aria-label="帖子分页"><button class="forum-button" :disabled="loading || page <= 1" @click="changePage(page - 1)">上一页</button><span>第 {{ page }} / {{ Math.max(1, Math.ceil(total / 20)) }} 页 · 共 {{ total }} 篇</span><button class="forum-button" :disabled="loading || page * 20 >= total" @click="changePage(page + 1)">下一页</button></nav>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getForumPosts, getMyForumPosts, forumCategories } from '../api/forum';
import { errorMessage } from '../api/request';
import type { ForumPost } from '../types';
import ForumPostCard from '../components/forum/ForumPostCard.vue';
import RequestState from '../components/common/RequestState.vue';
import '../styles/forum.css';
const props = defineProps<{ mine?: boolean }>();
const route = useRoute(), router = useRouter();
const posts = ref<ForumPost[]>([]), keyword = ref(''), category = ref('全部');
const page = ref(1), total = ref(0), loading = ref(false), error = ref('');
let version = 0;
async function load() {
  const current = ++version;
  loading.value = true; error.value = ''; posts.value = [];
  try {
    const data = props.mine ? await getMyForumPosts(page.value) : await getForumPosts({ keyword: keyword.value.trim(), category: category.value === '全部' ? undefined : category.value, page: page.value });
    if (current !== version) return;
    posts.value = data.items; total.value = data.total;
  } catch (e) { if (current === version) error.value = errorMessage(e); }
  finally { if (current === version) loading.value = false; }
}
function navigate(nextPage: number, nextCategory = category.value) {
  void router.push({ path: props.mine ? '/my-posts' : '/forum', query: { keyword: props.mine ? undefined : keyword.value.trim() || undefined, category: nextCategory === '全部' || props.mine ? undefined : nextCategory, page: nextPage > 1 ? String(nextPage) : undefined } });
}
function search() { if (String(route.query.keyword || '') === keyword.value.trim() && page.value === 1) void load(); else navigate(1); }
function chooseCategory(cat: string) { navigate(1, cat); }
function changePage(next: number) { navigate(next); }
watch(() => [props.mine, route.query.keyword, route.query.category, route.query.page], () => {
  keyword.value = String(route.query.keyword || '');
  const cat = String(route.query.category || '');
  category.value = forumCategories.some(c => c === cat) ? cat : '全部';
  const number = Number(route.query.page);
  page.value = Number.isSafeInteger(number) && number > 0 ? number : 1;
  void load();
}, { immediate: true });
onUnmounted(() => version++);
</script>
