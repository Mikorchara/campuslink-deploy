import { request } from './request';

export interface LikeState { count: number; liked: boolean }
export interface NotificationItem {
  id: number; kind: string; message: string; is_read: boolean; created_at: string; link: string | null;
}
export interface NotificationPage {
  items: NotificationItem[]; total: number; page: number; page_size: number; unread_count: number;
}
export function likePath(kind: 'product' | 'post', id: number) {
  return `${kind === 'product' ? '/products' : '/forum/posts'}/${id}/like`;
}
export async function getLike(kind: 'product' | 'post', id: number) {
  return (await request<LikeState>(likePath(kind, id))).data;
}
export async function setLike(kind: 'product' | 'post', id: number, enabled: boolean) {
  return (await request<LikeState>(likePath(kind, id), { method: enabled ? 'PUT' : 'DELETE' })).data;
}
export async function getUnreadCount() { return (await request<{ count: number }>('/notifications/unread-count')).data.count; }
export async function getNotifications(page = 1, unreadOnly = false) {
  return (await request<NotificationPage>(`/notifications?page=${page}&unread_only=${unreadOnly}`)).data;
}
export async function markNotificationRead(id: number) { await request(`/notifications/${id}/read`, { method: 'PATCH' }); }
export async function markNotificationsRead(upTo: number) {
  await request('/notifications/read-all', { method: 'PATCH', body: JSON.stringify({ up_to_id: upTo }) });
}
