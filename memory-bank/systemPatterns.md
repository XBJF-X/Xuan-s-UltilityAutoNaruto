# systemPatterns.md — 系统架构与设计模式

## 总体架构（V2）

```
┌──────────────────────────────────────────────┐
│  Electron 主进程（frontend/electron/）         │
│   - 创建窗口加载 frontend/dist                 │
│   - 以子进程启动 backend（FastAPI）            │
└──────────────────────┬───────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼───────────────────────┐
│  FastAPI 后端（backend/main.py，端口 4199）    │
│   ├── SPA 静态托管（依赖 frontend/dist）        │
│   ├── /api/* REST 路由                         │
│   └── /ws/logs、/ws/status WebSocket          │
└──────────────────────┬───────────────────────┘
                       │ 模拟点击 / adb / 图像识别
┌──────────────────────▼───────────────────────┐
│  游戏（火影忍者手游，通过 adb 控制设备）         │
└──────────────────────────────────────────────┘
```

## 后端分层

| 目录 | 职责 |
|---|---|
| `backend/main.py` | FastAPI 入口：注册路由、SPA 中间件、启动 WebSocket 日志 handler、异常捕获 |
| `backend/utils.py` | 工具函数（get_real_path 等） |
| `backend/log_setup.py` | 日志配置（文件轮转、双通道） |
| `backend/api/` | REST + WS 路由模块 |
| `backend/services/` | 业务服务（config_service.py 配置管理、scheduler_service.py 调度器、settings_service.py 全局设置、watchdog_service.py 超时监视器） |
| `backend/core/` | 核心模型与逻辑（config_model.py Config 模型、setting_model.py、scene_graph.py、recognizer_engine.py、enums.py、exceptions.py、legacy/） |
| `backend/tools/` | 底层工具（adb 控制、图像识别） |

## 调度器模式（SchedulerService）

- `SchedulerService`（backend/services/scheduler_service.py）无头调度器，严格遵循原版 Scheduler.py 三态（等待2→就绪1→执行0）扫描逻辑，剥离 PySide6/TimerThread。
- **线程模型**：`start()` 启动 daemon 后台扫描循环线程（`_scan_loop`），按 `扫描间隔`（配置项，默认 1000ms）周期调用 `scan()`；用 `_scanning` 标志防重入。
- **PriorityQueue**（heapq + task_dic）维护所有任务实例，支持 enqueue/dequeue/refresh/update_task_status/按状态取任务。
- **logger 命名**：`SchedulerService_{config_path.stem}`（如 `SchedulerService_Config_1`），须包含 `Config_N` 才能被 WebSocketLogHandler 归类；初始化时为 config 挂载专属文件 handler（`log/<用户名>/<日期>/Xuan.log`），并 `propagate=True` 继续写入 Main.log。
- **延迟初始化 `_lazy_init()`**：启动时才导入重型依赖（Device、Operationer、TransitionManager、TASK_TYPE_MAP），构造 device/operationer/transition_manager 实例，并注入 `_save_screenshot` 截图回调（保存到 `log/<用户名>/<日期>/screenshot/<任务名>/`）。
- **任务执行**：扫描时等待队列到期任务 → 就绪队列；就绪队列取优先级最高者执行（`min(heap)`）；执行中遇更高优先级任务可**抢占**（stop 当前任务）。回调 `on_status_change`/`on_task_state_change` 衔接前端 WebSocket。
- **截图复用**：`start()` 后 API 截图接口（device.py）优先复用调度器的 `sched.device.screen_cap()`，避免重复建立截图连接。调度器**未启动**时，`device.py` 的 `_capture_frame()` 临时实例化 `utils.Base.Device.Device`（同时建立 control_manager + screen_manager，MuMu/LD/ADB 截图依赖 ControlManager 初始化连接），经 `screen_manager.screencap()` 取帧，`finally` 统一 `release()` 释放两管理器；Device 类型标注指向旧版 Config，与调度器同款用法加 `type: ignore[arg-type]`。

## 配置管理模式（V3）

- `ConfigService`（backend/services/config_service.py）管理多个配置实例，模块级单例 `shared_config_service` 供所有 API 共享，确保 Config 对象内存唯一。
- `Config` 模型（backend/core/config_model.py，自 utils/Base/Config.py 迁移，剥离 PySide6 依赖）：
  - 加载配置时与 `src/DefaultConfig.json` 递归合并（V3 配置文件版本）：用户配置覆盖默认配置，缺失项用默认值补充；任务仅合并"是否启用/下次执行时间/执行参数.当前值/执行进度"。
  - 提供 get/set 体系：`get_config`/`set_config`（顶层）、`get_task_base_config`/`set_task_base_config`（任务共有属性）、`get_task_exe_param`/`set_task_exe_param`（执行参数"当前值"）、`get_task_exe_prog`/`set_task_exe_prog`（执行进度）。
  - 配置文件名 `Config_N.json`，存放于 `config/` 目录（get_real_path("config")）。
- `shared_config_service` 提供基础操作：list/get/create/delete/rename、set_config_value/set_task_base/set_task_exe_param、get_task_schema（从 DefaultConfig.json 读"任务"schema）、set/get_task_priorities（任务优先级顺序存于 setting_dics["任务优先级顺序"]）。

## API 路由模块（backend/api/）

| 模块 | 职责 |
|---|---|
| `config.py` | 配置 CRUD（多账号管理） |
| `tasks.py` | 任务定义与执行 |
| `scheduler.py` | 调度器启停、立即执行 |
| `settings.py` | 全局设置（调试模式、截图开关） |
| `ws.py` | WebSocket：日志流 + 状态流 |
| `utils.py` | 工具：串口列表、检查更新/应用更新/更新状态、历史日志、反馈选项/打包/状态、浏览文件夹 |
| `validate.py` | 安装路径校验（POST /api/utils/install-path，MuMu/LD 关键文件存在性，MUMU_MANAGER_CANDIDATES 常量） |
| `device.py` | adb 设备管理 + 截图（键位配置，调度器未启动时临时实例化 Device 取帧） |
| `resource.py` | 资源管理器（resourcemanager 页后端入口）：util_router + scenes 路由，前缀 `/api/resource`。提供全量读取 `GET /full`（场景+元素一次返回，joinedload 批量）、`GET /edges`（边批量）、按 id 的场景/元素 CRUD、元素迁移、场景树等 |

> 注：V2 旧 `scenes.py`、`elements.py`、`recognize.py`、`recognizer_service.py` 已删除，场景识别由 `backend/core/legacy/Recognizer.py`（经 `recognizer_engine.py` 导出）承担，场景/元素管理统一走 `resource.py`。

## OCR 识别链路（OnnxOcr 接入）

- **模型复用**：`backend/core/legacy/OnnxOcr/__init__.py` 适配层内定义 `OnnxOcr` 类，复用 `utils/Base/OnnxOcr` 的 PaddleOCR ONNX 模型（`utils/Base/OnnxOcr/models/ppocrv5/`），剥离 V1 依赖。
- **元素类别**：ElementType 新增 `OCR_AREA = 2`（backend/core/enums.py 与 backend/core/legacy/Enums.py 同步），用于在场景中划定 OCR 识别区域。
- **识别调用链**：`Operationer.area_ocr(ocr_area)` → `Recognizer.area_ocr(scene_img, ocr_area, bool_debug)`：
  1. 校验元素类型为 OCR_AREA，否则跳过；
  2. 惰性初始化 OCR 识别器（首次使用才实例化 `OnnxOcr`，不影响原有场景识别性能）；
  3. 按元素区域裁剪 ROI → `OnnxOcr.ocr(image, None, raw_json=True)` 获取结构化结果（`[{text, score, box}]`）；
  4. 按 `ocr_min_score`（Element 模型新增字段，默认 0.5）过滤低置信度文本；
  5. 返回 `List[Tuple[str, List[int]]]`：`[(识别文本, [x1, x2, y1, y2])]`，坐标为相对原图的文本框范围。
- **注意**：`OnnxOcr.ocr(image, box)` 的第二个参数 `box` 是裁剪框偏移复算参数，**不可**把 `threshold` 等无关数值传给它（曾因此产生错误的坐标偏移 Bug，已修复为传 `None` + `raw_json=True`）。
- **前端**：`frontend/src/views/ResourceManager.vue` 完整实现（Naive UI）：场景树/CD 卡片/元素表格增删改查、边管理、元素迁移、批量刷新（单请求 `GET /api/resource/full` 全量重建本地状态）；`frontend/src/router/index.ts` 注册 `resourcemanager` 路由（title: 资源管理器）。`tool/ResourceManager` 已停用（保留代码，无外部引用），OCR_AREA 类别在 `tool/ResourceManager` 中适配暂缓。

## WebSocket 通信模式

- 端点：`/ws/logs`（实时日志）、`/ws/status`（任务/设备状态）。
- `ConnectionManager` 单例维护所有连接，`broadcast()` 广播 JSON。
- `WebSocketLogHandler`（logging.Handler）：
  - 从 logger name 提取 config_id（正则 `Config_\d+`，如 `SchedulerService_Config_1` → `Config_1`）。
  - 30ms 批量刷新缓冲队列（threading.Lock 保护），批量时发送 `["log", batch]` 数组，单条则直接发对象。
  - 前端按 `config_id` 隔离各配置的日志展示。
- **重连恢复**：ws.ts 连接（含重连）成功时向订阅者广播 `reconnected` 事件，LogPanel 监听后拉取历史日志补齐缺口。

## 日志体系（双通道）

1. **主日志**：`log/Main.log`（10MB 轮转）。
2. **配置日志**：`log/<用户名>/<日期>/Xuan.log`（100MB 轮转），按配置隔离。

## 核心模块映射（backend/）

| 模块 | 职责 |
|---|---|
| `main.py` | FastAPI 入口：注册路由、SPA 中间件、启动 WebSocket 日志 handler、异常捕获 |
| `utils.py` | 工具函数（get_real_path 等） |
| `log_setup.py` | 日志配置（文件轮转、双通道） |
| `api/` | REST + WS 路由模块 |
| `services/` | 业务服务（config_service.py 配置管理、scheduler_service.py 调度器、settings_service.py 全局设置、watchdog_service.py 超时监视器） |
| `core/` | 核心模型与逻辑（config_model.py Config 模型、setting_model.py、scene_graph.py、recognizer_engine.py、enums.py、exceptions.py、legacy/） |
| `tools/` | 底层工具（adb 控制、图像识别） |

## 前端架构（frontend/）

- **技术栈**：Vue3 + Vite + Naive UI + Pinia + vue-router；场景资源图 ResourceGraph.vue 使用 d3-force（根目录 package.json 依赖）。
- **视图**：`Layout.vue`（三栏布局：配置列表 / 任务树 / 内容区）、`Dashboard.vue`（总览）、`Settings.vue`（设置）、`ResourceManager.vue`（资源管理器：场景/元素/边增删查改）、`ResourceGraph.vue`（场景资源图，独立页 /resource-graph）、`ResourceSceneEditor.vue`（场景编辑器，独立页 /resource-scene/:sceneId）。
- **组件**：`AssistantSettingsPanel.vue`、`TaskConfigPanel.vue`（任务参数面板）、`LogPanel.vue`（实时日志 + 历史恢复）、`UpdateDialog.vue`（检查更新弹窗 + 进度条）、`FeedbackDialog.vue`（反馈打包两步向导）等。
- **路由**：`/`（Layout：Dashboard/ConfigDetail/Settings/ResourceManager）、`/resource-graph`（ResourceGraph）、`/resource-scene/:sceneId`（ResourceSceneEditor）。

## 配置与任务数据模型

- 一个配置（config）对应一个玩家账号：保存账密、任务开关、任务参数、调度状态。
- 任务按类型分组：每日 / 每周 / 活动。
- 调度器基于优先级与上次执行时间规划下一次执行，支持手动"立即执行"。

## 反馈打包机制

- 目录结构：`log/<用户名>/<日期>/`（如 `log/玄不救非/2026-08-01/`），子目录 `screenshot/<任务名>/` 存截图。
- `GET /api/utils/feedback/options?config_id=&date=`：按 `log/<用户名>/` 生成日期选项（label 为 MM-DD），传 date 返回该日期 screenshot/ 下的任务列表。
- `POST /api/utils/feedback/package`：body `{config_id, date, task_names, save_path}`；后台线程收集 `Main.log*` + `log/<用户名>/<日期>/Xuan.log*` + `screenshot/<任务名>/*`，以 `compresslevel=9` 打包为 `XuanFeedBook_{用户名}_{YYYYMMDD}.zip`。
- `GET /api/utils/feedback/package-status`：查询打包进度（zipping/done/error）。
- `POST /api/utils/browse-folder`：pywin32 弹出 Windows 文件夹选择对话框。

## 版本更新机制

- `version.json` 记录 GitHub master 分支 commit SHA。
- `GET /api/utils/check-update` 请求 GitHub API 获取最新 SHA，对比判断是否有新版本。
- `POST /api/utils/apply-update`：后台线程下载 GitHub zipball → 解压 → 替换文件 → 更新 version.json → 清理临时目录；进度经 phase/percent/message 上报。
- `GET /api/utils/update-status`：查询更新任务进度（downloading/extracting/replacing/writing-version/done/error）。
- **触发方式**：顶栏"检查更新"打开 UpdateDialog（用户确认后才更新）；程序启动 `checkUpdateOnStart()` 仅在云端与本地 SHA 不一致时弹窗，网络异常静默忽略。

## V1 遗留代码（不再维护）

- `Xuan.py`（入口）、`StaticFunctions.py`、`src/`、`utils/`、`tool/`（PySide6 桌面版）。
- 包含完整 Updater、TaskPriorityEditor、ResourceManager 等旧实现；`tool/ResourceManager` 场景资源 UI 已**停用**（保留代码，无外部引用），改由新前端 `ResourceManager.vue` + `backend/api/resource.py` 承担。
