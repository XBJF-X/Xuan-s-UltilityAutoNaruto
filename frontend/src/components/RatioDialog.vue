<template>
  <n-modal
    :show="show"
    preset="card"
    title="设置 Ratio（点击元素图片选择位置）"
    style="width: 640px"
    @update:show="onClose"
  >
    <div class="ratio-dialog">
      <div class="ratio-image-wrap" ref="wrapEl">
        <img
          v-if="imageUrl"
          ref="imgEl"
          :src="imageUrl"
          class="ratio-image"
          @load="onImageLoad"
          @mousemove="onMouseMove"
          @click="onClick"
          draggable="false"
        />
        <div v-else class="ratio-empty">元素图片不存在</div>
        <!-- 十字标记（叠加在图片上） -->
        <div
          v-if="mark.x !== null"
          class="ratio-mark"
          :style="{ left: mark.x + 'px', top: mark.y + 'px' }"
        ></div>
      </div>
      <div class="ratio-info">
        <n-tag type="info" size="small">
          Ratio: ({{ ratio.x.toFixed(2) }}, {{ ratio.y.toFixed(2) }})
        </n-tag>
        <n-text depth="3" style="font-size: 12px">
          点击图片上任意位置（可超出图片边缘，允许大于 1 或负数）
        </n-text>
      </div>
    </div>
    <template #footer>
      <n-space justify="end">
        <n-button @click="onClose">取消</n-button>
        <n-button type="primary" :disabled="!picked" @click="onConfirm">确定</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { resourceApi } from '../api/resource'

const props = defineProps<{
  show: boolean
  elementId: string
}>()

const emit = defineEmits<{
  (e: 'update:show', v: boolean): void
  (e: 'confirm', ratio: { x: number; y: number }): void
}>()

const imageUrl = ref('')
const imgEl = ref<HTMLImageElement | null>(null)
const wrapEl = ref<HTMLDivElement | null>(null)
const ratio = reactive({ x: 0.5, y: 0.5 })
const mark = reactive({ x: null as number | null, y: null as number | null })
const picked = ref(false)
let objectUrl = ''

watch(
  () => props.show,
  async (v) => {
    if (!v) return
    picked.value = false
    mark.x = null
    mark.y = null
    ratio.x = 0.5
    ratio.y = 0.5
    if (objectUrl) URL.revokeObjectURL(objectUrl)
    objectUrl = ''
    imageUrl.value = ''
    try {
      const res = await resourceApi.getElementImage(props.elementId)
      objectUrl = URL.createObjectURL(res.data)
      imageUrl.value = objectUrl
    } catch {
      imageUrl.value = ''
    }
  },
)

function onImageLoad() {
  // 图片加载完成，重置标记位置
  mark.x = null
  mark.y = null
}

/** 将鼠标事件位置换算为图片内的逻辑像素坐标（基于图片实际显示大小） */
function eventToImagePos(e: MouseEvent) {
  const img = imgEl.value
  if (!img) return { x: 0, y: 0 }
  const rect = img.getBoundingClientRect()
  // 点击位置相对图片左上角（可能为负或超过宽高 → 允许 Ratio 为负/大于1）
  const imgX = e.clientX - rect.left
  const imgY = e.clientY - rect.top
  const w = rect.width || 1
  const h = rect.height || 1
  return { x: imgX, y: imgY, w, h }
}

function onMouseMove(e: MouseEvent) {
  if (!imgEl.value) return
  const { x, y } = eventToImagePos(e)
  mark.x = x
  mark.y = y
  // 实时预览 Ratio（允许大于1或负数）
  const { w, h } = eventToImagePos(e)
  ratio.x = w > 0 ? x / w : 0
  ratio.y = h > 0 ? y / h : 0
  picked.value = true
}

function onClick(e: MouseEvent) {
  if (!imgEl.value) return
  const { x, y, w, h } = eventToImagePos(e)
  ratio.x = w > 0 ? x / w : 0
  ratio.y = h > 0 ? y / h : 0
  mark.x = x
  mark.y = y
  picked.value = true
}

function onConfirm() {
  emit('confirm', { x: Number(ratio.x.toFixed(3)), y: Number(ratio.y.toFixed(3)) })
  onClose()
}

function onClose() {
  emit('update:show', false)
}

onBeforeUnmount(() => {
  if (objectUrl) URL.revokeObjectURL(objectUrl)
})
</script>

<style scoped>
.ratio-dialog {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ratio-image-wrap {
  position: relative;
  max-height: 480px;
  overflow: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}
.ratio-image {
  display: block;
  max-width: 100%;
  max-height: 480px;
  cursor: crosshair;
  user-select: none;
}
.ratio-empty {
  padding: 60px 20px;
  color: #999;
}
.ratio-mark {
  position: absolute;
  width: 20px;
  height: 20px;
  transform: translate(-50%, -50%);
  pointer-events: none;
}
.ratio-mark::before,
.ratio-mark::after {
  content: '';
  position: absolute;
  background: #ff4d4f;
}
.ratio-mark::before {
  left: 0;
  top: 9px;
  width: 20px;
  height: 2px;
}
.ratio-mark::after {
  left: 9px;
  top: 0;
  width: 2px;
  height: 20px;
}
.ratio-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
