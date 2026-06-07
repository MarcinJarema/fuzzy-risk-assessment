"""Pakiet ``src`` — silnik systemu rozmytego oraz trzy systemy oceny ryzyka."""

from __future__ import annotations

from . import ryzyko_dostaw, ryzyko_inwestycji, ryzyko_klienta
from .fuzzy_core import FuzzySystem, MF, Rule, SystemSpec, Variable

#: Wszystkie systemy dostępne w projekcie, w kolejności prezentacji.
SPECS = [
    ryzyko_klienta.SPEC,
    ryzyko_inwestycji.SPEC,
    ryzyko_dostaw.SPEC,
]

#: Zestawy przypadków testowych powiązane z kluczem systemu.
TEST_CASES = {
    ryzyko_klienta.SPEC.key: ryzyko_klienta.TEST_CASES,
    ryzyko_inwestycji.SPEC.key: ryzyko_inwestycji.TEST_CASES,
    ryzyko_dostaw.SPEC.key: ryzyko_dostaw.TEST_CASES,
}

__all__ = [
    "FuzzySystem",
    "MF",
    "Rule",
    "SystemSpec",
    "Variable",
    "SPECS",
    "TEST_CASES",
]
