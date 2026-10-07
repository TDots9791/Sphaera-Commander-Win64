"""«Открыть терминал здесь» на Windows (ТЗ §3, plugins/terminal_here.py).

Контракт — форма плагина terminal_here, чтобы плагин на Windows брал
список отсюда без ветвлений:

  find_terminal() -> (программа, аргументы) | None

  аргументы — кортеж с плейсхолдером {dir} (как TERMINALS плагина);
  выбор — первый найденный через shutil.which, в порядке предпочтения.

Планируемый список Windows (флаги проверить в Ф1 на живой машине):
  wt.exe          -d {dir}                  — Windows Terminal
  powershell.exe  -NoExit -Command "Set-Location -LiteralPath '{dir}'"
  cmd.exe         /K cd /d "{dir}"

Ф0: контракт; реализация — Ф1.
"""

from __future__ import annotations


def find_terminal():
    """(программа, аргументы с {dir}) | None; список — в docstring модуля. Ф1."""
    raise NotImplementedError("Ф1")
