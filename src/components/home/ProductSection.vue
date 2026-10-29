<template>
  <section class="product-section">
    <!-- 区域顶部标题栏 -->
    <div class="section-header">
      <div class="header-left">
        <span class="indicator-bar"></span>
        <h3 class="section-title">{{ title }}</h3>
      </div>
      <div class="header-right" @click="handleMoreClick">
        <span class="more-text">查看更多</span>
        <svg class="more-arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor">
          <path d="M6 3.5L10.5 8L6 12.5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <!-- 横向商品滚动容器 -->
    <div class="products-scroll-container">
      <div class="products-list">
        <ProductCard
          v-for="item in products"
          :key="item.id"
          :product="item"
          layout-mode="horizontal"
          @click="handleProductClick"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import ProductCard from '../product/ProductCard.vue';
import type { Product } from '../../types';

interface Props {
  title?: string;
  products: Product[];
  moreRoute?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: '最新闲置',
  moreRoute: '/idle'
});

const emit = defineEmits<{
  (e: 'product-click', product: Product): void;
  (e: 'more-click'): void;
}>();

const router = useRouter();

const handleMoreClick = () => {
  emit('more-click');
  if (props.moreRoute) {
    router.push(props.moreRoute);
  }
};

const handleProductClick = (product: Product) => {
  emit('product-click', product);
};
</script>

<style scoped>
.product-section {
  width: 100%;
  margin-top: 14px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 10px 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 7px;
}

.indicator-bar {
  width: 3.5px;
  height: 15px;
  background-color: var(--color-primary);
  border-radius: 2px;
  display: inline-block;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1E293B;
  letter-spacing: -0.2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: #8E9BAE;
  cursor: pointer;
  transition: color 0.15s ease;
  user-select: none;
}

.header-right:active {
  color: var(--color-text-main);
}

.more-text {
  font-weight: 400;
}

.more-arrow {
  width: 13px;
  height: 13px;
  color: #8E9BAE;
}

/* 横向水平滚动容器 */
.products-scroll-container {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  padding: 2px 0 6px 0;
  scrollbar-width: none; /* Firefox */
}

.products-scroll-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.products-list {
  display: flex;
  gap: 11px;
  padding: 0 16px;
  width: max-content;
}
</style>
