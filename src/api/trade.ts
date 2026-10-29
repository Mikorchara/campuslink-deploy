import { request } from './request';
import type { Product } from '../types';

export type TransactionStatus = 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'CANCELLED' | 'COMPLETED';
export interface Transaction {
  id: number; product_id: number; product_title: string;
  buyer_id: number; buyer_name: string; seller_id: number; seller_name: string;
  status: TransactionStatus; note: string | null; created_at: string;
}
export const transactionLabels: Record<TransactionStatus, string> = {
  PENDING: '等待卖家处理', ACCEPTED: '已接受，待面交', REJECTED: '已拒绝', CANCELLED: '已取消', COMPLETED: '已完成'
};
export async function getFavorites() {
  return (await request<{ id: number; product: Product }[]>('/favorites')).data;
}
export async function getFavoriteState(id: number) {
  return (await request<{ is_favorited: boolean }>(`/products/${id}/favorite`)).data.is_favorited;
}
export async function setFavorite(id: number, favorite: boolean) {
  return (await request<{ is_favorited: boolean }>(`/products/${id}/favorite`, { method: favorite ? 'POST' : 'DELETE' })).data.is_favorited;
}
export async function getTransactions() { return (await request<Transaction[]>('/transactions')).data; }
export async function requestTransaction(id: number, note: string) {
  return (await request<Transaction>(`/products/${id}/transactions`, { method: 'POST', body: JSON.stringify({ note }) })).data;
}
export async function changeTransactionStatus(id: number, status: TransactionStatus) {
  return (await request<Transaction>(`/transactions/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) })).data;
}
