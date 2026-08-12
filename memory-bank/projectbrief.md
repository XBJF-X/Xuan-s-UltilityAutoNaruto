# projectbrief.md — Xuan-s-UltilityAutoNaruto

## 项目定义

**Xuan-s-UltilityAutoNaruto**（玄的日常助手，火影忍者忍者日常助手）是一款面向《火影忍者》手游的日常任务自动化工具。通过模拟点击、场景识别、任务调度等方式，自动完成游戏内的日常任务（每日、每周、活动等），减少玩家重复手动操作。

- GitHub 仓库: https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto
- 当前工作区: `e:\PyProject\Xuan`
- 当前本地版本: V2 重构版（backend/ + frontend/），与 V1 遗留代码共存

## 核心需求

1. **多配置管理**：支持创建多个用户配置（username），每个配置独立保存账密、任务开关、任务参数、调度状态，互不干扰。
2. **任务自动化调度**：按任务类型（每日/每周/活动）分组，基于优先级与下次执行时间自动执行任务；支持手动"立即执行"。
3. **实时日志**：按 config_id 隔离显示各配置的运行日志，支持调试模式（显示 DEBUG 日志）、保存截图开关、自动滚动。
4. **场景识别**：通过图像识别当前游戏场景，驱动任务流程（backend/core/legacy/Recognizer.py + Operationer 识别链路；旧 api/recognize.py 已删除）。
5. **设备管理**：枚举 adb 串口设备列表（backend/api/device.py）。
6. **版本自动更新**：对比本地 version.json 与 GitHub master 分支 commit SHA，检测新版本；V1 有完整 Updater，V2 已实现 check-update/apply-update/update-status + UpdateDialog.vue 完整更新流程。

## V1 → V2 演进目标

| 维度 | V1（遗留） | V2（当前开发） |
|---|---|---|
| 前端 | PySide6 桌面 UI | Vue3 + Vite + Naive UI + Electron |
| 后端 | 单进程桌面应用 | FastAPI 独立服务（端口 4199） |
| 实时日志 | 本地控件 | WebSocket 推送（按 config_id 隔离） |
| 部署 | 桌面程序 | Electron 主进程 + 子进程后端 |

**演进状态**：V2 正在逐步替代 V1。`src/`、`utils/`、`tool/`、`Xuan.py`、`StaticFunctions.py` 为 V1 遗留；`backend/`、`frontend/` 为 V2 主力。

## 项目范围边界

- `.clineignore` 屏蔽目录：`test_scene`、`release`、`__pycache__`、`log`、`image`、`build`、`.venv`、`.idea`。
- 目标平台：Windows 11（依赖 pywin32、adb）。
- 生产构建需保持 frontend/dist 存在（backend 的 SPA 中间件依赖它）。