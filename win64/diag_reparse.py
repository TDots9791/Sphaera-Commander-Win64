#!/usr/bin/env python3
"""Диагностика отрицательных st_size на Windows (Ф3, живая проверка).

Проверяет lstat-размеры reparse-объектов (junction, симлинки) на
искусственных образцах и сканирует каталог на отрицательные значения —
те самые, что портят сумму dir_stats. Запуск из корня репозитория:

  python win64/diag_reparse.py                 # профиль пользователя
  python win64/diag_reparse.py "D:\\путь"      # конкретная папка
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile


def probe(path: str) -> None:
    st = os.lstat(path)
    mark = "  <-- ОТРИЦАТЕЛЬНЫЙ" if st.st_size < 0 else ""
    print(f"{path}  st_size = {st.st_size}{mark}")


def main() -> None:
    base = tempfile.mkdtemp(prefix="reparse_diag_")
    target = os.path.join(base, "target")
    os.mkdir(target)
    with open(os.path.join(base, "file.txt"), "w") as f:
        f.write("x")

    def mklink(*args: str) -> None:
        subprocess.run(["cmd", "/c", "mklink", *args],
                       capture_output=True, text=True)

    mklink("/J", os.path.join(base, "junction"), target)
    mklink("/D", os.path.join(base, "dirlink"), target)
    mklink(os.path.join(base, "filelink"),
           os.path.join(base, "file.txt"))

    print("== искусственные образцы ==")
    probe(os.path.join(base, "target"))
    probe(os.path.join(base, "file.txt"))
    for name in ("junction", "dirlink", "filelink"):
        path = os.path.join(base, name)
        if os.path.lexists(path):
            probe(path)

    print("== реальные reparse-объекты (до 12 находок) ==")
    shown = 0
    negative = []
    home = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~")
    print(f"сканируется: {home}")
    for root, dirs, files in os.walk(home):
        for name in dirs + files:
            path = os.path.join(root, name)
            try:
                st = os.lstat(path)
            except OSError:
                continue
            if st.st_file_attributes & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT
                if shown < 12:
                    probe(path)
                    shown += 1
            if st.st_size < 0:
                negative.append((path, st.st_size))
        if len(negative) >= 10:
            break

    print(f"== отрицательных lstat-размеров в профиле: {len(negative)} ==")
    for path, size in negative[:10]:
        print(f"  {path}  st_size = {size}")


if __name__ == "__main__":
    main()
