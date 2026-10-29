<template>
  <div class="forum-page forum-editor-page">
    <header class="forum-heading"><RouterLink :to="id ? `/forum/${id}` : '/forum'">返回</RouterLink><h1>{{ id ? '编辑帖子' : '写帖子' }}</h1></header>
    <RequestState v-if="loading || loadError" :loading="loading" :error="loadError" @retry="load" />
    <form v-else class="forum-panel" @submit.prevent="submit">
      <fieldset :disabled="saving || uploading">
        <label class="forum-field">标题<input v-model="form.title" aria-label="帖子标题" maxlength="120" required placeholder="你想分享什么校园经验？" /></label>
        <label class="forum-field">分类<select v-model="form.category" aria-label="帖子分类"><option v-for="cat in forumCategories" :key="cat">{{ cat }}</option></select></label>
        <label class="forum-field">正文<textarea v-model="form.content" aria-label="帖子正文" maxlength="10000" rows="12" required placeholder="写下具体的经验、地点或实用建议…" /></label>
        <p class="forum-count">{{ form.content.length }} / 10000</p>
        <label class="forum-field">封面（可选）<input type="file" accept="image/jpeg,image/png,image/webp" aria-label="帖子封面" @change="chooseImage" /></label>
        <p class="forum-subtitle">支持一张 JPEG、PNG 或 WebP 图片，大小不超过 5 MB。正文以纯文本保存。</p>
        <img v-if="form.image_url" :src="form.image_url" alt="帖子封面预览" class="forum-cover" />
        <button v-if="form.image_url" class="forum-button" type="button" @click="form.image_url = ''">移除封面</button>
        <div class="forum-actions"><button v-if="!id" class="forum-button" type="button" @click="saveDraft">存草稿</button><button class="forum-button primary" type="submit" :disabled="!form.title.trim() || !form.content.trim()">{{ saving ? '保存中…' : id ? '保存修改' : '发布帖子' }}</button></div>
      </fieldset>
      <p v-if="uploading" role="status">封面上传中…</p><p v-if="error" class="forum-error" role="alert">{{ error }}</p><p v-if="message" class="forum-success" role="status">{{ message }}</p>
      <p v-if="!id" class="forum-subtitle">草稿只保存在当前浏览器中，发布成功后清除。离开前可先存草稿。</p>
    </form>
  </div>
</template>
<script setup lang="ts">
import { computed, reactive, ref, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import { forumCategories, getForumPost, saveForumPost } from '../api/forum';
import { uploadImage } from '../api/product';
import { errorMessage } from '../api/request';
import type { ForumPostPayload } from '../types';
import RequestState from '../components/common/RequestState.vue';
import '../styles/forum.css';
const route = useRoute(), router = useRouter(), session = useUserStore();
const id = computed(() => route.params.id ? String(route.params.id) : undefined);
const draftKey = computed(() => `campuslink:forum-draft:${session.user?.id}`);
const form = reactive<ForumPostPayload>({ title: '', content: '', category: '生活', image_url: '' });
const loading = ref(false), loadError = ref(''), saving = ref(false), uploading = ref(false), error = ref(''), message = ref('');
let version = 0;
async function load() {
  const current = ++version; loadError.value = ''; error.value = ''; message.value = ''; loading.value = true;
  Object.assign(form, { title: '', content: '', category: '生活', image_url: '' });
  try {
    if (id.value) {
      const post = await getForumPost(id.value);
      if (current !== version) return;
      if (post.author.id !== session.user?.id) throw new Error('只能编辑自己发布的帖子');
      Object.assign(form, { title: post.title, content: post.content || '', category: post.category, image_url: post.image_url });
    } else {
      const draft = JSON.parse(localStorage.getItem(draftKey.value) || 'null');
      if (draft && typeof draft.title === 'string' && typeof draft.content === 'string' && forumCategories.includes(draft.category)) {
        Object.assign(form, { title: draft.title.slice(0, 120), content: draft.content.slice(0, 10000), category: draft.category, image_url: typeof draft.image_url === 'string' && /^\/api\/uploads\/[a-f0-9]{32}\.webp$/.test(draft.image_url) ? draft.image_url : '' });
        message.value = '已恢复本机草稿';
      }
    }
  } catch (e) { if (current === version) { if (id.value) loadError.value = errorMessage(e); else error.value = '无法读取本机草稿，可以直接写新帖子'; } }
  finally { if (current === version) loading.value = false; }
}
function saveDraft() {
  error.value = '';
  try { localStorage.setItem(draftKey.value, JSON.stringify(form)); message.value = '草稿已保存'; }
  catch { error.value = '浏览器存储不可用，草稿未保存'; }
}
async function chooseImage(event: Event) {
  const input = event.target as HTMLInputElement, file = input.files?.[0];
  if (!file || uploading.value || saving.value) return;
  error.value = ''; message.value = '';
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) { error.value = '请选择不超过 5 MB 的 JPEG、PNG 或 WebP 图片'; input.value = ''; return; }
  const current = version; uploading.value = true;
  try { const url = await uploadImage(file); if (current === version) form.image_url = url; }
  catch (e) { if (current === version) error.value = errorMessage(e); }
  finally { uploading.value = false; input.value = ''; }
}
async function submit() {
  if (saving.value || uploading.value || !form.title.trim() || !form.content.trim()) return;
  saving.value = true; error.value = ''; message.value = '';
  try {
    const post = await saveForumPost({ ...form, title: form.title.trim(), content: form.content.trim() }, id.value);
    if (!id.value) { try { localStorage.removeItem(draftKey.value); } catch { /* The server save already succeeded. */ } }
    await router.replace(`/forum/${post.id}`);
  } catch (e) { error.value = errorMessage(e); }
  finally { saving.value = false; }
}
watch(id, () => void load(), { immediate: true });
onUnmounted(() => version++);
</script>
<style scoped>fieldset { min-width: 0; border: 0; padding: 0; margin: 0; }</style>
