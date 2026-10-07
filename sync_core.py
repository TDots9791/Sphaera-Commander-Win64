#!/usr/bin/env python3
"""Подтянуть общий код (пакет sphaera_commander) из Linux-репозитория.

Модель разделения — ТЗ.md §2: общий код в этом репозитории не хранится
(копия в .gitignore) и вручную не правится; единственный писатель копии —
этот скрипт. Версия и коммит источника записываются в CORE_VERSION.txt.

Использование:
  python sync_core.py [--source ПУТЬ] [--commit SHA] [--check]

  --source  Linux-репозиторий; по умолчанию $SPHAERA_CORE_REPO, иначе
            «Sphaera Commander» рядом с этим репозиторием
  --commit  переопределить записываемый коммит (иначе git rev-parse HEAD
            источника; без git — «unknown»)
  --check   не копировать: сверить копию с источником (по байтам) и с
            записью CORE_VERSION.txt; расхождение — выход 1 (для CI)

Примечание о целостности: копия собирается во временную папку и проверяется
до замены прежней, но сама замена — «удалить старую, переименовать новую»
(атомарного переименования каталога поверх непустого в POSIX/Windows нет).
Окно сбоя закрывается повторным запуском.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE = "sphaera_commander"
RECORD = "CORE_VERSION.txt"
_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def default_source() -> Path:
    env = os.environ.get("SPHAERA_CORE_REPO")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "Sphaera Commander"


def _version_of(package_dir: Path) -> str:
    init = package_dir / "__init__.py"
    try:
        text = init.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"не читается {init}: {exc}") from exc
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.M)
    if not m:
        raise ValueError(f"нет __version__ в {init}")
    return m.group(1)


def git_commit(source: Path, override: str | None = None) -> str:
    if override:
        return override
    try:
        proc = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return proc.stdout.strip()


def copy_package(source: Path, dest_root: Path) -> str:
    """Скопировать пакет из источника во временную папку, проверить и
    заменить прежнюю копию. Возвращает версию подтянутого пакета."""
    src = source / PACKAGE
    if not (src / "__init__.py").is_file():
        raise FileNotFoundError(f"нет пакета {PACKAGE}/ в {source}")
    tmp = dest_root / f".{PACKAGE}.sync-tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp, ignore=_IGNORE)
    version = _version_of(tmp)  # валидация до замены известной копии
    final = dest_root / PACKAGE
    if final.exists():
        shutil.rmtree(final)
    os.replace(tmp, final)
    return version


def write_record(dest_root: Path, version: str, commit: str) -> None:
    target = dest_root / RECORD
    tmp = target.with_name(RECORD + ".tmp")
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    tmp.write_text(
        "# Пишется sync_core.py, вручную не править.\n"
        f"version={version}\n"
        f"commit={commit}\n"
        f"synced={now}\n",
        encoding="utf-8")
    os.replace(tmp, target)


def read_record(dest_root: Path) -> dict[str, str]:
    record: dict[str, str] = {}
    for line in (dest_root / RECORD).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            record[key.strip()] = value.strip()
    return record


def _tree_digest(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in sorted(filenames):
            if name.endswith(".pyc"):
                continue
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def check(dest_root: Path, source: Path,
          commit_override: str | None = None) -> list[str]:
    """Сверка для CI: копия по байтам равна источнику, запись — версии и
    коммиту источника. Возвращает список расхождений (пустой — всё сошлось)."""
    final = dest_root / PACKAGE
    if not final.is_dir():
        return [f"копии {PACKAGE}/ нет — запустите sync_core.py"]
    problems: list[str] = []
    src = _tree_digest(source / PACKAGE)
    dst = _tree_digest(final)
    if src != dst:
        only_src = sorted(set(src) - set(dst))
        only_dst = sorted(set(dst) - set(src))
        changed = sorted(k for k in set(src) & set(dst)
                         if src[k] != dst[k])
        for label, names in (("нет в копии", only_src),
                             ("лишнее в копии", only_dst),
                             ("изменено", changed)):
            if names:
                shown = ", ".join(names[:5]) + ("…" if len(names) > 5 else "")
                problems.append(f"{label}: {shown}")
    try:
        version = _version_of(final)
    except ValueError as exc:
        problems.append(str(exc))
        version = None
    record = read_record(dest_root)
    if version and record.get("version") != version:
        problems.append(f"запись version={record.get('version')!r}, "
                        f"в пакете {version!r}")
    commit = git_commit(source, commit_override)
    if record.get("commit") != commit:
        problems.append(f"запись commit={record.get('commit')!r}, "
                        f"источник {commit!r}")
    return problems


def main(argv: list[str] | None = None,
         dest_root: Path | None = None) -> int:
    # Windows-консоль по умолчанию в cp1251/cp866 — кириллица print()
    # падает UnicodeEncodeError; вывод принудительно в UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(
        description="Подтянуть общий код из Linux-репозитория (ТЗ §2)")
    ap.add_argument("--source", type=Path, default=None,
                    help="Linux-репозиторий (по умолчанию $SPHAERA_CORE_REPO "
                         "или ../Sphaera Commander)")
    ap.add_argument("--commit", default=None,
                    help="переопределить записываемый коммит")
    ap.add_argument("--check", action="store_true",
                    help="сверить копию с источником и записью, не копируя")
    args = ap.parse_args(argv)
    dest_root = dest_root or Path(__file__).resolve().parent
    source = args.source or default_source()
    if args.check:
        problems = check(dest_root, source, args.commit)
        if problems:
            print("КОПИЯ РАСШЛАСЬ С ИСТОЧНИКОМ:")
            for p in problems:
                print(f" - {p}")
            print("Перезапустите: python sync_core.py")
            return 1
        record = read_record(dest_root)
        print(f"OK: копия = {source} "
              f"(v{record.get('version')}, {record.get('commit', '')[:12]})")
        return 0
    version = copy_package(source, dest_root)
    commit = git_commit(source, args.commit)
    write_record(dest_root, version, commit)
    print(f"Общий код подтянут: {PACKAGE} v{version}, "
          f"коммит {commit[:12]}, источник {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
