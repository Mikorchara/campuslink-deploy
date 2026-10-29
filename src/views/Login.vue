<template>
  <div class="login-page">
    <!-- 顶部校园背景与品牌标识（复用首页品牌切图与水彩插画素材） -->
    <header class="brand-header">
      <!-- 校园水彩插画背景（极淡渐变融入，强化福州大学校园品牌识别，不挤占表单） -->
      <div class="campus-bg-wrapper" aria-hidden="true">
        <img
          src="/assets/images/fzu_campus_bg.png"
          alt="福州大学校园风景"
          class="campus-bg-img"
        />
        <div class="campus-bg-gradient-mask"></div>
      </div>

      <!-- 品牌 Logo 与副标题（精准复用首页绿黑书法动感字形，剔除多余标语短线） -->
      <div class="brand-main">
        <img
          src="/assets/images/logo_fubangbang_clean.png"
          alt="福帮帮"
          class="brand-logo-img"
        />
        <p class="brand-subtitle">福州大学校园互助平台</p>
      </div>
    </header>

    <!-- 登录主表单区（融入式舒朗布局，消除 AI 嵌套厚卡片感） -->
    <main class="login-body">
      <!-- 注册成功横幅提示 -->
      <div v-if="registeredSuccess" class="success-banner">
        <svg viewBox="0 0 20 20" fill="currentColor" class="banner-icon">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
        </svg>
        <span class="banner-text">账号注册成功！请使用新账号登录</span>
      </div>

      <!-- 欢迎标题 -->
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎登录</h1>
        <p class="welcome-subtitle">登录后畅享校园二手交易与论坛互助</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <!-- 账号输入框 -->
        <div class="field-item">
          <label class="field-label" for="login-account">账号</label>
          <div class="input-wrap" :class="{ 'is-focused': isAccountFocused }">
            <svg viewBox="0 0 20 20" fill="currentColor" class="field-icon">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
            </svg>
            <input
              id="login-account"
              v-model.trim="account"
              type="text"
              autocomplete="username"
              class="text-input"
              placeholder="请输入用户名或邮箱"
              @focus="isAccountFocused = true"
              @blur="isAccountFocused = false"
              @input="errorMessage = ''"
            />
          </div>
        </div>

        <!-- 密码输入框 -->
        <div class="field-item">
          <label class="field-label" for="login-password">密码</label>
          <div class="input-wrap" :class="{ 'is-focused': isPasswordFocused }">
            <svg viewBox="0 0 20 20" fill="currentColor" class="field-icon">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
            </svg>
            <input
              id="login-password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              class="text-input"
              placeholder="请输入登录密码"
              @focus="isPasswordFocused = true"
              @blur="isPasswordFocused = false"
              @input="errorMessage = ''"
            />
            <button
              type="button"
              class="toggle-pwd-btn"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
              @click="showPassword = !showPassword"
            >
              <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="pwd-icon">
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

        <!-- 记住账号与忘记密码 -->
        <div class="form-assist-row">
          <label class="remember-label">
            <input v-model="rememberMe" type="checkbox" class="remember-checkbox" />
            <span>记住账号</span>
          </label>
          <button type="button" class="forget-link" @click="handleForgetPassword">忘记密码？</button>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-tip-bar" role="alert">
          <svg viewBox="0 0 20 20" fill="currentColor" class="error-icon">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- 绿色登录按钮（复用首页品牌绿色及圆角体系） -->
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="!loading">登 录</span>
          <span v-else>正在登录...</span>
        </button>
      </form>

      <!-- 注册账号入口（单一定位，消除多余重复） -->
      <div class="register-nav-row">
        <span class="register-hint">还没有福帮帮账号？</span>
        <router-link :to="{ path: '/register', query: { redirect: route.query.redirect } }" class="register-action">立即注册</router-link>
      </div>

      <!-- 校园邮箱认证说明（精炼自然的一行辅助文字，去除大提示卡片） -->
      <div class="campus-auth-note">
        <svg class="auth-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
        </svg>
        <span>使用平台独立账号登录，发布与管理你的闲置</span>
      </div>
    </main>

    <!-- 底部协议说明与版权信息 -->
    <footer class="login-footer">
      <p class="agreement-text">
        登录即代表已阅读并同意
        <a href="javascript:void(0)" @click.prevent="showToastMsg('演示：福帮帮用户服务协议')">《用户协议》</a>
        与
        <a href="javascript:void(0)" @click.prevent="showToastMsg('演示：福帮帮隐私政策')">《隐私政策》</a>
      </p>
      <p class="copyright-text">Fubangbang · 福州大学校园互助平台</p>
    </footer>

    <!-- 全局轻提示 Toast -->
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
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';
import { errorMessage as describeError } from '../api/request';

const router = useRouter();
const route = useRoute();
const session = useUserStore();
const account = ref('');
const password = ref('');
const rememberMe = ref(true);
const showPassword = ref(false);
const loading = ref(false);
const errorMessage = ref(typeof route.query.reason === 'string' ? route.query.reason : '');
const toastMessage = ref('');
const registeredSuccess = ref(route.query.registered === '1');
const isAccountFocused = ref(false);
const isPasswordFocused = ref(false);
let toastTimer: ReturnType<typeof setTimeout>;
function showToastMsg(msg: string) {
  toastMessage.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastMessage.value = '', 2400);
}
function handleForgetPassword() { showToastMsg('暂不支持自助重置，请联系项目管理员'); }
async function handleLogin() {
  if (loading.value) return;
  if (!account.value || !password.value) { errorMessage.value = '请输入账号和密码'; return; }
  errorMessage.value = '';
  loading.value = true;
  try {
    await session.login(account.value, password.value);
    if (rememberMe.value) localStorage.setItem('fubangbang_saved_account', account.value);
    else localStorage.removeItem('fubangbang_saved_account');
    const next = typeof route.query.redirect === 'string' ? route.query.redirect : '/idle';
    await router.replace(next.startsWith('/') && !next.startsWith('//') && !next.startsWith('/login') ? next : '/idle');
  } catch (error) { errorMessage.value = describeError(error); }
  finally { loading.value = false; }
}
onMounted(() => account.value = localStorage.getItem('fubangbang_saved_account') || '');
onUnmounted(() => clearTimeout(toastTimer));
</script>

<style scoped>
.login-page {
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

/* ================= 顶部品牌区域 ================= */
.brand-header {
  position: relative;
  padding: 38px 24px 22px 24px;
  overflow: hidden;
  background: linear-gradient(180deg, #F0FDF4 0%, #F9FDF7 60%, #FFFFFF 100%);
  flex-shrink: 0;
}

/* 校园水彩风景插画（极轻融入右上角，完全复用首页资源） */
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

/* ================= 表单主体区域（融入式干净布局） ================= */
.login-body {
  flex: 1;
  padding: 12px 24px 16px 24px;
  display: flex;
  flex-direction: column;
}

/* 注册成功横幅 */
.success-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background-color: var(--color-primary-light);
  border: 1px solid #D6F7D2;
  border-radius: var(--radius-md, 12px);
  margin-bottom: 20px;
}

.banner-icon {
  width: 18px;
  height: 18px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.banner-text {
  font-size: 13px;
  color: #166534;
  font-weight: 500;
}

/* 欢迎语标题 */
.welcome-section {
  margin-bottom: 28px;
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
  margin-top: 6px;
}

/* 表单结构 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 7px;
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
  width: 18px;
  height: 18px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.text-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14.5px;
  color: var(--color-text-main);
  font-family: inherit;
}

.text-input::placeholder {
  color: var(--color-text-placeholder);
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

/* 记住密码 & 忘记密码 */
.form-assist-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: -2px;
}

.remember-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--color-text-secondary);
  cursor: pointer;
  user-select: none;
}

.remember-checkbox {
  width: 15px;
  height: 15px;
  accent-color: var(--color-primary);
  border-radius: 3px;
  cursor: pointer;
}

.forget-link {
  font-size: 12.5px;
  color: var(--color-primary);
  font-weight: 500;
  cursor: pointer;
  background: none;
  border: none;
  padding: 2px;
}

.forget-link:active {
  opacity: 0.7;
}

/* 错误提示条 */
.error-tip-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: #FEF2F2;
  border: 1px solid #FEE2E2;
  color: #DC2626;
  font-size: 12.5px;
  padding: 9px 12px;
  border-radius: var(--radius-sm, 8px);
}

.error-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 登录主按钮（统一采用首页绿色规范与圆角） */
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

/* 注册引导单一行（仅保留一处） */
.register-nav-row {
  margin-top: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13.5px;
}

.register-hint {
  color: var(--color-text-secondary);
}

.register-action {
  color: var(--color-primary);
  font-weight: 600;
}

.register-action:active {
  opacity: 0.75;
}

/* 校园认证说明（自然微弱的辅助行） */
.campus-auth-note {
  margin-top: 36px;
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

/* ================= 底部版权与协议 ================= */
.login-footer {
  margin-top: auto;
  padding: 16px 24px 20px 24px;
  text-align: center;
  flex-shrink: 0;
}

.agreement-text {
  font-size: 11px;
  color: var(--color-text-muted);
  line-height: 1.5;
}

.agreement-text a {
  color: var(--color-primary);
}

.agreement-text a:active {
  opacity: 0.7;
}

.copyright-text {
  font-size: 10.5px;
  color: #CBD5E1;
  margin-top: 6px;
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
