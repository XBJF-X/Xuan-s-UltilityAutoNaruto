import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { healthApi, configApi } from '@/api/client'

export const useAppStore = defineStore('app', () => {
  const backendConnected = ref(false)
  const backendVersion = ref('')
  const activeConfigId = ref<string | null>(null)
  const schedulerRunning = ref(false)
  const configs = ref<any[]>([])
  // 切换配置中：右侧面板需等待从后端获取完调度器/任务状态等请求结束后才允许点击，
  // 避免上一个配置的慢响应与当前配置请求产生竞态
  const configSwitching = ref(false)

  const activeConfig = computed(() =>
    configs.value.find(c => c.id === activeConfigId.value) || null
  )

  async function checkBackendHealth() {
    try {
      const res = await healthApi.check()
      backendConnected.value = true
      backendVersion.value = res.data.version
    } catch {
      backendConnected.value = false
    }
  }

  async function loadConfigs() {
    try {
      const res = await configApi.list()
      configs.value = res.data
    } catch {
      configs.value = []
    }
  }

  function setActiveConfig(id: string | null) {
    activeConfigId.value = id
  }

  return {
    backendConnected,
    backendVersion,
    activeConfigId,
    activeConfig,
    configs,
    schedulerRunning,
    configSwitching,
    checkBackendHealth,
    loadConfigs,
    setActiveConfig,
  }
})