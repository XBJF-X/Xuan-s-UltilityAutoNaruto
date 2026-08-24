<template>
  <div class="dashboard">
    <div class="panel-left">
      <div class="custom-card">
        <div class="custom-card-header">
          <span>任务状态</span>
          <n-button
            size="tiny"
            @click="loadTaskStatus"
            :loading="loadingTasks"
            :disabled="!appStore.activeConfigId"
            >刷新</n-button
          >
        </div>
        <div class="custom-card-body">
          <div v-if="!appStore.activeConfigId" class="card-empty">
            <n-empty description="请先在左侧选择配置" />
          </div>
          <div v-else-if="sortedTaskList.length === 0" class="card-empty">
            <n-empty description="无任务数据" />
          </div>
          <div v-else class="task-list">
            <div
              v-for="t in sortedTaskList"
              :key="t.name"
              class="task-item"
              :class="['status-' + t.status, { failed: !!failedTasks[t.name] }]"
            >
              <div class="task-left">
                <div class="task-row1">
                  <span class="task-priority-tag" :class="'tag-' + t.status">{{
                    t.status === 0 ? "执行" : t.status === 1 ? "就绪" : "等待"
                  }}</span>
                  <span class="task-priority">{{
                    padPriority(t.priority)
                  }}</span>
                  <span class="task-name">{{ t.name }}</span>
                  <span v-if="failedTasks[t.name]" class="task-failed-tag" :title="failedTasks[t.name]">失败</span>
                </div>
                <div class="task-time">{{ formatNextExecute(t) }}</div>
              </div>
              <button
                class="task-execute-btn"
                @click="handleExecuteNow(t.name)"
              >
                执行
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="panel-right">
      <LogPanel :config-id="appStore.activeConfigId" title="实时日志" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useAppStore } from "@/stores/app";
import { schedulerApi } from "@/api/client";
import LogPanel from "@/components/LogPanel.vue";
import { useWebSocket } from "@/api/ws";

const appStore = useAppStore();
const loadingTasks = ref(false);
// 任务列表直接读 AppStore 中由 WS scheduler_snapshot 维护的状态快照（零轮询）
const taskList = computed(() => {
  const snap = appStore.schedulerSnapshots[appStore.activeConfigId as string];
  return snap?.tasks || [];
});
const failedTasks = ref<Record<string, string>>({});

// 通过 WebSocket 监听任务状态变化，自动刷新
const { onMessage } = useWebSocket();
const unsubTaskState = onMessage((msg) => {
  if (msg.type === "task_state" && msg.config_id === appStore.activeConfigId) {
    if (msg.action === "complete" && msg.name) {
      if (msg.error) {
        failedTasks.value[msg.name] = msg.error;
      } else {
        delete failedTasks.value[msg.name];
      }
    }
  }
  // scheduler_snapshot 已直接写入 AppStore，无需再拉取；
  // task_state / status 作为向后兼容（旧后端无 snapshot 推送）触发兜底刷新
  if (msg.type === "task_state" || msg.type === "status") {
    loadTaskStatus();
  }
});

// 低频兜底轮询（WS snapshot 推送为主，轮询仅防 ws 断连/漏消息）
let _pollTimer: ReturnType<typeof setInterval> | null = null;
function startPolling() {
  stopPolling();
  if (appStore.activeConfigId) {
    loadTaskStatus();
    _pollTimer = setInterval(() => loadTaskStatus(), 5000);
  }
}
function stopPolling() {
  if (_pollTimer) {
    clearInterval(_pollTimer);
    _pollTimer = null;
  }
}

watch(
  () => appStore.activeConfigId,
  () => {
    startPolling();
  },
);

function compareTasks(a: any, b: any) {
  if (a.status !== b.status) return a.status - b.status;
  if (a.next_execute !== b.next_execute) {
    if (a.next_execute && b.next_execute)
      return a.next_execute < b.next_execute ? -1 : 1;
    if (a.next_execute) return -1;
    if (b.next_execute) return 1;
  }
  if (a.priority !== b.priority) return a.priority - b.priority;
  if (a.base_priority !== b.base_priority)
    return a.base_priority - b.base_priority;
  return 0;
}

const sortedTaskList = computed(() =>
  [...taskList.value].filter((t) => t.activated !== false).sort(compareTasks),
);

/** 调试用：打印每次 API 返回的原始数据 */
watch(taskList, (val) => {
  if (val.length > 0) {
    console.debug(
      "[Dashboard] 任务列表原始数据:",
      JSON.stringify(
        val.map((t) => ({ name: t.name, activated: t.activated })),
      ),
    );
  }
});

function padPriority(p: number | null | undefined): string {
  const v = Math.max(-999, Math.min(999, p ?? 0));
  return "[" + v.toString() + "]";
}

function formatNextExecute(t: any) {
  if (!t.next_execute) return "下次执行：-";
  const parts = t.next_execute.split(" ");
  const dateStr = parts[0];
  const timeStr = parts[1] || "";
  if (!dateStr) return "下次执行：-";
  return "下次执行：" + dateStr + " " + timeStr;
}

async function loadTaskStatus() {
  if (!appStore.activeConfigId) {
    return;
  }
  // 切换配置中：Layout 正等待后端请求结束，跳过本次刷新，避免竞态/重复请求
  if (appStore.configSwitching) return;
  loadingTasks.value = true;
  try {
    const res = await schedulerApi.getTasks(appStore.activeConfigId);
    const raw = res.data || [];
    // 统一写入 AppStore 快照（ws scheduler_snapshot 持续覆盖，本轮询仅作兜底）
    const prev = appStore.schedulerSnapshots[appStore.activeConfigId] || {
      running: false,
      mode: "persistent",
    };
    appStore.schedulerSnapshots[appStore.activeConfigId] = { ...prev, tasks: raw };
  } catch {
    // 拉取失败保留现有快照，不覆盖
  } finally {
    loadingTasks.value = false;
  }
}

async function handleExecuteNow(taskName: string) {
  if (!appStore.activeConfigId) return;
  try {
    await schedulerApi.executeTask(appStore.activeConfigId, taskName);
  } catch {}
}

onMounted(() => {
  startPolling();
});
onUnmounted(() => {
  unsubTaskState();
  stopPolling();
});
</script>

<style scoped>
.dashboard {
  height: 100%;
  display: flex;
  gap: 12px;
  padding: 8px;
  overflow: hidden;
}
.panel-left {
  flex: 1;
  min-width: 350px;
  max-width: 350px;
  display: flex;
  flex-direction: column;
}
.panel-right {
  flex: 2;
  min-width: 0;
}
.custom-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}
.custom-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  font-size: 17px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
  background: #fafafa;
}
.custom-card-body {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding: 8px;
}
.card-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 14px;
  background: #f8f9fa;
  border: 1px solid #e8e8e8;
  border-left: 4px solid #bbb;
  border-radius: 6px;
  transition: all 0.15s ease;
}
.task-item:hover {
  background: #f0f1f3;
  border-color: #ddd;
}
.task-item.status-0 {
  border-left-color: #52c41a;
  background: #f6ffee;
}
.task-item.status-1 {
  border-left-color: #faad14;
  background: #fffbe6;
}
.task-item.status-2 {
  border-left-color: #bbb;
}
.task-item.failed {
  border-left-color: #e53935;
  background: #fff1f0;
}
.task-failed-tag {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: #e53935;
  padding: 1px 6px;
  border-radius: 8px;
  flex-shrink: 0;
  cursor: help;
  margin-left: 6px;
}
.task-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}
.task-row1 {
  display: flex;
  align-items: center;
  gap: 0px;
  min-width: 0;
}
.task-priority-tag {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
  flex-shrink: 0;
  color: #fff;
}
.tag-0 {
  background: #52c41a;
}
.tag-1 {
  background: #faad14;
}
.tag-2 {
  background: #bbb;
}
.task-priority {
  font-size: 12px;
  color: #888;
  font-weight: 700;
  flex-shrink: 0;
  font-family: "Consolas", monospace;
  min-width: 3em;
  text-align: right;
}
.task-name {
  font-size: 17px;
  color: #333;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.task-time {
  font-size: 14px;
  color: #999;
  padding-left: 4px;
}
.task-execute-btn {
  font-size: 17px;
  font-weight: 700;
  background: transparent;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 6px 14px;
  border-radius: 4px;
  flex-shrink: 0;
  transition: all 0.15s;
  align-self: center;
}
.task-execute-btn:hover {
  color: #1677ff;
  background: #e6f4ff;
}
.task-execute-btn:active {
  background: #bae0ff;
}
</style>
