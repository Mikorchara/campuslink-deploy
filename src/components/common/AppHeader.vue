<template>
  <header class="app-header">
    <!-- 顶部校园实景插画背景（右上角自然淡出融合） -->
    <div class="campus-bg-wrapper">
      <img
        :src="campusBg"
        alt="福州大学校园风景"
        class="campus-bg-img"
      />
      <div class="campus-bg-gradient-mask"></div>
    </div>

    <!-- 左侧 Logo 与标语核心内容区 -->
    <div class="brand-content">
      <div class="logo-row">
        <!-- 优先渲染透明切图以百分百还原原稿中“福帮帮”的毛笔动感飞溅笔画 -->
        <img
          v-if="useImageLogo"
          :src="logoSrc"
          alt="福帮帮 Logo"
          class="logo-brand-img"
        />
        <!-- 亦支持纯文本/代码动态替换 -->
        <div v-else class="logo-text-group">
          <div class="brand-title">
            <span class="text-green">{{ title }}</span>
            <span class="brand-sparkle">
              <span class="sparkle-leaf leaf-1"></span>
              <span class="sparkle-leaf leaf-2"></span>
            </span>
          </div>
          <div class="brand-subtitle">{{ subTitle }}</div>
          <div class="brand-slogan">
            <span>{{ slogan }}</span>
            <svg class="slogan-curve" viewBox="0 0 180 18" fill="none">
              <path d="M 5,12 Q 90,2 175,12" stroke="#10B958" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.85" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
interface Props {
  title?: string;
  subTitle?: string;
  slogan?: string;
  campusBg?: string;
  logoSrc?: string;
  useImageLogo?: boolean;
}

withDefaults(defineProps<Props>(), {
  title: '福帮帮',
  subTitle: '福州大学校园互助平台',
  slogan: '在福大，遇见更好的校园生活',
  campusBg: '/assets/images/fzu_campus_bg.png',
  logoSrc: '/assets/images/logo_brand_transparent.png',
  useImageLogo: true
});
</script>

<style scoped>
.app-header {
  position: relative;
  width: 100%;
  padding-top: 18px;
  padding-bottom: 8px;
  overflow: hidden;
  background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 65%, #F7F9FA 100%);
}

/* 校园风景背景 */
.campus-bg-wrapper {
  position: absolute;
  top: 0;
  right: 0;
  width: 72%;
  height: 160px;
  pointer-events: none;
  z-index: 1;
}

.campus-bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top right;
  opacity: 0.98;
}

/* 自然过渡渐变遮罩 */
.campus-bg-gradient-mask {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(to right, #F0FDF4 0%, rgba(240, 253, 244, 0.6) 20%, transparent 60%),
    linear-gradient(to bottom, transparent 40%, rgba(255, 255, 255, 0.9) 82%, #F7F9FA 100%);
}

/* 品牌内容 */
.brand-content {
  position: relative;
  z-index: 3;
  padding: 4px 18px 2px 18px;
}

.logo-row {
  display: flex;
  flex-direction: column;
}

.logo-brand-img {
  width: 146px;
  height: auto;
  object-fit: contain;
  margin-top: 2px;
  display: block;
}

.logo-text-group {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.brand-title {
  display: inline-flex;
  align-items: center;
  font-size: 26px;
  font-weight: 800;
  color: var(--color-primary);
  letter-spacing: 0.5px;
  position: relative;
}

.brand-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
  letter-spacing: 0.2px;
}

.brand-slogan {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-main);
  font-weight: 500;
  display: flex;
  flex-direction: column;
  position: relative;
  width: fit-content;
}

.slogan-curve {
  width: 100%;
  height: 10px;
  margin-top: -2px;
}
</style>
