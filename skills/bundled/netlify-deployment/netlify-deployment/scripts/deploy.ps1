$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$DeployDir,
    [switch]$Prod,
    [string]$SiteId,
    [string]$Message
)

if (-not (Test-Path -LiteralPath $DeployDir -PathType Container)) {
    throw "找不到部署資料夾: $DeployDir"
}

try {
    & netlify status | Out-Null
}
catch {
    throw "Netlify 尚未登入，請先執行 netlify login。"
}

$args = @("deploy", "--dir=$DeployDir")
if ($Prod) { $args += "--prod" }
if ($SiteId) { $args += "--site=$SiteId" }
if ($Message) { $args += "--message=$Message" }

& netlify @args
