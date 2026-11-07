@echo off
setlocal
if exist "%~dp0dist\ewb\ewb.exe" (
  "%~dp0dist\ewb\ewb.exe" %*
  exit /b %errorlevel%
)
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Please run Start-Windows.cmd once to prepare Python.
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0entry.py" %*
