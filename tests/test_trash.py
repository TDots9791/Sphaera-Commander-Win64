"""Ф1: trash — фильтры/поток/отмена (кроссплатформенно) и реальное
удаление в корзину (только windows-раннер, skipUnless)."""

import os
import tempfile
import unittest

from win64.platform import trash


class _Entry:
    def __init__(self, name, path):
        self.name = name
        self.path = path


def _make_file(where, name="объект.txt", content="x"):
    path = os.path.join(where, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


class TestFlow(unittest.TestCase):
    """Семантика ops.execute_trash, не требующая реальной корзины."""

    def test_vfs_dotdot_and_empty_filtered(self):
        entries = [_Entry("..", "/x/.."), _Entry("пустой", ""),
                   _Entry("vfs", "/архив.zip::член"), _Entry("ok", "/цель")]
        states = []
        result = trash.trash(entries, states.append, lambda: False)
        self.assertEqual(states[0].total_files, 1)  # остался только «/цель»
        self.assertEqual(result.done_files, 0)      # /цель не существует
        self.assertTrue(all("::" not in s.current for s in states))
        for s in states:
            for field in ("phase", "current", "done_files", "total_files",
                          "done_bytes", "total_bytes"):
                self.assertTrue(hasattr(s, field))

    def test_cancel_before_first_item(self):
        entries = [_Entry("a", "/цель-а"), _Entry("b", "/цель-б")]
        calls = []
        result = trash.trash(entries, calls.append, lambda: True)
        self.assertTrue(result.cancelled)
        self.assertEqual(result.done_files, 0)
        self.assertEqual(len(calls), 1)  # только начальное состояние

    def test_progress_call_count(self):
        entries = [_Entry("a", "/цель")]
        calls = []
        trash.trash(entries, calls.append, lambda: False)
        # начальное + «текущий объект» + «после объекта»
        self.assertEqual(len(calls), 3)


@unittest.skipUnless(not trash.IS_WINDOWS,
                     "реальный gio-путь ядра не касается платформы")
class TestRefusesOnPosix(unittest.TestCase):
    def test_real_file_yields_error_and_survives(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = _make_file(tmp.name)
        result = trash.trash([_Entry("файл", path)],
                             lambda s: None, lambda: False)
        self.assertFalse(result.ok)
        self.assertEqual(result.done_files, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].path, path)
        self.assertTrue(os.path.exists(path))


@unittest.skipUnless(trash.IS_WINDOWS, "реальная корзина — только Windows")
class TestRealRecycleBin(unittest.TestCase):
    def test_file_goes_to_recycle_bin(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = _make_file(tmp.name, name="файл-тест.txt")
        result = trash.trash([_Entry("файл-тест.txt", path)],
                             lambda s: None, lambda: False)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.done_files, 1)
        self.assertFalse(os.path.exists(path))

    def test_deep_unicode_path(self):
        # ТЗ §7.6: длинные и юникодные пути — главный риск ctypes.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        deep = tmp.name
        for i in range(12):
            deep = os.path.join(deep, "каталог-уровня-с-длинным-именем")
        path = _make_file(deep, name="глубокий-файл.txt")
        self.assertGreater(len(path), 200)
        result = trash.trash([_Entry("глубокий-файл.txt", path)],
                             lambda s: None, lambda: False)
        self.assertTrue(result.ok, result.errors)
        self.assertFalse(os.path.exists(path))

    def test_fixed_drive_considered_recyclable(self):
        self.assertTrue(trash._drive_supports_recycle_bin(
            os.path.join(tempfile.gettempdir(), "цель")))


if __name__ == "__main__":
    unittest.main()
