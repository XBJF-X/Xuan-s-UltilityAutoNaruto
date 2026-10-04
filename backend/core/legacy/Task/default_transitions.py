# -*- coding: utf-8 -*-
"""BaseTask 内置的"公共弹窗 / 独立场景"处理函数（阶段 3 从 BaseTask 外移）

改前这 21 个处理函数写在 ``BaseTask`` 类体内，全部用 ``@TransitionOn("场景名")`` 装饰且
**方法名都是 ``_``**（描述符靠 ``__set_name__`` 收集注册），于是：
- ``BaseTask`` 末尾 140 行被"注册样板"占据，类主体（排期/执行/路由/自救）被淹没；
- 方法名一律为 ``_``，IDE/搜索无法定位，异常栈里也只显示 ``BaseTask._``；
- 新增一个公共弹窗必须改基类（本文件外移后仍然如此，但至少集中在一处数据表里）。

现在：处理函数是本模块的**普通函数**（首参 ``self``），由 ``DEFAULT_TRANSITION_HANDLERS``
这张表集中注册；``BaseTask`` 类体只保留 ``transition_func: dict = {}`` 声明，类定义之后
调用一次 ``install_default_handlers(BaseTask)``。

兼容性（与改前逐字等价）：
- 实例侧 ``BaseTask.__init__`` 仍按 MRO 合并 ``transition_func``，子类同名场景覆盖默认实现；
- ``transition_func[scene](self)`` 的调用形态不变（处理函数本来就是"函数 + 显式 self"）；
- ``SceneMeta.POPUP_SCENES``（识别顺序）与本表的字典顺序无关，本表只做"场景名 → 处理函数"。
"""
import time
from typing import Callable, Dict

from backend.core.legacy.Exceptions import StepFailedError

# --------------------------------------------------------------------------- #
#                                 各场景处理函数                                #
# --------------------------------------------------------------------------- #


def on_secondary_password(self):
    """二级密码弹窗：输入密码并确认"""
    self.logger.info("出现二级密码窗口")
    password = self.config.get_config("二级密码")
    if len(password) != 6:
        raise StepFailedError("请检查二级密码！")
    # 输入操作
    input_el = self.operationer.get_element("输入框")
    if input_el is None:
        raise StepFailedError("未找到二级密码输入框")
    self.operationer.click_and_input(input_el, password)
    # 点击二级密码-确定
    confirm_el = self.operationer.get_element("确定")
    if confirm_el is None:
        self.logger.error("未找到二级密码确认按钮")
        return False
    if not self.operationer.click_and_wait(confirm_el):
        self.logger.error("二级密码验证失败")
    return False


def on_upgrade(self):
    """升级提示：点 X 关闭"""
    self.operationer.click_and_wait("X")
    return False


def on_notice(self):
    """公告：点 X 关闭"""
    self.operationer.click_and_wait("X")
    return False


def on_login_start(self):
    """登录界面：点开始游戏"""
    self.operationer.click_and_wait("开始游戏")
    return False


def on_login_reward(self):
    """登录奖励：点领取"""
    self.operationer.click_and_wait("领取")
    return False


def on_friend_rank(self):
    """好友排名至 X 位：点确定"""
    self.operationer.click_and_wait("确定")
    return False


def on_reconnect_tip(self):
    """重连提示：点继续"""
    self.logger.warning("即将尝试网络重连...")
    self.operationer.click_and_wait("继续")
    return False


def on_response_timeout(self):
    """响应超时"""
    self.operationer.click_and_wait("确定")
    self.logger.warning("响应超时！")
    return False


def on_installer_update_error(self):
    """安装包更新异常：点重试"""
    self.operationer.click_and_wait("重试")
    return False


def on_peer_data_error(self):
    """对方数据异常"""
    self.operationer.click_and_wait("确定")
    self.logger.warning("对方数据异常，即将退出战斗...")
    return False


def on_network_poor(self):
    """网络不畅通"""
    self.operationer.click_and_wait("确定")
    self.logger.warning("网络不通畅！")
    return False


def on_login_auth_expired(self):
    """登录授权过期：点忽略"""
    self.operationer.click_and_wait("忽略")
    self.logger.warning("登陆授权过期，已自动忽略并继续执行...")
    return False


def on_version_update_1(self):
    """版本更新1：点重启游戏"""
    self.operationer.click_and_wait("重启游戏")
    self.logger.warning("游戏出现版本更新，请重启游戏更新")
    return False


def on_version_update_2(self):
    """版本更新2：点重启"""
    self.operationer.click_and_wait("重启")
    self.logger.warning("游戏出现版本更新，此更新必须重启")
    return False


def on_hide_bubble(self):
    """是否隐藏气泡：关闭所有气泡 + 确定"""
    self.operationer.click_and_wait("关闭所有气泡")
    self.operationer.click_and_wait("确定")
    return False


def on_network_connect_failed(self):
    """网络连接失败（决斗场）"""
    self.operationer.click_and_wait("确定")
    self.logger.warning("决斗场网络连接失败，已退出战斗")
    return False


def on_chat_channel(self):
    """聊天频道：点 X 关闭"""
    self.operationer.click_and_wait("X")
    return False


def on_network_reconnect_failed(self):
    """网络异常重连失败"""
    self.operationer.click_and_wait("确定")
    self.logger.warning("网络异常重连失败，已退出战斗")
    return False


def on_unknown_scene_with_x(self):
    """未知含 X 场景：依次尝试三种 X 元素关闭（只点一次）"""
    if self.operationer.search_and_click([
            self.operationer.get_element("X-普通", "主场景"),
            self.operationer.get_element("X-广告-1", "主场景"),
            self.operationer.get_element("X-广告-2", "主场景")
    ], [],
                                         once_max_attempts=1,
                                         max_attempts=1):
        self.logger.info("点击X关闭")
    return False


def on_unknown_scene(self):
    """未知场景：停连点并短暂等待（避免高速空转）"""
    self.operationer.clicker.stop()
    time.sleep(1)
    return False


def on_unregistered_scene(self):
    """未注册场景：停连点并短暂等待（避免高速空转）"""
    self.operationer.clicker.stop()
    time.sleep(1)
    return False


# --------------------------------------------------------------------------- #
#                              场景 → 处理函数 注册表                            #
# --------------------------------------------------------------------------- #

DEFAULT_TRANSITION_HANDLERS: Dict[str, Callable] = {
    "二级密码": on_secondary_password,
    "升级": on_upgrade,
    "公告": on_notice,
    "登录界面-开始游戏": on_login_start,
    "登录奖励": on_login_reward,
    "好友排名至X位": on_friend_rank,
    "重连提示": on_reconnect_tip,
    "响应超时": on_response_timeout,
    "安装包更新异常": on_installer_update_error,
    "对方数据异常": on_peer_data_error,
    "网络不畅通": on_network_poor,
    "登录授权过期": on_login_auth_expired,
    "版本更新1": on_version_update_1,
    "版本更新2": on_version_update_2,
    "是否隐藏气泡": on_hide_bubble,
    "网络连接失败": on_network_connect_failed,
    "聊天频道": on_chat_channel,
    "网络异常重连失败": on_network_reconnect_failed,
    "未知含X场景": on_unknown_scene_with_x,
    "未知场景": on_unknown_scene,
    "未注册场景": on_unregistered_scene,
}


def install_default_handlers(base_cls, *, replace: bool = False) -> dict:
    """把默认弹窗处理函数装到任务基类的 ``transition_func`` 上，返回最终映射。

    ``replace=False``（默认）时保留类上已有的同名场景（便于测试/特化），
    ``replace=True`` 时完全以本表覆盖。
    """
    current = getattr(base_cls, "transition_func", None)
    if not isinstance(current, dict):
        current = {}
    if replace:
        current.clear()
    for scene, func in DEFAULT_TRANSITION_HANDLERS.items():
        current.setdefault(scene, func)
    base_cls.transition_func = current
    return current


__all__ = ["DEFAULT_TRANSITION_HANDLERS", "install_default_handlers"]
