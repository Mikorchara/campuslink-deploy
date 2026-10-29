<template>
  <section class="forum-section">
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

    <!-- 垂直帖子列表 -->
    <div class="posts-list">
      <ForumPostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @click="handlePostClick"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import ForumPostCard from '../forum/ForumPostCard.vue';
import type { ForumPost } from '../../types';

interface Props {
  title?: string;
  posts: ForumPost[];
  moreRoute?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: '校园论坛',
  moreRoute: '/forum'
});

const emit = defineEmits<{
  (e: 'post-click', post: ForumPost): void;
  (e: 'more-click'): void;
}>();

const router = useRouter();

const handleMoreClick = () => {
  emit('more-click');
  if (props.moreRoute) {
    router.push(props.moreRoute);
  }
};

const handlePostClick = (post: ForumPost) => {
  emit('post-click', post);
};
</script>

<style scoped>
.forum-section {
  width: 100%;
  margin-top: 18px;
  padding-bottom: 20px;
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

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 16px;
}
</style>
