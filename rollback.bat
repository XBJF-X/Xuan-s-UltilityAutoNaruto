@echo off
chcp 65001 >nul
setlocal
rem Xuan 离线回滚（不联网）：列出/恢复 update_packages 下保存的更新包。
rem 用法：rollback.bat              -> 列出本机更新包
rem       rollback.bat --last       -> 回滚到最近一个非当前版本
rem       rollback.bat --to <sha>   -> 回滚到指定提交
set "ROOT=%~dp0"
set "PY="
if exist "%ROOT%_internal\venv\python.exe" set "PY=%ROOT%_internal\venv\python.exe"
if not defined PY if exist "%ROOT%.venv\Scripts\python.exe" set "PY=%ROOT%.venv\Scripts\python.exe"
if not defined PY set "PY=python"
"%PY%" -X utf8 "%ROOT%scripts\rollback.py" %*
if errorlevel 1 pause
endlocal
