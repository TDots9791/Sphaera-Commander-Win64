"""Sphaera Commander Win64: платформенный слой + точка входа (ТЗ §4).

Обычный пакет (с __init__.py), а не namespace: PyInstaller в связке с
namespace-пакетами сматчил win64/platform под именем stdlib-модуля
platform и затенил его — pypdfium2 падал на platform.system()
(поймано зеркальной сборкой Ф2).
"""
