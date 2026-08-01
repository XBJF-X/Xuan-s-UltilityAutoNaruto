# 进度追踪 (Progress)

## 任务完成状态

| 任务 | 状态 | 说明 |
| --- | --- | --- |
| 后端 FastAPI 迁移 | ✅ | 路由在 backend/api/,服务在 backend/services/ |
| 前端 Vue3 脚手架 | ✅ | layout/router/store/api 客户端就绪 |
| 子任务1: 任务树"助手设置"节点 + AssistantSettingsPanel.vue | ✅ | 新建组件,Layout.vue 挂载,配置项还原 |
| 子任务2: Settings.vue 全局设置页(反映 setting.ini) | ✅ | 按值类型渲染布尔/数字/字符串,写回 /settings |
| 键位配置弹窗(还原 KeyMapConfiguration.py) | ✅ | n-modal 图形编辑:10 键位可拖拽按钮,坐标换算与原版一致(加载减25/保存加25) |
| 串口列表弹窗(还原 SerialChoose.py) | ✅ | 调 deviceApi.serialList 枚举 ADB,支持重启 ADB 后重新枚举,确认写回 `串口` |
| 前端构建验证 | ✅ | `npm --prefix frontend run build` 通过(vite build 28.88s, 13438 modules) |

## 已完成事项

- 读取原版 `utils/Servicer.py` 确认助手设置键名与绑定逻辑;读取 `utils/KeyMapConfiguration.py` 确认键位保存语义(`set_config("键位", result_positions)`)。
- 确认后端接口链:`configApi.get(id)` → setting_dics;`configApi.updateSetting(id,key,value)` → PUT /configs/{id}/setting;`deviceApi.screenshot/serialList/restartAdb` → backend/api/device.py。
- AssistantSettingsPanel.vue 全部设置项:调试模式、控制模式、串口(+串口列表弹窗)、截图模式(+MuMu/LD 子面板)、扫描间隔、二级密码、键位配置(n-modal)。
- Layout.vue:currentView 扩展 'assistant',任务树底部固定"助手设置"节点。
- Settings.vue 按值类型渲染 bool→n-switch/数字→n-input-number/字符串→n-input,修改即调 settingsApi.set 写回。

## 已知问题 / 待办

- [ ] 运行时验证(需真实模拟器连接,点击助手设置节点、试串口列表/截图键位配置)。
- [ ] 键位配置截图依赖后端 /device/{config_id}/screenshot(需模拟器在线)。
- [ ] MuMu/LD 安装路径为手动输入(浏览器端无 QFileDialog 目录选择)。
- [ ] 前端大 chunk 警告(1.47MB 主包),后续可加 dynamic import 分包。
- [ ] 更新模块 README/文档与代码对应。

## 遗留事项

- 原版类型5任务挂到 roots[1](每周任务),前端 `typeGroupMap[5]='每周任务'` 已同步。
- 原版 KeyMapConfiguration/SerialChoose 已按 Qt 模态窗口逻辑还原为前端 n-modal;后续可按需增强。
