# Sphaera Commander Win64

Windows-порт [Sphaera Commander](../Sphaera%20Commander) — двухпанельного
файлового менеджера для Linux в духе Total Commander.

**Начните с [ТЗ.md](ТЗ.md)** — аудит переносимости, модель разделения
проектов, фазы работ. Статус: Ф0 сделано (скелет, sync_core, контракты
платформенного слоя); дальше — Ф1 (реализация paths/shell/terminals/trash).

```sh
python3 sync_core.py                       # подтянуть общий код (0.22.2)
python3 -m unittest discover -s tests -v   # тесты платформенного слоя
```
