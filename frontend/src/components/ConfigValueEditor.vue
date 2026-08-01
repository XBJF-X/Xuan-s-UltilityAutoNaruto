<template>
  <div class="config-value-editor">
    <!-- BOOL 类型 -->
    <n-switch
      v-if="fieldType === 'BOOL'"
      :value="currentValue"
      @update:value="emitValue"
      :size="props.size || 'small'"
    />

    <!-- COMBOX 枚举类型 -->
    <n-select
      v-else-if="fieldType === 'COMBOX'"
      :value="currentValue"
      @update:value="emitValue"
      :options="comboxOptions"
      :size="props.size || 'small'"
      style="min-width: 120px"
    />

    <!-- INT 类型 -->
    <n-input-number
      v-else-if="fieldType === 'INT'"
      :value="currentValue"
      @update:value="emitValue"
      :min="fieldSchema?.最小值 ?? 0"
      :max="fieldSchema?.最大值 ?? 99999"
      :size="props.size || 'small'"
      style="width: 120px"
    />

    <!-- 字符串/其他 -->
    <n-input
      v-else
      :value="String(currentValue ?? '')"
      @update:value="emitValue"
      :size="props.size || 'small'"
      style="min-width: 120px"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  configKey: string
  value: any
  taskSchema?: Record<string, any>
  size?: 'tiny' | 'small' | 'medium' | 'large'
}>()

const emit = defineEmits<{
  'update:value': [value: any]
}>()

// 判断字段类型
const fieldSchema = computed(() => {
  // value 可能是普通值（如 true/1/"字符串"）也可能是 schema 对象（如 {类型: "INT", 当前值: 0,...}）
  if (props.value && typeof props.value === 'object' && '类型' in props.value) {
    return props.value
  }
  // 尝试从 taskSchema 中获取
  if (props.taskSchema) {
    // 遍历所有任务的 schema
    const allTasks = props.taskSchema?.tasks || props.taskSchema?.setting_dics?.tasks || {}
    for (const task of Object.values(allTasks) as any[]) {
      for (const [k, v] of Object.entries(task?.['执行参数'] || {}) as any[]) {
        if (k === props.configKey) return v
      }
    }
  }
  return null
})

const fieldType = computed(() => {
  // 如果有 schema 对象，直接用类型字段
  if (fieldSchema.value?.类型) return fieldSchema.value.类型
  // 根据 value 推断类型
  if (typeof props.value === 'boolean') return 'BOOL'
  if (typeof props.value === 'number') return 'INT'
  if (Array.isArray(props.value)) return 'ARRAY'
  return 'STRING'
})

const comboxOptions = computed(() => {
  const list = fieldSchema.value?.['枚举列表']
  if (Array.isArray(list)) {
    return list.map((item: string, idx: number) => ({
      label: item,
      value: idx,
    }))
  }
  return []
})

// 当前显示的『值』
const currentValue = computed(() => {
  // schema 对象中有 '当前值' 字段
  if (fieldSchema.value && '当前值' in fieldSchema.value) {
    return fieldSchema.value.当前值
  }
  return props.value
})

function emitValue(val: any) {
  emit('update:value', val)
}
</script>

<style scoped>
.config-value-editor {
  display: inline-flex;
}
</style>