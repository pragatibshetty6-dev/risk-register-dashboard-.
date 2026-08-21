@echo off
title Risk Register Review Dashboard
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
  echo Python environment not found.
  echo Please run the one-time setup in VS Code first.
  pause
  exit /b 1
)
start "" http://127.0.0.1:5000
venv\Scripts\python.exe app.py
pause
