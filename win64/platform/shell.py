"""Единая точка запуска командной строки (ТЗ §3: app.py:1480, buttonbar.py:63).

Два сценария ядра:
  app.py:1480            командная строка окна — QProcess, вывод собирается
                         в GUI-потоке; ядру нужен argv -> shell_argv(cmd);
  buttonbar.run_command  кнопки панели — отсоединённый запуск -> run_shell(..., detached=True).

Контракт:
  shell_argv(cmd) -> list[str]      программа + аргументы для QProcess;
  run_shell(cmd, cwd=None, detached=False)
    detached=True   потомок не ждём: stdout/stderr в DEVNULL, отдельная
                    сессия/группа процесса; возвращает None;
    detached=False  ждём завершения; возвращает (код, объединённый вывод),
                    вывод декодирован с errors="replace".

Windows: cmd.exe /c (PowerShell — опция на живой проверке Ф3: кавычки
%f/%d из shlex для cmd.exe пересматриваются там же); Linux: /bin/sh -c.
"""

from __future__ import annotations

import subprocess
import sys

IS_WINDOWS = sys.platform == "win32"

# Удерживаем дескриптор последнего отсоединённого потомка, пока тот не
# завершится: сборка живого Popen мусором даёт ResourceWarning.
_last_detached = None


def shell_argv(cmd: str) -> list[str]:
    """argv для QProcess-сценариев (командная строка окна)."""
    if IS_WINDOWS:
        return ["cmd.exe", "/d", "/c", cmd]
    return ["/bin/sh", "-c", cmd]


def run_shell(cmd: str, cwd: str | None = None, detached: bool = False):
    """cmd.exe/PowerShell/sh; сценарии и возврат — в docstring модуля."""
    if detached:
        global _last_detached
        if IS_WINDOWS:
            flags = (getattr(subprocess, "DETACHED_PROCESS", 0)
                     | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
            _last_detached = subprocess.Popen(
                ["cmd.exe", "/d", "/c", cmd], cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags)
        else:
            _last_detached = subprocess.Popen(
                ["/bin/sh", "-c", cmd], cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True)
        return None
    proc = subprocess.run(shell_argv(cmd), cwd=cwd, capture_output=True)
    combined = (proc.stdout + proc.stderr).decode(errors="replace")
    return proc.returncode, combined
