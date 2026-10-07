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
        # Юникод + глубина в пределах MAX_PATH — корзина работает.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        deep = tmp.name
        while len(deep) + 60 < 240:
            deep = os.path.join(deep, "каталог-длинное-имя")
        os.makedirs(deep, exist_ok=True)
        path = _make_file(deep, name="глубокий-файл.txt")
        self.assertGreater(len(path), 150)
        result = trash.trash([_Entry("глубокий-файл.txt", path)],
                             lambda s: None, lambda: False)
        self.assertTrue(result.ok, result.errors)
        self.assertFalse(os.path.exists(path))

    def test_beyond_max_path_honest_error(self):
        # ТЗ §7.4/§7.6: поведение за MAX_PATH зависит от политики
        # LongPathsEnabled машины. Оба исхода корректны: SHFileOperationW
        # берёт длинный путь (где политика включена) — файл в корзине;
        # не берёт — честная ошибка по объекту, файл не теряется
        # (IFileOperation — улучшение Ф3).
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(tmp.cleanup)
        deep = tmp.name
        while len(deep) + 60 < 420:
            deep = os.path.join(deep, "каталог-за-пределом-max-path")
        long_path = os.path.join(deep, "файл.txt")
        os.makedirs("\\\\?\\" + deep, exist_ok=True)
        with open("\\\\?\\" + long_path, "w", encoding="utf-8") as f:
            f.write("x")
        self.assertTrue(os.path.exists("\\\\?\\" + long_path))
        result = trash.trash([_Entry("файл", long_path)],
                             lambda s: None, lambda: False)
        if result.ok:
            self.assertFalse(os.path.exists("\\\\?\\" + long_path))
        else:
            self.assertEqual(result.done_files, 0)
            self.assertEqual(len(result.errors), 1)
            self.assertTrue(os.path.exists("\\\\?\\" + long_path))

    def test_fixed_drive_considered_recyclable(self):
        self.assertTrue(trash._drive_supports_recycle_bin(
            os.path.join(tempfile.gettempdir(), "цель")))


if __name__ == "__main__":
    unittest.main()
