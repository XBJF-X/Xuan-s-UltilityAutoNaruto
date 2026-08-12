@echo off
echo 正在启动后端服务...
rem 必须用 .venv 的 Python 绝对路径启动，避免系统 Python（无 minidevice）抢跑
start "Backend" cmd /k "set PYTHONIOENCODING=utf-8 && .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 4199"
echo 正在启动前端服务...
start "Frontend" cmd /k "cd frontend && npm run dev"
echo 两个服务已启动。关闭各自窗口以停止服务。