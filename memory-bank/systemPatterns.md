# 系统架构与设计模式

## 原项目架构
- PyQt5 桌面应用
- `.ui` 文件定义界面布局
- `utils/` 下模块化组织:Servicer（服务/助手设置）、KeyMapConfiguration（键位配置）、SerialChoose（串口选择）等
- 全局配置存储于 `setting.ini`
- 每个账号配置存储于 `src/*.json`

## 新项目架构（迁移中）
- 前端:Vue3 + TypeScript + Vite,目录 `frontend/`
- 后端:Python（FastAPI）,目录 `backend/`
- 前端通过 API 与后端通信

## 设计模式
- 配置隔离:一个配置对应一个账号
- 多开支持
- 最小堆调度器调度任务