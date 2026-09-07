<template>
  <n-modal
    v-model:show="showModel"
    preset="card"
    title="检查更新"
    style="width: min(640px, calc(100vw - 48px))"
    :mask-closable="!isUpdating"
    :closable="!isUpdating"
    @after-leave="reset"
  >
    <!-- 内容区按当前视图高度限制并内部滚动：小窗口下页脚（关闭/立即更新）不被挤出窗口外 -->
    <div class="modal-scroll">
    <template v-if="loading">
      <div class="center-box">
        <n-spin size="large" />
        <n-text depth="3">正在检查云端提交记录...</n-text>
      </div>
    </template>

    <template v-else-if="error">
      <n-result status="error" title="检查更新失败" :description="error">
        <template #footer>
          <n-button @click="check">重试</n-button>
        </template>
      </n-result>
    </template>

    <template v-else-if="info">
      <div class="version-compare">
        <div class="vc-item">
          <div class="vc-label">本地版本</div>
          <div class="vc-value">
            <template v-if="info.update_type === 'full'">
              <span class="sha">{{ info.full.local_version || '未知' }}</span>
              <span class="msg">正式版</span>
            </template>
            <template v-else-if="info.current_commit">
              <span class="sha">{{ info.current_commit.short_sha }}</span>
              <span class="msg">{{ info.current_commit.message }}</span>
            </template>
            <template v-else>
              <span class="muted">{{ info.current_sha ? info.current_sha.slice(0, 7) : '未知' }}</span>
              <span class="muted">未在云端找到对应提交</span>
            </template>
          </div>
        </div>
        <div class="vc-arrow">→</div>
        <div class="vc-item">
          <div class="vc-label">云端最新</div>
          <div class="vc-value">
            <template v-if="info.update_type === 'full'">
              <span class="sha">{{ info.full.tag }}</span>
              <span class="msg">{{ info.full.name }}</span>
            </template>
            <template v-else>
              <span class="sha">{{ info.latest_sha.slice(0, 7) }}</span>
              <span class="msg">{{ info.latest_message }}</span>
            </template>
          </div>
        </div>
      </div>

      <n-alert v-if="info.update_type === 'full'" type="warning" :show-icon="true" style="margin-bottom: 12px;">
        <template v-if="info.full.deprecated">
          当前本地版本 {{ info.full.local_version }} 低于本版本要求的最低版本 {{ info.full.required_version }}，依赖库不完整，请前往 Release 下载完整安装包更新。
        </template>
        <template v-else>
          检测到新正式版本 {{ info.full.version }}，包含依赖库等完整更新。点击下方按钮下载安装包，程序将自动完成升级并重启。
        </template>
      </n-alert>
      <n-alert v-else-if="info.update_type === 'hot'" type="warning" :show-icon="true" style="margin-bottom: 12px;">
        检测到新的修复/功能更新，点击下方按钮可立即更新，程序将自动重启生效。
      </n-alert>
      <n-alert v-else type="success" :show-icon="true" style="margin-bottom: 12px;">
        当前已是最新版本。
      </n-alert>

      <!-- 大更新：Release 更新说明 -->
      <template v-if="info.update_type === 'full'">
        <div class="release-section">
          <div class="section-title">更新内容（{{ formatDate(info.full.published_at) }}）</div>
          <div class="release-body">{{ info.full.body || '暂无说明' }}</div>
        </div>
      </template>

      <!-- 更新进度 -->
      <template v-if="isUpdating">
        <n-card size="small" class="progress-card">
          <div class="phase-row">
            <n-text :type="progress.error ? 'error' : 'primary'" weight="bold">
              {{ phaseLabel }}
            </n-text>
            <n-text depth="3">{{ progress.percent }}%</n-text>
          </div>
          <n-progress
            type="line"
            :percentage="progress.percent"
            :status="progress.error ? 'error' : undefined"
            :processing="progress.running && !progress.error"
            indicator-placement="inside"
            height="14"
          />
          <n-text depth="3" class="phase-msg">{{ progress.message }}</n-text>
        </n-card>
      </template>

      <!-- 提交历史（仅热更新展示） -->
      <div v-if="info.update_type !== 'full'" class="commit-section">
        <div class="section-title">云端提交历史</div>
        <div class="commit-list">
          <div
            v-for="c in info.commits"
            :key="c.sha"
            class="commit-item"
            :class="{
              'is-latest': c.sha === info.latest_sha,
              'is-current': c.sha === info.current_sha,
            }"
          >
            <span class="c-tag" v-if="c.sha === info.latest_sha">最新</span>
            <span class="c-tag current" v-else-if="c.sha === info.current_sha">本地</span>
            <span class="c-sha">{{ c.short_sha }}</span>
            <span class="c-msg">{{ c.message }}</span>
            <span class="c-date">{{ formatDate(c.date) }}</span>
            <span class="c-author">{{ c.author }}</span>
          </div>
          <n-empty v-if="!info.commits || info.commits.length === 0" description="暂无提交记录" size="small" style="padding: 12px 0;" />
        </div>
      </div>

    </template>
    </div>

    <template #footer>
      <n-space justify="end">
        <n-button @click="close" :disabled="isUpdating">关闭</n-button>
        <n-button
          v-if="info && info.update_type !== 'none' && !isUpdating"
          type="primary"
          @click="onFooterClick"
          :loading="startingUpdate"
        >
          {{ footerButtonText }}
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'
import { utilsApi } from '@/api/client'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const showModel = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const message = useMessage()
const loading = ref(false)
const error = ref('')
const info = ref<any>(null)
const isUpdating = ref(false)
const startingUpdate = ref(false)
const progress = ref<{ running: boolean; phase: string; percent: number; message: string; error: string }>({
  running: false, phase: '', percent: 0, message: '', error: '',
})

let pollTimer: ReturnType<typeof setInterval> | null = null

const phaseLabel = computed(() => {
  const map: Record<string, string> = {
    downloading: '下载更新包',
    extracting: '解压更新包',
    replacing: '替换文件',
    'writing-version': '更新版本记录',
    'downloading-installer': '下载安装包',
    verifying: '校验安装包',
    done: '更新完成',
    error: '更新失败',
  }
  return map[progress.value.phase] || '准备中'
})

function formatDate(iso: string) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { hour12: false })
  } catch { return iso }
}

// 依赖库过旧（deprecated）且云端无可用安装包资产时，引导用户前往 Release 页面手动下载
const footerButtonText = computed(() => {
  if (!info.value || info.value.update_type === 'none') return ''
  const full = info.value.full
  if (info.value.update_type === 'full' && full?.deprecated && !full?.asset) return '前往 Release 页面'
  return info.value.update_type === 'full' ? '下载并升级' : '立即更新'
})

function onFooterClick() {
  const full = info.value?.full
  if (info.value?.update_type === 'full' && full?.deprecated && !full?.asset) {
    window.open(full.release_url || 'https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto/releases', '_blank')
    return
  }
  apply()
}

async function check() {
  loading.value = true
  error.value = ''
  info.value = null
  try {
    const res = await utilsApi.checkUpdate()
    const data = res.data
    if (!data?.ok) {
      error.value = data?.message || '检查更新失败'
      return
    }
    info.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '网络请求失败'
  } finally {
    loading.value = false
  }
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

async function apply() {
  isUpdating.value = true
  startingUpdate.value = true
  try {
    // 大更新走 Release 安装包；热更新走分支 zipball
    const res = info.value?.update_type === 'full'
      ? await utilsApi.applyReleaseUpdate()
      : await utilsApi.applyUpdate()
    if (!res.data?.ok) {
      message.error(res.data?.message || '启动更新失败')
      isUpdating.value = false
      return
    }
    pollTimer = setInterval(async () => {
      try {
        const stRes = await utilsApi.updateStatus()
        const st = stRes.data
        if (!st) return
        progress.value = {
          running: st.running,
          phase: st.phase,
          percent: st.percent ?? 0,
          message: st.message || '',
          error: st.error || '',
        }
        if (st.phase === 'done') {
          stopPolling()
          message.success(st.message || '更新完成')
          // 稍等让用户看到完成状态
          setTimeout(() => {
            isUpdating.value = false
            info.value = null
            close()
          }, 1500)
        } else if (st.phase === 'error') {
          stopPolling()
          message.error(st.message || '更新失败')
          isUpdating.value = false
        }
      } catch { /* 轮询失败忽略，下次继续 */ }
    }, 800)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '启动更新失败')
    isUpdating.value = false
  } finally {
    startingUpdate.value = false
  }
}

function reset() {
  stopPolling()
  loading.value = false
  error.value = ''
  info.value = null
  isUpdating.value = false
  startingUpdate.value = false
  progress.value = { running: false, phase: '', percent: 0, message: '', error: '' }
}

function close() {
  emit('update:show', false)
}

watch(() => props.show, (v) => {
  if (v && !info.value && !loading.value && !error.value) {
    check()
  }
})

onBeforeUnmount(stopPolling)
</script>

<style scoped>
.modal-scroll {
  max-height: max(140px, calc(100vh - 230px));
  overflow-y: auto;
  padding-right: 2px;
}
.center-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 0;
}
.version-compare {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-bottom: 12px;
}
.vc-item {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 12px;
  background: #fafafa;
}
.vc-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
}
.vc-value {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sha { font-family: Consolas, monospace; font-weight: bold; color: #1677ff; }
.msg { font-size: 12px; color: #333; }
.muted { color: #999; font-size: 12px; }
.vc-arrow {
  display: flex;
  align-items: center;
  font-size: 20px;
  color: #bbb;
  flex-shrink: 0;
}
.progress-card { margin-bottom: 12px; }
.phase-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.phase-msg {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  word-break: break-all;
}
.commit-section { margin-top: 4px; }
.release-section { margin-top: 4px; margin-bottom: 12px; }
.release-body {
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  color: #555;
  white-space: pre-wrap;
  word-break: break-word;
  background: #fafafa;
}
.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #666;
  margin-bottom: 6px;
}
.commit-list {
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
}
.commit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}
.commit-item:last-child { border-bottom: none; }
.commit-item:hover { background: #fafafa; }
.commit-item.is-latest { background: #fffbe6; }
.commit-item.is-current { background: #e6f4ff; }
.c-tag {
  flex-shrink: 0;
  font-size: 11px;
  color: #d46b08;
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 4px;
  padding: 0 4px;
}
.c-tag.current { color: #1677ff; background: #e6f4ff; border-color: #91caff; }
.c-sha { font-family: Consolas, monospace; color: #555; flex-shrink: 0; }
.c-msg {
  flex: 1;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.c-date { color: #999; flex-shrink: 0; font-size: 11px; }
.c-author { color: #888; flex-shrink: 0; font-size: 11px; }
</style>