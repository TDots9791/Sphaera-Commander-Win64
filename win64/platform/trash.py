"""Корзина на Windows: Recycle Bin (ТЗ §3, ops.execute_trash).

Контракт — сигнатура и семантика ops.execute_trash (ops.py:479), чтобы
ядро вызывало платформенную реализацию без обёрток (инъекцию делает
win64/run.py до запуска приложения: ops.trash_via_platform):

  trash(sources, progress_cb, is_cancelled) -> OpResult-совместимо

  sources      записи fsmodel (утинная типизация: .name и .path); только
               реальные пути — VFS («::» в пути) и «..» отсекаются здесь,
               как в ядре
  progress_cb  callback(state) — state с полями phase/current/done_files/
               total_files/done_bytes/total_bytes (как ops.Progress);
               вызывается в начале и до/после каждого объекта
  is_cancelled callback() -> bool; между объектами — отмена
               (result.cancelled = True); прерывание самой операции
               оболочкой (fAnyOperationsAborted) — тоже отмена

  возврат      объект утиной типизации ops.OpResult: done_files,
               done_bytes, skipped, errors (список .path/.message),
               cancelled, .ok

Реализация (Ф1): ctypes SHFileOperationW, FO_DELETE по одному пути за
вызов, флаги FOF_SILENT | FOF_NOCONFIRMATION | FOF_ALLOWUNDO |
FOF_NOERRORUI (без диалогов — подтверждения остаётся в ядре, как с gio).

Тома без корзины (сетевые, CD-RAM, неизвестные — GetDriveTypeW):
честный отказ по объекту. Безвозвратное удаление там возможно только
явным вопросом пользователю (ТЗ §7.4, решается на Ф3); молчаливая
деградация FOF_ALLOWUNDO недопустима. На не-Windows — отказ по каждому
объекту (ядро Linux ходит через gio в ops.execute_trash напрямую).
Длинные (>260) и юникодные пути — тестами на windows-раннере (ТЗ §7.6).
"""

from __future__ import annotations

import ctypes
import os
import sys

IS_WINDOWS = sys.platform == "win32"

_FOF_SILENT = 0x0004
_FOF_NOCONFIRMATION = 0x0010
_FOF_ALLOWUNDO = 0x0040
_FOF_NOERRORUI = 0x0400
_FO_DELETE = 3

# GetDriveTypeW: корзина есть на фиксированных и съёмных дисках
_DRIVE_FIXED = 3
_DRIVE_REMOVABLE = 2


class FileError:
    """Утиный ops.FileError (path, message)."""

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message


class OpResult:
    """Утиный ops.OpResult (done_files/done_bytes/skipped/errors/cancelled/.ok)."""

    def __init__(self) -> None:
        self.done_files = 0
        self.done_bytes = 0
        self.skipped = 0
        self.errors: list[FileError] = []
        self.cancelled = False

    @property
    def ok(self) -> bool:
        return not self.errors and not self.cancelled


class _Progress:
    """Утиный ops.Progress."""

    def __init__(self, total_files: int) -> None:
        self.phase = "run"
        self.current = ""
        self.done_files = 0
        self.total_files = total_files
        self.done_bytes = 0
        self.total_bytes = 0


def _eligible(sources) -> list:
    """Фильтр как в ops.execute_trash: без «..», пустых и VFS («::»)."""
    return [e for e in sources
            if getattr(e, "name", "") != ".."
            and getattr(e, "path", "") and "::" not in e.path]


def _drive_supports_recycle_bin(path: str) -> bool:
    drive = os.path.splitdrive(os.path.abspath(path))[0]
    if not drive:
        return False
    kind = ctypes.windll.kernel32.GetDriveTypeW(drive + os.sep)
    return kind in (_DRIVE_REMOVABLE, _DRIVE_FIXED)


def _sh_file_delete(path: str) -> tuple[str, str]:
    """FO_DELETE одного пути.

    Возврат: ("ok", "") | ("aborted", "") | ("error", сообщение).
    """

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [
            ("hwnd", ctypes.c_void_p),
            ("wFunc", ctypes.c_uint),
            ("pFrom", ctypes.c_wchar_p),
            ("pTo", ctypes.c_wchar_p),
            ("fFlags", ctypes.c_ushort),
            ("fAnyOperationsAborted", ctypes.c_int),
            ("hNameMappings", ctypes.c_void_p),
            ("lpszProgressTitle", ctypes.c_wchar_p),
        ]

    op = SHFILEOPSTRUCTW()
    op.hwnd = None
    op.wFunc = _FO_DELETE
    # SHFileOperationW требует двойной нулевой терминатор на конце:
    # c_wchar_p добавляет один, второй кладём сами.
    op.pFrom = path + "\x00"
    op.pTo = None
    op.fFlags = (_FOF_SILENT | _FOF_NOCONFIRMATION | _FOF_ALLOWUNDO
                 | _FOF_NOERRORUI)
    op.fAnyOperationsAborted = 0
    op.hNameMappings = None
    op.lpszProgressTitle = None
    code = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    if op.fAnyOperationsAborted:
        return "aborted", ""
    if code != 0:
        return "error", f"SHFileOperationW: код {code}"
    return "ok", ""


def trash(sources, progress_cb, is_cancelled):
    """Recycle Bin; контракт — в docstring модуля (копия ops.execute_trash)."""
    result = OpResult()
    items = _eligible(sources)
    state = _Progress(len(items))
    progress_cb(state)
    for entry in items:
        if is_cancelled():
            result.cancelled = True
            return result
        state.current = entry.path
        progress_cb(state)
        if not IS_WINDOWS:
            result.errors.append(FileError(
                entry.path, "корзина платформы доступна только на Windows"))
        elif not _drive_supports_recycle_bin(entry.path):
            result.errors.append(FileError(
                entry.path,
                "том без корзины — безвозвратное удаление "
                "требует явного подтверждения"))
        else:
            status, message = _sh_file_delete(entry.path)
            if status == "ok":
                result.done_files += 1
            elif status == "aborted":
                result.cancelled = True
                state.done_files = result.done_files
                progress_cb(state)
                return result
            else:
                result.errors.append(FileError(entry.path, message))
        state.done_files = result.done_files
        progress_cb(state)
    return result
