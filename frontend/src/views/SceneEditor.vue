<template>
  <div class="scene-editor">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <n-space align="center">
        <n-button @click="$router.back()">
          <template #icon><n-icon><ArrowBackOutlined /></n-icon></template>
          返回
        </n-button>
        <n-h3 style="margin: 0; margin-left: 8px">场景编辑器</n-h3>
        <n-tag type="info">{{ sceneName }}</n-tag>
        <n-divider vertical />

        <!-- 工具按钮组 -->
        <n-radio-group v-model:value="toolMode" size="small">
          <n-radio-button value="pan">拖动</n-radio-button>
          <n-radio-button value="roi">框选ROI</n-radio-button>
          <n-radio-button value="coordinate">选择坐标</n-radio-button>
        </n-radio-group>
        <n-divider vertical />
        <n-text depth="3" style="font-family: Consolas">{{ coordText }}</n-text>
        <n-divider vertical />
        <n-button size="small" @click="showUploadDialog = true" type="primary">
          <template #icon><n-icon><AddOutlined /></n-icon></template>
          添加元素
        </n-button>
      </n-space>
    </div>

    <!-- 主区域：图像画布 + 右侧元素面板 -->
    <div class="main-area">
      <!-- 左侧：画布 -->
      <div class="canvas-wrapper" ref="canvasWrapper">
        <v-stage ref="stageRef" :config="stageConfig"
          @wheel="handleWheel"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        >
          <!-- 背景图层 -->
          <v-layer ref="bgLayer">
            <!-- 白色背景 -->
            <v-rect :config="{ x: 0, y: 0, width: 1600, height: 900, fill: '#ffffff', listening: false }" />
            <!-- 场景截图（如果有） -->
            <v-image v-if="bgImage" :config="bgImageConfig" />
          </v-layer>

          <!-- ROL 高亮层 -->
          <v-layer ref="highlightLayer">
            <v-rect v-for="r in roiHighlights" :key="r.id"
              :config="{
                x: r.x - r.width / 2,
                y: r.y - r.height / 2,
                width: r.width,
                height: r.height,
                fill: 'rgba(255,0,0,0.2)',
                stroke: '#ff0000',
                strokeWidth: 2,
                dash: [6, 3],
                listening: false
              }"
            />
          </v-layer>

          <!-- 选择层：ROI框 + 坐标点 -->
          <v-layer ref="selectionLayer">
            <v-rect v-if="selectionRect" :config="selectionRect" />
            <v-circle v-for="c in coordinateMarks" :key="c.id"
              :config="{
                x: c.x,
                y: c.y,
                radius: 6,
                fill: '#00ffff',
                stroke: '#0000ff',
                strokeWidth: 2,
                listening: false,
              }"
            />
          </v-layer>
        </v-stage>

        <!-- 坐标显示标签 -->
        <div class="coord-label" v-if="showCoordLabel">
          {{ hoverCoordText }}
        </div>
      </div>

      <!-- 右侧：元素列表 -->
      <div class="element-panel">
        <n-space vertical style="height: 100%">
          <n-h4 style="margin: 0">元素列表</n-h4>
          <n-spin :show="loadingElements" />
          <div class="element-list" ref="elementListRef">
            <n-list v-if="elements.length > 0" hoverable>
              <n-list-item v-for="elem in elements" :key="elem.id"
                :class="{ 'selected': selectedElementId === elem.id }"
                @click="handleSelectElement(elem)"
                @dblclick="handleEditElement(elem)"
              >
                <template #prefix>
                  <n-avatar v-if="elem.has_bgra" :size="36" :src="elementImageUrl(elem.id)"
                    fallback-src="/placeholder.png" />
                  <n-avatar v-else :size="36" style="background: #ccc">
                    <n-icon><ImageOutlined /></n-icon>
                  </n-avatar>
                </template>
                <n-thing :title="elem.name" :title-extra="elem.type">
                  <template #description>
                    <n-space size="small">
                      <n-tag size="tiny" :bordered="false">阈值: {{ (elem.threshold * 100).toFixed(0) }}%</n-tag>
                      <n-tag size="tiny" :bordered="false">匹配: {{ elem.match_type }}</n-tag>
                    </n-space>
                  </template>
                  <template #action>
                    <n-button text size="tiny" type="error" @click.stop="handleDeleteElement(elem)">
                      <template #icon><n-icon><DeleteOutlined /></n-icon></template>
                    </n-button>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
            <n-empty v-else description="暂无元素" />
          </div>
        </n-space>
      </div>
    </div>

    <!-- 新建元素对话框 -->
    <n-modal v-model:show="showUploadDialog" title="新建元素" preset="card" style="width: 520px">
      <n-space vertical>
        <n-form-item label="元素名称" required>
          <n-input v-model:value="newElement.name" placeholder="输入元素名称" />
        </n-form-item>
        <n-form-item label="类型">
          <n-select v-model:value="newElement.type" :options="[
            { label: 'IMG', value: 'IMG' },
            { label: 'COORDINATE', value: 'COORDINATE' },
          ]" />
        </n-form-item>
        <n-form-item label="匹配阈值">
          <n-slider v-model:value="newElement.threshold" :min="0" :max="1" :step="0.01" :format-tooltip="(v:number)=> (v*100).toFixed(0)+'%'" />
        </n-form-item>
        <n-form-item label="匹配方式">
          <n-select v-model:value="newElement.match_type" :options="[
            { label: 'TEMPLATE', value: 'TEMPLATE' },
            { label: 'FEATURE', value: 'FEATURE' },
          ]" />
        </n-form-item>
        <n-form-item label="图片文件" required>
          <n-upload :max="1" accept="image/*" :show-file-list="true"
            :custom-request="handleUploadFile" />
        </n-form-item>

        <!-- ROL -->
        <n-divider>ROI 区域</n-divider>
        <n-grid :cols="4" :x-gap="8">
          <n-grid-item><n-form-item label="X"><n-input-number v-model:value="newElement.roi_x" :min="0" :max="1600" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="Y"><n-input-number v-model:value="newElement.roi_y" :min="0" :max="900" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="宽"><n-input-number v-model:value="newElement.roi_width" :min="1" :max="1600" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="高"><n-input-number v-model:value="newElement.roi_height" :min="1" :max="900" size="small" /></n-form-item></n-grid-item>
        </n-grid>

        <!-- 坐标 -->
        <n-divider>元素坐标 / 比例</n-divider>
        <n-grid :cols="4" :x-gap="8">
          <n-grid-item><n-form-item label="X"><n-input-number v-model:value="newElement.coordinate_x" :min="0" :max="1600" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="Y"><n-input-number v-model:value="newElement.coordinate_y" :min="0" :max="900" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="比例X"><n-input-number v-model:value="newElement.ratio_x" :min="0" :max="1" :step="0.01" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="比例Y"><n-input-number v-model:value="newElement.ratio_y" :min="0" :max="1" :step="0.01" size="small" /></n-form-item></n-grid-item>
        </n-grid>

        <n-button type="primary" block @click="handleCreateElement" :loading="creatingElement">
          创建
        </n-button>
      </n-space>
    </n-modal>

    <!-- 编辑元素对话框 -->
    <n-modal v-model:show="showEditDialog" title="编辑元素" preset="card" style="width: 460px">
      <n-space v-if="editingElement" vertical>
        <n-form-item label="名称">
          <n-input v-model:value="editingElement.name" />
        </n-form-item>
        <n-form-item label="类型">
          <n-select v-model:value="editingElement.type" :options="[
            { label: 'IMG', value: 'IMG' },
            { label: 'COORDINATE', value: 'COORDINATE' },
          ]" />
        </n-form-item>
        <n-form-item label="匹配阈值">
          <n-slider v-model:value="editingElement.threshold" :min="0" :max="1" :step="0.01"
            :format-tooltip="(v:number)=> (v*100).toFixed(0)+'%'" />
        </n-form-item>
        <n-form-item label="匹配方式">
          <n-select v-model:value="editingElement.match_type" :options="[
            { label: 'TEMPLATE', value: 'TEMPLATE' },
            { label: 'FEATURE', value: 'FEATURE' },
          ]" />
        </n-form-item>
        <n-divider>ROI</n-divider>
        <n-grid :cols="4" :x-gap="8">
          <n-grid-item><n-form-item label="X"><n-input-number v-model:value="editingElement.roi_x" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="Y"><n-input-number v-model:value="editingElement.roi_y" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="宽"><n-input-number v-model:value="editingElement.roi_width" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="高"><n-input-number v-model:value="editingElement.roi_height" size="small" /></n-form-item></n-grid-item>
        </n-grid>
        <n-divider>坐标</n-divider>
        <n-grid :cols="4" :x-gap="8">
          <n-grid-item><n-form-item label="X"><n-input-number v-model:value="editingElement.coordinate_x" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="Y"><n-input-number v-model:value="editingElement.coordinate_y" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="比例X"><n-input-number v-model:value="editingElement.ratio_x" :step="0.01" size="small" /></n-form-item></n-grid-item>
          <n-grid-item><n-form-item label="比例Y"><n-input-number v-model:value="editingElement.ratio_y" :step="0.01" size="small" /></n-form-item></n-grid-item>
        </n-grid>
        <n-button type="primary" block @click="handleSaveElement" :loading="savingElement">保存</n-button>
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { ArrowBackOutlined, AddOutlined, ImageOutlined, DeleteOutlined } from '@vicons/material'
import { scenesApi, elementsApi } from '@/api/client'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()

// Scene info
const sceneName = computed(() => route.params.id as string || '')
const sceneId = ref('')

// Canvas Refs
const stageRef = ref<any>(null)
const canvasWrapper = ref<HTMLDivElement>()
const bgLayer = ref<any>(null)
const highlightLayer = ref<any>(null)
const selectionLayer = ref<any>(null)

// Canvas Config
const stageConfig = reactive({
  width: 800,
  height: 600,
  scaleX: 1,
  scaleY: 1,
  x: 0,
  y: 0,
  draggable: false,
})

// Background image
const bgImage = ref<HTMLImageElement | null>(null)
const bgImageConfig = computed(() => ({
  x: 0, y: 0,
  width: 1600, height: 900,
  image: bgImage.value,
  listening: false,
}))

// Tool mode
const toolMode = ref<'pan' | 'roi' | 'coordinate'>('pan')
const showCoordLabel = ref(false)
const hoverCoordText = ref('')
const coordText = computed(() => hoverCoordText.value || '(-, -)')

// Selection
const isSelecting = ref(false)
const selectionStart = ref<{ x: number; y: number } | null>(null)
const selectionEnd = ref<{ x: number; y: number } | null>(null)
const selectionRect = computed(() => {
  if (!isSelecting.value || !selectionStart.value || !selectionEnd.value) return null
  const s = selectionStart.value
  const e = selectionEnd.value
  return {
    x: Math.min(s.x, e.x),
    y: Math.min(s.y, e.y),
    width: Math.abs(e.x - s.x),
    height: Math.abs(e.y - s.y),
    fill: 'rgba(255,0,0,0.15)',
    stroke: '#ff0000',
    strokeWidth: 2,
    dash: [6, 3],
    listening: false,
  }
})

// Coordinate marks (for element positions)
const coordinateMarks = ref<Array<{ id: string; x: number; y: number }>>([])

// ROL highlights
const roiHighlights = ref<Array<{ id: string; x: number; y: number; width: number; height: number }>>([])

// Elements
const elements = ref<any[]>([])
const selectedElementId = ref<string | null>(null)
const loadingElements = ref(false)
const showUploadDialog = ref(false)
const showEditDialog = ref(false)
const creatingElement = ref(false)
const savingElement = ref(false)
const editingElement = ref<any>(null)
const uploadedFile = ref<File | null>(null)
const newElement = reactive({
  name: '',
  type: 'IMG',
  threshold: 0.8,
  match_type: 'TEMPLATE',
  ratio_x: 0.5,
  ratio_y: 0.5,
  roi_x: 0,
  roi_y: 0,
  roi_width: 1600,
  roi_height: 900,
  coordinate_x: 0,
  coordinate_y: 0,
})

// Pan
const isPanning = ref(false)
const panStart = ref<{ x: number; y: number }>({ x: 0, y: 0 })
const lastStagePos = ref<{ x: number; y: number }>({ x: 0, y: 0 })

// Element image URL
function elementImageUrl(id: string) {
  return `/api/elements/${id}/image?type=bgra`
}

// === Processing ===
function getRelativePos(e: any): { x: number; y: number } {
  const stage = stageRef.value?.getStage()
  if (!stage) return { x: 0, y: 0 }
  const pos = stage.getPointerPosition()
  return pos || { x: 0, y: 0 }
}

// === Wheel Zoom ===
function handleWheel(e: any) {
  e.evt.preventDefault()
  const stage = stageRef.value?.getStage()
  if (!stage) return

  const oldScale = stage.scaleX()
  const pointer = stage.getPointerPosition()!

  const direction = e.evt.deltaY > 0 ? -1 : 1
  const scaleBy = 1.1
  const newScale = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy

  // Clamp scale
  if (newScale < 0.1 || newScale > 5) return

  const mousePointTo = {
    x: (pointer.x - stage.x()) / oldScale,
    y: (pointer.y - stage.y()) / oldScale,
  }

  stageConfig.scaleX = newScale
  stageConfig.scaleY = newScale
  stageConfig.x = pointer.x - mousePointTo.x * newScale
  stageConfig.y = pointer.y - mousePointTo.y * newScale
}

// === Mouse Events ===
function handleMouseDown(e: any) {
  const pos = getRelativePos(e)

  if (toolMode.value === 'pan') {
    isPanning.value = true
    panStart.value = { x: pos.x, y: pos.y }
    lastStagePos.value = { x: stageConfig.x, y: stageConfig.y }
    return
  }

  if (toolMode.value === 'roi') {
    isSelecting.value = true
    selectionStart.value = pos
    selectionEnd.value = pos
    return
  }

  if (toolMode.value === 'coordinate') {
    // Add coordinate mark and update newElement
    newElement.coordinate_x = Math.round(pos.x)
    newElement.coordinate_y = Math.round(pos.y)
    message.info(`坐标已设置: (${Math.round(pos.x)}, ${Math.round(pos.y)})`)
    coordinateMarks.value.push({
      id: `click-${Date.now()}`,
      x: pos.x,
      y: pos.y,
    })
    // Keep only the latest mark
    if (coordinateMarks.value.length > 1) {
      coordinateMarks.value = coordinateMarks.value.slice(-1)
    }
    toolMode.value = 'pan' // Reset to pan mode after coordinate selected
  }
}

function handleMouseMove(e: any) {
  const pos = getRelativePos(e)

  // Update hover coordinate display
  showCoordLabel.value = true
  hoverCoordText.value = `(${Math.round(pos.x)}, ${Math.round(pos.y)})`

  if (isPanning.value) {
    const dx = pos.x - panStart.value.x
    const dy = pos.y - panStart.value.y
    stageConfig.x = lastStagePos.value.x + dx
    stageConfig.y = lastStagePos.value.y + dy
    return
  }

  if (isSelecting.value) {
    selectionEnd.value = pos
  }
}

function handleMouseUp(_e: any) {
  if (isPanning.value) {
    isPanning.value = false
    return
  }

  if (isSelecting.value) {
    isSelecting.value = false
    // Set ROL values from selection
    if (selectionStart.value && selectionEnd.value) {
      const x = Math.min(selectionStart.value.x, selectionEnd.value.x)
      const y = Math.min(selectionStart.value.y, selectionEnd.value.y)
      const w = Math.abs(selectionEnd.value.x - selectionStart.value.x)
      const h = Math.abs(selectionEnd.value.y - selectionStart.value.y)
      newElement.roi_x = Math.round(x)
      newElement.roi_y = Math.round(y)
      newElement.roi_width = Math.round(w)
      newElement.roi_height = Math.round(h)
      message.info(`ROI 已设置: (${Math.round(x)}, ${Math.round(y)}) ${Math.round(w)}×${Math.round(h)}`)
    }
    // Reset selection rect
    selectionStart.value = null
    selectionEnd.value = null
    toolMode.value = 'pan' // Reset to pan mode after ROI selected
  }
}

// === Element Selection ===
function handleSelectElement(elem: any) {
  selectedElementId.value = elem.id
  // Highlight element position on canvas
  coordinateMarks.value = [{
    id: elem.id,
    x: elem.coordinate_x,
    y: elem.coordinate_y,
  }]
  // Also show ROI highlight
  roiHighlights.value = [{
    id: elem.id,
    x: elem.roi_x + elem.roi_width / 2,
    y: elem.roi_y + elem.roi_height / 2,
    width: elem.roi_width,
    height: elem.roi_height,
  }]
}

function handleEditElement(elem: any) {
  editingElement.value = {
    ...elem,
    threshold: elem.threshold || 0.8,
    match_type: elem.match_type || 'TEMPLATE',
    ratio_x: elem.ratio_x || 0.5,
    ratio_y: elem.ratio_y || 0.5,
    roi_x: elem.roi_x || 0,
    roi_y: elem.roi_y || 0,
    roi_width: elem.roi_width || 1600,
    roi_height: elem.roi_height || 900,
    coordinate_x: elem.coordinate_x || 0,
    coordinate_y: elem.coordinate_y || 0,
  }
  showEditDialog.value = true
}

async function handleDeleteElement(elem: any) {
  dialog.warning({
    title: '删除元素',
    content: `确定要删除元素 "${elem.name}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await elementsApi.delete(elem.id)
        message.success('元素已删除')
        await loadElements()
      } catch (e: any) {
        message.error('删除失败: ' + (e.response?.data?.detail || e.message))
      }
    },
  })
}

// === Element Create ===
function handleUploadFile({ file }: any) {
  uploadedFile.value = file.file
}

async function handleCreateElement() {
  if (!newElement.name || !uploadedFile.value) {
    message.warning('请填写元素名称并上传图片')
    return
  }
  creatingElement.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('name', newElement.name)
    formData.append('scene_name', sceneName.value)
    formData.append('type', newElement.type)
    formData.append('threshold', String(newElement.threshold))
    formData.append('match_type', newElement.match_type)
    formData.append('ratio_x', String(newElement.ratio_x))
    formData.append('ratio_y', String(newElement.ratio_y))
    formData.append('roi_x', String(newElement.roi_x))
    formData.append('roi_y', String(newElement.roi_y))
    formData.append('roi_width', String(newElement.roi_width))
    formData.append('roi_height', String(newElement.roi_height))
    formData.append('coordinate_x', String(newElement.coordinate_x))
    formData.append('coordinate_y', String(newElement.coordinate_y))

    await elementsApi.create(formData)
    message.success('元素创建成功')
    showUploadDialog.value = false
    // Reset form
    newElement.name = ''
    uploadedFile.value = null
    await loadElements()
  } catch (e: any) {
    message.error('创建失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    creatingElement.value = false
  }
}

// === Element Save ===
async function handleSaveElement() {
  if (!editingElement.value) return
  savingElement.value = true
  try {
    await elementsApi.update(editingElement.value.id, {
      name: editingElement.value.name,
      type: editingElement.value.type,
      threshold: editingElement.value.threshold,
      match_type: editingElement.value.match_type,
      ratio_x: editingElement.value.ratio_x,
      ratio_y: editingElement.value.ratio_y,
      roi_x: editingElement.value.roi_x,
      roi_y: editingElement.value.roi_y,
      roi_width: editingElement.value.roi_width,
      roi_height: editingElement.value.roi_height,
      coordinate_x: editingElement.value.coordinate_x,
      coordinate_y: editingElement.value.coordinate_y,
    })
    message.success('元素更新成功')
    showEditDialog.value = false
    editingElement.value = null
    await loadElements()
  } catch (e: any) {
    message.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    savingElement.value = false
  }
}

// === Data Loading ===
async function loadElements() {
  loadingElements.value = true
  try {
    const res = await elementsApi.list()
    // Filter elements belonging to this scene
    const all = (res.data || []) as any[]
    elements.value = all.filter((e: any) => e.scene_name === sceneName.value)
  } catch (e: any) {
    message.error('加载元素失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    loadingElements.value = false
  }
}

async function loadSceneImage() {
  try {
    const res = await scenesApi.getImage(sceneName.value)
    const blob = res.data as Blob
    if (blob && blob.size > 0) {
      const url = URL.createObjectURL(blob)
      const img = new Image()
      img.onload = () => {
        bgImage.value = img
      }
      img.src = url
    }
  } catch {
    // No image or error - show default white background
    bgImage.value = null
  }
}

async function loadSceneInfo() {
  try {
    const res = await scenesApi.get(sceneName.value)
    sceneId.value = res.data?.id || ''
  } catch {
    // ignore
  }
}

// === Watchers ===
watch(toolMode, (mode) => {
  const stage = stageRef.value?.getStage()
  if (!stage) return
  const container = stage.container()
  if (mode === 'roi' || mode === 'coordinate') {
    container.style.cursor = 'crosshair'
  } else {
    container.style.cursor = 'grab'
  }
})

// === Lifecycle ===
let resizeObserver: ResizeObserver | null = null

function updateStageSize() {
  if (!canvasWrapper.value) return
  const rect = canvasWrapper.value.getBoundingClientRect()
  stageConfig.width = rect.width
  stageConfig.height = rect.height
}

onMounted(async () => {
  await Promise.all([
    loadSceneInfo(),
    loadSceneImage(),
    loadElements(),
  ])

  updateStageSize()
  if (canvasWrapper.value) {
    resizeObserver = new ResizeObserver(updateStageSize)
    resizeObserver.observe(canvasWrapper.value)
  }

  // Fit to screen
  setTimeout(() => {
    const stage = stageRef.value?.getStage()
    if (stage) {
      // Center and fit
      stageConfig.x = (stage.width() - 1600) / 2
      stageConfig.y = (stage.height() - 900) / 2
    }
  }, 100)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.scene-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.toolbar {
  padding: 8px 16px;
  background: var(--n-color);
  border-bottom: 1px solid var(--n-border-color);
  flex-shrink: 0;
}

.main-area {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.canvas-wrapper {
  flex: 1;
  position: relative;
  background: #1a1a2e;
  border-right: 1px solid var(--n-border-color);
  overflow: hidden;
}

.coord-label {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: #00ff00;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: Consolas, monospace;
  font-size: 12px;
  pointer-events: none;
  z-index: 10;
}

.element-panel {
  width: 280px;
  flex-shrink: 0;
  padding: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.element-list {
  flex: 1;
  overflow-y: auto;
}

.element-list :deep(.n-list-item) {
  cursor: pointer;
}

.element-list :deep(.n-list-item.selected) {
  background: rgba(64, 158, 255, 0.1);
  border-left: 3px solid #409eff;
}
</style>