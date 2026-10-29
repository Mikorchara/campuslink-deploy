import { request } from './request';
import type { ForumCategory, ForumComment, ForumPage, ForumPost, ForumPostPayload } from '../types';

export const forumCategories: ForumCategory[] = ['备考', '新生', '宿舍', '学习', '生活'];
export async function getForumPosts(query: { keyword?: string; category?: string; page?: number; page_size?: number } = {}, signal?: AbortSignal) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => { if (value !== undefined && value !== '') params.set(key, String(value)); });
  return (await request<ForumPage<ForumPost>>(`/forum/posts?${params}`, { signal })).data;
}
export async function getMyForumPosts(page = 1, page_size = 20) {
  return (await request<ForumPage<ForumPost>>(`/forum/posts/mine?page=${page}&page_size=${page_size}`)).data;
}
export async function getForumPost(id: string | number) { return (await request<ForumPost>(`/forum/posts/${id}`)).data; }
export async function saveForumPost(payload: ForumPostPayload, id?: string) {
  return (await request<ForumPost>(`/forum/posts${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(payload) })).data;
}
export async function deleteForumPost(id: number) { await request(`/forum/posts/${id}`, { method: 'DELETE' }); }
export async function getForumComments(id: string | number, page = 1) {
  return (await request<ForumPage<ForumComment>>(`/forum/posts/${id}/comments?page=${page}&page_size=20`)).data;
}
export async function addForumComment(id: number, content: string) {
  return (await request<ForumComment>(`/forum/posts/${id}/comments`, { method: 'POST', body: JSON.stringify({ content }) })).data;
}
export async function editForumComment(id: number, content: string) {
  return (await request<ForumComment>(`/forum/comments/${id}`, { method: 'PUT', body: JSON.stringify({ content }) })).data;
}
export async function deleteForumComment(id: number) { await request(`/forum/comments/${id}`, { method: 'DELETE' }); }

export function forumDate(value?: string) {
  if (!value) return '';
  // SQLite's historical timestamps have no zone; all server timestamps are UTC.
  return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`).toLocaleString('zh-CN', { hour12: false });
}
