<template>
  <div class="forum-page post-detail-page">
    <header class="forum-heading"><RouterLink to="/forum">返回论坛</RouterLink><span>帖子详情</span><button @click="share">复制链接</button></header>
    <RequestState v-if="loading || error" :loading="loading" :error="error" @retry="load" />
    <template v-else-if="post">
      <article class="forum-panel">
        <p class="forum-meta">{{ post.tag }} · {{ forumDate(post.created_at) }}</p><h1 class="forum-title">{{ post.title }}</h1>
        <div class="forum-author"><img :src="post.author.avatar" alt="" /><span>{{ post.author.name }}</span></div>
        <div v-if="isOwner" class="forum-actions"><RouterLink class="forum-button" :to="`/forum/${post.id}/edit`">编辑帖子</RouterLink><button class="forum-button danger" @click="confirmDelete = { kind: 'post', id: post.id }">删除帖子</button></div>
        <img v-if="post.image_url" :src="post.image_url" :alt="post.title" class="forum-cover" />
        <div class="forum-body">{{ post.content }}</div>
        <LikeButton :key="post.id" kind="post" :id="post.id" />
      </article>
      <section class="forum-panel" aria-label="讨论区">
        <h2>讨论区（{{ totalComments }}）</h2><p class="forum-subtitle">文明发言，保护自己和他人的个人信息。</p>
        <form v-if="session.isLoggedIn" class="forum-comment-form" @submit.prevent="submitComment">
          <label class="forum-field">写评论<textarea v-model="commentText" aria-label="评论内容" maxlength="1000" rows="3" required :disabled="sending" /></label>
          <p class="forum-count">{{ commentText.length }} / 1000</p><button class="forum-button primary" :disabled="sending || !commentText.trim()">{{ sending ? '发送中…' : '发布评论' }}</button>
        </form>
        <RouterLink v-else class="forum-link" :to="{ path: '/login', query: { redirect: route.fullPath } }">登录后参与讨论</RouterLink>
        <RequestState v-if="commentsError" :error="commentsError" @retry="loadComments(1)" />
        <p v-if="!commentsLoading && !comments.length && !commentsError" class="forum-subtitle">还没有评论，来分享你的经验吧。</p>
        <article v-for="comment in comments" :key="comment.id" class="forum-comment">
          <div class="forum-author"><img :src="comment.author.avatar" alt="" /><h3>{{ comment.author.name }}</h3></div><time class="forum-meta">{{ forumDate(comment.created_at) }}</time>
          <form v-if="editingId === comment.id" @submit.prevent="saveComment(comment.id)"><label class="forum-field">修改评论<textarea v-model="editingText" aria-label="修改评论内容" rows="3" maxlength="1000" required :disabled="commentBusy" /></label><div class="forum-actions"><button class="forum-button" :disabled="commentBusy || !editingText.trim()">保存评论</button><button type="button" class="forum-button" :disabled="commentBusy" @click="editingId = null">取消</button></div></form>
          <template v-else><p>{{ comment.content }}</p><div v-if="session.user?.id === comment.author.id" class="forum-actions"><button class="forum-button" @click="editingId = comment.id; editingText = comment.content">编辑评论</button><button class="forum-button danger" @click="confirmDelete = { kind: 'comment', id: comment.id }">删除评论</button></div></template>
        </article>
        <p v-if="commentsLoading" role="status">正在加载评论…</p><button v-else-if="comments.length < totalComments" class="forum-button" @click="loadComments(commentPage + 1)">加载更多评论</button>
      </section>
    </template>
    <p v-if="actionError" class="forum-error" role="alert">{{ actionError }}</p><p v-if="message" class="forum-success" role="status">{{ message }}</p>
    <AppDialog :open="Boolean(confirmDelete)" :title="confirmDelete?.kind === 'post' ? '删除帖子' : '删除评论'" @close="!deleting && (confirmDelete = null)"><p>{{ confirmDelete?.kind === 'post' ? '删除后，帖子和下面的所有评论都会被移除。确认删除吗？' : '确认删除这条评论吗？' }}</p><p v-if="deleteError" class="forum-error" role="alert">{{ deleteError }}</p><div class="forum-actions"><button class="forum-button" :disabled="deleting" @click="confirmDelete = null">取消</button><button class="forum-button danger" :disabled="deleting" @click="remove">{{ deleting ? '删除中…' : '确认删除' }}</button></div></AppDialog>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import { getForumPost, getForumComments, addForumComment, editForumComment, deleteForumComment, deleteForumPost, forumDate } from '../api/forum';
import { errorMessage } from '../api/request';
import type { ForumPost, ForumComment } from '../types';
import RequestState from '../components/common/RequestState.vue';
import AppDialog from '../components/common/AppDialog.vue';
import LikeButton from '../components/common/LikeButton.vue';
import '../styles/forum.css';
const route = useRoute(), router = useRouter(), session = useUserStore();
const post = ref<ForumPost | null>(null), loading = ref(false), error = ref('');
const comments = ref<ForumComment[]>([]), commentPage = ref(1), totalComments = ref(0), commentsLoading = ref(false), commentsError = ref('');
const commentText = ref(''), sending = ref(false), actionError = ref(''), message = ref('');
const editingId = ref<number | null>(null), editingText = ref(''), commentBusy = ref(false);
const confirmDelete = ref<{ kind: 'post' | 'comment'; id: number } | null>(null), deleting = ref(false), deleteError = ref('');
const isOwner = computed(() => Boolean(session.user && session.user.id === post.value?.author.id));
let version = 0, commentsVersion = 0;
async function load() {
  const current = ++version; ++commentsVersion;
  post.value = null; comments.value = []; commentText.value = ''; actionError.value = ''; message.value = ''; loading.value = true; error.value = '';
  editingId.value = null; confirmDelete.value = null; commentsError.value = ''; totalComments.value = 0; commentPage.value = 1;
  try { const data = await getForumPost(String(route.params.id)); if (current !== version) return; post.value = data; totalComments.value = data.comment_count; void loadComments(1); }
  catch (e) { if (current === version) error.value = errorMessage(e); }
  finally { if (current === version) loading.value = false; }
}
async function loadComments(page: number) {
  const current = ++commentsVersion;
  commentsLoading.value = true; commentsError.value = '';
  try { const data = await getForumComments(String(route.params.id), page); if (current !== commentsVersion) return; comments.value = page === 1 ? data.items : [...comments.value, ...data.items.filter(item => !comments.value.some(c => c.id === item.id))]; totalComments.value = data.total; commentPage.value = page; }
  catch (e) { if (current === commentsVersion) commentsError.value = errorMessage(e); }
  finally { if (current === commentsVersion) commentsLoading.value = false; }
}
async function submitComment() {
  if (!post.value || sending.value || !commentText.value.trim()) return;
  sending.value = true; actionError.value = ''; message.value = '';
  try { const created = await addForumComment(post.value.id, commentText.value.trim()); commentText.value = ''; totalComments.value++; if (comments.value.length === totalComments.value - 1) comments.value.push(created); message.value = '评论已发布并保存'; }
  catch (e) { actionError.value = errorMessage(e); }
  finally { sending.value = false; }
}
async function saveComment(id: number) {
  if (commentBusy.value || !editingText.value.trim()) return;
  commentBusy.value = true; actionError.value = '';
  try { const item = await editForumComment(id, editingText.value.trim()); comments.value = comments.value.map(c => c.id === id ? item : c); editingId.value = null; message.value = '评论已更新'; }
  catch (e) { actionError.value = errorMessage(e); }
  finally { commentBusy.value = false; }
}
async function remove() {
  if (!confirmDelete.value || deleting.value) return;
  const target = confirmDelete.value; deleting.value = true; deleteError.value = '';
  try {
    if (target.kind === 'post') { await deleteForumPost(target.id); confirmDelete.value = null; await router.replace('/my-posts'); }
    else { await deleteForumComment(target.id); confirmDelete.value = null; await loadComments(1); message.value = '评论已删除'; }
  } catch (e) { deleteError.value = errorMessage(e); }
  finally { deleting.value = false; }
}
async function share() { try { await navigator.clipboard.writeText(location.href); message.value = '帖子链接已复制'; } catch { message.value = '请从浏览器地址栏复制帖子链接'; } }
watch(() => route.params.id, () => void load(), { immediate: true });
watch(confirmDelete, () => deleteError.value = '');
onUnmounted(() => { version++; commentsVersion++; });
</script>
