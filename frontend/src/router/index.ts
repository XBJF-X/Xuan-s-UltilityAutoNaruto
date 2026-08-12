import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    // 场景资源图（独立页面，顶部栏"场景资源"跳转口以新标签页打开）
    path: '/resource-graph',
    name: 'ResourceGraph',
    component: () => import('@/views/ResourceGraph.vue'),
    meta: { title: '场景资源' },
  },
  {
    // 场景编辑器（从场景图双击节点进入，独立页面）
    path: '/resource-scene/:sceneId',
    name: 'ResourceSceneEditor',
    component: () => import('@/views/ResourceSceneEditor.vue'),
    meta: { title: '场景编辑器' },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '总览' },
      },
      {
        path: 'config/:id?',
        name: 'ConfigDetail',
        component: () => import('@/views/ConfigDetail.vue'),
        meta: { title: '配置详情' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' },
      },
      {
        path: 'resourcemanager',
        name: 'ResourceManager',
        component: () => import('@/views/ResourceManager.vue'),
        meta: { title: '资源管理器' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router