"""设备运行时（串口解析 / 连点引擎关闭 / 残留触点自检 / 设备就绪等待）

阶段 4.1：从 `SchedulerService`(1604 行) 抽出的第一块职责。这些方法都只关心"设备与
连点引擎的状态"，不参与排期决策，抽走后 `start()` / `stop()` 只保留流程编排。

行为与拆分前**逐字一致**（含日志文案与异常降级策略）；`service` 回指见包 docstring。
"""
from __future__ import annotations

import logging
import time
from typing import Any


class DeviceRuntime:
    """设备/连点引擎运行时门面"""

    def __init__(self, service: Any):
        self.service = service

    # ---- 运行时状态（每次调用时经 service 取值，支持测试整体替换） ----
    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    @property
    def config(self):
        return getattr(self.service, "config", None)

    @property
    def device(self):
        return getattr(self.service, "device", None)

    def device_serial(self) -> str:
        """当前配置的串口（供残留触点自检/清理使用，取不到时返回空串）。"""
        serial = ""
        try:
            serial = self.config.get_config("串口", "") or ""
        except Exception as e:
            self.logger.debug(f"读取串口配置失败（按空串处理）: {e}")
            serial = ""
        if not serial:
            device = self.device
            if device is not None:
                try:
                    control = device.control_manager.get_current_control()
                except Exception as e:
                    self.logger.debug(f"从控制管理器取串口失败（按空串处理）: {e}")
                    control = None
                serial = getattr(control, "serial", "") or ""
        return str(serial).strip().replace("：", ":")

    def shutdown_clicker_engine(self) -> None:
        """关闭本设备的长驻连点引擎（调度器停止路径专用）。

        连点引擎自 v0.17.60 起是按设备串口全局唯一、线程长驻的执行体：任务级
        ``stop()`` 只失效会话、不销毁线程，因此调度器停止时必须显式关闭，否则
        线程与其持有的控制实例会被保留到进程结束。
        """
        serial = self.device_serial()
        if not serial:
            return
        try:
            from backend.core.legacy.Control.clicker_engine import (
                shutdown_device_clickers,
            )
            shutdown_device_clickers(serial, self.logger)
        except Exception as e:
            self.logger.debug(f"关闭连点引擎失败（不影响停止流程）: {e}")

    def ensure_no_stale_contacts(self, reason: str) -> bool:
        """设备端残留触点自检 + 裸 evdev 兜底清理（v0.17.46）。

        连点期间设备端 minitouch 进程一旦在「触点仍按下」时被终止，evdev 的
        MT slot 不会自动抬起，此后任何一次点击都会把残留坐标一并上报
        （表现为「点一下同时触发所有预设连点坐标」，旧版本只能重启模拟器）。

        v0.17.49：调度器启动/停止是任务边界，这里同时补执行连点期间为不阻塞任务
        而**挂起**的残留清理（`touch_residue.flush_pending_cleanup`，无挂起时零开销）。
        """
        serial = self.device_serial()
        if not serial:
            self.logger.debug(f"残留触点自检跳过（{reason}）：未配置串口")
            return False
        from backend.core.legacy.Control import touch_residue
        try:
            touch_residue.flush_pending_cleanup(
                serial, logger=self.logger,
                reason=f"{reason}｜补清理挂起的残留触点")
            return touch_residue.ensure_no_stale_contacts(
                serial, logger=self.logger, reason=reason)
        except Exception as e:
            self.logger.warning(f"残留触点自检异常（忽略，继续调度流程）: {e}")
            return False

    def wait_clicker_stopped(self, task, timeout: float = 3.0) -> bool:
        """等待任务内的连点线程真正退出。

        停止调度器时必须先让连点线程收尾、再释放控制实例：否则在途的
        ``multi_tap`` 批次会被「抬起命令 + 杀进程」打断，设备端 slot 永久停在
        按下态（v0.17.46 修复的根因之一）。
        """
        clicker = getattr(getattr(task, "operationer", None), "clicker", None)
        if clicker is None or not hasattr(clicker, "wait_stopped"):
            return True
        try:
            return bool(clicker.wait_stopped(timeout))
        except Exception as e:
            self.logger.warning(f"等待连点线程退出出错（继续停止流程）: {e}")
            return False

    def wait_device_ready(self, timeout: int = 120) -> bool:
        """等待设备重新就绪（轮询截图能力，间隔 5s）"""
        waited = 0
        while waited < timeout:
            try:
                device = self.device
                if device and device.device_ready and device.screen_cap() is not None:
                    self.logger.info("设备已恢复就绪")
                    return True
            except Exception as e:
                self.logger.debug(f"设备就绪探测失败（继续等待）: {e}")
            time.sleep(5)
            waited += 5
        self.logger.warning(f"等待设备恢复超时（{timeout}s）")
        return False
