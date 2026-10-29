<template>
  <div class="request-state" :role="error ? 'alert' : 'status'" aria-live="polite">
    <p>{{ loading ? '正在加载…' : error || emptyText }}</p>
    <button v-if="error" type="button" @click="$emit('retry')">重试</button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ loading?: boolean; error?: string; emptyText?: string }>(), {
  emptyText: '暂时没有内容'
});
defineEmits<{ retry: [] }>();
</script>

<style scoped>
.request-state { padding: var(--space-xl); text-align: center; color: var(--color-text-secondary); }
.request-state p { line-height: 1.7; overflow-wrap: anywhere; }
.request-state button { min-height: 44px; margin-top: var(--space-md); padding: var(--space-sm) var(--space-xl); border-radius: var(--radius-pill); color: var(--color-primary-dark); background: var(--color-primary-light); }
</style>
