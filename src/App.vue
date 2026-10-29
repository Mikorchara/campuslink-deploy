<template>
  <div class="app-layout" :class="{ 'is-desktop-preview': isDesktop }">
    <!-- 桌面端右上角快速预览控制台 -->
    <aside v-if="isDesktop" class="desktop-preview-toolbar" aria-label="预览设置">
      <div class="preview-mode-switch">
        <span class="preview-indicator">
          📱 iPhone 18 Pro Max (440 × 956)
        </span>
        <button
          type="button"
          class="switch-btn"
          :class="{ active: autoFitMode }"
          @click="autoFitMode = !autoFitMode"
          :title="autoFitMode ? '空间不足时自动等比例缩放' : '强制 100% 原始尺寸'"
        >
          {{ autoFitMode ? '自适应缩放: 开' : '100% 原始尺寸' }}
        </button>
      </div>
    </aside>

    <!-- 桌面等比例缩放 Stage 容器 -->
    <div
      class="app-stage"
      :style="stageStyle"
    >
      <!-- 移动端视口主容器（严格固定 440 × 956 CSS px） -->
      <div
        id="app-mobile-frame"
        class="mobile-container fixed-mobile-frame"
      >
        <!-- 页面内容独立纵向滚动主视口 -->
        <main
          class="app-scroll-viewport"
          :class="{ 'is-subpage': !shouldShowNav }"
          ref="scrollViewportRef"
        >
          <router-view v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>

        <!-- 底部固定导航区域（独立于滚动容器，不随内容移动） -->
        <BottomNavigation v-if="shouldShowNav" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import BottomNavigation from './components/common/BottomNavigation.vue';

const route = useRoute();
const scrollViewportRef = ref<HTMLElement | null>(null);

const isDesktop = ref(false);
const autoFitMode = ref(true);
const previewScale = ref(1);

const BASE_WIDTH = 440;
const BASE_HEIGHT = 956;

const shouldShowNav = computed(() => {
  return route.meta?.showNav !== false;
});

// 计算缩放尺寸和包裹器尺寸，确保在浏览器空间不足时等比例缩小预览区域
const updateLayout = () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  isDesktop.value = width >= 768;

  if (!isDesktop.value) {
    previewScale.value = 1;
    return;
  }

  if (!autoFitMode.value) {
    previewScale.value = 1;
    return;
  }

  // 为桌面四周留出一定的安全边距（顶部留出工具栏间隙）
  const paddingX = 40;
  const paddingTop = 60;
  const paddingBottom = 40;

  const availW = Math.max(200, width - paddingX);
  const availH = Math.max(300, height - paddingTop - paddingBottom);

  const scaleW = availW / BASE_WIDTH;
  const scaleH = availH / BASE_HEIGHT;

  // 最大缩放比为 1（100% 原始尺寸），窗口不足时按长宽等比例缩小
  const calculatedScale = Math.min(1, scaleW, scaleH);
  previewScale.value = Math.max(0.35, calculatedScale);
};

const stageStyle = computed(() => {
  if (!isDesktop.value) {
    return {};
  }
  return {
    width: `${BASE_WIDTH * previewScale.value}px`,
    height: `${BASE_HEIGHT * previewScale.value}px`,
    '--preview-scale': `${previewScale.value}`
  };
});

// 路由切换时，重置页面滚动容器的滚动条至顶部
watch(() => route.path, () => {
  if (scrollViewportRef.value) {
    scrollViewportRef.value.scrollTo({ top: 0, behavior: 'instant' });
  }
});

watch(autoFitMode, () => {
  updateLayout();
});

onMounted(() => {
  updateLayout();
  window.addEventListener('resize', updateLayout);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateLayout);
});
</script>

<style scoped>
.app-layout {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #EEF2F6;
  position: relative;
  overflow: hidden;
}

/* 桌面预览控制条 */
.desktop-preview-toolbar {
  position: fixed;
  top: 14px;
  right: 18px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(10px);
  padding: 4px 6px;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.preview-mode-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-indicator {
  font-size: 11.5px;
  font-weight: 600;
  color: #334155;
  padding: 0 6px 0 8px;
}

.switch-btn {
  padding: 5px 12px;
  border-radius: 14px;
  font-size: 11.5px;
  font-weight: 500;
  color: #64748B;
  background-color: #F1F5F9;
  transition: all 0.2s ease;
}

.switch-btn:hover {
  color: #1E293B;
}

.switch-btn.active {
  background-color: var(--color-primary);
  color: #FFFFFF;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(16, 185, 88, 0.3);
}

/* 缩放舞台包裹器 */
.app-stage {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  flex-shrink: 0;
}

/* 移动端主容器（iPhone 18 Pro Max 基准：440 × 956 CSS px） */
.mobile-container {
  width: 440px;
  height: 956px;
  max-width: 440px;
  max-height: 956px;
  min-height: 956px;
  background-color: var(--color-bg-page);
  position: relative;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

/* 桌面预览时应用等比例缩放与简化手机轮廓（使用外描边不挤占内部 440px 逻辑尺寸） */
.is-desktop-preview .mobile-container.fixed-mobile-frame {
  transform: scale(var(--preview-scale, 1));
  transform-origin: center center;
  border-radius: 38px;
  box-shadow: 0 0 0 4px #1E293B, 0 16px 48px rgba(15, 23, 42, 0.16), 0 2px 8px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

/* 页面内容独立滚动主视口 */
.app-scroll-viewport {
  flex: 1;
  min-height: 0;
  width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  position: relative;
  overscroll-behavior: contain;
}

/* 二级页面将独立滚动委托给内部组件容器 */
.app-scroll-viewport.is-subpage {
  overflow: hidden;
}

/* 页面切换淡入淡出动效 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.16s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
@media (max-width: 767px) {
  .app-layout { align-items: stretch; }
  .app-stage { width: 100%; height: 100%; }
  .mobile-container { width: 100%; height: 100%; min-height: 0; max-height: none; }
}
</style>
