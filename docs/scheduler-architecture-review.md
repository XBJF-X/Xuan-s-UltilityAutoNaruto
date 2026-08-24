# 调度器与任务基类架构评审报告

> 对应 Todo 需求：
> - `前端请求后端的调度器相关的API时，响应速度太慢，能不能给出优化（允许大改相关逻辑包括调度器，任务基类设计等等）`
> - `现有的调度器和任务基类设计，是否不适合现有任务…（任务状态数据放在前端而不是后端，后端只负责持有实例和执行）`
>
> 本报告为**分析 + 方案**，不含实现。实施按下文「实施路线」分阶段推进。

---

## 1. 现状架构盘点

### 1.1 SchedulerService（`backend/services/scheduler_service.py`，约 880 行）

一个类承担了全部调度职责：

| 职责 | 说明 |
| :--- | :--- |
| 优先级队列 | `PriorityQueue`（heapq），按 `(基础优先级, 下次执行时间)` 排序 |
| 三态扫描循环 | 等待(2)→就绪(1)→执行(0)，`force_execute_now` 优先 |
| 预设 once 模式 | `run_once` 按「任务执行顺序」逐一执行、失败跳过、跑完自动 stop |
| 设备生命周期 | `_lazy_init()` 构建 Device / Operationer / TransitionManager / watchdog |
| 异常处理 | 超时、模拟器卡死重启、游戏重启、截图回调注入 |
| 状态上报 | `on_status_change` / `on_task_state_change` → WebSocket |

### 1.2 BaseTask（`backend/core/legacy/Task/BaseTask.py`）

- 构造注入 **6 个依赖**：`task_name / config / transition_manager / operationer / activate_another_task_func / callback / parent_logger`
- 与 Config 通过 `get/set_task_base_config` 强耦合（内存 dict 但语义是「文件持久化」）
- 与调度器通过回调函数单向通信，状态（`is_activated` / `force_execute_now` / `is_temp`）散落在任务对象与 config 两层

### 1.3 现存痛点

1. **上帝对象**：调度决策、设备管理、任务执行、异常处理全部耦合在 SchedulerService，难以单测与替换。
2. **device 到处持有**：SchedulerService 持有；`backend/api/device.py` 截图接口在调度器未启动时还要临时 new 一个 Device（含 ControlManager/ScreenManager），重复建连。
3. **API 首次访问昂贵**：`backend/api/scheduler.py::_get_scheduler()` 首次调用即 `Config()` + `ResourceDBManager()` + **`SceneGraph(db)`——解码全部 186 场景 / 约 845 张元素 BGRA 图（cv2.imdecode + cvtColor，秒级）**，且每个配置各构建一份。
4. **状态查询重**：`get_tasks_status()` 直接遍历 heap 逐任务读 config，无内存快照。
5. **前端靠轮询**：Dashboard 每 2s 轮询 `/scheduler/tasks`，每条 ws 消息还触发一次刷新；`precheck` 每次同步跑 adb 子进程。

---

## 2. 性能优化方案（对应「响应速度太慢」）

### 2.1 根因定位

| 根因 | 成本 |
| :--- | :--- |
| SceneGraph 构建（全量元素图解码） | **秒级**，首次访问任何 scheduler API 即触发 |
| Config 每次创建无条件 `save_config_to_file()` | 磁盘 I/O |
| `precheck` 同步 adb 查询 | 秒级 |
| 前端 2s 轮询 + ws 消息触发刷新 | 高频请求 |

### 2.2 优化清单

1. **共享 SceneGraph / ResourceDBManager 单例**：`backend/api/scheduler.py` 模块级懒加载单例，所有配置的调度器复用同一个 SceneGraph（构建后只读，可安全共享）。
2. **SceneGraph 延迟到 `start()` 才构建**：`status / tasks / precheck / execute / activation` 均不需要 SceneGraph；`_get_scheduler` 只创建轻量 `SchedulerService`（与现有 `_lazy_init()` 方向一致）。
3. **内存状态快照**：SchedulerService 维护 `_state_snapshot = {running, current_task, tasks:[...]}`，由既有 `on_status_change/on_task_state_change` 回调在变更时更新；`get_status()/get_tasks_status()` 直接返回快照副本（O(1)），不再遍历 heap 逐任务读 config。
4. **precheck 加 TTL 缓存（5s）**：同一配置短时间内重复启动不重复跑 adb 查询。
5. **Config 创建免写盘**：`load_and_merge_config()` 后仅当内容与磁盘不一致时才 `save_config_to_file()`。
6. **前端降频**：Dashboard 轮询 2s→5s，且仅在 ws 状态变化时刷新；`configSwitching` 期间跳过（本次已实施第 7 项）。

---

## 3. 用户设想评估：任务队列放前端

> 设想：前端存储 config 中任务相关数据作为任务队列，把后端 TaskQueue 逻辑搬过来；后端只保存 Device / Operationer / BaseTask；前端判断任务需要执行时发送给后端；后端实例化 Task 并赋予监听器、Device、Operationer；后端 BaseTask 执行周期内向前端回报「立即执行调用」「执行出问题」等信号。

### 3.1 认可的部分

- **职责划分方向正确**：前端 = 决策 + 展示 + 命令；后端 = 持有实例 + 执行 + 信号回报。
- **消灭轮询**：状态由后端主动推送（WS）。
- **避免每处重复构建设备**：Device/Operationer 由后端统一持有并注入 Task。

### 3.2 风险与反对理由（全量迁移）

1. **状态双写/一致性**：`是否启用 / 下次执行时间 / 执行进度` 的**唯一事实源**是后端 config 文件（进度由 BaseTask 执行时写入，如「已购买体力次数」）。前端再持一份队列 = 双写；若要后端执行时写进度，就必须回传前端 → 又回到「推送/同步」循环。除非后端完全交出持久化，否则没有净收益。
2. **时间窗口任务依赖可靠时钟**：`冬日烟花季 19:00-22:00`、`叛忍来袭在天地战场/要塞争夺战结束后激活` 等需要**常驻、可靠的调度时钟**。放前端意味着后端无法脱离前端独立调度（前端刷新/断连即丢调度）。
3. **生命周期**：前端是多页签 SPA（`keep-alive` 页面缓存、可刷新），队列状态放前端容易与后端真实执行态脱节。
4. **现状已具备命令模型**：`execute_task_now / toggle_activation / task-order` 已实现「前端命令 → 后端执行」，缺口只在于**状态回传靠轮询**，而非决策层位置。

### 3.3 结论

**不推荐**把 TaskQueue 决策层整体搬到前端；**推荐**用「中间派」方案实现同样的交互模型（见下），无状态双写风险、保留后端可靠时钟。

---

---

## 4. 推荐重构方案：中间派（后端决策 + 前端快照/命令）

### 4.1 目标

1. 后端保留决策循环（可靠时钟 + config 单一事实源）；
2. 前端**零轮询**：后端 WS 主动推送状态快照，前端只管展示 + 发命令；
3. API 全部走内存快照（快路径）；
4. 拆分组件，解除「上帝对象」，让 BaseTask 依赖注入从 6 参数收敛为 1 个上下文。

### 4.2 组件拆分

```
┌─────────────────────────────────────────────┐
│ SchedulerCore（薄编排：start/stop/扫描循环）   │
│   ├─ TaskPlanner（纯逻辑决策）                 │
│   │    优先级 / 下次执行时间 / is_temp 门控    │
│   │    激活传播（execute_requested 信号）      │
│   ├─ TaskExecutor（执行）                     │
│   │    Device + Operationer + BaseTask        │
│   │    回报信号：execute_requested/completed/  │
│   │            failed/progress/screenshot     │
│   └─ SchedulerState（内存快照，API 直读）      │
└─────────────────────────────────────────────┘
        │  WS 推送 scheduler_snapshot
        ▼
前端 AppStore（状态） ←—— 命令 API（execute/toggle/order）
```

### 4.3 信号回报（替代当前回调函数）

BaseTask 增加统一信号口，替代目前散落的 `activate_another_task_func / callback`：

```python
class BaseTask:
    def __init__(self, ctx: RuntimeContext):
        self.ctx = ctx  # 聚合 config/device/operationer/transition_manager/logger/signals

    # 示例信号（由 SchedulerCore 订阅）
    def _emit(self, kind: str, payload: dict):
        self.ctx.signals.emit(self.task_name, kind, payload)
```

信号种类（对齐前端需求）：
- `execute_requested(task_name, enable_if_needed)` —— 立即执行 / 别的任务激活
- `completed(task_name, error=None)` —— 执行完成或失败
- `progress(task_name, step, total, detail)`
- `state_changed(task_name, field, value)` —— 是否启用 / 下次执行时间等变更

### 4.4 WS 协议演进

- 新增 `scheduler_snapshot` 消息：合并 `status + task_state` 一次推送（`{config_id, running, current_task, tasks:[...]}`）。
- 保留 `status / task_state` 向后兼容；前端 AppStore 按 `config_id` 覆盖快照，页面不再轮询。

### 4.5 依赖注入收敛

| 现状 | 目标 |
| :--- | :--- |
| BaseTask 6 参数构造 | BaseTask 只收 `RuntimeContext` 一个对象 |
| 调度器回调函数传参 | 统一 `signals` 订阅/发布 |
| device 每处临时 new | 每 config 单例 Device，由 TaskExecutor 持有，截图 API 复用同一实例 |

---

## 5. 实施路线（分阶段，每阶段可独立发布）

| 阶段 | 内容 | 影响面 | 验证 |
| :--- | :--- | :--- | :--- |
| **一：性能** | 共享 SceneGraph、SceneGraph 延迟到 start、状态内存快照、precheck TTL、Config 免写盘、前端降频 | 仅 scheduler API / 前端轮询 | 首次 status/tasks 请求耗时 <100ms |
| **二：拆分** | SchedulerCore / TaskPlanner / TaskExecutor 拆分，行为不变 | 重构，需全量回归任务执行 | 现有 verify_*.py + 全任务冒烟 |
| **三：信号** | BaseTask RuntimeContext + signals；WS scheduler_snapshot；前端 AppStore 状态化、去轮询 | 任务基类 + WS + 前端 | 前端刷新/断连后状态仍正确 |
| **四（可选）** | 前端 TaskPlanner「预演」视图（只展示调度器将如何调度，不执行） | 前端 | 可视化调度顺序 |

> 阶段一与本次已实施的「第 7 项：切换配置竞态防护」互补：竞态防护消除了前端切换时的乱序覆盖，阶段一从根上把接口提速，二者配合即可彻底解决「切换配置卡顿 / 竞态」体验。

---

## 6. 附：涉及文件清单

| 文件 | 阶段 |
| :--- | :--- |
| `backend/api/scheduler.py` | 一（共享 SceneGraph/快照/缓存） |
| `backend/services/scheduler_service.py` | 一/二（快照、拆分） |
| `backend/core/legacy/Task/BaseTask.py` | 三（RuntimeContext/signals） |
| `backend/api/ws.py` | 三（scheduler_snapshot） |
| `frontend/src/api/ws.ts` | 三（快照订阅） |
| `frontend/src/stores/app.ts` | 三（状态化） |
| `frontend/src/views/Dashboard.vue` / `PresetEditor.vue` | 一（降频）/ 三（读快照） |
| `backend/core/scene_graph.py` | 一（只读共享确认） |
| `backend/core/config_model.py` | 一（免写盘） |

