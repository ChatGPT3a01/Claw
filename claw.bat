@echo off
chcp 65001 > nul
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
setlocal
set "CLAW_HOME=%~dp0"
python "%CLAW_HOME%claw.py" %*
endlocal
