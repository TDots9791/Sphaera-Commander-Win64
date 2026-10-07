"""Точка входа Windows-сборки (exe, PyInstaller — Ф2).

Порядок импортов существенен (ТЗ §4): платформенный слой подключается
ДО импорта приложения, чтобы реализации сервисов были на месте, когда
ядро их спросит.

Запуск в разработке: python win64/run.py  (из корня репозитория)
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from win64 import platform  # noqa: E402 — до импорта приложения (ТЗ §4)
from sphaera_commander.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
