# Сборка Windows-версии (PyInstaller onedir): dist/SphaeraCommander/SphaeraCommander.exe
#
# Запускать из корня репозитория ПОСЛЕ sync_core.py — ядро (sphaera_commander)
# в git не хранится (ТЗ §2). Требования: python 3.10+ на PATH.
# Скрытые импорты: форматные библиотеки (их импортирует _selfcheck через
# importlib, статический анализ их не видит) и модули win64.platform
# (ядро достаёт их инъекцией/из функции, тоже вне статического анализа).

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

python -m pip install --quiet --disable-pip-version-check `
  PySide6-Essentials pypdfium2 pypdf python-docx mammoth openpyxl `
  python-pptx xlrd xlwt striprtf pyinstaller
if ($LASTEXITCODE -ne 0) { throw "pip завершился с кодом $LASTEXITCODE" }

python -m PyInstaller --noconfirm --windowed --name SphaeraCommander `
  --paths . `
  --add-data "sphaera_commander/assets;sphaera_commander/assets" `
  --add-data "sphaera_commander/plugins;sphaera_commander/plugins" `
  --hiddenimport pypdfium2 --hiddenimport pypdf --hiddenimport docx `
  --hiddenimport mammoth --hiddenimport openpyxl --hiddenimport pptx `
  --hiddenimport xlrd --hiddenimport xlwt --hiddenimport striprtf `
  --hiddenimport win64.platform.paths --hiddenimport win64.platform.trash `
  --hiddenimport win64.platform.shell --hiddenimport win64.platform.terminals `
  win64/run.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller завершился с кодом $LASTEXITCODE" }

Write-Host "Готово: dist/SphaeraCommander/SphaeraCommander.exe"
exit 0
