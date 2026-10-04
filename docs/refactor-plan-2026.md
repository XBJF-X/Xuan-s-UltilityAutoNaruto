# Xuan 后端与前后端通信重构方案（2026-09）

> 本文件为**审查 + 方案 + 实施记录**。审查方式：4 路并行只读深审（REST API 层 / 调度器与服务层 / 前后端通信与前端数据层 / core-legacy 核心业务层）+ 关键行号人工复核。
> 运行栈实测：CPython **3.12.6**（`.venv` 与 `build/runtime` 一致）、fastapi 0.139.2、starlette 1.3.1、pydantic 2.11.7、sqlmodel 0.0.24。
> 用户决策（2026-09-17）：交付形式=写入本文件；实施范围=**阶段 0~2**；高风险项=**允许破坏性变更**（前端与测试同步更新）。
>
> ⚠️ 审查时工作区有 **41 项未提交改动**（`backend/api/utils.py`、`backend/core/legacy/Clicker.py`、`Control/*`、`frontend/dist/*`、`src/DefaultConfig.json` 等）。本文档与后续实施**不得 revert/丢弃**这些改动；提交前须经用户确认。

---

## 0. 结论速览

最紧急的不是架构重构，而是若干**失控型缺陷**（静默丢数据 / 静默死线程 / 静默卡界面 / 静默改配置）+ 3 项**安全缺口**（可被 MITM 替换代码、本地文件读取、任意网页驱动本地 API）。这些改动面小、可独立热更新。

| 优先级 | 缺陷 | 位置 | 后果 |
|---|---|---|---|
| P0 | `setting.ini` 读路径触发全量重写且非原子 | `core/setting_model.py:19-23`、`services/settings_service.py:11-21` | 一次读=一次整文件重写；并发写可截断/交错 → **丢全部助手设置** |
| P0 | 线程因 `try` 块外类型转换异常静默死亡 | `scheduler_service.py:899-911`、`watchdog_service.py:492-499` | 用户填非数字「扫描间隔」→ 扫描线程死、`running` 仍 True：界面显示运行中但永不执行，无报错 |
| P0 | `async def` 路由内同步阻塞 I/O | `api/utils.py:817-958`、`api/scheduler.py:224-251`、`api/device.py:111-299`、`api/resource.py:68-145` | 单 worker 事件循环被冻结数秒~60s → **WS 日志推送与所有 API 一起停摆**，界面"卡死" |
| P0 | 热更新下载 `verify=False` 且无完整性校验 | `api/utils.py:679/831/846/871/1007/1154/1206` | TLS 校验关闭 + zip 无签名校验 + 覆盖 `backend/`/`frontend/dist` 后重启 → **可被 MITM 替换为任意代码** |
| P0 | SPA 回退中间件路径穿越 | `main.py:299-302` | `%2f` 未规范化 → 可读 `setting.ini`（含 `GithubPAT`）、`config/*.json`、`src/database.db` |
| P0 | 副本配置日志 `config_id` 提取错误 | `api/ws.py:93`、`api/utils.py:181`（`Config_1_副本`，`config_service.py:205`） | 副本日志挂到源配置：副本日志面板**永远空白**、源面板混入副本日志 |
| P1 | CORS 反射任意 Origin + WS 无 Origin 校验 | `main.py:267-273`、`api/ws.py:155-179` | 任意网页可调本地写接口（`apply-update`/删配置/启停调度器/`os.startfile`）与读全部日志 |
| P1 | 反馈打包 `date`/`task_name`/`save_path` 未净化 | `api/utils.py:1294-1371` | 任意目录读取 + 任意位置写文件（`username` 可经 rename 写成 `..\..`） |
| P1 | 停机把"临时启用"永久化 | `scheduler_service.py:616-622` | 被临时激活的禁用任务在停止后**永久变为启用并落盘** |
| P1 | GET 有副作用（读状态即创建调度器） | `api/scheduler.py:34-83,254,260` | 5s 轮询让每个看过的配置常驻调度器对象与日志 handler |
| P1 | 无优雅停机 | `main.py:129-139` | 调度器/线程/DB 引擎/WS 协程均不清理 → 设备端残留触点（v0.17.46 同源故障） |
| P1 | WS 协议无信封/无版本/两种帧/无订阅/无背压/无连接可见性 | `api/ws.py:41-152`、`frontend/src/api/ws.ts:181-224` | 断线不可见、日志静默中断、慢客户端阻塞广播、契约无法演进 |
| P1 | 前端无统一请求层、0 处 AbortController、快照三写者竞态 | `frontend/src/api/client.ts:12-18`、`stores/app.ts`、`Dashboard.vue:179` | 错误处理 5 种风格、切配置在途请求不取消、慢轮询覆盖新推送 |
| P2 | `TaskCompleted` 传 2 个参数 | `core/legacy/Task/MiJingTanXian.py:66` | **实测更正：`Exception("msg", 3)` 不抛 TypeError**（args 是元组），故不会翻转完成/异常语义；真实后果是日志渲染成 `('...%d 次...', 3)` 元组文本且 `%d` 不展开（纯日志质量） |

---

## 1. 现状体检（实测数据）

### 1.1 规模

| 文件 | 行数 | 职责问题 |
|---|---|---|
| `backend/core/legacy/Task/BaseTask.py` | 1712 | 排期 + 执行循环 + 日志 + 路由 + 自救 + 截图 + 等待 + 20 个内建 handler |
| `backend/services/scheduler_service.py` | 1534 | 39 个方法 / 至少 10 类职责 |
| `backend/api/utils.py` | 1495 | 13 端点：更新下载/zip 覆盖/反馈打包/win32 对话框/日志解析/依赖探测 |
| `backend/core/legacy/Recognizer.py` | 1136 | 场景识别 + OCR 增强阶梯 |
| `backend/core/legacy/Operationer.py` | 975 | 操作门面 |
| `backend/core/legacy/Scene/TransitionManager.py` | 864 | 250+ 装饰器注册的跳转表 |
| `backend/api/resource.py` | 758 | 23 端点 + 识别匹配 + SceneGraph 同步 |
| `frontend/src/views/Layout.vue` | 1072 | 配置 CRUD + 调度控制 + 任务树 + 启动弹窗 + 路由态 |

### 1.2 接口与通道

- REST **69 个**（68 router + `/api/health`）：GET 29 / POST 24 / PUT 10 / DELETE 4；WebSocket 2。
- `response_model` 仅 3 个（`api/config.py:44/56/64`）。
- `/ws/logs` 是前端唯一连接（`frontend/src/api/ws.ts:76`）；`/ws/status` **前端从不连接**。
- WS 消息类型：`log`（单条对象帧）、`["log",[items]]`（数组帧）、`status`、`task_state`、`scheduler_snapshot`、非 JSON 文本 `pong`、前端伪消息 `reconnected`（**不在 `WSMessage` 联合类型里**）。
- `/api/health` 的 `version` 硬编码 `"2.0.0"`（`main.py:311`），与 `_version.py` 真实版本不一致。

### 1.3 同义模块重复（已 diff 核验）

| 概念 | 新层 | 旧层 | 结论 |
|---|---|---|---|
| 场景图 | `core/scene_graph.py`(75) | `legacy/Scene/SceneGraph.py`(76) | 近乎逐字复制；**行为不同**：新层 `element.bgra = None`（内存优化），旧层 `np.ascontiguousarray`（保留）。运行时由新层构建单例，识别器却由旧层类型驱动 |
| 配置 | `core/config_model.py`(259) | `legacy/Config.py`(268) | 方法集完全相同、前 120 行逐字相同；旧层被 16 处 import 做类型标注 → 同名两个 `Config` 类 |
| 枚举 | `core/enums.py`(29) | `legacy/Enums.py`(39) | 取值逐字相同；新层 3 处引用 / 旧层 15 处 |
| 异常 | `core/exceptions.py`(41) | `legacy/Exceptions.py`(45) | **新层 0 引用（死文件）**，且内部 `Stop` 定义两次（:34、:39） |
| 设置 | `core/setting_model.py`(150) | `legacy/Setting.py`(120) | **旧层 0 引用（死文件）**，且缺 `optionxform=str`（会把 `MuMu安装路径` 小写化） |

其他重复知识：MuMu/LD 关键文件候选路径 **5 份**（`validate.py:19-31`、`device.py:201-211`、`scheduler.py:168`+`scheduler_service.py:222-234`、`Screen/MuMu.py:87-90`、`Screen/LD.py`，且 DLL 候选顺序不同）；ADB 串口枚举 2 份；任务 schema 2 份；用户名→日志目录 3 份；读 `_version.py` 2 份；后台任务样板 3 份；BaseTask 5 个 `_cleanup_on_*` 逐字相同；截图保存路径规则 2 份；键位 `update_coordinates` 样板 12 份；`clicker.stop()` 68 处。

### 1.4 死代码（引用计数 = 0，已核验）

`core/exceptions.py`、`legacy/Setting.py`、`core/recognizer_engine.py`（4 行壳）、`_LOG_LINE_RE`（`api/utils.py:148`）、`_RELEASES_URL`、`_github_pat_configured`（定义但从不调用）、`_BINARY_FIELDS`、`ConnectionManager.broadcast_log`、`/ws/status`、`PriorityQueue.{dequeue,peek,reheapify,refresh_task}`、`_cancel_scan_loop`（`pass` 且无调用点）、`/api/utils/serial-list`、`updateTaskPriorities` 三层死链、`get_task_priorities/get_task_order`、`getLogsByConfig`、`clearLogs`、`logMessages`+`syncGlobalLogs`。

### 1.5 工程化现状

- 无 `.github/workflows`（`.github/` 本身在 `.gitignore`）→ **零自动化验证**。
- 无 linter / formatter；`frontend/package.json` 只有 `vite build`（`tsconfig.json` 的 `strict: true` 仅在编辑器生效），无 `vue-tsc`。
- `frontend/dist` 入库（热更新必需），代价是每次构建 7000+ 行 diff。
- `test_scene/` 246 文件、36 个 `verify_*.py` 纯手工跑；批次入口 `test_scene/_run_verify_batch.py` 只列 12 个（缺 `verify_activation_window_guard.py`、`verify_task_recovery.py`、`verify_task_schedules.py`）。
- 前端业务实体零 interface，**105 处 `any`**。

---

## 2. 问题清单

### 2.1 P0（7 项）

1. **`setting.ini` 读即重写 + 非原子**：`Setting.__init__` 无条件 `save_to_file()`（`core/setting_model.py:19-23`），而 `SettingsService()` 每次调用都新建实例（`services/settings_service.py:11-21`，`api/utils.py:327/346/497` 各 new 一次）。`open(path,'w')` 直接截断（`:133-139`），无 tmp+rename、无锁 → 与 `api/settings.py:7` 的写路径并发可损坏文件。
2. **线程静默死亡**：`_scan_loop`（`scheduler_service.py:899-911`）与 `_monitor_loop`（`watchdog_service.py:492-499`）把间隔计算放在 `try` 之外，`float()/ /1000.0` 遇非数字抛 `TypeError` → 线程终止、`running` 仍为 True，无任何上报。
3. **`async def` 内同步阻塞**：见 §0 表格。单 uvicorn worker，阻塞期间 WS 30ms 批量推送协程（`api/ws.py:128-135`）与全部 API 一起冻结；`/check-update` 最坏 4×15s 而前端 axios 超时仅 30s（`frontend/src/api/client.ts:8`）。
4. **热更新 MITM 面**：`requests.get(..., verify=False)` 7 处；热更新 zipball 无哈希/签名校验即 `extractall` + 覆盖 + 重启（`api/utils.py:992-1112`）；`.update_backup` 无自动回滚。
5. **SPA 回退路径穿越**：`main.py:299-302` 未规范化 `request.url.path` 即拼接。
6. **副本配置日志串号**：`Config_\d+` 非锚定正则（`api/ws.py:93`、`api/utils.py:181`），`Config_1_副本` 被提取为 `Config_1`。
7. **GET 有副作用**：`api/scheduler.py:34-83` 的 `_get_scheduler` 被 GET `/status`（:254）与 GET `/tasks`（:260）调用；`destroy_scheduler` 只在删配置时（`api/config.py:140-141`）。另 `_schedulers` 是**无锁 check-then-create**（并发可建两个调度器 → 同串口双连接，`_precheck_serial:119-128` 的占用保证失效）。

> **P2 更正（实测）**：`core/legacy/Task/MiJingTanXian.py:66` 的 `raise TaskCompleted("...%d 次...", self.TZQ_OCR_ATTEMPTS)` —— 子代理初判为「2 参 → TypeError → 完成被误判为异常」。**实测证伪**：`Exception("msg", 3)` 合法（args 是元组），不抛 TypeError，也不会翻转完成/异常语义。真实后果仅为日志里出现 `('...%d 次...', 3)` 元组文本、`%d` 不展开。已按日志质量修复（f-string 单参数），见 `test_scene/verify_phase0_hardening.py::MiJingTanXianRaiseTest`。

### 2.2 P1（按域）

**配置与状态**
- 停机把"临时启用"永久化（`scheduler_service.py:616-622`）——只 `clear()` 登记、明确不写回。
- `Config.save_config_to_file` 非原子无锁（`core/config_model.py:244-259`），写入方含任务线程/扫描线程/事件循环三线程 → 可损坏 `Config_N.json`；`list_configs` 遇坏 JSON 静默跳过（`config_service.py:77-78`）→ 配置"消失"。
- 四份任务状态真相源（config JSON / task 属性 / heap 顺序 / `SchedulerState._tasks`）；配置页改「是否启用」走 `api/config.py:83-88` **不更新运行中调度器快照** → 零轮询前端可无限期显示错状态。
- `SchedulerState.set_running(False)` 不清 `task_count`/`mode`（`core/scheduler/state.py:22-28`）。

**并发与生命周期**
- `stop()` 不 join 任何线程、先释放设备再让任务线程收尾（`scheduler_service.py:610-706`）；L688-705 是重复清理段；`_cancel_scan_loop` 是空实现。
- `_scanning` TOCTOU（`:925-928`），而 `scan()` 会被 3 个线程调用；`heap.remove + heapify` 非线程安全。
- 无优雅停机（`main.py:129-139`）：不 stop 调度器、不 dispose `ResourceDBManager.engine`（只好在热更新里手工补刀 `api/utils.py:1053-1062`）、不取消 WS flush 协程。
- `_get_main_loop()` 在任意线程调 `asyncio.get_event_loop()`（`api/scheduler.py:27-31`）：3.12 下非主线程无 loop 会抛 `RuntimeError`——**与本方案"把 start 移出事件循环"必须同批修**。
- 共享 SceneGraph/Recognizer 无锁双检（`scheduler_service.py:46-53`、`api/resource.py:456-466`），且资源编辑路径在事件循环线程直接改写共享对象（`api/resource.py:558-632`）与扫描线程竞争。

**分层与契约**
- 分层泄漏/环：`core/config_model.py:39` → `api.ws`；`services/scheduler_service.py:197/495` → `api.ws` / `api.utils` 私有函数；`api/utils.py:797` → `import backend.main`（与 `main.py:51-56` 构成隐式循环）；`api/device.py:22` → `api.scheduler._schedulers`；`api/resource.py` → `services.scheduler_service`（7 处）。
- 契约不统一：裸 dict / `{ok:True}` / 200+`{ok:false}` / `HTTPException` 四种形态并存；错误信息泄漏原始异常（`main.py:208-212` `detail=f"服务器内部错误: {exc}"`）；`delete_config` 恒 `return True`（`config_service.py:265-270`）→ 删不存在的配置也 200；`settings.py:26-29` 对未知键也 200（`_merge_configs` 只保留默认声明过的键 → 静默丢弃）。
- `payload: dict` 9 个端点无 schema；`_filter_element_fields`（`api/resource.py:746-751`）`float()/int()` 遇 `"abc"` 抛 `ValueError` → 500；非法枚举静默降级（脏数据入库）。
- 契约统一**必须分批**（详见 §4 阶段 2），因为前端有既有依赖：`Dashboard.vue:203-212` 读 `data.ok/reason/window_state/schedule`；`UpdateDialog.vue:244-272`、`FeedbackDialog.vue:286-345` 读 `ok/message/phase/percent`；`ResourceSceneEditor.vue:751-937` 在 200 分支取 match/OCR 结果。

**通信协议与前端数据层**
- 无统一信封/无版本/两种帧并存；前端 `Array.isArray` 特判 + 归一化 hack（`frontend/src/api/ws.ts:185-207`），消费端 `msg.config_id` 与 `msg.data?.config_id` 两种写法并存。
- 连接状态不可见：`ws.ts:36 connected` 全仓无消费点；顶栏"已连接"来自 HTTP `/api/health`（仅 mount/手动刷新）；只发 ping 不校验 pong；`onerror` 忽略（`ws.ts:224`）。
- 无订阅粒度（全部配置广播给全部连接）、无背压（30ms 批推无上限 + 串行 `await send_json`，慢客户端阻塞全体）、`Manager.active_connections` 在迭代中 `${await}` 且可被 `disconnect` 改写（list 迭代静默跳过元素）。
- 无统一请求层（`frontend/src/api/client.ts:12-18` 只 `console.error`）；全仓 **0 处 AbortController**；错误处理 5 种风格；快照三写者（`Layout.vue:574` 有 `_switchSeq` 保护，`Dashboard.vue:179`、`PresetEditor.vue:197/296` 无）→ 慢轮询覆盖新推送。
- 同一字段双写/漏写：`TaskConfigPanel.vue:160+165` 对「是否启用」写两次；`PresetEditor.vue:231` 只写 config 不通知调度器；`ConfigDetail.vue:414-419` 一次保存发 N 个串行请求。
- `TaskConfigPanel.vue:198-204` 不订阅 WS，而调度器会自动改启用态（`scheduler_service.py:771-778`、`:1186-1188`）。
- 静默失败：后端 34 处 `except: pass/continue`（含 `api/ws.py:125/134` flush 协程静默死亡）；前端 12 处空 catch。**与项目 AGENTS.md「禁止空 catch / 空 try-except」直接冲突**。

### 2.3 P2（择要）

- `core/scheduler/` 三组件名不副实：`TaskPlanner` 只做 3 个静态判断（三态决策仍在 `scan`）、`TaskExecutor` 不管线程（线程由 `BaseTask` 自建）、`RuntimeContext` 只是 7 字段打包；`executor ↔ watchdog ↔ service` 回指成环。合计 221 行 vs `SchedulerService` 1534 行（重构文档记录重构前约 880 行 → **拆分后未减反增**）。
- `BaseTask` 内建 20 个 `@TransitionOn` 方法全名为 `_`（:1576-1712），靠描述符 `__set_name__` 注册，可读性差；5 个 `_cleanup_on_*` 逐字相同；`wait_for()`(:772) 无调用方。
- `legacy/` 名不副实（含刚重构的活跃主力 `Control/clicker_engine.py`、`touch_residue.py`、`adb_bootstrap.py`、`Task/`、`Scene/`）。改名成本：`test_scene/` 94 处 / 41 个脚本、2 处硬编码路径、3 处文档；**打包无需改**（`build/build_release.py:152` 整目录 copytree）。
- `TuanBen` 空壳任务已注册（`Task/TuanBen.py:3-4`），只会空转到最长时长。
- `scheduler_service.py:1451` 注释称 `is_naruto_frontend`"是方法需加括号"，实际是 `@property`（`Operationer.py:593-599`）——**代码正确、注释错误**。
- `resource.py:757` 用 `Element.__fields__`（pydantic 2.11 下为 v1 兼容属性，触发弃用告警）。
- `_safe_scene_filename` 把非法字符统一替换为 `_`（`resource.py:36-39`）→ `场景 A:B` 与 `场景 A?B` 映射同一文件名，**上传可覆盖另一场景底图**。
- `resource.py:147` 模块级 `_db` 定义在使用它的函数之后（依赖"调用时求值"）。
- import 期副作用（`main.py:19/47-56/60-85/168/219-221`）：`sys.path.insert`、导入全部 api 模块（建 `config/` 并删文件、建 SQLite 引擎并跑迁移）、monkey-patch `sys.excepthook`、`atexit.register`；lifespan 同步 rmtree 清理日志。
- 非问题澄清：`TransitionManager.py:569` 的嵌套引号 f-string 需 PEP 701，但运行时固定 3.12.6，**当前无问题**（仅阻止下调版本）。

---

## 3. 目标架构

### 3.1 后端分层与依赖铁律

```
backend/
├─ main.py                 # 只剩 create_app() + uvicorn 入口（无业务、无 import 副作用）
├─ app/                    # 【新】装配层：assembly.py / lifespan.py / middleware.py / errors.py
├─ api/                    # 【只做契约】routers/ + schemas/*（Pydantic v2）
├─ services/               # 【业务编排，禁止 import fastapi/api】
│  ├─ scheduler/           #   拆掉 1534 行上帝对象
│  │   ├─ service.py         Facade：start/stop/status/execute/toggle
│  │   ├─ scan_loop.py       线程 + RLock + 间隔 + 退出（唯一定时驱动）
│  │   ├─ planner.py         三态迁移/激活/预设 → Command 列表（纯逻辑）
│  │   ├─ activation.py      待激活登记 + 临时启用 enter/exit/restore_all
│  │   ├─ preset.py          run_once 顺序执行 + 进度重置
│  │   ├─ notifier.py        空闲/预设通知 + 去抖
│  │   ├─ device_runtime.py  _lazy_init/环境预检/残留触点/连点引擎/设备就绪
│  │   └─ incident.py        卡死告警编排 + 截图 + 脱困/重启
│  ├─ scheduler_registry.py  【新】_schedulers 收敛 + 每配置锁 + 生命周期
│  ├─ config_service.py / settings_service.py（进程级单例 + RLock + 内存缓存）
│  ├─ device_service.py / emulator_env_service.py     #【新】截图/adb/环境探测（合并 5 份重复）
│  ├─ resource_service.py / scene_graph_service.py    #【新】DB CRUD + 共享图加锁同步
│  └─ update_service.py / feedback_service.py / log_service.py   #【新】从 api/utils.py 下沉
├─ runtime/                # 【新】events.py / task_runner.py / paths.py / module_registry.py
└─ core/                   # 领域层：不 import api/services
   ├─ scheduler/{state.py→TaskStateStore, executor.py, commands.py, clock.py}
   ├─ config_model.py      # 退化为纯持久化（原子写 + 锁 + 去抖 flush + get_int/get_bool）
   └─ enums.py exceptions.py setting_model.py scene_graph.py
```

**三条铁律**（可用脚本静态校验）：
1. `core/**` 不得 import `api/**` 或 `services/**`；
2. `api/**` 不得 import 另一个 `api/**`；
3. 组件只依赖 `core` 的接口/协议，不反向持有 service。

**关键接口**：

```python
# core/scheduler/commands.py —— 决策与执行解耦
@dataclass(frozen=True)
class Promote:  task_name: str; to_status: int
@dataclass(frozen=True)
class Dispatch: task_name: str
@dataclass(frozen=True)
class Preempt:  running: str; candidate: str

# core/scheduler/state.py —— 唯一状态写入口（取代四份真相源）
class TaskStateStore:
    def set_enabled(self, task_name: str, value: bool) -> None: ...
    def set_next_execute(self, task_name: str, ts: int) -> None: ...
    def snapshot(self) -> dict: ...
    def subscribe(self, cb: Callable[[dict], None]) -> None: ...

# core/scheduler/executor.py
class TaskExecutor:
    def join_all(self, timeout: float) -> list[str]: ...   # 修 stop() 不 join
    def running_task_names(self) -> set[str]: ...

# runtime/events.py —— 取代 core/services 对 api.ws 的反向依赖
def publish_status(snapshot: dict) -> None: ...
def publish_log(record: dict) -> None: ...
def subscribe(kind: str, cb: Callable[[dict], None]) -> Callable[[], None]: ...
def bind_loop(loop: asyncio.AbstractEventLoop) -> None: ...   # lifespan 注入，删 _get_main_loop
```

### 3.2 通信协议 v1

统一信封（所有服务端帧，含批量）：

```json
{"v":1,"type":"scheduler.snapshot","seq":118,"ts":1730000000000,"config_id":"Config_1","payload":{...}}
```

不变式：`config_id` 只在顶层；`payload` 形状由 `type` 唯一决定；`seq` 每连接单调递增（前端丢弃过期帧）；未知 `type` 必须忽略；`hello` 协商能力。

| type | 方向 | payload | 触发 |
|---|---|---|---|
| `hello` | S→C | `{server_version, protocol, caps}` | 连接首帧 |
| `log.batch` | S→C | `{entries:[{id,ts,level,logger,config_id,message}], dropped}` | ≤30ms 聚合、每帧 ≤200 条 |
| `scheduler.snapshot` | S→C | `{running,mode,task_count,tasks[]}` | 仅状态迁移事件 |
| `task.state` | S→C | `{name,status,action,error}` | 任务起停 |
| `config.changed` | S→C | `{scope:'tasks'\|'setting'\|'exists'}` | REST 写成功后 |
| `subscribe` | C→S | `{config_ids, levels}` | 视图挂载/切换 |
| `ping`/`pong` | 双向 | — | 15s 心跳，40s 无帧判死 |
| `error` / `log.truncated` | S→C | `{code,message}` / `{dropped}` | 协议错误 / 背压丢弃 |

- 错误约定：REST 保留 HTTP 语义（非 2xx + `{detail}` 扩展为 `{code,message,detail}`）；HTTP 200 只用于**已枚举**的业务拒绝；前端 `request<T>()` 把「非2xx / `ok:false` / 超时 / 网络 / 取消」统一归一为 `ApiError{kind,status,code,message}`。
- 重连：指数退避 500ms→8s（±20% 抖动），`onopen` 重订阅 + 补拉 history，状态栏显示重试次数。
- 背压：每连接有界队列（溢出丢最旧 + `log.truncated`），发送 `wait_for(2s)` 判慢客户端并断开。
- **热更新兼容（硬约束）**：后端源码外置可热更，但用户磁盘上的 `frontend/dist` 可能仍是旧版 → ① 新语义一律**新增 type**，绝不改旧 type 字段含义；② 后端按连接能力（是否发 `hello`/`subscribe`）决定发新帧或旧帧，旧帧保留 ≥2 个 release；③ 发布顺序固定"后端先兼容、前端后切换"。

### 3.3 前端数据层（单出口 + 单写入口）

```
frontend/src/
├─ api/
│  ├─ http.ts                唯一 axios 实例 + request<T>() + ApiError 归一 + AbortController
│  ├─ ws/{protocol.ts, client.ts, handlers.ts}
│  └─ endpoints/{config,scheduler,device,resource,settings,utils}.ts
├─ types/{api.generated.ts（由 /openapi.json 生成）, domain.ts}
└─ stores/{app,scheduler,logs,config}.ts
```

**三条硬规则**：① 组件不直接 import `client`；② 组件不直接 `new WebSocket`/不解析帧（只用 `ws/handlers` 的 `on(type,handler)` 注册表）；③ 快照唯一写入口 `schedulerStore.applySnapshot(configId, seq, payload)`。`Layout.vue` 按 `useConfigs` / `useSchedulerControl` / `useTaskTree` / `useStartupChecks` 拆 composable，弹窗拆组件。

---

## 4. 分阶段路线图

### 阶段 0 · 紧急修复（0.5–1 天，风险极低）
| 项 | 文件 | 验收 |
|---|---|---|
| MiJingTanXian 双参异常 | `core/legacy/Task/MiJingTanXian.py:66` | `verify_ocr_robustness.py` |
| 扫描/监视线程静默死亡 | `services/scheduler_service.py:899-911`、`services/watchdog_service.py:492-499` | 新增"非法间隔 → 线程存活并上报"断言 |
| setting.ini 单例 + 读不落盘 + 原子写 | `services/settings_service.py`、`core/setting_model.py` | 新增"只读不写盘""并发写不丢键" |
| 停机恢复临时启用原值 | `services/scheduler_service.py:616-622` | `verify_temp_activation_restore.py`(7) |
| config_id 显式传递 + 正则锚定 | `api/ws.py:88-126`、`api/utils.py:148-191`、logger 创建处 | `verify_log_ws_payload.py`(4) + 副本配置断言 |

### 阶段 1 · 失控面收敛（2–3 天）
- `Config.save_config_to_file` 加锁 + tmp+`os.replace`（`core/config_model.py:244-259`）。
- 阻塞端点移出事件循环：纯 I/O 路由 `async def`→`def`（走 anyio 线程池）；`upload_*` 保留 async 但重活走 `run_in_threadpool`；**同批**把事件循环注入 `runtime/events.py` 并删除 `_get_main_loop`。
- GET 无副作用：新增 `peek_scheduler(id)`；`/status`、`/tasks` 未初始化时返回空快照；`_get_scheduler` 加每配置锁。
- 优雅停机：`shutdown_all_schedulers(timeout=5)` + `ResourceDBManager.dispose()` + `_ensure_no_stale_contacts("程序退出")`。
- 安全：`verify=True` + 热更新完整性校验（sha/manifest）；`runtime/paths.py::safe_join`/`safe_component` 应用于 SPA 中间件、反馈打包、open-log-dir、`get_config_file_handler`；删除 CORS 或改白名单 + WS Origin/一次性 token 校验。
- 回归：`verify_touch_residue_fix.py`(49)、`verify_force_preempt.py`(12)、`verify_manual_execute_guard.py`(12)、`verify_activation_window_guard.py`(15)、`verify_task_notify.py`(22)、`verify_browse_folder_fix.py`(10)。

### 阶段 2 · 契约与工程化（3–4 天）
- 后端补 `response_model`（按域分批，先 config/scheduler/settings/device/tasks/utils 中形状稳定者）；`/openapi.json` 成为唯一契约源。
- WS 统一信封落地（**后端双写：新帧 + 旧帧并行**），前端按形状嗅探兼容旧帧；连接首帧推一次 snapshot。
- 前端 `request<T>()` + `ApiError` + 全局提示；清理 12 处空 catch 与后端静默吞异常（至少 WARNING + `exc_info`）。
- 契约统一**分两批**：前端仅在 catch 读取的端点（`install-path`、"已在执行中"、反馈缺参）可先改 4xx/409；`execute-task`、`check-update`、match/OCR、`*-status` 保持 200+业务体，字段只加不减。
- 工程化：新增 `.github/workflows`（`compileall` + `test_scene` 批次 + 生成物 diff）；`package.json` 加 `typecheck`（`vue-tsc --noEmit`，白名单 `src/api`/`src/types`/`src/stores` 渐进）；补齐 `test_scene/_run_verify_batch.py` 脚本清单。
- **风险**：此前被吞的错误开始暴露（预期）；契约改动必须前后端同批（同一 zip 可满足）。

### 阶段 3 · 去重与分层（4–6 天）
删死代码 → `legacy/{Enums,Exceptions,Config}.py` 与 `legacy/Scene/SceneGraph.py` 改一行再导出 → 模拟器路径知识单点化（`core/emulator_env.py`）→ `api/utils.py` 拆 4 个 service + 3 个 router → 消除 api 间反向 import 与 `core → api` 倒置 → `BaseTask` 5 个同体 `_cleanup_on_*` 合并、20 个 `_` handler 外移。
回归：`verify_recognizer_pruning.py --full`、`verify_schedule.py`(40)、`verify_task_schedules.py`(22)、`verify_task_execution_logging.py`(14)、`_check_legacy_refs.py`、`_check_unused_imports.py`。

### 阶段 4 · `SchedulerService` 拆分（1–2 周，风险最高，独立分支小步提交）
顺序：`DeviceRuntime` → `PresetRunner` → `IdleNotifier` → `ActivationManager` → `ScanLoop` + `RLock` 收口（`scan()` 变 `plan → execute(commands)`）→ `FreezeIncidentHandler` → `TaskStateStore` 订阅化。
⚠️ 已知会被打破的测试（源码字符串断言，须同步改写为行为断言）：`verify_touch_residue_fix.py:814`、`verify_task_scene_stuck_param.py:294`、`verify_recognizer_pruning.py:517`。

### 阶段 5 · 前端数据层（1 周）
`http.ts` + `ws/*` + `endpoints/*` + `stores/*`；`Layout.vue` 拆 composable；接入 AbortController；快照唯一写入口；「是否启用」只保留 PUT activation 一个写端点；服务端订阅过滤与背压。

---

## 5. 不建议动的部分（明确理由）

1. **41 个任务的场景处理函数本体**：每处仅 3–8 行，但 `wait_time`/`max_time`/`stable_*` 均为实机标定值。
2. **`TransitionManager._register_transitions`（250+ 装饰器）**：坐标/时序强绑定；它用**已注册跳转**建 BFS 图，与 `SceneIndex`（数据库边 + 学习边）是两套图，合并会改变寻路结果。
3. **`SceneMeta.POPUP_SCENES`/`COINCIDENT_SCENES`**：顺序敏感（set→tuple 是为可复现），改了即识别行为变更。
4. **`Recognizer` 的 OCR 增强阶梯与阈值**、**`Screen/{MuMu,LD,DroidCastRaw,U2}`**、**`OnnxOcr/*`**（PaddleOCR 派生，2 处裸 `except`）：无实机/无收益。
5. **`BaseTask.__init__(ctx: RuntimeContext)` 签名**：41 个任务文件与 36 个 verify 依赖；内部抽协作者时保持"委托不改调用点"。
6. **`frontend/dist` 入库**：热更新必需；约定"dist 只随 release/热更新提交，不与源码改动混提交"。

---

## 6. 需确认清单

1. 生产 launcher 的实际访问 Origin/端口（决定 CORS/WS 白名单内容；仓库内仅 `main.py:316` 与 vite proxy 出现 4199，launcher 实际用动态端口 `find_available_port`）。
2. `verify=True` 后打包环境是否有可用 CA（`build/release/_internal` 是否含 `certifi/cacert.pem`），否则更新会全线失败。
3. `_get_main_loop()` 首次调用是否可能发生在工作线程（与阶段 1 改动强相关）。
4. WS 慢客户端是否导致 `_batch` 无界增长（需压测）。
5. `Element.__fields__` 在 pydantic 2.11 + sqlmodel 0.24 下是否仅告警。
6. `restart_request.json` 的消费端（launcher）字段契约。
7. `check-update` 的 `full` 分支对象缺 `source`/`release_url`，前端是否读取。

---

## 7. 实施记录

> 每项完成即记录：改动点、验证命令、结果。执行者：DSH 会话 2026-10-04。

### 7.1 阶段 0（紧急修复）— 已完成

| 项 | 改动 | 验证 |
|---|---|---|
| setting.ini 读即重写 + 非原子 | `core/setting_model.py`：`__init__(readonly=)` + `_needs_write()` 免写盘 + `_serialize()` + tmp+`os.replace` 原子写 + 模块级锁；`services/settings_service.py`：进程级单例 `get_settings()` / `reset_settings_cache()` / `SettingsService(setting=, path=)` 注入 | `verify_phase0_hardening.py`（读不写盘/mtime 不变/原子写/失败不残留 .tmp/单例/路径隔离） |
| 扫描与监视线程静默死亡 | `scheduler_service._scan_loop`：间隔读取与换算移入 `try` + 非法值降级 1s + `except BaseException` → `_report_loop_death()`；`watchdog_service._monitor_loop` 同型（降级 5s） | `verify_phase0_hardening.py::BackgroundLoopHardeningTest`（4 项） |
| 停机把"临时启用"永久化 | `scheduler_service.stop()` 先 `_restore_all_temp_activations()`（按登记写回"未启用"并同步快照；临时预设模式不写盘） | `verify_temp_activation_restore.py` 扩到 **9** 项 |
| 副本配置日志串号 | `log_setup.py` 新增 `extract_config_id(explicit=, logger_name=)`（正则含 `_副本\d*`）+ `bind_config_id(logger, id)` 过滤器；`WebSocketLogHandler._extract_config_id(record_or_name)` 优先读 `record.config_id`；`parse_log_lines` 复用同一提取器；`config_model` / `legacy/Config` / `SchedulerService` 建 logger 时显式绑定 | `verify_log_ws_payload.py` 扩到 **6** 项（副本 id 3 例 + 显式绑定优先 + bind 打标） |
| `TaskCompleted` 双参（**严重度更正为 P2**） | `MiJingTanXian.py:66` 改 f-string 单参数 | `verify_phase0_hardening.py::MiJingTanXianRaiseTest` |

> ⚠️ **实测更正**：子代理初判"`TaskCompleted("msg", n)` → TypeError → 完成被误判为未捕获异常"。实测证伪：`Exception("msg", 3)` 合法（args 是元组），不会翻转完成/异常语义；真实后果仅为日志渲染成元组文本、`%d` 不展开。已按日志质量修复并写进 `verify_phase0_hardening.py`。

### 7.2 阶段 1（失控面收敛）— 已完成

| 项 | 改动 | 验证 |
|---|---|---|
| 配置写盘三线程并发 | `core/config_model.py`：模块级 `_CONFIG_WRITE_LOCK` + tmp+`os.replace` 原子写 + 失败清理 .tmp | 回归批（`verify_activation_path_fix` / `verify_force_preempt` / `verify_temp_activation_restore` 等读写配置的脚本全绿） |
| 阻塞端点移出事件循环 | `api/scheduler.py` 的 start/stop/precheck/execute/toggle-activation 与 `api/device.py` 的 6 个端点、`api/utils.py` 的 log-history/dependency-check/check-update/feedback-options/serial-list 一律改同步 `def`（FastAPI 线程池）；`resource.py` 两个上传端点改为 `await file.read()` + `run_in_threadpool(落库/同步图/cv2)` + 10MB 上限 | `verify_api_event_loop_safety.py`（12 项，含逐端点 sync 断言与"读端点不得创建调度器"的源码防回退） |
| 事件循环注入 | `api/scheduler.py` 新增 `bind_main_loop(loop)` + `_get_main_loop_or_none()`（取不到返回 None 并告警，不再抛 RuntimeError）；`main.py` lifespan 用 `asyncio.get_running_loop()` 注入 | `verify_api_event_loop_safety.py::MainLoopInjectionTest` |
| GET 无副作用 + 注册表加锁 | `peek_scheduler(id)`（不创建）；`/status`、`/tasks` 改走 peek 并返回同形状"未运行"快照；`_schedulers_lock`（RLock）覆盖 check-then-create；`destroy_scheduler` 加锁 | 同上（`PeekSchedulerTest`） |
| 优雅停机 | `SchedulerService.stop()` 新增 `_join_task_threads()`（共享 5s 预算，未退出者 WARNING）；`api/scheduler.py` 新增 `shutdown_all_schedulers(timeout)`；`main.py` 关闭段 `_shutdown_schedulers()` + `_dispose_resource_db()`（释放 SQLAlchemy engine） | 同上（`StopJoinsTaskThreadsTest`）+ 回归批 |
| 热更新 TLS 与完整性 | `api/utils.py`：`_UPDATE_VERIFY_TLS=True`（7 处调用点统一），新增 `_verify_update_integrity()`——GitHub zipball 顶层目录名 `{repo}-{sha}` 与 `_get_latest_sha()` 比对，不一致即 `RuntimeError` 中止（Gitee 无 sha 时告警放行） | `verify_security_hardening.py::UpdateSecurityTest` |
| SPA 路径穿越 | 新增 `backend/runtime/paths.py`（`safe_component` / `safe_join` / `safe_join_path` / `is_within`）；`main.py` 的 SPA 回退改用 `safe_join_path` | `verify_security_hardening.py`（含源码接线断言；端到端 TestClient 用例因环境缺 httpx 而 SKIP） |
| 反馈打包越界 | `api/utils.py`：`username`/`date`/`task_names` 走 `safe_component` + `_DATE_DIR_RE` 校验 + 与真实目录求交集 + `is_within(log_root)` 兜底断言 + save_path 非空校验；`log_setup.get_config_file_handler` 的 username 也清洗 | 同上（`FeedbackPathTest`、`SafePathTest`） |
| CORS / WS 暴露 | `main.py` 删除 `allow_origins=["*"]` → 显式本地白名单；`api/ws.py` 新增 `_origin_allowed()`（`urlparse` 严格校验 host ∈ {127.0.0.1, localhost, ::1}）+ 两个 WS 端点接入 `_reject_if_origin_denied`（`close(1008)`） | 同上（`CorsTest`、`WsOriginTest`） |

### 7.3 阶段 2（契约与工程化）— 部分完成

| 项 | 改动 | 验证 |
|---|---|---|
| 前端类型检查 | 新增 `frontend/tsconfig.typecheck.json`（白名单 `src/api` / `src/types` / `src/stores`）+ `package.json` 的 `typecheck` 脚本（用已安装的 tsc 5.9.3，无需新增依赖） | `npx tsc -p tsconfig.typecheck.json` → OK（并**修掉** 2 个既有类型错误：`WSMessage` 缺 `'reconnected'`、缺 `ts` 字段） |
| 前端统一请求层 | 新增 `frontend/src/api/http.ts`：唯一 axios 实例 + `ApiError{kind,status,detail,response}` + `normalizeError` + `errorMessage` + `request<T>()` + 在途请求登记与 `abortAllInFlight()`；`client.ts` 改为再导出（默认导出保留），**既有 `e.response.data.detail` / `e.message` 取值方式继续可用**（向后兼容，无需一次改 50+ 处） | `npx tsc` + `vite build` 通过 |
| 清理静默失败 | `TaskConfigPanel.vue`(3) / `PresetEditor.vue`(3) 的 `.catch(() => {})` 改为 `message.error(...errorMessage(e))` | typecheck + build |
| 回归入口 | `test_scene/_run_verify_batch.py` 重写：自动发现全部 `verify_*.py`、区分 HEAVY / KNOWN_STALE（每项附证据）、`--full` / `--stale` / `--list`、失败返回非 0 | 见 7.4 |
| CI | 新增 `.github/workflows/ci.yml`（后端 compileall + 回归批 + 关键模块导入；前端 typecheck + build）；`.gitignore` 由忽略整个 `.github/` 改为 `.github/*` + 保留 `.github/workflows/` | 本地跑通等价命令 |
| WS 统一信封（v1） | `backend/api/ws.py`：信封 `{v,type,seq,ts,config_id,payload}` + `ConnState{protocol,seq,config_ids}` + `subscribe` 能力协商 + **双写**（legacy 连接仍收旧帧，含 `["log",batch]`）+ `log.batch` 单帧上限 200/`dropped` + 连接级订阅过滤 + 发送 `wait_for(2s)` 判慢客户端断开；前端新增 `wsProtocol.ts`（三种帧形态归一 + v1 type 映射回 legacy type，消费端零改动）、`ws.ts` 连接后发 `subscribe{protocol:1}` 并新增 `on(type,handler)` 注册表 | `verify_ws_protocol_v1.py`（23 项，后端帧/协商/双写/截断/订阅/慢客户端/源码防回退）、`verify_ws_protocol_frames.ts`（33 项，前端解析器，node 直跑）、**`verify_ws_dual_write_e2e.py`（3 项，进程内真实 uvicorn + 真 WS 客户端验证"legacy 永不收信封、v1 只收信封"）** |
| 待办（未完成） | ① `api/utils.py` 拆分与 `runtime/events.py` 事件总线；② `services/scheduler_registry.py`；③ 敏感设置掩码；④ `SchedulerService` 拆分（阶段 4） | — |

### 7.4 回归结果（2026-10-04）

- 快速集 `python -X utf8 test_scene/_run_verify_batch.py`：**30/30 PASS**（含新增 `verify_phase0_hardening.py` 16 项、`verify_api_event_loop_safety.py` 12 项、`verify_security_hardening.py` 13 项、`verify_api_contracts.py` 5 项、`verify_ws_protocol_v1.py` 23 项，以及 2 个前端 TS 脚本 `verify_log_dedupe.ts` / `verify_ws_protocol_frames.ts` 由 node 直跑）。
- 重型集（`--full`，另行执行）：`verify_ws_dual_write_e2e.py` **3/3 PASS**（进程内真实 uvicorn + 真 WS 客户端）。
- 因本次改造同步更新的既有测试：`verify_log_ws_payload.py`（4→6）、`verify_temp_activation_restore.py`（7→9）、`verify_consume_stamina_params.py`（3 处 `asyncio.run` → 直接调用）、`verify_manual_execute_guard.py`（同上）。
- 归类为既有滞后（不计入门槛，见 `_run_verify_batch.py::KNOWN_STALE` 的逐项证据）：`verify_startup_notice.py`、`verify_declare_next_scene.py`、`verify_transition_stall_guard.py`、`verify_renfatijiangli_flow.py`、`verify_renfatijiangli_time.py`、`verify_pending_scene_edges.py`。
- 前端：`tsc -p tsconfig.typecheck.json` OK；`vite build` OK（13.7s，dist 已更新）。

### 7.6 端到端冒烟（2026-10-04，新代码实例）

- 端口说明：本机 4199 被用户正在运行的后端占用，故新代码在 **4299** 起临时实例验证（验证后已关闭；用户实例未受影响）。
- REST：`/api/health` 200；`/api/utils/version` 200；**`/api/scheduler/status/Config_1` 返回 `{"running":false,"task_count":0,"mode":"persistent"}`、`/api/scheduler/tasks/Config_1` 返回 `[]` —— 读状态不再创建调度器实例**（旧实现会实例化 `SchedulerService`）；`/api/configs/Config_1` 200。
- WebSocket（真实连接）：同源 Origin 连接成功并回 `pong`；**恶意 Origin（`http://evil.example.com`）被拒（HTTP 403 / close 1008）**；无 Origin 的非浏览器客户端放行。
- lifespan：新实例的启动段（日志、`bind_main_loop`）与关闭段（`shutdown_all_schedulers`、`_dispose_resource_db`、`_kill adb`）均正常执行、无异常。

### 7.7 新增待办（本轮发现，未实施）

1. **敏感设置明文返回（P1，隐私）**：`GET /api/settings/` 返回整段 `[助手设置]`，其中包含 `GithubPAT` 与 `二级密码` 明文（前端 `Settings.vue:164` 已按"敏感项"做密文显示 + 显隐切换，说明 UI 层已识别敏感，但接口层没有）。旧 CORS `*` 下这等于对任意网站公开。建议：`get_all()` 对敏感键返回掩码（如 `已配置/未配置` 或 `***`），显隐切换改走单独的 `GET /api/settings/{section}/{key}?reveal=true`；用户 WIP 里新增的 `_github_pat_configured()` 正是这个方向。
2. **`adb kill-server` 的副作用（已缓解）**：lifespan 关闭段与 `atexit` 都会执行 `adb kill-server`（issue #4 的清理）。副作用：任何"短命的后端实例"（冒烟/测试/工具）退出时都会杀掉**用户正在运行的实例**所依赖的 adb server —— 本会话实测踩到两次。已加 `XUAN_SKIP_ADB_CLEANUP=1` 环境变量跳过（`backend/main.py::_shutdown_adb_server`），端到端测试在导入前设置该变量（`atexit` 注册的是导入时的原始函数对象，只改模块属性拦不住）；真正的默认行为（issue #4 修复）保持不变。
3. **`api/utils.py` 仍在事件循环里做文件/JSON 之外的重活**：`/feedback/package` 起线程（OK），但 `_do_apply_update` 的批量 `shutil.copy2`（数千文件）在后台线程里逐文件写 `_UPDATE_STATUS`（有锁）——可接受但应改为 job + 进度事件（阶段 2 未完成项 ③）。

### 7.9 WS 统一信封（v1 协议，含旧帧兼容）— 已实施（2026-10-04）

> 原计划见本节历史版本；实际实现与设计的差异与验证如下。

**已实现**
- 信封 `{v,type,seq,ts,config_id,payload}`（`build_frame`）+ 不变式（`config_id` 仅在顶层）。
- `ConnState{protocol, seq, config_ids}`；`ConnectionManager` 改为连接→状态映射，广播取快照
  遍历（修掉"迭代中 await 被 disconnect 改写"的漏发）。
- **能力协商**：连接首帧 `hello`；客户端发 `{"type":"subscribe","protocol":1}` 后该连接切 v1
  （可带 `config_ids` 做连接级订阅；无归属日志恒放行）。
- **双写**：`broadcast_dual()` 让 legacy 连接继续收到与改造前逐字等价的旧帧
  （`["log", batch]` / 单条对象 / `status` / `task_state` / `scheduler_snapshot`），v1 连接收
  `log.batch` / `status` / `task.state` / `scheduler.snapshot`。
- 背压：`log.batch` 单帧 ≤200 条 + `dropped` 计数；发送 `wait_for(2s)`，超时判慢客户端断开。
- v1 type 表：`hello` / `log.batch` / `status` / `task.state` / `scheduler.snapshot` /
  `error` / `log.truncated`；未知 type 必须被忽略。
- 前端：`wsProtocol.ts`（纯解析器，三种帧形态归一；**`task.state`→`task_state`、
  `scheduler.snapshot`→`scheduler_snapshot` 映射回 legacy type，Dashboard/Layout/PresetEditor/
  LogPanel 零改动**）；`ws.ts` 连接后协商、`on(type,handler)` 注册表（与 `onMessage` 并存）。
- 修正一处**行为回归**：旧后端在"单条日志"时发对象帧 `{type:'log',...}`，最初实现把它只当
  消息派发而不再入日志面板 → 解析器补回 `logs` 帧（并保留旧的"同时派发 message"语义）。

**验证**（三层）
1. `verify_ws_protocol_v1.py` 23 项：信封形状/seq 单调/双写分流/数组帧保留/截断+dropped/订阅过滤/慢客户端断开/`subscribe` 解析（含非法 JSON）/源码防回退。
2. `verify_ws_protocol_frames.ts` 33 项：前端解析器覆盖三种帧形态与全部 v1 type（node 直跑）。
3. `verify_ws_dual_write_e2e.py` 3 项：**进程内真实 uvicorn + 真实 WebSocket 客户端** —— legacy 连接全程收不到信封且仍收到旧形态日志帧；v1 连接首帧 `hello`、随后 `log.batch` 信封（`seq` 单调、`config_id` 仅在顶层、条目字段齐全）；两条连接共存互不串帧。

**发布顺序（硬约束）**：后端双写 → 前端切换 → 观察 ≥2 个 release → 删旧帧。
本仓库的 dist 与 backend 在同一 zip 内分发，故本轮已完成"后端双写 + 前端兼容"两步；
**删旧帧**留待 ≥2 个 release 之后。

**遗留**：`_periodic_flush` 的 `while True` 仍无退出条件（P2-15），退出依赖进程结束；
若后续要做优雅关闭需加 `asyncio.Event`。

### 7.12 阶段 3（去重与分层）实施记录（2026-10-04）

| 子项 | 状态 | 改动与验证 |
|---|---|---|
| 3.1 删死代码 | ✅ | 删文件：`core/exceptions.py`（0 引用 + `Stop` 重复定义两次）、`legacy/Setting.py`（0 引用，缺 `optionxform` 会小写化键名）、`core/recognizer_engine.py`（4 行转发壳）。删方法/接口：`PriorityQueue.{dequeue,peek,reheapify,refresh_task}`、`_cancel_scan_loop`（空实现）、`/api/configs/{id}/task-priorities` 三层死链（路由 + `UpdateTaskPrioritiesRequest` + `ConfigService.{set,get}_task_priorities` + `get_task_order` + 前端 `configApi.updateTaskPriorities`）、重复的 `/api/utils/serial-list`、`_RELEASES_URL`、`_BINARY_FIELDS`。`_github_pat_configured` 从死函数接线到 `/api/utils/dependency-check`（返回布尔、不回传 token）。验证：`verify_module_consolidation.py`（13 项） |
| 3.2 同义模块收敛 | ✅ | `core/enums.py` / `core/config_model.py` / `core/scene_graph.py` 成为唯一实现，`legacy/{Enums,Config}.py` 与 `legacy/Scene/SceneGraph.py` 改为再导出（两条 import 路径 `is` 同一对象）；异常类保留 `legacy/Exceptions.py` 为唯一实现。验证同上（含 SceneGraph 的 `bgra=None` 内存优化防回退断言） |
| 3.3 模拟器路径单点化 | ✅ | 新增 `core/emulator_env.py`（候选清单 / 文件检查 / `MuMuManager info -v` 与 `ldconsole list2` 解析 / 16:9 判定）；改写 `validate.py`、`device.py::check_environment`、`api/scheduler.py::_precheck_screenshot_path`、`scheduler_service.py::_pre_start_environment_check`、`Screen/MuMu.py`（用户可见文案保持原样）。验证：`verify_emulator_env.py`（12 项，含"除 emulator_env 外不得再出现带目录的候选字面量 / 旧内联元组 / 重复 16:9 判定式"的防回退检查） |
| 3.4 `api/utils.py` 拆分 + 消除反向 import | ✅ | `backend/api/utils.py`(1550 行 / 12 路由) → 包：`common.py`(共享状态与日志解析/平台与版本) `deps.py`(依赖与 OCR 探测) `logs.py` `/update.py`(648 行，更新链路) `feedback.py` `system.py` + `__init__.py` 门面（聚合 4 个子路由 + 逐一再导出旧模块全部 90 个名字）。分层倒置全部消除：新增 `runtime/log_sinks.py`（WS handler 注册表，core/services 不再 import `api.ws`）、`core/settings_store.py`（`SettingsService` 实现下沉，services 再导出）、`core/version_info.py`（版本工具唯一实现，`runtime_info` 改为委托）、`runtime/module_registry.py`（`api` 不再 import `main`）。验证：`verify_layering_rules.py`（16 项：ast 级分层规则 + 包等价性 + 注册表 + 版本比较行为） |
| 3.5 BaseTask 收敛 | ✅ | 21 个内置 `@TransitionOn` 处理函数（方法名全是 `_`）从 `BaseTask` 类体外移到 `Task/default_transitions.py`（普通函数 + `DEFAULT_TRANSITION_HANDLERS` 表 + `install_default_handlers`），BaseTask 1712 → 1589 行；五个同体 `_cleanup_on_*` 合并为 `_cleanup(reason)` + 5 个别名（"停止连点"实现 5 处 → 1 处）。验证：`verify_base_task_consolidation.py`（8 项，含 MRO 合并语义与源码防回退） |

回归批：**33/33 PASS**（30 → +`verify_module_consolidation` +`verify_emulator_env` +`verify_base_task_consolidation`）。
三个既有滞后脚本失败数未变（`verify_transition_stall_guard` 2 / `verify_declare_next_since` 1 / `verify_startup_notice` 2）。

### 7.13 下一步实施单

**A. 阶段 3.4（`api/utils.py` 拆分 + 分层倒置）— 已完成，见 §7.12 / §7.15**

**B. 阶段 4（`SchedulerService` 1432 行 / 47 方法拆分，高风险；方案见 §7.17）**：按 §4 顺序
DeviceRuntime → PresetRunner → IdleNotifier → ActivationManager → ScanLoop+RLock（`scan()` 改
`plan → execute(commands)`）→ FreezeIncidentHandler → TaskStateStore 订阅化；同步把 3 处
`inspect.getsource` 断言（`verify_touch_residue_fix.py:814`、`verify_task_scene_stuck_param.py:294`、
`verify_recognizer_pruning.py:517`）改写为行为断言。

**C. 阶段 5（前端数据层）**：`api/http.ts`（已有）+ `api/endpoints/*` + `stores/*` 目录化；
`Layout.vue`(1072 行) 拆 `useConfigs/useSchedulerControl/useTaskTree/useStartupChecks`；
接入 `abortAllInFlight()`（http.ts 已提供）到切配置；快照唯一写入口
`schedulerStore.applySnapshot(configId, seq, payload)`（当前 3 处写入，其中 Dashboard/PresetEditor
无 seq 保护）；「是否启用」收敛为单一写端点（现在 `TaskConfigPanel` 同时写 config 与 activation）。

**D. 阶段 3 收尾可选（低优先）**：`services/{update_service,feedback_service,log_service}.py`
（把 `api/utils/{update,logs,feedback}.py` 的业务逻辑再下沉，路由只做参数映射）——当前 3.4
只做了"按职责拆包 + 分层倒置"，业务逻辑仍在 api 层；以及 §7.7 敏感设置掩码。

### 7.10 阶段 2 收尾清单（仍未实施）

1. `api/utils.py`（1495 行 / 13 端点）拆为 `api/utils/{logs,update,feedback,system}.py` +
   `services/{update_service,feedback_service,log_service}.py`（**已并入 §7.13-A，含分层倒置一并处理**）。
2. `runtime/events.py` 事件总线：消除 `core`/`services` 对 `api.ws` 的反向依赖
   （`core/config_model.py:39`、`services/scheduler_service.py:197/495`）（**同上**）。
3. `services/scheduler_registry.py`：把 `api/scheduler._schedulers` 收敛为带生命周期的注册表。
4. 敏感设置掩码（§7.7 第 1 条；`_github_pat_configured` 已接线，前端掩码与 reveal 接口未做）。
5. `SchedulerService` 拆分（阶段 4，见 §4 阶段 4 的顺序与风险）。

### 7.15 阶段 3.4 实施细节与"patch 目标"迁移说明（2026-10-04）

**拆分映射**（机械搬运，一次性脚本校验：切片可独立 `ast.parse`、68 个顶层名字恰好落到唯一模块、
旧模块 90 个名字（含 import）全部仍可从包访问）：

| 新模块 | 行数 | 内容 |
|---|---|---|
| `api/utils/__init__.py` | 135 | 聚合 4 个子路由 + 逐一再导出旧模块所有名字 + `import requests`（patch 目标）+ `logger` |
| `api/utils/common.py` | 313 | `_UPDATE_STATUS`/`_FEEDBACK_STATUS`/`_STATUS_LOCK`、`_read_tail`/`parse_log_lines`、`_get_config_username`、更新源平台与 PAT、`_DATE_DIR_RE` |
| `api/utils/deps.py` | 214 | `check_ocr_accel` / `_probe_onnxruntime_providers` / `check_dependency` |
| `api/utils/logs.py` | 104 | `GET /log-history` |
| `api/utils/update.py` | 648 | `/version` `/dependency-check` `/check-update` `/apply-update` `/apply-release-update` `/update-status` + 完整性校验/备份/重启请求 |
| `api/utils/feedback.py` | 239 | `/feedback/options` `/feedback/package` `/feedback/package-status` |
| `api/utils/system.py` | 92 | `/browse-folder` `/open-log-dir` + `_latest_log_date_dir` |

**测试 patch 目标迁移**（拆包/下沉改变了"函数体内的全局查找"位置，属必要适配，覆盖未削弱）：
- `verify_ocr_cpu_fallback.py`：`utils_mod.get_real_path` / `utils_mod._get_config_username`
  → `backend.api.utils.system.*`（`open_log_dir` 已迁至 system；`os.startfile` 仍是 `os` 模块属性，无需改）
- `verify_security_hardening.py`：`utils_api._get_latest_sha` → `backend.api.utils.update._get_latest_sha`
- `verify_browse_folder_fix.py` / `verify_module_consolidation.py` / `verify_security_hardening.py`：
  源码级断言改为读整包（`backend/api/utils/*.py`）
- 未改动的既有用法仍成立：`mock.patch("backend.api.utils.requests.get")`（patch 的是 requests
  模块对象属性）、`assertLogs("backend.api.utils")`（6 个子模块 logger 同名）、
  `utils_mod.os.startfile`、`utils_api.browse_folder/_extract_browse_pidl/open_log_dir`（包级再导出）

**遗留**：`api/utils/{update,feedback,logs}.py` 的业务逻辑尚未下沉到 `services/*_service.py`
（§7.13-D）；`api/utils/update.py` 648 行仍是最大的单文件。

### 7.16 阶段 3 最终回归快照（2026-10-04）

- `compileall backend` OK；回归批 **34/34 PASS**（新增 `verify_layering_rules.py` 16 项）
- `verify_ws_dual_write_e2e.py` 3/3 OK（**证明 `runtime/log_sinks` 注册表端到端有效**：
  config 日志经 main.py 注册的 WS handler 推送前端）
- 分层规则（ast 精确判定）：`core/**`→`api|services` **0 处**、`services/**`→`api` **0 处**、
  `api/**`→`main` **0 处**
- 既有滞后脚本失败数未变（2 / 1 / 2）
- 本轮提交：`7c92b32d`(3.1+3.2) → `2cb2bad1`(3.3) → `8c56d3b0`(3.5) → 3.4（拆包 + 分层）

### 7.17 阶段 4 执行方案（`SchedulerService` 1432 行 / 47 方法，2026-10-04 侦察）

**约束（侦察所得，决定拆分策略）**
- 面向测试的私有方法（必须继续可从实例调用）：`_device_serial`、`_ensure_no_stale_contacts`、
  `_execute_done_callback`、`_handle_scene_stuck`、`_join_task_threads`、`_notifications_enabled`、
  `_notify_account_idle`、`_on_task_activate_request`、`_process_pending_activations`、`_scan_loop`、
  `_scan_once`、`_sync_task_state`、`_update_task_status`
- 面向 API/测试的公开面：`start` / `stop` / `scan` / `get_status` / `get_tasks_status` /
  `execute_task_now` / `toggle_task_activation`（调用次数：stop 30、execute_task_now 17、scan 12、start 9）
- 源码级断言**只有 1 处真正针对本类**：`verify_touch_residue_fix.py:812-817` 断言
  `SchedulerService.start` 源码含"调度器启动前自检"、`stop` 源码含"调度器停止后自检" 与
  `_wait_clicker_stopped`（另两处 §4 提到的断言实际在 `watchdog_service.py` / `api/resource.py`）
- 测试构造方式：`SchedulerService(config=<fake cfg>)`，随后直接替身 `svc.config` / `svc.device`

**策略：先"抽协作者 + 保留同名转发"，再在收尾阶段改写测试并删除转发。**
每一步都是"搬方法体 + 加 1 行转发 + 跑全批"，转发保证 13 个私有方法与 1 处源码断言
全部继续成立，任一步可独立回退。

| 步骤 | 新模块（实际落在 `backend/services/scheduler/`，比原计划的 `services/runtime/` 更贴近"调度器内部"） | 搬走的方法 | 状态 |
|---|---|---|---|
| 4.0 | `constants.py` | `IDLE_NOTIFY_THRESHOLD`（协作者需要常量而服务需要 import 协作者 → 放同模块会循环导入） | ✅ |
| 4.1 | `device_runtime.py` | `_device_serial` `_shutdown_clicker_engine` `_ensure_no_stale_contacts` `_wait_clicker_stopped` `_wait_device_ready` | ✅ |
| 4.2 | `preset_runner.py` | `_init_once_pending` `_reset_once_progress` + **持有** `pending_once_tasks`/`_preset_total`/`_completed_count` | ✅ |
| 4.3 | `idle_notifier.py` | `_notifications_enabled` `_notify_user` `_notify_preset_finished` `_notify_account_idle` + **持有** `_idle_notified` | ✅ |
| 4.4 | `activation_manager.py` | `toggle_task_activation` `_ensure_task_runnable` `_restore_all_temp_activations` `_restore_temp_activation` `_reject_manual_execute_outside_window`（4.4a）+ `_on_task_activate_request` `_schedule_task_activation` `_process_pending_activations` `_skip_expired_activation` + 持有 `_temp_activated_tasks`/`_pending_activate_tasks`（4.4b） | ✅ 分两次提交 |
| 4.5 | `scan_loop.py` | `_start_scan_loop` `_scan_loop` `_report_loop_death` `scan` `_scan_once` + RLock（`scan()` 改 `plan → execute(commands)`） | ⏳ |
| 4.6 | `freeze_handler.py` | `_on_watchdog_freeze` `_process_freeze_event` `_handle_scene_stuck` `_handle_game_frozen` `_handle_emulator_frozen` | ⏳ |
| 4.7 | `task_state_store.py` | `get_status` `get_tasks_status` `_update_task_status` `_push_snapshot` `_sync_task_state` + 状态字典（订阅式 `on_change`） | ⏳ |

**已落地的两条兼容手法（4.1~4.3 验证有效，后续步骤沿用）**
1. **同名转发方法 + 同名 property**：搬走的方法在服务侧保留 3 行转发；搬走的状态
   （`pending_once_tasks` / `_preset_total` / `_completed_count` / `_idle_notified`）在服务侧
   以 property（含 setter）暴露 —— 既有读写点与测试的直接赋值逐字不变。
2. **保留 monkeypatch 扩展点**：`_notify_user` 这类会被测试用实例属性替换的方法，
   协作者内部必须**回调服务方法**（`service._notify_user`），而不是直接调用自己的同名实现；
   否则 `sched._notify_user = ...` 的捕获写法会静默失效（4.3 首版即踩此坑，已修）。

**收尾（4.8）**：把 `verify_touch_residue_fix.py:812-817` 的源码断言改写为行为断言
（`assertLogs` 捕获"启动前自检/停止后自检"+ 替身 `device_runtime` 断言 `wait_clicker_stopped` 被调用），
然后删除 13 个转发方法；同步更新 `verify_*` 里对私有方法的直接调用改为针对协作者。

**回归门**：每步跑 `test_scene/_run_verify_batch.py`（34 个脚本），4.4 与 4.5 完成后额外跑
`--full`（含 HEAVY）与 `verify_ws_dual_write_e2e.py`。

### 7.18 阶段 4 进度快照（2026-10-04，4.1~4.4 已完成）

| 项 | 数值 |
|---|---|
| `SchedulerService` 行数 | **1604 → 1335**（−269，−17%） |
| 新协作者模块 | `services/scheduler/{constants,device_runtime,preset_runner,idle_notifier,activation_manager}.py`（+`__init__.py` 门面） |
| 服务侧保留 | 20 个同名转发方法 + 7 个同名 property（`pending_once_tasks`/`_preset_total`/`_completed_count`/`_idle_notified`/`_temp_activated_tasks`/`_pending_activate_tasks`） |
| 测试面 | 零改动（含 `sched._notify_user = ...` 捕获、`sched.pending_once_tasks = [...]`、`sched._pending_activate_tasks.append(...)`、`svc._temp_activated_tasks = {}`、`from ...scheduler_service import SOURCE_*`、`inspect.getsource` 源码断言） |
| 回归 | 每步后全批 **34/34 PASS**；7 个激活相关脚本全 OK；`compileall` OK |
| 提交 | `3d856096`(4.1) → `6085a244`(4.2) → `78b1ee17`(4.3) → `59f488b2`(4.4a) → `a4f40ab3`(4.4b) |

**协作者访问方式（阶段 4 定稿）**：`_collaborator(attr, factory)` + 同名只读 property **懒加载**。
起因：HEAVY 脚本 `verify_touch_residue_fix.py` 用 `object.__new__(SchedulerService)` 绕过
`__init__`，4.1 首版把协作者装配写在 `__init__` 里 → 该脚本新增 5 个
`AttributeError: ... has no attribute 'device_runtime'`。改为惰性创建后两种构造方式都可用。

**HEAVY 脚本基线核对方法（可复用）**：`git worktree add <tmp> <重构前的 commit>` →
在临时工作区跑脚本 → `git worktree remove`。据此确认 `verify_touch_residue_fix.py`
在阶段 4 起点即为 **2 failures / 23 errors**（Control 层与用户 WIP 不一致），
当前数值与基线**完全一致**；基线已写入 `_run_verify_batch.py` 的 HEAVY 条目注释。

**踩坑记录（供后续步骤复用）**
1. 4.2 首版遗漏了测试对 `sched.pending_once_tasks = [...]` 的**直接赋值** → property 必须配 setter。
2. 4.3 首版把 `notify_preset_finished` 的文案改成"拼接 suffix + lstrip('，')"，与原文案不等价
   （丢逗号）→ 已改回逐字原文；**搬文案时不要做"等价改写"**。
3. 4.3 首版漏掉 `self.idle_notifier = IdleNotifier(self)` 装配 → 15 个用例报
   `AttributeError`；4.4 起改懒加载后该类问题不再可能出现。
4. 4.3 首版让协作者直接调用自己的 `notify_user` → 3 个用 `sched._notify_user = ...` 捕获通知的
   测试静默失败（0 != 1）；改为回调 `service._notify_user` 后恢复。
5. 4.4b 把 `SOURCE_MANUAL`/`SOURCE_ACTIVATION` 移入 `constants.py`：协作者需要它们，
   若从 `scheduler_service` 导入会形成循环导入；测试从 `scheduler_service` 导入的写法靠
   同名再导出保持。

### 7.11 事故与恢复记录（重要）

### 7.11 事故与恢复记录（重要）

- **事故**：用 PowerShell 5.1 批量替换 `backend/api/device.py` / `backend/api/utils.py` 的 `async def` → `def` 时，`Get-Content`/`Set-Content` 按系统 ANSI（GBK）读写 UTF-8 文件，导致大量中文与部分 ASCII（含引号）字节丢失，两文件语法损坏。
- **恢复**：`device.py` 在损坏前无未提交改动 → `git checkout` 从 HEAD 恢复并重做 6 处签名改动；`utils.py` 有 WIP → 以 HEAD 为基底重放本会话改动，并从**损坏前编译产物** `__pycache__/utils.cpython-312.pyc` 精确恢复 WIP 内容（3 个新函数 `_get_github_pat` / `_platform_headers` / `_github_pat_configured` + 5 处调用点改为 `_platform_headers(pf)`），随后用 .pyc 的**全部代码对象 (firstlineno, 字符串常量)** 逐项校验，50/50 完全一致后才写盘。
- **教训（已写入工程约束）**：禁止用 PowerShell 文本 cmdlet 改写含中文的源码文件；批量改动一律用 `edit` 工具或 Python（显式 `encoding="utf-8"`）。恢复脚本执行后已删除（一次性脚本，不留在仓库）。

