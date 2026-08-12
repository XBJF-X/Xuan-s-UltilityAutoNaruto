<template>
  <n-config-provider :theme="theme" :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <!-- 缓存场景资源图/编辑器：从编辑器返回场景图时不重新拉取数据、不重跑布局 -->
          <router-view v-slot="{ Component, route }">
            <keep-alive :include="['ResourceGraph', 'ResourceSceneEditor']">
              <component :is="Component" :key="route.fullPath" />
            </keep-alive>
          </router-view>
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { zhCN, dateZhCN, darkTheme, NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider } from 'naive-ui'

const isDark = computed(() => false)
const theme = computed(() => isDark.value ? darkTheme : null)

/** 全局字体放大 */
const themeOverrides = {
  common: {
    fontSize: '15px',
    fontSizeMini: '12px',
    fontSizeTiny: '13px',
    fontSizeSmall: '14px',
    fontSizeMedium: '15px',
    fontSizeLarge: '17px',
    fontSizeHuge: '20px',
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* 全局基础字号 */
html {
  font-size: 15px;
}
</style>