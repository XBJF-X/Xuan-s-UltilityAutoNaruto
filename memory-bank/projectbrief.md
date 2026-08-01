# 项目简介

## 项目名称
XUAN（Xuan's UltilityAutoNaruto）- 火影忍者自动化日常工具

## 项目目标
- 基于图像检测识别信息 + 最小堆调度器自动调度任务的游戏自动化工具
- 不涉及任何读取和修改游戏内存数据
- 支持主流模拟器分辨率与多种截图/控制方案

## 当前阶段
从纯 Python（PyQt）技术栈迁移到前端 Vue3 + 后端 Python 技术栈,已完成部分核心功能的迁移。

## 当前任务
1. 还原"助手设置"功能（任务列表树状栏最下方,助手设置,前端内容）,包含键位配置、串口选择、控制模式、截图模式等
2. 重构全局设置页,使其反映 `setting.ini` 的内容并以合理方式展示（布尔类型用滑杆/开关,填写类型用文本框）

## 关键约束
- 参考原项目 `utils/ui/Service.ui`、`utils/ui/KeyMapConfiguration.ui`、`utils/ui/SerialChoose.ui`
- 参考原项目 `utils/Servicer.py`、`utils/KeyMapConfiguration.py`、`utils/SerialChoose.py`
- 遵守全局文档规范与 Memory Bank 规则