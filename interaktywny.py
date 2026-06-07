"""
Interaktywny kreator zapytań do systemów rozmytych.

Uruchamia program w trybie pytań: wybierasz system (1-3), podajesz po kolei
dwie wartości wejściowe, a program zwraca oszacowane ryzyko. Po wyniku możesz
policzyć kolejny scenariusz lub zakończyć.

Uruchomienie::

    python interaktywny.py
"""

from __future__ import annotations

from src import SPECS
from src.fuzzy_core import FuzzySystem, SystemSpec, Variable


def _wybierz_system() -> SystemSpec:
    """Wypisuje menu systemów i zwraca wybrany przez użytkownika (1-3)."""
    print("\nDostępne systemy oceny ryzyka:")
    for i, spec in enumerate(SPECS, start=1):
        print(f"  {i}) {spec.title}")

    while True:
        wybor = input(f"\nWybierz system (1-{len(SPECS)}) lub 'q' aby wyjść: ").strip()
        if wybor.lower() in {"q", "quit", "exit"}:
            raise SystemExit("Zakończono.")
        if wybor.isdigit() and 1 <= int(wybor) <= len(SPECS):
            return SPECS[int(wybor) - 1]
        print(f"  Niepoprawny wybór. Wpisz liczbę 1-{len(SPECS)}.")


def _zapytaj_o_wartosc(var: Variable) -> float:
    """Pyta o wartość jednej zmiennej, waliduje zakres i typ, powtarza przy błędzie."""
    monit = f"  {var.name} [{var.unit}], zakres {var.vmin:g}-{var.vmax:g}: "
    while True:
        surowe = input(monit).strip().replace(",", ".")
        try:
            wartosc = float(surowe)
        except ValueError:
            print("    To nie jest liczba — spróbuj ponownie.")
            continue
        if not (var.vmin <= wartosc <= var.vmax):
            print(f"    Wartość poza zakresem [{var.vmin:g}, {var.vmax:g}] — spróbuj ponownie.")
            continue
        return wartosc


def _policz_scenariusz(spec: SystemSpec) -> None:
    """Pyta o oba wejścia wybranego systemu i wypisuje wynik."""
    print(f"\n>>> {spec.title}")
    print(f"    {spec.goal}")
    print("    Podaj wartości wejściowe:")
    x1 = _zapytaj_o_wartosc(spec.input1)
    x2 = _zapytaj_o_wartosc(spec.input2)

    system = FuzzySystem(spec)
    y = system.infer(x1, x2)

    print("\n    --- WYNIK ---")
    print(f"    {spec.input1.name} = {x1:g} {spec.input1.unit}")
    print(f"    {spec.input2.name} = {x2:g} {spec.input2.unit}")
    print(f"    => {spec.output.name} = {y:.2f} {spec.output.unit}")


def main() -> None:
    print("=" * 60)
    print(" Systemy rozmyte — interaktywna ocena ryzyka biznesowego")
    print("=" * 60)

    try:
        while True:
            spec = _wybierz_system()
            _policz_scenariusz(spec)

            dalej = input("\nPoliczyć kolejny scenariusz? (t/n): ").strip().lower()
            if dalej not in {"t", "tak", "y", "yes"}:
                print("Zakończono.")
                break
    except (SystemExit, KeyboardInterrupt) as exc:
        print(f"\n{exc if str(exc) else 'Zakończono.'}")


if __name__ == "__main__":
    main()
