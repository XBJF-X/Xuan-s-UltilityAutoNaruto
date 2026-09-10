<template>
  <div class="log-panel" ref="containerRef">
    <div class="log-header">
      <n-text depth="2" style="font-size: 13px">{{ title }}</n-text>
      <n-space>
        <n-switch v-model:value="autoScroll" size="small" />
        <n-text depth="3" style="font-size: 12px">自动滚动</n-text>
        <n-text v-if="autoScrollPaused" style="font-size: 12px; color: #f0a020">选中中已暂停</n-text>
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
        <n-tooltip trigger="hover" :delay="300">
          <template #trigger>
            <n-button text size="tiny" @mousedown.prevent @click="copyLogs">复制</n-button>
          </template>
          选中日志后点「复制」只复制选中内容（也可选中后右键 → 复制），未选中则复制当前显示的全部日志
        </n-tooltip>
        <n-button text size="tiny" @click="clear">清空</n-button>
      </n-space>
    </div>
    <div
      class="log-body"
      ref="bodyRef"
      @mousedown="onBodyMouseDown"
      @contextmenu.prevent="openCtxMenu"
      @scroll="ctxMenu.show = false"
    >
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
    <!-- 右键菜单：选中日志后右键 → 复制选中；未选中时可复制全部/全选/清空 -->
    <n-dropdown
      trigger="manual"
      placement="bottom-start"
      :show="ctxMenu.show"
      :x="ctxMenu.x"
      :y="ctxMenu.y"
      :options="ctxMenuOptions"
      @select="handleCtxSelect"
      @clickoutside="ctxMenu.show = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'
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
const message = useMessage()
const autoScroll = ref(true)
const bodyRef = ref<HTMLElement | null>(null)
const saveScreenshotEnabled = ref(false)
const debugModeEnabled = ref(false)

// ---- 选择/右键复制相关状态 ----
// 拖选期间（以及已存在选区时）暂停"自动滚动"跳底：否则新日志到来会把视图拉到底部、
// 选区被顶走，导致没法在滚动过程中继续选择。
const isSelecting = ref(false)
const hasSelection = ref(false)
const autoScrollPaused = computed(() => isSelecting.value || hasSelection.value)
// 日志右键菜单（WebView2/Electron 默认没有原生右键菜单，这里自绘）
// text 为右键时的选中内容快照：点击菜单项会清掉页面选区，必须先记下来
const ctxMenu = ref({ show: false, x: 0, y: 0, hasSelection: false, text: '' })

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

/** 复制用完整时间戳（含日期，便于粘贴到反馈里定位问题） */
function formatFullTime(ts: number) {
  const d = new Date(ts)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} `
    + `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

/** 单条日志的复制文本（与面板展示一致：时间 [级别] [logger] 内容） */
function formatLogLine(line: LogEntry) {
  const parts = [formatFullTime(line.ts), `[${line.level}]`]
  if (line.logger_name) parts.push(`[${line.logger_name}]`)
  parts.push(line.message)
  return parts.join(' ')
}

/** 读取日志面板内鼠标选中的文本（选区不在面板内时返回空串） */
function selectedTextInBody(): string {
  const sel = window.getSelection?.()
  if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return ''
  const node = sel.getRangeAt(0).commonAncestorContainer
  const root = bodyRef.value
  if (root && node && !root.contains(node)) return ''
  return sel.toString()
}

/** 写剪贴板：优先 Clipboard API，不可用时降级 execCommand（Electron 兜底） */
async function writeClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch {
    // 剪贴板 API 被拒绝/不可用 → 走下方 execCommand 降级方案
  }
  try {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.top = '-1000px'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    return ok
  } catch {
    return false
  }
}

/** 复制任意文本到剪贴板并统一提示 */
async function copyText(text: string, okText: string) {
  const ok = await writeClipboard(text)
  if (ok) message.success(okText)
  else message.error('复制失败，请手动选中日志后按 Ctrl+C')
}

/** 复制当前选中的日志（无选中时提示） */
async function copySelection() {
  const selected = selectedTextInBody()
  if (!selected.trim()) {
    message.warning('请先用鼠标选中要复制的日志')
    return
  }
  await copyText(selected, '已复制选中日志')
}

/** 复制右键菜单打开时记录的选中内容（菜单点击会清掉页面选区，故用快照） */
async function copyCtxSelection() {
  const text = ctxMenu.value.text
  if (!text.trim()) {
    message.warning('请先用鼠标选中要复制的日志')
    return
  }
  await copyText(text, '已复制选中日志')
}

/** 复制当前显示的全部日志 */
async function copyAllLogs() {
  const lines = filteredLogs.value
  if (lines.length === 0) {
    message.warning('暂无可复制的日志')
    return
  }
  await copyText(lines.map(formatLogLine).join('\n'), `已复制 ${lines.length} 条日志`)
}

/**
 * 复制日志（顶部「复制」按钮）：有选中复制选中内容，未选中复制当前全部。
 */
async function copyLogs() {
  if (selectedTextInBody().trim()) await copySelection()
  else await copyAllLogs()
}

/** 全选日志内容（便于一次性复制，不必拖选到面板底部） */
function selectAllLogs() {
  const root = bodyRef.value
  const sel = window.getSelection?.()
  if (!root || !sel) return
  const range = document.createRange()
  range.selectNodeContents(root)
  sel.removeAllRanges()
  sel.addRange(range)
  updateSelectionState()
}

/** 同步"是否存在选区"（用于暂停自动滚动 + 右键菜单项启用判断） */
function updateSelectionState() {
  const has = selectedTextInBody().trim().length > 0
  if (has !== hasSelection.value) hasSelection.value = has
}

/** 右键菜单项：选中日志后右键即可「复制」 */
const ctxMenuOptions = computed(() => {
  const count = filteredLogs.value.length
  return [
    { label: '复制', key: 'copy', disabled: !ctxMenu.value.hasSelection },
    { label: `复制全部日志（${count} 条）`, key: 'copy-all', disabled: count === 0 },
    { label: '全选日志', key: 'select-all', disabled: count === 0 },
    { type: 'divider' as const },
    { label: '清空日志', key: 'clear' },
  ]
})

function openCtxMenu(e: MouseEvent) {
  updateSelectionState()
  const text = selectedTextInBody()
  ctxMenu.value = {
    show: true,
    x: e.clientX,
    y: e.clientY,
    hasSelection: text.trim().length > 0,
    text,
  }
}

function handleCtxSelect(key: string) {
  ctxMenu.value.show = false
  if (key === 'copy') copyCtxSelection()
  else if (key === 'copy-all') copyAllLogs()
  else if (key === 'select-all') selectAllLogs()
  else if (key === 'clear') clear()
}

// ==================== 拖选：上下边缘自动滚动 ====================
// 浏览器只在指针拖出容器后自动滚动；指针停在容器上下边缘内侧时不滚动，这里补上这段
// （指针在容器外则完全交给浏览器原生行为，避免二者叠加导致速度翻倍）。滚动的同时把
// 选区延伸到边缘所在行，保证"一边滚一边选"能选到后面/前面的日志。
const EDGE_SCROLL_ZONE = 26       // 距上/下边缘多少像素内触发滚动
const EDGE_SCROLL_MAX_SPEED = 16  // 每帧最大滚动像素
let edgeScrollRaf = 0
let pointerX = 0
let pointerY = 0
let selAnchor: { node: Node; offset: number } | null = null

type CaretRangeFn = (x: number, y: number) => Range | null
const caretRangeFromPoint: CaretRangeFn | undefined =
  (document as Document & { caretRangeFromPoint?: CaretRangeFn }).caretRangeFromPoint

/** 指针位于容器内上/下边缘区域时返回滚动速度（px/帧），否则 0 */
function edgeScrollSpeed(clientY: number, rect: DOMRect): number {
  if (clientY < rect.top || clientY > rect.bottom) return 0 // 容器外交给浏览器原生
  if (clientY < rect.top + EDGE_SCROLL_ZONE) {
    const ratio = (rect.top + EDGE_SCROLL_ZONE - clientY) / EDGE_SCROLL_ZONE
    return -Math.ceil(Math.min(ratio, 1) * EDGE_SCROLL_MAX_SPEED)
  }
  if (clientY > rect.bottom - EDGE_SCROLL_ZONE) {
    const ratio = (clientY - (rect.bottom - EDGE_SCROLL_ZONE)) / EDGE_SCROLL_ZONE
    return Math.ceil(Math.min(ratio, 1) * EDGE_SCROLL_MAX_SPEED)
  }
  return 0
}

/** 滚动后把选区延伸到指针所在行（指针在容器外时贴到最近的内边缘） */
function extendSelectionToPointer(x: number, y: number, rect: DOMRect) {
  if (!selAnchor || !caretRangeFromPoint) return
  const clampedY = Math.min(Math.max(y, rect.top + 1), rect.bottom - 1)
  const caret = caretRangeFromPoint.call(document, x, clampedY)
  const sel = window.getSelection?.()
  if (!caret || !sel) return
  try {
    const range = document.createRange()
    range.setStart(selAnchor.node, selAnchor.offset)
    range.setEnd(caret.startContainer, caret.startOffset)
    sel.removeAllRanges()
    sel.addRange(range)
  } catch {
    // 反向拖选（锚点在指针之后）时交换首尾；仍失败则只保留滚动效果
    try {
      const range = document.createRange()
      range.setStart(caret.startContainer, caret.startOffset)
      range.setEnd(selAnchor.node, selAnchor.offset)
      sel.removeAllRanges()
      sel.addRange(range)
    } catch {
      // 选区跨节点越界等异常：忽略，滚动效果不受影响
    }
  }
}

function runEdgeScroll() {
  edgeScrollRaf = 0
  if (!isSelecting.value) return
  const root = bodyRef.value
  if (!root) return
  const rect = root.getBoundingClientRect()
  const speed = edgeScrollSpeed(pointerY, rect)
  if (speed === 0) return
  const before = root.scrollTop
  root.scrollTop = before + speed
  if (root.scrollTop !== before) extendSelectionToPointer(pointerX, pointerY, rect)
  if (isSelecting.value) edgeScrollRaf = requestAnimationFrame(runEdgeScroll)
}

function startEdgeScroll() {
  if (!edgeScrollRaf) edgeScrollRaf = requestAnimationFrame(runEdgeScroll)
}

function onBodyMouseDown(e: MouseEvent) {
  ctxMenu.value.show = false
  if (e.button !== 0) return
  isSelecting.value = true
  pointerX = e.clientX
  pointerY = e.clientY
  // 记录拖选锚点，供边缘滚动时延伸选区
  const caret = caretRangeFromPoint ? caretRangeFromPoint.call(document, e.clientX, e.clientY) : null
  selAnchor = caret ? { node: caret.startContainer, offset: caret.startOffset } : null
}

function onDocMouseMove(e: MouseEvent) {
  pointerX = e.clientX
  pointerY = e.clientY
  if (!isSelecting.value) return
  const root = bodyRef.value
  if (!root) return
  if (edgeScrollSpeed(e.clientY, root.getBoundingClientRect()) !== 0) startEdgeScroll()
}

function onDocMouseUp() {
  isSelecting.value = false
  selAnchor = null
  if (edgeScrollRaf) {
    cancelAnimationFrame(edgeScrollRaf)
    edgeScrollRaf = 0
  }
  updateSelectionState()
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
  // 存在选区/正在拖选时不跳底，否则会打断"一边滚动一边选择"
  if (autoScroll.value && !autoScrollPaused.value) {
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
  // 拖选/右键复制：全局监听鼠标与选区变化（拖选可能移出日志面板范围）
  document.addEventListener('mousemove', onDocMouseMove)
  document.addEventListener('mouseup', onDocMouseUp)
  document.addEventListener('selectionchange', updateSelectionState)
})

onBeforeUnmount(() => {
  stopReconnectListener?.()
  document.removeEventListener('mousemove', onDocMouseMove)
  document.removeEventListener('mouseup', onDocMouseUp)
  document.removeEventListener('selectionchange', updateSelectionState)
  if (edgeScrollRaf) {
    cancelAnimationFrame(edgeScrollRaf)
    edgeScrollRaf = 0
  }
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
  /* 允许鼠标选中日志文本（Ctrl+C 复制），方便排查问题时粘贴 */
  user-select: text;
  -webkit-user-select: text;
  cursor: text;
}
.log-body ::selection {
  background: #3a5f8f;
  color: #fff;
}
.log-line {
  padding: 1px 12px;
  white-space: pre-wrap;
  word-break: break-all;
  user-select: text;
  -webkit-user-select: text;
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
