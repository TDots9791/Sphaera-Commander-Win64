"""Ф1: проводка — инъекция платформенных реализаций в ядро (win64/run.py).

Требуют ядра и PySide6 (на CI platform-ногах пропускаются; полная
проверка ядра на Windows — Ф2).
"""

import unittest

try:
    import sphaera_commander.ops as ops
    import sphaera_commander.buttonbar as buttonbar
    CORE_OK = True
except Exception:  # нет ядра/PySide6
    CORE_OK = False


@unittest.skipUnless(CORE_OK, "ядро или PySide6 недоступны")
class TestInjection(unittest.TestCase):
    def tearDown(self):
        ops.trash_via_platform = None
        buttonbar.run_detached_shell = None

    def test_defaults_keep_linux_behavior(self):
        self.assertIsNone(ops.trash_via_platform)
        self.assertIsNone(buttonbar.run_detached_shell)

    def test_execute_trash_delegates_when_injected(self):
        sentinel = object()
        calls = []
        ops.trash_via_platform = lambda *a: calls.append(a) or sentinel
        try:
            returned = ops.execute_trash([], lambda s: None, lambda: False)
        finally:
            ops.trash_via_platform = None
        self.assertIs(returned, sentinel)
        self.assertEqual(len(calls), 1)  # (sources, progress_cb, is_cancelled)

    def test_run_dot_py_wires_all_three_services(self):
        import win64.run  # noqa: F401 — импорт выполняет инъекцию
        from win64.platform import trash, shell
        self.assertIs(ops.trash_via_platform, trash.trash)
        self.assertIs(buttonbar.run_detached_shell, shell.run_shell)


if __name__ == "__main__":
    unittest.main()
