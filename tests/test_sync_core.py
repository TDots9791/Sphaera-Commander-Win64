"""Ф0: sync_core — копирование общего кода, запись CORE_VERSION.txt, --check.

Гоняется на фикстурном «источнике» во временном каталоге (без git:
коммит = «unknown», проверяется и переопределение --commit).
"""

import tempfile
import unittest
from pathlib import Path

import sync_core


def make_source(root: Path, version: str = "0.0.1-test") -> None:
    pkg = root / "sphaera_commander"
    (pkg / "assets").mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text(
        f'__version__ = "{version}"\n', encoding="utf-8")
    (pkg / "core.py").write_text("X = 1\n", encoding="utf-8")
    (pkg / "assets" / "icon.svg").write_text("<svg/>", encoding="utf-8")
    (pkg / "__pycache__").mkdir(exist_ok=True)
    (pkg / "__pycache__" / "core.cpython-312.pyc").write_bytes(b"\x00")


class TestSyncCore(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dest = Path(self._tmp.name) / "win64"
        self.source = Path(self._tmp.name) / "linux"
        self.dest.mkdir()
        make_source(self.source)

    def sync(self, *extra):
        return sync_core.main(["--source", str(self.source), *extra],
                              dest_root=self.dest)

    def test_copy_and_record(self):
        self.assertEqual(self.sync(), 0)
        copied = self.dest / "sphaera_commander"
        self.assertTrue((copied / "core.py").is_file())
        self.assertTrue((copied / "assets" / "icon.svg").is_file())
        record = sync_core.read_record(self.dest)
        self.assertEqual(record["version"], "0.0.1-test")
        self.assertEqual(record["commit"], "unknown")

    def test_pycache_not_copied(self):
        self.sync()
        copied = self.dest / "sphaera_commander"
        self.assertFalse((copied / "__pycache__").exists())

    def test_resync_replaces_stale_copy(self):
        self.sync()
        copied = self.dest / "sphaera_commander" / "core.py"
        copied.write_text("X = 2  # ручная правка\n", encoding="utf-8")
        self.assertEqual(self.sync(), 0)
        self.assertIn("X = 1", copied.read_text(encoding="utf-8"))

    def test_check_ok_and_detects_drift(self):
        self.sync("--commit", "abc123")
        self.assertEqual(self.sync("--check", "--commit", "abc123"), 0)
        (self.dest / "sphaera_commander" / "core.py").write_text(
            "X = 2\n", encoding="utf-8")
        self.assertEqual(self.sync("--check", "--commit", "abc123"), 1)

    def test_check_detects_stale_record(self):
        self.sync()
        make_source(self.source, version="0.0.2-test")
        self.assertEqual(self.sync("--check"), 1)

    def test_check_without_copy(self):
        self.assertEqual(self.sync("--check"), 1)

    def test_missing_package_is_error(self):
        empty = self.source.parent / "empty"
        empty.mkdir()
        with self.assertRaises(FileNotFoundError):
            sync_core.copy_package(empty, self.dest)


if __name__ == "__main__":
    unittest.main()
