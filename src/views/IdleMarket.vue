<template>
  <div class="idle-market-page">
    <!-- 顶部状态栏及导航 -->
    <header class="page-top-bar">
      <div class="top-title-row">
        <h2 class="page-main-title">二手闲置</h2>
        <span class="sub-location">福州大学 · 旗山校区</span>
      </div>

      <form class="market-search" @submit.prevent="search">
        <input v-model="keyword" aria-label="搜索闲置" placeholder="搜索商品名称或描述" maxlength="120" />
        <button type="submit">搜索</button>
      </form>
      <!-- 分类筛选横向滑动栏 -->
      <div class="category-tabs-wrapper">
        <button
          v-for="cat in categories"
          :key="cat"
          type="button"
          class="cat-tab-pill"
          :class="{ 'is-active': activeCategory === cat }"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <!-- 排序过滤条 -->
      <div class="filter-bar">
        <span class="result-count">已加载 {{ filteredList.length }} 件闲置宝贝</span>
        <div class="sort-options">
          <button
            class="sort-btn"
            :class="{ 'is-active': sortBy === 'latest' }"
            @click="sortBy = 'latest'"
          >
            最新
          </button>
          <span class="sort-divider">|</span>
          <button
            class="sort-btn"
            :class="{ 'is-active': sortBy === 'price-asc' }"
            @click="sortBy = 'price-asc'"
          >
            本页价格最低
          </button>
        </div>
      </div>
    </header>

    <!-- 商品双列网格 -->
    <main class="products-grid-container">
      <RequestState v-if="loading || loadError" :loading="loading" :error="loadError" @retry="load(false)" />
      <div v-else-if="filteredList.length > 0" class="products-grid">
        <ProductCard
          v-for="item in filteredList"
          :key="item.id"
          :product="item"
          layout-mode="grid"
          @click="handleProductClick"
        />
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon">📦</div>
        <p>暂无该分类下的闲置商品</p>
        <button class="reset-btn" @click="activeCategory = '全部'">查看全部闲置</button>
      </div>
      <button v-if="hasMore && !loadError" type="button" class="load-more" :disabled="loading" @click="load(true)">加载更多</button>
    </main>

    <!-- 浮动快速发布闲置原型按钮 -->
    <Teleport to="#app-mobile-frame">
      <button class="fab-publish-btn" @click="handlePublish">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="fab-icon">
          <line x1="12" y1="5" x2="12" y2="19" stroke-width="2.5" stroke-linecap="round"/>
          <line x1="5" y1="12" x2="19" y2="12" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <span>发布</span>
      </button>
    </Teleport>

    <!-- 原型提示 Toast -->
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import ProductCard from '../components/product/ProductCard.vue';
import RequestState from '../components/common/RequestState.vue';
import { getProductList, productCategories } from '../api/product';
import { errorMessage } from '../api/request';
import type { Product } from '../types';
const router = useRouter();
const route = useRoute();
const categories = ['全部', ...productCategories];
const activeCategory = ref('全部');
const keyword = ref(typeof route.query.keyword === 'string' ? route.query.keyword : '');
const sortBy = ref<'latest' | 'price-asc'>('latest');
const toastMessage = ref('');
const allProducts = ref<Product[]>([]);
const loading = ref(false);
const loadError = ref('');
const hasMore = ref(false);
let page = 1;
let sequence = 0;
let controller: AbortController | undefined;
const filteredList = computed(() => sortBy.value === 'price-asc'
  ? [...allProducts.value].sort((a, b) => a.price - b.price) : allProducts.value);
async function load(append = false) {
  const current = ++sequence;
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  loadError.value = '';
  if (!append) allProducts.value = [];
  const requestedPage = append ? page + 1 : 1;
  try {
    const items = await getProductList({ keyword: keyword.value.trim(), category: activeCategory.value, page: requestedPage, page_size: 20 }, controller.signal);
    if (sequence !== current) return;
    allProducts.value = append ? [...allProducts.value, ...items] : items;
    page = requestedPage;
    hasMore.value = items.length === 20;
  } catch (error) { if (sequence === current) loadError.value = errorMessage(error); }
  finally { if (sequence === current) loading.value = false; }
}
function search() { void router.replace({ path: '/idle', query: keyword.value.trim() ? { keyword: keyword.value.trim() } : {} }); void load(); }
watch(activeCategory, () => void load());
onMounted(() => void load());
onUnmounted(() => { sequence++; controller?.abort(); });
function handleProductClick(product: Product) { void router.push(`/product/${product.id}`); }
function handlePublish() { void router.push('/publish'); }
</script>

<style scoped>
.market-search { display: flex; gap: var(--space-sm); margin: var(--space-md) 0; }
.market-search input { min-width: 0; flex: 1; padding: var(--space-md); border: 1px solid var(--color-border-regular); border-radius: var(--radius-pill); background: var(--color-bg-card); }
.market-search button, .load-more { min-height: 44px; padding: var(--space-sm) var(--space-base); color: var(--color-primary-dark); }
.load-more { display: block; margin: var(--space-md) auto; }

.idle-market-page {
  width: 100%;
  padding-bottom: 24px;
  background-color: var(--color-bg-page);
  display: flex;
  flex-direction: column;
}

.page-top-bar {
  background-color: #FFFFFF;
  padding: 16px 16px 10px 16px;
  border-bottom: 1px solid #F1F5F9;
  position: sticky;
  top: 0;
  z-index: 10;
}

.top-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.page-main-title {
  font-size: 20px;
  font-weight: 800;
  color: #1E293B;
  letter-spacing: -0.3px;
}

.sub-location {
  font-size: 11px;
  color: #64748B;
  background-color: #F8FAFC;
  padding: 3px 8px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.category-tabs-wrapper {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding-bottom: 4px;
}

.category-tabs-wrapper::-webkit-scrollbar {
  display: none;
}

.cat-tab-pill {
  padding: 6px 14px;
  border-radius: 18px;
  background-color: #F8FAFC;
  color: #64748B;
  font-size: 12.5px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.cat-tab-pill.is-active {
  background-color: #EDFBEB;
  color: var(--color-primary);
  border-color: rgba(16, 185, 88, 0.3);
  font-weight: 600;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  font-size: 11.5px;
  color: #94A3B8;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sort-btn {
  color: #94A3B8;
  font-size: 11.5px;
  transition: color 0.15s ease;
}

.sort-btn.is-active {
  color: var(--color-primary);
  font-weight: 600;
}

.sort-divider {
  color: #E2E8F0;
  font-size: 10px;
}

.products-grid-container {
  padding: 14px 16px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94A3B8;
  font-size: 13px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.reset-btn {
  margin-top: 14px;
  padding: 6px 16px;
  background-color: var(--color-primary);
  color: #FFFFFF;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

/* 浮动发布按钮（定位在 App 手机容器右下角） */
.fab-publish-btn {
  position: absolute;
  right: 18px;
  bottom: 74px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--color-primary-gradient);
  color: #FFFFFF;
  padding: 10px 18px;
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(16, 185, 88, 0.35);
  font-size: 13.5px;
  font-weight: 600;
  z-index: 40;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.fab-publish-btn:active {
  transform: scale(0.94);
}

.fab-icon {
  width: 16px;
  height: 16px;
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
