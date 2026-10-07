"""«Открыть терминал здесь» на Windows (ТЗ §3, plugins/terminal_here.py).

Контракт — форма плагина terminal_here, чтобы плагин на Windows брал
список отсюда без ветвлений:

  find_terminal() -> (программа, аргументы) | None

  аргументы — кортеж с плейсхолдером {dir} (как TERMINALS плагина);
  выбор — первый найденный через shutil.which, в порядке предпочтения.

На не-Windows список пуст по смыслу (терминалы плагина терминалов Linux
живут в самом плагине): find_terminal() вернёт None.
"""

from __future__ import annotations

import shutil
import sys

IS_WINDOWS = sys.platform == "win32"

# (исполняемый файл, [аргументы с {dir}]) — порядок предпочтения.
# wt — app execution alias Windows Terminal; флаги проверить на живой
# машине в Ф3 (ТЗ §5), особенно кавычки для путей с пробелами.
TERMINALS = (
    ("wt", ("-d", "{dir}")),
    ("wt.exe", ("-d", "{dir}")),
    ("powershell.exe",
     ("-NoExit", "-Command", "Set-Location -LiteralPath '{dir}'")),
    ("cmd.exe", ("/K", 'cd /d "{dir}"')),
) if IS_WINDOWS else ()


def find_terminal():
    """(программа, аргументы с {dir}) | None; список — в docstring модуля."""
    for name, args in TERMINALS:
        path = shutil.which(name)
        if path:
            return path, args
    return None
