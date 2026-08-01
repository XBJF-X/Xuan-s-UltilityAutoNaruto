# 活动上下文 (Active Context)

## 当前工作焦点

从纯 Python(PySide6/Qt)到 Vue3 + FastAPI 技术栈迁移的"还原任务"——还原原版应用功能到前端。

本会话完成两个子任务:

### 子任务1: 任务列表树"助手设置"节点 ✅
- 前端任务树底部固定"助手设置"节点(对应原版 `task_index_dic["助手设置"] = 1`,位于树最下方)。
- 新建 `frontend/src/components/AssistantSettingsPanel.vue`:还原原版 DQH_Settings_widget 全部设置项。
- 数据来源: `configApi.get(id)` 的 `setting_dics`;写回: `configApi.updateSetting(id, key, value)`。
- 还原的设置项(键名与原版一致):
  - 调试模式(布尔 → n-switch)
  - 控制模式(0=MiniTouch / 1=U2 → n-select)
  - 串口(文本 → n-input + "串口列表"按钮弹窗)
  - 截图模式(5 模式 n-select:DroidCastRaw/WindowCapture/U2/MuMu/LD),按所选模式动态显示子面板
  - MuMu: 安装路径 + 实例索引; LD: 安装路径 + 实例索引
  - 扫描间隔(n-input-number 50-9999, suffix " ms")
  - 键位配置(n-modal 弹窗,说明文案 + 简短提示)
  - 二级密码(n-input type=password maxlength=6, placeholder "必须为六位")
- `Layout.vue` 修改:
  - `currentView` 类型扩展 `'overview' | 'task' | 'globallog' | 'assistant'`
  - 树底部追加"助手设置"节点(⚙ 图标),点击 → `switchToAssistant`
  - 内容区 `v-else-if="currentView === 'assistant'"` 渲染 `AssistantSettingsPanel`,带 `activeConfigId` 空值守卫
  - 任务分组修正: `typeGroupMap[5] = '每周任务'`(匹配原版 `task_type = 1 if 类型==5 else 类型`)

### 子任务2: 全局设置页 Settings.vue ✅
- 重写 `frontend/src/views/Settings.vue`:反映 `setting.ini` 内容。
- 读取 `settingsApi.getAll()` → 分节渲染;布尔(`true`/`false`)→ n-switch, 数字 → n-input-number, 字符串 → n-input。
- 修改后调 `settingsApi.set(section, key, value)` 写回,失败回滚重新加载。
- 样式调整为暗色主题,匹配全局 UI。

## 关键决策

- 助手设置项存于每个 config 的 `setting_dics`(经 `configApi.get(id)` 返回),不存 setting.ini(全局),与原版一致。
- 键位配置(KeyMapConfiguration)与串口列表(SerialChoose)原为 Qt 模态窗口,前端以 n-modal 弹窗简化还原。
- 前端无文件系统访问能力,MuMu/LD 安装路径以可编辑 n-input 代替 QFileDialog 浏览选择。
- `setting.ini` 内容是 `[Update] 自动更新`;Settings.vue 通用按值类型渲染,随 setting.ini 扩展自动适配。

## 下一步计划

- 运行时验证: 需真实模拟器在线,点击"助手设置"节点检查渲染、串口列表枚举、截图键位配置、各项写回 setting_dics。
- 键位配置截图依赖后端 `/device/{config_id}/screenshot`(ScreenManager.screencap + cv2 PNG base64);模拟器离线时显示空态提示。
- MuMu/LD 安装路径为手动输入;若需浏览器选目录,可引入 electron 的 dialog 或拖拽上传。
- 前端大 chunk(1.47MB)后续可用 dynamic import 分包。
- 更新模块文档(frontend README 等)。
