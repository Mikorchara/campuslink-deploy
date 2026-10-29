<template>
  <button type="button" class="forum-post-card" @click="handleClick">
    <!-- 左侧封面图 -->
    <div v-if="post.image_url" class="post-cover-wrapper">
      <img
        :src="post.image_url"
        :alt="post.title"
        class="post-cover"
        loading="lazy"
      />
    </div>

    <!-- 右侧内容区 -->
    <div class="post-content">
      <!-- 顶部标题与 Tag -->
      <div class="header-line">
        <h4 class="post-title truncate-1" :title="post.title">
          {{ post.title }}
        </h4>
        <span
          class="post-tag"
          :class="[`tag-${post.tagType || 'blue'}`]"
        >
          {{ post.tag }}
        </span>
      </div>

      <!-- 摘要内容（两行截断） -->
      <p class="post-summary truncate-2">
        {{ post.summary }}
      </p>

      <!-- 底部作者与互动信息 -->
      <div class="post-footer">
        <div class="author-info">
          <img
            :src="post.author.avatar"
            :alt="post.author.name"
            class="author-avatar"
          />
          <span class="author-name truncate-1">{{ post.author.name }}</span>
        </div>

        <div class="meta-info">
          <!-- 评论图标及数量 -->
          <div class="comment-count">
            <svg class="comment-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor">
              <path d="M2.5 3.5C2.5 2.94772 2.94772 2.5 3.5 2.5H12.5C13.0523 2.5 13.5 2.94772 13.5 3.5V10.5C13.5 11.0523 13.0523 11.5 12.5 11.5H5.5L2.5 14V3.5Z" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ post.comment_count }}</span>
          </div>
          <!-- 发布日期 -->
          <span class="created-date">{{ post.created_date }}</span>
        </div>
      </div>
    </div>
  </button>
</template>

<script setup lang="ts">
import type { ForumPost } from '../../types';

interface Props {
  post: ForumPost;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'click', post: ForumPost): void;
}>();

const handleClick = () => {
  emit('click', props.post);
};
</script>

<style scoped>
.forum-post-card {
  width: 100%;
  text-align: left;
  font: inherit;
  display: flex;
  background-color: var(--color-bg-card);
  border-radius: 14px;
  padding: 11px 12px;
  gap: 12px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(241, 245, 249, 0.85);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
  user-select: none;
  box-sizing: border-box;
}

.forum-post-card:active {
  transform: scale(0.985);
}

.post-cover-wrapper {
  width: 104px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #F8FAFC;
}

.post-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.forum-post-card:hover .post-cover {
  transform: scale(1.04);
}

.post-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.header-line {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 4px;
}

.post-title {
  font-size: 13px;
  font-weight: 700;
  color: #1E293B;
  flex: 1;
  min-width: 0;
  line-height: 1.35;
  letter-spacing: -0.2px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-tag {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 500;
  flex-shrink: 0;
  letter-spacing: 0.2px;
  white-space: nowrap;
  margin-top: 1px;
}

.tag-blue {
  background-color: #E8F4FD;
  color: #2563EB;
}

.tag-green {
  background-color: #EAF9EC;
  color: #16A34A;
}

.tag-orange {
  background-color: #FEF3C7;
  color: #D97706;
}

.post-summary {
  font-size: 11.5px;
  color: #64748B;
  line-height: 1.45;
  margin: 4px 0 6px 0;
}

.post-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 10.5px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.author-avatar {
  width: 17px;
  height: 17px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.author-name {
  color: #64748B;
  font-size: 10.5px;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94A3B8;
  font-size: 10.5px;
}

.comment-count {
  display: flex;
  align-items: center;
  gap: 3px;
}

.comment-icon {
  width: 12px;
  height: 12px;
}

.created-date {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
</style>
