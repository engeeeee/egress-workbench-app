@echo off
setlocal
cd /d "%~dp0"
if exist "dist\EgressWorkbench\EgressWorkbench.exe" (
  start "" "dist\EgressWorkbench\EgressWorkbench.exe"
  exit /b 0
)
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if errorlevel 1 (
    echo Please install Python 3.12 or newer from python.org, including Tcl/Tk and the Python launcher.
    pause
    exit /b 1
  )
  py -3 -m venv .venv
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :failed
start "" ".venv\Scripts\pythonw.exe" entry.py
exit /b 0
:failed
echo Setup failed. Please check your Python installation and Internet connection.
pause
exit /b 1
