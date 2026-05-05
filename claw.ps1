# Claw — 三 AI CLI 切換器（PowerShell 啟動器）
$env:PYTHONIOENCODING = "utf-8"
$ClawHome = Split-Path -Parent $MyInvocation.MyCommand.Path
& python "$ClawHome\claw.py" @args
