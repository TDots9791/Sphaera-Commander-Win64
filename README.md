# Sphaera Commander Win64

Windows-версия [Sphaera Commander](https://github.com/TDots9791/Sphaera-Commander) —
двухпанельного файлового менеджера в духе Total Commander
(Python 3.10+ / PySide6).

Общий код не хранится здесь: `sync_core.py` подтягивает пакет
`sphaera_commander` из Linux-репозитория (версия/коммит — в
`CORE_VERSION.txt`); вся Windows-специфика — только в `win64/platform/`,
подключается до импорта приложения (ТЗ §2–§4).

## Статус

Ф0 (скелет), Ф1 (платформенный слой), Ф2 (полный набор + сборка в CI),
Ф4 (MSI-установщик + смок установки) — **приняты CI**; осталась Ф3 —
живая проверка по чек-листу [docs/live-check.md](docs/live-check.md).

CI (`ci.yml`, ubuntu + windows): platform-тесты, полный набор ядра
offscreen, PyInstaller onedir + SELFCHECK, MSI (WiX 6, русский визард) и
смок install → update → uninstall. Артефакты каждого прогона: `.msi`
установщик и портативный `.zip`.

## Сборка из исходников

```sh
python3 sync_core.py            # подтянуть общий код (Windows: python sync_core.py)
python3 -m unittest discover -s tests -v          # тесты платформенного слоя
```

Windows: `powershell win64\build_exe.ps1` (onedir →
`dist\SphaeraCommander\SphaeraCommander.exe`), затем
`ISCC`/`wix build` по `win64\installer.wxs` (см. ci.yml).
