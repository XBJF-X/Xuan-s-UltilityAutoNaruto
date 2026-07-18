<template>
  <div>
    <n-h1>总览</n-h1>
    <n-grid :cols="3" :x-gap="16">
      <n-grid-item>
        <n-card title="配置" size="small" hoverable>
          <n-space vertical>
            <n-statistic label="配置数量" :value="configCount" />
            <n-button type="primary" @click="loadConfigs">刷新</n-button>
          </n-space>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="调度器" size="small" hoverable>
          <n-space vertical>
            <n-statistic label="状态" :value="schedulerStatus" />
            <n-button
              :type="appStore.schedulerRunning ? 'warning' : 'primary'"
              @click="toggleScheduler"
            >
              {{ appStore.schedulerRunning ? '停止' : '启动' }}
            </n-button>
          </n-space>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="后端" size="small" hoverable>
          <n-space vertical>
            <n-statistic label="版本" :value="appStore.backendVersion || '-'" />
            <n-tag :type="appStore.backendConnected ? 'success' : 'error'">
              {{ appStore.backendConnected ? '已连接' : '未连接' }}
            </n-tag>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { configApi, schedulerApi } from '@/api/client'

const appStore = useAppStore()
const configCount = ref(0)
const schedulerStatus = ref('未知')

async function loadConfigs() {
  try {
    const res = await configApi.list()
    configCount.value = res.data.length
  } catch {
    configCount.value = 0
  }
}

async function loadSchedulerStatus() {
  try {
    const res = await schedulerApi.status()
    appStore.schedulerRunning = res.data.running
    schedulerStatus.value = res.data.running ? '运行中' : '已停止'
  } catch {
    schedulerStatus.value = '未知'
  }
}

async function toggleScheduler() {
  try {
    if (appStore.schedulerRunning) {
      await schedulerApi.stop()
    } else {
      await schedulerApi.start()
    }
    await loadSchedulerStatus()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  appStore.checkBackendHealth()
  loadConfigs()
  loadSchedulerStatus()
})
</script>