# techContext.md — 技术栈与开发环境

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python + FastAPI（独立服务，端口 4199） |
| 前端 | Vue3 + Vite + TypeScript + Naive UI + Pinia + vue-router |
| 桌面壳 | Electron（主进程加载 frontend/dist，子进程启动 backend） |
| 实时通信 | WebSocket（/ws/logs、/ws/status） |
| 设备控制 | adb（模拟点击）、pywin32（Windows 桌面操作） |
| 图像识别 | OpenCV + ONNX OCR（backend/core/legacy/Recognizer.py 场景识别 + OnnxOcr 适配层 OCR 区域识别；旧 api/recognize.py 已删除） |

## 开发环境

- 操作系统：Windows 11
- 包管理：前端 pnpm / yarn / npm 均可（存在 pnpm-lock.yaml、yarn.lock、package-lock.json）
- 当前时间基准：UTC+8（Asia/Shanghai）
- 本地 git：origin = git@github.com:XBJF-X/Xuan-s-UltilityAutoNaruto.git

## 后端关键文件

| 文件 | 说明 |
|---|---|
| `backend/main.py` | FastAPI 入口：注册路由、SPA 中间件、WebSocket 日志 handler、异常捕获 |
| `backend/log_setup.py` | 日志配置（双通道、文件轮转） |
| `backend/utils.py` | get_real_path 等工具函数 |
| `backend/api/ws.py` | ConnectionManager 单例 + WebSocketLogHandler（30ms 批量推送） |
| `backend/api/utils.py` | /serial-list、/check-update、/apply-update、/update-status、/log-history、/feedback/options、/feedback/package、/feedback/package-status、/browse-folder |
| `backend/api/device.py` | adb 设备管理 |
| `backend/api/resource.py` | 资源管理器路由（util_router + scenes）：`GET /full` 全量读取（场景+元素一次返回）、`GET /edges` 边批量、按 id 的场景/元素 CRUD、元素迁移、场景树 |
| `backend/api/validate.py` | 安装路径校验（`POST /api/utils/install-path`，MuMu/LD 关键文件存在性，`MUMU_MANAGER_CANDIDATES` 常量） |
| `backend/services/config_service.py` | 配置管理（多配置 CRUD、模块级单例 `shared_config_service`） |
| `backend/services/settings_service.py` | 全局设置（setting.ini [助手设置] 读写，安装路径兜底） |
| `backend/services/scheduler_service.py` | 任务调度器 |
| `backend/services/watchdog_service.py` | TimeoutWatchdog 超时监视器（场景停滞/游戏卡死/模拟器卡死三级检测） |
| `backend/core/config_model.py` | Config 模型（V3 配置文件递归合并、get/set 体系） |
| `backend/core/legacy/OnnxOcr/` | OnnxOcr 适配层（复用 `utils/Base/OnnxOcr` 的 PaddleOCR ONNX 模型，剥离 V1 依赖；Recognizer.area_ocr 使用） |
| `backend/core/legacy/Recognizer.py` | 场景/元素识别（新增 `area_ocr`，OCR 区域识别） |
| `backend/core/legacy/Operationer.py` | 操作执行器（新增 `area_ocr`，转发到 Recognizer） |
| `backend/core/enums.py`、`backend/core/legacy/Enums.py` | ElementType 均含 `OCR_AREA = 2` |
| `backend/tools/models.py` | Element 模型（含 `ocr_min_score: float = 0.5` 字段） |
| `backend/tools/resource_db.py` | ResourceDBManager（SQLAlchemy 2.0 ORM + relationship 外键）：按 id CRUD、joinedload 批量读场景+元素、边管理、`_migrate_schema` 增量迁移（旧库补 `ocr_min_score` 列） |
| `frontend/src/api/resource.ts` | 资源管理器 API 封装（`getFull`/`getEdges` 等批量全量读取，一次请求全量重建） |
| `frontend/src/views/ResourceManager.vue` | resourcemanager 页（完整实现：场景树/CD 卡片/元素表格增删改查、边管理、元素迁移、批量刷新） |
| `frontend/src/views/ResourceGraph.vue` | 场景资源图（独立页 /resource-graph）：Canvas 力导向布局（d3-force），节点/边着色，缩放拖拽，双击进入场景编辑器 |
| `frontend/src/views/ResourceSceneEditor.vue` | 场景编辑器（独立页 /resource-scene/:sceneId）：场景图底图 + 元素染色框/裁剪图/OCR 区域 + 元素属性面板 |

## 数据与配置

- `version.json`：记录 GitHub master 分支 commit SHA（当前本地 SHA：`525d733fac159a7b5fc79306eff0d9220c122283`），用于 `/api/utils/check-update` 对比。
- OCR 模型：`utils/Base/OnnxOcr/models/ppocrv5/`（det.onnx、rec.onnx、ppocrv5_dict.txt），由 backend/core/legacy/OnnxOcr 适配层加载。
- V1 配置：`src/DefaultConfig.json`、`src/DefaultSetting.ini`。
- V2 配置与日志：由 backend 管理（多配置按 username 隔离）。
- d3-force：根目录 `package.json`（dependencies.d3-force ^3.0.0 + @types/d3-force dev 依赖），供 ResourceGraph.vue 力导向布局；frontend/package.json 不含该依赖。

## 常见命令

- 前端开发：`cd frontend && pnpm dev`（或 npm/yarn）
- 前端构建：`cd frontend && pnpm build`（产物 frontend/dist，SPA 中间件依赖）
- ⚠️ 前端构建验证务必用**本地** `frontend/node_modules/.bin/vite build`（或 pnpm build）；`npx vite build` 会拉取全局缓存的 vite v8（rolldown 版）与项目 vite v5 不兼容并报 UNRESOLVED_ENTRY
- 后端启动：`.venv\Scripts\python.exe backend\main.py`（必须用 venv Python，minidevice 等依赖仅装在 .venv）
- 后端启动：`python backend/main.py`（或通过 Electron 子进程拉起）
- 生产构建：需保持 frontend/dist 存在

## 关键约定

- WebSocket 日志消息含 `config_id`（格式 `Config_N`），前端按此隔离展示。
- 日志双通道：`log/Main.log`（主日志）+ `log/<用户名>/<日期>/Xuan.log`（配置日志）。
- `.clineignore` 屏蔽：test_scene、release、__pycache__、log、image、build、.venv、.idea。