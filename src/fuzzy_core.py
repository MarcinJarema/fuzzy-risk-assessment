"""
fuzzy_core
==========

Generyczny silnik systemu rozmytego typu **Mamdani Type-1**, zbudowany na
bibliotece ``scikit-fuzzy``. Jest to pythonowy odpowiednik procesu, który w
instrukcji realizowany jest w narzędziu MATLAB *Fuzzy Logic Designer*.

Założenia wnioskowania (zgodne z instrukcją / schematem projektowania):

* operator AND (t-norma)        -> ``min``
* metoda interpretacji reguł     -> ``min`` (implikacja Mamdaniego)
* metoda agregacji konkluzji     -> ``max``
* metoda defuzyfikacji           -> środek ciężkości (``centroid``)

Cały system opisuje się deklaratywnie obiektem :class:`SystemSpec`, a klasa
:class:`FuzzySystem` tłumaczy go na działający model ``skfuzzy.control`` oraz
udostępnia narzędzia weryfikacyjne (wykresy funkcji przynależności,
powierzchnia sterowania, tabela testów).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ---------------------------------------------------------------------------
# Deklaratywny opis systemu
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MF:
    """Pojedyncza funkcja przynależności (zbiór rozmyty).

    Parameters
    ----------
    label:
        Etykieta wartości lingwistycznej, np. ``"N"`` (niskie).
    kind:
        ``"trap"`` -> funkcja trapezowa (4 parametry),
        ``"tri"``  -> funkcja trójkątna (3 parametry).
    params:
        Punkty charakterystyczne funkcji przynależności.
    """

    label: str
    kind: str
    params: Sequence[float]


@dataclass(frozen=True)
class Variable:
    """Zmienna lingwistyczna (wejściowa lub wyjściowa)."""

    name: str
    unit: str
    vmin: float
    vmax: float
    mfs: Sequence[MF]
    step: float = 1.0
    #: Pełny, słowny opis etykiet — używany w sprawozdaniu i opisach wykresów.
    labels_pl: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    """Reguła bazy wiedzy: ``IF in1 is a AND in2 is b THEN out is c``."""

    antecedents: tuple[str, str]
    consequent: str
    weight: float = 1.0


@dataclass(frozen=True)
class SystemSpec:
    """Kompletna specyfikacja systemu rozmytego."""

    key: str  # krótki identyfikator, np. "klient"
    title: str  # tytuł czytelny dla człowieka
    goal: str  # cel systemu (krok 1 schematu)
    input1: Variable
    input2: Variable
    output: Variable
    rules: Sequence[Rule]


# ---------------------------------------------------------------------------
# Budowa i obsługa modelu
# ---------------------------------------------------------------------------


def _make_mf(universe: np.ndarray, mf: MF) -> np.ndarray:
    if mf.kind == "trap":
        return fuzz.trapmf(universe, list(mf.params))
    if mf.kind == "tri":
        return fuzz.trimf(universe, list(mf.params))
    raise ValueError(f"Nieznany typ funkcji przynależności: {mf.kind!r}")


class FuzzySystem:
    """Działający system rozmyty zbudowany na podstawie :class:`SystemSpec`."""

    #: Metody defuzyfikacji udostępniane przez scikit-fuzzy.
    DEFUZZ_METHODS = ("centroid", "bisector", "mom", "som", "lom")

    def __init__(self, spec: SystemSpec, defuzz_method: str = "centroid") -> None:
        if defuzz_method not in self.DEFUZZ_METHODS:
            raise ValueError(
                f"Nieznana metoda defuzyfikacji: {defuzz_method!r}. "
                f"Dostępne: {self.DEFUZZ_METHODS}"
            )
        self.spec = spec
        self.defuzz_method = defuzz_method

        # --- zmienne wejściowe (Antecedent) i wyjściowa (Consequent) ---
        self._ant1 = self._build_antecedent(spec.input1)
        self._ant2 = self._build_antecedent(spec.input2)
        self._con = self._build_consequent(spec.output)

        # --- baza reguł ---
        rules = []
        for r in spec.rules:
            a1, a2 = r.antecedents
            rule = ctrl.Rule(
                antecedent=(self._ant1[a1] & self._ant2[a2]),
                consequent=self._con[r.consequent],
                label=f"{a1}&{a2}->{r.consequent}",
            )
            rule.weight = r.weight
            rules.append(rule)

        self._control = ctrl.ControlSystem(rules)
        self._sim = ctrl.ControlSystemSimulation(self._control)

    # -- konstrukcja zmiennych -------------------------------------------------

    def _universe(self, var: Variable) -> np.ndarray:
        return np.arange(var.vmin, var.vmax + var.step, var.step)

    def _build_antecedent(self, var: Variable) -> ctrl.Antecedent:
        ant = ctrl.Antecedent(self._universe(var), var.name)
        for mf in var.mfs:
            ant[mf.label] = _make_mf(ant.universe, mf)
        return ant

    def _build_consequent(self, var: Variable) -> ctrl.Consequent:
        con = ctrl.Consequent(self._universe(var), var.name, defuzzify_method=self.defuzz_method)
        for mf in var.mfs:
            con[mf.label] = _make_mf(con.universe, mf)
        return con

    # -- wnioskowanie ----------------------------------------------------------

    @staticmethod
    def _check_range(var: Variable, value: float) -> None:
        if not (var.vmin <= value <= var.vmax):
            raise ValueError(
                f"Wartość {value:g} dla zmiennej '{var.name}' jest poza dozwolonym "
                f"zakresem [{var.vmin:g}, {var.vmax:g}] {var.unit}. "
                "Wejścia spoza zakresu byłyby po cichu przycięte do granicy i dałyby "
                "mylący wynik — popraw dane wejściowe."
            )

    def infer(self, x1: float, x2: float) -> float:
        """Zwraca wartość wyjściową po defuzyfikacji dla zadanych wejść.

        Raises
        ------
        ValueError
            Gdy któreś wejście wykracza poza zakres swojej zmiennej. Bez tej
            kontroli ``scikit-fuzzy`` po cichu przyciąłby wartość do granicy
            uniwersum, zwracając mylący wynik.
        """
        self._check_range(self.spec.input1, x1)
        self._check_range(self.spec.input2, x2)
        self._sim.input[self.spec.input1.name] = x1
        self._sim.input[self.spec.input2.name] = x2
        self._sim.compute()
        return float(self._sim.output[self.spec.output.name])

    # -- powierzchnia sterowania ----------------------------------------------

    def control_surface(self, n: int = 25) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Liczy powierzchnię sterowania na siatce ``n x n``.

        Zwraca ``(X, Y, Z)`` gotowe do wykresu 3D (``plot_surface``).
        """
        i1, i2 = self.spec.input1, self.spec.input2
        xs = np.linspace(i1.vmin, i1.vmax, n)
        ys = np.linspace(i2.vmin, i2.vmax, n)
        X, Y = np.meshgrid(xs, ys)
        Z = np.zeros_like(X)
        sim = ctrl.ControlSystemSimulation(self._control)
        for r in range(X.shape[0]):
            for c in range(X.shape[1]):
                sim.input[i1.name] = X[r, c]
                sim.input[i2.name] = Y[r, c]
                sim.compute()
                Z[r, c] = sim.output[self.spec.output.name]
        return X, Y, Z


# ---------------------------------------------------------------------------
# Wizualizacja i weryfikacja
# ---------------------------------------------------------------------------


def plot_membership(spec: SystemSpec, system: FuzzySystem, out_path: Path) -> None:
    """Zapisuje wykres funkcji przynależności wszystkich trzech zmiennych."""
    import matplotlib.pyplot as plt

    variables = [
        ("input", spec.input1, system._ant1),
        ("input", spec.input2, system._ant2),
        ("output", spec.output, system._con),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, (role, var, fuzzy_var) in zip(axes, variables):
        for mf in var.mfs:
            ax.plot(
                fuzzy_var.universe,
                fuzzy_var[mf.label].mf,
                linewidth=2,
                label=f"{mf.label} — {var.labels_pl.get(mf.label, mf.label)}",
            )
        unit = f" [{var.unit}]" if var.unit else ""
        prefix = "Wejście" if role == "input" else "Wyjście"
        ax.set_title(f"{prefix}: {var.name}{unit}")
        ax.set_xlabel(f"zakres [{var.vmin:g}, {var.vmax:g}]")
        ax.set_ylabel("μ — st. przynależności")
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=8, loc="upper center")
        ax.grid(alpha=0.3)
    fig.suptitle(f"Funkcje przynależności — {spec.title}", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def plot_surface(spec: SystemSpec, system: FuzzySystem, out_path: Path, n: int = 25) -> None:
    """Zapisuje wykres 3D powierzchni sterowania."""
    import matplotlib.pyplot as plt
    from matplotlib import cm

    X, Y, Z = system.control_surface(n=n)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, linewidth=0, antialiased=True)
    ax.set_xlabel(f"\n{spec.input1.name}")
    ax.set_ylabel(f"\n{spec.input2.name}")
    ax.set_zlabel(f"\n{spec.output.name}")
    ax.set_title(f"Powierzchnia sterowania — {spec.title}", fontweight="bold")
    fig.colorbar(surf, shrink=0.55, aspect=12, pad=0.1, label=spec.output.name)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def compare_defuzzifiers(
    spec: SystemSpec,
    cases: Sequence[tuple[float, float]],
    methods: Sequence[str] = FuzzySystem.DEFUZZ_METHODS,
) -> tuple[list[str], list[dict]]:
    """Porównuje wynik systemu dla różnych metod defuzyfikacji (analiza operatorów).

    Buduje ten sam system rozmyty (te same zmienne i reguły) osobno dla każdej
    metody wyostrzania, a następnie liczy wyjście dla wspólnego zestawu wejść.

    Zwraca ``(nazwy_metod, wiersze)``, gdzie każdy wiersz zawiera wejścia oraz
    wartość wyjściową uzyskaną każdą z metod.

    Skróty metod (scikit-fuzzy):

    * ``centroid`` — środek ciężkości,
    * ``bisector`` — dwusieczna pola,
    * ``mom``      — środek maksimum (*mean of maximum*),
    * ``som``      — najmniejsze z maksimów (*smallest of maximum*),
    * ``lom``      — największe z maksimów (*largest of maximum*).
    """
    systems = {m: FuzzySystem(spec, defuzz_method=m) for m in methods}
    rows: list[dict] = []
    for x1, x2 in cases:
        row = {spec.input1.name: x1, spec.input2.name: x2}
        for m in methods:
            row[m] = round(systems[m].infer(x1, x2), 2)
        rows.append(row)
    return list(methods), rows


def run_tests(system: FuzzySystem, cases: Sequence[tuple[float, float]]) -> list[dict]:
    """Uruchamia zestaw przypadków testowych i zwraca wyniki jako listę słowników."""
    spec = system.spec
    rows = []
    for x1, x2 in cases:
        y = system.infer(x1, x2)
        rows.append(
            {
                spec.input1.name: x1,
                spec.input2.name: x2,
                spec.output.name: round(y, 2),
            }
        )
    return rows
