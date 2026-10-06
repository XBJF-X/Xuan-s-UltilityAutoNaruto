# -*- coding: utf-8 -*-
"""阶段 5 回归：Layout.vue 拆分 composable 的结构不变量

背景：Layout.vue 的 `<script setup>` 原本 503 行、混着四件事（配置 CRUD / 任务树 /
调度器启停 / 启动检查）。本轮把后三块抽到 `frontend/src/composables/`：

- `useTaskTree.ts`     任务数据与分组（rawTasks / taskGroups / loadTaskData / onTaskEnabledChanged）
- `useSchedulerControl.ts` 启停 + status/scheduler_snapshot 的 WS 订阅（含自动退订）
- `useStartupChecks.ts` 引导 / 依赖检查 / 自动更新 / 截图 / 反馈入口
- `useScreenshotLimitAlerts.ts` 截图超限提醒（每日截图上限）的 WS 订阅（含自动退订）

本脚本钉住：
1. 三个 composable 存在且导出预期 API（正则级，避免 node 侧要装 vue/naive-ui）；
2. Layout.vue 已不再包含这些实现（防回退成"又抄一份"）；
3. Layout.vue **仍保留**它自己该有的部分：`openResourceGraph`（router 依赖）与
   `onMounted` 里对三项启动检查的编排 —— 本轮抽取时这两处曾被误删，必须有测试兜住。
"""
import re
import sys
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

COMPOSABLES = _PROJECT_ROOT / "frontend" / "src" / "composables"
LAYOUT = _PROJECT_ROOT / "frontend" / "src" / "views" / "Layout.vue"


def _strip_block_comments(code: str) -> str:
    """去掉 /* ... */ 块注释（含 JSDoc 文档字符串）：说明文字里会提到被抽取的符号名"""
    out = []
    depth = 0
    i = 0
    while i < len(code):
        if code.startswith("/*", i):
            depth += 1
            i += 2
            continue
        if code.startswith("*/", i) and depth:
            depth -= 1
            i += 2
            continue
        if depth == 0:
            out.append(code[i])
        i += 1
    return "".join(out)

EXPECTED_API = {
    "useTaskTree.ts": ["rawTasks", "taskSchema", "showDisabledTasks", "taskGroups",
                       "enabledTaskNames", "allTasks", "loadTaskData",
                       "onTaskEnabledChanged", "export function useTaskTree"],
    "useSchedulerControl.ts": ["schedulerRunning", "schedulerStarting", "toggleScheduler",
                               "startScheduler", "stopScheduler", "onBeforeUnmount",
                               "export function useSchedulerControl"],
    "useStartupChecks.ts": ["showUpdateDialog", "showFeedbackDialog", "showStartupNotice",
                            "checkStartupNotice", "checkDependencyOnStart",
                            "checkUpdateOnStart", "handleStartupGoFeedback",
                            "handleScreenshot", "openFeedback",
                            "export function useStartupChecks"],
    "useConfigs.ts": ["configTab", "filteredConfigs", "createDialogType", "createDialogTitle",
                      "configContextMenu", "configContextOptions", "selectConfig",
                      "switchConfigTab", "openCreateDialog", "handleCreateConfig",
                      "handleDuplicateConfig", "handleRenameConfig", "handleDeleteConfig",
                      "watch(() => appStore.activeConfigId",
                      "export function useConfigs"],
    # 截图超限提醒（每日截图上限）：弹窗队列 + WS 订阅（同样是 Layout 派生的派生状态）
    "useScreenshotLimitAlerts.ts": ["screenshotAlerts", "consumeScreenshotAlert",
                                    "onScreenshotLimit", "useWebSocket()",
                                    "onBeforeUnmount",
                                    "export function useScreenshotLimitAlerts"],
}

# Layout.vue 里不该再出现的实现（已搬进 composable）
MOVED_IMPLEMENTATIONS = [
    "const rawTasks = ref",
    "async function loadTaskData",
    "async function startScheduler",
    "async function stopScheduler",
    "async function toggleScheduler",
    "async function checkStartupNotice",
    "async function checkDependencyOnStart",
    "async function checkUpdateOnStart",
    "async function handleScreenshot",
    "function openFeedback",
    "useWebSocket(",
    "const configTab = ref",
    "const filteredConfigs = computed",
    "const configContextMenu = ref",
    "async function selectConfig",
    "function switchConfigTab",
    "function openCreateDialog",
    "async function handleCreateConfig",
    "function handleDuplicateConfig",
    "function handleRenameConfig",
    "function handleDeleteConfig",
]


class ComposablesExistTest(unittest.TestCase):

    def test_files_and_api(self):
        for filename, names in EXPECTED_API.items():
            path = COMPOSABLES / filename
            with self.subTest(file=filename):
                self.assertTrue(path.exists(), f"缺少 {filename}")
                src = path.read_text(encoding="utf-8")
                for name in names:
                    self.assertIn(name, src, f"{filename} 缺少 {name}")

    def test_composables_are_imported_by_layout(self):
        src = LAYOUT.read_text(encoding="utf-8")
        for name in ("useTaskTree", "useSchedulerControl", "useStartupChecks", "useConfigs",
                     "useScreenshotLimitAlerts"):
            with self.subTest(composable=name):
                self.assertIn(f"import {{ {name} }} from '@/composables/{name}'", src)
                self.assertIn(f"}} = {name}(", src)

    def test_use_configs_receives_injected_hooks(self):
        """useConfigs 不得反向依赖其它 composable：耦合必须通过回调注入"""
        comp = (COMPOSABLES / "useConfigs.ts").read_text(encoding="utf-8")
        self.assertIn("export interface UseConfigsOptions", comp)
        for hook in ("switchToOverview", "loadTaskData", "schedulerRunning"):
            self.assertIn(hook, comp, f"useConfigs 缺少注入项 {hook}")
        # 去掉注释与文档字符串后再查（说明文字里会提到其它 composable 的名字）
        code = _strip_block_comments(comp)
        code = "\n".join(line.split("//", 1)[0] for line in code.splitlines())
        self.assertNotIn("useTaskTree", code, "不得直接调用其它 composable")
        self.assertNotIn("useSchedulerControl", code)
        # Layout 侧必须把三项回调都传进去
        src = LAYOUT.read_text(encoding="utf-8")
        for hook in ("switchToOverview:", "loadTaskData,", "schedulerRunning,"):
            self.assertIn(hook, src, f"Layout 未注入 {hook}")

    def test_scheduler_ws_subscription_lives_in_composable(self):
        """WS 订阅（含退订）必须只在 composable 里，避免双份订阅"""
        comp = (COMPOSABLES / "useSchedulerControl.ts").read_text(encoding="utf-8")
        self.assertIn("useWebSocket()", comp)
        self.assertIn("onBeforeUnmount", comp)
        self.assertIn("unsubSchedulerStatus()", comp)
        self.assertIn("applySnapshot", comp, "快照必须走唯一写入口")


class LayoutNoRegressionTest(unittest.TestCase):

    def setUp(self):
        self.src = LAYOUT.read_text(encoding="utf-8")

    def test_moved_code_is_gone(self):
        for snippet in MOVED_IMPLEMENTATIONS:
            with self.subTest(snippet=snippet):
                self.assertNotIn(snippet, self.src, f"{snippet} 应已移入 composable")

    def test_layout_keeps_own_responsibilities(self):
        # 本轮抽取时这两处曾被误删（router 依赖 + 启动编排），必须有断言兜住
        self.assertIn("function openResourceGraph()", self.src)
        self.assertIn("router.resolve({ name: 'ResourceGraph' })", self.src)
        self.assertIn("onMounted(() => {", self.src)
        for call in ("appStore.checkBackendHealth()", "appStore.loadConfigs()",
                     "checkDependencyOnStart()", "checkUpdateOnStart()",
                     "checkStartupNotice()"):
            self.assertIn(call, self.src, f"onMounted 必须仍调用 {call}")

    def test_no_leftover_unused_imports(self):
        """抽取后不应留下只在 import 里出现的符号（曾残留 utilsApi/deviceApi/settingsApi/useDialog）"""
        for name in ("utilsApi", "deviceApi", "settingsApi", "useDialog",
                     "onBeforeUnmount", "useWebSocket"):
            with self.subTest(symbol=name):
                occurrences = len(re.findall(r"(?<![\w.])" + name + r"(?![\w])", self.src))
                self.assertEqual(occurrences, 0, f"{name} 不应再出现在 Layout.vue")

    def test_layout_script_smaller_than_before(self):
        """抽取四块后 script 段应显著变小（重构前 503 行 → 三块时 277 行 → 四块后 ~110 行）"""
        script = self.src[self.src.index("<script"):self.src.index("</script>")]
        lines = len(script.splitlines())
        self.assertLess(lines, 200, f"Layout script 段仍偏大：{lines} 行")
        self.assertGreater(lines, 60, "script 段过小，可能误删了 Layout 自身职责")
        # Layout 自身该留下的东西（视图切换 + 样板编排）必须还在
        for own in ("function switchToGlobalLog", "function switchToOverview",
                    "function switchToTask", "function switchToAssistant",
                    "function switchToSetting", "onMounted("):
            self.assertIn(own, self.src, f"Layout 自身职责缺失：{own}")

    def test_template_still_wired(self):
        """模板仍在消费 composable 暴露的状态（防止"抽走了但没人用"）"""
        for binding in ("openResourceGraph", "schedulerRunning", "schedulerStarting",
                        "taskGroups", "rawTasks", "showStartupNotice"):
            with self.subTest(binding=binding):
                self.assertIn(binding, self.src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
