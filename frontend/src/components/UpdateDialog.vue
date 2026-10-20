<template>
  <n-modal
    v-model:show="showModel"
    preset="card"
    title="检查更新"
    style="width: min(1400px, calc(100vw - 32px))"
    :mask-closable="!isUpdating"
    :closable="!isUpdating"
    @after-leave="reset"
  >
    <!-- 内容区按当前视图高度限制并内部滚动：小窗口下页脚（关闭/立即更新）不被挤出窗口外 -->
    <div class="modal-scroll">
    <!-- 当前客户端版本（根目录 _version.py，经 /utils/version 读取，不依赖更新源）：
         放在正文顶部，检查中/检查失败/已是最新 三种状态都可见 -->
    <div v-if="localVersion" class="version-badge">
      <span class="vb-label">当前客户端版本</span>
      <span class="vb-value">v{{ localVersion }}</span>
    </div>

    <!-- 拉取分支：默认 v17（稳定分支）；切到其它分支必须等待 10 秒确认（开发者测试用） -->
    <div class="branch-row">
      <span class="br-label">更新分支</span>
      <n-select
        class="br-select"
        size="small"
        :value="branch"
        :options="branchOptions"
        :disabled="isUpdating || loading"
        filterable
        tag
        placeholder="选择或输入分支名"
        @update:value="requestBranchChange"
      />
      <n-tag v-if="branch !== DEFAULT_BRANCH" type="warning" size="small">开发者测试</n-tag>
    </div>
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
          <div class="vc-label">云端最新（{{ info.branch || branch }}）</div>
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
              {{ progressTitle }}
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

      <!-- 提交历史与本地回滚包统一在弹窗底部同一列表展示（见下方 commit-section） -->
    </template>


    <!-- 提交历史 + 本地回滚包：融合在同一列表（带本地包的提交直接显示「回滚」；
         云端历史未覆盖到的更早提交/快照作为「本地包」行追加，保证所有可回滚项都可见） -->
    <div v-if="!loading" class="commit-section">
      <div class="section-title">
        <template v-if="info">
          提交历史（{{ info.branch || branch }} · 右侧可「拉取」任意提交；带本地包的提交可「回滚」）
        </template>
        <template v-else>本地可用回滚包（离线可用，不依赖网络）</template>
      </div>
      <div class="commit-list">
        <div
          v-for="c in commitRows"
          :key="c.sha"
          class="commit-item"
          :class="{
            'is-latest': c.sha === latestSha,
            'is-current': c.sha === currentSha,
          }"
        >
          <span class="c-tag" v-if="c.sha === latestSha">最新</span>
          <span class="c-tag current" v-else-if="c.sha === currentSha">本地</span>
          <span class="c-sha">{{ c.short_sha }}</span>
          <!-- 悬浮显示完整提交消息（列表里是首行 + 省略号） -->
          <n-tooltip placement="top-start" :style="{ maxWidth: '720px' }">
            <template #trigger>
              <span class="c-msg">{{ c.message }}</span>
            </template>
            <div style="white-space: pre-wrap; word-break: break-word; max-height: 320px; overflow-y: auto;">
              {{ c.full_message || c.message }}
            </div>
          </n-tooltip>
          <span class="c-date">{{ formatDate(c.date) }}</span>
          <span class="c-author">{{ c.author }}</span>
          <n-button
            v-if="packageMap.has(c.sha) && c.sha !== currentSha"
            size="tiny"
            tertiary
            type="warning"
            class="c-rollback"
            :loading="rollingBackSha === c.sha"
            :disabled="isUpdating && rollingBackSha !== c.sha"
            @click.stop="confirmRollback(c.sha, c.short_sha)"
          >
            回滚
          </n-button>
          <n-button
            size="tiny"
            tertiary
            type="primary"
            class="c-pull"
            :loading="pullingSha === c.sha"
            :disabled="isUpdating && pullingSha !== c.sha"
            @click.stop="apply(c.sha)"
          >
            拉取
          </n-button>
        </div>

        <!-- 云端历史未覆盖到的本地回滚包（更早的提交 / 更新前快照），同样可回滚 -->
        <div
          v-for="p in orphanPackages"
          :key="'pkg-' + p.sha"
          class="commit-item is-local-pkg"
          :class="{ 'is-current': p.is_current }"
        >
          <span class="c-tag pkg">本地包</span>
          <span class="c-tag current" v-if="p.is_current">当前</span>
          <span class="c-sha">{{ p.short_sha }}</span>
          <n-tooltip placement="top-start" :style="{ maxWidth: '720px' }">
            <template #trigger>
              <span class="c-msg">{{ p.message || (p.kind === 'snapshot' ? '更新前快照' : '已下载更新包') }}</span>
            </template>
            <div style="white-space: pre-wrap; word-break: break-word;">
              {{ p.kind === 'snapshot' ? '更新前快照（离线回滚包）' : '已下载更新包（离线回滚包）' }}
              保存于 {{ formatDate(p.saved_at) }}，共 {{ formatSize(p.size) }}。
            </div>
          </n-tooltip>
          <span class="c-date">{{ formatDate(p.saved_at) }}</span>
          <span class="c-date">{{ formatSize(p.size) }}</span>
          <n-button
            size="tiny"
            tertiary
            type="warning"
            class="c-rollback"
            :loading="rollingBackSha === p.sha"
            :disabled="p.is_current || (isUpdating && rollingBackSha !== p.sha)"
            @click.stop="confirmRollback(p.sha, p.short_sha)"
          >
            回滚
          </n-button>
        </div>

        <n-empty
          v-if="!commitRows.length && !orphanPackages.length"
          description="暂无可展示的提交或回滚包"
          size="small"
          style="padding: 12px 0;"
        />
      </div>
      <n-text depth="3" style="font-size: 12px;">
        回滚不依赖网络：直接用本机保存的更新包覆盖代码，完成后自动热重启。
        <template v-if="packages.length">
          （本机保留 {{ packages.length }}/{{ maxPackages }} 个包，共 {{ formatSize(totalSize) }}）
        </template>
      </n-text>
    </div>
    </div>

    <!-- 非稳定分支切换确认：强制等待 10 秒（防误触；开发者测试用） -->
    <n-modal
      v-model:show="branchConfirm.show"
      preset="card"
      title="切换到开发者测试分支？"
      style="width: min(460px, calc(100vw - 48px))"
      :mask-closable="false"
      :closable="true"
      @after-leave="cancelBranchConfirm"
    >
      <n-alert type="warning" :show-icon="true" style="margin-bottom: 12px;">
        开发者测试使用，普通用户使用v17稳定分支即可
      </n-alert>
      <n-text depth="3" style="font-size: 12px; line-height: 1.7;">
        即将切换到分支 <b>{{ branchConfirm.target }}</b>。该分支可能包含未经验证的改动，
        拉取后程序会自动重启；如需回到稳定版，重新选择 {{ DEFAULT_BRANCH }} 再拉取即可。
      </n-text>
      <template #footer>
        <n-space justify="end">
          <n-button size="small" @click="cancelBranchConfirm">取消</n-button>
          <n-button
            size="small"
            type="warning"
            :disabled="branchConfirm.countdown > 0"
            @click="confirmBranchConfirm"
          >
            {{ branchConfirm.countdown > 0 ? `请等待 ${branchConfirm.countdown} 秒` : '确认切换' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

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
import { ref, computed, watch, onBeforeUnmount, h } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { utilsApi } from '@/api/client'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const showModel = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const error = ref('')
const info = ref<any>(null)
// 更新分支：默认 v17（稳定分支）。dev 等开发者测试分支切换前必须等待 10 秒确认；
// 后端只接受单段简单分支名（字母/数字/点/下划线/短横线，不含 "/" 与 ".."）。
const DEFAULT_BRANCH = 'v17'
const BRANCH_CONFIRM_SECONDS = 10
const BRANCH_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$/
const branch = ref(DEFAULT_BRANCH)
const branchOptions = [
  { label: 'v17（稳定分支，推荐）', value: 'v17' },
  { label: 'dev（开发者测试）', value: 'dev' },
  { label: 'master（旧版主线）', value: 'master' },
]
// 非稳定分支切换确认框：倒计时结束前「确认切换」按钮禁用
const branchConfirm = ref({ show: false, target: '', countdown: 0 })
let branchTimer: ReturnType<typeof setInterval> | null = null
// 当前客户端版本（根目录 _version.py）：与更新源无关，弹窗打开即读取
const localVersion = ref('')
const isUpdating = ref(false)
const startingUpdate = ref(false)
// 正在拉取指定 commit 的 sha（用于该行按钮 loading；允许当前已是最新时重拉/回退）
const pullingSha = ref('')
// 正在回滚的 sha（本地更新包）
const rollingBackSha = ref('')
// 本机保留的热更新包（离线回滚候选）
const packages = ref<any[]>([])
const maxPackages = ref(5)
const totalSize = ref(0)
// sha -> 包信息（用于在云端提交历史行上显示「回滚」）
const packageMap = computed(() => {
  const map = new Map<string, any>()
  for (const p of packages.value) map.set(String(p.sha), p)
  return map
})
// 提交列表数据源：检查失败（info 为空）时只显示本地回滚包，回滚入口不依赖网络
const commitRows = computed<any[]>(() =>
  Array.isArray(info.value?.commits) ? info.value.commits : [])
const latestSha = computed(() => String(info.value?.latest_sha || ''))
const currentSha = computed(() => String(info.value?.current_sha || ''))
// 云端提交历史未覆盖到的本地回滚包（更早的提交 / 更新前快照）：追加到同一列表，
// 保证「本机所有可回滚的提交」都看得到（回滚包最多 5 个，不会超出 50 行上限）
const orphanPackages = computed(() => {
  const known = new Set(commitRows.value.map((c: any) => String(c.sha)))
  return packages.value.filter((p: any) => !known.has(String(p.sha)))
})
const progress = ref<{
  running: boolean
  mode: string
  targetSha: string
  phase: string
  percent: number
  message: string
  error: string
}>({
  running: false, mode: '', targetSha: '', phase: '', percent: 0, message: '', error: '',
})

let pollTimer: ReturnType<typeof setInterval> | null = null

const phaseLabel = computed(() => {
  const map: Record<string, string> = {
    downloading: '下载更新包',
    extracting: '解压更新包',
    replacing: '替换文件',
    'verifying-files': '校验文件覆盖',
    'writing-version': '更新版本记录',
    'downloading-installer': '下载安装包',
    verifying: '校验安装包',
    done: '更新完成',
    error: '更新失败',
  }
  return map[progress.value.phase] || '准备中'
})

// 进度标题：回滚时切换文案（更新沿用 phaseLabel）
const progressTitle = computed(() => {
  if (progress.value.mode !== 'rollback') return phaseLabel.value
  const sha = progress.value.targetSha ? progress.value.targetSha.slice(0, 7) : ''
  if (progress.value.phase === 'done') return '回滚完成'
  if (progress.value.phase === 'error') return '回滚失败'
  return sha ? `正在回滚到 ${sha}` : '正在回滚'
})

function formatDate(iso: string) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { hour12: false })
  } catch { return iso }
}

function formatSize(bytes: number) {
  const size = Number(bytes) || 0
  if (size <= 0) return '0 B'
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(0)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`
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

// 读取本地客户端版本：GET /utils/version 只读根目录 _version.py，不访问更新源，
// 因此即使更新源（GitHub/Gitee）不可达、"检查更新失败"页面上也能看到当前版本
async function loadLocalVersion() {
  try {
    const res = await utilsApi.localVersion()
    const v = res.data?.version
    if (v) localVersion.value = v
  } catch (e) {
    // 外部依赖不可控（后端未就绪/请求失败）：降级为不显示版本号，不影响弹窗其余功能
    console.warn('[UpdateDialog] 读取当前版本失败', e)
  }
}

// 读取本机保留的更新包（离线回滚候选）：不访问网络，检查更新失败时也照常展示
async function loadPackages() {
  try {
    const res = await utilsApi.updatePackages()
    const data = res.data
    if (data?.ok === false) {
      console.warn('[UpdateDialog] 读取更新包列表失败', data?.message)
      return
    }
    packages.value = Array.isArray(data?.packages) ? data.packages : []
    maxPackages.value = Number(data?.max_packages) || 5
    totalSize.value = Number(data?.total_size) || 0
  } catch (e) {
    // 后端未就绪/接口不可用：降级为不显示回滚入口（其余功能不受影响）
    console.warn('[UpdateDialog] 读取更新包列表失败', e)
  }
}

async function check() {
  loading.value = true
  error.value = ''
  info.value = null
  try {
    const res = await utilsApi.checkUpdate(branch.value)
    const data = res.data
    // check-update 顶层也带 local_version（含失败分支），拿到就同步显示
    if (data?.local_version) localVersion.value = data.local_version
    if (!data?.ok) {
      error.value = data?.message || '检查更新失败'
      return
    }
    // 后端回显实际使用的分支（未指定时为默认 v17）
    if (data?.branch) branch.value = data.branch
    info.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '网络请求失败'
  } finally {
    loading.value = false
  }
}

function stopBranchTimer() {
  if (branchTimer) { clearInterval(branchTimer); branchTimer = null }
}

function closeBranchConfirm() {
  stopBranchTimer()
  branchConfirm.value.show = false
  branchConfirm.value.countdown = 0
}

// 选择分支：切回稳定分支直接生效；切到其它分支必须先等满 10 秒再确认
function requestBranchChange(value: unknown) {
  const next = String(value ?? '').trim()
  if (!next || next === branch.value) return
  if (!BRANCH_PATTERN.test(next) || next.includes('..') || next.endsWith('.lock')) {
    message.warning('分支名只能包含字母、数字、点、下划线和短横线')
    return
  }
  if (next === DEFAULT_BRANCH) {
    closeBranchConfirm()
    branch.value = next
    void check()
    return
  }
  stopBranchTimer()
  branchConfirm.value = { show: true, target: next, countdown: BRANCH_CONFIRM_SECONDS }
  branchTimer = setInterval(() => {
    const left = branchConfirm.value.countdown - 1
    branchConfirm.value.countdown = left > 0 ? left : 0
    if (left <= 0) stopBranchTimer()
  }, 1000)
}

function cancelBranchConfirm() {
  closeBranchConfirm()
}

function confirmBranchConfirm() {
  if (branchConfirm.value.countdown > 0) return
  const next = branchConfirm.value.target
  closeBranchConfirm()
  if (!next) return
  branch.value = next
  void check()
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

async function apply(targetSha?: string) {
  // 只有字符串才算「拉取指定 commit」；页脚 @click 不会传参
  const sha = typeof targetSha === 'string' && targetSha ? targetSha : ''
  isUpdating.value = true
  startingUpdate.value = true
  pullingSha.value = sha
  try {
    // 指定 commit → 拉取该提交；大更新走 Release 安装包；其余走所选分支的 zipball
    let res
    if (sha) {
      res = await utilsApi.applyUpdate(sha, branch.value)
    } else if (info.value?.update_type === 'full') {
      res = await utilsApi.applyReleaseUpdate()
    } else {
      res = await utilsApi.applyUpdate(undefined, branch.value)
    }
    if (!res.data?.ok) {
      message.error(res.data?.message || '启动更新失败')
      isUpdating.value = false
      pullingSha.value = ''
      return
    }
    startStatusPolling()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '启动更新失败')
    isUpdating.value = false
    pullingSha.value = ''
  } finally {
    startingUpdate.value = false
  }
}

// 状态轮询（更新 / 回滚共用）：优先读 /update-status；该接口不可用时退回 /rollback-status
function startStatusPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    try {
      let st: any = null
      try {
        st = (await utilsApi.updateStatus()).data
      } catch {
        st = (await utilsApi.rollbackStatus()).data
      }
      if (!st) return
      const isRollback = st.mode === 'rollback'
      progress.value = {
        running: !!st.running,
        mode: st.mode || '',
        targetSha: st.target_sha || '',
        phase: st.phase || '',
        percent: st.percent ?? 0,
        message: st.message || '',
        error: st.error || '',
      }
      if (st.phase === 'done') {
        stopPolling()
        message.success(st.message || (isRollback ? '回滚完成' : '更新完成'))
        // 稍等让用户看到完成状态
        setTimeout(() => {
          isUpdating.value = false
          pullingSha.value = ''
          rollingBackSha.value = ''
          info.value = null
          close()
        }, 1500)
      } else if (st.phase === 'error') {
        stopPolling()
        message.error(st.message || (isRollback ? '回滚失败' : '更新失败'))
        isUpdating.value = false
        pullingSha.value = ''
        rollingBackSha.value = ''
      }
    } catch { /* 轮询失败忽略，下次继续 */ }
  }, 800)
}

function confirmRollback(sha: string, shortSha: string) {
  dialog.warning({
    title: `回滚到 ${shortSha}？`,
    content: () => h('div', { style: 'white-space: pre-line; line-height: 1.7;' }, [
      '· 回滚不依赖网络，直接使用本机保存的更新包',
      '· 会用该包内容覆盖当前代码，完成后自动热重启',
      '· 本地未提交的源码改动会被覆盖',
      '· 不会删除较新版本新增的文件',
    ].join('\n')),
    positiveText: '确认回滚',
    negativeText: '取消',
    onPositiveClick: () => { void doRollback(sha) },
  })
}

async function doRollback(sha: string) {
  isUpdating.value = true
  startingUpdate.value = true
  rollingBackSha.value = sha
  try {
    const res = await utilsApi.rollback(sha)
    if (!res.data?.ok) {
      message.error(res.data?.message || '启动回滚失败')
      isUpdating.value = false
      rollingBackSha.value = ''
      return
    }
    startStatusPolling()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '回滚请求失败')
    isUpdating.value = false
    rollingBackSha.value = ''
  } finally {
    startingUpdate.value = false
  }
}

function reset() {
  stopPolling()
  // 重新打开时回到默认稳定分支（开发者每次需重新显式选择测试分支）
  closeBranchConfirm()
  branch.value = DEFAULT_BRANCH
  loading.value = false
  error.value = ''
  info.value = null
  isUpdating.value = false
  startingUpdate.value = false
  pullingSha.value = ''
  rollingBackSha.value = ''
  progress.value = {
    running: false, mode: '', targetSha: '', phase: '', percent: 0, message: '', error: '',
  }
}

function close() {
  emit('update:show', false)
}

watch(() => props.show, (v) => {
  if (!v) return
  loadLocalVersion()
  // 更新包列表与云端检查并行：断网时仍能看到/使用本地回滚包
  loadPackages()
  if (!info.value && !loading.value && !error.value) {
    check()
  }
})

onBeforeUnmount(() => {
  stopPolling()
  stopBranchTimer()
})
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
.branch-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.branch-row .br-label {
  flex-shrink: 0;
  font-size: 12px;
  color: #888;
}
.branch-row .br-select {
  flex: 1;
  min-width: 0;
}
.version-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 6px 10px;
  border: 1px solid #e6f4ff;
  border-radius: 8px;
  background: #f0f8ff;
}
.version-badge .vb-label {
  font-size: 12px;
  color: #888;
}
.version-badge .vb-value {
  font-family: Consolas, monospace;
  font-weight: bold;
  color: #1677ff;
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
.commit-section { margin-top: 12px; }
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
  /* 最多 50 行（行高 28px）：云端 20 条提交 + 本机 ≤5 个回滚包能一次展示完，
     避免可回滚的 commit 被过矮的列表高度挤掉；只有超出 50 行才内部滚动 */
  --commit-row-h: 28px;
  max-height: calc(var(--commit-row-h) * 50);
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
}
.commit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: var(--commit-row-h);
  box-sizing: border-box;
  padding: 4px 10px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}
.commit-item:last-child { border-bottom: none; }
.commit-item:hover { background: #fafafa; }
.commit-item.is-latest { background: #fffbe6; }
.commit-item.is-current { background: #e6f4ff; }
.commit-item.is-local-pkg { background: #fcfcfc; }
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
.c-tag.pkg { color: #722ed1; background: #f9f0ff; border-color: #d3adf7; }
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
.c-pull { flex-shrink: 0; }
.c-rollback { flex-shrink: 0; }
</style>