<template>
  <section class="account-page">
    <header class="account-heading"><router-link to="/profile">‹ 我的</router-link><h1>我的收藏</h1><button @click="load">刷新</button></header>
    <RequestState v-if="loading || error || !items.length" :loading="loading" :error="error" empty-text="还没有收藏商品" @retry="load" />
    <p v-if="actionError" role="alert" class="account-error">{{ actionError }}</p>
    <div class="account-grid"><article v-for="item in items" :key="item.id"><ProductCard :product="item" layout-mode="grid" @click="router.push(`/product/${item.id}`)" /><div class="account-actions"><button :disabled="busy" @click="remove(item.id)">取消收藏</button></div></article></div>
  </section>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import RequestState from '../components/common/RequestState.vue';
import ProductCard from '../components/product/ProductCard.vue';
import { getFavorites, setFavorite } from '../api/trade';
import { errorMessage } from '../api/request';
import type { Product } from '../types';
const items = ref<Product[]>([]);
const router = useRouter();
const loading = ref(false), busy = ref(false), error = ref(''), actionError = ref('');
async function load() { loading.value = true; error.value = ''; try { items.value = (await getFavorites()).map(f => f.product); } catch (e) { error.value = errorMessage(e); } finally { loading.value = false; } }
async function remove(id: number) { busy.value = true; actionError.value = ''; try { await setFavorite(id, false); items.value = items.value.filter(p => p.id !== id); } catch (e) { actionError.value = errorMessage(e); } finally { busy.value = false; } }
onMounted(() => void load());
</script>
