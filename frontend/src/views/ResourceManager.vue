<template>
  <n-message-provider>
    <n-space vertical size="large" style="height: 100%">
      <!-- 顶部工具栏 -->
      <n-card :bordered="false">
        <n-space justify="space-between" align="center">
          <n-space align="center" size="small">
            <n-h3 style="margin: 0">场景资源管理</n-h3>
            <n-tag :type="loading ? 'warning' : 'success'" size="small">
              {{ loading ? '加载中…' : `已加载 ${scenes.length} 个场景 / ${totalElements} 个元素` }}
            </n-tag>
          </n-space>
          <n-space>
            <n-button @click="refreshAll" :loading="loading">批量刷新</n-button>
            <n-button type="primary" @click="openCreateScene">新增场景</n-button>
          </n-space>
        </n-space>
      </n-card>

      <!-- 主体：左场景列表 + 右元素表格 -->
      <n-layout has-sider sider-placement="left" style="flex: 1">
        <n-layout-sider bordered width="260" :native-scrollbar="false">
          <n-space vertical size="small" style="padding: 8px">
            <n-input v-model:value="sceneFilter" placeholder="搜索场景" clearable />
            <n-list hoverable clickable style="flex: 1; overflow-y: auto">
              <n-list-item
                v-for="scene in filteredScenes"
                :key="scene.id"
                @click="selectScene(scene.id)"
                :class="{ 'scene-active': scene.id === selectedSceneId }"
              >
                <n-space justify="space-between" align="center">
                  <span>{{ scene.name }}</span>
                  <n-tag size="small" round>{{ scene.elements?.length ?? 0 }}</n-tag>
                </n-space>
              </n-list-item>
              <n-empty
                v-if="filteredScenes.length === 0"
                description="暂无场景"
                style="padding: 24px 0"
              />
            </n-list>
          </n-space>
        </n-layout-sider>

        <n-layout-content :native-scrollbar="false" style="padding: 16px">
          <!-- 未选中场景 -->
          <n-empty v-if="!selectedScene" description="请选择左侧场景，或新建场景" style="margin-top: 80px" />

          <!-- 选中场景：元素管理 -->
          <n-space v-else vertical size="large">
            <!-- 场景信息与操作 -->
            <div>
              <n-space align="center" justify="space-between">
                <n-h3 style="margin: 0">
                  {{ selectedScene.name }}
                  <n-tag size="small" round style="margin-left: 8px">
                    {{ selectedScene.elements?.length ?? 0 }} 个元素
                  </n-tag>
                </n-h3>
                <n-space>
                  <n-button size="small" @click="openRenameScene(selectedScene)">
                    重命名场景
                  </n-button>
                  <n-popconfirm @positive-click="handleDeleteScene(selectedScene.id)">
                    <template #trigger>
                      <n-button size="small" type="error" secondary>删除场景</n-button>
                    </template>
                    删除场景将同时删除其全部元素与跳转边，确定？
                  </n-popconfirm>
                </n-space>
              </n-space>
            </div>

            <!-- 元素表格 -->
            <n-card :bordered="true" size="small">
              <template #header>
                <n-space justify="space-between" align="center">
                  <span>元素列表</span>
                  <n-button size="small" type="primary" @click="openCreateElement">
                    新增元素
                  </n-button>
                </n-space>
              </template>
              <n-data-table
                :columns="columns"
                :data="selectedScene.elements ?? []"
                :loading="loading"
                :row-key="(row: ResourceElement) => row.id"
                :pagination="{ pageSize: 10 }"
                size="small"
              />
            </n-card>
          </n-space>
        </n-layout-content>
      </n-layout>

      <!-- 场景跳转边管理 -->
      <n-collapse>
        <n-collapse-item title="场景跳转边管理" name="edges">
          <n-space vertical size="small">
            <n-space>
              <n-select
                v-model:value="newEdgeSource"
                :options="sceneOptions"
                placeholder="源场景"
                style="width: 200px"
                clearable
              />
              <span>→</span>
              <n-select
                v-model:value="newEdgeTarget"
                :options="sceneOptions"
                placeholder="目标场景"
                style="width: 200px"
                clearable
              />
              <n-button type="primary" size="small" @click="handleCreateEdge">
                添加跳转
              </n-button>
            </n-space>
            <n-data-table
              :columns="edgeColumns"
              :data="edges"
              size="small"
              :row-key="(row: ResourceEdge) => row.id"
            />
          </n-space>
        </n-collapse-item>
      </n-collapse>
    </n-space>

    <!-- ===== 场景对话框 ===== -->
    <n-modal v-model:show="sceneModal.show" preset="card" :title="sceneModal.title" style="width: 420px">
      <n-form label-placement="left" label-width="80">
        <n-form-item label="场景名称">
          <n-input v-model:value="sceneModal.name" placeholder="请输入场景名称" @keyup.enter="submitScene" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="sceneModal.show = false">取消</n-button>
          <n-button type="primary" @click="submitScene">确定</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- ===== 元素对话框 ===== -->
    <n-modal v-model:show="elementModal.show" preset="card" :title="elementModal.title" style="width: 560px">
      <n-form label-placement="left" label-width="100" size="small">
        <n-form-item label="元素名称">
          <n-input v-model:value="elementModal.form.name" placeholder="元素名称" />
        </n-form-item>
        <n-form-item label="所属场景">
          <n-select
            v-model:value="elementModal.form.scene_id"
            :options="sceneOptions"
            placeholder="选择场景"
            :disabled="elementModal.isEdit"
          />
        </n-form-item>
        <n-form-item label="元素类型">
          <n-select
            v-model:value="elementModal.form.element_type"
            :options="elementTypeOptions"
          />
        </n-form-item>
        <n-form-item label="匹配方式">
          <n-select
            v-model:value="elementModal.form.match_type"
            :options="matchTypeOptions"
          />
        </n-form-item>
        <n-form-item label="阈值">
          <n-input-number v-model:value="elementModal.form.threshold" :min="0" :max="1" :step="0.05" style="width: 100%" />
        </n-form-item>
        <n-form-item label="比例 X">
          <n-input-number v-model:value="elementModal.form.ratio_x" :min="0" :max="1" :step="0.01" style="width: 100%" />
        </n-form-item>
        <n-form-item label="比例 Y">
          <n-input-number v-model:value="elementModal.form.ratio_y" :min="0" :max="1" :step="0.01" style="width: 100%" />
        </n-form-item>
        <n-form-item label="ROI X">
          <n-input-number v-model:value="elementModal.form.roi_x" style="width: 100%" />
        </n-form-item>
        <n-form-item label="ROI Y">
          <n-input-number v-model:value="elementModal.form.roi_y" style="width: 100%" />
        </n-form-item>
        <n-form-item label="ROI 宽">
          <n-input-number v-model:value="elementModal.form.roi_width" style="width: 100%" />
        </n-form-item>
        <n-form-item label="ROI 高">
          <n-input-number v-model:value="elementModal.form.roi_height" style="width: 100%" />
        </n-form-item>
        <n-form-item label="OCR 阈值">
          <n-input-number v-model:value="elementModal.form.ocr_min_score" :min="0" :max="1" :step="0.05" style="width: 100%" />
        </n-form-item>
        <n-form-item label="坐标 X">
          <n-input-number v-model:value="elementModal.form.coordinate_x" style="width: 100%" />
        </n-form-item>
        <n-form-item label="坐标 Y">
          <n-input-number v-model:value="elementModal.form.coordinate_y" style="width: 100%" />
        </n-form-item>
        <n-form-item label="点击坐标">
          <n-switch v-model:value="elementModal.form.symbol" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="elementModal.show = false">取消</n-button>
          <n-button type="primary" @click="submitElement">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </n-message-provider>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { NButton, NPopconfirm, NSpace, useMessage, type DataTableColumns } from 'naive-ui'
import { resourceApi, type ResourceScene, type ResourceElement, type ResourceEdge, type ElementPayload } from '../api/resource'

const message = useMessage()
const loading = ref(false)
const scenes = ref<ResourceScene[]>([])
const edges = ref<ResourceEdge[]>([])
const selectedSceneId = ref<string | null>(null)
const sceneFilter = ref('')

const elementTypeOptions = [
  { label: '图像匹配 (IMG)', value: 0 },
  { label: '坐标 (COORDINATE)', value: 1 },
  { label: 'OCR 区域 (OCR_AREA)', value: 2 },
]

const matchTypeOptions = [
  { label: '模板匹配 (TEMPLATE)', value: 0 },
  { label: 'SIFT 特征匹配', value: 1 },
]

// ===== 计算属性 =====
const selectedScene = computed<ResourceScene | null>(() => {
  if (!selectedSceneId.value) return null
  return scenes.value.find((s) => s.id === selectedSceneId.value) ?? null
})

const filteredScenes = computed(() => {
  const kw = sceneFilter.value.trim().toLowerCase()
  if (!kw) return scenes.value
  return scenes.value.filter((s) => s.name.toLowerCase().includes(kw))
})

const sceneOptions = computed(() =>
  scenes.value.map((s) => ({ label: s.name, value: s.id })),
)

const totalElements = computed(() =>
  scenes.value.reduce((sum, s) => sum + (s.elements?.length ?? 0), 0),
)

const sceneNameById = (id: string | null | undefined) => {
  const scene = scenes.value.find((s) => s.id === id)
  return scene ? scene.name : id ?? '-'
}

// ===== 全量批量加载（前端初始化一次读取） =====
async function refreshAll() {
  loading.value = true
  try {
    const [fullRes, edgeRes] = await Promise.all([
      resourceApi.getFull(),
      resourceApi.listEdges(),
    ])
    scenes.value = fullRes.data.scenes ?? []
    edges.value = edgeRes.data.edges ?? []
    if (
      selectedSceneId.value &&
      !scenes.value.some((s) => s.id === selectedSceneId.value)
    ) {
      selectedSceneId.value = scenes.value[0]?.id ?? null
    } else if (!selectedSceneId.value && scenes.value.length > 0) {
      selectedSceneId.value = scenes.value[0].id
    }
  } catch (e: any) {
    message.error(`加载失败: ${e?.response?.data?.detail ?? e.message}`)
  } finally {
    loading.value = false
  }
}

function selectScene(id: string) {
  selectedSceneId.value = id
}

// ===== 场景 CRUD =====
const sceneModal = reactive({
  show: false,
  title: '新增场景',
  mode: 'create' as 'create' | 'rename',
  id: '',
  name: '',
})

function openCreateScene() {
  sceneModal.show = true
  sceneModal.mode = 'create'
  sceneModal.title = '新增场景'
  sceneModal.id = ''
  sceneModal.name = ''
}

function openRenameScene(scene: ResourceScene) {
  sceneModal.show = true
  sceneModal.mode = 'rename'
  sceneModal.title = '重命名场景'
  sceneModal.id = scene.id
  sceneModal.name = scene.name
}

async function submitScene() {
  const name = sceneModal.name.trim()
  if (!name) {
    message.warning('场景名称不能为空')
    return
  }
  try {
    if (sceneModal.mode === 'create') {
      const res = await resourceApi.createScene(name)
      const scene = res.data.scene
      if (scene?.id) {
        scenes.value.push({ ...scene, elements: scene.elements ?? [] })
        selectedSceneId.value = scene.id
        message.success('场景创建成功')
      } else {
        message.error('场景创建失败')
      }
    } else {
      await resourceApi.renameScene(sceneModal.id, name)
      const target = scenes.value.find((s) => s.id === sceneModal.id)
      if (target) target.name = name
      message.success('场景重命名成功')
    }
    sceneModal.show = false
  } catch (e: any) {
    message.error(`操作失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

async function handleDeleteScene(id: string) {
  try {
    await resourceApi.deleteScene(id)
    scenes.value = scenes.value.filter((s) => s.id !== id)
    if (selectedSceneId.value === id) {
      selectedSceneId.value = scenes.value[0]?.id ?? null
    }
    await refreshEdges()
    message.success('场景已删除')
  } catch (e: any) {
    message.error(`删除失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

// ===== 元素 CRUD =====
const emptyElementForm = () => ({
  name: '',
  scene_id: '' as string,
  element_type: 0,
  match_type: 0,
  symbol: false,
  threshold: 0.8,
  ratio_x: 0.5,
  ratio_y: 0.5,
  roi_x: 0,
  roi_y: 0,
  roi_width: 0,
  roi_height: 0,
  ocr_min_score: 0.6,
  coordinate_x: 0,
  coordinate_y: 0,
})

const elementModal = reactive({
  show: false,
  title: '新增元素',
  isEdit: false,
  editId: '',
  form: emptyElementForm(),
})

function openCreateElement() {
  elementModal.show = true
  elementModal.isEdit = false
  elementModal.title = '新增元素'
  elementModal.editId = ''
  elementModal.form = emptyElementForm()
  elementModal.form.scene_id = selectedSceneId.value ?? ''
}

function openEditElement(row: ResourceElement) {
  elementModal.show = true
  elementModal.isEdit = true
  elementModal.title = '编辑元素'
  elementModal.editId = row.id
  elementModal.form = {
    name: row.name,
    scene_id: row.scene_id,
    element_type: row.element_type,
    match_type: row.match_type,
    symbol: row.symbol,
    threshold: row.threshold,
    ratio_x: row.ratio_x,
    ratio_y: row.ratio_y,
    roi_x: row.roi_x,
    roi_y: row.roi_y,
    roi_width: row.roi_width,
    roi_height: row.roi_height,
    ocr_min_score: row.ocr_min_score,
    coordinate_x: row.coordinate_x,
    coordinate_y: row.coordinate_y,
  }
}

function buildElementPayload(): ElementPayload {
  const f = elementModal.form
  return {
    name: f.name.trim() || undefined,
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
  }
}

async function submitElement() {
  const f = elementModal.form
  if (!f.scene_id) {
    message.warning('请选择所属场景')
    return
  }
  if (!f.name.trim()) {
    message.warning('元素名称不能为空')
    return
  }
  try {
    if (elementModal.isEdit) {
      await resourceApi.updateElement(elementModal.editId, buildElementPayload())
      message.success('元素已更新')
    } else {
      await resourceApi.createElement(f.scene_id, f.name.trim(), buildElementPayload())
      message.success('元素已创建')
    }
    elementModal.show = false
    await refreshElements(f.scene_id)
  } catch (e: any) {
    message.error(`保存失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

async function handleDeleteElement(row: ResourceElement) {
  try {
    await resourceApi.deleteElement(row.id)
    message.success('元素已删除')
    await refreshElements(row.scene_id)
  } catch (e: any) {
    message.error(`删除失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

// 批量刷新指定场景内的全部元素（不逐条请求）
async function refreshElements(sceneId: string) {
  try {
    const res = await resourceApi.getSceneElements(sceneId)
    const scene = scenes.value.find((s) => s.id === sceneId)
    if (scene) scene.elements = res.data.elements ?? []
  } catch (e: any) {
    message.error(`刷新元素失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

async function refreshEdges() {
  try {
    const res = await resourceApi.listEdges()
    edges.value = res.data.edges ?? []
  } catch (e) {
    /* 边列表刷新失败不阻塞主流程 */
  }
}

// ===== 场景跳转边 CRUD =====
const newEdgeSource = ref<string | null>(null)
const newEdgeTarget = ref<string | null>(null)

async function handleCreateEdge() {
  if (!newEdgeSource.value || !newEdgeTarget.value) {
    message.warning('请选择源场景与目标场景')
    return
  }
  if (newEdgeSource.value === newEdgeTarget.value) {
    message.warning('源场景与目标场景不能相同')
    return
  }
  try {
    await resourceApi.createEdge(newEdgeSource.value, newEdgeTarget.value)
    message.success('跳转边已添加')
    newEdgeSource.value = null
    newEdgeTarget.value = null
    await refreshEdges()
  } catch (e: any) {
    message.error(`添加失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

async function handleDeleteEdge(row: ResourceEdge) {
  try {
    await resourceApi.deleteEdge(row.source_scene_id, row.target_scene_id)
    await refreshEdges()
    message.success('跳转边已删除')
  } catch (e: any) {
    message.error(`删除失败: ${e?.response?.data?.detail ?? e.message}`)
  }
}

// ===== 表格列 =====
const columns: DataTableColumns<ResourceElement> = [
  { title: '名称', key: 'name', width: 120 },
  {
    title: '类型',
    key: 'element_type',
    width: 140,
    render: (row) => {
      const opt = elementTypeOptions.find((o) => o.value === row.element_type)
      return opt?.label ?? row.element_type
    },
  },
  {
    title: '匹配',
    key: 'match_type',
    width: 130,
    render: (row) => {
      const opt = matchTypeOptions.find((o) => o.value === row.match_type)
      return opt?.label ?? row.match_type
    },
  },
  { title: '阈值', key: 'threshold', width: 80 },
  { title: '比例', key: 'ratio', width: 100, render: (row) => `${row.ratio_x},${row.ratio_y}` },
  {
    title: 'ROI',
    key: 'roi',
    width: 140,
    render: (row) =>
      `${row.roi_x},${row.roi_y},${row.roi_width},${row.roi_height}`,
  },
  {
    title: '点击坐标',
    key: 'coordinate',
    width: 110,
    render: (row) => `${row.coordinate_x},${row.coordinate_y}`,
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(
            NButton,
            { size: 'tiny', onClick: () => openEditElement(row) },
            { default: () => '编辑' },
          ),
          h(
            NPopconfirm,
            { onPositiveClick: () => handleDeleteElement(row) },
            {
              trigger: () =>
                h(
                  NButton,
                  { size: 'tiny', type: 'error', secondary: true },
                  { default: () => '删除' },
                ),
              default: () => `确定删除元素「${row.name}」？`,
            },
          ),
        ],
      }),
  },
]

const edgeColumns: DataTableColumns<ResourceEdge> = [
  {
    title: '源场景',
    key: 'source_scene_id',
    render: (row) => sceneNameById(row.source_scene_id),
  },
  {
    title: '目标场景',
    key: 'target_scene_id',
    render: (row) => sceneNameById(row.target_scene_id),
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) =>
      h(
        NPopconfirm,
        { onPositiveClick: () => handleDeleteEdge(row) },
        {
          trigger: () =>
            h(
              NButton,
              { size: 'tiny', type: 'error', secondary: true },
              { default: () => '删除' },
            ),
          default: () => '确定删除该跳转边？',
        },
      ),
  },
]

onMounted(refreshAll)
</script>

<style scoped>
.scene-active {
  background: rgba(84, 148, 246, 0.12);
}
</style>