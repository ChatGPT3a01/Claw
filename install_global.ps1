# Claw 全域安裝（PowerShell）
# 把 Claw 資料夾加進「目前使用者」的 PATH，永久生效，不需要管理員權限

$ErrorActionPreference = "Stop"
$ClawHome = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Claw 全域安裝" -ForegroundColor Cyan
Write-Host "  將加入使用者 PATH：" -ForegroundColor Cyan
Write-Host "  $ClawHome" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($userPath -and $userPath.Split(";") -contains $ClawHome) {
    Write-Host "[略過] 已在使用者 PATH 內。" -ForegroundColor Yellow
    Write-Host "若 claw 指令仍無效，請開新的 PowerShell / CMD 視窗。" -ForegroundColor Yellow
} else {
    if ([string]::IsNullOrEmpty($userPath)) {
        $newPath = $ClawHome
    } else {
        $newPath = "$userPath;$ClawHome"
    }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "[OK] 已加入使用者 PATH（永久生效）。" -ForegroundColor Green
}

Write-Host ""
Write-Host "重要提醒：" -ForegroundColor Magenta
Write-Host "  1. 關掉這個視窗" -ForegroundColor White
Write-Host "  2. 開「新的」PowerShell 或 CMD" -ForegroundColor White
Write-Host "  3. 在任何資料夾打：claw" -ForegroundColor Green
Write-Host ""
Read-Host "按 Enter 鍵結束"
