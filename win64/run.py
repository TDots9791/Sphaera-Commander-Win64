"""Точка входа Windows-сборки (exe, PyInstaller — Ф2).

Порядок существенен (ТЗ §4): платформенный слой подключается и
инъекцией подставляет свои реализации в ядро ДО импорта приложения —
ядро стартует уже с Windows-поведением (корзина, шелл, командная
строка); дефолты ядра при этом Linux-овые, поэтому на Linux этот файл
не используется.

Запуск в разработке: python win64/run.py  (из корня репозитория)
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from win64 import platform  # noqa: E402 — до импорта приложения (ТЗ §4)

# Инъекция платформенных реализаций в ядро (по одной точке на сервис):
import sphaera_commander.ops as _ops  # noqa: E402
import sphaera_commander.buttonbar as _buttonbar  # noqa: E402

_ops.trash_via_platform = platform.trash.trash
_buttonbar.run_detached_shell = platform.shell.run_shell

from sphaera_commander import app as _app  # noqa: E402

_app.shell_argv_provider = platform.shell.shell_argv

from sphaera_commander.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
