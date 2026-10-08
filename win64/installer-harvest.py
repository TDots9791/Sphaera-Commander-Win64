#!/usr/bin/env python3
"""Харвест dist/SphaeraCommander -> WiX-фрагмент (Ф4, ТЗ §5).

Обходит дерево onedir-сборки и генерирует <Fragment> с каталогами,
компонентами (файл = KeyPath, GUID WiX v4+ выводит автоматически и
стабильно от целевого пути) и ComponentGroup "AppComponents", на которую
ссылается Feature в installer.wxs. Запуск:

  python win64/installer-harvest.py [каталог-сборки] [выход.wxs]

По умолчанию: dist/SphaeraCommander -> win64/.harvest.wxs (в .gitignore).
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

DIST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist") / "SphaeraCommander"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent / ".harvest.wxs"


def build(dir_path: Path, dir_id: str, counters: dict, lines: list, depth: int) -> None:
    pad = "  " * depth
    for child in sorted(dir_path.iterdir()):
        if child.is_dir():
            counters["dir"] += 1
            cid = f"dir.{counters['dir']:04d}"
            lines.append(f'{pad}  <Directory Id={quoteattr(cid)} Name={quoteattr(child.name)}>')
            build(child, cid, counters, lines, depth + 1)
            lines.append(f'{pad}  </Directory>')
        else:
            counters["cmp"] += 1
            counters["file"] += 1
            cid = f"cmp.{counters['cmp']:04d}"
            fid = f"fil.{counters['file']:04d}"
            rel = child.relative_to(DIST).as_posix()
            lines.append(
                f'{pad}  <Component Id={quoteattr(cid)}>'
                f'<File Id={quoteattr(fid)} Source={quoteattr(rel)} />'
                f'</Component>')
            refs.append(f'      <ComponentRef Id={quoteattr(cid)} />')


if not (DIST / "SphaeraCommander.exe").is_file():
    raise SystemExit(f"нет {DIST}/SphaeraCommander.exe — сначала сборка (build_exe.ps1)")

counters = {"dir": 0, "cmp": 0, "file": 0}
refs: list[str] = []
lines: list[str] = [
    '<Fragment xmlns="http://wixtoolset.org/schemas/v4/wxs">',
    '  <StandardDirectory Id="ProgramFiles64Folder">',
    '    <Directory Id="INSTALLFOLDER" Name="SphaeraCommander">',
]
build(DIST, "INSTALLFOLDER", counters, lines, 3)
lines += [
    '    </Directory>',
    '  </StandardDirectory>',
    '  <ComponentGroup Id="AppComponents">',
    *refs,
    '  </ComponentGroup>',
    '</Fragment>',
]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"харвест: {counters['cmp']} файлов, {counters['dir']} каталогов -> {OUT}")

# самопроверка: хорошо сформированный XML
import xml.etree.ElementTree as ET

ET.parse(OUT)
