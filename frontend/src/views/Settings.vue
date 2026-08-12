<template>
  <div class="settings-page">
    <div class="page-header">
      <span class="page-title">全局设置</span>
      <div class="header-actions">
        <n-button size="small" secondary @click="load">
          <template #icon><n-icon><RefreshOutlined /></n-icon></template>
          刷新
        </n-button>
      </div>
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
              <div class="param-label-main">{{ displayKey(key) }}</div>
            </div>
            <!-- 模拟器安装路径：路径输入 + 浏览 + 检查环境（仅文件存在性校验） -->
            <template v-if="isInstallPath(section, key)">
              <div class="param-control install-path-control">
                <n-input
                  :value="val"
                  style="width: 320px"
                  :disabled="!!installChecking[key]"
                  @update:value="(v: string) => onInstallPathInput(key, v)"
                  @blur="(e: FocusEvent) => onInstallPathBlur(key, (e.target as HTMLInputElement).value)"
                />
                <n-button
                  size="small"
                  :loading="!!installChecking[key]"
                  @click="browseInstallPath(section, key)"
                  >浏览</n-button
                >
                <n-button
                  size="small"
                  type="primary"
                  secondary
                  :loading="!!installChecking[key]"
                  :disabled="!val.trim()"
                  @click="checkInstallPath(key)"
                  >检查环境</n-button
                >
              </div>
            </template>
            <div v-else class="param-control">
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
          <!-- 安装路径校验提示：仅显示在「助手设置」卡片内 -->
          <div
            v-if="section === '助手设置' && installHint"
            class="install-hint"
            :class="'hint-' + installHintType"
          >
            {{ installHint }}
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
import { settingsApi, utilsApi } from '@/api/client'

const message = useMessage()
const loading = ref(true)

const settings = ref<Record<string, Record<string, string>>>({})
// 安装路径输入缓冲（避免每次按键即保存）
const installPathInput: Record<string, string> = {}
// 检查环境进行中标记（key -> true）
const installChecking = ref<Record<string, boolean>>({})
// 检查环境结果提示
const installHint = ref('')
const installHintType = ref<'default' | 'success' | 'warning' | 'error'>('default')

// 是否为「助手设置」中的模拟器安装路径行（兼容历史遗留的小写 key）
function isInstallPath(section: string, key: string): boolean {
  if (section !== '助手设置') return false
  return key === 'MuMu安装路径' || key === '雷电安装路径' || key === 'mumu安装路径'
}

// 显示统一正确名称（历史遗留的小写 mumu安装路径 也显示为 MuMu安装路径）
const INSTALL_PATH_DISPLAY: Record<string, string> = {
  'MuMu安装路径': 'MuMu安装路径',
  'mumu安装路径': 'MuMu安装路径',
  '雷电安装路径': '雷电安装路径',
}

function displayKey(key: string): string {
  return INSTALL_PATH_DISPLAY[key] ?? key
}

function installPathMode(key: string): 'mumu' | 'ld' {
  return key === 'MuMu安装路径' || key === 'mumu安装路径' ? 'mumu' : 'ld'
}

function installPathTitle(key: string): string {
  return key === 'MuMu安装路径' || key === 'mumu安装路径'
    ? '选择 MuMu 模拟器安装目录'
    : '选择雷电模拟器安装目录'
}

// 安装路径选择引导：校验失败时弹窗告知应选择哪一层目录
function installPathGuide(key: string): string {
  if (key === 'MuMu安装路径' || key === 'mumu安装路径') {
    return (
      'MuMu 安装路径应选择模拟器安装根目录，例如 ...\\MuMuPlayer-12.0 或 ...\\MuMuPlayer，' +
      '请勿再向下选择子目录。' +
      '目录下应存在 MuMuManager.exe（shell 或 nx_main 子目录下）与 ' +
      'external_renderer_ipc.dll（shell\\sdk 子目录下）。'
    )
  }
  return (
    '雷电安装路径应选择模拟器安装根目录，例如 ...\\leidian\\LDPlayer9，' +
    '请勿再向下选择子目录。' +
    '目录下应存在 ldconsole.exe 与 ldopengl64.dll 文件。'
  )
}

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
    // 初始化路径输入缓冲
    Object.keys(settings.value).forEach((section) => {
      const items = settings.value[section]
      if (!items) return
      Object.keys(items).forEach((key) => {
        if (isInstallPath(section, key)) {
          installPathInput[key] = items[key] ?? ''
        }
      })
    })
    installHint.value = ''
    installHintType.value = 'default'
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

// 安装路径输入：仅更新缓冲，不改动已渲染值（失焦/浏览选中时再保存）
function onInstallPathInput(key: string, v: string) {
  installPathInput[key] = v
}

async function onInstallPathBlur(key: string, v: string) {
  const value = (v ?? '').trim()
  installPathInput[key] = value
  // 与当前已保存值一致则无需保存
  const saved = settings.value['助手设置']?.[key] ?? ''
  if (value !== saved) {
    await onSet('助手设置', key, value)
  }
}

// 选择安装目录：浏览后立即保存并触发文件存在性校验
async function browseInstallPath(section: string, key: string) {
  try {
    const res = await utilsApi.browseFolder(installPathTitle(key))
    const path: string | null = res.data?.path || null
    if (!path) return
    installPathInput[key] = path
    await onSet(section, key, path)
    await checkInstallPath(key)
  } catch (e: any) {
    message.error(
      `选择安装目录失败：${e?.response?.data?.detail || e?.message || e}`,
    )
  }
}

// 检查环境：仅校验安装路径下关键文件是否存在（不含实例/分辨率，运行时约束由调度器启动时检测）
async function checkInstallPath(key: string) {
  const path = (installPathInput[key] ?? '').trim()
  if (!path) {
    installHint.value = '请先填写安装路径'
    installHintType.value = 'warning'
    message.warning(installPathGuide(key))
    return
  }
  installChecking.value[key] = true
  installHint.value = ''
  try {
    const res = await utilsApi.validateInstallPath(installPathMode(key), path)
    const d = res.data || {}
    if (d.ok) {
      installHint.value = '路径校验通过'
      installHintType.value = 'success'
    } else {
      const missing = (d.missing || []).join('、')
      installHint.value = `路径下缺少关键文件${missing ? '：' + missing : ''}`
      installHintType.value = 'error'
      // 校验失败时弹窗提示应选择哪一层目录
      message.warning(installPathGuide(key))
    }
  } catch (e: any) {
    installHint.value = `检查失败：${e?.response?.data?.detail || e?.message || e}`
    installHintType.value = 'error'
    message.warning(installPathGuide(key))
  } finally {
    installChecking.value[key] = false
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
  background: #f2f2f2;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-title {
  font-size: 20px;
  font-weight: 800;
  color: #2e2e2e;
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
  background: rgba(195, 195, 195, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px 0;
}
.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #474747;
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
  color: #272727;
}
.param-control {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  min-width: 80px;
}
.install-path-control {
  gap: 8px;
  flex-wrap: wrap;
}
.install-hint {
  font-size: 12px;
  line-height: 1.6;
  margin: -2px 0 2px 0;
}
.hint-success {
  color: #18a058;
}
.hint-warning {
  color: #f0a020;
}
.hint-error {
  color: #d03050;
}
</style>