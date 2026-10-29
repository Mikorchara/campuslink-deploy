<template>
  <div
    class="product-card"
    :class="[layoutMode === 'horizontal' ? 'mode-horizontal' : 'mode-grid']"
    @click="handleClick"
  >
    <!-- 商品封面图 -->
    <div class="image-box">
      <img
        :src="product.image_url"
        :alt="product.title"
        class="product-image"
        loading="lazy"
      />
      <!-- 预留状态标签（如已预订/已售出） -->
      <span
        v-if="product.status && product.status !== 'AVAILABLE'"
        class="status-badge"
        :class="[`status-${product.status.toLowerCase()}`]"
      >
        {{ formatStatus(product.status) }}
      </span>
    </div>

    <!-- 商品信息区 -->
    <div class="product-info">
      <!-- 标题 -->
      <h4 class="product-title truncate-1" :title="product.title">
        {{ product.title }}
      </h4>

      <!-- 价格 -->
      <div class="price-row">
        <span class="currency-symbol">¥</span>
        <span class="price-value">{{ formatPrice(product.price) }}</span>
      </div>

      <!-- 卖家头像与发布时间 -->
      <div class="seller-meta">
        <div class="seller-user">
          <img
            :src="product.seller.avatar"
            :alt="product.seller.name"
            class="seller-avatar"
          />
          <span class="seller-name truncate-1">{{ product.seller.name }}</span>
        </div>
        <span class="time-ago">{{ product.time_ago }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product, ProductStatus } from '../../types';

interface Props {
  product: Product;
  layoutMode?: 'horizontal' | 'grid';
}

const props = withDefaults(defineProps<Props>(), {
  layoutMode: 'horizontal'
});

const emit = defineEmits<{
  (e: 'click', product: Product): void;
}>();

const handleClick = () => {
  emit('click', props.product);
};

const formatPrice = (price: number) => {
  return price % 1 === 0 ? price : price.toFixed(2);
};

const formatStatus = (status: ProductStatus) => {
  switch (status) {
    case 'RESERVED': return '已预约';
    case 'SOLD': return '已售出';
    case 'OFFLINE': return '已下架';
    default: return '';
  }
};
</script>

<style scoped>
.product-card {
  background-color: var(--color-bg-card);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
  user-select: none;
  border: 1px solid rgba(241, 245, 249, 0.85);
  box-sizing: border-box;
}

.product-card:active {
  transform: scale(0.97);
}

/* 首页横向滚动模式卡片宽度适配 440px 屏宽 */
.product-card.mode-horizontal {
  width: 154px;
  flex-shrink: 0;
}

/* 列表页网格模式卡片自适应 */
.product-card.mode-grid {
  width: 100%;
}

.image-box {
  width: 100%;
  aspect-ratio: 1.55 / 1;
  overflow: hidden;
  position: relative;
  background-color: #F8FAFC;
}

.mode-grid .image-box {
  aspect-ratio: 1.25 / 1;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image {
  transform: scale(1.03);
}

.status-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  backdrop-filter: blur(4px);
}

.status-reserved {
  background: rgba(245, 158, 11, 0.9);
  color: #FFFFFF;
}

.status-sold {
  background: rgba(100, 116, 139, 0.88);
  color: #FFFFFF;
}

.status-offline {
  background: rgba(15, 23, 42, 0.75);
  color: #FFFFFF;
}

.product-info {
  padding: 8px 10px 10px 10px;
  display: flex;
  flex-direction: column;
}

.product-title {
  font-size: 13.5px;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.35;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.2px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 3px;
  color: #FF2442;
  margin-bottom: 6px;
}

.currency-symbol {
  font-size: 12px;
  font-weight: 700;
}

.price-value {
  font-size: 16px;
  font-weight: 700;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  letter-spacing: -0.3px;
}

.seller-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2px;
  font-size: 10.5px;
}

.seller-user {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.seller-avatar {
  width: 17px;
  height: 17px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.seller-name {
  color: #64748B;
  font-weight: 400;
  font-size: 10.5px;
}

.time-ago {
  color: #94A3B8;
  font-size: 10px;
  flex-shrink: 0;
  letter-spacing: -0.2px;
}
</style>
