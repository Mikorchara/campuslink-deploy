<template>
  <section class="account-page">
    <header class="account-heading"><router-link to="/profile">‹ 我的</router-link><h1>我的发布</h1><router-link to="/publish">发布</router-link></header>
    <RequestState v-if="loading || error || !items.length" :loading="loading" :error="error" empty-text="还没有发布商品，发布第一件闲置吧" @retry="load" />
    <p v-if="actionError" role="alert" class="account-error">{{ actionError }}</p>
    <article v-for="item in items" :key="item.id" class="account-card">
      <h2><router-link :to="`/product/${item.id}`">{{ item.title }}</router-link></h2>
      <p>¥{{ item.price }} · {{ statusLabels[item.status] }}</p>
      <div class="account-actions">
        <router-link :to="`/product/${item.id}/edit`">编辑</router-link>
        <button v-for="(label, status) in statusLabels" :key="status" type="button" :disabled="busy || status === item.status" @click="setStatus(item, status)">{{ label }}</button>
        <button type="button" class="danger" :disabled="busy" @click="deleting = item">删除</button>
      </div>
    </article>
    <AppDialog :open="Boolean(deleting)" title="删除商品" @close="deleting = null">
      <p>确定删除「{{ deleting?.title }}」？相关收藏和交易记录也会被移除，此操作无法撤销。</p>
      <p v-if="deleteError" role="alert" class="account-error">{{ deleteError }}</p>
      <div class="account-actions"><button :disabled="busy" @click="remove">{{ busy ? '正在删除…' : '确认删除' }}</button><button :disabled="busy" @click="deleting = null">保留商品</button></div>
    </AppDialog>
  </section>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import RequestState from '../components/common/RequestState.vue';
import AppDialog from '../components/common/AppDialog.vue';
import { getMyProducts, updateProductStatus, deleteProduct, statusLabels } from '../api/product';
import { errorMessage } from '../api/request';
import type { Product, ProductStatus } from '../types';
const items = ref<Product[]>([]);
const loading = ref(false), error = ref(''), actionError = ref(''), deleteError = ref('');
const busy = ref(false);
const deleting = ref<Product | null>(null);
async function load() { loading.value = true; error.value = ''; try { items.value = await getMyProducts(); } catch (e) { error.value = errorMessage(e); } finally { loading.value = false; } }
async function setStatus(item: Product, status: ProductStatus) {
  busy.value = true; actionError.value = '';
  try { const saved = await updateProductStatus(item.id, status); items.value = items.value.map(p => p.id === saved.id ? saved : p); }
  catch (e) { actionError.value = errorMessage(e); } finally { busy.value = false; }
}
async function remove() {
  if (!deleting.value || busy.value) return;
  busy.value = true; deleteError.value = '';
  try { const id = deleting.value.id; await deleteProduct(id); items.value = items.value.filter(p => p.id !== id); deleting.value = null; }
  catch (e) { deleteError.value = errorMessage(e); } finally { busy.value = false; }
}
onMounted(() => void load());
</script>
