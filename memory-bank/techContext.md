# 技术栈与依赖

## 原项目技术栈
- Python 3.x
- PyQt5（GUI）
- ADB（Android Debug Bridge）集成
- uiautomator2（U2 控制/截图方案）
- MiniTouch（控制方案）
- DroidCastRaw（截图方案）
- MuMu / LD 模拟器接口（MaaXYZ/EmulatorExtras）

## 新项目技术栈
- 前端:Vue 3 + TypeScript + Vite,`frontend/` 目录
- 后端:Python FastAPI,`backend/` 目录
- 构建工具:Vite、pnpm/yarn

## 配置文件
- `setting.ini`:全局设置
- `src/DefaultConfig.json`:默认账号配置
- `src/*.json`:各账号配置
- `src/DefaultSetting.ini`:默认全局设置模板