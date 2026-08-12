<template>
  <div class="log-panel" ref="containerRef">
    <div class="log-header">
      <n-text depth="2" style="font-size: 13px">{{ title }}</n-text>
      <n-space>
        <n-switch v-model:value="autoScroll" size="small" />
        <n-text depth="3" style="font-size: 12px">自动滚动</n-text>
        <n-switch
          v-if="configId && configId !== '__global__'"
          :value="debugModeEnabled"
          size="small"
          @update:value="toggleDebugMode"
        />
        <n-text v-if="configId && configId !== '__global__'" depth="3" style="font-size: 12px">调试</n-text>
        <n-switch
          v-if="configId && configId !== '__global__'"
          :value="saveScreenshotEnabled"
          size="small"
          @update:value="toggleSaveScreenshot"
        />
        <n-text v-if="configId && configId !== '__global__'" depth="3" style="font-size: 12px">截图</n-text>
        <n-button text size="tiny" @click="clear">清空</n-button>
      </n-space>
    </div>
    <div class="log-body" ref="bodyRef">
      <div v-for="(line, i) in filteredLogs" :key="i" class="log-line" :class="'level-' + line.level.toLowerCase()">
        <span class="log-ts">{{ formatTime(line.ts) }}</span>
        <span class="log-level">[{{ line.level }}]</span>
        <span class="log-logger" v-if="line.logger_name">[{{ line.logger_name }}]</span>
        <span class="log-msg">{{ line.message }}</span>
      </div>
      <div v-if="filteredLogs.length === 0" class="log-empty">
        <n-text depth="3">暂无日志，启动调度器后将显示实时日志</n-text>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { mergeHistory, useWebSocket, type LogEntry } from '@/api/ws'
import { configApi, utilsApi } from '@/api/client'

const props = withDefaults(defineProps<{
  maxLines?: number
  configId?: string | null  // 指定显示哪个 config_id 的日志，null/undefined 显示全部
  title?: string
}>(), {
  maxLines: 999999,
  configId: undefined,
  title: '实时日志',
})

const { logMap, clearLogsByConfig, onMessage } = useWebSocket()
const autoScroll = ref(true)
const bodyRef = ref<HTMLElement | null>(null)
const saveScreenshotEnabled = ref(false)
const debugModeEnabled = ref(false)

let historyFetching = false
let stopReconnectListener: (() => void) | null = null

/** 拉取历史日志并合并（刷新/重连/切换配置后恢复展示） */
async function fetchHistory() {
  if (historyFetching) return
  historyFetching = true
  try {
    const cid = props.configId ?? ''
    const res = await utilsApi.logHistory(cid === '__global__' ? '' : cid, 1000)
    const data = res.data
    if (data?.ok) {
      mergeHistory(data.config_id || cid, (data.entries || []).map((e: any) => ({
        level: e.level || 'INFO',
        message: e.message || '',
        ts: e.ts ?? Date.now(),
        config_id: e.config_id,
        logger_name: e.logger_name || '',
      })))
    }
  } catch {
    // 历史日志拉取失败静默处理，不影响实时日志
  } finally {
    historyFetching = false
  }
}

/** 日志级别数值（DEBUG=0, INFO=1, WARNING=2, ERROR=3） */
const logLevelRank: Record<string, number> = {
  DEBUG: 0, INFO: 1, WARNING: 2, ERROR: 3,
}

/** 根据调试模式决定最低显示级别：开启=DEBUG(0)，关闭=INFO(1) */
const minLogRank = computed(() => debugModeEnabled.value ? 0 : 1)

/** 从配置中加载两个开关的状态 */
async function loadSettings() {
  if (!props.configId || props.configId === '__global__') {
    saveScreenshotEnabled.value = false
    debugModeEnabled.value = false
    return
  }
  try {
    const res = await configApi.get(props.configId)
    const dics = res.data?.setting_dics
    const sv = dics?.['保存截图']
    saveScreenshotEnabled.value = sv === 1 || sv === true
    const dv = dics?.['调试模式']
    debugModeEnabled.value = dv === 1 || dv === true
  } catch {
    saveScreenshotEnabled.value = false
    debugModeEnabled.value = false
  }
}

/** 切换保存截图开关并保存 */
async function toggleSaveScreenshot(v: boolean) {
  saveScreenshotEnabled.value = v
  if (props.configId && props.configId !== '__global__') {
    try { await configApi.updateSetting(props.configId, '保存截图', v ? 1 : 0) } catch { /* ignore */ }
  }
}

/** 切换调试模式开关并保存 */
async function toggleDebugMode(v: boolean) {
  debugModeEnabled.value = v
  if (props.configId && props.configId !== '__global__') {
    try { await configApi.updateSetting(props.configId, '调试模式', v ? 1 : 0) } catch { /* ignore */ }
  }
}

/** 根据 configId 过滤日志，并过滤掉低于最低显示级别的日志 */
const filteredLogs = computed<LogEntry[]>(() => {
  let entries: LogEntry[]
  if (props.configId === undefined) {
    // 显示所有日志（Dashboard 使用）
    const all: LogEntry[] = []
    for (const arr of Object.values(logMap.value)) {
      all.push(...arr)
    }
    all.sort((a, b) => a.ts - b.ts)
    entries = all
  } else if (props.configId === '__global__') {
    // 显示全局日志：只显示 config_id 为空的日志（程序本身，不含各 config 的）
    const arr = logMap.value[''] || []
    entries = arr
  } else {
    // 显示指定 config 的日志
    entries = logMap.value[props.configId || ''] || []
  }
  const minRank = minLogRank.value
  return entries.filter(e => (logLevelRank[e.level] ?? 1) >= minRank)
})

function formatTime(ts: number) {
  const d = new Date(ts)
  return d.toLocaleTimeString('zh-CN', { hour12: false })
}

function clear() {
  if (props.configId === '__global__') {
    clearLogsByConfig('')
  } else if (props.configId !== undefined) {
    clearLogsByConfig(props.configId ?? undefined)
  } else {
    clearLogsByConfig()
  }
}

watch(() => props.configId, () => {
  loadSettings()
  fetchHistory()
})

watch(filteredLogs, async () => {
  if (autoScroll.value) {
    await nextTick()
    if (bodyRef.value) {
      bodyRef.value.scrollTop = bodyRef.value.scrollHeight
    }
  }
}, { deep: true })

onMounted(() => {
  loadSettings()
  fetchHistory()
  // 后台搁置后 WebSocket 重连成功时，拉取历史日志补齐缺口
  stopReconnectListener = onMessage((msg) => {
    if ((msg as any).type === 'reconnected') {
      fetchHistory()
    }
  })
})

onBeforeUnmount(() => {
  stopReconnectListener?.()
})
</script>

<style scoped>
.log-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a2e;
  border-radius: 6px;
  overflow: hidden;
}
.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: #16213e;
  border-bottom: 1px solid #2a2a4a;
  flex-shrink: 0;
}
.log-body {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
}
.log-line {
  padding: 1px 12px;
  white-space: pre-wrap;
  word-break: break-all;
}
.log-line:hover {
  background: rgba(255, 255, 255, 0.05);
}
.log-ts {
  color: #666;
  margin-right: 8px;
}
.log-level {
  margin-right: 4px;
  font-weight: bold;
}
.level-info .log-level { color: #4fc3f7; }
.level-debug .log-level { color: #81c784; }
.level-warning .log-level { color: #ffb74d; }
.level-error .log-level { color: #e57373; }
.log-logger {
  margin-right: 4px;
  color: #888;
  font-weight: normal;
}
.log-msg {
  color: #ccc;
}
.level-error .log-msg { color: #ef9a9a; }
.level-warning .log-msg { color: #ffe0b2; }
.log-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
