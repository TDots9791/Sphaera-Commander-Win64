"""Платформенный слой Windows (ТЗ §4).

Подключается ДО импорта приложения (win64/run.py): реализация каждого
сервиса выбирается по sys.platform, максимум одна точка выбора на сервис.
Этот пакет НЕ импортирует общий код (sphaera_commander) — зависимость
односторонняя: ядро обращается к платформенному слою, не наоборот.

Ф1: реализованы paths (XDG на Linux / %APPDATA%, %LOCALAPPDATA% на
Windows), shell (run_shell + shell_argv, /bin/sh против cmd.exe),
terminals (wt/powershell/cmd), trash (ctypes SHFileOperationW с гардом
томов без корзины). Выбор платформы — внутри каждого модуля; в ядро
реализации подставляет win64/run.py инъекцией атрибутов.
"""

from __future__ import annotations

import sys

IS_WINDOWS = sys.platform == "win32"
