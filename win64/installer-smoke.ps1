# Дымовой тест Ф4 для MSI на чистой машине-раннере (ТЗ §5 Ф4):
# установка (msiexec /i /qn) -> SELFCHECK установленного -> маркер конфига
# -> обновление (REINSTALL, конфиг переживает) -> деинсталляция (msiexec /x)
# -> отсутствие мусора (каталог, ярлыки, ассоциация, ключ деинсталлятора).
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

$msi = (Resolve-Path "dist-installer\SphaeraCommander-*.msi" | Select-Object -First 1).Path
if (-not $msi) { throw "MSI не найден в dist-installer" }

$appDefault = Join-Path $env:ProgramFiles "SphaeraCommander"
$cfg = Join-Path $env:APPDATA "SphaeraCommander"

function Get-InstallLocation {
    foreach ($root in @("HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")) {
        $found = Get-ChildItem $root -ErrorAction SilentlyContinue |
                 Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName -eq "Sphaera Commander" }
        if ($found) {
            $loc = (Get-ItemProperty $found.PSPath).InstallLocation
            if ($loc) { return $loc }
        }
    }
    if (Test-Path (Join-Path $appDefault "SphaeraCommander.exe")) { return $appDefault }
    return $null
}

function Invoke-Msi([string]$action, [string]$target, [string[]]$extra = @()) {
    $argv = @($action) + $(if ($target) { , $target } else { @() }) + $extra + @("/qn", "/norestart")
    $p = Start-Process -FilePath "msiexec.exe" -ArgumentList $argv -Wait -PassThru
    if ($p.ExitCode -notin 0, 3010) { throw "msiexec $action -> код $($p.ExitCode)" }
}

# 1. установка
Invoke-Msi "/i" $msi
$deadline = (Get-Date).AddSeconds(90)
$app = $null
while (-not $app -and (Get-Date) -lt $deadline) {
    $app = Get-InstallLocation
    if (-not $app) { Start-Sleep -Milliseconds 500 }
}
$exe = if ($app) { Join-Path $app "SphaeraCommander.exe" } else { $null }
if (-not ($exe -and (Test-Path $exe))) { throw "после установки exe не появился (loc=$app)" }

# 2. SELFCHECK установленного exe
$env:SPHAERA_SELFCHECK = "1"
$p = Start-Process -FilePath $exe -Wait -PassThru
if ($p.ExitCode -ne 0) { throw "SELFCHECK установленного: код $($p.ExitCode)" }

# 3. маркер в конфиге пользователя
New-Item -ItemType Directory -Force -Path $cfg | Out-Null
Set-Content -Path (Join-Path $cfg "buttons.json") -Value '{"buttons":[]}'

# 4. обновление (тот же MSI, REINSTALL) — конфиг обязан пережить
Invoke-Msi "/i" $msi @("REINSTALL=ALL", "REINSTALLMODE=vomus")
if (-not (Test-Path (Join-Path $cfg "buttons.json"))) { throw "конфиг не пережил обновление" }

# 5. деинсталляция
Invoke-Msi "/x" $msi
$deadline = (Get-Date).AddSeconds(90)
while ((Test-Path $app) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
if (Test-Path $app) { throw "каталог приложения не удалён" }
$startMenu = Join-Path $env:ProgramData "Microsoft\Windows\Start Menu\Programs\Sphaera Commander"
if (Test-Path $startMenu) { throw "ярлык «Пуск» не удалён" }
$desktopLnk = Join-Path ([Environment]::GetFolderPath("CommonDesktopDirectory")) "Sphaera Commander.lnk"
if (Test-Path $desktopLnk) { throw "ярлык рабочего стола не удалён" }
$assoc = Get-Item "Registry::HKEY_CLASSES_ROOT\Directory\shell\SphaeraCommander" -ErrorAction SilentlyContinue
if ($assoc) { throw "ассоциация Directory\shell не удалена" }
$leftover = Get-ChildItem "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue |
            Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName -eq "Sphaera Commander" }
if ($leftover) { throw "ключ деинсталлятора не удалён" }

Write-Host "СМОК OK: установка, SELFCHECK, обновление (конфиг цел), деинсталляция без мусора"
