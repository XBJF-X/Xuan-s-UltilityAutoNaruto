"""卡死告警处理（超时监视器事件 → 任务自救 / 强制停止 / 兜底脱困）

阶段 4.6：从 `SchedulerService`(1227 行) 抽出的第六块职责。

搬走：
- `on_watchdog_freeze`（原 `_on_watchdog_freeze`）：监视器线程回调，转独立线程处理
- `process_freeze_event`（原 `_process_freeze_event`）：先给任务自救宽限，未确认则强制停止
  并按级别兜底脱困，最后通知监视器解除挂起
- `handle_scene_stuck`（原 `_handle_scene_stuck`）：点 X / 返回 类元素脱困
- `handle_game_frozen`（原 `_handle_game_frozen`）：重启游戏并等待回到前台
- `handle_emulator_frozen`（原 `_handle_emulator_frozen`）：按截图模式重启模拟器并等待设备就绪

回调服务方法（`service._handle_*` / `service._wait_device_ready` / `service._save_screenshot`）
而非直接调自身实现，保持"实例属性替换即可拦截"的既有测试/扩展点
（`verify_task_scene_stuck_param.py` 等会直接调用 `_handle_scene_stuck`）。
"""
from __future__ import annotations

import logging
import threading
import time
import traceback
from typing import Any

from backend.core.legacy.Exceptions import STOP_REASON_FROZEN, STOP_REASON_STUCK, Stop


class FreezeIncidentHandler:
    """超时监视器卡死事件的处理流程"""

    def __init__(self, service: Any):
        self.service = service

    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    @property
    def config(self):
        return getattr(self.service, "config", None)

    @property
    def watchdog(self):
        return getattr(self.service, "watchdog", None)

    @property
    def operationer(self):
        return getattr(self.service, "operationer", None)

    @property
    def device(self):
        return getattr(self.service, "device", None)

    # ---------------- 入口 ----------------

    def on_watchdog_freeze(self, event) -> None:
        """超时监视器告警回调（在监视器线程中触发，转独立线程处理避免阻塞检测）"""
        threading.Thread(target=self.service._process_freeze_event,
                         args=(event, ),
                         daemon=True).start()

    def process_freeze_event(self, event) -> None:
        """
        处理超时监视器上报的卡死事件（**先自救、后强制**）：

        1. 监视器在告警时已挂上"恢复请求"，这里先把恢复机会交给**任务线程**
           （任务在下一轮循环里执行 ``BaseTask.recover_from_stuck``），最多等待
           ``超时检测-任务自恢复宽限秒``（默认 60s）；
        2. 宽限内未确认（任务卡在长阻塞里 / 自救失败 / 线程已死）→ 强制停止任务
           （带停止原因：``STOP_REASON_STUCK`` / ``STOP_REASON_FROZEN``，任务侧据此
           走 ``on_stuck`` 冷却重试，不会把"下次执行时间"留在过去被立刻重跑），
           再按级别执行兜底脱困；
        3. 处理完毕后通知监视器解除告警挂起状态。

        旧实现是"先 stop_task（置停止标志）→ 再调 Operationer 去救援"，而
        `Operationer._search_loop` 首轮就会 ``raise Stop``，救援必然失败且每次告警
        都留下一条 ERROR traceback（见 2026-09-16 叛忍来袭现场日志）。
        """
        service = self.service
        from backend.services.watchdog_service import FreezeLevel
        level_name = {
            FreezeLevel.SCENE_STUCK: "场景停滞",
            FreezeLevel.GAME_FROZEN: "游戏卡死",
            FreezeLevel.EMULATOR_FROZEN: "模拟器卡死",
        }.get(event.level, str(event.level))
        self.logger.warning(
            f"收到超时监视器告警 [{level_name}] "
            f"任务={event.task_name} 场景={event.scene_name} "
            f"静止={event.static_seconds:.0f}s 详情={event.detail}")
        handled_by_task = False
        try:
            # 0. 卡死/停滞告警触发时自动截图一次，便于排查（截图失败不阻断处理流程）
            try:
                if service._save_screenshot:
                    service._save_screenshot(event.task_name, "WatchdogFreeze")
            except Exception as _e:
                self.logger.warning(f"卡死告警截图失败: {_e}")
            # 1. 先交给任务线程自救（不抢设备、不置停止标志）
            watchdog = self.watchdog
            grace = watchdog.task_recovery_grace() if watchdog is not None else 0.0
            if watchdog is not None and grace > 0:
                self.logger.info(
                    f"[{level_name}] 已请求任务 [{event.task_name}] 自行恢复"
                    f"（场景={event.scene_name}），最多等待 {grace:.0f}s")
                if watchdog.wait_recovery_done(grace):
                    handled_by_task = True
                    self.logger.info(
                        f"[{level_name}] 任务 [{event.task_name}] 已确认处理告警，"
                        f"无需强制停止")
            # 2. 任务未能自行处理 → 强制停止（带原因）+ 兜底脱困
            if not handled_by_task:
                reason = (STOP_REASON_STUCK
                          if event.level == FreezeLevel.SCENE_STUCK
                          else STOP_REASON_FROZEN)
                for task in service.task_queue.get_tasks_by_status(0):
                    service.executor.stop_task(task, reason)
                if event.level == FreezeLevel.SCENE_STUCK:
                    service._handle_scene_stuck(event)
                elif event.level == FreezeLevel.GAME_FROZEN:
                    service._handle_game_frozen(event)
                elif event.level == FreezeLevel.EMULATOR_FROZEN:
                    service._handle_emulator_frozen(event)
        except Exception as e:
            self.logger.error(f"卡死处理流程异常: {e}\n{traceback.format_exc()}")
        finally:
            # 3. 通知监视器处理完毕，进入恢复宽限期（任务自救成功时已自行通知过）
            if self.watchdog and not handled_by_task:
                self.watchdog.notify_recovery_done(event.level)

    # ---------------- 按级别的兜底脱困 ----------------

    def handle_scene_stuck(self, event) -> None:
        """
        场景停滞**兜底脱困**（任务线程自救失败/未响应时才会走到这里）：
        尝试寻找 X / 返回 等元素点击，使游戏脱离当前场景。

        注意：与旧实现的区别——①任务已停止（stop_event 已置位），而
        ``Operationer`` 的搜索/滑动首轮就会 ``raise Stop``，所以脱困动作必须包在
        `Operationer.ignoring_stop()` 里才能真正执行（退出时会原样恢复停止标志）；
        ②``Stop`` 不再是"处理失败"，只记 INFO（它不是异常，是停止请求的既定语义）。
        """
        operationer = self.operationer
        self.logger.info(f"执行场景停滞兜底脱困：尝试点击 X 类元素脱离场景 [{event.scene_name}]")
        if not operationer:
            return
        try:
            with operationer.ignoring_stop():
                elements = []
                for name in ("X-普通", "X-广告-1", "X-广告-2"):
                    el = operationer.get_element(name, "主场景")
                    if el is not None:
                        elements.append(el)
                if elements and operationer.search_and_click(
                        elements, [], max_attempts=2):
                    self.logger.info("场景停滞处理：已点击 X 元素")
                    return
                self.logger.info("场景停滞处理：未找到可点击的 X 元素")

                # 任何可视元素都未找到，则直接点击可能的坐标
                x_coor_element = operationer.get_element("X", "主场景")
                operationer.click_and_wait(x_coor_element)
                back_coor_element = operationer.get_element("返回", "主场景")
                operationer.click_and_wait(back_coor_element)

        except Stop:
            self.logger.info("场景停滞处理：停止请求已置位，跳过兜底脱困")
        except Exception as e:
            self.logger.error(f"场景停滞处理失败: {e}\n{traceback.format_exc()}")

    def handle_game_frozen(self, event) -> None:
        """
        游戏卡死处理：重启游戏。
        重启后等待前台应用恢复为火影忍者，避免在加载完成前被再次判定卡死。
        """
        operationer = self.operationer
        self.logger.warning("执行游戏卡死处理：重启游戏")
        try:
            if not operationer:
                return
            operationer.app_restart()
            time.sleep(5)
            # 等待游戏回到前台（is_naruto_frontend 是方法，需加括号调用）
            max_wait = 120  # 最多等待 2 分钟
            waited = 0
            while waited < max_wait:
                if operationer.is_naruto_frontend:
                    self.logger.info("游戏已回到前台")
                    break
                time.sleep(5)
                waited += 5
            else:
                self.logger.warning("等待游戏恢复超时（120s），交由模拟器卡死检测升级处理")
        except Exception as e:
            self.logger.error(f"重启游戏失败: {e}")

    def handle_emulator_frozen(self, event) -> None:
        """
        模拟器卡死处理：重启模拟器。
        根据截图模式分发：
            0/1/2（普通模拟器）→ Screen 基类 adb 重启
            3（MuMu）→ MuMu.restart_emulator（MuMuManager.exe）
            4（雷电）→ LD.restart_emulator（ldconsole.exe）
        重启完成后等待设备重新就绪，超时则发出错误日志交由上层处理。
        """
        service = self.service
        self.logger.error(
            f"检测到模拟器卡死（{event.detail}），开始重启模拟器")
        screen = None
        if self.device and getattr(self.device, "screen_manager", None):
            screen = self.device.screen_manager.current_screen

        try:
            mode = self.config.get_config("截图模式")
            restarted = False
            match mode:
                case 0 | 1 | 2:
                    # 普通模拟器重启流程：adb reboot（Screen 基类默认实现）
                    self.logger.info("截图模式 0/1/2：通过 adb 重启模拟器")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()
                    else:
                        self.logger.warning("当前截图实例不可用，无法执行模拟器重启")
                case 3:
                    # MuMu模拟器重启流程：MuMuManager.exe
                    self.logger.info("截图模式 3：通过 MuMuManager 重启模拟器")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()
                    else:
                        self.logger.warning("当前截图实例不可用，无法执行 MuMu 模拟器重启")
                case 4:
                    # 雷电模拟器重启流程：ldconsole.exe
                    self.logger.info("截图模式 4：通过 ldconsole 重启模拟器")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()
                    else:
                        self.logger.warning("当前截图实例不可用，无法执行雷电模拟器重启")
                case _:
                    self.logger.warning(f"未知截图模式: {mode}，尝试使用默认 adb 重启")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()

            if not restarted:
                self.logger.error("模拟器重启指令执行失败，请检查模拟器路径与实例索引配置")

            # 等待设备重新就绪（等待屏幕管理器重新可截图）
            if self.device:
                service._wait_device_ready(120)
        except Exception as e:
            self.logger.error(f"模拟器重启流程异常: {e}\n{traceback.format_exc()}")
