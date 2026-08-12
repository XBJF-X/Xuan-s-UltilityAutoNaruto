import client from './client'

// ===== 资源管理（场景 / 元素）API =====
// 设计：前端初始化一次全量读取，场景内元素一次批量读取，避免逐条请求

/** 元素概要（后端 /resource/full 返回） */
export interface ResourceElement {
  id: string
  name: string
  scene_id: string
  symbol: boolean
  element_type: number
  match_type: number
  threshold: number
  ratio_x: number
  ratio_y: number
  roi_x: number
  roi_y: number
  roi_width: number
  roi_height: number
  ocr_min_score: number
  coordinate_x: number
  coordinate_y: number
}

/** 场景（含元素概要） */
export interface ResourceScene {
  id: string
  name: string
  elements: ResourceElement[]
}

/** 场景跳转边 */
export interface ResourceEdge {
  id: string
  source_scene_id: string
  target_scene_id: string
}

/** 用于新增/编辑元素的请求字段 */
export interface ElementPayload {
  name?: string
  symbol?: boolean
  element_type?: number
  match_type?: number
  threshold?: number
  ratio_x?: number
  ratio_y?: number
  roi_x?: number
  roi_y?: number
  roi_width?: number
  roi_height?: number
  ocr_min_score?: number
  coordinate_x?: number
  coordinate_y?: number
}

export const resourceApi = {
  /** 全量读取：所有场景及其元素概要（前端初始化用） */
  getFull: () => client.get('/resource/full'),

  /** 场景列表（不含元素） */
  listScenes: () => client.get('/resource/scenes'),

  /** 新增场景 */
  createScene: (name: string) => client.post('/resource/scenes', { name }),

  /** 重命名场景 */
  renameScene: (sceneId: string, name: string) =>
    client.put(`/resource/scenes/${sceneId}`, { name }),

  /** 删除场景（连带其元素与跳转边） */
  deleteScene: (sceneId: string) => client.delete(`/resource/scenes/${sceneId}`),

  /** 批量读取场景内全部元素 */
  getSceneElements: (sceneId: string) =>
    client.get(`/resource/scenes/${sceneId}/elements`),

  /** 全部场景跳转边 */
  listEdges: () => client.get('/resource/edges'),

  /** 新增场景跳转边 */
  createEdge: (sourceSceneId: string, targetSceneId: string) =>
    client.post('/resource/edges', {
      source_scene_id: sourceSceneId,
      target_scene_id: targetSceneId,
    }),

  /** 删除场景跳转边 */
  deleteEdge: (sourceSceneId: string, targetSceneId: string) =>
    client.delete('/resource/edges', {
      data: { source_scene_id: sourceSceneId, target_scene_id: targetSceneId },
    }),

  /** 新增元素（必须指定所属场景） */
  createElement: (sceneId: string, name: string, payload: ElementPayload = {}) =>
    client.post('/resource/elements', { scene_id: sceneId, name, ...payload }),

  /** 更新元素字段 */
  updateElement: (elementId: string, payload: ElementPayload) =>
    client.put(`/resource/elements/${elementId}`, payload),

  /** 删除元素 */
  deleteElement: (elementId: string) =>
    client.delete(`/resource/elements/${elementId}`),

  /** 获取元素图像（仅存 4 通道 BGRA），返回 PNG blob */
  getElementImage: (elementId: string) =>
    client.get(`/resource/elements/${elementId}/image`, {
      responseType: 'blob',
    }),

  /** 上传/替换元素图像（原始 PNG 字节直接存 bgra） */
  uploadElementImage: (elementId: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return client.post(`/resource/elements/${elementId}/image`, form, {
      // 必须覆盖全局默认 Content-Type: application/json，
      // 否则 FormData 边界丢失导致 FastAPI 无法解析 file 字段（报错 [object Object]）
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** 场景执行匹配：对该场景全部 IMG 元素执行 element_match */
  matchScene: (sceneId: string) => client.post(`/resource/scenes/${sceneId}/match`),

  /** 元素执行匹配：加载所属场景底图并对该元素执行 element_match */
  matchElement: (elementId: string) => client.post(`/resource/elements/${elementId}/match`),

  /** 元素执行 OCR 识别：加载所属场景底图并对 OCR 元素 ROI 区域执行 area_ocr */
  ocrElement: (elementId: string) => client.post(`/resource/elements/${elementId}/ocr`),

  /** 获取场景底图（优先 test_scene/{场景名} 图片），返回 Blob */
  getSceneBaseImage: (sceneId: string) =>
    client.get(`/resource/scenes/${sceneId}/base_image`, {
      responseType: 'blob',
    }),
}
