"""Единая точка запуска командной строки (ТЗ §3: app.py:1480, buttonbar.py:63).

Сейчас ядро дважды вызывает /bin/sh -c напрямую:
  app.py:1480        командная строка окна — QProcess, вывод собирается
                     в GUI-потоке;
  buttonbar.run_command  кнопки панели — отсоединённый Popen, вывод в никуда.

Контракт (ТЗ §4):

  run_shell(cmd, cwd=None, detached=False)

  Windows: cmd.exe /c (опция PowerShell — решить в Ф1 по живому сценарию
  кнопок); Linux: /bin/sh -c (как сейчас).

  detached=True  потомок не ждём (buttonbar-сценарий): stdout/stderr в
                 DEVNULL, своя сессия процесса; возвращает None.
  detached=False ждём завершения (командная строка окна); возвращает
                 (код_выхода, объединённый вывод) — вывод в декодированном
                 виде с errors="replace", как app.py _collect_out.

Плейсхолдеры %f/%d (buttonbar.build_command с shlex.quote) не меняются;
для Windows-шелла кавычки пересматривает Ф1 (cmd.exe не понимает
одинарные кавычки sh).
"""

from __future__ import annotations


def run_shell(cmd: str, cwd: str | None = None, detached: bool = False):
    """cmd.exe/PowerShell/sh; сценарии и возврат — в docstring модуля. Ф1."""
    raise NotImplementedError("Ф1")
