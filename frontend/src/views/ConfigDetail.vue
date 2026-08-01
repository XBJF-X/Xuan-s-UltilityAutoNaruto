<template>
  <div class="config-detail">
    <n-h1>配置编辑器</n-h1>

    <!-- 配置选择器 -->
    <n-space vertical size="large">
      <n-card size="small">
        <n-space align="center" justify="space-between">
          <n-space align="center">
            <n-select
              v-model:value="selectedConfigId"
              :options="configOptions"
              placeholder="选择配置"
              style="width: 240px"
              clearable
              filterable
              @update:value="loadConfig"
            />
            <n-tag v-if="loadedConfig" type="info">{{ loadedConfig.username }}</n-tag>
            <n-tag v-if="loadedConfig" type="warning">版本: {{ loadedConfig.setting_dics?.['配置文件版本'] || '-' }}</n-tag>
          </n-space>
          <n-space>
            <n-button size="small" @click="loadConfig(selectedConfigId)" :disabled="!selectedConfigId">
              <template #icon><n-icon><RefreshRound /></n-icon></template>
              重新加载
            </n-button>
            <n-button size="small" type="primary" @click="saveAll" :disabled="!loadedConfig" :loading="saving">
              保存所有
            </n-button>
          </n-space>
        </n-space>
      </n-card>

      <template v-if="!loadedConfig">
        <n-empty description="请先选择一个配置">
          <template #extra>
            <n-button @click="router.push({ name: 'Dashboard' })">前往总览创建配置</n-button>
          </template>
        </n-empty>
      </template>

      <template v-else>
        <n-tabs type="line" animated>
          <!-- Tab 1: 助手设置 -->
          <n-tab-pane tab="助手设置">
            <n-space vertical size="medium">
              <!-- 控制模式 -->
              <n-card title="控制模式" size="small">
                <n-space align="center">
                  <n-input v-model:value="assistantSettings['串口']" placeholder="设备串口" style="width: 260px" />
                  <n-button size="small" @click="showSerialChooser = true">选择串口</n-button>
                  <n-select
                    v-model:value="assistantSettings['控制模式']"
                    :options="controlModeOptions"
                    style="width: 140px"
                    placeholder="控制模式"
                  />
                  <n-text depth="3" style="font-size: 12px">MiniTouch=1, U2=2</n-text>
                </n-space>
              </n-card>

              <!-- 截图模式 -->
              <n-card title="截图模式" size="small">
                <n-space vertical>
                  <n-space align="center">
                    <n-select
                      v-model:value="assistantSettings['截图模式']"
                      :options="screenModeOptions"
                      style="width: 200px"
                      placeholder="截图模式"
                    />
                    <n-text depth="3" style="font-size: 12px">DroidCast=0, Window=1, U2=2, MuMu=3, LD=4</n-text>
                  </n-space>
                  <!-- 截图模式动态参数 -->
                  <n-space v-if="assistantSettings['截图模式'] == 3 || assistantSettings['截图模式'] == 4" align="center">
                    <n-text style="font-size: 12px">安装路径:</n-text>
                    <n-input v-model:value="assistantSettings['模拟器路径']" placeholder="模拟器安装路径" style="width: 300px" />
                    <n-button size="tiny" @click="selectSimulatorPath">浏览</n-button>
                  </n-space>
                  <n-space v-if="assistantSettings['截图模式'] == 3 || assistantSettings['截图模式'] == 4" align="center">
                    <n-text style="font-size: 12px">实例索引:</n-text>
                    <n-input-number v-model:value="assistantSettings['实例索引']" :min="0" :max="9" style="width: 100px" />
                  </n-space>
                </n-space>
              </n-card>

              <!-- 扫描间隔 -->
              <n-card title="扫描间隔" size="small">
                <n-space align="center">
                  <n-input-number v-model:value="assistantSettings['扫描间隔']" :min="0" :max="60" style="width: 120px" />
                  <n-text depth="3" style="font-size: 12px">秒（0为最快）</n-text>
                </n-space>
              </n-card>

              <!-- 连点键位 -->
              <n-card title="连点键位" size="small">
                <template #header-extra>
                  <n-button size="small" type="primary" @click="showKeyMapEditor = true">配置键位</n-button>
                </template>
                <n-text depth="3" style="font-size: 12px">点击配置键位按钮，在截图上拖拽标记10个技能键位</n-text>
              </n-card>

              <!-- 二级密码 -->
              <n-card title="二级密码" size="small">
                <n-input
                  v-model:value="assistantSettings['二级密码']"
                  placeholder="游戏内二级密码"
                  type="password"
                  show-password-on="click"
                  style="width: 200px"
                />
              </n-card>

              <!-- 调试模式 -->
              <n-card title="调试" size="small">
                <n-space align="center">
                  <n-text style="font-size: 12px">调试模式:</n-text>
                  <n-switch
                    :value="assistantSettings['调试模式']"
                    @update:value="(v: boolean) => assistantSettings['调试模式'] = v"
                  />
                  <n-text depth="3" style="font-size: 12px">0=关闭, 1=开启</n-text>
                </n-space>
              </n-card>
            </n-space>
          </n-tab-pane>

          <!-- Tab 2: 任务配置 -->
          <n-tab-pane tab="任务配置">
            <n-tabs type="segment" animated>
              <n-tab-pane v-for="group in taskGroups" :key="group.label" :tab="`${group.label} (${group.tasks.length})`">
                <n-grid :cols="2" :x-gap="12" :y-gap="12">
                  <n-grid-item v-for="task in group.tasks" :key="task.name">
                    <n-card
                      :title="task.name"
                      size="small"
                      :segmented="{ content: true }"
                      hoverable
                      :class="{ 'task-disabled': !taskData[task.name]?.['是否启用'] }"
                    >
                      <template #header-extra>
                        <n-switch
                          :value="taskData[task.name]?.['是否启用'] ?? false"
                          @update:value="(v) => setTaskEnabled(task.name, v)"
                          size="small"
                        />
                      </template>
                      <n-space vertical size="small">
                        <n-text v-if="taskData[task.name]?.描述" depth="3" style="font-size: 12px">
                          {{ taskData[task.name]?.描述 }}
                        </n-text>

                        <n-space align="center">
                          <n-text depth="3" style="font-size: 12px">连点优先级:</n-text>
                          <n-input-number
                            :value="taskData[task.name]?.['连点优先级'] ?? 0"
                            @update:value="(v) => setTaskField(task.name, '连点优先级', v)"
                            size="tiny" :min="-999" :max="999" style="width: 80px"
                          />
                          <n-text depth="3" style="font-size: 12px">基础优先级:</n-text>
                          <n-input-number
                            :value="taskData[task.name]?.['基础优先级'] ?? 0"
                            @update:value="(v) => setTaskField(task.name, '基础优先级', v)"
                            size="tiny" :min="-999" :max="999" style="width: 80px"
                          />
                        </n-space>

                        <!-- 下次执行时间 -->
                        <n-space align="center" v-if="taskData[task.name]?.['下次执行时间']">
                          <n-text depth="3" style="font-size: 12px">下次执行:</n-text>
                          <n-text style="font-size: 12px">{{ taskData[task.name]['下次执行时间'] }}</n-text>
                        </n-space>

                        <template v-if="taskData[task.name]?.['执行参数']">
                          <n-divider style="margin: 4px 0" />
                          <n-text depth="3" style="font-size: 12px">执行参数</n-text>
                          <n-grid :cols="2" :x-gap="8" :y-gap="6">
                            <n-grid-item v-for="(paramVal, paramKey) in taskData[task.name]['执行参数']" :key="paramKey">
                              <n-thing style="font-size: 12px">
                                <template #label>
                                  <n-text style="font-size: 12px">{{ paramKey }}</n-text>
                                </template>
                                <template #description>
                                  <n-text v-if="paramVal.描述" depth="3" style="font-size: 11px">{{ paramVal.描述 }}</n-text>
                                  <ConfigValueEditor
                                    :config-key="paramKey"
                                    :value="paramVal"
                                    :task-schema="taskSchema"
                                    size="tiny"
                                    @update:value="(v) => onTaskParamChange(task.name, paramKey, v)"
                                  />
                                </template>
                              </n-thing>
                            </n-grid-item>
                          </n-grid>
                        </template>

                        <template v-if="taskData[task.name]?.['执行进度']">
                          <n-divider style="margin: 4px 0" />
                          <n-space v-if="hasProgress(taskData[task.name]['执行进度'])" align="center">
                            <n-text depth="3" style="font-size: 12px">执行进度:</n-text>
                            <n-tag size="tiny" type="success">{{ progressSummary(taskData[task.name]['执行进度']) }}</n-tag>
                          </n-space>
                        </template>
                      </n-space>
                    </n-card>
                  </n-grid-item>
                </n-grid>
              </n-tab-pane>
            </n-tabs>
          </n-tab-pane>
        </n-tabs>
      </template>
    </n-space>

    <!-- 串口选择对话框 -->
    <n-modal v-model:show="showSerialChooser" title="选择设备串口" preset="card" style="width: 420px">
      <n-space vertical>
        <n-empty v-if="serialDevices.length === 0" description="未检测到ADB设备">
          <template #extra>
            <n-button size="small" @click="refreshSerialDevices" :loading="loadingSerials">刷新</n-button>
          </template>
        </n-empty>
        <n-list v-else>
          <n-list-item v-for="s in serialDevices" :key="s" clickable @click="selectSerial(s)">
            {{ s }}
          </n-list-item>
        </n-list>
        <n-space justify="end">
          <n-button @click="refreshSerialDevices" :loading="loadingSerials">重启ADB</n-button>
          <n-button type="primary" @click="showSerialChooser = false">确定</n-button>
        </n-space>
      </n-space>
    </n-modal>

    <!-- 键位配置对话框 -->
    <n-modal v-model:show="showKeyMapEditor" title="键位配置" preset="card" style="width: 800px">
      <n-empty description="键位配置需要设备截图支持，请先启动调度器获取截图">
        <template #extra>
          <n-button @click="showKeyMapEditor = false">关闭</n-button>
        </template>
      </n-empty>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { configApi } from '@/api/client'
import { RefreshRound } from '@vicons/material'
import ConfigValueEditor from '@/components/ConfigValueEditor.vue'

const router = useRouter()
const appStore = useAppStore()
const message = useMessage()

const selectedConfigId = ref<string | null>(null)
const loadedConfig = ref<any>(null)
const saving = ref(false)

const settingDics = ref<Record<string, any>>({})
const taskData = ref<Record<string, any>>({})
const taskSchema = ref<Record<string, any>>({})

// 串口选择
const showSerialChooser = ref(false)
const serialDevices = ref<string[]>([])
const loadingSerials = ref(false)

// 键位编辑器
const showKeyMapEditor = ref(false)

// 助手设置 - 提取常用设置项
const assistantSettings = reactive<Record<string, any>>({
  '串口': '',
  '控制模式': 1,
  '截图模式': 0,
  '模拟器路径': '',
  '实例索引': 0,
  '扫描间隔': 1,
  '二级密码': '',
  '调试模式': 0,
})

const controlModeOptions = [
  { label: 'MiniTouch (1)', value: 1 },
  { label: 'U2 (2)', value: 2 },
]

const screenModeOptions = [
  { label: 'DroidCastRaw (0)', value: 0 },
  { label: 'WindowCapture (1)', value: 1 },
  { label: 'U2 (2)', value: 2 },
  { label: 'MuMu (3)', value: 3 },
  { label: 'LD (4)', value: 4 },
]

const configOptions = computed(() =>
  (appStore.configs || []).map((c: any) => ({
    label: `${c.username} (${c.id})`,
    value: c.id,
  }))
)

const taskGroups = computed(() => {
  const entries = Object.entries(taskData.value || {})
  const groups: Record<string, { label: string; tasks: any[] }> = {
    daily: { label: '每日任务', tasks: [] },
    weekly: { label: '每周/赛季', tasks: [] },
    event: { label: '限时活动', tasks: [] },
    pvp: { label: 'PVP', tasks: [] },
    other: { label: '其他', tasks: [] },
  }
  const typeMap: Record<number, string> = { 0: 'daily', 1: 'weekly', 2: 'weekly', 3: 'event', 4: 'event', 5: 'event' }
  for (const [name, info] of entries) {
    const group = typeMap[(info as any).类型] || 'other'
    groups[group].tasks.push({ name, ...info as any })
  }
  return Object.values(groups).filter(g => g.tasks.length > 0)
})

function hasProgress(p: any): boolean {
  if (!p || typeof p !== 'object') return false
  return Object.values(p).some(v => v !== false && v !== 0 && v !== '')
}

function progressSummary(p: any): string {
  return Object.entries(p || {}).filter(([, v]) => v !== false && v !== 0 && v !== '')
    .map(([k, v]) => `${k}: ${v}`).join(' | ') || '无'
}

function syncAssistantSettings() {
  for (const key of Object.keys(assistantSettings)) {
    if (key in settingDics.value) {
      assistantSettings[key] = settingDics.value[key]
    }
  }
}

async function loadConfig(configId?: string | null) {
  if (!configId) return
  try {
    const res = await configApi.get(configId)
    loadedConfig.value = res.data
    settingDics.value = JSON.parse(JSON.stringify(res.data.setting_dics || {}))
    taskData.value = JSON.parse(JSON.stringify(res.data.tasks || {}))
    syncAssistantSettings()
    if (Object.keys(taskSchema.value).length === 0) {
      const schemaRes = await configApi.getDefaultTasks()
      taskSchema.value = schemaRes.data
    }
  } catch (e) {
    console.error('加载配置失败:', e)
    loadedConfig.value = null
    settingDics.value = {}
    taskData.value = {}
  }
}

function setTaskEnabled(taskName: string, enabled: boolean) {
  if (taskData.value[taskName]) taskData.value[taskName]['是否启用'] = enabled
}

function setTaskField(taskName: string, field: string, value: any) {
  if (taskData.value[taskName]) taskData.value[taskName][field] = value
}

function onTaskParamChange(taskName: string, paramKey: string, value: any) {
  if (taskData.value[taskName]?.['执行参数']?.[paramKey]) {
    taskData.value[taskName]['执行参数'][paramKey]['当前值'] = value
  }
}

function selectSerial(serial: string) {
  assistantSettings['串口'] = serial
  showSerialChooser.value = false
}

async function refreshSerialDevices() {
  loadingSerials.value = true
  try {
    const res = await configApi.list()
    serialDevices.value = []
    message.warning('ADB设备列表需通过后端 /api/settings 获取')
  } catch {
    serialDevices.value = []
  }
  loadingSerials.value = false
}

async function selectSimulatorPath() {
  message.info('模拟器路径选择需要通过 Electron 支持，当前为浏览器模式')
}

async function saveAll() {
  if (!selectedConfigId.value || !loadedConfig.value) return
  saving.value = true
  try {
    // 同步助手设置到 settingDics
    for (const key of Object.keys(assistantSettings)) {
      settingDics.value[key] = assistantSettings[key]
    }
    // 逐个保存设置
    for (const [key, value] of Object.entries(settingDics.value)) {
      if (key === '任务') continue
      await configApi.updateSetting(selectedConfigId.value, key, value)
    }
    // 逐个保存任务
    for (const [taskName, taskInfo] of Object.entries(taskData.value)) {
      const info = taskInfo as any
      await configApi.updateTask(selectedConfigId.value, taskName, '是否启用', info['是否启用'])
      await configApi.updateTask(selectedConfigId.value, taskName, '连点优先级', info['连点优先级'])
      await configApi.updateTask(selectedConfigId.value, taskName, '基础优先级', info['基础优先级'])
      if (info['执行参数']) {
        for (const [paramKey, paramVal] of Object.entries(info['执行参数'])) {
          await configApi.updateTaskParam(selectedConfigId.value, taskName, paramKey, (paramVal as any)['当前值'])
        }
      }
    }
    message.success('所有配置已保存')
  } catch (e) {
    console.error('保存失败:', e)
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  appStore.loadConfigs()
})
</script>

<style scoped>
.config-detail {
  height: 100%;
  overflow-y: auto;
}
.task-disabled {
  opacity: 0.5;
}
</style>