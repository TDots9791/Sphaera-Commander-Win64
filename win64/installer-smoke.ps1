# Дымовой тест Ф4 на чистой машине-раннере (ТЗ §5 Ф4):
# установка -> SELFCHECK установленного -> маркер конфига -> обновление
# (конфиг переживает) -> деинсталляция -> отсутствие мусора
# (каталог приложения, ярлык «Пуск», ассоциация Directory\shell).
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

$ver = ((Get-Content CORE_VERSION.txt) | Where-Object { $_ -like 'version=*' }) -replace '^version=', ''
$setup = (Resolve-Path "dist-installer\SphaeraCommander-$ver-setup.exe").Path
$cfg = Join-Path $env:APPDATA "SphaeraCommander"
$guid = "B8CE0EF6-B7C3-4EBF-9C89-7489BB311EA5"

# Ключ деинсталлятора ищем по GUID-подстроке в обоих представлениях
# реестра: имя ключа Inno зависит от трактовки фигурных скобок в AppId.
function Get-UninstallKey {
    foreach ($root in @("HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")) {
        $found = Get-ChildItem $root -ErrorAction SilentlyContinue |
                 Where-Object { $_.PSChildName -like "*$guid*" }
        if ($found) { return $found }
    }
    return $null
}

function Get-InstallLocation {
    $k = Get-UninstallKey
    if ($k) { return (Get-ItemProperty $k.PSPath).InstallLocation }
    return $null
}

function Invoke-Setup([string]$path, [string[]]$argList) {
    $p = Start-Process -FilePath $path -ArgumentList $argList -Wait -PassThru
    if ($p.ExitCode -ne 0) { throw "$path -> код $($p.ExitCode)" }
}

# 1. установка
Invoke-Setup $setup @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART")
$deadline = (Get-Date).AddSeconds(60)
$app = $null
while (-not $app -and (Get-Date) -lt $deadline) {
    $app = Get-InstallLocation
    if (-not $app) { Start-Sleep -Milliseconds 500 }
}
$exe = Join-Path $app "SphaeraCommander.exe"
if (-not ($app -and (Test-Path $exe))) {
    throw "после установки exe не появился (loc=$app)"
}

# 2. SELFCHECK установленного exe
$env:SPHAERA_SELFCHECK = "1"
$p = Start-Process -FilePath (Join-Path $app "SphaeraCommander.exe") -Wait -PassThru
if ($p.ExitCode -ne 0) { throw "SELFCHECK установленного: код $($p.ExitCode)" }

# 3. маркер в конфиге пользователя
New-Item -ItemType Directory -Force -Path $cfg | Out-Null
Set-Content -Path (Join-Path $cfg "buttons.json") -Value '{"buttons":[]}'

# 4. обновление (повторная установка) — конфиг обязан пережить
Invoke-Setup $setup @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART")
if (-not (Test-Path (Join-Path $cfg "buttons.json"))) {
    throw "конфиг не пережил обновление"
}

# 5. деинсталляция
Invoke-Setup (Join-Path $app "unins000.exe") @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART")
$deadline = (Get-Date).AddSeconds(90)
while ((Test-Path $app) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
if (Test-Path $app) { throw "каталог приложения не удалён" }
$startMenu = Join-Path $env:ProgramData "Microsoft\Windows\Start Menu\Programs\Sphaera Commander"
if (Test-Path $startMenu) { throw "ярлык «Пуск» не удалён" }
$key = Get-Item "Registry::HKEY_CLASSES_ROOT\Directory\shell\SphaeraCommander" -ErrorAction SilentlyContinue
if ($key) { throw "ассоциация Directory\shell не удалена" }
if (Get-UninstallKey) { throw "ключ деинсталлятора не удалён" }

Write-Host "СМОК OK: установка, SELFCHECK, обновление (конфиг цел), деинсталляция без мусора"
