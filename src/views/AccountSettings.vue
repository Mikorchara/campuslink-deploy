<template>
  <section class="account-page">
    <header class="account-heading"><router-link to="/profile">‹ 我的</router-link><h1>个人资料</h1></header>
    <form class="account-card" @submit.prevent="save">
      <label class="account-field">用户名<input v-model.trim="username" required minlength="2" maxlength="50" /></label>
      <label class="account-field">邮箱<input v-model.trim="email" type="email" required /></label>
      <label class="account-field">联系方式<input v-model.trim="contact" maxlength="100" placeholder="如 QQ 或微信，登录用户联系你时可见" /></label>
      <label class="account-field">个人介绍<textarea v-model.trim="bio" maxlength="255" /></label>
      <p v-if="error" class="account-error" role="alert">{{ error }}</p><p v-if="message" class="account-message" role="status">{{ message }}</p>
      <button class="account-submit" :disabled="busy">{{ busy ? '正在保存…' : '保存资料' }}</button>
    </form>
  </section>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { request, errorMessage } from '../api/request';
import { useUserStore } from '../stores/user';
import type { UserProfile } from '../types';
const session = useUserStore();
const username = ref(session.user?.username || ''), email = ref(session.user?.email || '');
const contact = ref(session.user?.contact || ''), bio = ref(session.user?.bio || '');
const busy = ref(false), error = ref(''), message = ref('');
async function save() {
  if (busy.value) return;
  busy.value = true; error.value = ''; message.value = '';
  try { session.user = (await request<UserProfile>('/users/me', { method: 'PUT', body: JSON.stringify({ username: username.value, email: email.value, contact: contact.value, bio: bio.value }) })).data; message.value = '资料已保存'; }
  catch (e) { error.value = errorMessage(e); } finally { busy.value = false; }
}
</script>
