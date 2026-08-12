<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  NButton,
  NCard,
  NEmpty,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NInputNumber,
  NModal,
  NSelect,
  NSpin,
  useMessage,
} from "naive-ui";
import { configApi, deviceApi, utilsApi } from "../api/client";

const props = defineProps<{ configId: string }>();
const message = useMessage();
const loading = ref(true);
const saving = ref<string | null>(null);

const settings = reactive<any>({
  调试模式: 0,
  控制模式: 0,
  串口: "",
  截图模式: 0,
  雷电安装路径: "",
  雷电实例索引: 0,
  MuMu安装路径: "",
  MuMu实例索引: 0,
  扫描间隔: 1000,
  二级密码: "",
});
// 已保存的键位（独立维护，不进入 reactive 的固定键集合）
const keymapSaved = ref<any[] | null>(null);
const CONTROL_MODES = [
  { label: "MiniTouch（高性能推荐）", value: 0 },
  { label: "U2", value: 1 },
];
const SCREEN_MODES = [
  { label: "DroidCastRaw", value: 0 },
  { label: "WindowCapture", value: 1 },
  { label: "U2", value: 2 },
  { label: "MuMu", value: 3 },
  { label: "LD", value: 4 },
];

function gv(k: string, d: any) {
  const v = settings[k];
  return v === undefined || v === null || v === "" ? d : v;
}
async function save(k: string, v: any) {
  saving.value = k;
  try {
    await configApi.updateSetting(props.configId, k, v);
    settings[k] = v;
  } catch (e: any) {
    message.error(
      `保存「${k}」失败：${e?.response?.data?.detail || e?.message || e}`,
    );
  } finally {
    saving.value = null;
  }
}
const debugMode = computed({
  get: () => !!gv("调试模式", 0),
  set: (v: boolean) => save("调试模式", v ? 1 : 0),
});
const controlMode = computed({
  get: () => gv("控制模式", 0),
  set: (v: number | null) => save("控制模式", v ?? 0),
});
const screenMode = computed({
  get: () => gv("截图模式", 0),
  set: (v: number | null) => {
    const m = v ?? 0;
    save("截图模式", m);
    // 选择了 MuMu/LD 截图模式但未设置安装路径时给出提示
    if (m === 3 && !gv("MuMu安装路径", "")) {
      message.warning("已选择 MuMu 截图模式，但尚未设置 MuMu 安装路径，请到「全局设置」页配置");
    } else if (m === 4 && !gv("雷电安装路径", "")) {
      message.warning("已选择 LD 截图模式，但尚未设置雷电安装路径，请到「全局设置」页配置");
    }
  },
});
// 串口格式校验：127.0.0.1:xxxxx 或 emulator-xxxx
function isValidSerial(v: string): boolean {
  const t = v.trim();
  if (!t) return false;
  if (/^(\d{1,3}\.){3}\d{1,3}:\d+$/.test(t)) return true;
  if (/^emulator-\d+$/i.test(t)) return true;
  return false;
}
const serialText = ref("");
function onSerialChange(v: string) {
  serialText.value = v || "";
}
function commitSerial() {
  const v = serialText.value.trim();
  if (!v) {
    serialText.value = gv("串口", "") || "";
    return;
  }
  if (!isValidSerial(v)) {
    message.error("串口格式不正确，应为 127.0.0.1:5555 或 emulator-5554 形式");
    serialText.value = gv("串口", "") || "";
    return;
  }
  serialText.value = v;
  save("串口", v);
}
function syncdSerial() {
  serialText.value = gv("串口", "") || "";
}
const serial = computed({
  get: () => serialText.value,
  set: (v: string) => onSerialChange(v),
});
syncdSerial();
const LDInstanceIndex = computed({
  get: () => gv("雷电实例索引", 0),
  set: (v: number | null) => save("雷电实例索引", v ?? 0),
});
const MuMuInstanceIndex = computed({
  get: () => gv("MuMu实例索引", 0),
  set: (v: number | null) => save("MuMu实例索引", v ?? 0),
});
const scanInterval = computed({
  get: () => gv("扫描间隔", 1000),
  set: (v: number | null) => save("扫描间隔", v ?? 1000),
});
const secondaryPassword = computed({
  get: () => gv("二级密码", ""),
  set: (v: string) => save("二级密码", v),
});

async function load() {
  loading.value = true;
  try {
    const res = await configApi.get(props.configId);
    const dic = res.data.setting_dics || {};
    Object.keys(settings).forEach((k) => {
      if (dic[k] !== undefined) settings[k] = dic[k];
    });
    keymapSaved.value = Array.isArray(dic["键位"]) ? dic["键位"] : null;
    // 配置加载完成后同步串口输入框（此前 setup 阶段 syncdSerial 时配置尚未加载）
    syncdSerial();
    // 若当前已选 MuMu/LD 截图模式但未配置安装路径，进入时给出提示
    const sm = gv("截图模式", 0);
    if (sm === 3 && !gv("MuMu安装路径", "")) {
      message.warning("已选择 MuMu 截图模式，但尚未设置 MuMu 安装路径，请到「全局设置」页配置");
    } else if (sm === 4 && !gv("雷电安装路径", "")) {
      message.warning("已选择 LD 截图模式，但尚未设置雷电安装路径，请到「全局设置」页配置");
    }
  } catch (e: any) {
    serialText.value = "";
  } finally {
    loading.value = false;
  }
}
onMounted(load);

// 串口列表弹窗
const serialModalShow = ref(false);
const serialLoading = ref(false);
const serialList = ref<string[]>([]);
const selectedSerial = ref("");
async function openSerialList() {
  serialModalShow.value = true;
  await fetchSerialList();
}
async function fetchSerialList() {
  serialLoading.value = true;
  try {
    const res = await deviceApi.serialList(props.configId);
    serialList.value = res.data.serials || [];
    selectedSerial.value = "";
  } catch (e: any) {
    message.error(
      `获取串口列表失败：${e?.response?.data?.detail || e?.message || e}`,
    );
    serialList.value = [];
  } finally {
    serialLoading.value = false;
  }
}
async function restartAdb() {
  serialLoading.value = true;
  try {
    const res = await deviceApi.restartAdb(props.configId);
    serialList.value = res.data.serials || [];
    selectedSerial.value = "";
    message.success("ADB 服务已重启");
  } catch (e: any) {
    message.error(
      `重启 ADB 失败：${e?.response?.data?.detail || e?.message || e}`,
    );
  } finally {
    serialLoading.value = false;
  }
}
function confirmSerial() {
  if (!selectedSerial.value) {
    message.warning("未选择任何串口");
    return;
  }
  serial.value = selectedSerial.value;
  save("串口", selectedSerial.value);
  serialModalShow.value = false;
}

// 键位配置弹窗（还原 KeyMapConfiguration.py）
const keymapModalShow = ref(false);
const keymapLoading = ref(false);
const screenImageUrl = ref("");
const screenWidth = ref(0);
const screenHeight = ref(0);
const keyPositions = ref<{ x: number; y: number }[]>([]);
const dragging = ref<{ id: number; offsetX: number; offsetY: number } | null>(
  null,
);
function jitterKeymap() {
  keyPositions.value = Array.from({ length: 10 }, () => ({ x: 0, y: 0 }));
  const saved = keymapSaved.value;
  if (Array.isArray(saved) && saved.length === 10) {
    saved.forEach((pos: any, i: number) => {
      // 与原版一致：按钮中心对准配置点，故减去按钮半径 25
      keyPositions.value[i] = {
        x: ((pos?.[0] ?? 0) * screenWidth.value) / 1600 - 25,
        y: ((pos?.[1] ?? 0) * screenHeight.value) / 900 - 25,
      };
    });
  }
}
async function openKeymap() {
  keymapModalShow.value = true;
  keymapLoading.value = true;
  try {
    const res = await deviceApi.screenshot(props.configId);
    screenImageUrl.value = res.data.image || "";
    const img = new Image();
    img.onload = () => {
      screenWidth.value = img.naturalWidth;
      screenHeight.value = img.naturalHeight;
      jitterKeymap();
      keymapLoading.value = false;
    };
    img.onerror = () => {
      message.error("截图加载失败");
      keymapLoading.value = false;
    };
    img.src = screenImageUrl.value;
  } catch (e: any) {
    message.error(
      `获取截图失败：${e?.response?.data?.detail || e?.message || e}`,
    );
    keymapLoading.value = false;
  }
}
function onKeydownStart(e: MouseEvent, id: number) {
  e.preventDefault();
  e.stopPropagation();
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
  dragging.value = {
    id,
    offsetX: e.clientX - rect.left,
    offsetY: e.clientY - rect.top,
  };
  const onMove = (ev: MouseEvent) => {
    if (!dragging.value || dragging.value.id !== id) return;
    const c = document.getElementById("keymap-container");
    if (!c) return;
    const cr = c.getBoundingClientRect();
    keyPositions.value[id] = {
      x: Math.max(
        0,
        Math.min(ev.clientX - cr.left - dragging.value.offsetX, cr.width - 50),
      ),
      y: Math.max(
        0,
        Math.min(ev.clientY - cr.top - dragging.value.offsetY, cr.height - 50),
      ),
    };
  };
  const onUp = () => {
    dragging.value = null;
    window.removeEventListener("mousemove", onMove);
    window.removeEventListener("mouseup", onUp);
  };
  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);
}
function confirmKeymap() {
  const result = keyPositions.value.map((p) => [
    Math.round(((p.x + 25) * 1600) / screenWidth.value),
    Math.round(((p.y + 25) * 900) / screenHeight.value),
  ]);
  keymapSaved.value = result;
  save("键位", result);
  keymapModalShow.value = false;
  message.success("键位已保存");
}
</script>

<template>
  <div class="assistant-settings">
    <n-spin :show="loading">
      <div class="settings-header">
        <h2 class="settings-title">⚙ 助手设置</h2>
        <span class="settings-sub"
          >以下配置保存在当前配置文件中，仅对当前配置生效</span
        >
      </div>

      <!-- 控制设置 -->
      <n-card class="settings-card" title="控制设置" size="small">
        <n-grid :cols="1" :x-gap="24" :y-gap="16">
          <n-grid-item>
            <!-- 控制模式：带标签，选择框与说明水平排列 -->
            <n-form-item label="控制模式" label-placement="left">
              <div class="control-mode-line">
                <n-select
                  v-model:value="controlMode"
                  :options="CONTROL_MODES"
                  :disabled="saving === '控制模式'"
                  style="width: 250px"
                />
                <span class="field-desc"
                  >控制模式决定了模拟器按键/触摸的注入方式（U2：性能适中；MiniTouch：高性能推荐）</span
                >
              </div>
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="串口" label-placement="left">
              <div class="form-control-line">
                <n-input
                  v-model:value="serial"
                  placeholder="127.0.0.1:5555"
                  style="width: 170px"
                  :disabled="saving === '串口'"
                  @blur="commitSerial"
                  @keyup.enter="commitSerial"
                />
                <n-button size="small" @click="openSerialList"
                  >串口列表</n-button
                >
                <span class="field-desc"
                  >请先打开自己的模拟器，自行分辨哪个串口是自己正在使用的模拟器的串口<br>该串口会被
                  DroidCastRaw 和 U2 共同使用</span
                >
              </div>
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-card>

      <!-- 截图设置 -->
      <n-card class="settings-card" title="截图设置" size="small">
        <n-grid :cols="1" :x-gap="24" :y-gap="16">
          <n-grid-item>
            <n-form-item label="截图模式" label-placement="left">
              <n-select
                v-model:value="screenMode"
                :options="SCREEN_MODES"
                :disabled="saving === '截图模式'"
                style="width: 220px"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item v-if="screenMode === 3">
            <div class="sub-panel">
              <div class="sub-title">MuMu 模拟器设置</div>
              <n-form-item label="MuMu实例索引" label-placement="left">
                <n-input-number
                  v-model:value="MuMuInstanceIndex"
                  :min="0"
                  :max="100000"
                  style="width: 80px"
                  :disabled="saving === 'MuMu实例索引'"
                  @update:value="save('MuMu实例索引', $event)"
                />
                <span class="field-desc" style="margin-left: 12px"
                  >实例索引为多开时对应的实例编号</span
                >
              </n-form-item>
            </div>
          </n-grid-item>
          <n-grid-item v-if="screenMode === 4">
            <div class="sub-panel">
              <div class="sub-title">雷电模拟器设置</div>
              <n-form-item label="雷电实例索引" label-placement="left">
                <n-input-number
                  v-model:value="LDInstanceIndex"
                  :min="0"
                  :max="100000"
                  style="width: 80px"
                  :disabled="saving === '雷电实例索引'"
                  @update:value="save('雷电实例索引', $event)"
                />
                <span class="field-desc" style="margin-left: 12px"
                  >实例索引为多开时对应的实例编号</span
                >
              </n-form-item>
            </div>
          </n-grid-item>
        </n-grid>
      </n-card>

      <!-- 调度设置 -->
      <n-card class="settings-card" title="调度设置" size="small">
        <n-form-item label="扫描间隔" label-placement="left">
          <n-input-number
            v-model:value="scanInterval"
            :min="50"
            :max="9999"
            :step="100"
            style="width: 140px"
            :disabled="saving === '扫描间隔'"
            @update:value="save('扫描间隔', scanInterval)"
          >
            <template #suffix>ms</template>
          </n-input-number>
          <span class="field-desc" style="margin-left: 16px"
            >间隔越小调度器扫描任务越频繁，一般 1000ms 足够</span
          >
        </n-form-item>
      </n-card>

      <!-- 连点键位 -->
      <n-card class="settings-card" title="连点键位" size="small">
        <div class="keymap-row">
          <span class="field-desc" style="flex: 1"
            >诸如丰饶之间、每日胜场等任务的必要设置。关闭调度器之后，进入练习场，点击「配置」将在弹出窗口中把技能按钮拖动到游戏画面对应键位上。</span
          >
          <n-button size="small" type="primary" secondary @click="openKeymap"
            >配置</n-button
          >
        </div>
      </n-card>

      <!-- 二级密码 -->
      <n-card class="settings-card" title="二级密码" size="small">
        <n-form-item label="二级密码" label-placement="left">
          <n-input
            v-model:value="secondaryPassword"
            type="password"
            show-password-on="click"
            :maxlength="6"
            placeholder="必须为六位"
            style="width: 120px"
            :disabled="saving === '二级密码'"
            @blur="save('二级密码', secondaryPassword)"
          />
          <span class="field-desc" style="margin-left: 16px"
            >用来自动执行一些需要二级密码的任务，只在本地存储</span
          >
        </n-form-item>
      </n-card>
    </n-spin>

    <!-- 串口列表弹窗（还原 SerialChoose.py）-->
    <n-modal
      v-model:show="serialModalShow"
      preset="card"
      title="串口列表"
      style="width: 350px"
      :bordered="false"
    >
      <n-spin :show="serialLoading">
        <div class="serial-modal-body">
          <div class="serial-list-box">
            <div
              v-for="s in serialList"
              :key="s"
              class="serial-item"
              :class="{ active: selectedSerial === s }"
              @click="selectedSerial = s"
            >
              {{ s }}
            </div>
            <n-empty
              v-if="!serialList.length"
              description="未找到已连接的 ADB 设备"
              size="small"
              style="padding: 24px 0"
            />
          </div>
          <div class="serial-actions">
            <n-button size="small" @click="restartAdb" :loading="serialLoading"
              >重启 Adb</n-button
            >
            <n-button
              size="small"
              type="primary"
              @click="confirmSerial"
              :disabled="!selectedSerial"
              >确定</n-button
            >
          </div>
        </div>
      </n-spin>
    </n-modal>

    <!-- 键位配置弹窗（还原 KeyMapConfiguration.py）-->
    <n-modal
      v-model:show="keymapModalShow"
      preset="card"
      title="键位配置"
      style="width: 80vw; max-width: 1200px"
      :bordered="false"
    >
      <n-spin :show="keymapLoading">
        <template v-if="screenImageUrl">
          <div class="keymap-scroll">
            <div class="keymap-body">
              <div
                id="keymap-container"
                class="keymap-container"
                :style="{
                  width: screenWidth + 'px',
                  height: screenHeight + 'px',
                }"
              >
                <img :src="screenImageUrl" alt="截图" class="keymap-bg" />
                <div
                  v-for="(pos, i) in keyPositions"
                  :key="i"
                  class="skill-btn"
                  :style="{ left: pos.x + 'px', top: pos.y + 'px' }"
                  @mousedown="onKeydownStart($event, i)"
                >
                  {{ i + 1 }}
                </div>
              </div>
            </div>
          </div>
          <div class="keymap-footer">
            <span class="field-desc"
            
              >
              1: 平A&nbsp;&nbsp;
              2: 子技能&nbsp;&nbsp;
              3: 二技能&nbsp;&nbsp;
              4:奥义&nbsp;&nbsp;
              5:左子技能&nbsp;&nbsp;
              6:右子技能&nbsp;&nbsp;
              7:替身&nbsp;&nbsp;
              8:秘卷&nbsp;&nbsp;
              9:通灵&nbsp;&nbsp;
              10:摇杆<br><br>
              拖动圆形按钮到游戏画面对应的键位上，点击「完成」保存<br>
              PS：截图可通过滚动条移动

            </span>
            <n-button size="small" type="primary" @click="confirmKeymap"
              >完成</n-button
            >
          </div>
        </template>
        <n-empty
          v-else-if="!keymapLoading"
          description="无法获取截图，请检查模拟器连接"
          style="padding: 40px 0"
        />
      </n-spin>
    </n-modal>
  </div>
</template>

<style scoped>
.assistant-settings {
  height: 100%;
  box-sizing: border-box;
  overflow-y: auto;
  padding: 16px 20px 24px;
}
.settings-header {
  margin-bottom: 16px;
}
.settings-title {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: #4c4c4c;
}
.settings-sub {
  font-size: 12px;
  color: #6d6d6d;
}
.settings-card {
  margin-bottom: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(255, 255, 255, 0.08) !important;
}

.settings-card :deep(.n-card-header) {
  padding: 12px 16px;
}
.settings-card :deep(.n-card-header__main) {
  font-size: 18px;
  font-weight: 600;
  color: #444444;
}
.settings-card :deep(.n-card__content) {
  padding: 16px;
}
.form-control-line {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.control-mode-line {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.field-desc {
  font-size: 12px;
  color: #777676;
  line-height: 1.6;
}
.keymap-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.sub-panel {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  padding: 12px 16px;
}
.sub-title {
  font-size: 13px;
  font-weight: 600;
  color: #c0c0c0;
  margin-bottom: 8px;
}
.serial-modal-body {
  display: flex;
  gap: 12px;
}
.serial-list-box {
  flex: 1;
  max-height: 320px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 8px;
}
.serial-item {
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
  font-family: Consolas, monospace;
  font-size: 14px;
  color: #444444;
  text-align: center;
  transition: background-color 0.2s;
  user-select: none;
}
.serial-item:hover {
  background: rgba(255, 255, 255, 0.08);
}
.serial-item.active {
  background: rgba(57, 197, 187, 0.25);
  color: #39c5bb;
}
.serial-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: flex-end;
}
.keymap-scroll {
  max-height: 60vh;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: #111;
}
.keymap-body {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
}
.keymap-side {
  flex-shrink: 0;
  min-width: 100px;
  border-left: 1px solid rgba(255, 255, 255, 0.15);
  padding-left: 16px;
}
.keymap-side .field-desc {
  color: #c8c8c8;
  white-space: nowrap;
  font-size: 13px;
}
.keymap-container {
  position: relative;
  cursor: crosshair;
  flex-shrink: 0;
}
.keymap-bg {
  display: block;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
.skill-btn {
  position: absolute;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(50, 150, 255, 0.55);
  border: 2px solid #fff;
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  user-select: none;
  z-index: 10;
  box-sizing: border-box;
}
.skill-btn:active {
  cursor: grabbing;
}
.keymap-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}
</style>