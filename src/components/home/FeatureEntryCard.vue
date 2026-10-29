<template>
  <div
    class="feature-entry-card"
    :class="[`theme-${theme}`]"
    @click="handleClick"
  >
    <div class="icon-wrapper">
      <img :src="icon" :alt="title" class="entry-icon" />
    </div>
    <div class="info-wrapper">
      <div class="title-row">
        <span class="card-title">{{ title }}</span>
        <svg class="arrow-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor">
          <path d="M6 3.5L10.5 8L6 12.5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="card-subtitle">{{ subtitle }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

interface Props {
  title: string;
  subtitle: string;
  icon: string;
  theme?: 'green' | 'blue';
  route?: string;
}

const props = withDefaults(defineProps<Props>(), {
  theme: 'green',
  route: ''
});

const emit = defineEmits<{
  (e: 'click'): void;
}>();

const router = useRouter();

const handleClick = () => {
  emit('click');
  if (props.route) {
    router.push(props.route);
  }
};
</script>

<style scoped>
.feature-entry-card {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 10px 10px 10px 10px;
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s ease;
  user-select: none;
  min-width: 0;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.feature-entry-card:active {
  transform: scale(0.975);
}

/* 绿色主题（二手闲置） */
.theme-green {
  background: linear-gradient(135deg, #EEFCEB 0%, #E6F8E3 100%);
  border: 1px solid rgba(16, 185, 88, 0.14);
}

.theme-green:hover {
  box-shadow: 0 4px 14px rgba(16, 185, 88, 0.12);
}

/* 蓝色主题（校园论坛） */
.theme-blue {
  background: linear-gradient(135deg, #E8F4FD 0%, #DFF0FD 100%);
  border: 1px solid rgba(59, 130, 246, 0.14);
}

.theme-blue:hover {
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.12);
}

.icon-wrapper {
  width: 44px;
  height: 44px;
  margin-right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.entry-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.05));
}

.info-wrapper {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-bottom: 2px;
}

.card-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #1E293B;
  letter-spacing: -0.2px;
  white-space: nowrap;
}

.arrow-icon {
  width: 13px;
  height: 13px;
  color: #475569;
  flex-shrink: 0;
}

.card-subtitle {
  font-size: 11px;
  color: #64748B;
  white-space: nowrap;
  letter-spacing: -0.2px;
  font-weight: 400;
}
</style>
