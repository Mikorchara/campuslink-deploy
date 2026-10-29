<template>
  <nav class="bottom-navigation">
    <div class="nav-tabs">
      <button
        v-for="item in navItems"
        :key="item.path"
        type="button"
        class="nav-tab-item"
        :class="{ 'is-active': currentPath === item.path }"
        @click="handleNavigate(item.path)"
      >
        <!-- 首页图标 -->
        <div class="icon-box" v-if="item.id === 'home'">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2.5L2 11h3v9.5a.5.5 0 0 0 .5.5h5v-6h3v6h5a.5.5 0 0 0 .5-.5V11h3L12 2.5z"/>
          </svg>
        </div>

        <!-- 闲置图标 -->
        <div class="icon-box" v-else-if="item.id === 'idle'">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M6 8V6a6 6 0 0 1 12 0v2" stroke-width="2" stroke-linecap="round"/>
            <rect x="3" y="8" width="18" height="13" rx="3" stroke-width="2"/>
          </svg>
        </div>

        <!-- 论坛图标 -->
        <div class="icon-box" v-else-if="item.id === 'forum'">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>

        <!-- 我的图标 -->
        <div class="icon-box" v-else-if="item.id === 'profile'">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="7" r="4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>

        <!-- 文本标签 -->
        <span class="tab-label">{{ item.label }}</span>
      </button>
    </div>

    <!-- 底部安全区域指示条 (iOS Home Indicator) -->
    <div class="home-indicator-bar" v-if="showHomeIndicator">
      <div class="indicator-pill"></div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { NavItem } from '../../types';

interface Props {
  showHomeIndicator?: boolean;
}

withDefaults(defineProps<Props>(), {
  showHomeIndicator: true
});

const route = useRoute();
const router = useRouter();

const navItems: NavItem[] = [
  { id: 'home', label: '首页', path: '/', icon: 'home' },
  { id: 'idle', label: '闲置', path: '/idle', icon: 'bag' },
  { id: 'forum', label: '论坛', path: '/forum', icon: 'chat' },
  { id: 'profile', label: '我的', path: '/profile', icon: 'user' }
];

const currentPath = computed(() => {
  if (route.path.startsWith('/idle')) return '/idle';
  if (route.path.startsWith('/forum')) return '/forum';
  if (route.path.startsWith('/profile')) return '/profile';
  return '/';
});

const handleNavigate = (path: string) => {
  if (route.path !== path) {
    router.push(path);
  }
};
</script>

<style scoped>
.bottom-navigation {
  width: 100%;
  flex-shrink: 0;
  background-color: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(226, 232, 240, 0.85);
  box-shadow: 0 -3px 14px rgba(0, 0, 0, 0.03);
  z-index: 50;
  display: flex;
  flex-direction: column;
  user-select: none;
  box-sizing: border-box;
}

.nav-tabs {
  display: flex;
  height: 52px;
  align-items: center;
  justify-content: space-around;
  padding: 2px 6px 0 6px;
  width: 100%;
  box-sizing: border-box;
}

.nav-tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #8E9BAE;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  padding: 3px 0;
  position: relative;
  height: 100%;
}

.nav-tab-item:active {
  transform: scale(0.92);
}

.icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.tab-icon {
  width: 21px;
  height: 21px;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.tab-label {
  font-size: 11.5px;
  font-weight: 500;
  letter-spacing: 0.2px;
  transition: color 0.2s ease;
}

/* 激活状态 */
.nav-tab-item.is-active {
  color: var(--color-primary);
}

.nav-tab-item.is-active .tab-icon {
  transform: scale(1.08);
}

.nav-tab-item.is-active .tab-label {
  font-weight: 600;
}

/* 底部小黑条 Home Indicator */
.home-indicator-bar {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 6px;
  padding-top: 3px;
}

.indicator-pill {
  width: 134px;
  height: 4px;
  background-color: #B4B9C2;
  border-radius: 2px;
}
</style>
