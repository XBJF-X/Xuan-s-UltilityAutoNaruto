import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { healthApi, configApi } from '@/api/client'

export const useAppStore = defineStore('app', () => {
  const backendConnected = ref(false)
  const backendVersion = ref('')
  const activeConfigId = ref<string | null>(null)
  const schedulerRunning = ref(false)
  const configs = ref<any[]>([])

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
    checkBackendHealth,
    loadConfigs,
    setActiveConfig,
  }
})