"""Каталоги данных приложения (ТЗ §3, строка «пути данных»).

Раскладка каталогов; набор каталогов одинаков на обеих платформах,
меняется только база:

  config_dir()  настройки (buttonbar, colorize, hotlist, cloudsync,
                pluginmgr, ключ age из plugins/encrypt)
  cache_dir()   кэш (миниатюры — в cache_dir()/thumbs, как thumbnails.py)
  data_dir()    данные (cloudsync-листинги, cloudmount-точки)

Linux — как сейчас, включая переменные XDG_*:
  ~/.config/sphaera-commander · ~/.cache/sphaera-commander ·
  ~/.local/share/sphaera-commander

Windows:
  %APPDATA%\\SphaeraCommander ·
  %LOCALAPPDATA%\\SphaeraCommander\\cache ·
  %LOCALAPPDATA%\\SphaeraCommander

База читается из окружения при каждом вызове (без кэша — тесты подменяют
env), каталог создаётся при первом вызове; возвращается абсолютный путь
(str) без завершающего разделителя.
"""

from __future__ import annotations

import os
import sys

IS_WINDOWS = sys.platform == "win32"


def _windows_base(env_var: str, fallback: tuple[str, ...]) -> str:
    base = os.environ.get(env_var)
    if base:
        return base
    return os.path.join(os.path.expanduser("~"), *fallback)


def _xdg(var: str, default: str) -> str:
    return os.environ.get(var) or os.path.join(os.path.expanduser("~"), default)


def config_dir() -> str:
    """Каталог настроек (раскладка — в docstring модуля)."""
    if IS_WINDOWS:
        path = os.path.join(_windows_base("APPDATA", ("AppData", "Roaming")),
                            "SphaeraCommander")
    else:
        path = os.path.join(_xdg("XDG_CONFIG_HOME", ".config"),
                            "sphaera-commander")
    os.makedirs(path, exist_ok=True)
    return path


def cache_dir() -> str:
    """Каталог кэша, миниатюры — в cache_dir()/thumbs."""
    if IS_WINDOWS:
        path = os.path.join(_windows_base("LOCALAPPDATA", ("AppData", "Local")),
                            "SphaeraCommander", "cache")
    else:
        path = os.path.join(_xdg("XDG_CACHE_HOME", ".cache"),
                            "sphaera-commander")
    os.makedirs(path, exist_ok=True)
    return path


def data_dir() -> str:
    """Каталог данных (cloudsync/cloudmount)."""
    if IS_WINDOWS:
        path = os.path.join(_windows_base("LOCALAPPDATA", ("AppData", "Local")),
                            "SphaeraCommander")
    else:
        path = os.path.join(_xdg("XDG_DATA_HOME", os.path.join(".local", "share")),
                            "sphaera-commander")
    os.makedirs(path, exist_ok=True)
    return path
