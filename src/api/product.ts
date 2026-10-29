import { request } from './request';
import type { Product, ProductPayload, ProductStatus } from '../types';

export const productCategories = ['教材', '数码', '生活用品', '毕业季物品', '代步出行', '服饰鞋包', '文体乐器', '其他'];
export const statusLabels: Record<ProductStatus, string> = {
  AVAILABLE: '在售', RESERVED: '已预约', SOLD: '已售出', OFFLINE: '已下架'
};

export interface ProductQueryParams {
  keyword?: string;
  category?: string;
  status?: ProductStatus;
  page?: number;
  page_size?: number;
}

export async function getProductList(params: ProductQueryParams = {}, signal?: AbortSignal): Promise<Product[]> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '' && value !== '全部') query.set(key, String(value));
  }
  return (await request<Product[]>(`/products?${query}`, { signal })).data;
}

export async function getProductDetail(id: number): Promise<Product> {
  return (await request<Product>(`/products/${id}`)).data;
}

export async function createProduct(payload: ProductPayload): Promise<Product> {
  return (await request<Product>('/products', { method: 'POST', body: JSON.stringify(payload) })).data;
}

export async function updateProduct(id: number, payload: Partial<ProductPayload>) {
  return (await request<Product>(`/products/${id}`, { method: 'PUT', body: JSON.stringify(payload) })).data;
}

export async function updateProductStatus(id: number, status: ProductStatus) {
  return (await request<Product>(`/products/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) })).data;
}

export async function deleteProduct(id: number) {
  await request(`/products/${id}`, { method: 'DELETE' });
}

export async function getMyProducts() {
  return (await request<Product[]>('/users/me/products')).data;
}

export async function getSellerContact(id: number) {
  return (await request<{ name: string; email: string; contact: string | null }>(`/products/${id}/contact`)).data;
}

export async function uploadImage(file: File): Promise<string> {
  const body = new FormData();
  body.append('file', file);
  return (await request<{ image_url: string }>('/uploads', { method: 'POST', body })).data.image_url;
}
