"""Платформенный слой Windows (ТЗ §4).

Подключается ДО импорта приложения (win64/run.py): реализация каждого
сервиса выбирается по sys.platform, максимум одна точка выбора на сервис.
Этот пакет НЕ импортирует общий код (sphaera_commander) — зависимость
односторонняя: ядро обращается к платформенному слою, не наоборот.

Ф0: контракты — сигнатуры и документация; реализации — Ф1
(paths/shell/terminals — stdlib; trash — ctypes SHFileOperationW).
"""

from __future__ import annotations

import sys

IS_WINDOWS = sys.platform == "win32"
