# Sphaera Commander Win64

Windows-порт [Sphaera Commander](https://github.com/TDots9791/Sphaera-Commander) —
двухпанельного файлового менеджера в духе Total Commander.

Общий код не хранится в этом репозитории: `sync_core.py` подтягивает пакет
`sphaera_commander` из Linux-репозитория (версия/коммит — в
`CORE_VERSION.txt`); вся Windows-специфика — только в `win64/platform/`
(выбор реализации по `sys.platform`, подключается до импорта приложения).
Статус: скелет готов (`sync_core`, контракты платформенного слоя, точка
входа, тесты, CI); реализация слоя — следующий шаг.

```sh
python3 sync_core.py                       # подтянуть общий код
python3 -m unittest discover -s tests -v   # тесты платформенного слоя
```
