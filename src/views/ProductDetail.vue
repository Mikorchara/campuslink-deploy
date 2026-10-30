<template>
  <div class="product-detail-page">
    <!-- 顶部导航条 -->
    <header class="detail-header">
      <button class="header-action-btn" @click="handleBack" aria-label="返回">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="action-icon">
          <path d="M15 19l-7-7 7-7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <span class="header-title">商品详情</span>
      <div class="header-right-actions">
        <button class="header-action-btn" :disabled="!product || busy" @click="toggleFavorite" aria-label="收藏商品">
          <svg viewBox="0 0 24 24" :fill="isFavorited ? 'var(--color-price)' : 'none'" :stroke="isFavorited ? 'var(--color-price)' : 'currentColor'" class="action-icon">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke-width="2"/>
          </svg>
        </button>
        <button class="header-action-btn" @click="handleShareTip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="action-icon">
            <circle cx="18" cy="5" r="3" stroke-width="2"/>
            <circle cx="6" cy="12" r="3" stroke-width="2"/>
            <circle cx="18" cy="19" r="3" stroke-width="2"/>
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" stroke-width="2"/>
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" stroke-width="2"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- 中间独立滚动正文内容区 -->
    <RequestState v-if="loading || loadError" :loading="loading" :error="loadError" @retry="load" />
    <div v-else-if="product" class="detail-scroll-body">
      <!-- 商品大图 -->
      <div class="hero-image-box">
        <img :src="product.image_url" :alt="product.title" class="hero-image" />
        <span class="category-chip">{{ product.category }}</span>
      </div>

      <!-- 核心信息卡片 -->
      <div class="product-main-card">
        <div class="price-section">
          <div class="price-left">
            <span class="currency">¥</span>
            <span class="price-val">{{ product.price }}</span>
          </div>
          <span class="status-pill">{{ statusLabels[product.status] }}</span>
        </div>

        <h1 class="item-title">{{ product.title }}</h1>
        <p class="item-desc">{{ product.description }}</p>
        <LikeButton :key="product.id" kind="product" :id="product.id" />

        <div class="meta-tags">
          <div class="meta-tag-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="tag-icon">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke-width="2"/>
              <circle cx="12" cy="10" r="3" stroke-width="2"/>
            </svg>
            <span>{{ product.location || '福州大学旗山校区面交' }}</span>
          </div>
          <div class="meta-tag-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="tag-icon">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <polyline points="12 6 12 12 16 14" stroke-width="2"/>
            </svg>
            <span>发布于 {{ product.time_ago }}</span>
          </div>
        </div>
      </div>

      <!-- 卖家卡片 -->
      <div class="seller-card">
        <img :src="product.seller.avatar" :alt="product.seller.name" class="seller-big-avatar" />
        <div class="seller-details">
          <div class="seller-name-row">
            <span class="seller-name">{{ product.seller.name }}</span>
            <span class="fzu-verify-badge">平台用户</span>
          </div>
          <span class="seller-tip">请通过联系方式沟通，约定校内面交</span>
        </div>
      </div>

      <!-- 校园互助面交安全提醒 -->
      <div class="safety-tip-card">
        <div class="tip-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="shield-icon">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke-width="2"/>
          </svg>
          <span>校园安全互助提示</span>
        </div>
        <p class="tip-content">福帮帮建议选择图书馆、教学楼或宿舍大厅等人流密集处当面验货交付，拒绝提前私下转账，守护校园信用生态。</p>
      </div>

      <!-- 物品成色及保障说明 -->
      <div class="product-guarantee-card">
        <div class="guarantee-header">
          <span class="guarantee-title">校园面交建议</span>
          <span class="guarantee-tag">当面验货</span>
        </div>
        <div class="guarantee-list">
          <div class="guarantee-item">
            <span class="dot"></span>
            <span>平台使用独立账号，尚未接入学校学号认证，请自行核实交易信息。</span>
          </div>
          <div class="guarantee-item">
            <span class="dot"></span>
            <span>当面验货交付：支持旗山校区图书馆、风雨操场、各生活区面交验货。</span>
          </div>
          <div class="guarantee-item">
            <span class="dot"></span>
            <span>无中介服务费：福帮帮为校园纯公益互助平台，无额外费用。</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏（固定在 App 容器底部） -->
    <footer v-if="product" class="action-footer-bar">
      <template v-if="isOwner"><router-link class="sub-btn" to="/my-products">我的发布</router-link><router-link class="primary-buy-btn" :to="`/product/${product.id}/edit`">编辑商品</router-link></template>
      <template v-else>
      <button class="sub-btn" :disabled="busy" @click="handleChatTip">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="btn-icon">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" stroke-width="2"/>
        </svg>
        <span>联系卖家</span>
      </button>
      <button class="primary-buy-btn" :disabled="busy || product.status !== 'AVAILABLE'" @click="handleBuyTip">
        <span>{{ product.status === 'AVAILABLE' ? '申请预订' : statusLabels[product.status] }}</span>
      </button>
      </template>
    </footer>

    <AppDialog :open="contactOpen" title="联系卖家" @close="contactOpen = false">
      <p>{{ contact?.name }}</p><p>邮箱：{{ contact?.email }}</p><p>其他联系方式：{{ contact?.contact || '卖家尚未填写，可通过邮箱联系' }}</p>
    </AppDialog>
    <AppDialog :open="bookingOpen" title="申请预订" @close="bookingOpen = false">
      <label class="account-field">给卖家留言<textarea v-model="bookingNote" maxlength="500" placeholder="如面交时间和地点" /></label>
      <p v-if="bookingError" class="account-error" role="alert">{{ bookingError }}</p>
      <div class="account-actions"><button :disabled="busy" @click="book">{{ busy ? '正在提交…' : '发送预订请求' }}</button></div>
    </AppDialog>
    <!-- 操作反馈 -->
    <Teleport to="#app-mobile-frame">
      <Transition name="toast">
        <div v-if="toastMessage" class="prototype-toast">
          {{ toastMessage }}
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getProductDetail, getSellerContact, statusLabels } from '../api/product';
import { getFavoriteState, setFavorite, requestTransaction } from '../api/trade';
import { errorMessage } from '../api/request';
import { useUserStore } from '../stores/user';
import RequestState from '../components/common/RequestState.vue';
import AppDialog from '../components/common/AppDialog.vue';
import LikeButton from '../components/common/LikeButton.vue';
import type { Product } from '../types';
const route = useRoute();
const router = useRouter();
const session = useUserStore();
const product = ref<Product | null>(null);
const loading = ref(false), loadError = ref(''), busy = ref(false);
const isOwner = computed(() => product.value?.seller.id === session.user?.id);
const isFavorited = ref(false), toastMessage = ref('');
const contactOpen = ref(false), bookingOpen = ref(false);
const contact = ref<{ name: string; email: string; contact: string | null } | null>(null);
const bookingNote = ref(''), bookingError = ref('');
let sequence = 0;
let timer: ReturnType<typeof setTimeout>;
function showToast(message: string) { toastMessage.value = message; clearTimeout(timer); timer = setTimeout(() => toastMessage.value = '', 2600); }
async function load() {
  const version = ++sequence;
  loading.value = true; loadError.value = ''; product.value = null; isFavorited.value = false;
  try {
    const id = Number(route.params.id);
    if (!Number.isSafeInteger(id) || id < 1) throw new Error('商品不存在');
    const item = await getProductDetail(id);
    if (sequence !== version) return;
    product.value = item;
    if (session.isLoggedIn) {
      try { const state = await getFavoriteState(id); if (sequence === version) isFavorited.value = state; }
      catch (error) { if (sequence === version) showToast(errorMessage(error)); }
    }
  } catch (error) { if (sequence === version) loadError.value = errorMessage(error); }
  finally { if (sequence === version) loading.value = false; }
}
function requireLogin() {
  if (session.isLoggedIn) return true;
  void router.push({ path: '/login', query: { redirect: route.fullPath } });
  return false;
}
async function toggleFavorite() {
  if (!product.value || busy.value || !requireLogin()) return;
  busy.value = true;
  try { isFavorited.value = await setFavorite(product.value.id, !isFavorited.value); showToast(isFavorited.value ? '已收藏' : '已取消收藏'); }
  catch (error) { showToast(errorMessage(error)); } finally { busy.value = false; }
}
async function handleShareTip() { try { await navigator.clipboard.writeText(window.location.href); showToast('商品链接已复制'); } catch { showToast('无法复制，请从地址栏复制商品链接'); } }
function handleBack() { void router.push('/idle'); }
async function handleChatTip() {
  if (!product.value || busy.value || !requireLogin()) return;
  busy.value = true;
  try { contact.value = await getSellerContact(product.value.id); contactOpen.value = true; }
  catch (error) { showToast(errorMessage(error)); } finally { busy.value = false; }
}
function handleBuyTip() { if (requireLogin()) { bookingError.value = ''; bookingOpen.value = true; } }
async function book() {
  if (!product.value || busy.value) return;
  busy.value = true; bookingError.value = '';
  try { await requestTransaction(product.value.id, bookingNote.value.trim()); bookingOpen.value = false; await router.push('/transactions'); }
  catch (error) { bookingError.value = errorMessage(error); } finally { busy.value = false; }
}
watch(() => route.params.id, () => void load(), { immediate: true });
onUnmounted(() => { sequence++; clearTimeout(timer); });
</script>

<style scoped>
.product-detail-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-bg-page);
  position: relative;
}

.detail-header {
  height: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background-color: #FFFFFF;
  z-index: 10;
  border-bottom: 1px solid #F1F5F9;
}

.detail-scroll-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 20px;
  display: flex;
  flex-direction: column;
}

.header-action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1E293B;
  border-radius: 50%;
}

.header-action-btn:active {
  background-color: #F1F5F9;
}

.action-icon {
  width: 20px;
  height: 20px;
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  color: #1E293B;
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.hero-image-box {
  width: 100%;
  aspect-ratio: 1.4 / 1;
  position: relative;
  background-color: #000;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.category-chip {
  position: absolute;
  top: 12px;
  left: 12px;
  background-color: rgba(15, 23, 42, 0.7);
  color: #FFFFFF;
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.product-main-card {
  margin: 12px 16px;
  background-color: #FFFFFF;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.price-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.price-left {
  color: #FF2442;
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.currency {
  font-size: 15px;
  font-weight: 700;
}

.price-val {
  font-size: 26px;
  font-weight: 800;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.status-pill {
  font-size: 11px;
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 600;
}

.item-title {
  font-size: 17px;
  font-weight: 700;
  color: #1E293B;
  line-height: 1.4;
  margin-bottom: 10px;
}

.item-desc {
  font-size: 13.5px;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 14px;
}

.meta-tags {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid #F8FAFC;
}

.meta-tag-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748B;
}

.tag-icon {
  width: 14px;
  height: 14px;
  color: #94A3B8;
}

.seller-card {
  margin: 0 16px 12px 16px;
  background-color: #FFFFFF;
  border-radius: 16px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.seller-big-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
}

.seller-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.seller-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.seller-name {
  font-size: 14px;
  font-weight: 700;
  color: #1E293B;
}

.fzu-verify-badge {
  font-size: 10px;
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.seller-tip {
  font-size: 11px;
  color: #94A3B8;
}

.safety-tip-card {
  margin: 0 16px 14px 16px;
  background-color: #F8FAFC;
  border: 1px dashed #CBD5E1;
  border-radius: 14px;
  padding: 12px;
}

.tip-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}

.shield-icon {
  width: 14px;
  height: 14px;
  color: var(--color-primary);
}

.tip-content {
  font-size: 11px;
  color: #64748B;
  line-height: 1.5;
}

.product-guarantee-card {
  margin: 0 16px 18px 16px;
  background-color: #FFFFFF;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  border: 1px solid #F1F5F9;
}

.guarantee-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.guarantee-title {
  font-size: 13px;
  font-weight: 700;
  color: #1E293B;
}

.guarantee-tag {
  font-size: 10.5px;
  color: #16A34A;
  background-color: #EAF9EC;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.guarantee-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guarantee-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 11.5px;
  color: #475569;
  line-height: 1.45;
}

.guarantee-item .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--color-primary);
  margin-top: 6px;
  flex-shrink: 0;
}

.action-footer-bar {
  width: 100%;
  height: 60px;
  flex-shrink: 0;
  background-color: #FFFFFF;
  border-top: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.05);
  z-index: 50;
  box-sizing: border-box;
}

.sub-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #475569;
  font-size: 10.5px;
  gap: 2px;
  padding: 0 8px;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.primary-buy-btn {
  flex: 1;
  height: 42px;
  background: var(--color-primary-gradient);
  color: #FFFFFF;
  border-radius: 22px;
  font-size: 14.5px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(16, 185, 88, 0.25);
  transition: transform 0.15s ease;
}

.primary-buy-btn:active {
  transform: scale(0.97);
}

/* Toast 原型提示 */
.prototype-toast {
  position: absolute;
  bottom: 74px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(15, 23, 42, 0.9);
  color: #FFFFFF;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  z-index: 300;
  white-space: nowrap;
  backdrop-filter: blur(8px);
  pointer-events: none;
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 15px);
}
</style>
