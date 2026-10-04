# -*- coding: utf-8 -*-
"""验证「程序启动使用引导弹窗」+「反馈界面代码版本检测」（全部离线，不访问真实网络）。

需求：
  1. 程序启动弹出使用引导弹窗，10s 内不可关闭，正文为截图/反馈指引文案
  2. 左下角「不再提示」默认不勾选；右下角「跳转反馈界面」「知道了」
  3. 点「跳转反馈界面」→ 打开反馈界面并自动检测当前代码是否最新；
     非最新时提示「可先尝试更新后看是否解决，未解决再反馈」

覆盖断言：
  A. 新组件 StartupNoticeDialog.vue（倒计时 10s / 不可关闭 / 默认不勾选 / 两个按钮 / 持久化 / 定时器清理）
  B. Layout.vue 接线（启动检查 + 跳转反馈 + 打开更新窗口）
  C. FeedbackDialog.vue 版本检测（checkUpdate / 非最新提示 / 去更新 / reset 复位）
  D. src/DefaultSetting.ini 新增 [助手设置] 启动提示 = True，且后端合并不丢该键、用户值优先级生效
"""
import configparser
import logging
import sys
import tempfile
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

FRONTEND_SRC = _PROJECT_ROOT / "frontend" / "src"
STARTUP_DIALOG = FRONTEND_SRC / "components" / "StartupNoticeDialog.vue"
LAYOUT_VUE = FRONTEND_SRC / "views" / "Layout.vue"
FEEDBACK_DIALOG = FRONTEND_SRC / "components" / "FeedbackDialog.vue"
DEFAULT_SETTING = _PROJECT_ROOT / "src" / "DefaultSetting.ini"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class StartupDialogCase(unittest.TestCase):
    """A. 启动引导弹窗组件"""

    @classmethod
    def setUpClass(cls):
        cls.src = read_text(STARTUP_DIALOG)

    def test_component_exists(self):
        self.assertTrue(STARTUP_DIALOG.exists(), "缺少 StartupNoticeDialog.vue")

    def test_countdown_is_ten_seconds(self):
        self.assertIn("const COUNTDOWN_SECONDS = 10", self.src)
        self.assertIn("countdown = ref(COUNTDOWN_SECONDS)", self.src)
        self.assertIn("countdown.value <= 0", self.src, "倒计时结束才可关闭")
        self.assertIn("请阅读提示", self.src, "展示剩余秒数提示")

    def test_cannot_close_before_countdown(self):
        self.assertIn(':mask-closable="false"', self.src, "10s 内点遮罩不得关闭")
        self.assertIn(':closable="canClose"', self.src, "10s 内不得出现关闭叉")
        # NModal 的 closeOnEsc 默认 true（已核对 naive-ui/es/modal/src/Modal.mjs），必须显式跟随倒计时
        self.assertIn(':close-on-esc="canClose"', self.src, "10s 内按 Esc 不得关闭")
        self.assertIn("const canClose = computed(() => countdown.value <= 0)", self.src)

    def test_buttons_disabled_until_countdown_over(self):
        # 两个按钮都受倒计时约束（含「跳转反馈界面」）
        self.assertEqual(self.src.count("countdown > 0 || saving"), 2)

    def test_dont_remind_default_unchecked(self):
        self.assertIn('v-model:checked="dontRemind"', self.src)
        self.assertIn("const dontRemind = ref(false)", self.src, "默认不勾选")
        self.assertIn("不再提示", self.src)

    def test_footer_buttons_and_events(self):
        self.assertIn("跳转反馈界面", self.src)
        self.assertIn("知道了", self.src)
        self.assertIn("emit('go-feedback')", self.src)
        self.assertIn("emit('update:show', false)", self.src)

    def test_persist_dont_remind_to_settings(self):
        self.assertIn("settingsApi.set('助手设置', '启动提示', 'False')", self.src)
        self.assertIn("await persistDontRemind()", self.src, "任一按钮点击前先落库")
        self.assertIn("if (!dontRemind.value) return", self.src, "未勾选时不写设置")

    def test_notice_text_matches_requirement(self):
        for frag in (
            "如果任务执行出现异常，请第一时间打开日志面板右上角的截图开关",
            "点击顶部栏右上角的文件夹图标",
            "选择日期和对应的任务后生成反馈包",
            "将反馈包发送给开发者即可",
        ):
            self.assertIn(frag, self.src, f"引导文案缺少：{frag}")

    def test_timer_cleaned_up(self):
        self.assertIn("onBeforeUnmount(stopCountdown)", self.src)
        self.assertIn("clearInterval(timer)", self.src)
        self.assertIn("watch(() => props.show", self.src)


class LayoutWiringCase(unittest.TestCase):
    """B. Layout.vue 接线"""

    @classmethod
    def setUpClass(cls):
        cls.src = read_text(LAYOUT_VUE)

    def test_component_imported_and_rendered(self):
        self.assertIn("import StartupNoticeDialog from '@/components/StartupNoticeDialog.vue'", self.src)
        self.assertIn('v-model:show="showStartupNotice"', self.src)
        self.assertIn('@go-feedback="handleStartupGoFeedback"', self.src)

    def test_startup_check_on_mounted(self):
        self.assertIn("const showStartupNotice = ref(false)", self.src)
        self.assertIn("checkStartupNotice()", self.src)

    def test_startup_check_reads_setting(self):
        self.assertIn("settingsApi.getAll()", self.src)
        self.assertIn("['助手设置']?.['启动提示']", self.src)
        self.assertIn("=== 'false'", self.src, "仅显式 False 才不再提示")
        self.assertIn("setTimeout(resolve, 1200)", self.src, "与其他启动弹窗错开")

    def test_go_feedback_guard_without_config(self):
        self.assertIn("function handleStartupGoFeedback()", self.src)
        self.assertIn("请先在左侧选择或新建一个配置，再生成反馈包", self.src)

    def test_feedback_dialog_can_open_update_dialog(self):
        self.assertIn('@open-update="showUpdateDialog = true"', self.src)


class FeedbackCodeCheckCase(unittest.TestCase):
    """C. FeedbackDialog.vue 代码版本检测"""

    @classmethod
    def setUpClass(cls):
        cls.src = read_text(FEEDBACK_DIALOG)

    def test_emits_open_update(self):
        self.assertIn("'open-update': []", self.src)
        self.assertIn("function openUpdate()", self.src)
        self.assertIn("emit('open-update')", self.src)

    def test_check_on_open(self):
        self.assertIn("checkCodeVersion()", self.src)
        self.assertIn("loadOptions()\n    // 打开反馈界面即检测代码是否最新", self.src)

    def test_check_uses_update_api(self):
        self.assertIn("utilsApi.checkUpdate()", self.src)
        self.assertIn("data.update_type !== 'none'", self.src)

    def test_outdated_notice_and_hint(self):
        self.assertIn('title="当前代码非最新"', self.src)
        self.assertIn("若有问题可先尝试更新后看是否解决，未解决再按下方步骤生成反馈包", self.src)
        self.assertIn("去更新", self.src)

    def test_unknown_state_is_non_blocking(self):
        self.assertIn("codeCheckState.value = 'unknown'", self.src)
        self.assertIn("可忽略此提示直接生成反馈包", self.src)

    def test_state_reset_on_close(self):
        self.assertIn("codeCheckState.value = 'idle'", self.src)
        self.assertIn("codeCheckMessage.value = ''", self.src)


class SettingKeyCase(unittest.TestCase):
    """D. [助手设置] 启动提示 的默认值与后端合并"""

    def test_default_setting_declares_key(self):
        parser = configparser.ConfigParser()
        parser.optionxform = str  # type: ignore[assignment]
        parser.read(DEFAULT_SETTING, encoding="utf-8")
        self.assertTrue(parser.has_option("助手设置", "启动提示"), "DefaultSetting.ini 缺 启动提示")
        self.assertEqual(parser.get("助手设置", "启动提示").strip(), "True", "默认 True（显示提示）")

    def test_merge_keeps_key_with_default(self):
        from backend.core.setting_model import Setting

        with tempfile.TemporaryDirectory(prefix="xuan_setting_") as tmp:
            setting = Setting(
                parent_logger=logging.getLogger("verify_startup_notice"),
                setting_path=Path(tmp) / "setting.ini",
            )
            self.assertEqual(setting.get("助手设置", "启动提示", None), "True")

    def test_user_false_is_respected(self):
        """勾选「不再提示」写 False 后，合并结果必须是 False（后端不覆盖用户值）"""
        from backend.core.setting_model import Setting

        with tempfile.TemporaryDirectory(prefix="xuan_setting_") as tmp:
            user_file = Path(tmp) / "setting.ini"
            user_file.write_text("[助手设置]\n启动提示 = False\n", encoding="utf-8")
            setting = Setting(
                parent_logger=logging.getLogger("verify_startup_notice"),
                setting_path=user_file,
            )
            self.assertEqual(setting.get("助手设置", "启动提示", None), "False")
            parser = configparser.ConfigParser()
            parser.optionxform = str  # type: ignore[assignment]
            parser.read(user_file, encoding="utf-8")
            self.assertEqual(parser.get("助手设置", "启动提示").strip(), "False")


if __name__ == "__main__":
    unittest.main(verbosity=2)
