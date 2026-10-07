"""Ф0: контракты платформенного слоя.

Проверяем то, что уже обязано быть верным до реализации Ф1:
модули импортируются; вызовы честно отказываются (NotImplementedError);
платформенный слой не зависит от общего кода (ТЗ §4, зависимость
односторонняя). На ubuntu-раннере IS_WINDOWS ложен — это тоже фиксация
контракта выбора по sys.platform.
"""

import re
import sys
import unittest
from pathlib import Path

from win64.platform import IS_WINDOWS, paths, shell, terminals, trash

PLATFORM_DIR = Path(__file__).resolve().parent.parent / "win64" / "platform"

_IMPORT_CORE = re.compile(r"^\s*(import|from)\s+(sphaera_commander|PySide6)\b",
                          re.M)


def _call_stubs():
    yield paths.config_dir
    yield paths.cache_dir
    yield paths.data_dir
    yield terminals.find_terminal
    yield lambda: trash.trash([], lambda state: None, lambda: False)
    yield lambda: shell.run_shell("echo hi")


class TestPlatformContracts(unittest.TestCase):
    def test_is_windows_follows_sys_platform(self):
        self.assertEqual(IS_WINDOWS, sys.platform == "win32")

    def test_stubs_refuse_until_phase1(self):
        for call in _call_stubs():
            with self.assertRaises(NotImplementedError):
                call()

    def test_platform_layer_does_not_import_core(self):
        # Зависимость односторонняя (ТЗ §4): в исходниках platform нет
        # импортов общего кода и Qt (упоминания в docstring — можно).
        for py in PLATFORM_DIR.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            self.assertIsNone(_IMPORT_CORE.search(text),
                              f"{py.name} импортирует общий код или Qt")

    def test_contracts_documented(self):
        # «Пустые модули с контрактами»: у каждой точки входа — docstring
        # с формулой поведения (ТЗ §5, Ф0).
        for func in (paths.config_dir, paths.cache_dir, paths.data_dir,
                     shell.run_shell, terminals.find_terminal, trash.trash):
            self.assertTrue((func.__doc__ or "").strip(),
                            f"{func.__name__} без контракта")


if __name__ == "__main__":
    unittest.main()
