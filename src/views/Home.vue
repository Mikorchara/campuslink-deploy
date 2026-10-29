<template>
  <div class="home-page">
    <!-- 顶部校园插画、Logo 与标语 -->
    <AppHeader
      title="福帮帮"
      sub-title="福州大学校园互助平台"
      slogan="在福大，遇见更好的校园生活"
    />

    <!-- 搜索栏 -->
    <div class="search-section">
      <SearchBar
        v-model="searchQuery"
        placeholder="搜索闲置 / 帖子 / 攻略"
        @click="handleSearchTrigger"
        @search="handleDoSearch"
        @scan="handleScanTrigger"
      />
    </div>

    <!-- 首页两大核心入口：二手闲置 & 校园论坛 -->
    <section class="feature-entries-section">
      <div class="entries-grid">
        <FeatureEntryCard
          title="二手闲置"
          subtitle="教材、数码、生活用品"
          icon="/assets/images/icon_idle_bag.png"
          theme="green"
          route="/idle"
        />
        <FeatureEntryCard
          title="校园论坛"
          subtitle="学习、生活、经验分享"
          icon="/assets/images/icon_forum_chat.png"
          theme="blue"
          route="/forum"
        />
      </div>
    </section>

    <!-- 最新闲置商品展示区 -->
    <RequestState v-if="productsLoading || productsError" :loading="productsLoading" :error="productsError" @retry="loadProducts" />
    <RequestState v-else-if="!products.length" empty-text="暂时没有闲置，发布第一件吧" />
    <ProductSection v-else
      title="最新闲置"
      :products="products"
      more-route="/idle"
      @product-click="handleProductDetail"
    />

    <!-- 校园论坛精选区 -->
    <RequestState v-if="forumLoading || forumError" :loading="forumLoading" :error="forumError" @retry="loadForum" />
    <RequestState v-else-if="!forumPosts.length" empty-text="校园论坛还没有帖子，欢迎分享第一篇经验" />
    <ForumSection v-else
      title="最新校园分享"
      :posts="forumPosts"
      more-route="/forum"
      @post-click="handlePostDetail"
    />

    <!-- 搜索浮层交互（点击搜索框时进入） -->
    <Teleport to="#app-mobile-frame">
      <Transition name="fade">
        <div v-if="isSearchActive" class="search-modal-backdrop" @click="isSearchActive = false">
          <div class="search-modal-content" @click.stop>
            <div class="search-modal-header">
              <div class="modal-search-box">
                <svg class="search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor">
                  <circle cx="8.5" cy="8.5" r="5.5" stroke-width="2" stroke-linecap="round" />
                  <path d="M13 13L17.5 17.5" stroke-width="2" stroke-linecap="round" />
                </svg>
                <input
                  v-model="modalSearchKeyword"
                  type="text"
                  placeholder="搜索闲置商品、论坛攻略..."
                  class="modal-input"
                  autofocus
                  @keydown.enter="performModalSearch"
                />
                <button
                  v-if="modalSearchKeyword"
                  class="modal-clear-btn"
                  @click="modalSearchKeyword = ''"
                >
                  ✕
                </button>
              </div>
              <button class="modal-cancel-btn" @click="isSearchActive = false">取消</button>
            </div>

            <!-- 搜索历史与热门标签 -->
            <div class="search-suggestions" v-if="!modalSearchKeyword">
              <div class="hot-searches">
                <div class="section-title-sm">热门搜索</div>
                <div class="hot-tags">
                  <span
                    v-for="tag in hotKeywords"
                    :key="tag"
                    class="hot-tag"
                    @click="selectKeyword(tag)"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              <div class="history-searches">
                <div class="section-title-sm">历史搜索</div>
                <div class="history-list">
                  <span class="history-item" @click="selectKeyword('高数教材')">高数教材</span>
                  <span class="history-item" @click="selectKeyword('自习室攻略')">自习室攻略</span>
                  <span class="history-item" @click="selectKeyword('台灯')">台灯</span>
                </div>
              </div>
            </div>

            <!-- 搜索结果预览列表 -->
            <div class="search-results-list" v-else>
              <RequestState v-if="searchLoading || searchError" :loading="searchLoading" :error="searchError" @retry="searchPreview(modalSearchKeyword)" />
              <button type="button" class="modal-cancel-btn" @click="performModalSearch">查看全部商品结果</button>
              <button type="button" class="modal-cancel-btn" @click="performForumSearch">查看全部帖子结果</button>
              <div class="result-category" v-if="filteredProducts.length > 0">
                <div class="category-header">闲置商品 ({{ filteredProducts.length }})</div>
                <div
                  v-for="p in filteredProducts"
                  :key="p.id"
                  class="search-result-item"
                  @click="navigateToProduct(p.id)"
                >
                  <img :src="p.image_url" :alt="p.title" class="result-thumb" />
                  <div class="result-details">
                    <span class="result-title">{{ p.title }}</span>
                    <span class="result-price">¥{{ p.price }}</span>
                  </div>
                </div>
              </div>

              <div class="result-category" v-if="filteredPosts.length > 0">
                <div class="category-header">论坛帖子 ({{ filteredPosts.length }})</div>
                <div
                  v-for="post in filteredPosts"
                  :key="post.id"
                  class="search-result-item"
                  @click="navigateToPost(post.id)"
                >
                  <img :src="post.image_url" :alt="post.title" class="result-thumb" />
                  <div class="result-details">
                    <span class="result-title">{{ post.title }}</span>
                    <span class="result-tag-badge">{{ post.tag }}</span>
                  </div>
                </div>
              </div>

              <div v-if="!searchLoading && !searchError && filteredProducts.length === 0 && filteredPosts.length === 0" class="no-result">
                暂未找到与 “{{ modalSearchKeyword }}” 相关的闲置或帖子
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 原型状态提示 Toast -->
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
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppHeader from '../components/common/AppHeader.vue';
import SearchBar from '../components/common/SearchBar.vue';
import FeatureEntryCard from '../components/home/FeatureEntryCard.vue';
import ProductSection from '../components/home/ProductSection.vue';
import ForumSection from '../components/home/ForumSection.vue';
import { getForumPosts } from '../api/forum';
import { getProductList } from '../api/product';
import { errorMessage } from '../api/request';
import RequestState from '../components/common/RequestState.vue';
import type { Product, ForumPost } from '../types';

const router = useRouter();

const searchQuery = ref('');
const isSearchActive = ref(false);
const modalSearchKeyword = ref('');
const toastMessage = ref('');

const products = ref<Product[]>([]);
const forumPosts = ref<ForumPost[]>([]);
const forumLoading = ref(false), forumError = ref('');

const hotKeywords = ['高等数学', 'AirPods', '护眼台灯', '新生报到', '自习室预约', '四六级真题', '电风扇'];

const showToast = (msg: string) => {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = '';
  }, 2200);
};

const handleSearchTrigger = () => {
  isSearchActive.value = true;
};

const handleDoSearch = (keyword: string) => {
  modalSearchKeyword.value = keyword;
  isSearchActive.value = true;
};

const handleScanTrigger = () => {
  showToast('暂不支持扫一扫，可使用关键词搜索商品');
};

const handleProductDetail = (product: Product) => {
  router.push(`/product/${product.id}`);
};

const handlePostDetail = (post: ForumPost) => {
  router.push(`/forum/${post.id}`);
};

const selectKeyword = (kw: string) => {
  modalSearchKeyword.value = kw;
};

const performModalSearch = () => {
  isSearchActive.value = false;
  void router.push({ path: '/idle', query: { keyword: modalSearchKeyword.value.trim() } });
};
const performForumSearch = () => {
  isSearchActive.value = false;
  void router.push({ path: '/forum', query: { keyword: modalSearchKeyword.value.trim() } });
};

const navigateToProduct = (id: number) => {
  isSearchActive.value = false;
  router.push(`/product/${id}`);
};

const navigateToPost = (id: number) => {
  isSearchActive.value = false;
  router.push(`/forum/${id}`);
};

const productsLoading = ref(false);
const productsError = ref('');
const filteredProducts = ref<Product[]>([]);
const filteredPosts = ref<ForumPost[]>([]);
const searchError = ref('');
const searchLoading = ref(false);
let searchTimer: ReturnType<typeof setTimeout>;
let searchVersion = 0;
async function loadProducts() {
  productsLoading.value = true;
  productsError.value = '';
  try { products.value = await getProductList({ page_size: 6 }); }
  catch (error) { productsError.value = errorMessage(error); }
  finally { productsLoading.value = false; }
}
async function loadForum() {
  forumLoading.value = true; forumError.value = '';
  try { forumPosts.value = (await getForumPosts({ page_size: 3 })).items; }
  catch (error) { forumError.value = errorMessage(error); }
  finally { forumLoading.value = false; }
}
function searchPreview(value: string) {
  const version = ++searchVersion;
  clearTimeout(searchTimer);
  filteredProducts.value = [];
  filteredPosts.value = [];
  searchError.value = '';
  searchLoading.value = Boolean(value.trim());
  if (!value.trim()) return;
  searchTimer = setTimeout(async () => {
    try {
      const [items, posts] = await Promise.all([getProductList({ keyword: value.trim(), page_size: 10 }), getForumPosts({ keyword: value.trim(), page_size: 10 })]);
      if (version === searchVersion) { filteredProducts.value = items; filteredPosts.value = posts.items; }
    } catch (error) { if (version === searchVersion) searchError.value = errorMessage(error); }
    finally { if (version === searchVersion) searchLoading.value = false; }
  }, 300);
}
watch(modalSearchKeyword, searchPreview);
onMounted(() => { void loadProducts(); void loadForum(); });
onUnmounted(() => { searchVersion++; clearTimeout(searchTimer); });

</script>

<style scoped>
.home-page {
  width: 100%;
  padding-bottom: 24px;
  background-color: var(--color-bg-page);
  display: flex;
  flex-direction: column;
}

.search-section {
  margin-top: 2px;
  position: relative;
  z-index: 5;
}

.feature-entries-section {
  width: 100%;
  padding: 14px 16px 0 16px;
  box-sizing: border-box;
}

.entries-grid {
  display: flex;
  gap: 12px;
  width: 100%;
}

/* 搜索交互浮层 */
.search-modal-backdrop {
  position: absolute;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(6px);
  z-index: 200;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: hidden;
}

.search-modal-content {
  width: 100%;
  height: 100%;
  background-color: #FFFFFF;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
}

.search-modal-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #F1F5F9;
  gap: 12px;
  position: sticky;
  top: 0;
  background-color: #FFFFFF;
  z-index: 2;
}

.modal-search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: #F1F5F9;
  height: 40px;
  border-radius: 20px;
  padding: 0 12px;
  gap: 8px;
}

.modal-search-box .search-icon {
  width: 16px;
  height: 16px;
  color: #64748B;
}

.modal-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 13.5px;
  color: #1E293B;
}

.modal-clear-btn {
  color: #94A3B8;
  font-size: 14px;
}

.modal-cancel-btn {
  font-size: 14px;
  color: #64748B;
  font-weight: 500;
}

.search-suggestions {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title-sm {
  font-size: 12px;
  font-weight: 600;
  color: #64748B;
  margin-bottom: 10px;
  text-transform: uppercase;
}

.hot-tags, .history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-tag, .history-item {
  padding: 5px 12px;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  font-size: 12px;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}

.hot-tag:active, .history-item:active {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.search-results-list {
  padding: 12px 16px;
}

.category-header {
  font-size: 12px;
  font-weight: 600;
  color: #94A3B8;
  margin-bottom: 8px;
  padding-left: 2px;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 9px 8px;
  border-radius: 8px;
  gap: 12px;
  cursor: pointer;
  border-bottom: 1px solid #F8FAFC;
}

.search-result-item:active {
  background-color: #F1F5F9;
}

.result-thumb {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
}

.result-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-title {
  font-size: 13.5px;
  color: #1E293B;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-price {
  font-size: 13px;
  color: #FF2442;
  font-weight: 700;
}

.result-tag-badge {
  font-size: 11px;
  color: #2563EB;
}

.no-result {
  text-align: center;
  padding: 40px 16px;
  color: #94A3B8;
  font-size: 13px;
}

/* 浮层动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Toast 原型提示 */
.prototype-toast {
  position: absolute;
  bottom: 74px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(15, 23, 42, 0.88);
  color: #FFFFFF;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12.5px;
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
