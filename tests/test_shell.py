"""Ф1: shell — shell_argv и run_shell на обеих платформах."""

import os
import shlex
import tempfile
import time
import unittest

from win64.platform import shell


class TestShellArgv(unittest.TestCase):
    def test_shape_per_platform(self):
        argv = shell.shell_argv("echo hi")
        self.assertIsInstance(argv, list)
        if shell.IS_WINDOWS:
            self.assertEqual(argv[0], "cmd.exe")
            self.assertIn("/c", argv)
            self.assertEqual(argv[-1], "echo hi")
        else:
            self.assertEqual(argv, ["/bin/sh", "-c", "echo hi"])


class TestRunShell(unittest.TestCase):
    def test_capture(self):
        cmd = "echo hello" if shell.IS_WINDOWS else "printf hi"
        code, out = shell.run_shell(cmd)
        self.assertEqual(code, 0)
        self.assertIn("hello" if shell.IS_WINDOWS else "hi", out)

    def test_exit_code(self):
        code, _ = shell.run_shell("exit 3")
        self.assertEqual(code, 3)

    def test_cwd(self):
        d = tempfile.mkdtemp()
        cmd = "cd" if shell.IS_WINDOWS else "pwd"
        code, out = shell.run_shell(cmd, cwd=d)
        self.assertEqual(code, 0)
        self.assertEqual(os.path.realpath(out.strip()),
                         os.path.realpath(d))

    def test_detached_delivers_side_effect(self):
        d = tempfile.mkdtemp()
        marker = os.path.join(d, "done")
        if shell.IS_WINDOWS:
            cmd = f'type nul > "{marker}"'
        else:
            cmd = f': > {shlex.quote(marker)}'
        self.assertIsNone(shell.run_shell(cmd, cwd=d, detached=True))
        deadline = time.time() + 10
        while not os.path.exists(marker) and time.time() < deadline:
            time.sleep(0.05)
        self.assertTrue(os.path.exists(marker), "отсоединённый потомок "
                                                "не отработал за 10 с")


if __name__ == "__main__":
    unittest.main()
