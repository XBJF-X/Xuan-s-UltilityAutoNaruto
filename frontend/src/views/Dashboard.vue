<template>
  <div>
    <n-h1>总览</n-h1>
    <n-grid :cols="2" :x-gap="16" :y-gap="16">
      <n-grid-item>
        <n-card title="配置" size="small" hoverable>
          <template #header-extra>
            <n-button size="tiny" @click="appStore.loadConfigs()">刷新</n-button>
          </template>
          <n-list v-if="appStore.configs.length > 0">
            <n-list-item v-for="cfg in appStore.configs" :key="cfg.id" clickable
              @click="handleSelectConfig(cfg.id)">
              <n-thing :title="cfg.username || cfg.id" :description="cfg.id" />
            </n-list-item>
          </n-list>
          <n-empty v-else description="暂无配置" />
          <n-button block style="margin-top: 12px" @click="showCreateDialog = true">
            新建配置
          </n-button>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="后端状态" size="small" hoverable>
          <n-space vertical>
            <n-statistic label="版本" :value="appStore.backendVersion || '-'" />
            <n-tag :type="appStore.backendConnected ? 'success' : 'error'" size="large">
              {{ appStore.backendConnected ? '已连接' : '未连接' }}
            </n-tag>
            <n-button @click="appStore.checkBackendHealth()">检测连接</n-button>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 新建配置对话框 -->
    <n-modal v-model:show="showCreateDialog" title="新建配置" preset="card" style="width: 400px">
      <n-space vertical>
        <n-input v-model:value="newUsername" placeholder="输入用户名" />
        <n-button type="primary" block @click="handleCreateConfig" :loading="creating">
          创建
        </n-button>
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { configApi } from '@/api/client'

const router = useRouter()
const appStore = useAppStore()

const showCreateDialog = ref(false)
const newUsername = ref('')
const creating = ref(false)

async function handleSelectConfig(id: string) {
  appStore.setActiveConfig(id)
  router.push({ name: 'ConfigDetail' })
}

async function handleCreateConfig() {
  if (!newUsername.value) return
  creating.value = true
  try {
    await configApi.create(newUsername.value)
    await appStore.loadConfigs()
    showCreateDialog.value = false
    newUsername.value = ''
  } catch (e) {
    console.error(e)
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  appStore.checkBackendHealth()
  appStore.loadConfigs()
})
</script>