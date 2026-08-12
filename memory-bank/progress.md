# progress.md — 项目进度与状态

## 已完成（V2）

- **gitignore/clineignore 整理（2026-08）**：`.gitignore` 重写适配 V2（清旧条目、放行 requirements.txt/.cz.toml/_version.py/新 bat/Todo.txt、新增 del/frontend dist/.vite/OCR 模型忽略、运行数据忽略）；`.clineignore` 精简（新增 del/config/utils/frontend dist/.vite）。`git rm --cached` 移除误跟踪的 `.vite` 与 `src/database.db`。要点：gitignore 行尾注释会失效（# 仅行首生效）。

- **旧版本代码依赖解耦（2026-08）**：`device.py` 截图接口由 `utils.Base.Device` 迁移为 `backend.core.legacy.Device`；`utils/Base/` 全部代码与 `StaticFunctions.py` 已移入 `del/`，仅保留 OCR 模型文件 `utils/Base/OnnxOcr/models/ppocrv5/`（文件依赖，`backend/core/legacy/OnnxOcr` 按路径读取）。验证：compileall + import backend.main / legacy.Device / OnnxOcr 均 OK，backend 无 utils/StaticFunctions 引用。剩余保留项均为文件依赖（src 默认配置/数据库/图标、test_scene、version.json 等）。
- **安装路径误报修复（2026-08）**：`config_service.get_config_full` 对 `MuMu安装路径/雷电安装路径` 增加 setting.ini 兜底（`cfg.get_config`），修复打开预设设置时误报"雷电安装路径未设置"（路径实际存在根目录 setting.ini，前端此前只读 config JSON）。
- **预设交互修复（2026-08，终版）**：中栏「助手设置」在预设模式下直接进入 `PresetEditor.vue`（预设设置 + 任务流程整体界面，PresetSettingsPanel 已删除，设置卡片复用 AssistantSettingsPanel）；点击左侧任务预设默认进入总览；预设任务参数在任务卡片下方内联展开；ws.ts 归一化 status/task_state 的 `data.config_id` 到顶层 + Layout 增加 ws 状态监听，解决调度器自动停止后前端仍显示「暂停」、失败标记收不到的问题。
- **两套任务启动方式（2026-08）**：持久账号配置（跟踪进度，现状）+ 临时任务预设（只执行一遍、按顺序、跑完自动关调度器、失败跳过并标记、进度不落盘）。DefaultConfig 增 `配置类型` 全局参数区分；ConfigService/API 支持类型创建、复制（用户名+_副本）、任务执行顺序持久化；SchedulerService once 模式 + 多开支持；前端侧栏 tab 区分两类配置 + PresetEditor.vue（拖拽排序 + 执行参数编辑 + 运行进度/失败标记）。
- **场景图/编辑器交互五项优化（2026-08）**：返回场景图不刷新（keep-alive）、右键子菜单滚动、元素类型角标配色优化、错误/超时/卡死自动截图、配置复制。

- **多配置管理**：配置 CRUD 后端 API + 前端配置列表（右键重命名/删除、顶栏新建）。
- **前端三栏工作台**：Layout.vue（配置列表 / 任务树 / 内容区）已实现。
- **实时日志**：WebSocket 推送（ConnectionManager 单例 + WebSocketLogHandler 30ms 批量），按 config_id（`Config_N`）隔离展示；调试模式开关、保存截图开关、自动滚动。
- **任务调度器**：backend/services/scheduler_service.py，按每日/每周/活动分组 + 优先级 + 下次执行时间；支持手动"立即执行"。
- **场景识别**：backend/core/legacy/Recognizer.py + Operationer 识别链路（图像识别；旧 api/recognize.py 已删除）。
- **设备管理**：backend/api/device.py + /serial-list 枚举 adb 设备。
- **全局工具**：检查更新（对比 version.json 与 GitHub master SHA）、打开日志目录、浏览文件夹（pywin32 对话框）。
- **日志恢复**：`GET /api/utils/log-history` + ws.ts `mergeHistory` + LogPanel 重连恢复，后台搁置/刷新不丢日志。
- **可视化更新**：UpdateDialog.vue + `check-update`/`apply-update`/`update-status`；启动时仅云端与本地提交不一致才自动弹窗。
- **反馈打包**：FeedbackDialog.vue + `feedback/options`/`feedback/package`/`feedback/package-status`；两步选择日期/任务 + 保存位置，打包为 `XuanFeedBook_{用户名}_{YYYYMMDD}.zip`。
- **超时监视器**：`backend/services/watchdog_service.py`（TimeoutWatchdog）三级检测（场景停滞/游戏卡死/模拟器卡死），调度器持有、任务执行时 attach_task 注入、BaseTask 心跳上报场景，告警回调调度器停止任务并按级别分发处理（场景自救/重启游戏/重启模拟器）。
- **卡死处理流程**：场景停滞点 X 类元素兜底返回；游戏卡死重启游戏并轮询前台恢复（120s）；模拟器卡死按截图模式分发（adb / MuMuManager.exe / ldconsole.exe 整合到 Screen 派生类 `restart_emulator`），重启后 `_wait_device_ready` 等待设备就绪（120s）。
- **V2-CHANGELOG.md**：记录 V2 版本变更。
- **助手设置 5 步改造（任务8）**：串口即时回显 + 控制模式水平布局（去小标题）+ 安装路径迁移到 DefaultSetting.ini [助手设置] + 串口格式前端校验 & 安装路径文件存在性 API（`POST /api/utils/install-path`，backend/api/validate.py）+ 调度器启动时 16:9/保活运行时检测（预检失败不启动 + keep_alive_hint）；分层落实（设置阶段只查存在性/格式，启动时查运行时约束）。
- **MuMuManager 候选路径收敛（任务8续）**：4 处校验点统一 `('MuMuManager.exe','shell/MuMuManager.exe','nx_main/MuMuManager.exe')`，dll 补 nx_main/sdk 候选；validate.py 抽出 `MUMU_MANAGER_CANDIDATES` 常量；mock 目录复测 + 路由注册验证通过。
- **截图索引修复（本次）**：AssistantSettingsPanel.vue 的 MuMu/雷电实例索引 `@update:value` 由内联传 computed 旧值改为传 `$event` 新值，修复点击 + 后数字不变的问题。
- **截图接口 500 修复（本次）**：device.py `_capture_frame()` 在调度器未启动时临时实例化 `utils.Base.Device.Device`（同时建立 ControlManager + ScreenManager，MuMu/LD/ADB 截图依赖其初始化），finally 释放连接；`type: ignore[arg-type]` 兼容 Device 的旧版 Config 类型标注。`py_compile` 通过。
- **OnnxOcr 接入（本次）**：ElementType 新增 `OCR_AREA = 2`（backend/core/enums.py + backend/core/legacy/Enums.py）；Element 模型新增 `ocr_min_score: float = 0.5`；Recognizer 新增 `area_ocr(scene_img, ocr_area, bool_debug)` 返回 `[(文本, [x1, x2, y1, y2])]`（经 ONNX OCR 按 ROI 识别 + 置信度过滤，修复 threshold 误传 box 参数的坐标偏移 Bug）；Operationer 新增 `area_ocr` 转发；backend/api/resource.py 资源管理器占位路由（`GET /api/resource/status` → `{"ready": False}`）已注册；前端 ResourceManager.vue 空页面 + `resourcemanager` 路由已注册；`tool/ResourceManager` 场景资源 UI 适配 OCR_AREA 暂缓。`py_compile` + `vite build` 通过。
- **场景资源管理器新前端化（2026-08）**：`backend/tools/resource_db.py` 重写为 `ResourceDBManager`（SQLAlchemy 2.0 ORM + relationship 外键，joinedload 多态加载批量读场景+元素；`get_scene_tree/get_scene_edges` 批量读边；全部按 id CRUD；`_migrate_schema` 增量迁移补旧库 `ocr_min_score` 列，修正 186 场景全量读取空结果）。`backend/api/resource.py` 改为 `util_router` + `scenes` 路由注册（main.py `include_router`），旧 `tool/ResourceManager` 停用（保留代码，无外部引用）。前端新增 `frontend/src/api/resource.ts` 批量全量读取封装；`ResourceManager.vue` 完整实现（Naive UI）：场景树/CD 卡片/元素表格增删改查、边管理、元素迁移、批量刷新（单请求全量重建）。验证：迁移后 `get_all_scenes` 返回 186 场景/845 元素/16+43 边；前端 `vue-tsc` 通过。全量读取由"N 场景+N 元素"次请求降为 3 次（场景+元素+边）。
- **场景资源图 + 场景编辑器独立页（2026-08）**：`ResourceManager.vue` 保留原有表格管理功能（元素迁移/批量刷新等仍可用），布局改为"顶部功能栏 + 下方内容区"。前端新增两页：
  - `ResourceGraph.vue`（路由 `/resource-graph`，顶栏"场景资源"图标按钮 `window.open` 新标签页打开）：Canvas 力导向布局展示所有场景节点与边，节点按类型着色、边按方向着色（in/out），支持缩放/拖拽/悬浮信息、顶部"新建场景"（NewScene 弹窗）/“刷新场景”（重新拉取全量数据）、双击节点跳转对应场景编辑器。
  - `ResourceSceneEditor.vue`（路由 `/resource-scene/:sceneId`）：左 3/4 区以场景图片为底图，按元素类型/方向/点击类型绘制染色框/裁剪图/OCR 区域/箭头等（对齐 `tool/ResourceManager/SceneEditor.py` 绘制规则）；右 1/4 区上部分场景元素树（根=场景、叶=元素，多态图标）、下部分元素属性面板（按类型动态渲染，含基础信息/识别参数/OCR参数/点击参数，保存后更新树节点）。删除元素节点时同步处理底图注册事件（清理后避免事件冒泡报错）。未上传底图的场景显示占位提示。
  - 后端 image 接口扩充校验（不在 `test_scene` 目录内的图片跳过/降级返回），`GET /api/resource/scene/{sid}/image`、`GET /api/resource/element/{eid}/image`（bgra/gray/mask 参数）直接用于前端底图与裁剪图绘制。
  - 验证：`vite build` 全量编译通过（ResourceGraph/ResourceSceneEditor 独立 chunk 生成），`python compileall` 后端语法通过。
- **V2 场景/元素/识别旧 API 清理（2026-08）**：删除 `backend/api/recognize.py`、`backend/api/elements.py`、`backend/api/scenes.py`、`backend/services/recognizer_service.py`；main.py 路由导入与前端 client.ts 同步清理。场景识别由 `backend/core/legacy/Recognizer.py` 承担，场景/元素管理统一走 `backend/api/resource.py`。
- **d3-force 依赖（2026-08）**：根目录新增 `package.json`（dependencies.d3-force ^3.0.0 + @types），供 ResourceGraph.vue Canvas 力导向布局使用；frontend/package.json 不含该依赖，构建时经 vite 解析根 node_modules。
- **场景编辑器交互改造（2026-08）**：ResourceSceneEditor.vue 全面重构——①元素按需渲染（仅选中元素绘制在底图，取消/切换自动清除）；②场景根节点属性面板（重命名 + 执行场景匹配，仅 IMG/OCR 元素）；③IMG 元素 ROI 改为"标签展示 + 底图框选"（Canvas 框选模式实时虚线预览），Ratio 改为"标签展示 + RatioDialog.vue 弹窗点选"（支持 >1 或负数，不限制范围），新增"选择图片"上传；④COORDINATE 元素坐标只允许底图点击获取（coordinate 点选模式）；⑤OCR 元素 ROI 与 IMG 相同框选交互，新增"执行识别"（area_ocr）；⑥新增后端端点 `POST /api/resource/scenes/{scene_id}/match`、`POST /api/resource/elements/{element_id}/match`、`POST /api/resource/elements/{element_id}/ocr`；前端新增 `frontend/src/components/RatioDialog.vue`。
- **图片存储简化（2026-08）**：Element 模型删除 `gray`/`mask` 列（仅存 4 通道 BGRA 原始字节），`_migrate_schema` 对旧库 DROP COLUMN；SceneGraph（backend/core/scene_graph.py、backend/core/legacy/Scene/SceneGraph.py、utils/Base/Scene/SceneGraph.py 三处）在初始化时从 bgra 推导 gray/mask（`object.__setattr__` 挂载，因 SQLModel extra="allow" 下 `__pydantic_extra__` 可能为 None）；`get_element_image`/`upload_element_image` 移除 type 参数；旧客户端 `tool/ResourceManager` 的 NewElement/SceneEditor/ResourceDBManager 同步移除 split 逻辑；`element_to_qpixmap` 仅支持 bgra。
- **场景编辑器交互修正（2026-08，第2轮）**：①`symbol` 语义修正为"标志"（该元素作为 scene 的标志，优先级最高），属性面板/新建对话框标签由"点击坐标"改为"标志"，勾选标志后元素名自动改为"标志"；②右侧元素树删除类型文字后缀，改为右上角彩色角标（标志红色 `#d03050`/IMG 蓝色 `#2080f0`/COORDINATE 黑色 `#333`/OCR 橙色 `#f0a020`），Canvas 标注色同步；③场景节点"执行匹配"改为 `recognizer.scene()` 识别当前底图属于哪个场景（不再对所有 IMG 逐元素匹配），返回 `{ok, scene_name, recognized, matched}`；④新建元素对话框按元素类型动态展示属性（IMG：标志/匹配方式/阈值/Ratio/ROI；COORDINATE：仅坐标；OCR：ROI/OCR阈值）。
- **元素匹配 gray AttributeError 修复（2026-08）**：`match_element`/`match_scene`/`ocr_element` 原从 `_db` 直接查询元素对象（无 gray/mask），导致 `element_match` 读取 `template.gray` 报 `'Element' object has no attribute 'gray'`。新增 `_find_element_in_graph()` 从 `recognizer.scene_graph` 中按 id 取 SceneGraph 已预处理（gray/mask 已推导）的元素对象再执行匹配；`bool_debug` 统一改 False 避免刷日志。
- **场景编辑器交互修正（2026-08，第3轮）**：①树节点角标修复——由"文字右侧内联"改为绝对定位右上角（`position:absolute; top:-5px; right:0`），白字深底加粗保证可读，`.tree-label` 预留 `padding-right:32px`；②删除底图点击选中元素功能（`hitTest` 移除，拖拽不再误选中，只能通过右侧树选择）；③修复 IMG 图片上传失败 `[object Object]`——根因是 axios 实例全局默认 `Content-Type: application/json` 覆盖了 FormData 的 `multipart/form-data` 边界，`uploadElementImage` 显式传 `headers: {'Content-Type': 'multipart/form-data'}`；④元素匹配/OCR 识别结果改为弹窗展示（`n-modal`，`mask-closable=false` 手动点"关闭"按钮，含匹配位置列表/OCR 文本列表）。
- **场景资源图节点功能增强（2026-08）**：ResourceGraph.vue——①节点右键菜单（`@contextmenu.prevent` + `n-dropdown`）：复制场景名称（navigator.clipboard）、连接到场景（二级菜单列出未连接场景，`createEdge`）、断开连接（列出已连接场景，`deleteEdge`）、删除场景（`window.confirm` 确认 + `deleteScene`）；②单击节点高亮关联——选中节点及其所有直接相连节点的填充变橙色 `#f0a020`、字样变蓝色 `#2080f0`、选中节点描边红色加粗，关联边变黄色 `#f5c518` 加粗，其余保持默认（灰边/蓝节点）；`loadData` 重载时重置选中与菜单状态。
- **场景资源图交互优化（2026-08）**：①新建场景节点不再触发 `loadData()` 全量刷新（重新载入很慢）——`handleCreate` 用后端返回的 `{scene:{id,name}}` 在本地 `nodes`/`scenes` 中直接新增一个节点，默认放在画布可视中心附近（带偏移避免完全重叠），只 `render()` 不重载；②删除场景节点只有存在相连边（`node.edges.length>0`）时才触发 `loadData()`（边需从后端重算），无边时仅从本地 `nodes`/`scenes`/`edgeList` 移除并 `render()`。已验证 `create_scene` 返回 `{scene:{id,name}}`、`delete_scene` 返回 `{ok:true}`。

## 进行中 / 待办

- 前端 `ResourceManager.vue` 的"添加元素"弹窗暂用属性选择器（场景参照列表）；图形化元素编辑器已由 `ResourceSceneEditor.vue`（/resource-scene/:sceneId）承担，可评估是否统一两者体验。
- ResourceSceneEditor 的 ROI 框选/坐标点选已完成；可评估是否将"新建元素"对话框也改为交互式（底图框选 ROI / 点击定坐标）。当前新建对话框按类型展示属性，ROI/坐标仍为数字输入。
- OCR_AREA 类别的元素已可在新 `ResourceManager.vue` 中管理（含 ocr_min_score 编辑），后续可在识别链路中联调验证。
- 确认 V2 各 API 与前端面板的完整联动（AssistantSettingsPanel、TaskConfigPanel、Dashboard、Settings 等）。
- 评估 V2 自动更新实现（check-update/apply-update/update-status + UpdateDialog.vue）与 V1 utils/Base/Updater.py 的差异与合并策略。
- 关注游戏 UI 变化（如好友体力），通过场景/元素识别 + 可配置参数适配。

## 已知问题 / 注意事项

- **SPA 中间件依赖 frontend/dist**：若 dist 缺失，访问非 API 路径可能失败；生产构建需保持 frontend/dist 存在。
- 日志 logger 命名必须包含 `Config_N`，WebSocketLogHandler 才可正确归类到对应配置。
- WebSocket 日志消息有**单条对象**与**批量数组**（`["log", batch]`）两种格式，前端需兼容。
- **minidevice / MiniTouch 模式（已验证通过）**：
  - 代码修复：`ControlManager.py` 与 `Clicker.py` 两处模块顶部无条件 `from ..MiniTouch import MiniTouch` 已改为函数内懒导入；ControlManager 在 MiniTouch 初始化失败时仅本次降级 U2，**不写回用户配置**（保留 MiniTouch 设置）。
  - 环境根因：`minidevice` 只安装在 `.venv`（基于 Python312）。若后端进程由系统 Python（如 `C:\Python313`）或非 venv Python 启动，会报 `No module named 'minidevice'`。**启动后端必须用 `.venv\Scripts\python.exe` 绝对路径**（`start cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 4199"`），不能依赖 `activate.bat && python`（可能解析到错误 Python）。
  - 真实验证（14:05:02 日志）：`MiniTouch 初始化成功 | 分辨率:1600x900,最大连接数:10,最大压力:2`，无降级警告；`POST /api/scheduler/start/Config_1` → `{"ok":true}`。

## 版本基线

- version.json（GitHub master SHA）：`525d733fac159a7b5fc79306eff0d9220c122283`（"fix:[好友体力]适配好友体力UI变化"）。
- 本地 git 最新提交：`1f3c9dd1453822ee1598c454f737aafd95c09b92`。

## 演进决策记录

- V2 采用 FastAPI 独立服务（端口 4199）+ Vue3 前端，逐步替代 V1 的 PySide6 单进程桌面应用。
- 日志体系保持双通道：主日志（log/Main.log）+ 配置日志（log/<用户名>/<日期>/Xuan.log），V2 增加 WebSocket 实时推送层。