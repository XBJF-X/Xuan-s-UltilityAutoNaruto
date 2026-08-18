<template>
  <n-message-provider>
    <div class="scene-editor">
      <!-- 顶部工具栏 -->
      <div class="se-toolbar">
        <n-space align="center">
          <n-button quaternary size="small" @click="goBack">
            ← 返回场景图
          </n-button>
          <n-h3 style="margin: 0" class="se-title">
            场景编辑器：{{ scene?.name ?? sceneId }}
          </n-h3>
          <n-tag size="small" :type="baseImage ? 'success' : 'warning'">
            {{ baseImage ? `底图 ${baseSize.width}×${baseSize.height}` : '无底图(白色占位)' }}
          </n-tag>
          <n-tag v-if="selectionMode === 'roi'" type="error" size="small">
            框选 ROI 模式：拖拽鼠标绘制区域
          </n-tag>
          <n-tag v-else-if="selectionMode === 'coordinate'" type="error" size="small">
            坐标点选模式：点击底图设置坐标
          </n-tag>
        </n-space>
        <n-space>
          <n-button size="small" @click="triggerBaseImageFile" :loading="uploadingBase">设置底图</n-button>
          <input
            ref="baseFileInput"
            type="file"
            accept="image/png"
            style="display: none"
            @change="onBaseImageFileSelected"
          />
          <n-button size="small" @click="refreshBaseImage" :loading="baseLoading">刷新底图</n-button>
          <n-button size="small" @click="handleRefreshElements" :loading="loading">刷新场景</n-button>
          <n-button size="small" type="primary" @click="openCreateElement">新建元素</n-button>
        </n-space>
      </div>

      <!-- 主体：左3/4 底图 + 右1/4 树与属性 -->
      <div class="se-body">
        <!-- 左 3/4：底图绘制区 -->
        <div
          ref="canvasWrap"
          class="se-canvas-wrap"
          @dragover.prevent="onBaseImageDragOver"
          @drop.prevent="onBaseImageDrop"
        >
          <canvas ref="canvasEl" class="se-canvas" @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @wheel.prevent="onWheel"></canvas>
          <div class="se-hint">
            {{ selectionMode === 'roi' ? '拖拽鼠标框选 ROI 区域' : selectionMode === 'coordinate' ? '点击底图设置坐标' : '滚轮缩放 · 拖拽平移 · 拖入 PNG 图片可设为底图' }}
          </div>
        </div>

        <!-- 右 1/4：元素树 + 属性面板 -->
        <div class="se-right">
          <!-- 上：元素树（根=场景节点，叶=元素节点） -->
          <div class="se-tree">
            <div class="se-panel-title">
              <span>元素列表</span>
              <n-tag size="small" round>{{ elements.length }}</n-tag>
            </div>
            <n-tree
              v-if="treeData.length > 0"
              :data="treeData"
              :default-expanded-keys="treeExpandedKeys"
              :selected-keys="selectedKeys"
              :render-label="renderTreeLabel"
              block-line
              selectable
              @update:selected-keys="onTreeSelect"
            />
            <n-empty v-else description="暂无元素" style="padding: 16px 0" />
          </div>

          <!-- 下：属性 -->
          <div class="se-props">
            <div class="se-panel-title">
              <span>属性</span>
              <span
                v-if="selectedElement"
                class="elem-type-badge"
                :style="{ background: badgeInfo.bg }"
              >{{ badgeInfo.text }}</span>
              <n-tag v-else-if="selectedSceneMode" size="small" type="info">场景</n-tag>
            </div>

            <!-- 未选中任何对象 -->
            <n-empty
              v-if="!selectedElement && !selectedSceneMode"
              description="点击左侧树节点查看/编辑属性"
              style="padding: 16px 0"
            />

            <!-- 场景属性面板 -->
            <div v-else-if="selectedSceneMode" class="se-prop-form">
              <n-form label-placement="left" label-width="86" size="small">
                <n-form-item label="场景名称">
                  <n-input v-model:value="sceneNameForm" @keyup.enter="saveSceneName" />
                </n-form-item>
                <n-form-item label="底图文件">
                  <n-text depth="3" style="font-size: 12px; word-break: break-all">
                    test_scene/{{ scene?.name ?? sceneId }}.png
                  </n-text>
                </n-form-item>
                <n-form-item label="元素数量">
                  <n-text>{{ elements.length }}</n-text>
                </n-form-item>
                <n-form-item label="执行匹配">
                  <n-text depth="3" style="font-size: 12px">
                    识别当前底图属于哪个场景（recognizer.scene）
                  </n-text>
                </n-form-item>
              </n-form>
              <n-space justify="end" size="small" class="se-prop-actions">
                <n-button
                  size="small"
                  :loading="sceneMatching"
                  @click="handleSceneMatch"
                >
                  识别当前场景
                </n-button>
                <n-button size="small" type="primary" :loading="savingScene" @click="saveSceneName">
                  保存场景名
                </n-button>
              </n-space>

              <!-- 场景匹配结果 -->
              <n-collapse-transition :show="sceneMatchResult !== null">
                <div class="match-result">
                  <n-tag v-if="sceneMatchResult?.ok && sceneMatchResult?.matched" type="success" size="small" round>
                    识别成功：{{ sceneMatchResult.recognized }}
                  </n-tag>
                  <n-tag v-else-if="sceneMatchResult?.ok" type="warning" size="small" round>
                    识别为其他场景：{{ sceneMatchResult.recognized }}
                  </n-tag>
                  <n-tag v-else type="error" size="small" round>
                    识别失败：{{ sceneMatchResult?.error ?? '未知错误' }}
                  </n-tag>
                </div>
              </n-collapse-transition>
            </div>
            <!-- 元素属性面板 -->
            <div v-else class="se-prop-form">
              <n-form label-placement="left" label-width="86" size="small">
                <n-form-item label="名称">
                  <n-input v-model:value="propForm.name" @keyup.enter="saveElement" />
                </n-form-item>
                <n-form-item label="类型">
                  <n-select v-model:value="propForm.element_type" :options="elementTypeOptions" />
                </n-form-item>

                <!-- IMG 元素专属属性 -->
                <template v-if="propForm.element_type === 0">
                  <n-form-item label="标志">
                    <n-switch v-model:value="propForm.symbol" @update:value="onSymbolChange" />
                    <n-text depth="3" style="font-size: 11px; margin-left: 6px">
                      作为该场景的标志元素（优先级最高）
                    </n-text>
                  </n-form-item>
                  <n-form-item label="匹配方式">
                    <n-select v-model:value="propForm.match_type" :options="matchTypeOptions" />
                  </n-form-item>
                  <n-form-item label="阈值">
                    <n-input-number v-model:value="propForm.threshold" :min="0" :max="1" :step="0.01" style="width: 100%" />
                  </n-form-item>
                  <n-form-item label="ROI">
                    <div class="roi-display">
                      <n-tag size="small" :type="hasRoi ? 'success' : 'default'">
                        {{ roiLabel }}
                      </n-tag>
                      <n-button size="small" @click="enterRoiMode">框选ROI</n-button>
                    </div>
                  </n-form-item>
                  <n-form-item label="Ratio">
                    <div class="roi-display">
                      <n-tag size="small" type="info">
                        ({{ propForm.ratio_x.toFixed(2) }}, {{ propForm.ratio_y.toFixed(2) }})
                      </n-tag>
                      <n-button size="small" @click="openRatioDialog">设置Ratio</n-button>
                    </div>
                  </n-form-item>
                </template>

                <!-- COORDINATE 元素专属属性 -->
                <template v-else-if="propForm.element_type === 1">
                  <n-form-item label="坐标">
                    <div class="roi-display">
                      <n-tag size="small" type="success">
                        ({{ propForm.coordinate_x }}, {{ propForm.coordinate_y }})
                      </n-tag>
                      <n-button size="small" @click="enterCoordMode">设置坐标</n-button>
                    </div>
                  </n-form-item>
                </template>

                <!-- OCR 元素专属属性 -->
                <template v-else-if="propForm.element_type === 2">
                  <n-form-item label="ROI">
                    <div class="roi-display">
                      <n-tag size="small" :type="hasRoi ? 'success' : 'default'">
                        {{ roiLabel }}
                      </n-tag>
                      <n-button size="small" @click="enterRoiMode">框选ROI</n-button>
                    </div>
                  </n-form-item>
                  <n-form-item label="OCR阈值">
                    <n-input-number v-model:value="propForm.ocr_min_score" :min="0" :max="1" :step="0.05" style="width: 100%" />
                  </n-form-item>
                  <n-form-item label="执行识别">
                    <n-button size="small" :loading="ocrRunning" @click="handleElementOcr">
                      {{ ocrResultText || '执行 OCR 识别' }}
                    </n-button>
                  </n-form-item>
                </template>
              </n-form>

              <!-- 元素操作按钮 -->
              <n-space justify="space-between" size="small" class="se-prop-actions">
                <n-space size="small">
                  <!-- IMG 元素图片操作 -->
                  <template v-if="propForm.element_type === 0">
                    <n-button size="small" @click="previewElementImage">查看图片</n-button>
                    <n-button size="small" @click="triggerImageFile">选择图片</n-button>
                  </template>
                  <!-- IMG/OCR 执行匹配/识别 -->
                  <n-button
                    v-if="propForm.element_type === 0"
                    size="small"
                    type="info"
                    :loading="elementMatching"
                    @click="handleElementMatch"
                  >
                    执行匹配
                  </n-button>
                </n-space>
                <n-space size="small">
                  <n-popconfirm @positive-click="handleDeleteElement">
                    <template #trigger>
                      <n-button size="small" type="error" secondary>删除</n-button>
                    </template>
                    确定删除元素「{{ selectedElement?.name }}」？
                  </n-popconfirm>
                  <n-button size="small" type="primary" :loading="saving" @click="saveElement">
                    保存修改
                  </n-button>
                </n-space>
              </n-space>

              <!-- OCR 识别结果提示（已改为弹窗展示） -->
            </div>
          </div>
        </div>
      </div>

      <!-- 新建元素对话框（场景固定为当前场景） -->
      <n-modal v-model:show="createModal.show" preset="card" title="新建元素" style="width: 560px">
        <n-form label-placement="left" label-width="90" size="small">
          <n-form-item label="元素名称">
            <n-input v-model:value="createModal.form.name" placeholder="元素名称" />
          </n-form-item>
          <n-form-item label="元素类型">
            <n-select v-model:value="createModal.form.element_type" :options="elementTypeOptions" @update:value="onCreateTypeChange" />
          </n-form-item>

          <!-- IMG 类型专属属性 -->
          <template v-if="createModal.form.element_type === 0">
            <n-form-item label="标志">
              <n-switch v-model:value="createModal.form.symbol" @update:value="onCreateSymbolChange" />
            </n-form-item>
            <n-form-item label="匹配方式">
              <n-select v-model:value="createModal.form.match_type" :options="matchTypeOptions" />
            </n-form-item>
            <n-form-item label="阈值">
              <n-input-number v-model:value="createModal.form.threshold" :min="0" :max="1" :step="0.01" style="width: 100%" />
            </n-form-item>
            <n-form-item label="Ratio">
              <n-space size="small">
                <n-input-number v-model:value="createModal.form.ratio_x" :step="0.01" style="width: 96px" />
                <n-input-number v-model:value="createModal.form.ratio_y" :step="0.01" style="width: 96px" />
              </n-space>
            </n-form-item>
            <n-form-item label="ROI">
              <div class="roi-grid">
                <n-input-number v-model:value="createModal.form.roi_x" placeholder="X" style="width: 100%" />
                <n-input-number v-model:value="createModal.form.roi_y" placeholder="Y" style="width: 100%" />
                <n-input-number v-model:value="createModal.form.roi_width" placeholder="宽" style="width: 100%" />
                <n-input-number v-model:value="createModal.form.roi_height" placeholder="高" style="width: 100%" />
              </div>
            </n-form-item>
          </template>

          <!-- COORDINATE 类型专属属性 -->
          <template v-else-if="createModal.form.element_type === 1">
            <n-form-item label="坐标">
              <n-space size="small">
                <n-input-number v-model:value="createModal.form.coordinate_x" style="width: 96px" />
                <n-input-number v-model:value="createModal.form.coordinate_y" style="width: 96px" />
              </n-space>
            </n-form-item>
          </template>

          <!-- OCR 类型专属属性 -->
          <template v-else-if="createModal.form.element_type === 2">
            <n-form-item label="ROI">
              <div class="roi-grid">
                <n-input-number v-model:value="createModal.form.roi_x" placeholder="X" style="width: 100%" />
                <n-input-number v-model:value="createModal.form.roi_y" placeholder="Y" style="width: 100%" />
                <n-input-number v-model:value="createModal.form.roi_width" placeholder="宽" style="width: 100%" />
                <n-input-number v-model:value="createModal.form.roi_height" placeholder="高" style="width: 100%" />
              </div>
            </n-form-item>
            <n-form-item label="OCR阈值">
              <n-input-number v-model:value="createModal.form.ocr_min_score" :min="0" :max="1" :step="0.05" style="width: 100%" />
            </n-form-item>
          </template>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="createModal.show = false">取消</n-button>
            <n-button type="primary" :loading="creating" @click="submitCreateElement">确定</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- Ratio 点选弹窗 -->
      <RatioDialog
        :show="ratioDialog.show"
        :element-id="ratioDialog.elementId"
        @update:show="ratioDialog.show = $event"
        @confirm="onRatioConfirm"
      />

      <!-- 元素匹配结果弹窗（手动关闭） -->
      <n-modal
        v-model:show="matchResultModal.show"
        preset="card"
        title="元素匹配结果"
        style="width: 480px"
        :mask-closable="false"
        :closable="false"
      >
        <div class="match-result" v-if="matchResultModal.data">
          <n-tag
            v-if="matchResultModal.data.matched"
            type="success"
            size="medium"
            round
            style="align-self: center"
          >
            匹配成功：{{ matchResultModal.data.count ?? 0 }} 处
          </n-tag>
          <n-tag
            v-else
            type="error"
            size="medium"
            round
            style="align-self: center"
          >
            匹配失败：{{ matchResultModal.data.error ?? '未找到' }}
          </n-tag>
          <div
            v-if="matchResultModal.data.positions?.length"
            class="match-result-list"
          >
            <div
              v-for="(pos, i) in matchResultModal.data.positions"
              :key="i"
              class="match-result-item"
            >
              <span class="match-result-name">位置 {{ i + 1 }}:</span>
              <span class="match-result-count">({{ pos[0] }}, {{ pos[1] }}, {{ pos[2] }}, {{ pos[3] }})</span>
            </div>
          </div>
        </div>
        <template #footer>
          <n-space justify="center">
            <n-button type="primary" @click="matchResultModal.show = false">关闭</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- OCR 识别结果弹窗（手动关闭） -->
      <n-modal
        v-model:show="ocrResultModal.show"
        preset="card"
        title="OCR 识别结果"
        style="width: 480px"
        :mask-closable="false"
        :closable="false"
      >
        <div class="match-result">
          <n-tag type="success" size="medium" round style="align-self: center">
            识别到 {{ ocrResultModal.results.length }} 条文本
          </n-tag>
          <div
            v-if="ocrResultModal.results.length > 0"
            class="match-result-list"
          >
            <div
              v-for="(r, i) in ocrResultModal.results"
              :key="i"
              class="match-result-item"
            >
              <n-tag size="small" type="primary">{{ i + 1 }}</n-tag>
              <span class="match-result-name">{{ r.text }}</span>
              <span class="match-result-count">({{ r.box[0] }}, {{ r.box[1] }})</span>
            </div>
          </div>
          <n-text v-else depth="3" style="text-align: center; font-size: 12px">
            未识别到文本
          </n-text>
        </div>
        <template #footer>
          <n-space justify="center">
            <n-button type="primary" @click="ocrResultModal.show = false">关闭</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- 隐藏的文件选择输入（IMG 元素图片） -->
      <input
        ref="fileInput"
        type="file"
        accept="image/png,image/jpeg"
        style="display: none"
        @change="onImageFileSelected"
      />
    </div>
  </n-message-provider>
</template>

<script setup lang="ts">
defineOptions({ name: 'ResourceSceneEditor' })
import { computed, h, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { resourceApi, type ResourceElement, type ElementPayload } from '../api/resource'
import RatioDialog from '../components/RatioDialog.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const sceneId = computed(() => String(route.params.sceneId ?? ''))
const scene = ref<{ id: string; name: string } | null>(null)
const elements = ref<ResourceElement[]>([])
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)

// ===== 场景属性 =====
const selectedSceneMode = ref(false)
const sceneNameForm = ref('')
const savingScene = ref(false)
const sceneMatching = ref(false)
const sceneMatchResult = ref<any>(null)

// ===== 元素匹配/OCR =====
const elementMatching = ref(false)
const elementMatchResult = ref<any>(null)
const ocrRunning = ref(false)
const ocrResults = ref<{ text: string; box: number[] }[]>([])
const ocrResultText = computed(() =>
  ocrResults.value.length > 0 ? `识别到 ${ocrResults.value.length} 条文本` : '',
)

// 匹配/OCR 结果弹窗（手动关闭，避免转瞬即逝）
const matchResultModal = reactive({
  show: false,
  data: null as any,
})
const ocrResultModal = reactive({
  show: false,
  results: [] as { text: string; box: number[] }[],
})

// ===== Ratio 弹窗 =====
const ratioDialog = reactive({ show: false, elementId: '' })

// ===== 图片文件选择 =====
const fileInput = ref<HTMLInputElement | null>(null)
const baseFileInput = ref<HTMLInputElement | null>(null)
const uploadingBase = ref(false)

const elementTypeOptions = [
  { label: '图像匹配 (IMG)', value: 0 },
  { label: '坐标 (COORDINATE)', value: 1 },
  { label: 'OCR 区域 (OCR_AREA)', value: 2 },
]
const matchTypeOptions = [
  { label: '模板匹配 (TEMPLATE)', value: 0 },
  { label: 'SIFT 特征匹配', value: 1 },
]

/** 元素类型角标信息（树节点角标与属性面板头部共用同一套配色） */
function getBadgeInfo(elementType: number, symbol?: boolean) {
  if (symbol) return { text: '★标志', bg: '#d03050' }
  if (elementType === 0) return { text: 'IMG', bg: '#2080f0' }
  if (elementType === 1) return { text: '坐标', bg: '#4a4a4a' }
  if (elementType === 2) return { text: 'OCR', bg: '#e8820c' }
  return { text: `类型${elementType}`, bg: '#888888' }
}
const badgeInfo = computed(() => {
  const e = selectedElement.value
  if (!e) return { text: '', bg: '' }
  return getBadgeInfo(e.element_type, e.symbol)
})

// ===== 数据加载 =====
async function loadScene() {
  try {
    const res = await resourceApi.listScenes()
    const list = res.data.scenes ?? []
    scene.value = list.find((s: any) => s.id === sceneId.value) ?? null
  } catch (e: any) {
    message.error(`加载场景失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

async function handleRefreshElements() {
  loading.value = true
  try {
    const res = await resourceApi.getSceneElements(sceneId.value)
    elements.value = res.data.elements ?? []
    // 底部状态提示
    message.success(`已加载 ${elements.value.length} 个元素`)
    await nextTick()
    render()
  } catch (e: any) {
    message.error(`加载元素失败: ${e?.response?.data?.detail ?? e.message}`)
  } finally {
    loading.value = false
  }
}
// ===== 底图 =====
const canvasWrap = ref<HTMLDivElement | null>(null)
const canvasEl = ref<HTMLCanvasElement | null>(null)
const baseImage = ref<HTMLImageElement | null>(null)
const baseSize = ref({ width: 1600, height: 900 })
const baseLoading = ref(false)
let baseObjectUrl = ''

const view = reactive({ scale: 1, tx: 0, ty: 0 })
const canvasSize = reactive({ width: 0, height: 0 })
// 底图 fit 变换：world(底图像素) -> canvas 坐标（未叠加 view）
const fit = reactive({ scale: 1, ox: 0, oy: 0 })
const pan = reactive({ active: false, lx: 0, ly: 0 })

async function loadBaseImage() {
  baseLoading.value = true
  try {
    if (baseObjectUrl) URL.revokeObjectURL(baseObjectUrl)
    const res = await resourceApi.getSceneBaseImage(sceneId.value)
    const url = URL.createObjectURL(res.data)
    baseObjectUrl = url
    const img = new Image()
    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve()
      img.onerror = () => reject(new Error('底图加载失败'))
      img.src = url
    })
    baseImage.value = img
    baseSize.value = { width: img.naturalWidth || 1600, height: img.naturalHeight || 900 }
    view.scale = 1
    if (fit.scale === 0) computeFit()
    await nextTick()
    render()
  } catch (e: any) {
    baseImage.value = null
    message.warning(`底图不可用: ${e?.response?.data?.detail ?? e.message}`)
  } finally {
    baseLoading.value = false
  }
}

function refreshBaseImage() {
  loadBaseImage()
}

// ===== 底图上传（拖入 / 选择本地 PNG）=====
function triggerBaseImageFile() {
  baseFileInput.value?.click()
}

async function onBaseImageFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  await uploadSceneBase(file)
}

function onBaseImageDragOver(e: DragEvent) {
  if (e.dataTransfer?.types.includes('Files')) {
    e.dataTransfer.dropEffect = 'copy'
  }
}

async function onBaseImageDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  await uploadSceneBase(file)
}

async function uploadSceneBase(file: File) {
  if (!/\.png$/i.test(file.name) && file.type !== 'image/png') {
    message.warning('仅支持 PNG 图片作为底图')
    return
  }
  uploadingBase.value = true
  try {
    await resourceApi.uploadSceneBaseImage(sceneId.value, file)
    message.success('底图已更新，正在刷新…')
    await loadBaseImage()
  } catch (err: any) {
    message.error(`底图上传失败: ${err?.response?.data?.detail ?? err.message}`)
  } finally {
    uploadingBase.value = false
  }
}

function computeFit() {
  const cw = canvasSize.width
  const ch = canvasSize.height
  if (!cw || !ch) return
  fit.scale = Math.min(cw / baseSize.value.width, ch / baseSize.value.height)
  fit.ox = (cw - baseSize.value.width * fit.scale) / 2
  fit.oy = (ch - baseSize.value.height * fit.scale) / 2
}

// world(底图像素坐标) -> 画布坐标
function worldToCanvas(x: number, y: number) {
  return {
    x: (x * fit.scale + fit.ox) * view.scale + view.tx,
    y: (y * fit.scale + fit.oy) * view.scale + view.ty,
  }
}

// ===== 元素选择 =====
const selectedElementId = ref<string | null>(null)
const selectedElement = computed<ResourceElement | null>(() => {
  if (!selectedElementId.value) return null
  return elements.value.find((e) => e.id === selectedElementId.value) ?? null
})
const selectedKeys = computed(() => {
  if (selectedElementId.value) return [selectedElementId.value]
  if (selectedSceneMode.value) return [sceneId.value]
  return []
})

const treeData = computed(() => [
  {
    key: sceneId.value,
    label: `场景：${scene.value?.name ?? sceneId.value}`,
    children: elements.value.map((e) => ({
      key: e.id,
      name: e.name,
      elementType: e.element_type,
      symbol: e.symbol,
      label: e.name,
    })),
  },
])
const treeExpandedKeys = computed(() => [sceneId.value])

// 树节点标签渲染：元素名 + 右上角类型角标（树节点与属性面板共用 getBadgeInfo 配色）
// 标志元素红色（优先级最高）、IMG 蓝色、COORDINATE 深灰、OCR 深橙
function renderTreeLabel({ option }: { option: any }) {
  const e = option
  if (!e || e.elementType === undefined) {
    return h('span', { class: 'tree-label' }, option.label)
  }
  const info = getBadgeInfo(e.elementType, e.symbol)
  return h('span', { class: 'tree-label' }, [
    h('span', { class: 'tree-label-name' }, option.label),
    h('span', { class: 'tree-label-badge', style: { background: info.bg } }, info.text),
  ])
}

function onTreeSelect(keys: (string | number)[]) {
  const key = String(keys[0] ?? '')
  // 取消当前选择模式（若正在框选/点选）
  cancelSelectionMode()
  if (!key) {
    selectedElementId.value = null
    selectedSceneMode.value = false
  } else if (key === sceneId.value) {
    // 选中场景根节点 → 显示场景属性面板，清空元素选中与标注
    selectedElementId.value = null
    selectedSceneMode.value = true
    sceneNameForm.value = scene.value?.name ?? ''
  } else {
    // 选中元素节点 → 加载该元素标注并渲染
    selectedElementId.value = key
    selectedSceneMode.value = false
    syncPropForm()
  }
  render()
}

// ===== 场景属性操作 =====
async function saveSceneName() {
  const newName = sceneNameForm.value.trim()
  if (!newName) {
    message.warning('场景名称不能为空')
    return
  }
  if (newName === scene.value?.name) return
  savingScene.value = true
  try {
    await resourceApi.renameScene(sceneId.value, newName)
    message.success('场景已重命名')
    if (scene.value) scene.value.name = newName
  } catch (err: any) {
    message.error(`重命名失败: ${err?.response?.data?.detail ?? err.message}`)
  } finally {
    savingScene.value = false
  }
}

async function handleSceneMatch() {
  sceneMatching.value = true
  sceneMatchResult.value = null
  try {
    const res = await resourceApi.matchScene(sceneId.value)
    sceneMatchResult.value = res.data
  } catch (err: any) {
    message.error(`场景识别失败: ${err?.response?.data?.detail ?? err.message}`)
    sceneMatchResult.value = { ok: false, error: err?.response?.data?.detail ?? err.message }
  } finally {
    sceneMatching.value = false
  }
}

/** 属性面板中标志开关变化：勾选后名字自动改为"标志" */
function onSymbolChange(value: boolean) {
  if (value) {
    propForm.name = '标志'
  }
}

/** 新建元素类型切换：重置为对应类型的默认值 */
function onCreateTypeChange(type: number) {
  const f = createModal.form
  f.symbol = false
  f.match_type = 0
  f.threshold = 0.8
  f.ratio_x = 0.5
  f.ratio_y = 0.5
  f.ocr_min_score = 0.6
  f.coordinate_x = 0
  f.coordinate_y = 0
  if (type === 0) {
    // IMG 默认全屏 ROI
    f.roi_x = 0
    f.roi_y = 0
    f.roi_width = baseSize.value.width
    f.roi_height = baseSize.value.height
  } else if (type === 2) {
    // OCR 默认 ROI 也全屏（可由后续框选调整）
    f.roi_x = 0
    f.roi_y = 0
    f.roi_width = baseSize.value.width
    f.roi_height = baseSize.value.height
  }
}

/** 新建元素标志开关：勾选后名字自动改为"标志" */
function onCreateSymbolChange(value: boolean) {
  if (value) {
    createModal.form.name = '标志'
  }
}

// ===== Canvas 选择模式（ROI 框选 / 坐标点选） =====
const selectionMode = ref<'roi' | 'coordinate' | null>(null)
const roiStart = ref<{ x: number; y: number } | null>(null)
const roiRect = ref<{ x: number; y: number; w: number; h: number } | null>(null)

function cancelSelectionMode() {
  selectionMode.value = null
  roiStart.value = null
  roiRect.value = null
}

function enterRoiMode() {
  const e = selectedElement.value
  if (!e) return
  if (e.element_type !== 0 && e.element_type !== 2) {
    message.warning('仅 IMG / OCR 元素支持 ROI 框选')
    return
  }
  selectionMode.value = 'roi'
  roiStart.value = null
  roiRect.value = null
  render()
}

function enterCoordMode() {
  const e = selectedElement.value
  if (!e) return
  if (e.element_type !== 1) {
    message.warning('仅 COORDINATE 元素支持坐标点选')
    return
  }
  selectionMode.value = 'coordinate'
  render()
}

const hasRoi = computed(
  () => propForm.roi_width > 0 && propForm.roi_height > 0,
)
const roiLabel = computed(
  () => `[${propForm.roi_x}, ${propForm.roi_y}, ${propForm.roi_width}, ${propForm.roi_height}]`,
)

// ===== Ratio 弹窗 =====
function openRatioDialog() {
  const e = selectedElement.value
  if (!e) return
  ratioDialog.elementId = e.id
  ratioDialog.show = true
}

function onRatioConfirm(ratio: { x: number; y: number }) {
  const e = selectedElement.value
  if (!e) return
  propForm.ratio_x = ratio.x
  propForm.ratio_y = ratio.y
  // 立即保存
  saveElement()
}

// ===== 元素图片查看/选择 =====
async function previewElementImage() {
  const e = selectedElement.value
  if (!e) return
  try {
    const res = await resourceApi.getElementImage(e.id)
    const url = URL.createObjectURL(res.data)
    window.open(url, '_blank')
    setTimeout(() => URL.revokeObjectURL(url), 60000)
  } catch (err: any) {
    message.error(`加载图片失败: ${err?.response?.data?.detail ?? err.message}`)
  }
}

function triggerImageFile() {
  fileInput.value?.click()
}

async function onImageFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  const e = selectedElement.value
  if (!file || !e) return
  if (e.element_type !== 0) {
    message.warning('仅 IMG 元素可设置图片')
    return
  }
  try {
    await resourceApi.uploadElementImage(e.id, file)
    message.success('元素图片已更新')
  } catch (err: any) {
    message.error(`图片上传失败: ${err?.response?.data?.detail ?? err.message}`)
  }
}

// ===== 元素匹配 / OCR 识别 =====
async function handleElementMatch() {
  const e = selectedElement.value
  if (!e) return
  elementMatching.value = true
  elementMatchResult.value = null
  try {
    const res = await resourceApi.matchElement(e.id)
    elementMatchResult.value = res.data
    // 弹窗展示结果（手动关闭）
    matchResultModal.data = res.data
    matchResultModal.show = true
  } catch (err: any) {
    message.error(`匹配失败: ${err?.response?.data?.detail ?? err.message}`)
    matchResultModal.data = { matched: false, error: err?.response?.data?.detail ?? err.message }
    matchResultModal.show = true
  } finally {
    elementMatching.value = false
  }
}

async function handleElementOcr() {
  const e = selectedElement.value
  if (!e) return
  ocrRunning.value = true
  ocrResults.value = []
  try {
    const res = await resourceApi.ocrElement(e.id)
    ocrResults.value = res.data.results ?? []
    ocrResultModal.results = ocrResults.value
    ocrResultModal.show = true
  } catch (err: any) {
    message.error(`OCR 识别失败: ${err?.response?.data?.detail ?? err.message}`)
    ocrResultModal.results = []
    ocrResultModal.show = true
  } finally {
    ocrRunning.value = false
  }
}

// ===== 属性表单 =====
const emptyPropForm = () => ({
  name: '',
  symbol: false,
  element_type: 0,
  match_type: 0,
  threshold: 0.8,
  ratio_x: 0.5,
  ratio_y: 0.5,
  roi_x: 0,
  roi_y: 0,
  roi_width: 1600,
  roi_height: 900,
  ocr_min_score: 0.6,
  coordinate_x: 0,
  coordinate_y: 0,
})
const propForm = reactive(emptyPropForm())

function syncPropForm() {
  const e = selectedElement.value
  if (!e) return
  propForm.name = e.name
  propForm.symbol = e.symbol
  propForm.element_type = e.element_type
  propForm.match_type = e.match_type
  propForm.threshold = e.threshold
  propForm.ratio_x = e.ratio_x
  propForm.ratio_y = e.ratio_y
  propForm.roi_x = e.roi_x
  propForm.roi_y = e.roi_y
  propForm.roi_width = e.roi_width
  propForm.roi_height = e.roi_height
  propForm.ocr_min_score = e.ocr_min_score
  propForm.coordinate_x = e.coordinate_x
  propForm.coordinate_y = e.coordinate_y
}

function buildPayload(): ElementPayload {
  return {
    name: propForm.name.trim() || undefined,
    symbol: propForm.symbol,
    element_type: propForm.element_type,
    match_type: propForm.match_type,
    threshold: propForm.threshold,
    ratio_x: propForm.ratio_x,
    ratio_y: propForm.ratio_y,
    roi_x: propForm.roi_x,
    roi_y: propForm.roi_y,
    roi_width: propForm.roi_width,
    roi_height: propForm.roi_height,
    ocr_min_score: propForm.ocr_min_score,
    coordinate_x: propForm.coordinate_x,
    coordinate_y: propForm.coordinate_y,
  }
}

async function saveElement() {
  const e = selectedElement.value
  if (!e) return
  if (!propForm.name.trim()) {
    message.warning('元素名称不能为空')
    return
  }
  saving.value = true
  try {
    await resourceApi.updateElement(e.id, buildPayload())
    message.success('元素已保存')
    await handleRefreshElements()
    // 保持选中
    selectedElementId.value = e.id
  } catch (err: any) {
    message.error(`保存失败: ${err?.response?.data?.detail ?? err.message}`)
  } finally {
    saving.value = false
  }
}

async function handleDeleteElement() {
  const e = selectedElement.value
  if (!e) return
  try {
    await resourceApi.deleteElement(e.id)
    message.success('元素已删除')
    selectedElementId.value = null
    selectedSceneMode.value = false
    cancelSelectionMode()
    await handleRefreshElements()
  } catch (err: any) {
    message.error(`删除失败: ${err?.response?.data?.detail ?? err.message}`)
  }
}

// ===== 新建元素 =====
const createModal = reactive({
  show: false,
  form: emptyPropForm(),
})

function openCreateElement() {
  createModal.form = emptyPropForm()
  createModal.form.name = ''
  createModal.show = true
}

async function submitCreateElement() {
  const f = createModal.form
  if (!f.name.trim()) {
    message.warning('元素名称不能为空')
    return
  }
  creating.value = true
  try {
    await resourceApi.createElement(sceneId.value, f.name.trim(), {
      symbol: f.symbol,
      element_type: f.element_type,
      match_type: f.match_type,
      threshold: f.threshold,
      ratio_x: f.ratio_x,
      ratio_y: f.ratio_y,
      roi_x: f.roi_x,
      roi_y: f.roi_y,
      roi_width: f.roi_width,
      roi_height: f.roi_height,
      ocr_min_score: f.ocr_min_score,
      coordinate_x: f.coordinate_x,
      coordinate_y: f.coordinate_y,
    })
    message.success('元素已创建')
    createModal.show = false
    await handleRefreshElements()
  } catch (err: any) {
    message.error(`创建失败: ${err?.response?.data?.detail ?? err.message}`)
  } finally {
    creating.value = false
  }
}

// ===== Canvas 绘制 =====
function getCtx() {
  return canvasEl.value?.getContext('2d') ?? null
}

function resizeCanvas() {
  const wrap = canvasWrap.value
  if (!wrap || !canvasEl.value) return
  const dpr = window.devicePixelRatio || 1
  canvasEl.value.width = Math.round(wrap.clientWidth * dpr)
  canvasEl.value.height = Math.round(wrap.clientHeight * dpr)
  canvasEl.value.style.width = wrap.clientWidth + 'px'
  canvasEl.value.style.height = wrap.clientHeight + 'px'
  canvasSize.width = wrap.clientWidth
  canvasSize.height = wrap.clientHeight
  const ctx = getCtx()
  if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  computeFit()
  render()
}

function render() {
  const ctx = getCtx()
  if (!ctx) return
  const cw = canvasSize.width
  const ch = canvasSize.height
  ctx.clearRect(0, 0, cw, ch)

  // 背景
  ctx.fillStyle = '#f0f2f5'
  ctx.fillRect(0, 0, cw, ch)

  // 底图
  if (baseImage.value) {
    const x = fit.ox * view.scale + view.tx
    const y = fit.oy * view.scale + view.ty
    const w = baseSize.value.width * fit.scale * view.scale
    const h = baseSize.value.height * fit.scale * view.scale
    ctx.drawImage(baseImage.value, x, y, w, h)
  } else {
    // 白色占位图区域
    const x = fit.ox * view.scale + view.tx
    const y = fit.oy * view.scale + view.ty
    const w = 1600 * fit.scale * view.scale
    const h = 900 * fit.scale * view.scale
    ctx.fillStyle = '#fff'
    ctx.fillRect(x, y, w, h)
    ctx.strokeStyle = '#ccc'
    ctx.strokeRect(x, y, w, h)
  }

  // 元素标注（需求：仅在选中时绘制该元素，取消选中/切换时自动清除）
  if (selectedElement.value) {
    drawElement(ctx, selectedElement.value, true)
  }

  // ROI 框选中的实时预览矩形
  if (selectionMode.value === 'roi' && roiStart.value && roiRect.value) {
    const r = roiRect.value
    const p1 = worldToCanvas(r.x, r.y)
    const p2 = worldToCanvas(r.x + r.w, r.y + r.h)
    ctx.strokeStyle = '#ff4d4f'
    ctx.lineWidth = 2
    ctx.setLineDash([6, 4])
    ctx.strokeRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y)
    ctx.setLineDash([])
    ctx.fillStyle = 'rgba(255, 77, 79, 0.08)'
    ctx.fillRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y)
  }
}

function drawElement(ctx: CanvasRenderingContext2D, e: ResourceElement, high: boolean) {
  const lw = high ? 3 : 1.5
  const colorHigh = '#ff4d4f'
  // 标志元素红色（优先级最高）、普通 IMG 蓝色、COORDINATE 黑色
  const colorImg = e.symbol ? '#d03050' : '#2080f0'
  const colorCoord = '#333'

  if (e.element_type === 0) {
    // IMG：ROI 矩形区域
    const p1 = worldToCanvas(e.roi_x, e.roi_y)
    const p2 = worldToCanvas(e.roi_x + e.roi_width, e.roi_y + e.roi_height)
    const w = p2.x - p1.x
    const h = p2.y - p1.y
    ctx.strokeStyle = high ? colorHigh : colorImg
    ctx.lineWidth = lw
    ctx.strokeRect(p1.x, p1.y, w, h)
    // 半透明填充
    ctx.fillStyle = high ? 'rgba(255,77,79,0.08)' : 'rgba(82,196,26,0.05)'
    ctx.fillRect(p1.x, p1.y, w, h)
    // 类型标记
    ctx.fillStyle = high ? colorHigh : colorImg
    ctx.font = '11px SimHei, sans-serif'
    ctx.textAlign = 'left'
    ctx.textBaseline = 'top'
    ctx.fillText(`IMG${e.symbol ? '·点击' : ''} ${e.name}`, p1.x, p1.y - 14)
    // 附着点（定位点）
    const ap = worldToCanvas(e.roi_x + e.roi_width * e.ratio_x, e.roi_y + e.roi_height * e.ratio_y)
    ctx.beginPath()
    ctx.arc(ap.x, ap.y, high ? 5 : 3.5, 0, Math.PI * 2)
    ctx.fillStyle = high ? colorHigh : colorImg
    ctx.fill()
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 1
    ctx.stroke()
  } else if (e.element_type === 1) {
    // COORDINATE：坐标十字标记
    const p = worldToCanvas(e.coordinate_x, e.coordinate_y)
    const r = high ? 7 : 5
    ctx.strokeStyle = high ? colorHigh : colorCoord
    ctx.lineWidth = lw
    ctx.beginPath()
    ctx.moveTo(p.x - r, p.y)
    ctx.lineTo(p.x + r, p.y)
    ctx.moveTo(p.x, p.y - r)
    ctx.lineTo(p.x, p.y + r)
    ctx.stroke()
    ctx.beginPath()
    ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2)
    ctx.fillStyle = high ? colorHigh : colorCoord
    ctx.fill()
    ctx.fillStyle = high ? colorHigh : colorCoord
    ctx.font = '11px SimHei, sans-serif'
    ctx.textAlign = 'left'
    ctx.textBaseline = 'bottom'
    ctx.fillText(`坐标 ${e.name}`, p.x + r + 2, p.y - r - 2)
  } else if (e.element_type === 2) {
    // OCR_AREA：ROI 矩形区域（与 IMG 一致）
    const p1 = worldToCanvas(e.roi_x, e.roi_y)
    const p2 = worldToCanvas(e.roi_x + e.roi_width, e.roi_y + e.roi_height)
    const w = p2.x - p1.x
    const h = p2.y - p1.y
    ctx.strokeStyle = high ? colorHigh : '#fa8c16'
    ctx.lineWidth = lw
    ctx.strokeRect(p1.x, p1.y, w, h)
    ctx.fillStyle = high ? 'rgba(255,77,79,0.08)' : 'rgba(250,140,22,0.06)'
    ctx.fillRect(p1.x, p1.y, w, h)
    ctx.fillStyle = high ? colorHigh : '#fa8c16'
    ctx.font = '11px SimHei, sans-serif'
    ctx.textAlign = 'left'
    ctx.textBaseline = 'top'
    ctx.fillText(`OCR ${e.name}`, p1.x, p1.y - 14)
  }
}

// ===== Canvas 交互 =====
function screenToWorld(sx: number, sy: number) {
  return { x: (sx - view.tx) / view.scale, y: (sy - view.ty) / view.scale }
}

/** 屏幕坐标 → 底图像素坐标（用于 ROI/坐标选择） */
function screenToImage(sx: number, sy: number) {
  const p = screenToWorld(sx, sy)
  return {
    x: (p.x - fit.ox) / fit.scale,
    y: (p.y - fit.oy) / fit.scale,
  }
}

function onMouseDown(e: MouseEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  const sx = e.clientX - rect.left
  const sy = e.clientY - rect.top

  // ROI 框选模式
  if (selectionMode.value === 'roi') {
    const img = screenToImage(sx, sy)
    roiStart.value = img
    roiRect.value = { x: img.x, y: img.y, w: 0, h: 0 }
    render()
    return
  }

  // 坐标点选模式
  if (selectionMode.value === 'coordinate') {
    const img = screenToImage(sx, sy)
    if (baseImage.value) {
      propForm.coordinate_x = Math.round(img.x)
      propForm.coordinate_y = Math.round(img.y)
    }
    cancelSelectionMode()
    saveElement()
    render()
    return
  }

  // 正常模式：直接拖拽平移（不再通过点击底图选中元素，只能通过右侧树选择）
  pan.active = true
  pan.lx = e.clientX
  pan.ly = e.clientY
}

function onMouseMove(e: MouseEvent) {
  // ROI 框选过程中实时更新矩形
  if (selectionMode.value === 'roi' && roiStart.value) {
    const rect = canvasEl.value!.getBoundingClientRect()
    const img = screenToImage(e.clientX - rect.left, e.clientY - rect.top)
    roiRect.value = {
      x: Math.min(roiStart.value.x, img.x),
      y: Math.min(roiStart.value.y, img.y),
      w: Math.abs(img.x - roiStart.value.x),
      h: Math.abs(img.y - roiStart.value.y),
    }
    render()
    return
  }
  if (!pan.active) return
  view.tx += e.clientX - pan.lx
  view.ty += e.clientY - pan.ly
  pan.lx = e.clientX
  pan.ly = e.clientY
  render()
}

function onMouseUp(e: MouseEvent) {
  // ROI 框选完成
  if (selectionMode.value === 'roi' && roiStart.value && roiRect.value) {
    const r = roiRect.value
    // 限制 ROI 在底图范围内
    if (baseImage.value) {
      r.x = Math.max(0, Math.min(r.x, baseSize.value.width))
      r.y = Math.max(0, Math.min(r.y, baseSize.value.height))
      r.w = Math.max(0, Math.min(r.w, baseSize.value.width - r.x))
      r.h = Math.max(0, Math.min(r.h, baseSize.value.height - r.y))
    }
    propForm.roi_x = Math.round(r.x)
    propForm.roi_y = Math.round(r.y)
    propForm.roi_width = Math.round(r.w)
    propForm.roi_height = Math.round(r.h)
    cancelSelectionMode()
    saveElement()
    render()
    return
  }
  pan.active = false
}

function onWheel(e: WheelEvent) {
  const rect = canvasEl.value!.getBoundingClientRect()
  const sx = e.clientX - rect.left
  const sy = e.clientY - rect.top
  const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15
  const newScale = Math.min(8, Math.max(0.1, view.scale * factor))
  view.tx = sx - ((sx - view.tx) / view.scale) * newScale
  view.ty = sy - ((sy - view.ty) / view.scale) * newScale
  view.scale = newScale
  render()
}

function goBack() {
  router.push({ name: 'ResourceGraph' })
}

// ===== 生命周期 =====
let resizeObserver: ResizeObserver | null = null
onMounted(async () => {
  await Promise.all([loadScene(), loadBaseImage()])
  await handleRefreshElements()
  await nextTick()
  resizeCanvas()
  resizeObserver = new ResizeObserver(() => resizeCanvas())
  if (canvasWrap.value) resizeObserver.observe(canvasWrap.value)
  window.addEventListener('resize', resizeCanvas)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  window.removeEventListener('resize', resizeCanvas)
  if (baseObjectUrl) URL.revokeObjectURL(baseObjectUrl)
})
</script>

<style scoped>
.scene-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f7f9fc;
}
.se-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-bottom: 1px solid #e8e8e8;
  background: #fff;
  flex-shrink: 0;
}
.se-title {
  font-size: 15px;
}
.se-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.se-canvas-wrap {
  flex: 3;
  position: relative;
  overflow: hidden;
  background: #f0f2f5;
}
.se-canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: grab;
}
.se-canvas:active {
  cursor: grabbing;
}
.se-hint {
  position: absolute;
  left: 12px;
  bottom: 10px;
  font-size: 12px;
  color: #999;
  background: rgba(255, 255, 255, 0.85);
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid #eee;
  pointer-events: none;
  user-select: none;
}
.se-right {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #e8e8e8;
  background: #fff;
}
.se-tree {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
  border-bottom: 1px solid #eee;
}
.se-props {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
}
.se-panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.se-prop-form {
  display: flex;
  flex-direction: column;
}
.roi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  width: 100%;
}
.roi-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
}
.se-prop-actions {
  margin-top: 4px;
}
.match-result {
  margin-top: 10px;
  padding: 8px 10px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.match-result-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 180px;
  overflow-y: auto;
}
.match-result-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.match-result-name {
  font-weight: 600;
  color: #333;
}
.match-result-count {
  color: #888;
}
.match-result-error {
  color: #e53935;
  font-size: 11px;
}
.tree-label {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding-right: 44px; /* 为右上角角标预留空间 */
}
.tree-label-name {
  font-size: 13px;
}
/* 树节点右上角类型角标 + 属性面板头部类型角标（同一套样式） */
.elem-type-badge,
.tree-label-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 15px;
  padding: 0 5px;
  border-radius: 8px;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.5px;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
  user-select: none;
}
.tree-label-badge {
  position: absolute;
  top: -4px;
  right: 0;
}
</style>