$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$DeployDir,

    [switch]$Prod,

    [string]$SiteId,

    [string]$Message
)

function Write-Step($Text) {
    Write-Host "[Netlify] $Text" -ForegroundColor Cyan
}

if (-not (Test-Path -LiteralPath $DeployDir -PathType Container)) {
    throw "找不到部署資料夾: $DeployDir"
}

$netlifyCmd = Get-Command netlify -ErrorAction SilentlyContinue
$useNpx = $false

if (-not $netlifyCmd) {
    $npxCmd = Get-Command npx -ErrorAction SilentlyContinue
    if (-not $npxCmd) {
        throw "找不到 netlify 或 npx，請先安裝 Node.js 與 Netlify CLI。"
    }
    $useNpx = $true
}

Write-Step "檢查 Netlify 登入狀態"
try {
    if ($useNpx) {
        & npx netlify status | Out-Null
    }
    else {
        & netlify status | Out-Null
    }
}
catch {
    throw "Netlify 尚未登入或 CLI 無法使用，請先執行 netlify login。"
}

$args = @("deploy", "--dir=$DeployDir")

if ($Prod) {
    $args += "--prod"
}

if ($SiteId) {
    $args += "--site=$SiteId"
}

if ($Message) {
    $args += "--message=$Message"
}

Write-Step "開始部署 $DeployDir"

if ($useNpx) {
    & npx netlify @args
}
else {
    & netlify @args
}
