import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
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
        path: 'scenes',
        name: 'Scenes',
        component: () => import('@/views/SceneGraph.vue'),
        meta: { title: '场景管理' },
      },
      {
        path: 'scenes/:id',
        name: 'SceneEditor',
        component: () => import('@/views/SceneEditor.vue'),
        meta: { title: '场景编辑器' },
      },
      {
        path: 'tools/task-priority',
        name: 'TaskPriority',
        component: () => import('@/views/TaskPriorityEditor.vue'),
        meta: { title: '任务优先级' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router