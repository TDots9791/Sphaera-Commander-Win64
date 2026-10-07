"""Корзина на Windows: Recycle Bin (ТЗ §3, ops.execute_trash).

Контракт — сигнатура и семантика ops.execute_trash (ops.py:479), чтобы
ядро вызывало платформенную реализацию без обёрток:

  trash(sources, progress_cb, is_cancelled) -> OpResult-совместимо

  sources      записи fsmodel (утинная типизация: .name и .path); только реальные
               пути — VFS (»::» в пути) и «..» отсекаются здесь, как в ядре
  progress_cb  callback(state) — state с полями phase/current/done_files/
               total_files/done_bytes/total_bytes (как ops.Progress);
               вызывается в начале и после каждого объекта
  is_cancelled callback() -> bool; между объектами — отмена
               (result.cancelled = True)

  возврат      объект утиной типизации ops.OpResult: done_files, done_bytes, skipped,
               errors (список объектов с .path и .message), cancelled, .ok

Windows: Recycle Bin через ctypes SHFileOperationW с FOF_ALLOWUNDO
(FOF_NOCONFIRMATION | FOF_SILENT | FOF_ALLOWUNDO), по одному пути за вызов
(успех — done_files, иначе FileError). ТЗ §7.4: сетевые диски и тома без
корзины — деградация на безвозвратное удаление только после явного
подтверждения пользователя (механизм вопроса — Ф1/Ф3). Длинные и юникодные
пути — проверить на windows-раннере (главный риск ctypes, ТЗ §7.6).

Ф0: контракт; реализация — Ф1 (тесты обязательны на windows-раннере).
"""

from __future__ import annotations


def trash(sources, progress_cb, is_cancelled):
    """Recycle Bin; контракт ops.execute_trash — в docstring модуля. Ф1."""
    raise NotImplementedError("Ф1")
