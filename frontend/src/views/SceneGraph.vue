<template>
  <div class="scene-graph-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <n-space align="center">
        <n-h3 style="margin: 0">场景管理</n-h3>
        <n-button size="small" type="primary" @click="showAddSceneDialog = true">
          <template #icon><n-icon><AddOutlined /></n-icon></template>
          新建场景
        </n-button>
        <n-button size="small" @click="showAddEdgeDialog = true" :disabled="scenes.length < 2">
          <template #icon><n-icon><AccountTreeOutlined /></n-icon></template>
          添加跳转
        </n-button>
        <n-button size="small" @click="autoLayout">
          <template #icon><n-icon><RefreshOutlined /></n-icon></template>
          自动布局
        </n-button>
        <n-button size="small" @click="fitToScreen">
          <template #icon><n-icon><ScannerOutlined /></n-icon></template>
          适应屏幕
        </n-button>
        <n-divider vertical />
        <n-tag type="info">{{ scenes.length }} 个场景</n-tag>
        <n-tag type="success">{{ edgeCount }} 条跳转</n-tag>
        <n-spin v-if="loading" size="small" />
      </n-space>
    </div>

    <!-- 图可视区域 -->
    <div class="cy-container" ref="cyContainer"></div>

    <!-- 图例 -->
    <div class="legend">
      <n-space vertical size="small">
        <n-text depth="3" style="font-size: 12px">图例：</n-text>
        <n-space align="center" :size="4">
          <div class="legend-dot" style="background: #4682b4"></div>
          <n-text depth="3" style="font-size: 12px">正常</n-text>
        </n-space>
        <n-space align="center" :size="4">
          <div class="legend-dot" style="background: #ff0000"></div>
          <n-text depth="3" style="font-size: 12px">缺少元素</n-text>
        </n-space>
        <n-space align="center" :size="4">
          <div class="legend-dot" style="background: #ffd700"></div>
          <n-text depth="3" style="font-size: 12px">缺少截图</n-text>
        </n-space>
        <n-space align="center" :size="4">
          <div class="legend-line" style="background: #696969; width: 24px; height: 3px"></div>
          <n-text depth="3" style="font-size: 12px">已实现</n-text>
        </n-space>
        <n-space align="center" :size="4">
          <div class="legend-line" style="background: #dc143c; width: 24px; height: 3px"></div>
          <n-text depth="3" style="font-size: 12px">未实现</n-text>
        </n-space>
      </n-space>
    </div>

    <!-- 新建场景对话框 -->
    <n-modal v-model:show="showAddSceneDialog" title="新建场景" preset="card" style="width: 420px">
      <n-space vertical>
        <n-input v-model:value="newSceneName" placeholder="输入场景名称" @keyup.enter="handleAddScene" />
        <n-button type="primary" block @click="handleAddScene" :loading="addingScene">
          创建
        </n-button>
      </n-space>
    </n-modal>

    <!-- 添加跳转关系对话框 -->
    <n-modal v-model:show="showAddEdgeDialog" title="添加跳转关系" preset="card" style="width: 420px">
      <n-space vertical>
        <n-form-item label="源场景">
          <n-select v-model:value="edgeSource" :options="sceneOptions" placeholder="选择源场景" />
        </n-form-item>
        <n-form-item label="目标场景">
          <n-select v-model:value="edgeTarget" :options="sceneOptions" placeholder="选择目标场景" />
        </n-form-item>
        <n-button type="primary" block @click="handleAddEdge" :loading="addingEdge"
          :disabled="!edgeSource || !edgeTarget || edgeSource === edgeTarget">
          添加跳转
        </n-button>
      </n-space>
    </n-modal>

    <!-- 场景详情抽屉 -->
    <n-drawer v-model:show="showSceneDetail" :width="400">
      <n-drawer-content :title="selectedScene?.name || '场景详情'">
        <n-descriptions v-if="selectedScene" :column="1" bordered size="small">
          <n-descriptions-item label="场景名称">{{ selectedScene.name }}</n-descriptions-item>
          <n-descriptions-item label="场景ID">{{ selectedScene.id }}</n-descriptions-item>
          <n-descriptions-item label="元素数量">{{ selectedScene.elementCount }}</n-descriptions-item>
          <n-descriptions-item label="出边数量">{{ selectedScene.outEdgeCount }}</n-descriptions-item>
          <n-descriptions-item label="入边数量">{{ selectedScene.inEdgeCount }}</n-descriptions-item>
          <n-descriptions-item label="创建时间">{{ selectedScene.createdAt }}</n-descriptions-item>
          <n-descriptions-item label="更新时间">{{ selectedScene.updatedAt }}</n-descriptions-item>
        </n-descriptions>
        <template #footer>
          <n-space>
            <n-button type="primary" @click="handleEditScene">编辑场景</n-button>
            <n-button type="error" @click="handleDeleteScene">删除场景</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { AddOutlined, AccountTreeOutlined, RefreshOutlined, ScannerOutlined } from '@vicons/material'
import cytoscape from 'cytoscape'
import type { Core, NodeSingular, EdgeSingular, NodeCollection } from 'cytoscape'
import { scenesApi, elementsApi } from '@/api/client'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

// Refs
const cyContainer = ref<HTMLDivElement>()
const cy = ref<Core | null>(null)
const loading = ref(false)
const showAddSceneDialog = ref(false)
const showAddEdgeDialog = ref(false)
const showSceneDetail = ref(false)
const newSceneName = ref('')
const addingScene = ref(false)
const addingEdge = ref(false)
const edgeSource = ref<string | null>(null)
const edgeTarget = ref<string | null>(null)
const scenes = ref<any[]>([])
const edges = ref<any[]>([])
const elements = ref<any[]>([])  // 所有元素列表，用于检查场景是否有元素
const selectedScene = ref<any>(null)
const highlightedNode = ref<NodeSingular | null>(null)

// Computed
const sceneOptions = computed(() =>
  scenes.value.map(s => ({ label: s.name, value: s.name }))
)

const edgeCount = computed(() => edges.value.length)

// 场景名称到ID的映射
const nameToId = computed(() => {
  const map: Record<string, string> = {}
  scenes.value.forEach(s => { map[s.name] = s.id })
  return map
})

// API: 加载所有场景和边
async function loadData() {
  loading.value = true
  try {
    const [sceneList, elementList] = await Promise.all([
      scenesApi.list(),
      elementsApi.list(),
    ])
    scenes.value = (sceneList.data || []) as any[]
    elements.value = (elementList.data || []) as any[]

    // 从场景详情中提取边关系
    const allEdges: any[] = []
    const edgeSet = new Set<string>()
    for (const scene of scenes.value) {
      try {
        const detail = await scenesApi.get(scene.name)
        if (detail.data?.out_edges) {
          for (const edge of detail.data.out_edges) {
            const key = `${edge.source}->${edge.target}`
            if (!edgeSet.has(key)) {
              edgeSet.add(key)
              allEdges.push(edge)
            }
          }
        }
      } catch {
        // skip
      }
    }
    edges.value = allEdges

    await nextTick()
    buildGraph()
  } catch (e: any) {
    message.error('加载场景数据失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

// 检查场景是否有元素（除 scene_id 为 1 的元素外）
function hasElements(sceneName: string): boolean {
  return elements.value.some(
    e => {
      // 通过 API 返回的 scene_name 来判断
      // 如果 API 未返回 scene_name，则尝试通过场景ID匹配
      return (e.scene_name === sceneName) && e.type !== 'COORDINATE' || (e.type === 'COORDINATE')
    }
  )
}

// 检查场景是否有截图
function hasScreenshot(sceneName: string): boolean {
  // 通过尝试获取场景图片来判断
  // 简化处理：假设数据库中有截图记录的都会返回 has_bgra = true 的元素
  return elements.value.some(e => e.scene_name === sceneName && e.has_bgra)
}

// 构建 Cytoscape 图
function buildGraph() {
  if (!cyContainer.value) return

  // 销毁旧图
  if (cy.value) {
    cy.value.destroy()
    cy.value = null
  }

  // 构建节点元素
  const nodes = scenes.value.map(s => {
    const hasElem = hasElements(s.name)
    const hasShot = hasScreenshot(s.name)
    let color = '#4682b4' // 正常：蓝色
    if (!hasElem) {
      color = '#ff0000' // 缺少元素：红色
    } else if (!hasShot) {
      color = '#ffd700' // 缺少截图：黄色
    }
    return {
      data: {
        id: s.name,
        label: s.name,
        sceneId: s.id,
        elementCount: s.element_count,
        outEdgeCount: s.out_edge_count,
        inEdgeCount: s.in_edge_count,
        createdAt: s.created_at,
        updatedAt: s.updated_at,
        color,
      },
    }
  })

  // 构建边元素，区分已实现/未实现
  const cyEdges = edges.value.map(e => {
    const source = e.source
    const target = e.target
    // 检查是否有跳转关系（通过出边判断）
    const isImplemented = scenes.value.some(
      s => s.name === source && s.out_edge_count > 0
    )
    const edgeColor = isImplemented ? '#696969' : '#dc143c'

    return {
      data: {
        id: `${source}->${target}`,
        source,
        target,
        color: edgeColor,
        implemented: isImplemented,
      },
    }
  })

  const instance = cytoscape({
    container: cyContainer.value,
    elements: [...nodes, ...cyEdges],
    style: [
      // 节点样式
      {
        selector: 'node',
        style: {
          'background-color': 'data(color)',
          'label': 'data(label)',
          'color': '#ffffff',
          'font-size': '16px',
          'font-family': 'SimHei, Microsoft YaHei, sans-serif',
          'font-weight': 'bold',
          'text-valign': 'center',
          'text-halign': 'center',
          'text-wrap': 'wrap',
          'text-max-width': '200px',
          'shape': 'round-rectangle',
          'width': 'label',
          'height': 'label',
          'padding': '20px',
          'border-width': 2,
          'border-color': '#000000',
          'text-outline-width': 1,
          'text-outline-color': '#333333',
          'min-width': '120px',
          'min-height': '60px',
        },
      },
      // 边样式
      {
        selector: 'edge',
        style: {
          'width': 4,
          'line-color': 'data(color)',
          'target-arrow-color': 'data(color)',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 1.5,
          'curve-style': 'bezier',
        },
      },
      // 选中节点高亮
      {
        selector: 'node:selected',
        style: {
          'background-color': '#39c5bb',
          'border-color': '#00ffff',
          'border-width': 4,
        },
      },
      // 边选中
      {
        selector: 'edge:selected',
        style: {
          'line-color': '#ff8c00',
          'target-arrow-color': '#ff8c00',
          'width': 6,
        },
      },
    ],
    layout: {
      name: 'breadthfirst',
      directed: true,
      padding: 30,
      spacingFactor: 1.5,
      animate: true,
      animationDuration: 500,
    },
    wheelSensitivity: 0.3,
    minZoom: 0.1,
    maxZoom: 3,
    autoungrabify: false,
    autounselectify: false,
  })

  // 节点双击 → 编辑场景
  instance.on('dblclick', 'node', (evt: { target: NodeSingular }) => {
    const node = evt.target
    const sceneName = node.data('id')
    router.push({ name: 'SceneEditor', params: { id: sceneName } })
  })

  // 节点单击 → 选中高亮
  instance.on('tap', 'node', (evt: { target: NodeSingular }) => {
    const node = evt.target
    if (highlightedNode.value && highlightedNode.value.id() === node.id()) {
      // 取消高亮
      clearHighlights()
      return
    }
    clearHighlights()
    highlightedNode.value = node

    // 高亮当前节点
    node.style('background-color', '#39c5bb')
    node.style('border-color', '#00ffff')
    node.style('border-width', 4)

    // 高亮邻接节点
    const neighborhood = node.closedNeighborhood()
    neighborhood.nodes().forEach((n: NodeSingular) => {
      if (n.id() !== node.id()) {
        n.style('background-color', '#39c5bb')
      }
    })
  })

  // 点击空白区域取消高亮
  instance.on('tap', (evt: { target: any }) => {
    if (evt.target === instance) {
      clearHighlights()
    }
  })

  // 右键菜单
  instance.on('cxttap', 'node', (evt: { target: NodeSingular; originalEvent: MouseEvent }) => {
    const node = evt.target
    const sceneName = node.data('id')

    // 使用 Naive UI 的 dialog 作为右键菜单
    dialog.warning({
      title: `场景: ${sceneName}`,
      content: '选择操作',
      positiveText: '关闭',
      negativeText: '复制名称',
      showIcon: false,
      action: () => {
        navigator.clipboard.writeText(sceneName).then(() => {
          message.success('已复制场景名称')
        })
      },
      onPositiveClick: () => { /* 关闭 */ },
      onClose: () => { /* 关闭 */ },
    })
  })

  // 边右键 → 删除
  instance.on('cxttap', 'edge', (evt: { target: EdgeSingular }) => {
    const edge = evt.target
    const source = edge.data('source')
    const target = edge.data('target')

    dialog.warning({
      title: '删除跳转关系',
      content: `确定要删除 "${source}" → "${target}" 的跳转关系吗？`,
      positiveText: '确定删除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await scenesApi.deleteEdge(source, target)
          instance.remove(edge)
          message.success('已删除跳转关系')
          await loadData()
        } catch (e: any) {
          message.error('删除失败: ' + (e.response?.data?.detail || e.message))
        }
      },
    })
  })

  // 节点拖拽结束 → 保存位置（暂不持久化到后端）
  instance.on('free', 'node', () => {
    // 节点位置变更，可以考虑在后期持久化
  })

  cy.value = instance
}

// 清除所有高亮
function clearHighlights() {
  if (!cy.value) return
  highlightedNode.value = null
  cy.value.nodes().forEach((node: NodeSingular) => {
    const originalColor = node.data('color') || '#4682b4'
    node.style('background-color', originalColor)
    node.style('border-color', '#000000')
    node.style('border-width', 2)
  })
}

// 自动布局
function autoLayout() {
  if (!cy.value) return
  cy.value.layout({
    name: 'breadthfirst',
    directed: true,
    padding: 30,
    spacingFactor: 1.5,
    animate: true,
    animationDuration: 500,
  }).run()
}

// 适应屏幕
function fitToScreen() {
  if (!cy.value) return
  cy.value.fit(undefined, 50)
}

// 新建场景
async function handleAddScene() {
  const name = newSceneName.value.trim()
  if (!name) {
    message.warning('请输入场景名称')
    return
  }
  addingScene.value = true
  try {
    await scenesApi.create({ name })
    message.success(`场景 "${name}" 创建成功`)
    showAddSceneDialog.value = false
    newSceneName.value = ''
    await loadData()
  } catch (e: any) {
    message.error('创建失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    addingScene.value = false
  }
}

// 添加跳转关系
async function handleAddEdge() {
  if (!edgeSource.value || !edgeTarget.value) return
  addingEdge.value = true
  try {
    await scenesApi.addEdge(edgeSource.value, edgeTarget.value)
    message.success(`跳转 "${edgeSource.value}" → "${edgeTarget.value}" 添加成功`)
    showAddEdgeDialog.value = false
    edgeSource.value = null
    edgeTarget.value = null
    await loadData()
  } catch (e: any) {
    message.error('添加失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    addingEdge.value = false
  }
}

// 编辑场景
function handleEditScene() {
  if (!selectedScene.value) return
  router.push({ name: 'SceneEditor', params: { id: selectedScene.value.name } })
  showSceneDetail.value = false
}

// 删除场景
async function handleDeleteScene() {
  if (!selectedScene.value) return
  const name = selectedScene.value.name

  dialog.warning({
    title: '删除场景',
    content: `确定要删除场景 "${name}" 及其所有元素和跳转关系吗？此操作不可撤销！`,
    positiveText: '确定删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await scenesApi.delete(name)
        message.success(`场景 "${name}" 已删除`)
        showSceneDetail.value = false
        selectedScene.value = null
        await loadData()
      } catch (e: any) {
        message.error('删除失败: ' + (e.response?.data?.detail || e.message))
      }
    },
  })
}

// 生命周期
let resizeObserver: ResizeObserver | null = null
onMounted(async () => {
  await loadData()
  if (cyContainer.value) {
    resizeObserver = new ResizeObserver(() => {
      if (cy.value) {
        cy.value.resize()
        cy.value.fit(undefined, 50)
      }
    })
    resizeObserver.observe(cyContainer.value)
  }
})

onBeforeUnmount(() => {
  if (cy.value) {
    cy.value.destroy()
    cy.value = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

// 监听场景数据变化，重新构建图
watch([scenes, edges], () => {
  if (cy.value) {
    // 增量更新而不是完全重建
    buildGraph()
  }
}, { deep: true })
</script>

<style scoped>
.scene-graph-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  position: relative;
}

.toolbar {
  padding: 8px 16px;
  background: var(--n-color);
  border-bottom: 1px solid var(--n-border-color);
  flex-shrink: 0;
}

.cy-container {
  flex: 1;
  width: 100%;
  min-height: 400px;
  background: #1a1a2e;
  border-radius: 0 0 8px 8px;
}

.legend {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.75);
  padding: 8px 12px;
  border-radius: 6px;
  z-index: 10;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.legend-line {
  border-radius: 2px;
}
</style>