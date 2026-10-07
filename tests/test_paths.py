"""Ф1: paths — раскладка каталогов по платформам (ТЗ §3).

env-базы читаются при каждом вызове, поэтому тесты подменяют окружение
и проверяют и Linux-раскладку (XDG_*), и Windows-раскладку (APPDATA/
LOCALAPPDATA) на любой машине — реализация ветвится только по
sys.platform, а ожидания теста строятся из той же переменной окружения.
"""

import os
import tempfile
import unittest

from win64.platform import paths


class TestPaths(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = tmp.name
        self._saved = {}
        for var, value in self._overrides().items():
            self._saved[var] = os.environ.get(var)
            os.environ[var] = value
        self.addCleanup(self._restore)

    def _overrides(self):
        if paths.IS_WINDOWS:
            return {"APPDATA": os.path.join(self.base, "roaming"),
                    "LOCALAPPDATA": os.path.join(self.base, "local")}
        return {"XDG_CONFIG_HOME": os.path.join(self.base, "config"),
                "XDG_CACHE_HOME": os.path.join(self.base, "cache"),
                "XDG_DATA_HOME": os.path.join(self.base, "share")}

    def _restore(self):
        for var, old in self._saved.items():
            if old is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = old

    def _expected(self):
        if paths.IS_WINDOWS:
            local = os.environ["LOCALAPPDATA"]
            return (os.path.join(os.environ["APPDATA"], "SphaeraCommander"),
                    os.path.join(local, "SphaeraCommander", "cache"),
                    os.path.join(local, "SphaeraCommander"))
        return (os.path.join(os.environ["XDG_CONFIG_HOME"],
                             "sphaera-commander"),
                os.path.join(os.environ["XDG_CACHE_HOME"],
                             "sphaera-commander"),
                os.path.join(os.environ["XDG_DATA_HOME"],
                             "sphaera-commander"))

    def test_layout_and_creation(self):
        expected_cfg, expected_cache, expected_data = self._expected()
        self.assertEqual(paths.config_dir(), expected_cfg)
        self.assertEqual(paths.cache_dir(), expected_cache)
        self.assertEqual(paths.data_dir(), expected_data)
        for path in (expected_cfg, expected_cache, expected_data):
            self.assertTrue(os.path.isdir(path), path)

    def test_no_trailing_separator_and_stable(self):
        for call in (paths.config_dir, paths.cache_dir, paths.data_dir):
            first = call()
            self.assertFalse(first.endswith(os.sep))
            self.assertEqual(call(), first)


if __name__ == "__main__":
    unittest.main()
