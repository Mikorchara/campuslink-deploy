import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { pinia, useUserStore } from '../stores/user';

const routes: RouteRecordRaw[] = [
  {
    path: '/my-discussions',
    component: () => import('../views/ForumList.vue'),
    props: { participated: true },
    meta: { title: '我参与的讨论 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/notifications',
    component: () => import('../views/Notifications.vue'),
    meta: { title: '消息中心 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '福帮帮 - 首页', showNav: true }
  },
  {
    path: '/idle',
    name: 'IdleMarket',
    component: () => import('../views/IdleMarket.vue'),
    meta: { title: '二手闲置 - 福帮帮', showNav: true }
  },
  {
    path: '/forum',
    name: 'ForumList',
    component: () => import('../views/ForumList.vue'),
    meta: { title: '校园论坛 - 福帮帮', showNav: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '个人中心 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/ProductDetail.vue'),
    meta: { title: '商品详情 - 福帮帮', showNav: false }
  },
  {
    path: '/forum/new',
    component: () => import('../views/PostEditor.vue'),
    meta: { title: '写帖子 - 福帮帮', showNav: false, requiresAuth: true }
  },
  {
    path: '/forum/:id/edit',
    component: () => import('../views/PostEditor.vue'),
    meta: { title: '编辑帖子 - 福帮帮', showNav: false, requiresAuth: true }
  },
  {
    path: '/my-posts',
    component: () => import('../views/ForumList.vue'),
    props: { mine: true },
    meta: { title: '我的帖子 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/forum/:id',
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue'),
    meta: { title: '帖子详情 - 福帮帮', showNav: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '福帮帮 · 登录', showNav: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '福帮帮 · 注册', showNav: false }
  },
  {
    path: '/publish',
    name: 'Publish',
    component: () => import('../views/Publish.vue'),
    meta: { title: '福帮帮 · 发布闲置', showNav: false, requiresAuth: true }
  },
  {
    path: '/product/:id/edit',
    name: 'EditProduct',
    component: () => import('../views/Publish.vue'),
    meta: { title: '编辑闲置 - 福帮帮', showNav: false, requiresAuth: true }
  },
  {
    path: '/my-products',
    component: () => import('../views/MyProducts.vue'),
    meta: { title: '我的发布 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/favorites',
    component: () => import('../views/Favorites.vue'),
    meta: { title: '我的收藏 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/transactions',
    component: () => import('../views/Transactions.vue'),
    meta: { title: '我的交易 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/settings',
    component: () => import('../views/AccountSettings.vue'),
    meta: { title: '个人资料 - 福帮帮', showNav: true, requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

router.beforeEach(async (to) => {
  const session = useUserStore(pinia);
  await session.restore();
  if (to.meta.requiresAuth && !session.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath, reason: session.restoreError || undefined } };
  }
});

router.afterEach((to) => {
  if (to.meta.title) {
    document.title = to.meta.title as string;
  }
});

export default router;
