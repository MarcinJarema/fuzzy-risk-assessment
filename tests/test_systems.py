"""
Testy weryfikacyjne systemów rozmytych.

Sprawdzają poprawność konstrukcji (kompletność bazy reguł, pokrycie zakresów)
oraz merytoryczną logikę wnioskowania — monotoniczność i sensowność wyników,
zgodnie z krokiem 6/9 schematu projektowania.
"""

from __future__ import annotations

import numpy as np
import pytest

from src import SPECS, TEST_CASES
from src.fuzzy_core import FuzzySystem, compare_defuzzifiers


@pytest.fixture(params=SPECS, ids=lambda s: s.key)
def spec(request):
    return request.param


def test_baza_regul_kompletna(spec):
    """9 reguł = wszystkie kombinacje 3x3 wartości lingwistycznych wejść."""
    assert len(spec.rules) == 9
    kombinacje = {r.antecedents for r in spec.rules}
    assert len(kombinacje) == 9
    etykiety1 = {mf.label for mf in spec.input1.mfs}
    etykiety2 = {mf.label for mf in spec.input2.mfs}
    assert kombinacje == {(a, b) for a in etykiety1 for b in etykiety2}


def test_konkluzje_w_zbiorze_wyjscia(spec):
    dozwolone = {mf.label for mf in spec.output.mfs}
    assert all(r.consequent in dozwolone for r in spec.rules)


def test_pokrycie_przestrzeni_wejsc(spec):
    """Każdy punkt zakresu wejścia ma niezerową przynależność do >=1 zbioru."""
    system = FuzzySystem(spec)
    for var, fuzzy_var in [(spec.input1, system._ant1), (spec.input2, system._ant2)]:
        suma = np.zeros_like(fuzzy_var.universe, dtype=float)
        for mf in var.mfs:
            suma = np.maximum(suma, fuzzy_var[mf.label].mf)
        assert np.all(suma > 0), f"luka w pokryciu zmiennej {var.name}"


def test_wyjscie_w_zakresie(spec):
    system = FuzzySystem(spec)
    for x1, x2 in TEST_CASES[spec.key]:
        y = system.infer(x1, x2)
        assert spec.output.vmin <= y <= spec.output.vmax


def test_walidacja_zakresu_wejsc(spec):
    """Wejście spoza zakresu zmiennej powinno rzucić ValueError, a nie
    zostać po cichu przycięte do granicy uniwersum."""
    system = FuzzySystem(spec)
    poza1 = spec.input1.vmax + 1
    poza2 = spec.input2.vmin - 1
    with pytest.raises(ValueError):
        system.infer(poza1, (spec.input2.vmin + spec.input2.vmax) / 2)
    with pytest.raises(ValueError):
        system.infer((spec.input1.vmin + spec.input1.vmax) / 2, poza2)
    # wartości na samych granicach są dozwolone
    assert system.infer(spec.input1.vmin, spec.input2.vmin) is not None
    assert system.infer(spec.input1.vmax, spec.input2.vmax) is not None


def test_monotonicznosc_drugiego_wejscia():
    """Dla ryzyka inwestycji: przy stałej stopie zwrotu wzrost zmienności
    rynku nie obniża szacowanego ryzyka."""
    from src import ryzyko_inwestycji

    system = FuzzySystem(ryzyko_inwestycji.SPEC)
    poprzednie = -1.0
    for zmiennosc in [10, 30, 50, 70, 90]:
        y = system.infer(15, zmiennosc)  # stała, średnia stopa zwrotu
        assert y >= poprzednie - 1e-6, "ryzyko spadło mimo wzrostu zmienności"
        poprzednie = y


def test_analiza_operatorow_defuzyfikacji(spec):
    """compare_defuzzifiers zwraca wynik każdą metodą, w zakresie wyjścia."""
    methods, rows = compare_defuzzifiers(spec, TEST_CASES[spec.key])
    assert set(methods) == set(FuzzySystem.DEFUZZ_METHODS)
    assert len(rows) == len(TEST_CASES[spec.key])
    for row in rows:
        for m in methods:
            assert spec.output.vmin <= row[m] <= spec.output.vmax


def test_nieznana_metoda_defuzyfikacji():
    with pytest.raises(ValueError):
        FuzzySystem(SPECS[0], defuzz_method="nieistnieje")


def test_skrajne_przypadki_klient():
    """Najgorszy klient ma wyraźnie wyższe ryzyko niż najlepszy."""
    from src import ryzyko_klienta

    system = FuzzySystem(ryzyko_klienta.SPEC)
    najgorszy = system.infer(1000, 5)     # niski dochód, zła historia
    najlepszy = system.infer(18000, 95)   # wysoki dochód, dobra historia
    assert najgorszy > najlepszy
    assert najgorszy > 60
    assert najlepszy < 40


def test_skrajne_przypadki_dostawy():
    from src import ryzyko_dostaw

    system = FuzzySystem(ryzyko_dostaw.SPEC)
    ryzykowny = system.infer(10, 55)   # niska niezawodność, długi czas
    bezpieczny = system.infer(98, 5)   # wysoka niezawodność, krótki czas
    assert ryzykowny > bezpieczny
    assert ryzykowny > 60
    assert bezpieczny < 40
