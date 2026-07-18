<template>
  <n-layout style="height: 100vh">
    <n-layout-header bordered>
      <div class="header-inner">
        <div class="header-left">
          <n-gradient-text type="info" :size="20" style="font-weight: bold">
            ☯ Xuan - 火影忍者日常助手
          </n-gradient-text>
          <n-tag :type="appStore.backendConnected ? 'success' : 'error'" size="small" style="margin-left: 12px">
            {{ appStore.backendConnected ? '已连接' : '未连接' }}
          </n-tag>
        </div>
        <div class="header-right">
          <n-button text @click="appStore.checkBackendHealth()">
            <template #icon>
              <n-icon><refresh-icon /></n-icon>
            </template>
            刷新
          </n-button>
        </div>
      </div>
    </n-layout-header>

    <n-layout has-sider position="absolute" style="top: 48px; bottom: 0">
      <n-layout-sider bordered width="200" content-style="padding: 8px">
        <n-menu
          :value="activeKey"
          :options="menuOptions"
          @update:value="handleMenuSelect"
        />
      </n-layout-sider>
      <n-layout content-style="padding: 16px; overflow-y: auto">
        <router-view />
      </n-layout>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import { DashboardOutlined, SettingOutlined, ApartmentOutlined, FormatPainterOutlined, TaskOutlined } from '@vicons/material'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const activeKey = computed(() => route.name as string)

const menuOptions = [
  { label: '总览', key: 'Dashboard', icon: () => h(NIcon, null, h(DashboardOutlined)) },
  { label: '配置详情', key: 'ConfigDetail', icon: () => h(NIcon, null, h(FormatPainterOutlined)), disabled: !appStore.activeConfigId },
  { label: '场景管理', key: 'Scenes', icon: () => h(NIcon, null, h(ApartmentOutlined)) },
  { label: '任务优先级', key: 'TaskPriority', icon: () => h(NIcon, null, h(TaskOutlined)) },
  { label: '设置', key: 'Settings', icon: () => h(NIcon, null, h(SettingOutlined)) },
]

function handleMenuSelect(key: string) {
  router.push({ name: key })
}
</script>

<style scoped>
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
}
.header-left {
  display: flex;
  align-items: center;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>