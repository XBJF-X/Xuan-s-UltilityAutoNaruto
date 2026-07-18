import { defineStore } from 'pinia'
import { ref } from 'vue'
import { healthApi } from '@/api/client'

export const useAppStore = defineStore('app', () => {
  const backendConnected = ref(false)
  const backendVersion = ref('')
  const activeConfigId = ref<string | null>(null)
  const schedulerRunning = ref(false)

  async function checkBackendHealth() {
    try {
      const res = await healthApi.check()
      backendConnected.value = true
      backendVersion.value = res.data.version
    } catch {
      backendConnected.value = false
    }
  }

  function setActiveConfig(id: string | null) {
    activeConfigId.value = id
  }

  return {
    backendConnected,
    backendVersion,
    activeConfigId,
    schedulerRunning,
    checkBackendHealth,
    setActiveConfig,
  }
})