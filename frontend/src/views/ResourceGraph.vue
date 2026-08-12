<template>
  <div class="rg-page">
    <!-- 顶部工具栏 -->
    <div class="rg-toolbar">
      <span class="rg-title">场景资源图</span>
      <div class="rg-actions">
        <n-button size="small" type="primary" @click="openCreateDialog">
          <template #icon><n-icon><AddOutlined /></n-icon></template>
          新建场景节点
        </n-button>
        <n-button size="small" @click="loadData">
          <template #icon><n-icon><RefreshOutlined /></n-icon></template>
          刷新场景
        </n-button>
      </div>
    </div>

    <!-- 画布 -->
    <div ref="canvasWrap" class="rg-canvas-wrap">
      <canvas ref="canvasEl" class="rg-canvas" @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @wheel.prevent="onWheel" @dblclick="onCanvasDblClick" @contextmenu.prevent="onContextMenu" />
    </div>

    <!-- 画布右上角提示 -->
    <div class="rg-hint">
      单击节点高亮关联 · 双击进入编辑器 · 右键节点菜单 · 拖拽节点移动 · 滚轮缩放
    </div>

    <!-- 节点右键菜单 -->
    <n-dropdown
      :show="ctxMenu.show"
      :x="ctxMenu.x"
      :y="ctxMenu.y"
      :options="ctxMenuOptions"
      @select="onCtxMenuSelect"
      @clickoutside="ctxMenu.show = false"
    />

    <!-- 新建场景对话框 -->
    <n-modal v-model:show="showCreate" preset="card" title="新建场景" style="width: 420px">
      <n-space vertical>
        <n-input v-model:value="newSceneName" placeholder="输入场景名称" @keyup.enter="handleCreate" />
        <n-button type="primary" block :loading="creating" @click="handleCreate">创建</n-button>
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'ResourceGraph' })
import { ref, computed, onMounted, onBeforeUnmount, nextTick, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { AddOutlined, RefreshOutlined } from '@vicons/material'
import { resourceApi } from '@/api/resource'
import type { ResourceScene, ResourceEdge } from '@/api/resource'
import {
  forceSimulation,
  forceManyBody,
  forceLink,
  forceCenter,
  forceCollide
} from 'd3-force'

const router = useRouter()
const message = useMessage()

const canvasWrap = ref<HTMLElement>()
const canvasEl = ref<HTMLCanvasElement>()

interface GNode {
  id: string
  name: string
  x: number
  y: number
  vx: number
  vy: number
  width: number
  height: number
  hasSymbol: boolean
  hasBaseImage: boolean
  edges: GEdge[]
}

interface GEdge {
  source: string
  target: string
  implemented: boolean
}

const nodes = reactive<Record<string, GNode>>({})
const edgeList = ref<GEdge[]>([])
const scenes = ref<ResourceScene[]>([])

// 视图变换
const view = reactive({ scale: 1, tx: 0, ty: 0 })
// 拖拽状态
const dragState = reactive<{ nodeId: string | null; ox: number; oy: number }>({ nodeId: null, ox: 0, oy: 0 })
const panState = reactive<{ active: boolean; lx: number; ly: number }>({ active: false, lx: 0, ly: 0 })

const showCreate = ref(false)
const newSceneName = ref('')
const creating = ref(false)

// 选中的节点（单击高亮关联边与节点）
const selectedNodeId = ref<string | null>(null)
// 右键菜单状态
const ctxMenu = reactive({
  show: false,
  x: 0,
  y: 0,
  nodeId: null as string | null,
})
// 右键菜单"连接到场景"的展开项缓存
const ctxConnectTargets = ref<{ label: string; key: string }[]>([])
// 右键菜单"断开连接"的展开项缓存
const ctxDisconnectTargets = ref<{ label: string; key: string }[]>([])

const nodeColors = {
  normal: '#4682B4',
  highlight: '#39C5BB',
  selectedFill: '#f0a020', // 选中节点关联节点填充（橙色）
  selectedText: '#2080f0', // 选中节点关联节点字样（蓝色）
  noBaseImageText: '#f5c518',
}
const edgeColors = {
  implemented: '#696969',
  selected: '#f5c518', // 选中节点关联边（黄色）
}

// 右键菜单选项（动态构建）
const ctxMenuOptions = computed(() => {
  if (!ctxMenu.nodeId) return []
  const node = nodes[ctxMenu.nodeId]
  if (!node) return []
  const connected = new Set<string>()
  for (const e of node.edges) {
    connected.add(e.source === node.id ? e.target : e.source)
  }
  // 未连接场景列表
  ctxConnectTargets.value = Object.values(nodes)
    .filter(n => n.id !== node.id && !connected.has(n.id))
    .map(n => ({ label: n.name, key: `connect:${n.id}` }))
  // 已连接场景列表
  ctxDisconnectTargets.value = [...connected]
    .map(id => nodes[id])
    .filter(Boolean)
    .map(n => ({ label: n.name, key: `disconnect:${n.id}` }))

  const options: any[] = [
    { label: `复制场景名称「${node.name}」`, key: 'copy-name' },
  ]
  if (ctxConnectTargets.value.length > 0) {
    options.push({
      label: '连接到场景',
      key: 'connect',
      children: ctxConnectTargets.value,
    })
  } else {
    options.push({ label: '连接到场景（无未连接场景）', key: 'connect', disabled: true })
  }
  if (ctxDisconnectTargets.value.length > 0) {
    options.push({
      label: '断开连接',
      key: 'disconnect',
      children: ctxDisconnectTargets.value,
    })
  } else {
    options.push({ label: '断开连接（无已连接场景）', key: 'disconnect', disabled: true })
  }
  options.push({ type: 'divider', key: 'divider' })
  options.push({
    label: '删除场景',
    key: 'delete-scene',
    props: { style: { color: '#d03050' } },
  })
  return options
})

// ---------- 工具函数 ----------
function log(...args: any[]) {
  console.log('[ResourceGraph]', ...args)
}
function warn(...args: any[]) {
  console.warn('[ResourceGraph]', ...args)
}
function error(...args: any[]) {
  console.error('[ResourceGraph]', ...args)
}

// ---------- 数据加载 ----------
async function loadData() {
  log('加载场景数据...')
  // 清空旧数据
  for (const key of Object.keys(nodes)) delete nodes[key]
  edgeList.value = []
  selectedNodeId.value = null
  ctxMenu.show = false

  await nextTick()
  await new Promise(resolve => requestAnimationFrame(resolve))

  try {
    const [fullRes, edgeRes] = await Promise.all([
      resourceApi.getFull(),
      resourceApi.listEdges(),
    ])

    const sceneList = fullRes.data?.scenes
    if (!Array.isArray(sceneList)) {
      throw new Error(`scenes 数据格式异常: ${typeof sceneList}`)
    }
    log(`场景数量: ${sceneList.length}`)

    scenes.value = sceneList
    const edges: ResourceEdge[] = edgeRes.data?.edges ?? []
    log(`边数量: ${edges.length}`)

    // 重建节点（宽度根据字符数动态计算）
    for (const s of scenes.value) {
      const name = s.name || s.id.slice(0, 8)
      const charCount = name.length
      const estimatedWidth = charCount * 14 + 12
      const width = Math.max(60, Math.min(240, estimatedWidth))
      nodes[s.id] = {
        id: s.id,
        name,
        x: 0, y: 0, vx: 0, vy: 0,
        width,
        height: 22,
        hasSymbol: (s.elements || []).some(e => e.symbol),
        hasBaseImage: false,
        edges: [],
      }
    }

    // 重建边
    edgeList.value = edges.map(e => ({
      source: e.source_scene_id,
      target: e.target_scene_id,
      implemented: true,
    }))
    for (const n of Object.values(nodes)) n.edges = []
    for (const e of edgeList.value) {
      const sn = nodes[e.source]
      const tn = nodes[e.target]
      if (sn && tn) {
        sn.edges.push(e)
        tn.edges.push(e)
      }
    }

    // 力导向布局（动画可见）
    await runForceLayout()

    // 异步探测底图
    detectBaseImagesAsync()
  } catch (e: any) {
    error('加载场景数据失败:', e)
    message.error(`加载场景数据失败: ${e?.message || '未知错误'}`)
    for (const key of Object.keys(nodes)) delete nodes[key]
    edgeList.value = []
    render()
  }
}

async function detectBaseImagesAsync() {
  log('开始探测底图...')
  const CONCURRENCY = 12
  for (let i = 0; i < scenes.value.length; i += CONCURRENCY) {
    const slice = scenes.value.slice(i, i + CONCURRENCY)
    await Promise.all(slice.map(async s => {
      try {
        await resourceApi.getSceneBaseImage(s.id)
        nodes[s.id].hasBaseImage = true
      } catch {
        nodes[s.id].hasBaseImage = false
      }
    }))
  }
  log('底图探测完成')
  render()
}

// ---------- 力导向布局（d3-force） ----------
function mulberry32(seed: number) {
  return function () {
    let t = (seed += 0x6d2b79f5)
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function runForceLayout(): Promise<void> {
  return new Promise((resolve) => {
    const all = Object.values(nodes)
    if (all.length === 0) {
      resolve()
      return
    }

    const count = all.length
    const rand = mulberry32(42)

    // 初始环形分布
    const radius = Math.max(250, Math.min(900, count * 80))
    all.forEach((n, i) => {
      const angle = (i * 2 * Math.PI) / count
      n.x = radius * Math.cos(angle) + (rand() - 0.5) * 20
      n.y = radius * Math.sin(angle) + (rand() - 0.5) * 20
    })

    const links = edgeList.value
      .filter(e => nodes[e.source] && nodes[e.target])
      .map(e => ({
        source: nodes[e.source],
        target: nodes[e.target]
      }))

      // 在 simulation 配置中加入 alphaMin 并设置目标步数
      const desiredTicks = 70;                     // 想要的总步数
      const alphaMin = 0.02;
      const decay = 1 - Math.pow(alphaMin, 1 / desiredTicks);
      // 然后设置

    const simulation = forceSimulation(all)
      .force('charge', forceManyBody().strength(-800))
      .force('link', forceLink(links).distance(280).strength(0.4))
      .force('center', forceCenter(0, 0))
      .force('collision', forceCollide()
        .radius((d: any) => Math.max(d.width, d.height) / 2 + 12)
      )

      .alphaDecay(decay)
      .alphaMin(alphaMin)
      .alpha(1)
      .on('tick', () => {
        for (const n of all) {
          if (!isFinite(n.x) || !isFinite(n.y)) {
            n.x = (rand() - 0.5) * 50
            n.y = (rand() - 0.5) * 50
          }
        }
        fitView()   // 每帧自适应，保证全局可见
      })
      .on('end', () => {
        fitView()
        resolve()
      })
  })
}

// ---------- 视图适配 ----------
function fitView() {
  const wrap = canvasWrap.value
  if (!wrap) return
  const cw = wrap.clientWidth
  const ch = wrap.clientHeight
  if (cw === 0 || ch === 0) return

  const all = Object.values(nodes)
  if (all.length === 0) return

  for (const n of all) {
    if (!isFinite(n.x) || !isFinite(n.y)) return
  }

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  for (const n of all) {
    minX = Math.min(minX, n.x - n.width / 2)
    minY = Math.min(minY, n.y - n.height / 2)
    maxX = Math.max(maxX, n.x + n.width / 2)
    maxY = Math.max(maxY, n.y + n.height / 2)
  }

  const w = Math.max(maxX - minX + 100, 1)
  const h = Math.max(maxY - minY + 100, 1)
  const newScale = Math.min(cw / w, ch / h, 1.2)

  if (!isFinite(newScale) || newScale <= 0) {
    view.scale = 1
  } else {
    view.scale = newScale
  }

  view.tx = (cw - (maxX + minX) * view.scale) / 2
  view.ty = (ch - (maxY + minY) * view.scale) / 2
  render()
}

// ---------- 渲染 ----------
function render() {
  const canvas = canvasEl.value
  if (!canvas) return
  const wrap = canvasWrap.value!
  const cw = wrap.clientWidth
  const ch = wrap.clientHeight
  if (cw === 0 || ch === 0) return

  if (!isFinite(view.scale) || view.scale <= 0 || view.scale > 10) {
    view.scale = 1
    fitView()
    return
  }

  const dpr = window.devicePixelRatio || 1
  canvas.width = cw * dpr
  canvas.height = ch * dpr
  const ctx = canvas.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  ctx.fillStyle = '#f7f9fc'
  ctx.fillRect(0, 0, cw, ch)

  ctx.save()
  ctx.translate(view.tx, view.ty)
  ctx.scale(view.scale, view.scale)

  // 边
  for (const e of edgeList.value) {
    const sn = nodes[e.source]
    const tn = nodes[e.target]
    if (!sn || !tn) continue
    drawEdge(ctx, sn, tn)
  }

  // 节点
  for (const n of Object.values(nodes)) {
    drawNode(ctx, n)
  }

  ctx.restore()
}

function drawNode(ctx: CanvasRenderingContext2D, n: GNode) {
  const x = n.x - n.width / 2
  const y = n.y - n.height / 2
  const r = 2
  // 高亮判定：选中节点本身或与选中节点直接相连的节点
  const isSelected = selectedNodeId.value === n.id
  const isLinked = selectedNodeId.value !== null &&
    n.edges.some(e => e.source === selectedNodeId.value || e.target === selectedNodeId.value)
  const isHighlighted = isSelected || isLinked

  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + n.width, y, x + n.width, y + n.height, r)
  ctx.arcTo(x + n.width, y + n.height, x, y + n.height, r)
  ctx.arcTo(x, y + n.height, x, y, r)
  ctx.arcTo(x, y, x + n.width, y, r)
  ctx.closePath()
  // 填充：选中节点或关联节点用橙色，拖动中的用高亮青色，否则默认蓝
  if (isHighlighted) {
    ctx.fillStyle = nodeColors.selectedFill // 橙色
  } else {
    ctx.fillStyle = dragState.nodeId === n.id ? nodeColors.highlight : nodeColors.normal
  }
  ctx.fill()
  // 描边：选中的节点加粗描边
  ctx.strokeStyle = isSelected ? '#d03050' : '#222'
  ctx.lineWidth = isSelected ? 2.5 : 1.2
  ctx.stroke()

  // 字样：高亮关联节点用蓝色，否则按底图有无区分
  ctx.fillStyle = isHighlighted ? nodeColors.selectedText : (!n.hasBaseImage ? nodeColors.noBaseImageText : '#fff')
  ctx.font = '14px SimHei, sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(n.name, n.x, n.y)
}

function drawEdge(ctx: CanvasRenderingContext2D, sn: GNode, tn: GNode) {
  const p1 = intersectRect(sn, sn.x, sn.y, tn.x, tn.y)
  const p2 = intersectRect(tn, tn.x, tn.y, sn.x, sn.y)
  if (!p1 || !p2) return

  // 选中节点关联的边高亮为黄色
  const isLinked = selectedNodeId.value !== null && (
    sn.id === selectedNodeId.value || tn.id === selectedNodeId.value
  )
  const color = isLinked ? edgeColors.selected : edgeColors.implemented

  ctx.strokeStyle = color
  ctx.lineWidth = isLinked ? 3 : 2
  ctx.beginPath()
  ctx.moveTo(p1.x, p1.y)
  ctx.lineTo(p2.x, p2.y)
  ctx.stroke()

  // 箭头
  const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x)
  const size = 8
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.moveTo(p2.x, p2.y)
  ctx.lineTo(p2.x - size * Math.cos(angle - Math.PI / 8), p2.y - size * Math.sin(angle - Math.PI / 8))
  ctx.lineTo(p2.x - size * Math.cos(angle + Math.PI / 8), p2.y - size * Math.sin(angle + Math.PI / 8))
  ctx.closePath()
  ctx.fill()
}

function intersectRect(n: GNode, cx1: number, cy1: number, cx2: number, cy2: number) {
  const halfW = n.width / 2
  const halfH = n.height / 2
  const dx = cx2 - cx1
  const dy = cy2 - cy1
  if (dx === 0 && dy === 0) return { x: cx1, y: cy1 }

  let t = Infinity
  if (dx !== 0) {
    const tx = dx > 0 ? (n.x + halfW - cx1) / dx : (n.x - halfW - cx1) / dx
    if (tx >= 0) t = Math.min(t, tx)
  }
  if (dy !== 0) {
    const ty = dy > 0 ? (n.y + halfH - cy1) / dy : (n.y - halfH - cy1) / dy
    if (ty >= 0) t = Math.min(t, ty)
  }
  if (!isFinite(t)) return null
  return { x: cx1 + dx * t, y: cy1 + dy * t }
}

// ---------- 交互 ----------
function screenToWorld(sx: number, sy: number) {
  return { x: (sx - view.tx) / view.scale, y: (sy - view.ty) / view.scale }
}

function hitTest(sx: number, sy: number): string | null {
  const p = screenToWorld(sx, sy)
  for (const n of Object.values(nodes)) {
    if (Math.abs(p.x - n.x) <= n.width / 2 && Math.abs(p.y - n.y) <= n.height / 2) {
      return n.id
    }
  }
  return null
}

function onMouseDown(e: MouseEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  const sx = e.clientX - rect.left
  const sy = e.clientY - rect.top
  const id = hitTest(sx, sy)
  if (id) {
    // 单击节点：选中并高亮关联边与节点
    selectedNodeId.value = id
    dragState.nodeId = id
    const p = screenToWorld(sx, sy)
    dragState.ox = p.x - nodes[id].x
    dragState.oy = p.y - nodes[id].y
    render()
  } else {
    selectedNodeId.value = null
    panState.active = true
    panState.lx = e.clientX
    panState.ly = e.clientY
  }
}

/** 节点右键菜单 */
function onContextMenu(e: MouseEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  const sx = e.clientX - rect.left
  const sy = e.clientY - rect.top
  const id = hitTest(sx, sy)
  if (!id) return
  selectedNodeId.value = id
  ctxMenu.nodeId = id
  ctxMenu.x = e.clientX
  ctxMenu.y = e.clientY
  ctxMenu.show = true
  render()
}

/** 右键菜单项选择 */
async function onCtxMenuSelect(key: string) {
  const nodeId = ctxMenu.nodeId
  ctxMenu.show = false
  if (!nodeId || !nodes[nodeId]) return
  const node = nodes[nodeId]

  if (key === 'copy-name') {
    try {
      await navigator.clipboard.writeText(node.name)
      message.success(`已复制场景名称「${node.name}」`)
    } catch {
      message.error('复制失败（浏览器不允许剪贴板访问）')
    }
    return
  }

  if (key === 'connect' || key === 'disconnect') {
    return // 仅展开子菜单
  }

  if (key.startsWith('connect:')) {
    const targetId = key.slice('connect:'.length)
    try {
      await resourceApi.createEdge(nodeId, targetId)
      message.success('已创建连接')
      await loadData()
    } catch (err: any) {
      message.error(err?.response?.data?.detail || '连接失败')
    }
    return
  }

  if (key.startsWith('disconnect:')) {
    const targetId = key.slice('disconnect:'.length)
    try {
      await resourceApi.deleteEdge(nodeId, targetId)
      message.success('已断开连接')
      await loadData()
    } catch (err: any) {
      message.error(err?.response?.data?.detail || '断开失败')
    }
    return
  }

  if (key === 'delete-scene') {
    await handleDeleteScene(node)
  }
}

/** 删除场景（带确认） */
async function handleDeleteScene(node: GNode) {
  const name = node.name
  const confirmed = window.confirm(`确定删除场景「${name}」及其所有元素、连接边吗？\n此操作不可恢复！`)
  if (!confirmed) return
  try {
    await resourceApi.deleteScene(node.id)
    message.success(`场景「${name}」已删除`)
    selectedNodeId.value = null
    // 存在相连边时刷新场景（边需要从后端重算）；否则仅从本地移除节点
    if (node.edges.length > 0) {
      await loadData()
    } else {
      delete nodes[node.id]
      scenes.value = scenes.value.filter(s => s.id !== node.id)
      edgeList.value = edgeList.value.filter(e => e.source !== node.id && e.target !== node.id)
      render()
    }
  } catch (err: any) {
    message.error(err?.response?.data?.detail || '删除场景失败')
  }
}

function onMouseMove(e: MouseEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  if (dragState.nodeId) {
    const p = screenToWorld(e.clientX - rect.left, e.clientY - rect.top)
    const n = nodes[dragState.nodeId]
    n.x = p.x - dragState.ox
    n.y = p.y - dragState.oy
    render()
  } else if (panState.active) {
    view.tx += e.clientX - panState.lx
    view.ty += e.clientY - panState.ly
    panState.lx = e.clientX
    panState.ly = e.clientY
    render()
  }
}

function onMouseUp() {
  dragState.nodeId = null
  panState.active = false
}

function onWheel(e: WheelEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  const sx = e.clientX - rect.left
  const sy = e.clientY - rect.top
  const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15
  const newScale = Math.min(3, Math.max(0.2, view.scale * factor))
  view.tx = sx - ((sx - view.tx) / view.scale) * newScale
  view.ty = sy - ((sy - view.ty) / view.scale) * newScale
  view.scale = newScale
  render()
}

function onCanvasDblClick(e: MouseEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  const id = hitTest(e.clientX - rect.left, e.clientY - rect.top)
  if (id) {
    router.push({ name: 'ResourceSceneEditor', params: { sceneId: id } })
  }
}

// ---------- 新建场景 ----------
function openCreateDialog() {
  newSceneName.value = ''
  showCreate.value = true
}

async function handleCreate() {
  const name = newSceneName.value.trim()
  if (!name) {
    message.warning('请输入场景名称')
    return
  }
  creating.value = true
  try {
    const res = await resourceApi.createScene(name)
    const created = res.data?.scene
    if (!created?.id) {
      throw new Error('创建场景失败：未返回场景 id')
    }
    message.success('场景创建成功')
    showCreate.value = false

    // 不触发全量刷新（loadData 较慢）：直接新增一个节点放在默认位置
    const charCount = created.name.length
    const estimatedWidth = charCount * 14 + 12
    const width = Math.max(60, Math.min(240, estimatedWidth))
    // 默认位置：画布可视区域中心（世界坐标）
    const wrap = canvasWrap.value
    const cw = wrap?.clientWidth ?? 800
    const ch = wrap?.clientHeight ?? 600
    const wx = (cw / 2 - view.tx) / view.scale
    const wy = (ch / 2 - view.ty) / view.scale
    // 稍微偏移避免与已有节点完全重叠
    const offset = Object.keys(nodes).length % 8 * 24
    nodes[created.id] = {
      id: created.id,
      name: created.name,
      x: wx + offset,
      y: wy + offset,
      vx: 0, vy: 0,
      width,
      height: 22,
      hasSymbol: false,
      hasBaseImage: false,
      edges: [],
    }
    scenes.value.push({ id: created.id, name: created.name, elements: [] })
    selectedNodeId.value = null
    render()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || e?.message || '创建场景失败')
  } finally {
    creating.value = false
  }
}

// ---------- 生命周期 ----------
let resizeObserver: ResizeObserver | null = null

onMounted(async () => {
  await nextTick()
  await new Promise(resolve => requestAnimationFrame(resolve))
  await loadData()

  resizeObserver = new ResizeObserver(() => fitView())
  if (canvasWrap.value) resizeObserver.observe(canvasWrap.value)
  window.addEventListener('resize', () => fitView())
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  window.removeEventListener('resize', render)
})
</script>

<style scoped>
.rg-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f7f9fc;
}
.rg-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid #e8e8e8;
  background: #fff;
  flex-shrink: 0;
}
.rg-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}
.rg-actions {
  display: flex;
  gap: 10px;
}
.rg-canvas-wrap {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.rg-canvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
}
.rg-canvas:active {
  cursor: grabbing;
}
.rg-hint {
  position: absolute;
  right: 16px;
  bottom: 12px;
  font-size: 12px;
  color: #999;
  background: rgba(255,255,255,0.85);
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #eee;
  pointer-events: none;
  user-select: none;
}
/* 右键菜单二级子菜单（连接至/断开连接）允许滚动，场景多时不溢出视口。
   n-dropdown 通过 teleport 渲染到 body，必须用 :global 全局生效 */
:global(.n-dropdown .n-dropdown-menu-wrapper .n-dropdown-menu) {
  max-height: min(50vh, 420px);
  overflow-y: auto;
}
</style>