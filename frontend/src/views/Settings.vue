<template>
  <div class="settings-page">
    <div class="page-header">
      <span class="page-title">全局设置</span>
      <n-button size="small" secondary @click="load">
        <template #icon><n-icon><RefreshOutlined /></n-icon></template>
        刷新
      </n-button>
    </div>
    <div v-if="loading" class="loading-wrap">
      <n-spin size="large" />
    </div>
    <div v-else class="settings-scroll">
      <n-empty
        v-if="Object.keys(settings).length === 0"
        description="setting.ini 暂无配置项"
      />
      <div v-for="(items, section) in settings" :key="section" class="setting-card">
        <div class="card-title">{{ section }}</div>
        <div class="card-divider"></div>
        <div class="param-grid">
          <div v-for="(val, key) in items" :key="key" class="param-row">
            <div class="param-label">
              <div class="param-label-main">{{ key }}</div>
            </div>
            <div class="param-control">
              <n-switch
                v-if="isBool(val)"
                :value="parseBool(val)"
                @update:value="(v: boolean) => onSet(section, key, String(v))"
              />
              <n-input-number
                v-else-if="isNum(val)"
                :value="parseNum(val)"
                style="width: 140px"
                @update:value="(v: number | null) => onSet(section, key, String(v ?? 0))"
              />
              <n-input
                v-else
                :value="val"
                style="width: 260px"
                @update:value="(v: string) => onSet(section, key, v)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NIcon, useMessage } from 'naive-ui'
import { RefreshOutlined } from '@vicons/material'
import { settingsApi } from '@/api/client'

const message = useMessage()
const loading = ref(true)
const settings = ref<Record<string, Record<string, string>>>({})

function isBool(v: string): boolean {
  const s = v.trim().toLowerCase()
  return s === 'true' || s === 'false'
}

function isNum(v: string): boolean {
  return /^-?\d+(\.\d+)?$/.test(v.trim())
}

function parseBool(v: string): boolean {
  return v.trim().toLowerCase() === 'true'
}

function parseNum(v: string): number {
  const n = Number(v.trim())
  return Number.isFinite(n) ? n : 0
}

async function load() {
  loading.value = true
  try {
    const res = await settingsApi.getAll()
    settings.value = res.data ?? {}
  } catch (e) {
    console.error('加载全局设置失败:', e)
    message.error('加载全局设置失败')
    settings.value = {}
  } finally {
    loading.value = false
  }
}

async function onSet(section: string, key: string, value: string) {
  try {
    await settingsApi.set(section, key, value)
    if (settings.value[section]) {
      settings.value[section][key] = value
    }
  } catch (e) {
    console.error('保存全局设置失败:', e)
    message.error(`保存 ${key} 失败`)
    load()
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.settings-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
  background: #1a1a1a;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.page-title {
  font-size: 20px;
  font-weight: 800;
  color: #e8e8e8;
}
.loading-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.settings-scroll {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 4px;
}
.setting-card {
  background: rgba(30, 30, 30, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px 0;
}
.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #d0d0d0;
  margin: 0 14px 6px;
  letter-spacing: 0.5px;
}
.card-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 0 14px 10px;
}
.param-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 14px 0 24px;
}
.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 40px;
}
.param-label {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
}
.param-label-main {
  font-size: 14px;
  font-weight: 600;
  color: #d0d0d0;
}
.param-control {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  min-width: 80px;
}
</style>