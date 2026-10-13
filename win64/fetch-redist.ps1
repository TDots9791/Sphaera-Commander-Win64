# Redist в дистрибутив: rclone (облака как диски) и WinFsp (его rclone
# требует на Windows для монтирования). Версии запинены, SHA256 сверяется —
# сборка воспроизводима и не зависит от «последней» версии в сети.
# Кладёт: dist/SphaeraCommander/rclone.exe (рядом с exe приложения —
# ядро находит его само) и dist/SphaeraCommander/redist/winfsp.msi
# (ставится nested-MSI кастом-действием установщика, если WinFsp нет).
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

$RCLONE_URL = "https://downloads.rclone.org/v1.75.2/rclone-v1.75.2-windows-amd64.zip"
$RCLONE_SHA256 = "8A9DB2BAD1DC79A65B3348FD857069598E2AAB7CF4D118B77B1DF23055AFF818"
$WINFSP_URL = "https://github.com/winfsp/winfsp/releases/download/v2.1/winfsp-2.1.25156.msi"
$WINFSP_SHA256 = "073A70E00F77423E34BED98B86E600DEF93393BA5822204FAC57A29324DB9F7A"

$cache = "win64/.redist"
New-Item -ItemType Directory -Force $cache | Out-Null
New-Item -ItemType Directory -Force "dist/SphaeraCommander/redist" | Out-Null

function Fetch([string]$url, [string]$out, [string]$sha256) {
    if (Test-Path $out) {
        $h = (Get-FileHash $out -Algorithm SHA256).Hash
        if ($h -ieq $sha256) { return $out }
    }
    Write-Host "== скачивание $url"
    Invoke-WebRequest -Uri $url -OutFile $out -MaximumRedirection 5
    $h = (Get-FileHash $out -Algorithm SHA256).Hash
    if ($h -ine $sha256) {
        throw "SHA256 не сошёлся для ${out}: получено $h, ожидалось $sha256"
    }
    return $out
}

# 1. rclone.exe — рядом с SphaeraCommander.exe (ядро находит само)
$zip = Fetch $RCLONE_URL "$cache/rclone.zip" $RCLONE_SHA256
$tmp = Join-Path $cache "unzip"
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
Expand-Archive -Path $zip -DestinationPath $tmp -Force
Copy-Item (Join-Path $tmp "rclone-v1.75.2-windows-amd64/rclone.exe") `
          "dist/SphaeraCommander/rclone.exe" -Force

# 2. WinFsp MSI — в redist (вшивается в наш MSI, ставится его CA)
Fetch $WINFSP_URL "dist/SphaeraCommander/redist/winfsp.msi" $WINFSP_SHA256 | Out-Null

Write-Host ("redist: rclone.exe {0:N0} байт, winfsp.msi {1:N0} байт" -f `
    (Get-Item "dist/SphaeraCommander/rclone.exe").Length, `
    (Get-Item "dist/SphaeraCommander/redist/winfsp.msi").Length)
