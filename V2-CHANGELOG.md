# Xuan V2 开发日志

## 项目架构

```
Xuan/
├── backend/          # FastAPI 后端（新增）
│   ├── api/          # REST API 路由
│   ├── core/         # 核心业务逻辑（引用自 utils/Base/）
│   ├── tools/        # 工具模块（引用自 tool/）
│   └── main.py       # 服务入口
├── frontend/         # Vue3 + Electron 前端（新增）
│   ├── src/          # 前端源码
│   ├── electron/     # Electron 主进程
│   └── package.json
├── utils/            # 现有后端代码（逐步剥离 PySide6 依赖）
├── tool/             # 现有工具代码（逐步剥离 GUI 依赖）
├── src/              # 配置文件和资源
└── Xuan.py           # 旧版入口（保留供参考）
```

## 迁移状态

- [ ] 后端 FastAPI 骨架搭建
  - [x] 项目目录结构
  - [ ] API 路由实现
  - [ ] WebSocket 日志流
  - [ ] 配置 CRUD
  - [ ] 场景 CRUD
  - [ ] 元素 CRUD
  - [ ] 任务管理
  - [ ] 调度器控制
  - [ ] 场景识别
- [ ] Vue3 前端开发
  - [x] 项目骨架
  - [ ] 布局组件
  - [ ] 总览页
  - [ ] 配置详情页
  - [ ] 场景图可视化
  - [ ] 场景编辑器
  - [ ] 任务优先级编辑器
  - [ ] 设置页
- [ ] Electron 集成
  - [x] 主进程骨架
  - [ ] 打包配置
- [ ] 旧版代码剥离
  - [ ] Scheduler.py 剥离 TaskWidget
  - [ ] ControlManager.py 剥离 QMessageBox
  - [ ] 其他 PySide6 依赖清理