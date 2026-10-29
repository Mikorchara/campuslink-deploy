<template>
  <div class="search-bar-container">
    <div
      class="search-bar"
      :class="{ 'is-focused': isFocused }"
      @click="handleContainerClick"
    >
      <!-- 左侧搜索放大镜图标 -->
      <div class="search-icon-box">
        <svg class="search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor">
          <circle cx="8.5" cy="8.5" r="5.5" stroke-width="2" stroke-linecap="round" />
          <path d="M13 13L17.5 17.5" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>

      <!-- 输入框 -->
      <input
        ref="inputRef"
        v-model="internalValue"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        :readonly="readonly"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown.enter="handleSearch"
      />

      <!-- 清空按钮 -->
      <button
        v-if="internalValue && !readonly"
        type="button"
        class="clear-btn"
        @click.stop="handleClear"
        aria-label="清空输入"
      >
        <svg viewBox="0 0 16 16" fill="currentColor">
          <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
        </svg>
      </button>

      <!-- 右侧扫一扫图标 -->
      <button
        type="button"
        class="scan-action-btn"
        @click.stop="handleScanClick"
        title="扫一扫"
      >
        <svg class="scan-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <!-- 四角扫描框 -->
          <path d="M4 8V5a1 1 0 0 1 1-1h3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M16 4h3a1 1 0 0 1 1 1v3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M4 16v3a1 1 0 0 0 1 1h3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M16 20h3a1 1 0 0 0 1-1v-3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          <!-- 中间扫描横线 -->
          <line x1="7" y1="12" x2="17" y2="12" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

interface Props {
  modelValue?: string;
  placeholder?: string;
  readonly?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '搜索闲置 / 帖子 / 攻略',
  readonly: false
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'search', keyword: string): void;
  (e: 'click'): void;
  (e: 'scan'): void;
}>();

const internalValue = ref(props.modelValue);
const isFocused = ref(false);
const inputRef = ref<HTMLInputElement | null>(null);

watch(() => props.modelValue, (newVal) => {
  internalValue.value = newVal;
});

watch(internalValue, (newVal) => {
  emit('update:modelValue', newVal);
});

const handleContainerClick = () => {
  emit('click');
  if (!props.readonly && inputRef.value) {
    inputRef.value.focus();
  }
};

const handleFocus = () => {
  isFocused.value = true;
};

const handleBlur = () => {
  isFocused.value = false;
};

const handleClear = () => {
  internalValue.value = '';
  emit('update:modelValue', '');
  if (inputRef.value) {
    inputRef.value.focus();
  }
};

const handleSearch = () => {
  emit('search', internalValue.value);
};

const handleScanClick = () => {
  emit('scan');
};
</script>

<style scoped>
.search-bar-container {
  width: 100%;
  padding: 0 16px;
  position: relative;
  z-index: 5;
}

.search-bar {
  display: flex;
  align-items: center;
  height: 44px;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-pill);
  padding: 0 8px 0 14px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(240, 243, 246, 0.9);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.search-bar.is-focused {
  border-color: rgba(16, 185, 88, 0.4);
  box-shadow: 0 4px 16px rgba(16, 185, 88, 0.12), 0 1px 3px rgba(0, 0, 0, 0.02);
}

.search-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
  margin-right: 8px;
  flex-shrink: 0;
}

.search-icon {
  width: 18px;
  height: 18px;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 13.5px;
  color: var(--color-text-main);
  padding: 0;
  cursor: inherit;
}

.search-input::placeholder {
  color: #8E9BAE;
  font-weight: 400;
  letter-spacing: 0.2px;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: #94A3B8;
  padding: 4px;
  transition: color 0.15s ease;
}

.clear-btn:hover {
  color: var(--color-text-main);
}

.clear-btn svg {
  width: 14px;
  height: 14px;
}

.scan-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: var(--color-primary);
  border-radius: 50%;
  transition: transform 0.15s ease, background-color 0.15s ease;
  flex-shrink: 0;
  margin-left: 2px;
}

.scan-action-btn:active {
  transform: scale(0.92);
  background-color: var(--color-primary-light);
}

.scan-icon {
  width: 20px;
  height: 20px;
}
</style>
