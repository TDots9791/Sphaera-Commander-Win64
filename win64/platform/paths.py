"""Каталоги данных приложения (ТЗ §3, строка «пути данных»).

Раскладка каталогов; набор каталогов одинаков на обеих платформах,
меняется только база:

  config_dir()  настройки (buttonbar, colorize, hotlist, cloudsync,
                pluginmgr, ключ age из plugins/encrypt)
  cache_dir()   кэш (миниатюры — в cache_dir()/thumbs, как thumbnails.py)
  data_dir()    данные (cloudsync-листинги, cloudmount-точки)

Linux (как сейчас, включая переменные XDG_*):
  config_dir() -> ~/.config/sphaera-commander
  cache_dir()  -> ~/.cache/sphaera-commander
  data_dir()   -> ~/.local/share/sphaera-commander

Windows:
  config_dir() -> %APPDATA%\\SphaeraCommander
  cache_dir()  -> %LOCALAPPDATA%\\SphaeraCommander\\cache
  data_dir()   -> %LOCALAPPDATA%\\SphaeraCommander

Ф1: каталог создаётся при первом вызове; возвращается абсолютный путь
(str) без завершающего разделителя.
"""

from __future__ import annotations


def config_dir() -> str:
    """Каталог настроек (раскладка — в docstring модуля). Реализация — Ф1."""
    raise NotImplementedError("Ф1")


def cache_dir() -> str:
    """Каталог кэша, миниатюры — в cache_dir()/thumbs. Реализация — Ф1."""
    raise NotImplementedError("Ф1")


def data_dir() -> str:
    """Каталог данных (cloudsync/cloudmount). Реализация — Ф1."""
    raise NotImplementedError("Ф1")
