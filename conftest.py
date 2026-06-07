"""Konfiguracja pytest.

Sama obecność tego pliku w katalogu głównym projektu sprawia, że pytest dodaje
go do ``sys.path``, dzięki czemu ``import src`` działa przy zwykłym wywołaniu
``pytest`` (bez konieczności ``python -m pytest`` ani ustawiania PYTHONPATH).
"""
