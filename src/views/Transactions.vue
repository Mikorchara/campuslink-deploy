<template>
  <section class="account-page">
    <header class="account-heading"><router-link to="/profile">‹ 我的</router-link><h1>我的交易</h1><button :disabled="loading" @click="load">刷新</button></header>
    <RequestState v-if="loading || error || !items.length" :loading="loading" :error="error" empty-text="还没有交易请求" @retry="load" />
    <p v-if="actionError" class="account-error" role="alert">{{ actionError }}</p>
    <article v-for="item in items" :key="item.id" class="account-card" :class="{ 'notified-transaction': String(item.id) === route.query.transaction }" :id="`transaction-${item.id}`">
      <p v-if="String(item.id) === route.query.transaction" class="notification-context">本条消息关联的交易</p>
      <h2><router-link :to="`/product/${item.product_id}`">{{ item.product_title }}</router-link></h2>
      <p>{{ item.seller_id === session.user?.id ? '卖给' : '向卖家购买' }}：{{ item.seller_id === session.user?.id ? item.buyer_name : item.seller_name }}</p>
      <p>{{ transactionLabels[item.status] }}</p><p v-if="item.note">留言：{{ item.note }}</p>
      <div class="account-actions">
        <template v-if="item.status === 'PENDING' && item.seller_id === session.user?.id"><button :disabled="busy" @click="change(item, 'ACCEPTED')">接受</button><button :disabled="busy" @click="change(item, 'REJECTED')">拒绝</button></template>
        <button v-if="item.status === 'ACCEPTED' && item.seller_id === session.user?.id" :disabled="busy" @click="completing = item">确认面交完成</button>
        <button v-if="['PENDING', 'ACCEPTED'].includes(item.status)" :disabled="busy" @click="change(item, 'CANCELLED')">取消交易</button>
      </div>
    </article>
    <AppDialog :open="Boolean(completing)" title="确认交易完成" @close="completing = null"><p>请确认「{{ completing?.product_title }}」已当面交付。确认后商品将标记为已售出。</p><div class="account-actions"><button :disabled="busy" @click="complete">已面交，确认完成</button><button @click="completing = null">返回</button></div></AppDialog>
  </section>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import RequestState from '../components/common/RequestState.vue';
import AppDialog from '../components/common/AppDialog.vue';
import { getTransactions, changeTransactionStatus, transactionLabels } from '../api/trade';
import type { Transaction, TransactionStatus } from '../api/trade';
import { errorMessage } from '../api/request';
import { useUserStore } from '../stores/user';
const session = useUserStore();
const route = useRoute();
const items = ref<Transaction[]>([]), completing = ref<Transaction | null>(null);
const loading = ref(false), busy = ref(false), error = ref(''), actionError = ref('');
async function focusTransaction() {
  await nextTick();
  const id = Number(route.query.transaction);
  if (Number.isSafeInteger(id) && id > 0) document.getElementById(`transaction-${id}`)?.scrollIntoView({ block: 'center' });
}
async function load() { loading.value = true; error.value = ''; try { items.value = await getTransactions(); } catch (e) { error.value = errorMessage(e); } finally { loading.value = false; await focusTransaction(); } }
async function change(item: Transaction, status: TransactionStatus) { if (busy.value) return; busy.value = true; actionError.value = ''; try { const saved = await changeTransactionStatus(item.id, status); items.value = items.value.map(t => t.id === saved.id ? saved : t); } catch (e) { actionError.value = errorMessage(e); } finally { busy.value = false; } }
async function complete() { if (completing.value) { await change(completing.value, 'COMPLETED'); completing.value = null; } }
onMounted(() => void load());
watch(() => route.query.transaction, () => void focusTransaction());
</script>
<style scoped>
.notified-transaction { outline: 2px solid var(--color-primary); }
.notification-context { color: var(--color-primary-dark); font-size: var(--font-size-sm); }
</style>
