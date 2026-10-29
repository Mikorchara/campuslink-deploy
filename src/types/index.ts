export type ProductStatus = 'AVAILABLE' | 'RESERVED' | 'SOLD' | 'OFFLINE';

export interface SellerInfo {
  id: number;
  name: string;
  avatar: string;
}

export interface Product {
  id: number;
  title: string;
  description?: string | null;
  price: number;
  category: string;
  image_url: string;
  status: ProductStatus;
  location?: string | null;
  seller: SellerInfo;
  time_ago: string;
  created_at?: string;
}

export type ForumTagType = 'blue' | 'green' | 'orange' | 'purple';

export interface ForumPost {
  id: number;
  title: string;
  summary: string;
  content?: string;
  tag: string;
  tagType: ForumTagType;
  image_url: string;
  author: {
    id?: number;
    name: string;
    avatar: string;
  };
  comment_count: number;
  created_date: string;
  likes_count?: number;
  category?: ForumCategory;
  created_at?: string;
  updated_at?: string;
}

export type ForumCategory = '备考' | '新生' | '宿舍' | '学习' | '生活';
export interface ForumPostPayload {
  title: string;
  content: string;
  category: ForumCategory;
  image_url: string;
}
export interface ForumComment {
  id: number;
  post_id: number;
  content: string;
  author: SellerInfo;
  created_at: string;
  updated_at: string;
}
export interface ForumPage<T> { items: T[]; total: number; page: number; page_size: number }

export interface FeatureEntry {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  theme: 'green' | 'blue';
  route: string;
}

export interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: string;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  avatar: string;
  contact: string | null;
  bio: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ProductPayload {
  title: string;
  description?: string;
  price: number;
  category: string;
  image_url: string;
  location: string;
}
