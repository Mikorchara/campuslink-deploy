<template>
  <Teleport to="body">
    <dialog ref="dialog" class="app-dialog" @cancel.prevent="$emit('close')" @click="onBackdrop">
      <header><h2>{{ title }}</h2><button type="button" aria-label="关闭对话框" @click="$emit('close')">✕</button></header>
      <slot />
    </dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue';
const props = defineProps<{ open: boolean; title: string }>();
const emit = defineEmits<{ close: [] }>();
const dialog = ref<HTMLDialogElement | null>(null);
watch(() => props.open, async (open) => {
  await nextTick();
  if (open && !dialog.value?.open) dialog.value?.showModal();
  else if (!open) dialog.value?.close();
}, { immediate: true });
function onBackdrop(event: MouseEvent) { if (event.target === dialog.value) emit('close'); }
onUnmounted(() => dialog.value?.close());
</script>

<style scoped>
.app-dialog { margin: auto; width: min(400px, calc(100vw - 32px)); max-height: 80vh; padding: var(--space-lg); border: 1px solid var(--color-border-regular); border-radius: var(--radius-xl); background: var(--color-bg-card); color: var(--color-text-main); line-height: 1.8; }
.app-dialog::backdrop { background: var(--color-dialog-backdrop); }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-base); }
h2 { font-size: var(--font-size-lg); }
header button { min-width: 44px; min-height: 44px; color: var(--color-text-secondary); }
</style>
