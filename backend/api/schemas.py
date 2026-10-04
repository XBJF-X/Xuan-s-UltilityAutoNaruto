"""API 响应模型（阶段 2：把"裸 dict 契约"变成可校验、可生成 OpenAPI / TS 类型的 schema）

审查结论（docs/refactor-plan-2026.md §2.2）：67 个 REST 端点里只有 3 个声明了
`response_model`，其余全部返回裸 dict —— 前端只能手抄字段名（如 `resource.ts` 与
`resource.py` 一一对应但无任何机制保证同步），契约漂移无人发现。

设计取舍：
- 基类 `PassthroughModel` 设 `extra="allow"`：**未声明的字段照样返回**。这样
  `response_model` 只承担"声明与校验已知字段 + 生成文档/类型"的职责，绝不会因为
  漏声明某个字段而把前端在用的数据静默过滤掉（这是引入 response_model 最大的风险）。
- 只声明"稳定且前端确实消费"的字段；其余由 extra 透传。
- 字段名与现状保持一致（中文键的配置结构不作为 response_model，避免过度约束）。
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PassthroughModel(BaseModel):
    """允许额外字段的响应基类（见模块 docstring 的取舍说明）"""

    model_config = ConfigDict(extra="allow")


# ===== 健康检查 / 版本 =====

class HealthResponse(PassthroughModel):
    status: str
    version: str = ""


class VersionResponse(PassthroughModel):
    ok: bool = True
    version: str = ""


# ===== 通用操作结果 =====

class OkResponse(PassthroughModel):
    """`{"ok": true}` 类响应（PUT/激活/启停等）"""

    ok: bool = True
    message: Optional[str] = None


# ===== 调度器 =====

class SchedulerStatus(PassthroughModel):
    """与 `SchedulerState.get_status()` 同形状；未创建调度器时返回同样的"未运行"快照"""

    running: bool
    task_count: int = 0
    mode: str = "persistent"          # persistent / once


class TaskRuntimeItem(PassthroughModel):
    """调度器任务快照项（`SchedulerState._tasks` 的值；前端 Dashboard 直接消费）"""

    name: str
    status: int = 2                   # 2=等待 1=就绪 0=执行
    priority: int = 0
    base_priority: int = 0
    activated: bool = True
    next_execute: Optional[str] = None


class SchedulerTaskList(PassthroughModel):
    """仅用于文档：实际端点声明为 `list[TaskRuntimeItem]`"""

    tasks: List[TaskRuntimeItem] = Field(default_factory=list)


# ===== 设备 / 串口 =====

class SerialListResponse(PassthroughModel):
    serials: List[str] = Field(default_factory=list)


class AdbRestartResponse(PassthroughModel):
    ok: bool
    serials: List[str] = Field(default_factory=list)


class StaleContactsResponse(PassthroughModel):
    ok: bool
    serial: str = ""
    had_stale: bool = False
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None


# ===== 全局设置 =====

class SettingValueResponse(PassthroughModel):
    value: Optional[str] = None
