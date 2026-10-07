"""Ф1: terminals — контракт find_terminal."""

import unittest

from win64.platform import terminals


class TestTerminals(unittest.TestCase):
    def test_found_shape_or_none(self):
        found = terminals.find_terminal()
        if found is None:
            self.skipTest("терминалов из списка нет на этой машине")
        prog, args = found
        self.assertTrue(prog)
        self.assertTrue(any("{dir}" in a for a in args))

    def test_no_windows_terminals_on_posix(self):
        if terminals.IS_WINDOWS:
            self.skipTest("тест про не-Windows")
        self.assertIsNone(terminals.find_terminal())


if __name__ == "__main__":
    unittest.main()
