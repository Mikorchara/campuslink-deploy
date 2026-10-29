<template>
  <div class="register-page">
    <!-- 顶部校园背景与返回导航（复用首页品牌切图与水彩插画素材） -->
    <header class="register-header">
      <!-- 校园水彩插画背景（极淡渐变融入，强化福州大学校园品牌识别，不挤占表单） -->
      <div class="campus-bg-wrapper" aria-hidden="true">
        <img
          src="/assets/images/fzu_campus_bg.png"
          alt="福州大学校园风景"
          class="campus-bg-img"
        />
        <div class="campus-bg-gradient-mask"></div>
      </div>

      <!-- 返回登录条 -->
      <div class="nav-bar">
        <router-link to="/login" class="back-link">
          <svg viewBox="0 0 20 20" fill="currentColor" class="back-icon">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          <span>返回登录</span>
        </router-link>
      </div>

      <!-- 品牌 Logo 与副标题 -->
      <div class="brand-main">
        <img
          src="/assets/images/logo_fubangbang_clean.png"
          alt="福帮帮"
          class="brand-logo-img"
        />
        <p class="brand-subtitle">福州大学校园互助平台</p>
      </div>
    </header>

    <!-- 注册主表单区（融入式舒朗布局，消除 AI 嵌套厚卡片感） -->
    <main class="register-body">
      <!-- 标题区 -->
      <div class="welcome-section">
        <h1 class="welcome-title">创建账号</h1>
        <p class="welcome-subtitle">创建平台独立账号，开启校园互助与闲置交易</p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <!-- 手机号/学号 -->
        <div class="field-item">
          <label class="field-label" for="reg-username">用户名</label>
          <div class="input-wrap" :class="{ 'is-focused': focusedField === 'phone' }">
            <svg viewBox="0 0 20 20" fill="currentColor" class="field-icon">
              <path fill-rule="evenodd" d="M7 2a2 2 0 00-2 2v12a2 2 0 002 2h6a2 2 0 002-2V4a2 2 0 00-2-2H7zm3 14a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
            </svg>
            <input
              id="reg-username"
              v-model.trim="username"
              type="text"
              autocomplete="username"
              minlength="2"
              maxlength="50"
              class="text-input"
              placeholder="请输入 2–50 字用户名"
              @focus="focusedField = 'phone'"
              @blur="focusedField = ''"
              @input="errorMessage = ''"
            />
          </div>
        </div>

        <div class="field-item">
          <label class="field-label" for="reg-email">邮箱</label>
          <div class="input-wrap">
            <input id="reg-email" v-model.trim="email" type="email" autocomplete="email" required
              class="text-input" placeholder="请输入常用邮箱" @input="errorMessage = ''" />
          </div>
        </div>

        <!-- 设置密码 -->
        <div class="field-item">
          <label class="field-label" for="reg-pwd">设置密码</label>
          <div class="input-wrap" :class="{ 'is-focused': focusedField === 'pwd' }">
            <svg viewBox="0 0 20 20" fill="currentColor" class="field-icon">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
            </svg>
            <input
              id="reg-pwd"
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              class="text-input"
              placeholder="6–128 位密码"
              @focus="focusedField = 'pwd'"
              @blur="focusedField = ''"
              @input="errorMessage = ''"
            />
            <button
              type="button"
              class="toggle-pwd-btn"
              :aria-label="showPwd ? '隐藏密码' : '显示密码'"
              @click="showPwd = !showPwd"
            >
              <svg v-if="!showPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="pwd-icon">
                <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" stroke-width="2"/>
                <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" stroke-width="2"/>
                <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" stroke-width="2"/>
                <line x1="2" y1="2" x2="22" y2="22" stroke-width="2"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" class="pwd-icon">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" stroke-width="2"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 确认密码 -->
        <div class="field-item">
          <label class="field-label" for="reg-pwd2">确认密码</label>
          <div class="input-wrap" :class="{ 'is-focused': focusedField === 'pwd2' }">
            <svg viewBox="0 0 20 20" fill="currentColor" class="field-icon">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
            </svg>
            <input
              id="reg-pwd2"
              v-model="confirmPassword"
              :type="showConfirmPwd ? 'text' : 'password'"
              class="text-input"
              placeholder="请再次输入登录密码"
              @focus="focusedField = 'pwd2'"
              @blur="focusedField = ''"
              @input="errorMessage = ''"
            />
            <button
              type="button"
              class="toggle-pwd-btn"
              :aria-label="showConfirmPwd ? '隐藏密码' : '显示密码'"
              @click="showConfirmPwd = !showConfirmPwd"
            >
              <svg v-if="!showConfirmPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="pwd-icon">
                <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" stroke-width="2"/>
                <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" stroke-width="2"/>
                <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" stroke-width="2"/>
                <line x1="2" y1="2" x2="22" y2="22" stroke-width="2"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" class="pwd-icon">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" stroke-width="2"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 用户协议勾选 -->
        <label class="agreement-row">
          <input v-model="agreed" type="checkbox" class="agreement-checkbox" />
          <span class="agreement-label">
            我已阅读并同意
            <a href="javascript:void(0)" @click.stop="showToastMsg('演示：福帮帮用户协议')">《福帮帮用户协议》</a>
            与
            <a href="javascript:void(0)" @click.stop="showToastMsg('演示：隐私政策')">《隐私政策》</a>
          </span>
        </label>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-tip-bar" role="alert">
          <svg viewBox="0 0 20 20" fill="currentColor" class="error-icon">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- 注册主按钮 -->
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="!loading">注 册</span>
          <span v-else>正在注册...</span>
        </button>
      </form>

      <!-- 返回登录引导 -->
      <div class="login-nav-row">
        <span class="login-hint">已有福帮帮账号？</span>
        <router-link to="/login" class="login-action">返回登录</router-link>
      </div>

      <!-- 校园提示 -->
      <div class="campus-auth-note">
        <svg class="auth-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a10.912 10.912 0 01.352 1.897 10.94 10.94 0 00-1.6 3.193 1 1 0 00.957 1.359h10.082a1 1 0 00.957-1.359 10.94 10.94 0 00-1.6-3.193 10.912 10.912 0 01.352-1.897l2.644-1.131a1 1 0 000-1.84l-7-3zM3.31 16.5A11.966 11.966 0 0010 18a11.966 11.966 0 006.69-1.5H3.31z"/>
        </svg>
        <span>校园互助平台 · 请使用真实、可联系的邮箱</span>
      </div>
    </main>

    <!-- 底部版权 -->
    <footer class="register-footer">
      <p class="copyright-text">Fubangbang · 福州大学校园互助平台</p>
    </footer>

    <!-- 全局 Toast -->
    <Teleport to="#app-mobile-frame">
      <Transition name="toast-fade">
        <div v-if="toastMessage" class="app-toast">
          {{ toastMessage }}
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { register } from '../api/auth';
import { errorMessage as describeError } from '../api/request';
const router = useRouter();
const route = useRoute();
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const agreed = ref(false);
const showPwd = ref(false);
const showConfirmPwd = ref(false);
const focusedField = ref('');
const loading = ref(false);
const errorMessage = ref('');
const toastMessage = ref('');
let toastTimer: ReturnType<typeof setTimeout>;
function showToastMsg(msg: string) {
  toastMessage.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastMessage.value = '', 2400);
}
async function handleRegister() {
  if (loading.value) return;
  if (username.value.length < 2 || username.value.length > 50) { errorMessage.value = '用户名应为 2–50 字'; return; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) { errorMessage.value = '请输入有效邮箱'; return; }
  if (password.value.length < 6 || password.value.length > 128) { errorMessage.value = '密码长度应为 6–128 位'; return; }
  if (password.value !== confirmPassword.value) { errorMessage.value = '两次输入的密码不一致'; return; }
  if (!agreed.value) { errorMessage.value = '请阅读并同意用户协议与隐私政策'; return; }
  errorMessage.value = '';
  loading.value = true;
  try {
    await register({ username: username.value, email: email.value, password: password.value });
    localStorage.setItem('fubangbang_saved_account', username.value);
    await router.replace({ path: '/login', query: { registered: '1', redirect: route.query.redirect } });
  } catch (error) { errorMessage.value = describeError(error); }
  finally { loading.value = false; }
}
onUnmounted(() => clearTimeout(toastTimer));
</script>

<style scoped>
.register-page {
  width: 100%;
  height: 100%;
  min-height: 100%;
  background-color: #FFFFFF;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* ================= 顶部品牌与返回条 ================= */
.register-header {
  position: relative;
  padding: 24px 24px 18px 24px;
  overflow: hidden;
  background: linear-gradient(180deg, #F0FDF4 0%, #F9FDF7 60%, #FFFFFF 100%);
  flex-shrink: 0;
}

.campus-bg-wrapper {
  position: absolute;
  top: 0;
  right: 0;
  width: 65%;
  height: 145px;
  pointer-events: none;
  z-index: 1;
}

.campus-bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top right;
  opacity: 0.85;
}

.campus-bg-gradient-mask {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(to right, #F0FDF4 0%, rgba(240, 253, 244, 0.5) 25%, transparent 70%),
    linear-gradient(to bottom, transparent 30%, rgba(255, 255, 255, 0.95) 85%, #FFFFFF 100%);
}

.nav-bar {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 13.5px;
  color: var(--color-text-regular);
  font-weight: 500;
  padding: 4px 0;
}

.back-link:active {
  opacity: 0.7;
}

.back-icon {
  width: 18px;
  height: 18px;
  color: var(--color-text-secondary);
}

.brand-main {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.brand-logo-img {
  width: 140px;
  height: auto;
  display: block;
}

.brand-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
  letter-spacing: 0.4px;
  margin: 0;
}

/* ================= 表单区域 ================= */
.register-body {
  flex: 1;
  padding: 10px 24px 16px 24px;
  display: flex;
  flex-direction: column;
}

.welcome-section {
  margin-bottom: 22px;
}

.welcome-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-main);
  letter-spacing: -0.4px;
  margin: 0;
}

.welcome-subtitle {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 5px;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-regular);
}

.input-wrap {
  height: 48px;
  background-color: #F8FAFC;
  border: 1px solid var(--color-border-regular);
  border-radius: var(--radius-md, 12px);
  padding: 0 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
}

.input-wrap.is-focused {
  background-color: #FFFFFF;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(16, 185, 88, 0.12);
}

.field-icon {
  width: 17px;
  height: 17px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.text-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: var(--color-text-main);
  font-family: inherit;
}

.text-input::placeholder {
  color: var(--color-text-placeholder);
}

/* 验证码行 */
.code-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.code-input-wrap {
  flex: 1;
}

.send-code-btn {
  height: 48px;
  padding: 0 14px;
  border-radius: var(--radius-md, 12px);
  background: var(--color-primary-light);
  border: 1px solid #C6F0BE;
  color: var(--color-primary-dark);
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.send-code-btn:active {
  background: #DCF5D6;
}

.send-code-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  color: var(--color-text-muted);
  background: var(--color-bg-subtle);
  border-color: var(--color-border-regular);
}

.toggle-pwd-btn {
  background: none;
  border: none;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  cursor: pointer;
}

.pwd-icon {
  width: 18px;
  height: 18px;
}

/* 用户协议勾选 */
.agreement-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 2px;
  cursor: pointer;
  user-select: none;
}

.agreement-checkbox {
  width: 15px;
  height: 15px;
  accent-color: var(--color-primary);
  border-radius: 3px;
  margin-top: 2px;
  cursor: pointer;
}

.agreement-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.agreement-label a {
  color: var(--color-primary);
}

.agreement-label a:active {
  opacity: 0.7;
}

/* 错误提示 */
.error-tip-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: #FEF2F2;
  border: 1px solid #FEE2E2;
  color: #DC2626;
  font-size: 12px;
  padding: 8px 12px;
  border-radius: var(--radius-sm, 8px);
}

.error-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

/* 注册主按钮 */
.submit-btn {
  height: 48px;
  width: 100%;
  border-radius: var(--radius-md, 12px);
  background: var(--color-primary-gradient);
  color: #FFFFFF;
  font-size: 15.5px;
  font-weight: 600;
  letter-spacing: 2px;
  box-shadow: 0 4px 14px rgba(16, 185, 88, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.15s ease;
  margin-top: 6px;
}

.submit-btn:active {
  transform: scale(0.985);
  opacity: 0.92;
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}

/* 返回登录 */
.login-nav-row {
  margin-top: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13.5px;
}

.login-hint {
  color: var(--color-text-secondary);
}

.login-action {
  color: var(--color-primary);
  font-weight: 600;
}

.login-action:active {
  opacity: 0.75;
}

/* 校园认证辅助 */
.campus-auth-note {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-muted);
}

.auth-icon {
  width: 14px;
  height: 14px;
  color: var(--color-primary);
  flex-shrink: 0;
}

/* ================= 底部版权 ================= */
.register-footer {
  margin-top: auto;
  padding: 12px 24px 16px 24px;
  text-align: center;
  flex-shrink: 0;
}

.copyright-text {
  font-size: 10.5px;
  color: #CBD5E1;
  margin: 0;
}

/* 全局 Toast */
.app-toast {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(4px);
  color: #FFFFFF;
  padding: 9px 18px;
  border-radius: var(--radius-pill);
  font-size: 12.5px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  pointer-events: none;
  white-space: nowrap;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 8px);
}
</style>
