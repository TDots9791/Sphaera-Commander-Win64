"""Ф1: контракты платформенного слоя.

Модули импортируются; платформенный слой не зависит от общего кода и Qt
(ТЗ §4, зависимость односторонняя); у каждой точки входа — docstring
с формулой поведения. На ubuntu-раннере IS_WINDOWS ложен — это фиксация
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


class TestPlatformContracts(unittest.TestCase):
    def test_is_windows_follows_sys_platform(self):
        self.assertEqual(IS_WINDOWS, sys.platform == "win32")

    def test_platform_layer_does_not_import_core(self):
        # Зависимость односторонняя (ТЗ §4): в исходниках platform нет
        # импортов общего кода и Qt (упоминания в docstring — можно).
        for py in PLATFORM_DIR.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            self.assertIsNone(_IMPORT_CORE.search(text),
                              f"{py.name} импортирует общий код или Qt")

    def test_contracts_documented(self):
        # У каждой точки входа — docstring с формулой поведения (ТЗ §4).
        for func in (paths.config_dir, paths.cache_dir, paths.data_dir,
                     shell.run_shell, shell.shell_argv,
                     terminals.find_terminal, trash.trash):
            self.assertTrue((func.__doc__ or "").strip(),
                            f"{func.__name__} без контракта")


if __name__ == "__main__":
    unittest.main()
