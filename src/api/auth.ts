import { request } from './request';
import type { UserProfile } from '../types';

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export async function register(payload: RegisterPayload) {
  return await request<UserProfile>('/auth/register', {
    anonymous: true,
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function login(payload: LoginPayload) {
  return await request<{ token: string; user: UserProfile }>('/auth/login', {
    anonymous: true,
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function getCurrentUser() {
  return (await request<UserProfile>('/users/me')).data;
}
